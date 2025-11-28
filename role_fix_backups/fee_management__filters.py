import django_filters
from django.db.models import Q
from .models import (
    Invoice, Payment, BursaryAllocation,
    RefundRequest, Penalty
)
from students.models import Student
from institutions.models import Institution


class StudentFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(method='filter_full_name')
    admission_number = django_filters.CharFilter(field_name='admission_number', lookup_expr='icontains')
    class_level = django_filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    stream = django_filters.CharFilter(field_name='stream__name', lookup_expr='icontains')
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())

    class Meta:
        model = Student
        fields = [ 'admission_number', 'class_level', 'stream', 'institution']

    def filter_full_name(self, queryset, name, value):
        return queryset.filter(
            Q(user__first_name__icontains=value) |
            Q(user__last_name__icontains=value) |
            Q(user__full_name__icontains=value)
        )


class InvoiceFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(method='filter_student_name')
    class_level = django_filters.CharFilter(field_name='student__class_level__name', lookup_expr='icontains')
    stream = django_filters.CharFilter(field_name='student__stream__name', lookup_expr='icontains')
    institution = django_filters.ModelChoiceFilter(field_name='institution', queryset=Institution.objects.all())
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='year__year')
    status = django_filters.ChoiceFilter(choices=Invoice.STATUS_CHOICES)

    class Meta:
        model = Invoice
        fields = ['student', 'class_level', 'stream', 'term', 'year', 'status', 'institution']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )


class PaymentFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(method='filter_student_name')
    mode = django_filters.ChoiceFilter(field_name='mode', choices=Payment.MODE_CHOICES)
    paid_at = django_filters.DateFromToRangeFilter()
    institution = django_filters.ModelChoiceFilter(field_name='student__institution', queryset=Institution.objects.all())

    class Meta:
        model = Payment
        fields = ['student', 'mode', 'paid_at', 'institution']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )


class BursaryFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(method='filter_student_name')
    source = django_filters.CharFilter(lookup_expr='icontains')
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='year__year')

    class Meta:
        model = BursaryAllocation
        fields = ['student', 'source', 'term', 'year']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )


class RefundRequestFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(method='filter_student_name')
    status = django_filters.ChoiceFilter(choices=RefundRequest.STATUS_CHOICES)
    refunded_on = django_filters.DateFromToRangeFilter()

    class Meta:
        model = RefundRequest
        fields = ['student', 'status', 'refunded_on']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )


class PenaltyFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(method='filter_student_name')
    term = django_filters.CharFilter(field_name='term__name', lookup_expr='icontains')

    class Meta:
        model = Penalty
        fields = ['student', 'term']

    def filter_student_name(self, queryset, name, value):
        return queryset.filter(
            Q(student__user__first_name__icontains=value) |
            Q(student__user__last_name__icontains=value) |
            Q(student__user__full_name__icontains=value)
        )
