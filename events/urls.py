from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet,
    EventTagViewSet,
    RecurringEventRuleViewSet,
    suggest_event_slots,
)

# DRF Router setup
router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tags', EventTagViewSet, basename='event-tag')
router.register(r'recurrence', RecurringEventRuleViewSet, basename='recurring-rule')

# URL patterns
urlpatterns = [
    path('', include(router.urls)),
    
    # AI-Powered Scheduling
    path('events/suggest-time/', suggest_event_slots, name='event-suggest-time'),
]
