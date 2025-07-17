from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.utils import timezone

from .models import (
    Book, BookCopy, BorrowTransaction, LibraryMember,
    Acquisition, BookRating, BookRequest, BookRecommendation
)
from .serializers import (
    BookSerializer, BookCopySerializer, BorrowTransactionSerializer,
    LibraryMemberSerializer, AcquisitionSerializer,
    BookRatingSerializer, BookRequestSerializer, BookRecommendationSerializer
)
from .permissions import (
    IsLibrarian, IsAdminOrLibrarian, IsOwnerOrReadOnly, IsInstitutionMember
)
from .filters import (
    BookFilter, BookCopyFilter, BorrowTransactionFilter,
    LibraryMemberFilter, AcquisitionFilter
)
from .ai import LibraryAI


# ========== Book ==========
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.select_related('category', 'institution')
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    filterset_class = BookFilter
    search_fields = ['title', 'author', 'isbn', 'publisher']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def top_borrowed(self, request):
        books = LibraryAI.top_borrowed_books()
        return Response(BookSerializer(books, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def inactive(self, request):
        books = LibraryAI.inactive_books()
        return Response(BookSerializer(books, many=True).data)


# ========== BookCopy ==========
class BookCopyViewSet(viewsets.ModelViewSet):
    queryset = BookCopy.objects.select_related('book')
    serializer_class = BookCopySerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    filterset_class = BookCopyFilter
    search_fields = ['accession_number', 'book__title']


# ========== BorrowTransaction ==========
class BorrowTransactionViewSet(viewsets.ModelViewSet):
    queryset = BorrowTransaction.objects.select_related('user', 'book_copy__book')
    serializer_class = BorrowTransactionSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = BorrowTransactionFilter
    search_fields = ['user__username', 'book_copy__accession_number']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def overdue(self, request):
        today = timezone.now().date()
        overdue_qs = self.queryset.filter(returned_on__isnull=True, due_date__lt=today)
        return Response(self.serializer_class(overdue_qs, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        today = timezone.now().date()
        return Response({
            'active_loans': self.queryset.filter(returned_on__isnull=True).count(),
            'overdue_loans': self.queryset.filter(returned_on__isnull=True, due_date__lt=today).count(),
            'total_transactions': self.queryset.count()
        })


# ========== LibraryMember ==========
class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.select_related('user', 'institution')
    serializer_class = LibraryMemberSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLibrarian]
    filterset_class = LibraryMemberFilter
    search_fields = ['user__username', 'membership_id']


# ========== Acquisition ==========
class AcquisitionViewSet(viewsets.ModelViewSet):
    queryset = Acquisition.objects.select_related('book', 'vendor')
    serializer_class = AcquisitionSerializer
    permission_classes = [IsAuthenticated, IsAdminOrLibrarian]
    filterset_class = AcquisitionFilter
    search_fields = ['book__title', 'vendor__name']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        stats = self.queryset.extra(
            select={'year': "EXTRACT(year FROM acquisition_date)"}
        ).values('year').annotate(total=Count('id'))
        return Response({'yearly_acquisitions': stats})


# ========== BookRating ==========
class BookRatingViewSet(viewsets.ModelViewSet):
    queryset = BookRating.objects.select_related('user', 'book')
    serializer_class = BookRatingSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    search_fields = ['book__title', 'user__username']


# ========== BookRequest ==========
class BookRequestViewSet(viewsets.ModelViewSet):
    queryset = BookRequest.objects.select_related('requested_by', 'institution')
    serializer_class = BookRequestSerializer
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'author']


# ========== BookRecommendation ==========
class BookRecommendationViewSet(viewsets.ModelViewSet):
    queryset = BookRecommendation.objects.select_related('book', 'recommended_to', 'institution')
    serializer_class = BookRecommendationSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    search_fields = ['book__title', 'recommended_to__username']
