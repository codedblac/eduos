from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from .models import Teacher
from .serializers import TeacherSerializer
from .permissions import IsSuperAdminOrInstitutionAdmin


class TeacherListCreateView(generics.ListCreateAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrInstitutionAdmin]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Teacher.objects.all()
        return Teacher.objects.filter(institution=user.institution)

    def perform_create(self, serializer):
        user = self.request.user
        if not user.is_superuser:
            serializer.save(institution=user.institution)
        else:
            serializer.save()


class TeacherRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrInstitutionAdmin]
    queryset = Teacher.objects.all()


# ✅ NEW: Upload/Replace Teacher Timetable PDF
class TeacherTimetableUploadView(generics.UpdateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperAdminOrInstitutionAdmin]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, *args, **kwargs):
        teacher = self.get_object()
        timetable_pdf = request.FILES.get('timetable_pdf')

        if not timetable_pdf:
            return Response({'error': 'No timetable PDF uploaded.'}, status=status.HTTP_400_BAD_REQUEST)

        teacher.timetable_pdf = timetable_pdf
        teacher.save()
        return Response({'success': 'Timetable uploaded successfully.'})
