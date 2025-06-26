from django.contrib import admin
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration,
    AlumniDonation, AlumniMentorship, AlumniAchievement,
    AlumniNotification, AlumniFeedback, AlumniMembership,
    AlumniEmployment, AlumniVolunteer
)

@admin.register(AlumniProfile)
class AlumniProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'email', 'profession', 'organization', 'is_verified', 'institution')
    search_fields = ('student__first_name', 'student__last_name', 'email', 'profession', 'organization')
    list_filter = ('is_verified', 'institution', 'country')
    readonly_fields = ('joined_on',)


@admin.register(AlumniEvent)
class AlumniEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'event_date', 'event_time', 'location', 'created_by', 'institution')
    search_fields = ('title', 'location')
    list_filter = ('event_date', 'institution')


@admin.register(AlumniEventRegistration)
class AlumniEventRegistrationAdmin(admin.ModelAdmin):
    list_display = ('event', 'alumni', 'registered_on', 'is_attended')
    list_filter = ('event', 'is_attended')
    search_fields = ('alumni__student__first_name', 'alumni__student__last_name')


@admin.register(AlumniDonation)
class AlumniDonationAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'amount', 'purpose', 'donated_on', 'institution')
    search_fields = ('alumni__student__first_name', 'alumni__student__last_name', 'purpose')
    list_filter = ('donated_on', 'institution')


@admin.register(AlumniMentorship)
class AlumniMentorshipAdmin(admin.ModelAdmin):
    list_display = ('mentor', 'mentee', 'start_date', 'status', 'institution')
    search_fields = ('mentor__student__first_name', 'mentee__first_name')
    list_filter = ('status', 'institution')


@admin.register(AlumniAchievement)
class AlumniAchievementAdmin(admin.ModelAdmin):
    list_display = ('title', 'alumni', 'date_achieved', 'institution')
    search_fields = ('title', 'alumni__student__first_name')
    list_filter = ('date_achieved', 'institution')


@admin.register(AlumniNotification)
class AlumniNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'sent_by', 'type', 'sent_on', 'is_read')
    list_filter = ('type', 'is_read', 'sent_on', 'institution')
    search_fields = ('title', 'recipient__student__first_name')


@admin.register(AlumniFeedback)
class AlumniFeedbackAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'submitted_on', 'responded', 'institution')
    search_fields = ('alumni__student__first_name', 'message')
    list_filter = ('responded', 'institution')


@admin.register(AlumniMembership)
class AlumniMembershipAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'membership_number', 'is_active_member', 'membership_paid_on', 'next_due_date')
    search_fields = ('alumni__student__first_name', 'membership_number')
    list_filter = ('is_active_member', 'institution')


@admin.register(AlumniEmployment)
class AlumniEmploymentAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'company_name', 'position', 'start_date', 'currently_employed', 'institution')
    search_fields = ('alumni__student__first_name', 'company_name', 'position')
    list_filter = ('currently_employed', 'institution')


@admin.register(AlumniVolunteer)
class AlumniVolunteerAdmin(admin.ModelAdmin):
    list_display = ('alumni', 'area_of_interest', 'availability', 'registered_on', 'institution')
    search_fields = ('alumni__student__first_name', 'area_of_interest')
    list_filter = ('availability', 'institution')
