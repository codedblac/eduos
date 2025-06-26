import django_filters
from .models import Department, DepartmentUser, Subject


class DepartmentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.NumberFilter()

    class Meta:
        model = Department
        fields = ['name', 'institution', 'is_academic', 'type']


class DepartmentUserFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter()
    department = django_filters.NumberFilter()
    role = django_filters.CharFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = DepartmentUser
        fields = ['user', 'department', 'role', 'is_active']


class SubjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    department = django_filters.NumberFilter()
    assigned_teacher = django_filters.NumberFilter()

    class Meta:
        model = Subject
        fields = ['name', 'code', 'department', 'assigned_teacher', 'is_examable', 'is_mapped_to_timetable']
