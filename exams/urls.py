from django.urls import path, include
from rest_framework.routers import DefaultRouter
from exams.views import (
    RenderExamPDFView,
    RenderExamLaTeXView,
    RenderMarkingSchemeView,
)



from . import views

# DRF router for ViewSets
router = DefaultRouter()
router.register(r'exams', views.ExamViewSet, basename='exam')
router.register(r'exam-subjects', views.ExamSubjectViewSet, basename='exam-subject')
router.register(r'exam-results', views.ExamResultViewSet, basename='exam-result')
router.register(r'student-scores', views.StudentScoreViewSet, basename='student-score')
router.register(r'grade-boundaries', views.GradeBoundaryViewSet, basename='grade-boundary')
router.register(r'insights', views.ExamInsightViewSet, basename='exam-insight')
router.register(r'predictions', views.ExamPredictionViewSet, basename='exam-prediction')

urlpatterns = [
    # ViewSet endpoints
    path('', include(router.urls)),

    # --------- Rendering ---------
        path('render/exam/<int:exam_id>/pdf/', RenderExamPDFView.as_view(), name='render-exam-pdf'),
        path('render/exam/<int:exam_id>/latex/', RenderExamLaTeXView.as_view(), name='render-exam-latex'),
        path('render/exam/<int:exam_id>/marking-scheme/', RenderMarkingSchemeView.as_view(), name='render-marking-scheme'),


    # --------- OCR Endpoints ---------
    path('ocr/upload/image/', views.OCRExtractView.as_view(), {'filetype': 'image'}, name='ocr-image-upload'),
    path('ocr/upload/pdf/', views.OCRExtractView.as_view(), {'filetype': 'pdf'}, name='ocr-pdf-upload'),

    # --------- AI, Predictions, Remedials ---------
    path('ai/generate/', views.ExamViewSet.as_view({'post': 'generate'}), name='ai-generate-exam'),

    # --------- Analytics & Insights ---------
    path('analytics/statistics/<int:exam_id>/', views.ExamStatisticsView.as_view(), name='exam-statistics'),
    path('analytics/rank/<int:exam_id>/', views.BulkActionsView.as_view(), {'action': 'generate-ranking'}, name='generate-ranking'),
    path('analytics/grade-assign/<int:exam_id>/', views.BulkActionsView.as_view(), {'action': 'assign-grades'}, name='bulk-assign-grades'),
    path('analytics/summary/<int:exam_id>/<int:student_id>/', views.StudentExamSummaryView.as_view(), name='student-exam-summary'),

    # --------- Utility Endpoints ---------
    path('utils/normalize/', views.UtilityAPIView.as_view(), {'util': 'normalize-score'}, name='normalize-score'),
    path('utils/generate-slug/', views.UtilityAPIView.as_view(), {'util': 'generate-slug'}, name='generate-exam-slug'),
    path('utils/label/<int:exam_id>/', views.FormatExamLabelView.as_view(), name='format-exam-label'),
]
