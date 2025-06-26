from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import (
    LibraryBook, AccessionRecord, BorrowTransaction,
    LibraryMember, ProcurementRecord
)
from .serializers import (
    LibraryBookSerializer, AccessionRecordSerializer,
    BorrowTransactionSerializer, LibraryMemberSerializer,
    ProcurementRecordSerializer
)
from .permissions import (
    IsLibrarianOrAdmin, IsLibrarianOrReadOnly, IsMemberOrReadOnly
)
from .filters import (
    LibraryBookFilter, AccessionRecordFilter,
    BorrowTransactionFilter, LibraryMemberFilter,
    ProcurementRecordFilter
)

# ======== LibraryBook ViewSet ========
class LibraryBookViewSet(viewsets.ModelViewSet):
    queryset = LibraryBook.objects.all().select_related('subject')
    serializer_class = LibraryBookSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]
    filterset_class = LibraryBookFilter
    search_fields = ['title', 'author', 'isbn', 'publisher']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request):
        top_borrowed = LibraryBook.objects.annotate(
            borrow_count=Count('accessionrecord__borrowtransaction')
        ).order_by('-borrow_count')[:10]

        return Response({
            'top_borrowed_books': LibraryBookSerializer(top_borrowed, many=True).data
        })

# ======== AccessionRecord ViewSet ========
class AccessionRecordViewSet(viewsets.ModelViewSet):
    queryset = AccessionRecord.objects.select_related('book')
    serializer_class = AccessionRecordSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrReadOnly]
    filterset_class = AccessionRecordFilter
    search_fields = ['accession_number', 'book__title']

# ======== BorrowTransaction ViewSet ========
class BorrowTransactionViewSet(viewsets.ModelViewSet):
    queryset = BorrowTransaction.objects.select_related('member', 'accession__book')
    serializer_class = BorrowTransactionSerializer
    permission_classes = [IsAuthenticated, IsMemberOrReadOnly]
    filterset_class = BorrowTransactionFilter
    search_fields = ['member__user__username', 'accession__accession_number']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def overdue(self, request):
        overdue_qs = self.queryset.filter(is_returned=False, due_date__lt=request.query_params.get('date'))
        return Response(self.serializer_class(overdue_qs, many=True).data)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def analytics(self, request):
        data = {
            'active_loans': self.queryset.filter(is_returned=False).count(),
            'overdue_loans': self.queryset.filter(is_returned=False, due_date__lt=request.query_params.get('date')).count(),
            'total_transactions': self.queryset.count(),
        }
        return Response(data)

# ======== LibraryMember ViewSet ========
class LibraryMemberViewSet(viewsets.ModelViewSet):
    queryset = LibraryMember.objects.select_related('user')
    serializer_class = LibraryMemberSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrAdmin]
    filterset_class = LibraryMemberFilter
    search_fields = ['user__username', 'membership_number']

# ======== ProcurementRecord ViewSet ========
class ProcurementRecordViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRecord.objects.select_related('book', 'vendor')
    serializer_class = ProcurementRecordSerializer
    permission_classes = [IsAuthenticated, IsLibrarianOrAdmin]
    filterset_class = ProcurementRecordFilter
    search_fields = ['book__title', 'vendor']

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def stats(self, request):
        yearly = ProcurementRecord.objects.extra(select={'year': "EXTRACT(year FROM date_procured)"}).values('year').annotate(total=Count('id'))
        return Response({'yearly_procurement': yearly})
