import django_filters
from .models import Guardian, GuardianStudentLink, GuardianNotification
from institutions.models import Institution
from students.models import Student


class GuardianFilter(django_filters.FilterSet):
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    user__first_name = django_filters.CharFilter(lookup_expr='icontains', label="First Name")
    user__last_name = django_filters.CharFilter(lookup_expr='icontains', label="Last Name")
    phone_number = django_filters.CharFilter(lookup_expr='icontains')
    id_number = django_filters.CharFilter(lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Guardian
        fields = ['institution', 'phone_number', 'id_number', 'is_active']


class GuardianStudentLinkFilter(django_filters.FilterSet):
    guardian = django_filters.ModelChoiceFilter(queryset=Guardian.objects.all())
    student = django_filters.ModelChoiceFilter(queryset=Student.objects.all())
    relationship = django_filters.CharFilter(lookup_expr='icontains')
    is_primary = django_filters.BooleanFilter()

    class Meta:
        model = GuardianStudentLink
        fields = ['guardian', 'student', 'relationship', 'is_primary']


class GuardianNotificationFilter(django_filters.FilterSet):
    guardian = django_filters.ModelChoiceFilter(queryset=Guardian.objects.all())
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    type = django_filters.CharFilter(lookup_expr='icontains')
    is_read = django_filters.BooleanFilter()
    timestamp__date = django_filters.DateFromToRangeFilter(field_name="timestamp")

    class Meta:
        model = GuardianNotification
        fields = ['guardian', 'institution', 'type', 'is_read', 'timestamp__date']
