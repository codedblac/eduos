import django_filters
from django.db.models import Q
from e_wallet.models import WalletTransaction, MicroFee, Wallet
from students.models import Student
from accounts.models import CustomUser


class WalletTransactionFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(
        field_name='wallet__student__user__username', lookup_expr='icontains'
    )
    type = django_filters.ChoiceFilter(
        choices=[('credit', 'Credit'), ('debit', 'Debit'), ('refund', 'Refund')]
    )
    min_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = django_filters.NumberFilter(field_name='amount', lookup_expr='lte')
    start_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    end_date = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = WalletTransaction
        fields = ['type', 'student', 'min_amount', 'max_amount', 'start_date', 'end_date']


class MicroFeeFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains')
    teacher = django_filters.ModelChoiceFilter(queryset=CustomUser.objects.filter(primary_role='teacher'))
    class_level = django_filters.CharFilter(field_name='class_level__name', lookup_expr='icontains')
    stream = django_filters.CharFilter(field_name='stream__name', lookup_expr='icontains')
    due_date = django_filters.DateFilter(field_name='due_date')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = MicroFee
        fields = ['title', 'teacher', 'class_level', 'stream', 'due_date', 'is_active']


class WalletFilter(django_filters.FilterSet):
    student = django_filters.CharFilter(field_name='student__user__username', lookup_expr='icontains')
    min_balance = django_filters.NumberFilter(field_name='balance', lookup_expr='gte')
    max_balance = django_filters.NumberFilter(field_name='balance', lookup_expr='lte')
    is_active = django_filters.BooleanFilter()

    class Meta:
        model = Wallet
        fields = ['student', 'min_balance', 'max_balance', 'is_active']
