from rest_framework import serializers
from accounts.models import CustomUser
from accounts.serializers import UserSerializer
from django.conf import settings

from .models import (
    JobPosting, JobApplication, StaffHRRecord, Contract,
    Department, SchoolBranch, LeaveType, LeaveRequest,
    AttendanceRecord, PerformanceReview, DisciplinaryAction,
    HRDocument, HRAuditLog
)
from django.contrib.auth import get_user_model
User = get_user_model()


class JobVacancySerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPosting
        fields = '__all__'


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = '__all__'


class BranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolBranch
        fields = '__all__'


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), source='user', write_only=True)

    class Meta:
        model = StaffHRRecord
        fields = [
            'id', 'user', 'user_id', 'institution', 'branch', 'department',
            'designation', 'employee_id', 'date_joined', 'status', 'photo'
        ]


class EmploymentContractSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)

    class Meta:
        model = Contract
        fields = ['id', 'staff', 'staff_id', 'contract_type', 'start_date', 'end_date', 'signed_document', 'is_active']


class LeaveTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeaveType
        fields = '__all__'


class LeaveApplicationSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)

    class Meta:
        model = LeaveRequest
        fields = ['id', 'staff', 'staff_id', 'leave_type', 'start_date', 'end_date', 'reason', 'status', 'requested_on']


class AttendanceLogSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)

    class Meta:
        model = AttendanceRecord
        fields = ['id', 'staff', 'staff_id', 'date', 'check_in', 'check_out', 'method']


class PerformanceReviewSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)
    reviewer_name = serializers.SerializerMethodField()

    class Meta:
        model = PerformanceReview
        fields = ['id', 'staff', 'staff_id', 'review_period_start', 'review_period_end', 'reviewer', 'reviewer_name', 'score', 'comments', 'submitted_on']

    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name() if obj.reviewer else None


class DisciplinaryActionSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)
    added_by_name = serializers.SerializerMethodField()

    class Meta:
        model = DisciplinaryAction
        fields = ['id', 'staff', 'staff_id', 'incident_date', 'description', 'outcome', 'resolved', 'added_by', 'added_by_name']

    def get_added_by_name(self, obj):
        return obj.added_by.get_full_name() if obj.added_by else None


class StaffDocumentSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    staff_id = serializers.PrimaryKeyRelatedField(queryset=StaffHRRecord.objects.all(), source='staff', write_only=True)

    class Meta:
        model = HRDocument
        fields = ['id', 'staff', 'staff_id', 'title', 'document', 'uploaded_at']


class HRMLogSerializer(serializers.ModelSerializer):
    staff = StaffProfileSerializer(read_only=True)
    actor_name = serializers.SerializerMethodField()

    class Meta:
        model = HRAuditLog
        fields = ['id', 'staff', 'action', 'performed_by', 'actor_name', 'timestamp', 'details']

    def get_actor_name(self, obj):
        return obj.performed_by.get_full_name() if obj.performed_by else None


class StaffHRRecordSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='user',
        write_only=True
    )
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = StaffHRRecord
        fields = [
            'id', 'user', 'user_id', 'institution', 'branch', 'branch_name',
            'department', 'department_name', 'designation', 'employee_id',
            'date_joined', 'status', 'photo'
    ]   
        
    
    
    
class ContractSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = Contract
        fields = [
            'id', 'staff', 'staff_name', 'contract_type',
            'start_date', 'end_date', 'signed_document', 'is_active'
        ]

class SchoolBranchSerializer(serializers.ModelSerializer):
    institution_name = serializers.CharField(source='institution.name', read_only=True)

    class Meta:
        model = SchoolBranch
        fields = ['id', 'institution', 'institution_name', 'location']
        
        
class LeaveRequestSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            'id', 'staff', 'staff_name', 'leave_type', 'leave_type_name',
            'start_date', 'end_date', 'reason', 'status', 'requested_on'
        ]

class AttendanceRecordSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = AttendanceRecord
        fields = [
            'id', 'staff', 'staff_name', 'date',
            'check_in', 'check_out', 'method'
        ]

class HRDocumentSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)

    class Meta:
        model = HRDocument
        fields = ['id', 'staff', 'staff_name', 'title', 'document', 'uploaded_at']


class JobPostingSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = JobPosting
        fields = [
            'id',
            'title',
            'department',
            'department_name',
            'description',
            'requirements',
            'is_internal',
            'posted_on',
            'deadline']
        read_only_fields = ['id', 'posted_on']