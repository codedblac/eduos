from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q, F
from students.models import Student
from .models import Invoice, Payment, BursaryAllocation, Penalty
from institutions.models import Institution
from typing import List, Union


class FeeAIEngine:
    """
    A predictive analytics engine for fee insights, payment behaviors,
    and recommendations to guide school finance decisions.
    """

    @staticmethod
    def get_top_debtors(institution: Institution, limit: int = 10) -> List[Student]:
        """
        Return top students with the highest unpaid balances.
        """
        students = (
            Student.objects.filter(institution=institution)
            .annotate(
                total_invoiced=Sum('invoices__total_amount'),
                total_paid=Sum('payments__amount'),
                balance=F('invoices__total_amount') - F('payments__total_amount'),
            )
            .filter(total_invoiced__gt=0)
            .order_by('-balance')[:limit]
        )
        return students

    @staticmethod
    def students_at_risk_due_to_arrears(threshold: int = 2) -> List[Student]:
        """
        Return students with overdue invoices above a specified threshold.
        """
        return (
            Student.objects.annotate(
                overdue_invoices=Count('invoices', filter=Q(invoices__status='overdue'))
            )
            .filter(overdue_invoices__gte=threshold)
        )

    @staticmethod
    def suggest_payment_reminders() -> List[Invoice]:
        """
        Return invoices due soon for reminder notification.
        """
        due_soon = timezone.now().date() + timedelta(days=3)
        return Invoice.objects.filter(
            is_paid=False,
            due_date__lte=due_soon,
            status__in=['issued', 'overdue']
        )

    @staticmethod
    def predict_collection_rate(institution: Institution) -> float:
        """
        Predict end-of-term collection rate for the current month.
        """
        now = timezone.now()
        invoices = Invoice.objects.filter(
            institution=institution,
            created_at__year=now.year,
            created_at__month=now.month
        )
        total_invoiced = invoices.aggregate(total=Sum('total_amount'))['total'] or 0
        total_paid = Payment.objects.filter(
            student__institution=institution,
            paid_at__year=now.year,
            paid_at__month=now.month
        ).aggregate(total=Sum('amount'))['total'] or 0

        return round((total_paid / total_invoiced) * 100, 2) if total_invoiced else 0.0

    @staticmethod
    def recommend_bursary_candidates(institution: Institution, limit: int = 10) -> List[Student]:
        """
        Recommend students with the highest unpaid balances for bursary consideration.
        """
        students = (
            Student.objects.filter(institution=institution)
            .annotate(
                total_invoiced=Sum('invoices__total_amount'),
                total_paid=Sum('payments__amount'),
                balance=F('invoices__total_amount') - F('payments__total_amount'),
            )
            .order_by('-balance')[:limit]
        )
        return students

    @staticmethod
    def detect_unusual_payment_patterns() -> List[Payment]:
        """
        Detect unusually large payments considered as outliers.
        """
        avg_amount = Payment.objects.aggregate(avg=Avg('amount'))['avg'] or 0
        threshold = avg_amount * 3
        return Payment.objects.filter(amount__gte=threshold).order_by('-amount')

    @staticmethod
    def suggest_invoice_improvements() -> str:
        """
        Suggest improvements for invoice formatting.
        """
        return (
            "Improve invoice readability by using clear fee item names, "
            "due dates, and highlight any penalties or discounts."
        )
