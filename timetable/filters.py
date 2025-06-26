# timetable/filters.py

import django_filters
from .models import Room, SubjectAssignment, TimetableEntry

class RoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains')
    room_type = django_filters.CharFilter(field_name='room_type', lookup_expr='icontains')

    class Meta:
        model = Room
        fields = ['name', 'room_type']


class SubjectAssignmentFilter(django_filters.FilterSet):
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    subject = django_filters.NumberFilter(field_name='subject__id')
    stream = django_filters.NumberFilter(field_name='stream__id')
    lessons_per_week = django_filters.NumberFilter()

    class Meta:
        model = SubjectAssignment
        fields = ['teacher', 'subject', 'stream', 'lessons_per_week']


class TimetableEntryFilter(django_filters.FilterSet):
    day_of_week = django_filters.CharFilter(lookup_expr='iexact')
    timeslot = django_filters.NumberFilter()
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    stream = django_filters.NumberFilter(field_name='stream__id')
    subject = django_filters.NumberFilter(field_name='subject__id')
    room = django_filters.NumberFilter(field_name='room__id')

    class Meta:
        model = TimetableEntry
        fields = ['day_of_week', 'timeslot', 'teacher', 'stream', 'subject', 'room']
