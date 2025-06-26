from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from typing import Dict, List, Any
from students.models import Student
from institutions.models import Institution
from .models import (
    Invoice, Payment, Penalty, BursaryAllocation,
    RefundRequest, FeeStructure, FeeItem
)
from academics.models import Term, AcademicYear
from classes.models import ClassLevel


class FeeAnalyticsEngine:
    """
    Core analytics engine powering dashboards, reports, and summaries
    for finance and fee collections.
    """

    @staticmethod
    def institution_summary(institution: Institution) -> Dict[str, float]:
        """
        Returns total invoiced, paid, balance, bursaries, and penalties for an institution.
        """
        total_invoiced = Invoice.objects.filter(institution=institution).aggregate(
            total=Sum('total_amount'))['total'] or 0

        total_paid = Payment.objects.filter(student__institution=institution).aggregate(
            total=Sum('amount'))['total'] or 0

        balance = total_invoiced - total_paid

        total_bursary = BursaryAllocation.objects.filter(student__institution=institution).aggregate(
            total=Sum('amount'))['total'] or 0

        total_penalties = Penalty.objects.filter(student__institution=institution).aggregate(
            total=Sum('amount'))['total'] or 0

        return {
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "balance_due": balance,
            "bursary_allocated": total_bursary,
            "penalties_collected": total_penalties,
        }

    @staticmethod
    def class_wise_collection_summary(class_level: ClassLevel) -> Dict[str, Any]:
        """
        Summary of invoiced vs paid amounts for a class level.
        """
        invoices = Invoice.objects.filter(student__class_level=class_level)
        total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or 0

        total_paid = Payment.objects.filter(student__class_level=class_level).aggregate(
            total=Sum('amount'))['total'] or 0

        return {
            "class": class_level.name,
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "collection_rate": round((total_paid / total_invoiced) * 100, 2) if total_invoiced else 0
        }

    @staticmethod
    def top_outstanding_students(limit: int = 10) -> List[Student]:
        """
        Returns top N students with the highest fee balances.
        """
        return (
            Student.objects.annotate(
                total_invoiced=Sum('invoices__total_amount'),
                total_paid=Sum('payments__amount'),
                balance=F('total_invoiced') - F('total_paid')
            )
            .filter(balance__gt=0)
            .order_by('-balance')[:limit]
        )

    @staticmethod
    def recent_payments(limit: int = 20) -> List[Payment]:
        """
        List of recent payment entries.
        """
        return (
            Payment.objects
            .select_related('student', 'invoice')
            .order_by('-paid_at')[:limit]
        )

    @staticmethod
    def refund_status_summary() -> List[Dict[str, Any]]:
        """
        Count of refund requests grouped by status.
        """
        return RefundRequest.objects.values('status').annotate(count=Count('id'))

    @staticmethod
    def term_summary(term: Term, year: AcademicYear, institution: Institution) -> Dict[str, Any]:
        """
        Summary of collections for a specific term.
        """
        invoices = Invoice.objects.filter(term=term, year=year, institution=institution)
        payments = Payment.objects.filter(invoice__in=invoices)

        total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = payments.aggregate(total=Sum('amount'))['total'] or 0

        return {
            "term": str(term),
            "year": str(year),
            "total_invoiced": total_invoiced,
            "total_paid": total_paid,
            "collection_rate": round((total_paid / total_invoiced) * 100, 2) if total_invoiced else 0
        }

    @staticmethod
    def fee_item_distribution(institution: Institution) -> Dict[str, float]:
        """
        Total amount per fee item name across all fee structures.
        """
        structures = FeeStructure.objects.filter(institution=institution).prefetch_related('items')
        item_totals: Dict[str, float] = {}

        for structure in structures:
            for item in structure.items.all():
                item_totals[item.name] = item_totals.get(item.name, 0) + item.amount

        return item_totals
