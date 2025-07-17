from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources

from .models import (
    BookCategory, Book, BookCopy, BorrowTransaction,
    LibraryMember, Fine, Vendor, Acquisition,
    BookIssueReport, BookRating, BookUsageStat
)

# ========== Resource Classes ==========
class BookCategoryResource(resources.ModelResource):
    class Meta:
        model = BookCategory

class BookResource(resources.ModelResource):
    class Meta:
        model = Book

class BookCopyResource(resources.ModelResource):
    class Meta:
        model = BookCopy

class BorrowTransactionResource(resources.ModelResource):
    class Meta:
        model = BorrowTransaction

class LibraryMemberResource(resources.ModelResource):
    class Meta:
        model = LibraryMember

class FineResource(resources.ModelResource):
    class Meta:
        model = Fine

class VendorResource(resources.ModelResource):
    class Meta:
        model = Vendor

class AcquisitionResource(resources.ModelResource):
    class Meta:
        model = Acquisition

class BookIssueReportResource(resources.ModelResource):
    class Meta:
        model = BookIssueReport

class BookRatingResource(resources.ModelResource):
    class Meta:
        model = BookRating

class BookUsageStatResource(resources.ModelResource):
    class Meta:
        model = BookUsageStat

# ========== Admin Classes ==========
@admin.register(BookCategory)
class BookCategoryAdmin(ImportExportModelAdmin):
    resource_class = BookCategoryResource
    list_display = ('name', 'description', 'parent')
    search_fields = ('name',)

@admin.register(Book)
class BookAdmin(ImportExportModelAdmin):
    resource_class = BookResource
    list_display = ('title', 'author', 'isbn', 'publisher', 'publication_year', 'language', 'category', 'institution')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('language', 'publication_year', 'category')
    autocomplete_fields = ('institution', 'category')

@admin.register(BookCopy)
class BookCopyAdmin(ImportExportModelAdmin):
    resource_class = BookCopyResource
    list_display = ('book', 'accession_number', 'is_available', 'is_damaged', 'is_lost', 'location', 'acquired_on')
    search_fields = ('accession_number', 'book__title')
    list_filter = ('is_available', 'is_damaged', 'is_lost')
    autocomplete_fields = ('book',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(BorrowTransaction)
class BorrowTransactionAdmin(ImportExportModelAdmin):
    resource_class = BorrowTransactionResource
    list_display = ('user', 'book_copy', 'borrowed_on', 'due_date', 'returned_on', 'renewed_times', 'is_renewed', 'fine_applied')
    search_fields = ('user__username', 'book_copy__accession_number')
    list_filter = ('borrowed_on', 'due_date', 'returned_on')
    autocomplete_fields = ('user', 'book_copy')

@admin.register(LibraryMember)
class LibraryMemberAdmin(ImportExportModelAdmin):
    resource_class = LibraryMemberResource
    list_display = ('user', 'institution', 'membership_id', 'membership_type', 'joined_at', 'membership_expiry', 'can_borrow', 'is_active')
    search_fields = ('user__username', 'membership_id')
    list_filter = ('membership_type', 'is_active')
    autocomplete_fields = ('user', 'institution')

@admin.register(Fine)
class FineAdmin(ImportExportModelAdmin):
    resource_class = FineResource
    list_display = ('transaction', 'amount', 'paid', 'paid_on', 'waived', 'waived_by', 'institution')
    search_fields = ('transaction__book_copy__accession_number', 'transaction__user__username')
    list_filter = ('paid', 'waived')
    autocomplete_fields = ('transaction', 'waived_by', 'institution')

@admin.register(Vendor)
class VendorAdmin(ImportExportModelAdmin):
    resource_class = VendorResource
    list_display = ('name', 'contact_person', 'email', 'phone', 'institution')
    search_fields = ('name', 'contact_person', 'email', 'tax_id')

@admin.register(Acquisition)
class AcquisitionAdmin(ImportExportModelAdmin):
    resource_class = AcquisitionResource
    list_display = ('book', 'vendor', 'quantity', 'price_per_unit', 'acquisition_date', 'funding_source', 'procurement_status', 'approved_by')
    search_fields = ('book__title', 'vendor__name')
    list_filter = ('vendor', 'acquisition_date', 'procurement_status')
    autocomplete_fields = ('book', 'vendor', 'approved_by')

@admin.register(BookIssueReport)
class BookIssueReportAdmin(ImportExportModelAdmin):
    resource_class = BookIssueReportResource
    list_display = ('book_copy', 'issue_type', 'reported_by', 'reported_on', 'resolved', 'resolved_on', 'institution')
    search_fields = ('book_copy__accession_number', 'reported_by__username')
    list_filter = ('issue_type', 'resolved')
    autocomplete_fields = ('book_copy', 'reported_by', 'institution')

@admin.register(BookRating)
class BookRatingAdmin(ImportExportModelAdmin):
    resource_class = BookRatingResource
    list_display = ('book', 'user', 'rating', 'anonymize_review', 'created_at', 'institution')
    search_fields = ('book__title', 'user__username')
    list_filter = ('rating', 'anonymize_review')
    autocomplete_fields = ('book', 'user', 'institution')

@admin.register(BookUsageStat)
class BookUsageStatAdmin(ImportExportModelAdmin):
    resource_class = BookUsageStatResource
    list_display = ('book', 'institution', 'date', 'borrow_count', 'search_count', 'recommendation_score', 'average_rating', 'unique_borrowers_count')
    search_fields = ('book__title',)
    list_filter = ('date',)
    autocomplete_fields = ('book', 'institution')
