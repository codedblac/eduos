# institutions/urls.py

from django.urls import path
from institutions import views
from institutions.services.onboarding import OnboardInstitutionView  # DRF APIView for onboarding
from institutions.views import InstitutionStatusUpdateView

urlpatterns = [

    # =============================
    # 📝 School Registration Requests
    # =============================
    path(
        'registrations/',
        views.SchoolRegistrationRequestListView.as_view(),
        name='schoolregistration-list'
    ),
    path(
        'registrations/create/',
        views.SchoolRegistrationRequestCreateView.as_view(),
        name='schoolregistration-create'
    ),
    path(
        'registrations/<uuid:pk>/approve/',
        views.SchoolRegistrationRequestApproveView.as_view(),
        name='schoolregistration-approve'
    ),

    # =============================
    # 🏫 Institution Management
    # =============================
    path(
        '',
        views.InstitutionListView.as_view(),
        name='institution-list'
    ),
    path(
        'create/',
        views.InstitutionCreateView.as_view(),
        name='institution-create'
    ),
    path(
    '<uuid:pk>/status/',
    InstitutionStatusUpdateView.as_view(),
    name='institution-status-update'
    ),

    path(
        '<uuid:pk>/',
        views.InstitutionDetailView.as_view(),
        name='institution-detail'
    ),
    path(
        'me/',
        views.MyInstitutionView.as_view(),
        name='my-institution'
    ),

    # =============================
    # 💳 School Accounts
    # =============================
    path(
        '<uuid:institution_id>/accounts/',
        views.SchoolAccountListCreateView.as_view(),
        name='schoolaccount-list-create'
    ),
    path(
        '<uuid:institution_id>/accounts/<uuid:pk>/',
        views.SchoolAccountDetailView.as_view(),
        name='schoolaccount-detail'
    ),
    
    
    

    # =============================
    # 🤖 AI Recommendations
    # =============================
    path(
        'ai/recommendation/',
        views.InstitutionAIRecommendationView.as_view(),
        name='institution-ai-recommendation'
    ),

    # =============================
    # 📊 Analytics
    # =============================
    path(
        'analytics/overview/',
        views.InstitutionAnalyticsOverviewView.as_view(),
        name='institution-analytics-overview'
    ),

    # =============================
    # 🚀 Automated Onboarding Flow
    # =============================
    path(
        'onboarding/',
        OnboardInstitutionView.as_view(),
        name='institution-onboarding'
    ),
]
