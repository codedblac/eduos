import django_filters
from teachers.models import Teacher
from institutions.models import Institution
from subjects.models import Subject
from classes.models import ClassLevel, Stream


class TeacherFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    phone = django_filters.CharFilter(lookup_expr='icontains')
    staff_id = django_filters.CharFilter(lookup_expr='icontains')
    gender = django_filters.ChoiceFilter(choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')])
    employment_type = django_filters.ChoiceFilter(
        choices=[
            ('full_time', 'Full-Time'),
            ('part_time', 'Part-Time'),
            ('contract', 'Contract'),
            ('volunteer', 'Volunteer'),
        ]
    )
    is_active = django_filters.BooleanFilter()
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    subjects = django_filters.ModelMultipleChoiceFilter(
        field_name='subjects',
        to_field_name='id',
        queryset=Subject.objects.all()
    )
    class_levels_handled = django_filters.ModelMultipleChoiceFilter(
        queryset=ClassLevel.objects.all()
    )
    streams_handled = django_filters.ModelMultipleChoiceFilter(
        queryset=Stream.objects.all()
    )
    date_joined = django_filters.DateFromToRangeFilter()

    class Meta:
        model = Teacher
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'staff_id', 'gender',
            'employment_type', 'is_active', 'institution', 'subjects',
            'class_levels_handled', 'streams_handled', 'date_joined'
        ]
