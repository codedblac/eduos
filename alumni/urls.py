from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profiles', views.AlumniProfileViewSet, basename='alumni-profiles')
router.register(r'employment', views.AlumniEmploymentViewSet, basename='alumni-employment')
router.register(r'education', views.AlumniEducationViewSet, basename='alumni-education')
router.register(r'contributions', views.AlumniContributionViewSet, basename='alumni-contributions')

urlpatterns = [
    path('', include(router.urls)),
]
