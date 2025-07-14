import django_filters
from .models import LessonPlan, LessonSchedule, LessonSession


class LessonPlanFilter(django_filters.FilterSet):
    institution = django_filters.NumberFilter(field_name='institution__id')
    teacher = django_filters.NumberFilter(field_name='teacher__id')
    subject = django_filters.NumberFilter(field_name='subject__id')
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    topic = django_filters.NumberFilter(field_name='topic__id')
    week_number = django_filters.NumberFilter()
    is_approved = django_filters.BooleanFilter()

    class Meta:
        model = LessonPlan
        fields = [
            'institution', 'teacher', 'subject',
            'class_level', 'topic', 'week_number', 'is_approved'
        ]


class LessonScheduleFilter(django_filters.FilterSet):
    scheduled_date = django_filters.DateFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=LessonSchedule._meta.get_field('status').choices)
    subject = django_filters.NumberFilter(field_name='lesson_plan__subject__id')
    teacher = django_filters.NumberFilter(field_name='lesson_plan__teacher__id')
    class_level = django_filters.NumberFilter(field_name='lesson_plan__class_level__id')

    class Meta:
        model = LessonSchedule
        fields = ['scheduled_date', 'status', 'subject', 'teacher', 'class_level']


class LessonSessionFilter(django_filters.FilterSet):
    delivered_on = django_filters.DateFromToRangeFilter()
    coverage_status = django_filters.ChoiceFilter(choices=LessonSession._meta.get_field('coverage_status').choices)
    teacher = django_filters.NumberFilter(field_name='lesson_schedule__lesson_plan__teacher__id')
    subject = django_filters.NumberFilter(field_name='lesson_schedule__lesson_plan__subject__id')

    class Meta:
        model = LessonSession
        fields = ['delivered_on', 'coverage_status', 'teacher', 'subject']
