# e_library/filters.py
import django_filters
from .models import ELibraryResource

class ELibraryResourceFilter(django_filters.FilterSet):
    subject = django_filters.CharFilter(field_name='subject', lookup_expr='icontains')
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    visibility = django_filters.ChoiceFilter(field_name='visibility', choices=ELibraryResource.VISIBILITY_CHOICES)
    uploaded_by = django_filters.CharFilter(field_name='uploaded_by__user__username', lookup_expr='icontains')
    institution = django_filters.UUIDFilter(field_name='institution__id')
    resource_type = django_filters.ChoiceFilter(field_name='resource_type', choices=ELibraryResource.RESOURCE_TYPE_CHOICES)
    created_after = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = ELibraryResource
        fields = [
            'subject',
            'class_level',
            'visibility',
            'uploaded_by',
            'institution',
            'resource_type',
            'created_after',
            'created_before',
        ]
