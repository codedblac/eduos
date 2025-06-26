from django.urls import path
from .views import (
    TeacherListCreateView,
    TeacherRetrieveUpdateDestroyView,
    TeacherTimetableUploadView,  # Import the new view
)

urlpatterns = [
    path('', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('<int:pk>/', TeacherRetrieveUpdateDestroyView.as_view(), name='teacher-detail'),
    path('<int:pk>/upload-timetable/', TeacherTimetableUploadView.as_view(), name='teacher-upload-timetable'),  # New endpoint
]
