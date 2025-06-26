from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    EventViewSet,
    EventTagViewSet,
    RecurringEventRuleViewSet,
    suggest_event_slots,  # 👈 NEW
)

router = DefaultRouter()
router.register(r'events', EventViewSet, basename='event')
router.register(r'tags', EventTagViewSet, basename='event-tag')
router.register(r'recurrence', RecurringEventRuleViewSet, basename='recurring-rule')

urlpatterns = [
    path('', include(router.urls)),
    path('events/suggest-time/', suggest_event_slots, name='suggest-time'),  # 👈 NEW
]
