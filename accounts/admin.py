from django.contrib import admin
from django.utils.html import format_html
from accounts.models import CustomUser, Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("name", "is_active")}),
        ("Metadata", {"fields": ("created_at",)}),
    )


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "full_name",
        "role",
        "institution",
        "is_active",
        "is_staff",
        "last_login",
        "last_login_ip",
    )
    list_filter = ("role", "is_active", "is_staff", "institution")
    search_fields = ("email", "first_name", "last_name", "institution__name")
    ordering = ("-date_joined",)
    readonly_fields = ("date_joined", "last_updated", "last_login", "last_login_ip", "last_user_agent")

    fieldsets = (
        ("Credentials", {
            "fields": ("email", "password")
        }),
        ("Personal Info", {
            "fields": ("first_name", "last_name", "phone")
        }),
        ("Institutional Info", {
            "fields": ("role", "institution")
        }),
        ("Status", {
            "fields": ("is_active", "is_staff", "is_superuser")
        }),
        ("Metadata", {
            "fields": ("date_joined", "last_updated", "last_login", "last_login_ip", "last_user_agent")
        }),
        ("Permissions", {
            "fields": ("groups", "user_permissions")
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Full Name"
