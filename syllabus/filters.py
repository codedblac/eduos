import django_filters
from .models import SyllabusTopic, SyllabusProgress, CurriculumSubject


class SyllabusTopicFilter(django_filters.FilterSet):
    curriculum = django_filters.CharFilter(field_name="curriculum_subject__curriculum__name", lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name="curriculum_subject__subject__name", lookup_expr='icontains')
    class_level = django_filters.CharFilter(field_name="curriculum_subject__class_level__name", lookup_expr='icontains')
    title = django_filters.CharFilter(field_name="title", lookup_expr='icontains')

    class Meta:
        model = SyllabusTopic
        fields = ['curriculum', 'subject', 'class_level', 'title']


class SyllabusProgressFilter(django_filters.FilterSet):
    teacher = django_filters.CharFilter(field_name="teacher__username", lookup_expr='icontains')
    status = django_filters.ChoiceFilter(field_name="status", choices=SyllabusProgress.STATUS_CHOICES)
    topic_title = django_filters.CharFilter(field_name="topic__title", lookup_expr='icontains')
    curriculum = django_filters.CharFilter(field_name="topic__curriculum_subject__curriculum__name", lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name="topic__curriculum_subject__subject__name", lookup_expr='icontains')

    class Meta:
        model = SyllabusProgress
        fields = ['teacher', 'status', 'topic_title', 'curriculum', 'subject']


class CurriculumSubjectFilter(django_filters.FilterSet):
    curriculum = django_filters.CharFilter(field_name="curriculum__name", lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name="subject__name", lookup_expr='icontains')
    class_level = django_filters.CharFilter(field_name="class_level__name", lookup_expr='icontains')

    class Meta:
        model = CurriculumSubject
        fields = ['curriculum', 'subject', 'class_level']
