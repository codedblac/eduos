# medical/urls.py

from django.urls import path
from .views import (
    SickBayVisitCreateView,
    SickBayVisitListView,
    MedicalFlagCreateView,
    MedicalFlagListView,
    MedicineInventoryListCreateView,
    MedicineInventoryDetailView,
    AffectedClassesAnalyticsView,
    CommonSymptomsAnalyticsView,
)

urlpatterns = [
    # Sick bay
    path('visits/', SickBayVisitListView.as_view(), name='sickbay-visit-list'),
    path('visits/create/', SickBayVisitCreateView.as_view(), name='sickbay-visit-create'),

    # Medical flags
    path('flags/', MedicalFlagListView.as_view(), name='medical-flag-list'),
    path('flags/create/', MedicalFlagCreateView.as_view(), name='medical-flag-create'),

    # Medicine inventory
    path('inventory/', MedicineInventoryListCreateView.as_view(), name='medicine-inventory-list'),
    path('inventory/<int:pk>/', MedicineInventoryDetailView.as_view(), name='medicine-inventory-detail'),

    # AI analytics
    path('analytics/affected-classes/', AffectedClassesAnalyticsView.as_view(), name='ai-affected-classes'),
    path('analytics/common-symptoms/', CommonSymptomsAnalyticsView.as_view(), name='ai-common-symptoms'),
]
