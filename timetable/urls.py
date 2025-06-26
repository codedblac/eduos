# timetable/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Room URLs
    path('rooms/', views.RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', views.RoomRetrieveUpdateDestroyView.as_view(), name='room-detail'),

    # SubjectAssignment URLs
    path('subject-assignments/', views.SubjectAssignmentListCreateView.as_view(), name='subject-assignment-list-create'),
    path('subject-assignments/<int:pk>/', views.SubjectAssignmentRetrieveUpdateDestroyView.as_view(), name='subject-assignment-detail'),

    # TimetableEntry URLs
    path('entries/', views.TimetableEntryListView.as_view(), name='timetableentry-list'),
    path('entries/<int:pk>/', views.TimetableEntryRetrieveView.as_view(), name='timetableentry-detail'),

    # AI-Powered Timetable Generator
    path('generate-ai-timetable/', views.GenerateAITimetableView.as_view(), name='generate-ai-timetable'),
]
