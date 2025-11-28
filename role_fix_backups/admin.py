from django.contrib import admin
from .models import Institution, SchoolAccount, SchoolRegistrationRequest


# =========================
# Inline School Accounts
# =========================
class SchoolAccountInline(admin.TabularInline):
    model = SchoolAccount
    extra = 1
    fields = ('account_name', 'account_number', 'payment_type', 'bank_name', 'mpesa_till_number', 'is_default')
    show_change_link = True
    readonly_fields = ('created_at', 'updated_at')


# =========================
# Institution Admin
# =========================
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'institution_type', 'school_type',
        'country', 'county', 'sub_county', 'ward',
        'phone', 'email', 'established_year', 'created_at',
    )
    list_filter = ('institution_type', 'school_type', 'country', 'county')
    search_fields = ('name', 'code', 'email', 'phone', 'registration_number')
    ordering = ('name',)
    inlines = [SchoolAccountInline]

    fieldsets = (
        ("Basic Information", {
            'fields': ('name', 'code', 'registration_number', 'institution_type', 'school_type')
        }),
        ("Location & Contact", {
            'fields': ('country', 'county', 'sub_county', 'ward', 'village', 'address', 'phone', 'email', 'website')
        }),
        ("Branding", {
            'fields': ('logo', 'primary_color', 'secondary_color', 'theme_mode')
        }),
        ("Ownership & Establishment", {
            'fields': ('ownership', 'funding_source', 'established_year')
        }),
        ("Timestamps & Metadata", {
            'fields': ('created_at', 'updated_at', 'extra_info')
        }),
    )

    readonly_fields = ('created_at', 'updated_at')


# =========================
# School Account Admin
# =========================
@admin.register(SchoolAccount)
class SchoolAccountAdmin(admin.ModelAdmin):
    list_display = (
        'institution', 'account_name', 'account_number', 'payment_type',
        'bank_name', 'mpesa_till_number', 'is_default',
        'created_at', 'updated_at',
    )
    list_filter = ('payment_type', 'is_default', 'institution__county', 'institution__school_type')
    search_fields = ('account_name', 'account_number', 'bank_name', 'institution__name')
    ordering = ('-created_at',)
    autocomplete_fields = ('institution',)
    readonly_fields = ('created_at', 'updated_at')


# =========================
# School Registration Request Admin
# =========================
@admin.register(SchoolRegistrationRequest)
class SchoolRegistrationRequestAdmin(admin.ModelAdmin):
    list_display = (
        'school_name', 'code', 'institution_type', 'school_type',
        'country', 'county', 'sub_county', 'ward',
        'submitted_at', 'approved', 'admin_created'
    )
    list_filter = ('school_type', 'institution_type', 'county', 'approved', 'submitted_at')
    search_fields = ('school_name', 'code', 'email', 'county', 'sub_county', 'ward')
    ordering = ('-submitted_at',)
    readonly_fields = ('submitted_at', 'approved_at', 'admin_created')

    actions = ['approve_registration']

    def approve_registration(self, request, queryset):
        """
        Admin action to approve selected registration requests.
        """
        from django.contrib import messages
        from django.utils import timezone
        from django.contrib.auth import get_user_model

        User = get_user_model()
        approved_count = 0

        for req in queryset.filter(approved=False):
            # Create Institution
            institution = Institution.objects.create(
                name=req.school_name,
                code=req.code,
                country=req.country,
                county=req.county,
                sub_county=req.sub_county,
                ward=req.ward,
                village=req.village,
                institution_type=req.institution_type,
                school_type=req.school_type
            )

            # Create Institution Admin
            temp_password = User.objects.make_random_password()
            User.objects.create_user(
                username=f"{req.code}_admin",
                email=req.email,
                password=temp_password,
                primary_role='ADMIN',
                institution=institution,
                is_active=True
            )

            # Update registration request
            req.approved = True
            req.approved_at = timezone.now()
            req.admin_created = True
            req.save()

            approved_count += 1

        self.message_user(request, f"{approved_count} registration request(s) approved.", level=messages.SUCCESS)

    approve_registration.short_description = "Approve selected school registration requests"
