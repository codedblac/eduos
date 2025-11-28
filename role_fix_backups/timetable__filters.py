import django_filters
from .models import (
    PeriodTemplate, Room, SubjectAssignment, TimetableEntry
)
from institutions.models import Institution
from classes.models import Stream
from teachers.models import Teacher
from subjects.models import Subject


class PeriodTemplateFilter(django_filters.FilterSet):
    day = django_filters.CharFilter(lookup_expr='iexact')
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    class_level = django_filters.NumberFilter(field_name='class_level__id')

    class Meta:
        model = PeriodTemplate
        fields = ['day', 'institution', 'class_level']


class RoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    is_lab = django_filters.BooleanFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = Room
        fields = ['name', 'is_lab', 'institution']


class SubjectAssignmentFilter(django_filters.FilterSet):
    teacher = django_filters.ModelChoiceFilter(queryset=Teacher.objects.all())
    subject = django_filters.ModelChoiceFilter(queryset=Subject.objects.all())
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all())
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = SubjectAssignment
        fields = ['teacher', 'subject', 'stream', 'institution']


class TimetableEntryFilter(django_filters.FilterSet):
    period_template__day = django_filters.CharFilter(lookup_expr='iexact')
    period_template__class_level = django_filters.NumberFilter(field_name='period_template__class_level__id')
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all())
    subject = django_filters.ModelChoiceFilter(queryset=Subject.objects.all())
    teacher = django_filters.ModelChoiceFilter(queryset=Teacher.objects.all())

    class Meta:
        model = TimetableEntry
        fields = ['period_template__day', 'period_template__class_level', 'stream', 'subject', 'teacher']
