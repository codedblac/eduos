from rest_framework import serializers
from .models import Teacher
from institutions.models import Institution
from subjects.models import Subject
from classes.models import ClassLevel, Stream
from payroll.models import BankAccount
from accounts.serializers import UserSerializer  


class TeacherSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    institution = serializers.SlugRelatedField(slug_field='name', read_only=True)
    subjects_taught = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Subject.objects.all(), required=False
    )
    class_levels_handled = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=ClassLevel.objects.all(), required=False
    )
    streams_handled = serializers.SlugRelatedField(
        many=True, slug_field='name', queryset=Stream.objects.all(), required=False
    )
    bank_account = serializers.SlugRelatedField(
        slug_field='account_number', queryset=BankAccount.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Teacher
        fields = [
            # Identity
            'id', 'user', 'staff_id', 'institution', 'photo', 'first_name', 'middle_name', 'last_name',
            'gender', 'date_of_birth', 'national_id', 'marital_status', 'bio',

            # Professional
            'employment_type', 'job_title', 'department', 'designation',
            'joining_date', 'leaving_date',
            'subjects_taught', 'class_levels_handled', 'streams_handled', 'assigned_roles',

            # Qualifications
            'qualifications', 'professional_certifications', 'specializations',
            'education_history', 'languages_spoken',

            # Work History
            'work_experience', 'transfer_records', 'teaching_history',

            # Digital & AI
            'digital_portfolio_url', 'teaching_philosophy', 'performance_score',
            'ai_insights', 'recommended_subjects', 'student_feedback_summary',
            'teacher_ratings', 'disciplinary_flags',

            # Extra Duties
            'co_curricular_roles', 'dormitory_duties', 'substitution_availability',
            'available_for_virtual_teaching', 'verified_virtual_tutor', 'assigned_virtual_courses',

            # Contact
            'email', 'phone_number', 'alternative_contact',
            'emergency_contact_name', 'emergency_contact_number',
            'residence_address', 'postal_address',
            'next_of_kin', 'next_of_kin_relationship',

            # HR & Payroll
            'bank_account', 'salary_scale', 'grade', 'payroll_profile',
            'contract_renewal_due', 'promotion_due',
            'leave_balance', 'approved_leave_days',

            # Attendance
            'daily_checkin_logs', 'teacher_absenteeism_records', 'leave_history',

            # Audit
            'created_by', 'updated_by', 'created_at', 'updated_at',

            # Misc
            'is_active', 'timetable_pdf'
        ]
        read_only_fields = ['created_at', 'updated_at', 'created_by', 'updated_by', 'user', 'institution']


class TeacherMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'full_name', 'staff_id', 'email', 'phone_number']
