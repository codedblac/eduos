from rest_framework import serializers
from django.utils import timezone
from .models import (
    BookCategory, Book, BookCopy, BorrowTransaction, Fine,
    Vendor, Acquisition, BookIssueReport, BookRating, BookUsageStat,
    LibraryMember, BookRequest, BookRecommendation, LibraryAuditLog
)
from django.contrib.auth import get_user_model
from institutions.serializers import InstitutionSerializer

User = get_user_model()

# === Book Category ===
class BookCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookCategory
        fields = '__all__'


# === Book ===
class BookSerializer(serializers.ModelSerializer):
    category = BookCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BookCategory.objects.all(), write_only=True, source='category'
    )
    institution = InstitutionSerializer(read_only=True)
    available_copies = serializers.SerializerMethodField()
    total_copies = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'institution', 'title', 'author', 'isbn', 'publisher',
            'publication_year', 'edition', 'language', 'summary', 'cover_image',
            'category', 'category_id', 'available_copies', 'total_copies', 'average_rating',
            'is_active', 'created_at', 'updated_at'
        ]

    def get_available_copies(self, obj):
        return obj.copies.filter(is_available=True, is_damaged=False, is_lost=False).count()

    def get_total_copies(self, obj):
        return obj.copies.count()

    def get_average_rating(self, obj):
        ratings = obj.ratings.all().values_list('rating', flat=True)
        return round(sum(ratings) / len(ratings), 2) if ratings else None


# === Book Copy ===
class BookCopySerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')

    class Meta:
        model = BookCopy
        fields = [
            'id', 'book', 'book_id', 'accession_number', 'barcode', 'rfid_tag',
            'is_available', 'is_damaged', 'is_lost', 'condition_notes', 'location',
            'acquired_on', 'created_at', 'updated_at'
        ]


# === Borrow Transaction ===
class BorrowTransactionSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    book_copy = BookCopySerializer(read_only=True)
    book_copy_id = serializers.PrimaryKeyRelatedField(
        queryset=BookCopy.objects.filter(is_available=True, is_lost=False),
        write_only=True,
        source='book_copy'
    )
    is_overdue = serializers.SerializerMethodField()

    class Meta:
        model = BorrowTransaction
        fields = [
            'id', 'user', 'user_id', 'book_copy', 'book_copy_id',
            'borrowed_on', 'due_date', 'returned_on', 'is_overdue',
            'is_renewed', 'renewed_times', 'fine_applied'
        ]

    def get_is_overdue(self, obj):
        return obj.is_overdue


# === Fine ===
class FineSerializer(serializers.ModelSerializer):
    transaction = BorrowTransactionSerializer(read_only=True)
    transaction_id = serializers.PrimaryKeyRelatedField(queryset=BorrowTransaction.objects.all(), write_only=True, source='transaction')

    class Meta:
        model = Fine
        fields = [
            'id', 'transaction', 'transaction_id', 'amount', 'paid', 'paid_on', 'waived', 'waived_by'
        ]


# === Vendor ===
class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


# === Acquisition ===
class AcquisitionSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')
    vendor = VendorSerializer(read_only=True)
    vendor_id = serializers.PrimaryKeyRelatedField(queryset=Vendor.objects.all(), write_only=True, source='vendor')
    total_cost = serializers.SerializerMethodField()

    class Meta:
        model = Acquisition
        fields = [
            'id', 'book', 'book_id', 'vendor', 'vendor_id',
            'quantity', 'price_per_unit', 'acquisition_date',
            'funding_source', 'total_cost', 'procurement_status', 'approved_by'
        ]

    def get_total_cost(self, obj):
        return obj.total_cost()


# === Book Issue Report ===
class BookIssueReportSerializer(serializers.ModelSerializer):
    book_copy = BookCopySerializer(read_only=True)
    book_copy_id = serializers.PrimaryKeyRelatedField(queryset=BookCopy.objects.all(), write_only=True, source='book_copy')
    reported_by = serializers.StringRelatedField(read_only=True)
    reported_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='reported_by')

    class Meta:
        model = BookIssueReport
        fields = [
            'id', 'book_copy', 'book_copy_id', 'reported_by', 'reported_by_id',
            'issue_type', 'description', 'reported_on', 'resolved', 'resolved_on',
            'assigned_to', 'action_taken'
        ]


# === Book Rating ===
class BookRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')

    class Meta:
        model = BookRating
        fields = [
            'id', 'user', 'user_id', 'book', 'book_id', 'rating', 'review', 'created_at'
        ]


# === Book Usage Stats ===
class BookUsageStatSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(queryset=Book.objects.all(), write_only=True, source='book')

    class Meta:
        model = BookUsageStat
        fields = [
            'id', 'book', 'book_id', 'date',
            'borrow_count', 'search_count', 'recommendation_score', 'average_rating', 'unique_borrowers_count'
        ]
        read_only_fields = ['recommendation_score']


# === Library Member ===
class LibraryMemberSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='user')
    institution = InstitutionSerializer(read_only=True)

    class Meta:
        model = LibraryMember
        fields = [
            'id', 'user', 'user_id', 'institution', 'membership_type',
            'membership_id', 'profile_picture', 'joined_at', 'is_active',
            'max_books_allowed', 'membership_expiry_date'
        ]


# === Book Request ===
class BookRequestSerializer(serializers.ModelSerializer):
    requested_by = serializers.StringRelatedField(read_only=True)
    requested_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='requested_by')

    class Meta:
        model = BookRequest
        fields = '__all__'


# === Book Recommendation ===
class BookRecommendationSerializer(serializers.ModelSerializer):
    recommended_by = serializers.StringRelatedField(read_only=True)
    recommended_by_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True, source='recommended_by')

    class Meta:
        model = BookRecommendation
        fields = '__all__'


# === Audit Log ===
class LibraryAuditLogSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = LibraryAuditLog
        fields = '__all__'
