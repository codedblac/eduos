import django_filters
from django.db.models import Q
from .models import (
    StaffProfile, JobVacancy, JobApplication, EmploymentContract,
    LeaveType, LeaveApplication, AttendanceLog, PerformanceReview,
    DisciplinaryAction, StaffDocument
)


class StaffProfileFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name="department__name", lookup_expr='icontains')
    branch = django_filters.CharFilter(field_name="branch__name", lookup_expr='icontains')
    role = django_filters.CharFilter(field_name="role__name", lookup_expr='icontains')
    employment_type = django_filters.CharFilter(field_name="employment_type", lookup_expr='iexact')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')
    designation = django_filters.CharFilter(field_name="designation", lookup_expr='icontains')

    class Meta:
        model = StaffProfile
        fields = ['department', 'branch', 'role', 'employment_type', 'status', 'designation']


class JobVacancyFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=JobVacancy.STATUS_CHOICES)

    class Meta:
        model = JobVacancy
        fields = ['title', 'status']


class JobApplicationFilter(django_filters.FilterSet):
    applicant_name = django_filters.CharFilter(field_name="applicant__name", lookup_expr='icontains')
    job_title = django_filters.CharFilter(field_name="job__title", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=JobApplication.STATUS_CHOICES)

    class Meta:
        model = JobApplication
        fields = ['job_title', 'status']


class EmploymentContractFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    contract_type = django_filters.CharFilter(field_name="contract_type", lookup_expr='icontains')
    end_date_before = django_filters.DateFilter(field_name="end_date", lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name="end_date", lookup_expr='gte')

    class Meta:
        model = EmploymentContract
        fields = ['staff', 'contract_type', 'end_date_before', 'end_date_after']


class LeaveApplicationFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    leave_type = django_filters.CharFilter(field_name="leave_type__name", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(choices=LeaveApplication.STATUS_CHOICES)
    start_month = django_filters.NumberFilter(field_name="start_date__month")
    start_year = django_filters.NumberFilter(field_name="start_date__year")

    class Meta:
        model = LeaveApplication
        fields = ['staff', 'leave_type', 'status', 'start_month', 'start_year']


class AttendanceLogFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    date = django_filters.DateFilter(field_name="timestamp__date")
    month = django_filters.NumberFilter(field_name="timestamp__month")
    year = django_filters.NumberFilter(field_name="timestamp__year")

    class Meta:
        model = AttendanceLog
        fields = ['staff', 'date', 'month', 'year']


class PerformanceReviewFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    reviewer = django_filters.NumberFilter(field_name="reviewer__id")
    min_score = django_filters.NumberFilter(field_name="score", lookup_expr='gte')
    max_score = django_filters.NumberFilter(field_name="score", lookup_expr='lte')

    class Meta:
        model = PerformanceReview
        fields = ['staff', 'reviewer', 'min_score', 'max_score']


class DisciplinaryActionFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    action_type = django_filters.CharFilter(field_name="action_type", lookup_expr='icontains')
    date_from = django_filters.DateFilter(field_name="date", lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name="date", lookup_expr='lte')

    class Meta:
        model = DisciplinaryAction
        fields = ['staff', 'action_type', 'date_from', 'date_to']


class StaffDocumentFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    document_type = django_filters.CharFilter(field_name="document_type", lookup_expr='icontains')

    class Meta:
        model = StaffDocument
        fields = ['staff', 'document_type']
