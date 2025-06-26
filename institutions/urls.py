# institutions/urls.py

from django.urls import path
from .views import (
    InstitutionListCreateView,
    InstitutionRetrieveUpdateDestroyView,
    SchoolAccountListCreateView,
    SchoolAccountRetrieveUpdateDestroyView,
)

urlpatterns = [
    # Institution endpoints
    path('', InstitutionListCreateView.as_view(), name='institution-list-create'),
    path('<int:pk>/', InstitutionRetrieveUpdateDestroyView.as_view(), name='institution-detail'),

    # School financial accounts (e.g., fee payment destinations)
    path('<int:institution_id>/accounts/', SchoolAccountListCreateView.as_view(), name='schoolaccount-list-create'),
    path('accounts/<int:pk>/', SchoolAccountRetrieveUpdateDestroyView.as_view(), name='schoolaccount-detail'),
]
