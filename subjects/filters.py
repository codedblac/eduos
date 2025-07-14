import django_filters
from .models import (
    Subject, SubjectClassLevel, SubjectTeacher,
    SubjectPrerequisite, SubjectAssessmentWeight,
    SubjectGradingScheme, SubjectResource, SubjectVersion
)


class SubjectFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    code = django_filters.CharFilter(lookup_expr='icontains')
    curriculum_type = django_filters.CharFilter(lookup_expr='iexact')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    institution_id = django_filters.NumberFilter(field_name='institution__id')
    is_core = django_filters.BooleanFilter()
    is_elective = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()
    archived = django_filters.BooleanFilter()

    class Meta:
        model = Subject
        fields = [
            'name', 'code', 'curriculum_type', 'category_name',
            'institution_id', 'is_core', 'is_elective',
            'is_active', 'archived'
        ]


class SubjectClassLevelFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    class_level_id = django_filters.NumberFilter(field_name='class_level__id')
    compulsory = django_filters.BooleanFilter()

    class Meta:
        model = SubjectClassLevel
        fields = ['subject_id', 'class_level_id', 'compulsory']


class SubjectTeacherFilter(django_filters.FilterSet):
    teacher_id = django_filters.NumberFilter(field_name='teacher__id')
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    is_head = django_filters.BooleanFilter()

    class Meta:
        model = SubjectTeacher
        fields = ['teacher_id', 'subject_id', 'is_head']


class SubjectPrerequisiteFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    prerequisite_id = django_filters.NumberFilter(field_name='prerequisite__id')
    is_corequisite = django_filters.BooleanFilter()

    class Meta:
        model = SubjectPrerequisite
        fields = ['subject_id', 'prerequisite_id', 'is_corequisite']


class SubjectAssessmentWeightFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    term_id = django_filters.NumberFilter(field_name='term__id')
    component = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = SubjectAssessmentWeight
        fields = ['subject_id', 'term_id', 'component']


class SubjectGradingSchemeFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    grade = django_filters.CharFilter(lookup_expr='iexact')

    class Meta:
        model = SubjectGradingScheme
        fields = ['subject_id', 'grade']


class SubjectResourceFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    title = django_filters.CharFilter(lookup_expr='icontains')
    type = django_filters.ChoiceFilter(choices=[
        ('document', 'Document'),
        ('video', 'Video'),
        ('interactive', 'Interactive'),
        ('link', 'Link'),
    ])

    class Meta:
        model = SubjectResource
        fields = ['subject_id', 'title', 'type']


class SubjectVersionFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name='subject__id')
    version_number = django_filters.CharFilter(lookup_expr='iexact')
    created_by_id = django_filters.NumberFilter(field_name='created_by__id')

    class Meta:
        model = SubjectVersion
        fields = ['subject_id', 'version_number', 'created_by_id']
