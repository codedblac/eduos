import django_filters
from .models import (
    GeneratedReport,
    ReportStudentPerformance,
    ReportSubjectBreakdown,
    ReportPrintRequest,
    ReportAuditTrail,
    ReportType,
    ReportAccessLevel,
    ReportStatus,
)
from classes.models import ClassLevel, Stream
from institutions.models import Institution
from students.models import Student
from subjects.models import Subject
from exams.models import Exam
from accounts.models import CustomUser


class GeneratedReportFilter(django_filters.FilterSet):
    report_type = django_filters.ChoiceFilter(choices=ReportType.choices)
    access_level = django_filters.ChoiceFilter(choices=ReportAccessLevel.choices)
    status = django_filters.ChoiceFilter(choices=ReportStatus.choices)
    term = django_filters.CharFilter(lookup_expr='iexact')
    year = django_filters.CharFilter(lookup_expr='iexact')
    class_level = django_filters.ModelChoiceFilter(queryset=ClassLevel.objects.all())
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all())
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    is_auto_generated = django_filters.BooleanFilter()
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = GeneratedReport
        fields = [
            'report_type', 'access_level', 'status', 'term', 'year',
            'class_level', 'stream', 'institution',
            'is_auto_generated', 'is_active'
        ]


class ReportStudentPerformanceFilter(django_filters.FilterSet):
    report = django_filters.ModelChoiceFilter(queryset=GeneratedReport.objects.all())
    student = django_filters.ModelChoiceFilter(queryset=Student.objects.all())
    class_level = django_filters.ModelChoiceFilter(queryset=ClassLevel.objects.all())
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all())
    flagged = django_filters.BooleanFilter()

    class Meta:
        model = ReportStudentPerformance
        fields = [
            'report', 'student', 'class_level', 'stream', 'flagged'
        ]


class ReportSubjectBreakdownFilter(django_filters.FilterSet):
    report = django_filters.ModelChoiceFilter(queryset=GeneratedReport.objects.all())
    subject = django_filters.ModelChoiceFilter(queryset=Subject.objects.all())
    teacher = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    class_level = django_filters.ModelChoiceFilter(queryset=ClassLevel.objects.all())
    stream = django_filters.ModelChoiceFilter(queryset=Stream.objects.all())
    exam = django_filters.ModelChoiceFilter(queryset=Exam.objects.all())
    flagged = django_filters.BooleanFilter()

    class Meta:
        model = ReportSubjectBreakdown
        fields = [
            'report', 'subject', 'teacher',
            'class_level', 'stream', 'exam', 'flagged'
        ]


class ReportAuditTrailFilter(django_filters.FilterSet):
    report = django_filters.ModelChoiceFilter(queryset=GeneratedReport.objects.all())
    performed_by = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    timestamp = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ReportAuditTrail
        fields = ['report', 'performed_by', 'timestamp']


class ReportPrintRequestFilter(django_filters.FilterSet):
    report = django_filters.ModelChoiceFilter(queryset=GeneratedReport.objects.all())
    requested_by = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    is_printed = django_filters.BooleanFilter()
    requested_at = django_filters.DateTimeFromToRangeFilter()
    printed_at = django_filters.DateTimeFromToRangeFilter()

    class Meta:
        model = ReportPrintRequest
        fields = [
            'report', 'requested_by', 'is_printed',
            'requested_at', 'printed_at'
        ]
