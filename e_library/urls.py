from django.urls import path
from .views import (
    ELibraryResourceListCreateView,
    ELibraryResourceDetailView,
    MyELibraryResourcesView,
    PublicELibraryResourcesView,
    ELibraryAIInsightsView,
)

urlpatterns = [
    # Admins & Teachers: List or upload institutional resources
    path('resources/', ELibraryResourceListCreateView.as_view(), name='elibrary-list-create'),

    # Detail view for updating/deleting a resource
    path('resources/<uuid:pk>/', ELibraryResourceDetailView.as_view(), name='elibrary-detail'),

    # Teachers & Students: See resources in their institution
    path('resources/my/', MyELibraryResourcesView.as_view(), name='elibrary-my-resources'),

    # Everyone: Public (open-access) e-library resources
    path('resources/public/', PublicELibraryResourcesView.as_view(), name='elibrary-public-resources'),

    # AI Analysis Endpoint
    path('resources/ai/insights/', ELibraryAIInsightsView.as_view(), name='elibrary-ai-insights'),
]
