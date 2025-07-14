import django_filters
from .models import (
    Assessment, AssessmentSession, StudentAnswer,
    PerformanceTrend, AssessmentWeight
)
from students.models import Student
from subjects.models import Subject
from academics.models import Term
from classes.models import ClassLevel
from institutions.models import Institution


class AssessmentFilter(django_filters.FilterSet):
    scheduled_after = django_filters.DateFilter(field_name="scheduled_date", lookup_expr='gte')
    scheduled_before = django_filters.DateFilter(field_name="scheduled_date", lookup_expr='lte')
    is_published = django_filters.BooleanFilter()

    class Meta:
        model = Assessment
        fields = [
            'institution', 'subject', 'class_level', 'term',
            'type', 'is_published'
        ]


class AssessmentSessionFilter(django_filters.FilterSet):
    submitted_after = django_filters.DateFilter(field_name="submitted_at", lookup_expr='gte')
    submitted_before = django_filters.DateFilter(field_name="submitted_at", lookup_expr='lte')
    is_graded = django_filters.BooleanFilter()

    class Meta:
        model = AssessmentSession
        fields = ['student', 'assessment', 'is_graded']


class StudentAnswerFilter(django_filters.FilterSet):
    min_marks = django_filters.NumberFilter(field_name="marks_awarded", lookup_expr='gte')
    max_marks = django_filters.NumberFilter(field_name="marks_awarded", lookup_expr='lte')
    auto_graded = django_filters.BooleanFilter()

    class Meta:
        model = StudentAnswer
        fields = ['session', 'question', 'auto_graded']


class PerformanceTrendFilter(django_filters.FilterSet):
    min_score = django_filters.NumberFilter(field_name="average_score", lookup_expr='gte')
    max_score = django_filters.NumberFilter(field_name="average_score", lookup_expr='lte')

    class Meta:
        model = PerformanceTrend
        fields = ['student', 'subject', 'term']


class AssessmentWeightFilter(django_filters.FilterSet):
    class Meta:
        model = AssessmentWeight
        fields = ['institution', 'term', 'subject', 'type']
