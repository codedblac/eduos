import django_filters
from django.db.models import Q
from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AttendanceStatus
)
from accounts.models import CustomUser
from students.models import Student
from classes.models import ClassLevel, Stream
from subjects.models import Subject


class SchoolAttendanceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date", lookup_expr="exact")
    date_range = django_filters.DateFromToRangeFilter(field_name="date")
    user = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    role = django_filters.CharFilter(method="filter_by_role")

    class Meta:
        model = SchoolAttendanceRecord
        fields = ['institution', 'user', 'date', 'date_range', 'source']

    def filter_by_role(self, queryset, name, value):
        return queryset.filter(user__role__iexact=value)


class ClassAttendanceFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name="date", lookup_expr="exact")
    date_range = django_filters.DateFromToRangeFilter(field_name="date")
    status = django_filters.ChoiceFilter(choices=AttendanceStatus.choices)
    subject = django_filters.ModelChoiceFilter(queryset=Subject.objects.all(), required=False)
    student = django_filters.ModelChoiceFilter(queryset=Student.objects.all(), required=False)
    teacher = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all(), required=False)
    class_level = django_filters.ModelChoiceFilter(queryset=ClassLevel.objects.all(), required=False)
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all(), required=False)
    source = django_filters.CharFilter(field_name='source', lookup_expr='iexact')

    class Meta:
        model = ClassAttendanceRecord
        fields = [
            'institution', 'date', 'date_range', 'status',
            'student', 'teacher', 'subject', 'class_level',
            'stream', 'source'
        ]
