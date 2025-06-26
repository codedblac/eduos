# staff/filters.py

import django_filters
from .models import StaffProfile, EmploymentHistory, StaffLeave, StaffDisciplinaryRecord, StaffDocument


class StaffProfileFilter(django_filters.FilterSet):
    department = django_filters.CharFilter(field_name='department__name', lookup_expr='icontains')
    designation = django_filters.CharFilter(lookup_expr='icontains')
    employment_type = django_filters.ChoiceFilter(choices=StaffProfile.EMPLOYMENT_TYPE_CHOICES)
    gender = django_filters.ChoiceFilter(choices=StaffProfile.GENDER_CHOICES)
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = StaffProfile
        fields = ['institution', 'department', 'employment_type', 'gender', 'is_active']


class EmploymentHistoryFilter(django_filters.FilterSet):
    designation = django_filters.CharFilter(lookup_expr='icontains')
    from_date = django_filters.DateFilter(field_name='start_date', lookup_expr='gte')
    to_date = django_filters.DateFilter(field_name='end_date', lookup_expr='lte')

    class Meta:
        model = EmploymentHistory
        fields = ['staff_profile', 'designation', 'start_date', 'end_date']


class StaffLeaveFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=StaffLeave.STATUS_CHOICES)
    leave_type = django_filters.CharFilter(lookup_expr='icontains')
    date_requested_from = django_filters.DateFilter(field_name='requested_on', lookup_expr='gte')
    date_requested_to = django_filters.DateFilter(field_name='requested_on', lookup_expr='lte')

    class Meta:
        model = StaffLeave
        fields = ['staff_profile', 'leave_type', 'status']


class StaffDisciplinaryRecordFilter(django_filters.FilterSet):
    issue_date_from = django_filters.DateFilter(field_name='issued_on', lookup_expr='gte')
    issue_date_to = django_filters.DateFilter(field_name='issued_on', lookup_expr='lte')
    resolution_status = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StaffDisciplinaryRecord
        fields = ['staff_profile', 'violation_type', 'resolution_status']


class StaffDocumentFilter(django_filters.FilterSet):
    document_type = django_filters.CharFilter(lookup_expr='icontains')
    uploaded_from = django_filters.DateFilter(field_name='uploaded_on', lookup_expr='gte')
    uploaded_to = django_filters.DateFilter(field_name='uploaded_on', lookup_expr='lte')

    class Meta:
        model = StaffDocument
        fields = ['staff_profile', 'document_type', 'uploaded_on']
