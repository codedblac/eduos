from django_filters import rest_framework as filters
from .models import (
    Staff,
    StaffProfile,
    EmploymentHistory,
    StaffQualification,
    StaffLeave,
    StaffDisciplinaryAction,
    StaffAttendance,
)


class StaffFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    institution = filters.NumberFilter(field_name='institution_id')
    department = filters.NumberFilter(field_name='department_id')
    staff_category = filters.ChoiceFilter(choices=Staff._meta.get_field('staff_category').choices)
    is_active = filters.BooleanFilter()

    class Meta:
        model = Staff
        fields = ['user', 'institution', 'department', 'staff_category', 'is_active']


class StaffProfileFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    gender = filters.ChoiceFilter(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    nationality = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StaffProfile
        fields = ['user', 'gender', 'nationality']


class EmploymentHistoryFilter(filters.FilterSet):
    staff = filters.NumberFilter(field_name='staff_id')
    department = filters.NumberFilter(field_name='department_id')
    employment_type = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = EmploymentHistory
        fields = ['staff', 'department', 'employment_type']


class StaffQualificationFilter(filters.FilterSet):
    staff = filters.NumberFilter(field_name='staff_id')
    qualification = filters.CharFilter(lookup_expr='icontains')
    institution_name = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = StaffQualification
        fields = ['staff', 'qualification', 'institution_name']


class StaffLeaveFilter(filters.FilterSet):
    staff = filters.NumberFilter(field_name='staff_id')
    leave_type = filters.CharFilter(lookup_expr='icontains')
    is_approved = filters.BooleanFilter()
    start_date = filters.DateFilter()
    end_date = filters.DateFilter()

    class Meta:
        model = StaffLeave
        fields = ['staff', 'leave_type', 'is_approved', 'start_date', 'end_date']


class StaffDisciplinaryActionFilter(filters.FilterSet):
    staff = filters.NumberFilter(field_name='staff_id')
    is_resolved = filters.BooleanFilter()
    date_reported = filters.DateFromToRangeFilter()

    class Meta:
        model = StaffDisciplinaryAction
        fields = ['staff', 'is_resolved', 'date_reported']


class StaffAttendanceFilter(filters.FilterSet):
    staff = filters.NumberFilter(field_name='staff_id')
    date = filters.DateFromToRangeFilter()
    status = filters.ChoiceFilter(choices=StaffAttendance._meta.get_field('status').choices)

    class Meta:
        model = StaffAttendance
        fields = ['staff', 'date', 'status']
