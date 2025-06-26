from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    AdmissionSession, Applicant, AdmissionDocument, EntranceExam,
    AdmissionOffer, AdmissionComment
)


@admin.register(AdmissionSession)
class AdmissionSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'academic_year', 'intake_date', 'application_deadline', 'level', 'institution', 'is_active')
    list_filter = ('institution', 'level', 'is_active')
    search_fields = ('name', 'academic_year__name')
    ordering = ('-intake_date',)


class AdmissionDocumentInline(admin.TabularInline):
    model = AdmissionDocument
    extra = 0


class AdmissionCommentInline(admin.StackedInline):
    model = AdmissionComment
    extra = 0


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = (
        'first_name', 'last_name', 'gender', 'phone', 'email', 'entry_class_level',
        'admission_session', 'application_status', 'submitted_on'
    )
    list_filter = ('gender', 'admission_session', 'entry_class_level', 'application_status')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'parent_name')
    inlines = [AdmissionDocumentInline, AdmissionCommentInline]
    autocomplete_fields = ['admission_session', 'entry_class_level']
    readonly_fields = ('submitted_on',)
    ordering = ('-submitted_on',)


@admin.register(AdmissionDocument)
class AdmissionDocumentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'document_type', 'uploaded_on')
    list_filter = ('document_type',)
    search_fields = ('applicant__first_name', 'applicant__last_name', 'document_type')
    autocomplete_fields = ['applicant']


@admin.register(EntranceExam)
class EntranceExamAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'exam_date', 'score', 'passed')
    list_filter = ('exam_date', 'passed')
    search_fields = ('applicant__first_name', 'applicant__last_name')
    autocomplete_fields = ['applicant']


@admin.register(AdmissionOffer)
class AdmissionOfferAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'issued_on', 'expiry_date', 'status')
    list_filter = ('status',)
    search_fields = ('applicant__first_name', 'applicant__last_name')
    autocomplete_fields = ['applicant']


@admin.register(AdmissionComment)
class AdmissionCommentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'author', 'created_at')
    search_fields = ('applicant__first_name', 'applicant__last_name', 'author__username')
    autocomplete_fields = ['applicant', 'author']
