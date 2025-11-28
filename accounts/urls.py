from django.urls import path
from accounts.views import (
    CreateInstitutionAdminView,
    RegisterView,
    CustomLoginView,  # Optional: only if still using token-based login
    EmailTokenObtainPairView,  # JWT login
    ChangePasswordView,
    ForgotPasswordView,
    PasswordResetConfirmView,
    UserListCreateView,
    UserDetailView,
    MeView,
    SwitchAccountView,
    UserRolesView,
)

urlpatterns = [
    # Institution Admin Creation
    path("institution-admins/create/", CreateInstitutionAdminView.as_view(), name="create-institution-admin"),

    # Authentication
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', EmailTokenObtainPairView.as_view(), name='login'),  # JWT-based login
    # path('auth/login-token/', CustomLoginView.as_view(), name='login-token'),  # OPTIONAL: remove if not used

    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-password/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='reset-password'),

    # User Management
    path('users/', UserListCreateView.as_view(), name='user-list-create'),
    path('users/<int:pk>/', UserDetailView.as_view(), name='user-detail'),

    # Current Profile Access
    path('me/', MeView.as_view(), name='user-me'),

    # Account Switching
    path('switch-account/', SwitchAccountView.as_view(), name='switch-account'),

    # Roles Listing
    path('roles/', UserRolesView.as_view(), name='user-roles'),
]
