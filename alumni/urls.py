from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AlumniProfileViewSet, AlumniEventViewSet, AlumniEventRegistrationViewSet,
    AlumniDonationViewSet, AlumniMentorshipViewSet, AlumniAchievementViewSet,
    AlumniNotificationViewSet, AlumniFeedbackViewSet, AlumniMembershipViewSet,
    AlumniEmploymentViewSet, AlumniVolunteerViewSet
)

router = DefaultRouter()
router.register(r'profiles', AlumniProfileViewSet, basename='alumni-profile')
router.register(r'events', AlumniEventViewSet, basename='alumni-event')
router.register(r'event-registrations', AlumniEventRegistrationViewSet, basename='alumni-event-registration')
router.register(r'donations', AlumniDonationViewSet, basename='alumni-donation')
router.register(r'mentorships', AlumniMentorshipViewSet, basename='alumni-mentorship')
router.register(r'achievements', AlumniAchievementViewSet, basename='alumni-achievement')
router.register(r'notifications', AlumniNotificationViewSet, basename='alumni-notification')
router.register(r'feedbacks', AlumniFeedbackViewSet, basename='alumni-feedback')
router.register(r'memberships', AlumniMembershipViewSet, basename='alumni-membership')
router.register(r'employments', AlumniEmploymentViewSet, basename='alumni-employment')
router.register(r'volunteers', AlumniVolunteerViewSet, basename='alumni-volunteer')

urlpatterns = [
    path('', include(router.urls)),
]
