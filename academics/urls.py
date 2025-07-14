from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'academic-years', views.AcademicYearViewSet, basename='academic-year')
router.register(r'terms', views.TermViewSet, basename='term')
router.register(r'events', views.AcademicEventViewSet, basename='academic-event')
router.register(r'breaks', views.HolidayBreakViewSet, basename='holiday-break')

urlpatterns = [
    path('', include(router.urls)),
]
