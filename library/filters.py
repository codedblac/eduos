import django_filters
from django_filters import rest_framework as filters
from .models import (
    LibraryBook, AccessionRecord, BorrowTransaction,
    LibraryMember, ProcurementRecord
)

# ======== LibraryBook Filters ========
class LibraryBookFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(lookup_expr='icontains')
    isbn = filters.CharFilter(lookup_expr='icontains')
    subject = filters.CharFilter(field_name='subject__name', lookup_expr='icontains')
    is_active = filters.BooleanFilter()

    class Meta:
        model = LibraryBook
        fields = ['title', 'author', 'isbn', 'subject', 'is_active']

# ======== AccessionRecord Filters ========
class AccessionRecordFilter(filters.FilterSet):
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    accession_number = filters.CharFilter(lookup_expr='icontains')
    condition = filters.ChoiceFilter(choices=AccessionRecord.Condition.choices)
    is_available = filters.BooleanFilter()

    class Meta:
        model = AccessionRecord
        fields = ['accession_number', 'book', 'condition', 'is_available']

# ======== BorrowTransaction Filters ========
class BorrowTransactionFilter(filters.FilterSet):
    member = filters.CharFilter(field_name='member__user__username', lookup_expr='icontains')
    accession = filters.CharFilter(field_name='accession__accession_number', lookup_expr='icontains')
    is_returned = filters.BooleanFilter()
    date_borrowed__gte = filters.DateFilter(field_name='date_borrowed', lookup_expr='gte')
    date_borrowed__lte = filters.DateFilter(field_name='date_borrowed', lookup_expr='lte')

    class Meta:
        model = BorrowTransaction
        fields = [
            'member', 'accession', 'is_returned',
            'date_borrowed__gte', 'date_borrowed__lte'
        ]

# ======== LibraryMember Filters ========
class LibraryMemberFilter(filters.FilterSet):
    membership_number = filters.CharFilter(lookup_expr='icontains')
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    role = filters.ChoiceFilter(choices=LibraryMember.Role.choices)
    is_active = filters.BooleanFilter()

    class Meta:
        model = LibraryMember
        fields = ['membership_number', 'user', 'role', 'is_active']

# ======== ProcurementRecord Filters ========
class ProcurementRecordFilter(filters.FilterSet):
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    vendor = filters.CharFilter(lookup_expr='icontains')
    date_procured__gte = filters.DateFilter(field_name='date_procured', lookup_expr='gte')
    date_procured__lte = filters.DateFilter(field_name='date_procured', lookup_expr='lte')

    class Meta:
        model = ProcurementRecord
        fields = ['book', 'vendor', 'date_procured__gte', 'date_procured__lte']
