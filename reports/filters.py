import django_filters
from .models import GeneratedReport, ReportStudentPerformance, ReportSubjectBreakdown


class GeneratedReportFilter(django_filters.FilterSet):
    term = django_filters.CharFilter(lookup_expr='iexact')
    year = django_filters.CharFilter(lookup_expr='exact')
    report_type = django_filters.ChoiceFilter(choices=GeneratedReport.ReportType.choices)
    access_level = django_filters.ChoiceFilter(choices=GeneratedReport.ReportAccessLevel.choices)
    institution_id = django_filters.NumberFilter(field_name="institution__id")
    class_level_id = django_filters.NumberFilter(field_name="class_level__id")
    stream_id = django_filters.NumberFilter(field_name="stream__id")
    date_generated = django_filters.DateFromToRangeFilter()

    class Meta:
        model = GeneratedReport
        fields = [
            'institution_id', 'report_type', 'access_level',
            'class_level_id', 'stream_id', 'term', 'year', 'date_generated'
        ]


class ReportStudentPerformanceFilter(django_filters.FilterSet):
    student_id = django_filters.NumberFilter(field_name="student__id")
    report_id = django_filters.NumberFilter(field_name="report__id")
    grade = django_filters.CharFilter(lookup_expr='iexact')
    class_level_id = django_filters.NumberFilter(field_name="class_level__id")
    stream_id = django_filters.NumberFilter(field_name="stream__id")

    class Meta:
        model = ReportStudentPerformance
        fields = [
            'student_id', 'report_id', 'grade',
            'class_level_id', 'stream_id'
        ]


class ReportSubjectBreakdownFilter(django_filters.FilterSet):
    subject_id = django_filters.NumberFilter(field_name="subject__id")
    teacher_id = django_filters.NumberFilter(field_name="teacher__id")
    report_id = django_filters.NumberFilter(field_name="report__id")
    class_level_id = django_filters.NumberFilter(field_name="class_level__id")
    stream_id = django_filters.NumberFilter(field_name="stream__id")

    class Meta:
        model = ReportSubjectBreakdown
        fields = [
            'report_id', 'subject_id', 'teacher_id',
            'class_level_id', 'stream_id'
        ]
