import django_filters
from django.db.models import Q
from exams.models import (
    Exam, ExamSubject, ExamResult, StudentScore,
    GradeBoundary, ExamInsight, ExamPrediction
)
from students.models import Student
from subjects.models import Subject


class ExamFilter(django_filters.FilterSet):
    term = django_filters.CharFilter(field_name="term", lookup_expr='iexact')
    year = django_filters.NumberFilter(field_name="year")
    class_level = django_filters.NumberFilter(field_name="class_level__id")
    stream = django_filters.NumberFilter(field_name="stream__id")
    institution = django_filters.NumberFilter(field_name="institution__id")
    search = django_filters.CharFilter(method='filter_search', label="Search by exam name")

    def filter_search(self, queryset, name, value):
        return queryset.filter(name__icontains=value)

    class Meta:
        model = Exam
        fields = ['term', 'year', 'class_level', 'stream', 'institution']


class ExamSubjectFilter(django_filters.FilterSet):
    exam = django_filters.NumberFilter(field_name="exam__id")
    subject = django_filters.NumberFilter(field_name="subject__id")

    class Meta:
        model = ExamSubject
        fields = ['exam', 'subject']


class ExamResultFilter(django_filters.FilterSet):
    exam = django_filters.NumberFilter(field_name="exam__id")
    student = django_filters.NumberFilter(field_name="student__id")
    min_score = django_filters.NumberFilter(field_name="average_score", lookup_expr='gte')
    max_score = django_filters.NumberFilter(field_name="average_score", lookup_expr='lte')
    grade = django_filters.CharFilter(field_name="grade", lookup_expr='iexact')

    class Meta:
        model = ExamResult
        fields = ['exam', 'student', 'grade']


class StudentScoreFilter(django_filters.FilterSet):
    exam_subject = django_filters.NumberFilter(field_name="exam_subject__id")
    student = django_filters.NumberFilter(field_name="student__id")
    grade = django_filters.CharFilter(field_name="grade", lookup_expr='iexact')
    min_score = django_filters.NumberFilter(field_name="score", lookup_expr='gte')
    max_score = django_filters.NumberFilter(field_name="score", lookup_expr='lte')

    class Meta:
        model = StudentScore
        fields = ['exam_subject', 'student', 'grade']


class GradeBoundaryFilter(django_filters.FilterSet):
    subject = django_filters.NumberFilter(field_name="subject__id")
    institution = django_filters.NumberFilter(field_name="institution__id")
    grade = django_filters.CharFilter(field_name="grade", lookup_expr='iexact')

    class Meta:
        model = GradeBoundary
        fields = ['institution', 'subject', 'grade']


class ExamInsightFilter(django_filters.FilterSet):
    exam = django_filters.NumberFilter(field_name="exam__id")
    subject = django_filters.NumberFilter(field_name="subject__id")

    class Meta:
        model = ExamInsight
        fields = ['exam', 'subject']


class ExamPredictionFilter(django_filters.FilterSet):
    subject = django_filters.NumberFilter(field_name="subject__id")
    class_level = django_filters.NumberFilter(field_name="class_level__id")
    stream = django_filters.NumberFilter(field_name="stream__id")
    term = django_filters.CharFilter(field_name="term", lookup_expr='iexact')
    year = django_filters.NumberFilter(field_name="year")
    institution = django_filters.NumberFilter(field_name="institution__id")

    class Meta:
        model = ExamPrediction
        fields = ['subject', 'class_level', 'stream', 'term', 'year', 'institution']
