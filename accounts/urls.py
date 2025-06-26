# accounts/urls.py

from django.urls import path
from .views import (
    LoginView,
    RegisterUserView,
    UserDetailView,
    UserUpdateView,
    InstitutionCreateView,
    InstitutionDetailView
)

app_name = "accounts"  # good for namespacing in large systems

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterUserView.as_view(), name="register"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
    path("users/<int:pk>/update/", UserUpdateView.as_view(), name="user-update"),
    path("institutions/create/", InstitutionCreateView.as_view(), name="institution-create"),
    path("institutions/<int:pk>/", InstitutionDetailView.as_view(), name="institution-detail"),
]
