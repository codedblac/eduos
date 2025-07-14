from django.urls import path, include
from rest_framework.routers import DefaultRouter
from admissions import views

router = DefaultRouter()
router.register(r'sessions', views.AdmissionSessionViewSet, basename='admission-session')
router.register(r'applicants', views.ApplicantViewSet, basename='applicant')
router.register(r'offers', views.AdmissionOfferViewSet, basename='admission-offer')
router.register(r'documents', views.AdmissionDocumentViewSet, basename='admission-document')
router.register(r'entrance-exams', views.EntranceExamViewSet, basename='entrance-exam')
router.register(r'comments', views.AdmissionCommentViewSet, basename='admission-comment')

urlpatterns = [
    path('', include(router.urls)),

    # AI & Analytics
    path('ai/suggest-placement/', views.AIPlacementSuggestionAPIView.as_view(), name='ai-placement-suggestion'),
    path('ai/recommend-offer/<int:pk>/', views.RecommendAdmissionStatusAPIView.as_view(), name='ai-recommend-offer'),
    path('analytics/summary/', views.AdmissionAnalyticsAPIView.as_view(), name='admission-analytics'),

    # Applicant Actions
    path('applicants/<int:pk>/generate-offer-letter/', views.GenerateOfferLetterAPIView.as_view(), name='generate-offer-letter'),
    path('applicants/<int:pk>/enroll/', views.EnrollApplicantAPIView.as_view(), name='enroll-applicant'),
    path('applicants/<int:pk>/generate-id/', views.GenerateStudentIDAPIView.as_view(), name='generate-student-id'),
]
