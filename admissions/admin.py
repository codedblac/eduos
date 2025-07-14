from django.contrib import admin
from .models import (
    AdmissionSession,
    Applicant,
    AdmissionDocument,
    EntranceExam,
    AdmissionOffer,
    AdmissionWorkflowStep,
    AdmissionComment,
    AdmissionAuditLog,
)


@admin.register(AdmissionSession)
class AdmissionSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'academic_year', 'level', 'intake_date', 'application_deadline', 'is_active')
    list_filter = ('institution', 'academic_year', 'is_active')
    search_fields = ('name', 'institution__name', 'level__name')
    ordering = ('-intake_date',)


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'admission_session', 'entry_class_level', 'application_status', 'submitted_on', 'is_converted_to_student')
    list_filter = ('admission_session__institution', 'application_status', 'entry_class_level')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'parent_name', 'guardian_name')
    readonly_fields = ('submitted_on',)
    ordering = ('-submitted_on',)


@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'applicant', 'uploaded_on')
    list_filter = ('document_type',)
    search_fields = ('applicant__first_name', 'applicant__last_name')
    ordering = ('-uploaded_on',)


@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'exam_date', 'score', 'passed')
    list_filter = ('exam_date', 'passed')
    search_fields = ('applicant__first_name', 'applicant__last_name')
    ordering = ('-exam_date',)


@admin.register(AdmissionOffer)
class AdmissionOfferAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'issued_on', 'expiry_date', 'status', 'acceptance_date')
    list_filter = ('status',)
    search_fields = ('applicant__first_name', 'applicant__last_name')
    ordering = ('-issued_on',)


@admin.register(AdmissionWorkflowStep)
class AdmissionWorkflowStepAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'step_name', 'completed', 'completed_by', 'timestamp')
    list_filter = ('step_name', 'completed', 'completed_by')
    search_fields = ('applicant__first_name', 'applicant__last_name', 'step_name')
    ordering = ('-timestamp',)


@admin.register(AdmissionComment)
class AdmissionCommentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'author', 'created_at')
    search_fields = ('applicant__first_name', 'applicant__last_name', 'author__email')
    ordering = ('-created_at',)


@admin.register(AdmissionAuditLog)
class AdmissionAuditLogAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'action', 'actor', 'record_id', 'timestamp')
    list_filter = ('model_name', 'action')
    search_fields = ('actor__email', 'model_name', 'record_id')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
