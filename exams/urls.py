from django.urls import path
from . import views

urlpatterns = [
    # Exams
    path('exams/', views.ExamListCreateView.as_view(), name='exam-list-create'),
    path('exams/<int:pk>/', views.ExamRetrieveUpdateDestroyView.as_view(), name='exam-detail'),

    # Student Exam Results
    path('results/', views.StudentResultListView.as_view(), name='student-result-list'),
    path('results/<int:pk>/', views.StudentResultDetailView.as_view(), name='student-result-detail'),

    # # Analytics & Auto Processing
    # path('results/auto-process/<int:exam_id>/', views.AutoProcessExamResultsView.as_view(), name='auto-process-results'),

    # # (Optional) Predictive Exams (AI-Generated Exams)
    # path('generate-exam/', views.GenerateStandardExamView.as_view(), name='generate-standard-exam'),

    # # (Optional) Analytics endpoint
    # path('analytics/exam/<int:exam_id>/', views.ExamAnalyticsView.as_view(), name='exam-analytics'),
]
