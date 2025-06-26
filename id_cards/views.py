from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, permissions, status, filters as drf_filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import IDCard, IDCardTemplate
from .serializers import IDCardSerializer, IDCardTemplateSerializer
from .permissions import IsInstitutionAdminOrReadOnly
from .filters import IDCardFilter
from .ai import generate_id_card_image, regenerate_id_card_on_update
from .analytics import get_idcard_issuance_stats


class IDCardViewSet(viewsets.ModelViewSet):
    queryset = IDCard.objects.all().select_related("user", "institution", "template")
    serializer_class = IDCardSerializer
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter]
    filterset_class = IDCardFilter
    search_fields = ["user__first_name", "user__last_name", "user__username", "unique_identifier"]
    ordering_fields = ["issued_on", "expires_on", "user__last_name"]

    def perform_create(self, serializer):
        instance = serializer.save()
        generate_id_card_image(instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        regenerate_id_card_on_update(instance)

    @action(detail=False, methods=["get"], url_path="analytics", permission_classes=[permissions.IsAdminUser])
    def analytics(self, request):
        stats = get_idcard_issuance_stats()
        return Response(stats)

    @action(detail=True, methods=["post"], url_path="revoke")
    def revoke_id(self, request, pk=None):
        id_card = self.get_object()
        id_card.status = 'revoked'
        id_card.revoked_on = timezone.now()
        id_card.save(update_fields=['status', 'revoked_on'])
        return Response({"status": "revoked"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="reissue")
    def reissue_id(self, request, pk=None):
        id_card = self.get_object()
        id_card.status = 'active'
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
    search_fields = ["institution__name", "name"]
    ordering_fields = ["created_at", "updated_at"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
