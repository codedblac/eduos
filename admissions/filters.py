import django_filters
from django.db.models import Q
from .models import Applicant, AdmissionSession, EntranceExam, AdmissionOffer


class AdmissionSessionFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    academic_year = django_filters.NumberFilter(field_name='academic_year__id')
    institution = django_filters.NumberFilter(field_name='institution__id')
    level = django_filters.NumberFilter(field_name='level__id')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = AdmissionSession
        fields = ['name', 'academic_year', 'institution', 'level', 'is_active']


class ApplicantFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(method='filter_by_full_name', label="Search by Full Name")
    gender = django_filters.CharFilter()
    county = django_filters.CharFilter(lookup_expr='icontains')
    nationality = django_filters.CharFilter(lookup_expr='icontains')
    orphan_status = django_filters.ChoiceFilter(choices=Applicant.ORPHAN_STATUS)
    has_disability = django_filters.BooleanFilter()
    has_chronic_illness = django_filters.BooleanFilter()
    application_status = django_filters.CharFilter()
    admission_session = django_filters.NumberFilter(field_name='admission_session__id')
    entry_class_level = django_filters.NumberFilter(field_name='entry_class_level__id')
    submitted_from = django_filters.DateFilter(field_name='submitted_on', lookup_expr='gte')
    submitted_to = django_filters.DateFilter(field_name='submitted_on', lookup_expr='lte')

    class Meta:
        model = Applicant
        fields = [
            'gender', 'county', 'nationality', 'orphan_status',
            'has_disability', 'has_chronic_illness', 'application_status',
            'admission_session', 'entry_class_level'
        ]

    def filter_by_full_name(self, queryset, name, value):
        return queryset.filter(
            Q(first_name__icontains=value) |
            Q(last_name__icontains=value) |
            Q(other_names__icontains=value)
        )


class EntranceExamFilter(django_filters.FilterSet):
    applicant_id = django_filters.NumberFilter(field_name='applicant__id')
    passed = django_filters.BooleanFilter()
    score_min = django_filters.NumberFilter(field_name='score', lookup_expr='gte')
    score_max = django_filters.NumberFilter(field_name='score', lookup_expr='lte')
    exam_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = EntranceExam
        fields = ['applicant_id', 'passed', 'score', 'exam_date']


class AdmissionOfferFilter(django_filters.FilterSet):
    applicant_id = django_filters.NumberFilter(field_name='applicant__id')
    status = django_filters.CharFilter()
    issued_on = django_filters.DateFromToRangeFilter()
    expiry_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = AdmissionOffer
        fields = ['applicant_id', 'status', 'issued_on', 'expiry_date']
