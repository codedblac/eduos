from datetime import timedelta
from django.db.models import Sum, F
from django.utils import timezone

from finance.models import (
    Income, Expense, Refund, Waiver,
    StudentFinanceSnapshot, Budget, WalletTransaction
)
from students.models import Student


class FinanceAnalytics:
    """
    Centralized financial analytics service for dashboards and reports.
    """

    def __init__(self, institution=None, academic_year=None, term=None):
        self.institution = institution
        self.academic_year = academic_year
        self.term = term

    def income_expense_summary(self):
        """
        Returns total income, total expense, and net balance for the selected budget scope.
        """
        income_total = Income.objects.filter(
            budget__institution=self.institution,
            budget__academic_year=self.academic_year,
            budget__term=self.term
        ).aggregate(total=Sum('amount'))['total'] or 0

        expense_total = Expense.objects.filter(
            budget__institution=self.institution,
            budget__academic_year=self.academic_year,
            budget__term=self.term
        ).aggregate(total=Sum('amount'))['total'] or 0

        return {
            "total_income": float(income_total),
            "total_expense": float(expense_total),
            "net_balance": float(income_total - expense_total)
        }

    def refund_stats(self):
        """
        Returns total refunds requested and approved within the academic year.
        """
        refunds = Refund.objects.filter(student__institution=self.institution)

        if self.academic_year:
            refunds = refunds.filter(academic_year=self.academic_year)

        total_requested = refunds.aggregate(total=Sum('amount'))['total'] or 0
        total_approved = refunds.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0

        return {
            "total_requested": float(total_requested),
            "total_approved": float(total_approved)
        }

    def waiver_distribution(self):
        """
        Returns waiver totals grouped by term name within the selected academic year.
        """
        waivers = Waiver.objects.filter(
            student__institution=self.institution,
            academic_year=self.academic_year,
            term=self.term
        ).values(term_name=F('term__name')).annotate(
            total_waiver=Sum('amount')
        ).order_by('term_name')

        return [
            {
                "term": w['term_name'],
                "total_waiver": float(w['total_waiver'] or 0)
            }
            for w in waivers
        ]

    def fee_collection_progress(self):
        """
        Returns collected vs expected fee summary and collection rate percentage.
        """
        qs = StudentFinanceSnapshot.objects.filter(
            student__institution=self.institution,
            academic_year=self.academic_year,
            term=self.term
        )

        total_paid = qs.aggregate(total=Sum('total_paid'))['total'] or 0
        total_invoiced = qs.aggregate(total=Sum('total_invoiced'))['total'] or 0
        collection_rate = (total_paid / total_invoiced * 100) if total_invoiced > 0 else 0.0

        return {
            "collected": float(total_paid),
            "expected": float(total_invoiced),
            "collection_rate": round(collection_rate, 2)
        }

    def wallet_transactions_summary(self):
        """
        Summarizes student wallet activity — credits, debits, and net wallet balance.
        """
        qs = WalletTransaction.objects.filter(wallet__student__institution=self.institution)

        total_credit = qs.filter(type='credit').aggregate(total=Sum('amount'))['total'] or 0
        total_debit = qs.filter(type='debit').aggregate(total=Sum('amount'))['total'] or 0

        return {
            "credits": float(total_credit),
            "debits": float(total_debit),
            "net_wallet_balance": float(total_credit - total_debit)
        }

    def top_defaulters(self, limit=10):
        """
        Returns students with the highest outstanding balances.
        """
        qs = StudentFinanceSnapshot.objects.filter(
            academic_year=self.academic_year,
            term=self.term,
            student__institution=self.institution,
            balance__gt=0
        ).select_related('student').order_by('-balance')[:limit]

        return [
            {
                "student_id": snapshot.student.id,
                "name": snapshot.student.full_name,
                "balance": float(snapshot.balance)
            }
            for snapshot in qs
        ]

    def daily_collections_chart(self, days=30):
        """
        Returns total daily income received over the past X days for plotting.
        """
        today = timezone.now().date()
        start_date = today - timedelta(days=days)

        qs = Income.objects.filter(
            received_on__range=(start_date, today),
            budget__institution=self.institution
        ).values('received_on').annotate(
            total=Sum('amount')
        ).order_by('received_on')

        return [
            {
                "date": item['received_on'],
                "total": float(item['total'] or 0)
            }
            for item in qs
        ]
