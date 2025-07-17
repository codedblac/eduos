from django.contrib import admin
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration, AlumniDonation,
    AlumniMentorship, AlumniAchievement, AlumniNotification, AlumniFeedback,
    AlumniMembership, AlumniEmployment, AlumniVolunteer,
    AlumniJobOpportunity, AlumniTestimonial
)


class BaseInstitutionAdmin(admin.ModelAdmin):
    """Limit queryset and auto-assign institution on create."""
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(institution=request.user.institution)

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.institution_id:
            obj.institution = request.user.institution
        obj.save()


@admin.register(AlumniProfile)
class AlumniProfileAdmin(BaseInstitutionAdmin):
    list_display = ('student', 'profession', 'university', 'is_verified', 'joined_on')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'email', 'profession', 'university')
    list_filter = ('is_verified', 'institution')


@admin.register(AlumniEvent)
class AlumniEventAdmin(BaseInstitutionAdmin):
    list_display = ('title', 'event_date', 'location', 'is_virtual')
    search_fields = ('title', 'location')
    list_filter = ('event_date', 'is_virtual', 'institution')


@admin.register(AlumniEventRegistration)
class AlumniEventRegistrationAdmin(BaseInstitutionAdmin):
    list_display = ('event', 'alumni', 'registered_on', 'is_attended')
    list_filter = ('is_attended', 'event')
    search_fields = ('event__title', 'alumni__student__user__first_name')


@admin.register(AlumniDonation)
class AlumniDonationAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'amount', 'purpose', 'campaign_name', 'payment_method', 'donated_on')
    search_fields = ('purpose', 'campaign_name')
    list_filter = ('payment_method', 'institution')


@admin.register(AlumniMentorship)
class AlumniMentorshipAdmin(BaseInstitutionAdmin):
    list_display = ('mentor', 'mentee', 'status', 'start_date', 'meeting_frequency')
    list_filter = ('status', 'institution')


@admin.register(AlumniAchievement)
class AlumniAchievementAdmin(BaseInstitutionAdmin):
    list_display = ('title', 'alumni', 'date_achieved')
    search_fields = ('title', 'alumni__student__user__first_name')
    list_filter = ('institution',)


@admin.register(AlumniNotification)
class AlumniNotificationAdmin(BaseInstitutionAdmin):
    list_display = ('title', 'recipient', 'type', 'sent_on', 'is_read')
    search_fields = ('title', 'message')
    list_filter = ('type', 'is_read', 'institution')


@admin.register(AlumniFeedback)
class AlumniFeedbackAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'submitted_on', 'responded')
    list_filter = ('responded', 'institution')


@admin.register(AlumniMembership)
class AlumniMembershipAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'membership_number', 'is_active_member', 'membership_paid_on', 'membership_tier')
    search_fields = ('membership_number',)
    list_filter = ('is_active_member', 'membership_tier', 'institution')


@admin.register(AlumniEmployment)
class AlumniEmploymentAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'company_name', 'position', 'currently_employed', 'start_date')
    search_fields = ('company_name', 'position', 'industry')
    list_filter = ('currently_employed', 'industry', 'institution')


@admin.register(AlumniVolunteer)
class AlumniVolunteerAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'area_of_interest', 'availability', 'registered_on')
    search_fields = ('area_of_interest', 'alumni__student__user__first_name')
    list_filter = ('area_of_interest', 'institution')


@admin.register(AlumniJobOpportunity)
class AlumniJobOpportunityAdmin(BaseInstitutionAdmin):
    list_display = ('title', 'company_name', 'posted_on', 'expires_on')
    search_fields = ('title', 'company_name', 'location')
    list_filter = ('posted_on', 'institution')


@admin.register(AlumniTestimonial)
class AlumniTestimonialAdmin(BaseInstitutionAdmin):
    list_display = ('alumni', 'approved', 'submitted_on')
    list_filter = ('approved', 'institution')
    search_fields = ('alumni__student__user__first_name', 'message')
