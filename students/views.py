from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Student
from .serializers import StudentSerializer
from .permissions import (
    CanManageStudents,
    CanViewStudentProfile,
    IsAdminOrSuperAdmin,
)
from .ai_engine import analyze_student_performance  # AI analysis function


class StudentListCreateView(generics.ListCreateAPIView):
    queryset = Student.objects.select_related('institution', 'stream').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, CanManageStudents]

    def perform_create(self, serializer):
        serializer.save()


class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.select_related('institution', 'stream').all()
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewStudentProfile]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # AI-powered performance analysis and feedback generation
        ai_insights = analyze_student_performance(instance)

        data = serializer.data
        data['ai_insights'] = ai_insights

        return Response(data)


class MyChildrenView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'parent':
            return Student.objects.none()
        return Student.objects.filter(parents__id=user.id)


class MyStreamStudentsView(generics.ListAPIView):
    serializer_class = StudentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role != 'teacher':
            return Student.objects.none()
        return Student.objects.filter(stream__teachers__id=user.id)


class UpdateEnrollmentStatusView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]

    def post(self, request, pk):
        student = get_object_or_404(Student, pk=pk)
        status = request.data.get('enrollment_status')

        if status not in dict(Student.ENROLLMENT_STATUSES):
            return Response({"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST)

        student.enrollment_status = status
        student.save(update_fields=["enrollment_status"])
        return Response({"detail": f"Student enrollment status updated to '{status}'."})
