from rest_framework import serializers
from accounts.serializers import UserSerializer
from institutions.serializers import InstitutionSerializer
from classes.serializers import ClassLevelSerializer
from academics.serializers import TermSerializer, AcademicYearSerializer
from students.serializers import StudentSerializer
from .models import (
    Department, DepartmentUser, DepartmentRoleAssignmentHistory,
    Subject, DepartmentAnnouncement, DepartmentPerformanceNote,
    DepartmentLeaveApproval, DepartmentMeeting, DepartmentKPI,
    DepartmentBudget, DepartmentResource, DepartmentAuditLog,
    DepartmentDocument, DepartmentGoal, DepartmentAnnualPlan,
    DepartmentTask, DepartmentAnalyticsSnapshot
)





class DepartmentSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    parent_department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Department
        fields = '__all__'


class DepartmentUserSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartmentUser
        fields = '__all__'


class DepartmentRoleAssignmentHistorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartmentRoleAssignmentHistory
        fields = '__all__'


class SubjectSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    assigned_teacher = UserSerializer(read_only=True)
    class_levels = ClassLevelSerializer(read_only=True, many=True)

    class Meta:
        model = Subject
        fields = '__all__'


class DepartmentAnnouncementSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    created_by = UserSerializer(read_only=True)
    term = TermSerializer(read_only=True)
    academic_year = AcademicYearSerializer(read_only=True)

    class Meta:
        model = DepartmentAnnouncement
        fields = '__all__'


class DepartmentPerformanceNoteSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    student = StudentSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    term = TermSerializer(read_only=True)

    class Meta:
        model = DepartmentPerformanceNote
        fields = '__all__'


class DepartmentLeaveApprovalSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    staff_member = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentLeaveApproval
        fields = '__all__'


class DepartmentMeetingSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    conducted_by = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentMeeting
        fields = '__all__'


class DepartmentKPISerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    term = TermSerializer(read_only=True)
    reviewed_by = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentKPI
        fields = '__all__'


class DepartmentBudgetSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartmentBudget
        fields = '__all__'


class DepartmentResourceSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartmentResource
        fields = '__all__'


class DepartmentAuditLogSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    actor = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentAuditLog
        fields = '__all__'


class DepartmentDocumentSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    uploaded_by = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentDocument
        fields = '__all__'


class DepartmentGoalSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = DepartmentGoal
        fields = '__all__'


class DepartmentAnnualPlanSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    reviewed_by = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentAnnualPlan
        fields = '__all__'


class DepartmentTaskSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    assigned_to = UserSerializer(read_only=True)

    class Meta:
        model = DepartmentTask
        fields = '__all__'


class DepartmentAnalyticsSnapshotSerializer(serializers.ModelSerializer):
    department = serializers.StringRelatedField(read_only=True)
    term = TermSerializer(read_only=True)

    class Meta:
        model = DepartmentAnalyticsSnapshot
        fields = '__all__'










# --- Department ---
class DepartmentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = [ 'code', 'description', 'institution', 'head',
            'is_active', 'is_deleted'
        ]


# --- DepartmentUser ---
class DepartmentUserCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentUser
        fields = [
            'user', 'department', 'primary_role', 'is_active'
        ]


# --- Subject ---
class SubjectCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = [ 'code', 'description', 'department',
            'assigned_teacher', 'is_examable'
        ]


# --- DepartmentAnnouncement ---
class DepartmentAnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentAnnouncement
        fields = [
            'title', 'message', 'department', 'created_by',
            'created_at', 'is_published'
        ]


# --- DepartmentLeaveApproval ---
class DepartmentLeaveApprovalCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentLeaveApproval
        fields = [
            'staff_member', 'department', 'start_date',
            'end_date', 'reason', 'status', 'reviewed_by', 'reviewed_at'
        ]


# --- DepartmentPerformanceNote ---
class DepartmentPerformanceNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentPerformanceNote
        fields = [
            'student', 'department', 'note', 'created_by', 'created_at'
        ]


# --- DepartmentBudget ---
class DepartmentBudgetCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentBudget
        fields = [
            'department', 'term', 'allocated_amount',
            'spent_amount', 'approved_by', 'approval_date'
        ]


# --- DepartmentKPI ---
class DepartmentKPICreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentKPI
        fields = [
            'department', 'term', 'target_value',
            'achieved_value', 'remarks'
        ]


# --- DepartmentMeeting ---
class DepartmentMeetingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentMeeting
        fields = [
            'department', 'title', 'agenda', 'meeting_date',
            'conducted_by', 'minutes'
        ]


# --- DepartmentResource ---
class DepartmentResourceCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepartmentResource
        fields = [
            'department', 'title', 'description', 'file',
            'uploaded_by', 'uploaded_at'
        ]