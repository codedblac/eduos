# exams/filters.py

import django_filters
from .models import Exam, ExamResult

class ExamFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    term = django_filters.CharFilter(lookup_expr='iexact')
    year = django_filters.NumberFilter()
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    institution = django_filters.NumberFilter(field_name='institution__id')

    class Meta:
        model = Exam
        fields = ['title', 'term', 'year', 'class_level', 'institution']


class ExamResultFilter(django_filters.FilterSet):
    student = django_filters.NumberFilter(field_name='student__id')
    exam = django_filters.NumberFilter(field_name='exam__id')
    subject = django_filters.NumberFilter(field_name='subject__id')
    stream = django_filters.NumberFilter(field_name='stream__id')
    class_level = django_filters.NumberFilter(field_name='exam__class_level__id')

    class Meta:
        model = ExamResult
        fields = ['student', 'exam', 'subject', 'stream', 'class_level']
