# reports/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 📄 Reports: CRUD
    path('', views.GeneratedReportListCreateView.as_view(), name='report-list-create'),
    path('<int:pk>/', views.GeneratedReportDetailView.as_view(), name='report-detail'),

    # 📤 Export Reports
    path('<int:pk>/export/pdf/', views.ExportReportPDFView.as_view(), name='report-export-pdf'),
    path('<int:pk>/export/excel/', views.ExportReportExcelView.as_view(), name='report-export-excel'),

    # ⚙️ Triggers: Report Generation + AI + Notifications
    path('generate/', views.TriggerReportGenerationView.as_view(), name='trigger-report-generation'),
    path('<int:pk>/ai/', views.TriggerAIInsightsView.as_view(), name='trigger-ai-insights'),
    path('<int:pk>/notify-top/', views.NotifyTopPerformersView.as_view(), name='notify-top-performers'),

    # 🧑‍🎓 Student & Subject Performance (per report)
    path('<int:report_id>/students/', views.ReportStudentPerformanceView.as_view(), name='report-student-performance'),
    path('<int:report_id>/subjects/', views.ReportSubjectBreakdownView.as_view(), name='report-subject-breakdown'),

    # 📊 Analytics & Insights
    path('analytics/class/<int:institution_id>/<int:class_level_id>/<int:stream_id>/', views.ClassPerformanceTrendsView.as_view(), name='class-performance-trends'),
    path('analytics/subject-difficulty/<int:institution_id>/', views.SubjectDifficultyAnalysisView.as_view(), name='subject-difficulty-analysis'),
    path('analytics/top-performers/<int:report_id>/', views.StreamTopPerformersView.as_view(), name='top-performers'),
    path('analytics/grade-distribution/<int:report_id>/', views.GradeDistributionView.as_view(), name='grade-distribution'),
    path('analytics/improvement/', views.MostImprovedStudentsView.as_view(), name='most-improved-students'),
    path('analytics/failure-alerts/<int:report_id>/', views.SubjectFailureAlertsView.as_view(), name='subject-failure-alerts'),
]
