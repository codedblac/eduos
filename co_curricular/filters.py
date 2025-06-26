import django_filters
from .models import (
    CoCurricularCategory,
    StudentTalentProfile,
    CoCurricularActivity,
    ParticipationRecord,
    Award,
    EventSchedule,
    CoachFeedback
)


class CoCurricularCategoryFilter(django_filters.FilterSet):
    class Meta:
        model = CoCurricularCategory
        fields = {
            'name': ['icontains'],
            'category_type': ['exact'],
        }


class CoCurricularActivityFilter(django_filters.FilterSet):
    class Meta:
        model = CoCurricularActivity
        fields = {
            'name': ['icontains'],
            'category__name': ['icontains'],
            'coach__username': ['icontains'],
            'term__name': ['icontains'],
        }


class StudentTalentProfileFilter(django_filters.FilterSet):
    class Meta:
        model = StudentTalentProfile
        fields = {
            'student__first_name': ['icontains'],
            'student__last_name': ['icontains'],
            'activities__name': ['icontains'],
            'current_skill_level': ['exact'],
        }


class ParticipationRecordFilter(django_filters.FilterSet):
    class Meta:
        model = ParticipationRecord
        fields = {
            'student_profile__student__first_name': ['icontains'],
            'activity__name': ['icontains'],
            'term__name': ['icontains'],
            'status': ['exact'],
        }


class AwardFilter(django_filters.FilterSet):
    class Meta:
        model = Award
        fields = {
            'student_profile__student__first_name': ['icontains'],
            'activity__name': ['icontains'],
            'award_type': ['exact'],
            'level': ['exact'],
        }


class EventScheduleFilter(django_filters.FilterSet):
    class Meta:
        model = EventSchedule
        fields = {
            'activity__name': ['icontains'],
            'scheduled_by__username': ['icontains'],
            'event_date': ['exact', 'gte', 'lte'],
            'event_type': ['exact'],
        }


class CoachFeedbackFilter(django_filters.FilterSet):
    class Meta:
        model = CoachFeedback
        fields = {
            'student_profile__student__first_name': ['icontains'],
            'coach__username': ['icontains'],
            'activity__name': ['icontains'],
            'term__name': ['icontains'],
        }
