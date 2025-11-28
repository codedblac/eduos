from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from accounts.models import CustomUser, SystemModule
from institutions.models import Institution

# ---------------------
# SystemModule Admin
# ---------------------
@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default")
    list_filter = ("is_default",)
    search_fields = ("name",)
    ordering = ("name",)

# ---------------------
# Forms for CustomUser
# ---------------------
class CustomUserCreationForm(forms.ModelForm):
    """Form for creating new users via admin, ensures password hashing."""
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "primary_role", "institution", "modules")

    def clean_password2(self):
        pw1 = self.cleaned_data.get("password1")
        pw2 = self.cleaned_data.get("password2")
        if pw1 and pw2 and pw1 != pw2:
            raise forms.ValidationError("Passwords do not match.")
        return pw2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            self.save_m2m()
        return user

class CustomUserChangeForm(forms.ModelForm):
    """Form for updating users in admin."""
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = "__all__"

    def save(self, commit=True):
        user = super().save(commit=False)
        pw = self.cleaned_data.get("password")
        if pw:
            user.set_password(pw)
        if commit:
            user.save()
            self.save_m2m()
        return user

# ---------------------
# CustomUser Admin
# ---------------------
@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    model = CustomUser

    list_display = (
        "email",
        "full_name",
        "primary_role",
        "institution",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "last_login_ip",
    )
    list_filter = ("primary_role", "is_active", "is_staff", "is_superuser", "institution")
    search_fields = ("email", "first_name", "last_name", "institution__name")
    ordering = ("-date_joined",)
    readonly_fields = (
        "date_joined",
        "last_updated",
        "last_login",
        "last_login_ip",
        "last_user_agent",
    )

    fieldsets = (
        ("Credentials", {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name", "phone", "profile_picture")}),
        ("Institutional Info", {"fields": ("primary_role", "institution", "modules")}),
        ("Status", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Metadata", {"fields": ("date_joined", "last_updated", "last_login", "last_login_ip", "last_user_agent")}),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "primary_role", "institution", "modules"),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Full Name"
