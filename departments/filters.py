import django_filters
from django_filters import rest_framework as filters
from departments.models import *
from django.contrib.auth import get_user_model

User = get_user_model()


class DepartmentFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    institution = filters.NumberFilter(field_name='institution_id')
    parent_department = filters.NumberFilter(field_name='parent_department_id')
    type = filters.CharFilter()
    is_academic = filters.BooleanFilter()
    is_deleted = filters.BooleanFilter()

    class Meta:
        model = Department
        fields = ['name', 'institution', 'type', 'is_academic', 'parent_department', 'is_deleted']


class DepartmentUserFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name='user_id')
    department = filters.NumberFilter(field_name='department_id')
    role = filters.ChoiceFilter(choices=DepartmentUser.ROLE_CHOICES)
    is_active = filters.BooleanFilter()

    class Meta:
        model = DepartmentUser
        fields = ['user', 'department', 'role', 'is_active']


class DepartmentRoleAssignmentHistoryFilter(filters.FilterSet):
    user = filters.NumberFilter(field_name='user_id')
    department = filters.NumberFilter(field_name='department_id')
    role = filters.ChoiceFilter(choices=DepartmentUser.ROLE_CHOICES)
    assigned_on__gte = filters.DateTimeFilter(field_name='assigned_on', lookup_expr='gte')
    revoked_on__isnull = filters.BooleanFilter()

    class Meta:
        model = DepartmentRoleAssignmentHistory
        fields = ['user', 'department', 'role', 'assigned_on__gte', 'revoked_on__isnull']


class SubjectFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    department = filters.NumberFilter(field_name='department_id')
    assigned_teacher = filters.NumberFilter(field_name='assigned_teacher_id')
    is_examable = filters.BooleanFilter()
    is_mapped_to_timetable = filters.BooleanFilter()
    is_linked_to_elearning = filters.BooleanFilter()

    class Meta:
        model = Subject
        fields = ['name', 'department', 'assigned_teacher', 'is_examable', 'is_mapped_to_timetable', 'is_linked_to_elearning']


class DepartmentAnnouncementFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    created_by = filters.NumberFilter(field_name='created_by_id')
    term = filters.NumberFilter(field_name='term_id')
    academic_year = filters.NumberFilter(field_name='academic_year_id')
    created_at__gte = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')

    class Meta:
        model = DepartmentAnnouncement
        fields = ['department', 'created_by', 'term', 'academic_year', 'created_at__gte']


class DepartmentPerformanceNoteFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    student = filters.NumberFilter(field_name='student_id')
    term = filters.NumberFilter(field_name='term_id')
    approved = filters.BooleanFilter()

    class Meta:
        model = DepartmentPerformanceNote
        fields = ['department', 'student', 'term', 'approved']


class DepartmentLeaveApprovalFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    staff_member = filters.NumberFilter(field_name='staff_member_id')
    status = filters.CharFilter()
    requested_at__gte = filters.DateTimeFilter(field_name='requested_at', lookup_expr='gte')

    class Meta:
        model = DepartmentLeaveApproval
        fields = ['department', 'staff_member', 'status', 'requested_at__gte']


class DepartmentMeetingFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    date = filters.DateFilter()
    date__gte = filters.DateFilter(field_name='date', lookup_expr='gte')
    date__lte = filters.DateFilter(field_name='date', lookup_expr='lte')

    class Meta:
        model = DepartmentMeeting
        fields = ['department', 'date']


class DepartmentKPIFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    term = filters.NumberFilter(field_name='term_id')

    class Meta:
        model = DepartmentKPI
        fields = ['department', 'term']


class DepartmentBudgetFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    fiscal_year = filters.CharFilter()

    class Meta:
        model = DepartmentBudget
        fields = ['department', 'fiscal_year']


class DepartmentResourceFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    status = filters.CharFilter()

    class Meta:
        model = DepartmentResource
        fields = ['department', 'status']


class DepartmentAuditLogFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    actor = filters.NumberFilter(field_name='actor_id')
    timestamp__gte = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    action = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = DepartmentAuditLog
        fields = ['department', 'actor', 'timestamp__gte', 'action']


class DepartmentDocumentFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    uploaded_by = filters.NumberFilter(field_name='uploaded_by_id')
    uploaded_on__gte = filters.DateTimeFilter(field_name='uploaded_on', lookup_expr='gte')

    class Meta:
        model = DepartmentDocument
        fields = ['department', 'uploaded_by', 'uploaded_on__gte']


class DepartmentGoalFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    status = filters.CharFilter()
    target_date__lte = filters.DateFilter(field_name='target_date', lookup_expr='lte')
    target_date__gte = filters.DateFilter(field_name='target_date', lookup_expr='gte')

    class Meta:
        model = DepartmentGoal
        fields = ['department', 'status', 'target_date__gte', 'target_date__lte']


class DepartmentAnnualPlanFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    year = filters.CharFilter()
    reviewed_by = filters.NumberFilter(field_name='reviewed_by_id')

    class Meta:
        model = DepartmentAnnualPlan
        fields = ['department', 'year', 'reviewed_by']


class DepartmentTaskFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    assigned_to = filters.NumberFilter(field_name='assigned_to_id')
    status = filters.CharFilter()
    due_date__lte = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    due_date__gte = filters.DateFilter(field_name='due_date', lookup_expr='gte')

    class Meta:
        model = DepartmentTask
        fields = ['department', 'assigned_to', 'status', 'due_date__gte', 'due_date__lte']


class DepartmentAnalyticsSnapshotFilter(filters.FilterSet):
    department = filters.NumberFilter(field_name='department_id')
    term = filters.NumberFilter(field_name='term_id')
    snapshot_date = filters.DateFilter()

    class Meta:
        model = DepartmentAnalyticsSnapshot
        fields = ['department', 'term', 'snapshot_date']
