import django_filters
from .models import (
    StaffHRRecord, JobPosting, JobApplication, Contract,
    LeaveType, LeaveRequest, AttendanceRecord, PerformanceReview,
    DisciplinaryAction, HRDocument
)


class StaffHRRecordFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name="department__name", lookup_expr='icontains')
    branch = django_filters.CharFilter(field_name="branch__name", lookup_expr='icontains')
    designation = django_filters.CharFilter(field_name="designation", lookup_expr='icontains')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')

    class Meta:
        model = StaffHRRecord
        fields = ['department', 'branch', 'designation', 'status']


class JobPostingFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.CharFilter(field_name="department__name", lookup_expr='icontains')

    class Meta:
        model = JobPosting
        fields = ['title', 'department']


class JobApplicationFilter(django_filters.FilterSet):
    applicant_name = django_filters.CharFilter(field_name="applicant_name", lookup_expr='icontains')
    job_title = django_filters.CharFilter(field_name="job__title", lookup_expr='icontains')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')

    class Meta:
        model = JobApplication
        fields = ['applicant_name', 'job_title', 'status']


class ContractFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    contract_type = django_filters.CharFilter(field_name="contract_type", lookup_expr='icontains')
    end_date_before = django_filters.DateFilter(field_name="end_date", lookup_expr='lte')
    end_date_after = django_filters.DateFilter(field_name="end_date", lookup_expr='gte')

    class Meta:
        model = Contract
        fields = ['staff', 'contract_type', 'end_date_before', 'end_date_after']


class LeaveRequestFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    leave_type = django_filters.CharFilter(field_name="leave_type__name", lookup_expr='icontains')
    status = django_filters.CharFilter(field_name="status", lookup_expr='iexact')
    start_month = django_filters.NumberFilter(field_name="start_date__month")
    start_year = django_filters.NumberFilter(field_name="start_date__year")

    class Meta:
        model = LeaveRequest
        fields = ['staff', 'leave_type', 'status', 'start_month', 'start_year']


class AttendanceRecordFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    date = django_filters.DateFilter(field_name="date")
    month = django_filters.NumberFilter(field_name="date__month")
    year = django_filters.NumberFilter(field_name="date__year")

    class Meta:
        model = AttendanceRecord
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
    incident_date_from = django_filters.DateFilter(field_name="incident_date", lookup_expr='gte')
    incident_date_to = django_filters.DateFilter(field_name="incident_date", lookup_expr='lte')
    resolved = django_filters.BooleanFilter(field_name="resolved")

    class Meta:
        model = DisciplinaryAction
        fields = ['staff', 'incident_date_from', 'incident_date_to', 'resolved']


class HRDocumentFilter(django_filters.FilterSet):
    staff = django_filters.NumberFilter(field_name="staff__id")
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')

    class Meta:
        model = HRDocument
        fields = ['staff', 'title']
