import django_filters
from django_filters import rest_framework as filters
from .models import CommunicationAnnouncement, AnnouncementCategory
from django.contrib.auth import get_user_model

User = get_user_model()


class CommunicationAnnouncementFilter(filters.FilterSet):
    priority = filters.ChoiceFilter(choices=CommunicationAnnouncement.PRIORITY_CHOICES)
    institution = filters.NumberFilter(field_name='institution__id')
    category = filters.ModelChoiceFilter(queryset=AnnouncementCategory.objects.all())
    author = filters.ModelChoiceFilter(queryset=User.objects.all())
    is_public = filters.BooleanFilter()
    sent = filters.BooleanFilter()
    scheduled_at = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    expires_at = filters.DateFromToRangeFilter()

    class Meta:
        model = CommunicationAnnouncement
        fields = [
            'priority',
            'institution',
            'category',
            'author',
            'is_public',
            'sent',
            'scheduled_at',
            'created_at',
            'expires_at']
