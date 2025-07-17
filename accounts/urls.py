from django.urls import path
from accounts import views

urlpatterns = [
    #  Authentication
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('auth/login/', views.CustomLoginView.as_view(), name='login'),
    path('auth/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('auth/forgot-password/', views.ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='reset-password'),

    #  User Management
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user-detail'),

    #  Current Profile
    path('me/', views.MeView.as_view(), name='user-me'),

    #  Account Switching
    path('switch-account/', views.SwitchAccountView.as_view(), name='switch-account'),

    #  Roles Listing
    path('roles/', views.UserRolesView.as_view(), name='user-roles'),
]
