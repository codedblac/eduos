from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DisciplineCategoryViewSet,
    DisciplineCaseViewSet,
    DisciplinaryActionViewSet
)

router = DefaultRouter()
router.register(r'categories', DisciplineCategoryViewSet, basename='discipline-category')
router.register(r'cases', DisciplineCaseViewSet, basename='discipline-case')
router.register(r'actions', DisciplinaryActionViewSet, basename='discipline-action')

urlpatterns = [
    path('', include(router.urls)),
]
