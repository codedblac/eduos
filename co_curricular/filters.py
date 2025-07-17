import django_filters
from .models import (
    ActivityCategory,
    Activity,
    StudentProfile,
    StudentActivityParticipation,
    StudentAward,
    ActivityEvent,
    CoachFeedback
)


class ActivityCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = ActivityCategory
        fields = {
            'name': ['icontains'],
            'category_type': ['exact'],
        }


class ActivityFilter(django_filters.FilterSet):
    coach_username = django_filters.CharFilter(field_name='coach_or_patron__username', lookup_expr='icontains')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    class Meta:
        model = Activity
        fields = ['name', 'category_name', 'coach_username', 'is_competitive']


class StudentProfileFilter(django_filters.FilterSet):
    student_first_name = django_filters.CharFilter(field_name='student__first_name', lookup_expr='icontains')
    student_last_name = django_filters.CharFilter(field_name='student__last_name', lookup_expr='icontains')
    preferred_category_name = django_filters.CharFilter(field_name='preferred_categories__name', lookup_expr='icontains')

    class Meta:
        model = StudentProfile
        fields = ['student_first_name', 'student_last_name', 'preferred_category_name']


class StudentActivityParticipationFilter(django_filters.FilterSet):
    student_first_name = django_filters.CharFilter(field_name='student__first_name', lookup_expr='icontains')
    student_last_name = django_filters.CharFilter(field_name='student__last_name', lookup_expr='icontains')
    activity_name = django_filters.CharFilter(field_name='activity__name', lookup_expr='icontains')

    class Meta:
        model = StudentActivityParticipation
        fields = ['student_first_name', 'student_last_name', 'activity_name', 'status', 'skill_level']


class StudentAwardFilter(django_filters.FilterSet):
    student_first_name = django_filters.CharFilter(field_name='student__first_name', lookup_expr='icontains')
    student_last_name = django_filters.CharFilter(field_name='student__last_name', lookup_expr='icontains')
    activity_name = django_filters.CharFilter(field_name='activity__name', lookup_expr='icontains')

    class Meta:
        model = StudentAward
        fields = ['student_first_name', 'student_last_name', 'activity_name', 'level', 'status', 'title']


class ActivityEventFilter(django_filters.FilterSet):
    activity_name = django_filters.CharFilter(field_name='activity__name', lookup_expr='icontains')
    created_by_username = django_filters.CharFilter(field_name='created_by__username', lookup_expr='icontains')

    class Meta:
        model = ActivityEvent
        fields = ['activity_name', 'created_by_username', 'start_date', 'end_date', 'venue']


class CoachFeedbackFilter(django_filters.FilterSet):
    student_first_name = django_filters.CharFilter(field_name='participation__student__first_name', lookup_expr='icontains')
    student_last_name = django_filters.CharFilter(field_name='participation__student__last_name', lookup_expr='icontains')
    coach_username = django_filters.CharFilter(field_name='coach__username', lookup_expr='icontains')
    activity_name = django_filters.CharFilter(field_name='participation__activity__name', lookup_expr='icontains')

    class Meta:
        model = CoachFeedback
        fields = ['student_first_name', 'student_last_name', 'coach_username', 'activity_name', 'rating']
