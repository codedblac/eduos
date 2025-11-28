import django_filters
from .models import Student, StudentHistory


class StudentFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    admission_number = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=Student._meta.get_field('gender').choices)
    enrollment_status = django_filters.ChoiceFilter(choices=Student._meta.get_field('enrollment_status').choices)
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    stream = django_filters.NumberFilter(field_name='stream__id')
    institution = django_filters.NumberFilter(field_name='institution__id')
    date_joined_after = django_filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    date_joined_before = django_filters.DateFilter(field_name='date_joined', lookup_expr='lte')

    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'admission_number',
            'gender', 'enrollment_status',
            'class_level', 'stream', 'institution']


class StudentHistoryFilter(django_filters.FilterSet):
    change_type = django_filters.CharFilter(lookup_expr='icontains')
    student_id = django_filters.UUIDFilter(field_name='student__id')
    student_name = django_filters.CharFilter(method='filter_student_name')
    changed_by = django_filters.NumberFilter(field_name='changed_by__id')
    date_changed_after = django_filters.DateTimeFilter(field_name='date_changed', lookup_expr='gte')
    date_changed_before = django_filters.DateTimeFilter(field_name='date_changed', lookup_expr='lte')

    class Meta:
        model = StudentHistory
        fields = ['change_type', 'student_id', 'changed_by', 'date_changed_after', 'date_changed_before']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            student__first_name__icontains=value
        ) | queryset.filter(
            student__last_name__icontains=value
        )
