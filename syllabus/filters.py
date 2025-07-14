import django_filters
from .models import SyllabusTopic, SyllabusProgress, CurriculumSubject


class SyllabusTopicFilter(django_filters.FilterSet):
    curriculum = django_filters.CharFilter(
        field_name="curriculum_subject__curriculum__name",
        lookup_expr='icontains',
        label="Curriculum"
    )
    subject = django_filters.CharFilter(
        field_name="curriculum_subject__subject__name",
        lookup_expr='icontains',
        label="Subject"
    )
    class_level = django_filters.CharFilter(
        field_name="curriculum_subject__class_level__name",
        lookup_expr='icontains',
        label="Class Level"
    )
    term = django_filters.CharFilter(
        field_name="curriculum_subject__term__name",
        lookup_expr='icontains',
        label="Term"
    )
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr='icontains',
        label="Topic Title"
    )

    class Meta:
        model = SyllabusTopic
        fields = ['curriculum', 'subject', 'class_level', 'term', 'title']


class SyllabusProgressFilter(django_filters.FilterSet):
    teacher = django_filters.CharFilter(
        field_name="teacher__username",
        lookup_expr='icontains',
        label="Teacher Username"
    )
    status = django_filters.ChoiceFilter(
        field_name="status",
        choices=SyllabusProgress._meta.get_field('status').choices,
        label="Progress Status"
    )
    topic_title = django_filters.CharFilter(
        field_name="topic__title",
        lookup_expr='icontains',
        label="Topic Title"
    )
    curriculum = django_filters.CharFilter(
        field_name="topic__curriculum_subject__curriculum__name",
        lookup_expr='icontains',
        label="Curriculum"
    )
    subject = django_filters.CharFilter(
        field_name="topic__curriculum_subject__subject__name",
        lookup_expr='icontains',
        label="Subject"
    )
    class_level = django_filters.CharFilter(
        field_name="topic__curriculum_subject__class_level__name",
        lookup_expr='icontains',
        label="Class Level"
    )

    class Meta:
        model = SyllabusProgress
        fields = ['teacher', 'status', 'topic_title', 'curriculum', 'subject', 'class_level']


class CurriculumSubjectFilter(django_filters.FilterSet):
    curriculum = django_filters.CharFilter(
        field_name="curriculum__name",
        lookup_expr='icontains',
        label="Curriculum"
    )
    subject = django_filters.CharFilter(
        field_name="subject__name",
        lookup_expr='icontains',
        label="Subject"
    )
    class_level = django_filters.CharFilter(
        field_name="class_level__name",
        lookup_expr='icontains',
        label="Class Level"
    )
    term = django_filters.CharFilter(
        field_name="term__name",
        lookup_expr='icontains',
        label="Term"
    )

    class Meta:
        model = CurriculumSubject
        fields = ['curriculum', 'subject', 'class_level', 'term']
