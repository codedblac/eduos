# accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import CustomUser, Institution


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'is_active', 'mpesa_paybill', 'theme_mode', 'created_at')
    list_filter = ('is_active', 'theme_mode', 'created_at')
    search_fields = ('name', 'location', 'mpesa_paybill', 'mpesa_shortcode')
    readonly_fields = ('created_at',)


class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'role', 'institution', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('role', 'institution', 'is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        (_('Account Info'), {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('first_name', 'last_name', 'phone')}),
        (_('Institution Details'), {'fields': ('institution', 'role')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important Dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'phone', 'institution', 'role', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

    search_fields = ('email', 'first_name', 'last_name', 'phone')
    readonly_fields = ('date_joined', 'last_login')


admin.site.register(CustomUser, CustomUserAdmin)
