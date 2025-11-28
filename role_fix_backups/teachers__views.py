from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from .models import Teacher
from .serializers import TeacherSerializer
from .permissions import IsInstitutionAdminOrReadOnly
from .analytics import TeacherAnalytics
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q


class TeacherViewSet(viewsets.ModelViewSet):
    queryset = Teacher.objects.select_related('user', 'institution')
    serializer_class = TeacherSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]

    def get_queryset(self):
        institution = self.request.user.institution
        return self.queryset.filter(institution=institution)

    def perform_create(self, serializer):
        serializer.save(institution=self.request.user.institution)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        teacher = get_object_or_404(Teacher, user=request.user)
        serializer = self.get_serializer(teacher)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def search(self, request):
        query = request.query_params.get("q")
        if query:
            qs = self.get_queryset().filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query)
            )
        else:
            qs = self.get_queryset().none()
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_timetable(self, request, pk=None):
        teacher = self.get_object()
        timetable_pdf = request.FILES.get('timetable_pdf')
        if timetable_pdf:
            teacher.timetable_pdf = timetable_pdf
            teacher.save(update_fields=['timetable_pdf'])
            return Response({'status': 'Timetable uploaded'}, status=200)
        return Response({'error': 'No file uploaded'}, status=400)


class TeacherAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsInstitutionAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        institution = request.user.institution
        analytics = TeacherAnalytics(institution)
        data = analytics.generate_summary()
        return Response(data)
