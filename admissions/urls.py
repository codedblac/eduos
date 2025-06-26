from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admissions import views

router = DefaultRouter()
router.register(r'sessions', views.AdmissionSessionViewSet)
router.register(r'applicants', views.ApplicantViewSet)
router.register(r'offers', views.AdmissionOfferViewSet)
router.register(r'documents', views.AdmissionDocumentViewSet)
router.register(r'entrance-exams', views.EntranceExamViewSet)
router.register(r'comments', views.AdmissionCommentViewSet)

urlpatterns = [
    path('', include(router.urls)),

    # AI and Analytics
    path('ai/suggest-placement/', views.AIPlacementSuggestionAPIView.as_view(), name='ai-placement-suggestion'),
    path('analytics/summary/', views.AdmissionAnalyticsAPIView.as_view(), name='admission-analytics'),

    # Custom actions
    path('applicants/<int:pk>/enroll/', views.EnrollApplicantAPIView.as_view(), name='enroll-applicant'),
    path('applicants/<int:pk>/generate-id/', views.GenerateStudentIDAPIView.as_view(), name='generate-student-id'),
]
