from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AcademicYearViewSet, TermViewSet, AcademicEventViewSet, HolidayBreakViewSet

router = DefaultRouter()
router.register(r'academic-years', AcademicYearViewSet, basename='academic-year')
router.register(r'terms', TermViewSet, basename='term')
router.register(r'academic-events', AcademicEventViewSet, basename='academic-event')
router.register(r'holiday-breaks', HolidayBreakViewSet, basename='holiday-break')

urlpatterns = [
    path('', include(router.urls)),
] 
