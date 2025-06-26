import django_filters
from .models import Student, Enrollment
from classes.models import ClassLevel, Stream
from accounts.models import Institution

class StudentFilter(django_filters.FilterSet):
    # Filter by student full name (partial match)
    full_name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    
    # Filter by enrollment status (active, graduated, expelled)
    enrollment_status = django_filters.CharFilter(field_name='enrollment_status', lookup_expr='iexact')
    
    # Filter by gender
    gender = django_filters.ChoiceFilter(field_name='gender', choices=Student.GENDER_CHOICES)
    
    # Filter by institution
    institution = django_filters.NumberFilter(field_name='institution__id')
    
    # Filter by class level
    class_level = django_filters.NumberFilter(field_name='class_level__id')
    
    # Filter by stream
    stream = django_filters.NumberFilter(field_name='stream__id')
    
    # Filter by admission date range
    admission_date_after = django_filters.DateFilter(field_name='admission_date', lookup_expr='gte')
    admission_date_before = django_filters.DateFilter(field_name='admission_date', lookup_expr='lte')

    class Meta:
        model = Student
        fields = [
            'full_name', 'enrollment_status', 'gender',
            'institution', 'class_level', 'stream',
            'admission_date_after', 'admission_date_before',
        ]
