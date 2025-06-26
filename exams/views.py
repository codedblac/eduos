from django.shortcuts import render

# Create your views here.
# exams/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Exam, ExamSubject, StudentScore
from .serializers import ExamSerializer, ExamSubjectSerializer, StudentScoreSerializer
from .permissions import (
    IsTeacher, IsStudent, IsAdminOrSuperAdmin,
    CanEnterMarks, CanGenerateAIInsights, CanViewOwnResults
)
from .utils import calculate_grade, generate_exam_predictions, generate_ai_exam



# -----------------------------
# Exam Views
# -----------------------------




class ExamListCreateView(generics.ListCreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class ExamRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


# -----------------------------
# ExamSubject Views
# -----------------------------

class ExamSubjectListCreateView(generics.ListCreateAPIView):
    queryset = ExamSubject.objects.all()
    serializer_class = ExamSubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


class ExamSubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamSubject.objects.all()
    serializer_class = ExamSubjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSuperAdmin]


# -----------------------------
# StudentScore Views (Teachers Input Only Marks)
# -----------------------------

class StudentScoreCreateView(generics.CreateAPIView):
    queryset = StudentScore.objects.all()
    serializer_class = StudentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher, CanEnterMarks]

    def perform_create(self, serializer):
        instance = serializer.save()
        calculate_grade(instance)  # Automatically grade and rank


class StudentScoreUpdateView(generics.UpdateAPIView):
    queryset = StudentScore.objects.all()
    serializer_class = StudentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher, CanEnterMarks]

    def perform_update(self, serializer):
        instance = serializer.save()
        calculate_grade(instance)  # Recalculate on update


# -----------------------------
# Student Result Views
# -----------------------------

class StudentResultListView(generics.ListAPIView):
    serializer_class = StudentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        return StudentScore.objects.filter(student__user=self.request.user)


class StudentResultDetailView(generics.RetrieveAPIView):
    serializer_class = StudentScoreSerializer
    permission_classes = [permissions.IsAuthenticated, CanViewOwnResults]
    queryset = StudentScore.objects.all()


# -----------------------------
# AI-Powered Insights & Predictions
# -----------------------------

class AIPredictedPerformanceView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanGenerateAIInsights]

    def post(self, request):
        try:
            predictions = generate_exam_predictions()
            return Response(predictions, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class AIGeneratedExamView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanGenerateAIInsights]

    def post(self, request):
        try:
            exam_paper = generate_ai_exam()
            return Response({"exam": exam_paper}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
