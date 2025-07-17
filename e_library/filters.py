# e_library/filters.py

import django_filters
from .models import ELibraryResource

class ELibraryResourceFilter(django_filters.FilterSet):
    subject = django_filters.NumberFilter(field_name='subject__id')
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    visibility = django_filters.ChoiceFilter(field_name='visibility', choices=[
        ('students', 'Students'),
        ('teachers', 'Teachers'),
        ('all', 'All Users'),
        ('institution', 'Institution Only'),
        ('public', 'Public'),
    ])
    uploader = django_filters.CharFilter(field_name='uploader__username', lookup_expr='icontains')
    institution = django_filters.UUIDFilter(field_name='institution__id')
    resource_type = django_filters.ChoiceFilter(field_name='resource_type', choices=[
        ('pdf', 'PDF'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('presentation', 'Presentation'),
        ('external_link', 'External Link'),
    ])
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    is_approved = django_filters.BooleanFilter(field_name='is_approved')
    is_deleted = django_filters.BooleanFilter(field_name='is_deleted')

    class Meta:
        model = ELibraryResource
        fields = [
            'subject',
            'class_level',
            'visibility',
            'uploader',
            'institution',
            'resource_type',
            'created_after',
            'created_before',
            'is_approved',
            'is_deleted',
        ]
