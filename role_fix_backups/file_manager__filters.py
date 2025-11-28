import django_filters
from .models import ManagedFile, FileAccessLog


class ManagedFileFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    file_type = django_filters.CharFilter(lookup_expr='iexact')
    uploaded_by = django_filters.CharFilter(field_name='uploaded_by__username', lookup_expr='icontains')
    class_level = django_filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    stream = django_filters.CharFilter(field_name='stream__name', lookup_expr='icontains')
    subject = django_filters.CharFilter(field_name='subject__name', lookup_expr='icontains')
    tags = django_filters.CharFilter(lookup_expr='icontains')
    created_at = django_filters.DateFromToRangeFilter()
    institution = django_filters.CharFilter(field_name='institution__name', lookup_expr='icontains')
    is_public = django_filters.BooleanFilter()
    is_archived = django_filters.BooleanFilter()

    class Meta:
        model = ManagedFile
        fields = [ 'file_type', 'uploaded_by', 'class_level', 'stream',
            'subject', 'tags', 'created_at', 'institution', 'is_public', 'is_archived'
        ]


class FileAccessLogFilter(django_filters.FilterSet):
    file = django_filters.CharFilter(field_name='file__name', lookup_expr='icontains')
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    action = django_filters.ChoiceFilter(choices=FileAccessLog.ACTION_CHOICES)
    accessed_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = FileAccessLog
        fields = ['file', 'user', 'action', 'accessed_at']
