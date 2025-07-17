import django_filters
from .models import Guardian, GuardianStudentLink, GuardianNotification


class GuardianFilter(django_filters.FilterSet):
    institution = django_filters.UUIDFilter(field_name='institution__id')
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Guardian
        fields = ['institution', 'user', 'is_active']


class GuardianStudentLinkFilter(django_filters.FilterSet):
    guardian = django_filters.UUIDFilter(field_name='guardian__id')
    student = django_filters.UUIDFilter(field_name='student__id')
    relationship = django_filters.ChoiceFilter(field_name='relationship', choices=[
        ("father", "Father"),
        ("mother", "Mother"),
        ("guardian", "Guardian"),
        ("sponsor", "Sponsor"),
        ("uncle", "Uncle"),
        ("aunt", "Aunt"),
        ("grandparent", "Grandparent"),
        ("other", "Other"),
    ])
    is_primary = django_filters.BooleanFilter()

    class Meta:
        model = GuardianStudentLink
        fields = ['guardian', 'student', 'relationship', 'is_primary']


class GuardianNotificationFilter(django_filters.FilterSet):
    guardian = django_filters.UUIDFilter(field_name='guardian__id')
    institution = django_filters.UUIDFilter(field_name='institution__id')
    type = django_filters.ChoiceFilter(field_name='type', choices=[
        ("exam_update", "Exam Update"),
        ("fee_balance", "Fee Balance"),
        ("medical_alert", "Medical Alert"),
        ("timetable_update", "Timetable Update"),
        ("announcement", "General Announcement"),
        ("discipline", "Discipline Alert"),
        ("chat", "New Chat Message"),
        ("wallet", "Wallet Activity"),
    ])
    is_read = django_filters.BooleanFilter()
    timestamp_after = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp_before = django_filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = GuardianNotification
        fields = ['guardian', 'institution', 'type', 'is_read', 'timestamp_after', 'timestamp_before']
