from django.urls import path
from institutions import views

urlpatterns = [
    #  Institution Management
    path('', views.InstitutionListView.as_view(), name='institution-list'),
    path('create/', views.InstitutionCreateView.as_view(), name='institution-create'),
    path('<int:pk>/', views.InstitutionDetailView.as_view(), name='institution-detail'),
    path('me/', views.MyInstitutionView.as_view(), name='my-institution'),

    #  School Accounts
    path('<int:institution_id>/accounts/', views.SchoolAccountListCreateView.as_view(), name='schoolaccount-list-create'),
    path('accounts/<int:pk>/', views.SchoolAccountDetailView.as_view(), name='schoolaccount-detail'),

    #  AI Features 
    path('ai/recommendation/', views.InstitutionAIRecommendationView.as_view(), name='institution-ai-recommendation'),

    #  Analytics 
    path('analytics/overview/', views.InstitutionAnalyticsOverviewView.as_view(), name='institution-analytics-overview'),
]
