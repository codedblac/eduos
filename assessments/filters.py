from django_filters import rest_framework as filters
from .models import Assessment, AssessmentSession, Question, AssessmentResult


class AssessmentFilter(filters.FilterSet):
    term = filters.NumberFilter(field_name="term__id")
    subject = filters.NumberFilter(field_name="subject__id")
    class_level = filters.NumberFilter(field_name="class_level__id")
    type = filters.CharFilter(field_name="assessment_type__name", lookup_expr='icontains')
    date = filters.DateFromToRangeFilter()

    class Meta:
        model = Assessment
        fields = ['term', 'subject', 'class_level', 'type', 'date']


class AssessmentSessionFilter(filters.FilterSet):
    assessment = filters.NumberFilter(field_name="assessment__id")
    student = filters.NumberFilter(field_name="student__id")
    status = filters.ChoiceFilter(choices=[
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('missed', 'Missed')
    ])

    class Meta:
        model = AssessmentSession
        fields = ['assessment', 'student', 'status']


class QuestionFilter(filters.FilterSet):
    difficulty = filters.CharFilter(lookup_expr='iexact')
    topic = filters.NumberFilter(field_name="topic__id")
    subject = filters.NumberFilter(field_name="subject__id")
    type = filters.CharFilter(field_name="question_type", lookup_expr='iexact')

    class Meta:
        model = Question
        fields = ['difficulty', 'topic', 'subject', 'type']


class AssessmentResultFilter(filters.FilterSet):
    assessment = filters.NumberFilter(field_name="assessment__id")
    student = filters.NumberFilter(field_name="student__id")
    subject = filters.NumberFilter(field_name="subject__id")
    grade = filters.CharFilter(field_name="grade", lookup_expr='iexact')

    class Meta:
        model = AssessmentResult
        fields = ['assessment', 'student', 'subject', 'grade']
