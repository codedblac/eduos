from django.urls import path
from .views import (
    SubjectListCreateView, SubjectRetrieveUpdateDestroyView,
    SubjectClassLevelListCreateView, SubjectTeacherListCreateView
)

urlpatterns = [
    path('', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('<int:pk>/', SubjectRetrieveUpdateDestroyView.as_view(), name='subject-detail'),
    path('class-levels/', SubjectClassLevelListCreateView.as_view(), name='subject-classlevel-list'),
    path('teachers/', SubjectTeacherListCreateView.as_view(), name='subject-teacher-list'),
]
