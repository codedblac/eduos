# classes/urls.py
from django.urls import path
from .views import (
    ClassLevelListCreateView,
    ClassLevelRetrieveUpdateDestroyView,
    StreamListCreateView,
    StreamRetrieveUpdateDestroyView,
)

urlpatterns = [
    path('classlevels/', ClassLevelListCreateView.as_view(), name='classlevel-list-create'),
    path('classlevels/<int:pk>/', ClassLevelRetrieveUpdateDestroyView.as_view(), name='classlevel-detail'),
    path('streams/', StreamListCreateView.as_view(), name='stream-list-create'),
    path('streams/<int:pk>/', StreamRetrieveUpdateDestroyView.as_view(), name='stream-detail'),
]
