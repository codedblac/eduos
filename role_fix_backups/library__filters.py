from django_filters import rest_framework as filters
from .models import (
    Book, BookCategory, BookCopy, BorrowTransaction,
    LibraryMember, Acquisition, Vendor, Fine,
    BookIssueReport, BookRating, BookUsageStat,
    BookRequest, BookRecommendation, LibraryAuditLog
)


# ========== Book Filter ==========
class BookFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(lookup_expr='icontains')
    isbn = filters.CharFilter(lookup_expr='icontains')
    publisher = filters.CharFilter(lookup_expr='icontains')
    language = filters.CharFilter(lookup_expr='icontains')
    category = filters.CharFilter(field_name='category__name', lookup_expr='icontains')
    institution = filters.NumberFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publisher', 'language', 'category', 'institution', 'is_active']


# ========== BookCategory Filter ==========
class BookCategoryFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    parent = filters.NumberFilter()

    class Meta:
        model = BookCategory
        fields = [ 'parent']


# ========== BookCopy Filter ==========
class BookCopyFilter(filters.FilterSet):
    accession_number = filters.CharFilter(lookup_expr='icontains')
    barcode = filters.CharFilter(lookup_expr='icontains')
    rfid_tag = filters.CharFilter(lookup_expr='icontains')
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    location = filters.CharFilter(lookup_expr='icontains')
    is_available = filters.BooleanFilter()
    is_damaged = filters.BooleanFilter()
    is_lost = filters.BooleanFilter()

    class Meta:
        model = BookCopy
        fields = ['accession_number', 'barcode', 'rfid_tag', 'book', 'location', 'is_available', 'is_damaged', 'is_lost']


# ========== LibraryMember Filter ==========
class LibraryMemberFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    membership_id = filters.CharFilter(lookup_expr='icontains')
    membership_type = filters.ChoiceFilter(choices=LibraryMember._meta.get_field('membership_type').choices)
    institution = filters.NumberFilter()
    is_active = filters.BooleanFilter()

    class Meta:
        model = LibraryMember
        fields = ['user', 'membership_id', 'membership_type', 'institution', 'is_active']


# ========== BorrowTransaction Filter ==========
class BorrowTransactionFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    book_copy = filters.CharFilter(field_name='book_copy__accession_number', lookup_expr='icontains')
    borrowed_on__gte = filters.DateFilter(field_name='borrowed_on', lookup_expr='gte')
    borrowed_on__lte = filters.DateFilter(field_name='borrowed_on', lookup_expr='lte')
    due_date__gte = filters.DateFilter(field_name='due_date', lookup_expr='gte')
    due_date__lte = filters.DateFilter(field_name='due_date', lookup_expr='lte')
    returned_on__isnull = filters.BooleanFilter(method='filter_returned_status')

    class Meta:
        model = BorrowTransaction
        fields = [
            'user', 'book_copy',
            'borrowed_on__gte', 'borrowed_on__lte',
            'due_date__gte', 'due_date__lte',
            'returned_on__isnull'
        ]

    def filter_returned_status(self, queryset, name, value):
        return queryset.filter(returned_on__isnull=value)


# ========== Fine Filter ==========
class FineFilter(filters.FilterSet):
    transaction = filters.CharFilter(field_name='transaction__book_copy__accession_number', lookup_expr='icontains')
    paid = filters.BooleanFilter()
    waived = filters.BooleanFilter()
    institution = filters.NumberFilter()

    class Meta:
        model = Fine
        fields = ['transaction', 'paid', 'waived', 'institution']


# ========== Vendor Filter ==========
class VendorFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    email = filters.CharFilter(lookup_expr='icontains')
    institution = filters.NumberFilter()

    class Meta:
        model = Vendor
        fields = [ 'email', 'institution']


# ========== Acquisition Filter ==========
class AcquisitionFilter(filters.FilterSet):
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    vendor = filters.CharFilter(field_name='vendor__name', lookup_expr='icontains')
    procurement_status = filters.ChoiceFilter(choices=Acquisition._meta.get_field('procurement_status').choices)
    acquisition_date__gte = filters.DateFilter(field_name='acquisition_date', lookup_expr='gte')
    acquisition_date__lte = filters.DateFilter(field_name='acquisition_date', lookup_expr='lte')

    class Meta:
        model = Acquisition
        fields = ['book', 'vendor', 'procurement_status', 'acquisition_date__gte', 'acquisition_date__lte']


# ========== BookIssueReport Filter ==========
class BookIssueReportFilter(filters.FilterSet):
    book_copy = filters.CharFilter(field_name='book_copy__accession_number', lookup_expr='icontains')
    reported_by = filters.CharFilter(field_name='reported_by__username', lookup_expr='icontains')
    issue_type = filters.ChoiceFilter(choices=BookIssueReport._meta.get_field('issue_type').choices)
    resolved = filters.BooleanFilter()
    institution = filters.NumberFilter()

    class Meta:
        model = BookIssueReport
        fields = ['book_copy', 'reported_by', 'issue_type', 'resolved', 'institution']


# ========== BookRating Filter ==========
class BookRatingFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    institution = filters.NumberFilter()

    class Meta:
        model = BookRating
        fields = ['user', 'book', 'institution']


# ========== BookUsageStat Filter ==========
class BookUsageStatFilter(filters.FilterSet):
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    date__gte = filters.DateFilter(field_name='date', lookup_expr='gte')
    date__lte = filters.DateFilter(field_name='date', lookup_expr='lte')
    institution = filters.NumberFilter()

    class Meta:
        model = BookUsageStat
        fields = ['book', 'date__gte', 'date__lte', 'institution']


# ========== BookRequest Filter ==========
class BookRequestFilter(filters.FilterSet):
    requested_by = filters.CharFilter(field_name='requested_by__username', lookup_expr='icontains')
    title = filters.CharFilter(lookup_expr='icontains')
    author = filters.CharFilter(lookup_expr='icontains')
    is_fulfilled = filters.BooleanFilter()
    institution = filters.NumberFilter()

    class Meta:
        model = BookRequest
        fields = ['requested_by', 'title', 'author', 'is_fulfilled', 'institution']


# ========== BookRecommendation Filter ==========
class BookRecommendationFilter(filters.FilterSet):
    book = filters.CharFilter(field_name='book__title', lookup_expr='icontains')
    recommended_to = filters.CharFilter(field_name='recommended_to__username', lookup_expr='icontains')
    institution = filters.NumberFilter()

    class Meta:
        model = BookRecommendation
        fields = ['book', 'recommended_to', 'institution']


# ========== LibraryAuditLog Filter ==========
class LibraryAuditLogFilter(filters.FilterSet):
    user = filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    model_name = filters.CharFilter(lookup_expr='icontains')
    object_id = filters.NumberFilter()
    action = filters.CharFilter(lookup_expr='icontains')
    institution = filters.NumberFilter()
    timestamp__gte = filters.DateTimeFilter(field_name='timestamp', lookup_expr='gte')
    timestamp__lte = filters.DateTimeFilter(field_name='timestamp', lookup_expr='lte')

    class Meta:
        model = LibraryAuditLog
        fields = ['user', 'model_name', 'object_id', 'action', 'institution', 'timestamp__gte', 'timestamp__lte']
