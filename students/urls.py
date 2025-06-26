from django.urls import path
from .views import (
    StudentListCreateView,
    StudentDetailView,  # updated to match views.py
    MyChildrenView,
    MyStreamStudentsView,
    UpdateEnrollmentStatusView,
)

urlpatterns = [
    path('students/', StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('my-children/', MyChildrenView.as_view(), name='my-children'),
    path('my-stream-students/', MyStreamStudentsView.as_view(), name='my-stream-students'),
    path('students/<int:pk>/update-status/', UpdateEnrollmentStatusView.as_view(), name='update-enrollment-status'),
]
