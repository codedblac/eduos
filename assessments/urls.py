from django.urls import path, include
from rest_framework.routers import DefaultRouter
from assessments import views

router = DefaultRouter()

# Register ViewSets
router.register(r'types', views.AssessmentTypeViewSet)
router.register(r'templates', views.AssessmentTemplateViewSet)
router.register(r'assessments', views.AssessmentViewSet)
router.register(r'questions', views.QuestionViewSet)
router.register(r'choices', views.AnswerChoiceViewSet)
router.register(r'sessions', views.AssessmentSessionViewSet)
router.register(r'answers', views.StudentAnswerViewSet)
router.register(r'marking-schemes', views.MarkingSchemeViewSet)
router.register(r'grading-rubrics', views.GradingRubricViewSet)
router.register(r'feedbacks', views.FeedbackViewSet)
router.register(r'retake-policies', views.RetakePolicyViewSet)
router.register(r'groups', views.AssessmentGroupViewSet)
router.register(r'weights', views.AssessmentWeightViewSet)
router.register(r'locks', views.AssessmentLockViewSet)
router.register(r'visibilities', views.AssessmentVisibilityViewSet)
router.register(r'performance-trends', views.PerformanceTrendViewSet)
router.register(r'test-cases', views.CodeTestCaseViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # 🔐 Lock/Publish actions
    path('assessments/<int:pk>/lock/', views.lock_assessment, name='assessment-lock'),
    path('assessments/<int:pk>/publish/', views.publish_assessment, name='assessment-publish'),

    # 📊 Analytics
    path('analytics/overall-summary/', views.overall_performance_summary_view, name='analytics-overall-summary'),
    path('analytics/student-trend/<int:student_id>/', views.student_performance_trend_view, name='analytics-student-trend'),
    path('analytics/topic-coverage/<int:subject_id>/', views.subject_coverage_analysis_view, name='analytics-topic-coverage'),
    path('analytics/inconsistencies/', views.flagged_students_view, name='analytics-inconsistencies'),
    path('analytics/heatmap/<int:student_id>/', views.topic_mastery_heatmap_view, name='analytics-heatmap'),
    path('analytics/participation/<int:assessment_id>/', views.assessment_participation_rate_view, name='analytics-participation'),

    # 🤖 AI endpoints
    path('ai/adaptive/<int:student_id>/<int:subject_id>/<int:class_level_id>/<int:term_id>/', views.generate_adaptive_assessment_view, name='ai-generate-adaptive'),
    path('ai/predict-score/<int:student_id>/<int:subject_id>/', views.predict_student_score_view, name='ai-predict-score'),
    path('ai/remedial/<int:student_id>/<int:subject_id>/', views.recommend_remedial_assessment_view, name='ai-remedial'),
    path('ai/underrepresented/<int:subject_id>/', views.underrepresented_topics_view, name='ai-underrepresented'),
    path('ai/suggest-questions/<int:topic_id>/', views.suggest_questions_for_topic_view, name='ai-suggest-questions'),
]
