from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django import forms
from django.urls import path
from django.http import JsonResponse

from accounts.models import CustomUser
from institutions.models import Institution
from modules.models import SystemModule, ModulePermission


# ---------------------
# SystemModule Admin
# ---------------------
@admin.register(SystemModule)
class SystemModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "is_default", "display_permissions")
    list_filter = ("is_default",)
    search_fields = ("name",)
    ordering = ("name",)

    #
    # FIXED: SystemModule does NOT have "permissions"
    # All permissions live inside module.linked_group.permissions
    #
    def display_permissions(self, obj):
        if not obj.linked_group:
            return "No group"

        perms = obj.linked_group.permissions.all()
        if not perms:
            return "No permissions"

        return ", ".join([p.codename for p in perms])

    display_permissions.short_description = "Permissions"

    #
    # Admin endpoint for JS requests (used by your custom_user_modules.js)
    #
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("module-data/", self.admin_site.admin_view(self.module_data_view)),
        ]
        return custom_urls + urls

    def module_data_view(self, request):
        ids = request.GET.get("ids", "")
        ids_list = [int(i) for i in ids.split(",") if i.isdigit()]

        groups = []
        permissions = []

        modules = SystemModule.objects.filter(id__in=ids_list)

        for module in modules:
            # group exists?
            if module.linked_group:
                groups.append(module.linked_group.id)

                # FIXED: get permissions from the linked group
                perms = module.linked_group.permissions.all().values_list("id", flat=True)
                permissions.extend(list(perms))

        return JsonResponse({
            "groups": list(set(groups)),
            "permissions": list(set(permissions)),
        })


# ---------------------
# Forms for CustomUser
# ---------------------
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Confirm Password", widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ("email", "first_name", "last_name", "primary_role", "institution", "modules")

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
        "display_modules",
        "is_active",
        "is_staff",
        "is_superuser",
        "last_login",
        "last_login_ip",
    )
    list_filter = ("primary_role", "is_active", "is_staff", "is_superuser", "institution", "modules")
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
            "fields": ("email", "password1", "password2", "first_name", "last_name",
                       "primary_role", "institution", "modules"),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = "Full Name"

    def display_modules(self, obj):
        return ", ".join([m.name for m in obj.modules.all()])
    display_modules.short_description = "Modules"

    class Media:
        js = ("admin/js/custom_user_modules.js",)

    # -------------------------
    # Auto-assign modules, groups & permissions
    # -------------------------
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        # Assign default modules if not selected
        if not obj.modules.exists():
            default_modules = SystemModule.objects.filter(is_default=True)
            role_module_map = {
                CustomUser.Role.SUPER_ADMIN: default_modules,
                CustomUser.Role.INSTITUTION_ADMIN: default_modules,
                CustomUser.Role.TEACHER: default_modules.filter(name__in=["Academics", "Attendance"]),
                CustomUser.Role.STUDENT: default_modules.filter(name__in=["Academics", "Fee Management"]),
                CustomUser.Role.STAFF: default_modules,
            }
            modules_to_assign = role_module_map.get(obj.primary_role, default_modules)
            obj.modules.set(modules_to_assign)

        # Add linked groups
        for module in obj.modules.all():
            if module.linked_group:
                obj.groups.add(module.linked_group)

        # Assign module permissions
        all_perms = ModulePermission.objects.filter(module__in=obj.modules.all())
        obj.module_permissions.set(all_perms)

        obj.save()
