from django.urls import path
from .views import (
    ELibraryResourceListCreateView,
    ELibraryResourceDetailView,
    MyELibraryResourcesView,
    PublicELibraryListView,
    ResourceViewLogCreateView,
    ELibraryAIInsightsAPIView,
    ELibraryAnalyticsAPIView,
)

urlpatterns = [
    path('resources/', ELibraryResourceListCreateView.as_view(), name='elibrary-list-create'),
    path('resources/<uuid:pk>/', ELibraryResourceDetailView.as_view(), name='elibrary-detail'),
    path('resources/my/', MyELibraryResourcesView.as_view(), name='elibrary-my-resources'),
    path('resources/public/', PublicELibraryListView.as_view(), name='elibrary-public-resources'),
    path('resources/ai/insights/', ELibraryAIInsightsAPIView.as_view(), name='elibrary-ai-insights'),
    path('resources/analytics/', ELibraryAnalyticsAPIView.as_view(), name='elibrary-analytics'),
    path('resources/view-log/', ResourceViewLogCreateView.as_view(), name='elibrary-view-log'),
]
