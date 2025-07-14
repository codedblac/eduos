from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        'staff_id', 'full_name', 'institution', 'email', 'phone_number',
        'employment_type', 'designation', 'is_active'
    )
    list_filter = ('institution', 'employment_type', 'designation', 'is_active')
    search_fields = ('staff_id', 'first_name', 'last_name', 'email', 'phone_number')
    readonly_fields = ('id',)  # UUIDs should be readonly
    fieldsets = (
        ('Identity & Personal Details', {
            'fields': (
                'id', 'user', 'institution', 'staff_id',
                'first_name', 'middle_name', 'last_name', 'photo',
                'gender', 'date_of_birth', 'marital_status',
                'national_id', 'email', 'phone_number', 'alternative_contact'
            )
        }),
        ('Professional Info', {
            'fields': (
                'employment_type', 'job_title', 'department',
                'designation', 'joining_date', 'leaving_date',
                'subjects_taught', 'class_levels_handled', 'streams_handled',
                'assigned_roles'
            )
        }),
        ('Qualifications & Experience', {
            'fields': (
                'qualifications', 'professional_certifications',
                'specializations', 'education_history', 'work_experience',
                'transfer_records', 'teaching_history', 'languages_spoken'
            )
        }),
        ('Digital & AI', {
            'fields': (
                'digital_portfolio_url', 'teaching_philosophy', 'performance_score',
                'ai_insights', 'recommended_subjects', 'student_feedback_summary',
                'teacher_ratings', 'disciplinary_flags'
            )
        }),
        ('Duties & Assignments', {
            'fields': (
                'co_curricular_roles', 'dormitory_duties',
                'substitution_availability', 'available_for_virtual_teaching',
                'verified_virtual_tutor', 'assigned_virtual_courses'
            )
        }),
        ('Contact & Emergency', {
            'fields': (
                'residence_address', 'postal_address',
                'emergency_contact_name', 'emergency_contact_number',
                'next_of_kin', 'next_of_kin_relationship'
            )
        }),
        ('Payroll & HR', {
            'fields': (
                'bank_account', 'salary_scale', 'grade', 'payroll_profile',
                'contract_renewal_due', 'promotion_due', 'leave_balance'
            )
        }),
        ('Attendance & Leave', {
            'fields': (
                'daily_checkin_logs', 'teacher_absenteeism_records',
                'leave_history', 'approved_leave_days'
            )
        }),
        ('Other', {
            'fields': ('is_active', 'timetable_pdf')
        }),
    )
