import django_filters
from .models import Teacher

class TeacherFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')
    email = django_filters.CharFilter(lookup_expr='icontains')
    institution = django_filters.NumberFilter(field_name='institution__id')

    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'email', 'institution', 'is_active']
