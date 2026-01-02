from django import forms
from django.contrib import admin
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from .models import Institution, SchoolAccount, SchoolRegistrationRequest

User = get_user_model()


# ---------------------------
# Inline School Accounts
# ---------------------------
class SchoolAccountInline(admin.TabularInline):
    model = SchoolAccount
    extra = 1
    fields = (
        'account_name', 'account_number', 'payment_type',
        'bank_name', 'mpesa_till_number', 'is_default'
    )
    show_change_link = True
    readonly_fields = ('created_at', 'updated_at')


# ---------------------------
# Custom Institution Form
# ---------------------------
class InstitutionAdminForm(forms.ModelForm):

    admin_email = forms.EmailField(required=True, label="Institution Admin Email")
    admin_first_name = forms.CharField(required=False, label="Admin First Name")
    admin_last_name = forms.CharField(required=False, label="Admin Last Name", initial="Admin")
    admin_password = forms.CharField(
        required=False,
        label="Admin Password",
        widget=forms.PasswordInput,
        help_text="Leave blank to generate a random password"
    )

    # NOTE: custom_modules intentionally NOT in Meta.fields (it is NOT a model field)

    class Meta:
        model = Institution
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # LAZY imports to avoid circular dependencies
        from modules.models import Plan, SystemModule

        # Plan dropdown
        self.fields['plan'] = forms.ModelChoiceField(
            queryset=Plan.objects.all().order_by('is_custom', 'name'),
            required=True,
            label="Subscription Plan",
            empty_label=None
        )

        # Custom modules (form-only field)
        self.fields['custom_modules'] = forms.ModelMultipleChoiceField(
            queryset=SystemModule.objects.all(),
            required=False,
            label="Custom Modules (only if Custom Plan)"
        )

        # Hide field initially if plan is not custom
        instance = getattr(self, "instance", None)
        if instance and instance.pk and instance.plan and not instance.plan.is_custom:
            self.fields['custom_modules'].widget.attrs['style'] = "display:none;"

    def clean(self):
        cleaned_data = super().clean()
        plan = cleaned_data.get("plan")

        if plan and plan.is_custom and not cleaned_data.get("custom_modules"):
            raise forms.ValidationError("Please select at least one module for a Custom plan.")

        return cleaned_data

    def save(self, commit=True):
        from modules.models import SchoolModule
        from institutions.services.onboarding import OnboardingService

        institution = super().save(commit=False)

        # Auto-code
        if not institution.code:
            institution.code = OnboardingService.generate_institution_code()

        institution.plan = self.cleaned_data['plan']

        if commit:
            institution.save()

        # Assign modules
        plan = institution.plan

        if plan.is_custom:
            modules = self.cleaned_data.get("custom_modules", [])
        else:
            modules = plan.modules.all()

        for module in modules:
            SchoolModule.assign_custom_module(institution, module)

        # Create admin user
        if not institution.admin_user_id:
            admin_email = self.cleaned_data["admin_email"]
            first_name = self.cleaned_data.get("admin_first_name") or institution.name
            last_name = self.cleaned_data.get("admin_last_name") or "Admin"
            password = self.cleaned_data.get("admin_password") or User.objects.make_random_password()

            admin_user = User.objects.create_user(
                email=admin_email,
                first_name=first_name,
                last_name=last_name,
                primary_role=User.Role.INSTITUTION_ADMIN,
                institution=institution,
                password=password,
                is_staff=True
            )
            admin_user.save()
            admin_user.modules.set(modules)

            institution.admin_user = admin_user
            institution.save()

            try:
                send_mail(
                    subject="Your Institution Admin Account Has Been Created",
                    message=(
                        f"Hello {admin_user.get_full_name()},\n\n"
                        f"Your institution '{institution.name}' has been registered.\n"
                        f"Login credentials:\nEmail: {admin_user.email}\nPassword: {password}\n\n"
                        "Please change your password after first login.\n\n"
                        "Welcome to EduOS!"
                    ),
                    from_email="no-reply@eduos.com",
                    recipient_list=[admin_user.email],
                    fail_silently=True,
                )
            except:
                pass

        return institution


# ---------------------------
# Institution Admin
# ---------------------------
@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    form = InstitutionAdminForm

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
            'fields': ('name', 'code', 'registration_number', 'institution_type',
                       'school_type', 'plan')
        }),
        ("Location & Contact", {
            'fields': ('country', 'county', 'sub_county', 'ward', 'village',
                       'address', 'phone', 'email', 'website')
        }),
        ("Branding", {
            'fields': ('logo', 'primary_color', 'secondary_color', 'theme_mode')
        }),
        ("Ownership & Establishment", {
            'fields': ('ownership', 'funding_source', 'established_year')
        }),
        ("Institution Admin", {
            'fields': ('admin_email', 'admin_first_name', 'admin_last_name', 'admin_password')
        }),
        ("Timestamps & Metadata", {
            'fields': ('created_at', 'updated_at', 'extra_info', 'admin_user')
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'admin_user')


# ---------------------------
# School Account Admin
# ---------------------------
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


# ---------------------------
# School Registration Request Admin
# ---------------------------
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
        from django.contrib import messages
        from institutions.services.onboarding import OnboardingService

        approved_count = 0
        for reg_request in queryset.filter(approved=False):
            OnboardingService.onboard_institution(
                school_name=reg_request.school_name,
                email=reg_request.email,
                phone=reg_request.phone,
                county=reg_request.county,
                country=reg_request.country,
                sub_county=reg_request.sub_county,
                ward=reg_request.ward,
                village=reg_request.village,
                institution_type=reg_request.institution_type,
                school_type=reg_request.school_type,
                reg_request=reg_request,
                plan_name=getattr(reg_request, "plan_name", "basic")
            )
            approved_count += 1

        self.message_user(
            request,
            f"{approved_count} registration request(s) approved and onboarded.",
            level=messages.SUCCESS
        )

    approve_registration.short_description = "Approve selected registration requests"
