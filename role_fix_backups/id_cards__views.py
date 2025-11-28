from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status, filters as drf_filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import IDCard, IDCardTemplate
from .serializers import IDCardSerializer, IDCardTemplateSerializer
from .permissions import IsInstitutionAdminOrReadOnly
from .filters import IDCardFilter
from .ai import IDCardAIEngine
from .analytics import get_idcard_statistics

from accounts.models import CustomUser
from institutions.models import Institution
from .models import IDCard, IDCardTemplate
# from .ai import generate_id_card_image, generate_bulk_id_cards
# from .analytics import get_idcard_issuance_stats
from .serializers import IDCardSerializer
from rest_framework.views import APIView
from django.http import HttpResponse
from django.shortcuts import get_object_or_404


class IDCardViewSet(viewsets.ModelViewSet):
    queryset = IDCard.objects.select_related("user", "institution", "template").all()
    serializer_class = IDCardSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = IDCardFilter
    search_fields = ["user__first_name", "user__last_name", "user__username", "unique_identifier"]
    ordering_fields = ["issued_on", "expires_on", "user__last_name"]

    def perform_create(self, serializer):
        instance = serializer.save()
        IDCardAIEngine(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        IDCardAIEngine(instance)

    @action(detail=False, methods=["get"], url_path="analytics", permission_classes=[permissions.IsAdminUser])
    def analytics(self, request):
        stats = get_idcard_statistics()
        return Response(stats)

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke_id(self, request, pk=None):
        id_card = self.get_object()
        if id_card.status == IDCard.StatusChoices.REVOKED:
            return Response({"detail": "ID card already revoked."}, status=status.HTTP_400_BAD_REQUEST)
        id_card.status = IDCard.StatusChoices.REVOKED
        id_card.revoked_on = timezone.now()
        id_card.save(update_fields = ["status", "revoked_on"])
        return Response({"status": "revoked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reissue")
    def reissue_id(self, request, pk=None):
        id_card = self.get_object()
        id_card.status = IDCard.StatusChoices.ACTIVE
        id_card.revoked_on = None
        id_card.expires_on = timezone.now() + timezone.timedelta(days=365)
        regenerate_id_card_on_update(id_card)
        id_card.save()
        return Response({"status": "reissued"}, status=status.HTTP_200_OK)


class IDCardTemplateViewSet(viewsets.ModelViewSet):
    queryset = IDCardTemplate.objects.all()
    serializer_class = IDCardTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    search_fields = ["institution__name"]
    ordering_fields = ["created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class GenerateSingleIDCardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_type, user_id):
        user = get_object_or_404(CustomUser, id=user_id)
        institution = user.institution

        # Choose latest active template or default logic
        template = IDCardTemplate.objects.filter(institution=institution).order_by('-updated_at').first()
        if not template:
            return Response({"detail": "No template found for institution."}, status=status.HTTP_400_BAD_REQUEST)

        id_card = IDCard.objects.create(
            user=user,
            institution=institution,
            template=template,
            issued_on=timezone.now()
        )
        IDCardAIEngine(id_card)

        serializer = IDCardSerializer(id_card)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GenerateBulkIDCardsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_type):
        institution = request.user.institution
        users = CustomUser.objects.filter(institution=institution, user_type=user_type.upper())

        created_cards = []
        for user in users:
            if IDCard.objects.filter(user=user, status=IDCard.StatusChoices.ACTIVE).exists():
                continue
            template = IDCardTemplate.objects.filter(institution=institution).order_by('-updated_at').first()
            if not template:
                continue
            id_card = IDCard.objects.create(
                user=user,
                institution=institution,
                template=template,
                issued_on=timezone.now()
            )
            IDCardAIEngine(id_card)
            created_cards.append(id_card)

        serializer = IDCardSerializer(created_cards, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class IDCardAnalyticsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        stats = get_idcard_statistics()
        return Response(stats)


class PreviewIDCardTemplateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, template_id):
        template = get_object_or_404(IDCardTemplate, id=template_id)
        dummy_user = request.user 
        dummy_card = IDCard(
            user=dummy_user,
            institution=dummy_user.institution,
            template=template,
            issued_on=timezone.now()
        )
        image_data = IDCardAIEngine(dummy_card, preview=True)

        response = HttpResponse(image_data, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="preview_template_{template.id}.png"'
        return response


class DownloadIDCardPDFView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        id_card = get_object_or_404(IDCard, pk=pk)
        if id_card.user != request.user and not request.user.is_staff:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        pdf_data = id_card.generate_pdf()  # Make sure this method exists
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="idcard_{pk}.pdf"'
        return response