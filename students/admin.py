from django.contrib import admin
from .models import (
    Student,
    GuardianRelationship,
    StudentDocument,
    StudentExitRecord,
    AcademicSnapshot,
    MedicalFlag,
    StudentHistory,
)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('admission_number', 'first_name', 'last_name', 'class_level', 'stream', 'enrollment_status')
    list_filter = ('institution', 'class_level', 'stream', 'enrollment_status', 'gender', 'is_boarding')
    search_fields = ('first_name', 'last_name', 'admission_number', 'national_id', 'birth_certificate_number')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(GuardianRelationship)
class GuardianRelationshipAdmin(admin.ModelAdmin):
    list_display = ('student', 'guardian', 'relationship', 'is_primary')
    list_filter = ('is_primary',)
    search_fields = ('student__first_name', 'student__last_name', 'guardian__user__email')


@admin.register(StudentDocument)
class StudentDocumentAdmin(admin.ModelAdmin):
    list_display = ('student', 'name', 'uploaded_at')
    search_fields = ('student__first_name', 'student__last_name', 'name')


@admin.register(StudentExitRecord)
class StudentExitRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'reason', 'exit_date')
    search_fields = ('student__first_name', 'student__last_name', 'reason')


@admin.register(AcademicSnapshot)
class AcademicSnapshotAdmin(admin.ModelAdmin):
    list_display = ('student', 'term', 'year', 'average_score')
    search_fields = ('student__first_name', 'student__last_name', 'term', 'year')


@admin.register(MedicalFlag)
class MedicalFlagAdmin(admin.ModelAdmin):
    list_display = ('student', 'condition', 'critical', 'created_at')
    list_filter = ('critical',)
    search_fields = ('student__first_name', 'student__last_name', 'condition')


@admin.register(StudentHistory)
class StudentHistoryAdmin(admin.ModelAdmin):
    list_display = ('student', 'change_type', 'date_changed')
    list_filter = ('change_type',)
    search_fields = ('student__first_name', 'student__last_name', 'change_type')
