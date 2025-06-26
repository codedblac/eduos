import django_filters
from lessons.models import LessonPlan, LessonSession, LessonSchedule


class LessonPlanFilter(django_filters.FilterSet):
    subject = django_filters.CharFilter(field_name="subject__name", lookup_expr='icontains')
    class_level = django_filters.CharFilter(field_name="class_level__name", lookup_expr='icontains')
    teacher = django_filters.CharFilter(field_name="teacher__username", lookup_expr='icontains')
    term = django_filters.CharFilter(field_name="term__name", lookup_expr='icontains')

    class Meta:
        model = LessonPlan
        fields = ['term', 'subject', 'class_level', 'teacher']


class LessonSessionFilter(django_filters.FilterSet):
    coverage_status = django_filters.ChoiceFilter(choices=[
        ('covered', 'Covered'),
        ('pending', 'Pending'),
        ('skipped', 'Skipped')
    ])
    delivered_on = django_filters.DateFromToRangeFilter()

    class Meta:
        model = LessonSession
        fields = ['coverage_status', 'delivered_on']


class LessonScheduleFilter(django_filters.FilterSet):
    scheduled_date = django_filters.DateFromToRangeFilter()
    status = django_filters.ChoiceFilter(choices=[
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('missed', 'Missed')
    ])

    class Meta:
        model = LessonSchedule
        fields = ['scheduled_date', 'status']
