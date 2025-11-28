# id_cards/filters.py

import django_filters
from .models import IDCard, IDCardAuditLog, IDCardReissueRequest
from institutions.models import Institution
from accounts.models import CustomUser


class IDCardFilter(django_filters.FilterSet):
    primary_role= django_filters.ChoiceFilter(field_name='role', choices=IDCard.ROLE_CHOICES)
    institution = django_filters.ModelChoiceFilter(queryset=Institution.objects.all())
    is_active = django_filters.BooleanFilter()
    revoked = django_filters.BooleanFilter()
    printed = django_filters.BooleanFilter()
    digital_only = django_filters.BooleanFilter()
    issued_on = django_filters.DateFromToRangeFilter()
    expiry_date = django_filters.DateFromToRangeFilter()

    class Meta:
        model = IDCard
        fields = [
            'role',
            'institution',
            'is_active',
            'revoked',
            'printed',
            'digital_only',
            'issued_on',
            'expiry_date',
        ]


class IDCardAuditLogFilter(django_filters.FilterSet):
    action = django_filters.ChoiceFilter(field_name='action', choices=IDCardAuditLog.ACTION_CHOICES)
    timestamp = django_filters.DateFromToRangeFilter()
    performed_by = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())

    class Meta:
        model = IDCardAuditLog
        fields = [
            'action',
            'timestamp',
            'performed_by',
        ]


class IDCardReissueRequestFilter(django_filters.FilterSet):
    approved = django_filters.BooleanFilter()
    created_on = django_filters.DateFromToRangeFilter()
    approved_on = django_filters.DateFromToRangeFilter()
    requester = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())
    handled_by = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.all())

    class Meta:
        model = IDCardReissueRequest
        fields = [
            'approved',
            'created_on',
            'approved_on',
            'requester',
            'handled_by',
        ]
