from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()

# Register ViewSets for models
router.register(r'types', views.AssessmentTypeViewSet)
router.register(r'templates', views.AssessmentTemplateViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'choices', views.AnswerChoiceViewSet)
router.register(r'sessions', views.AssessmentSessionViewSet)
router.register(r'answers', views.StudentAnswerViewSet)
router.register(r'results', views.AssessmentResultViewSet)
router.register(r'rubrics', views.GradingRubricViewSet)
router.register(r'schemes', views.MarkingSchemeViewSet)
router.register(r'feedback', views.FeedbackViewSet)
router.register(r'retakes', views.RetakePolicyViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # AI endpoints
    path('ai/generate/', views.AIGenerateAssessmentView.as_view(), name='ai-generate-assessment'),
    path('ai/predict-performance/', views.PredictPerformanceView.as_view(), name='predict-performance'),
    path('ai/remedial/', views.GenerateRemedialAssessmentView.as_view(), name='generate-remedial'),

    # Analytics endpoints
    path('analytics/performance/', views.AssessmentPerformanceAnalyticsView.as_view(), name='performance-analytics'),
    path('analytics/trends/', views.PerformanceTrendAnalysisView.as_view(), name='trend-analysis'),
    path('analytics/summary/', views.TeacherAssessmentSummaryView.as_view(), name='teacher-assessment-summary'),
]
