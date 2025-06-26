from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DepartmentViewSet, DepartmentUserViewSet, SubjectViewSet

router = DefaultRouter()
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'department-users', DepartmentUserViewSet, basename='departmentuser')
router.register(r'subjects', SubjectViewSet, basename='subject')

urlpatterns = [
    path('', include(router.urls)),
]
