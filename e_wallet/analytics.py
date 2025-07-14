from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from django.db.models.functions import TruncDay
from e_wallet.models import WalletTransaction, MicroFee, MicroFeePayment, Wallet
from students.models import Student
from accounts.models import CustomUser


class EWalletAnalytics:

    @staticmethod
    def get_total_wallet_balance(institution=None):
        """
        Total wallet balance for all students, optionally filtered by institution.
        """
        wallets = Wallet.objects.all()
        if institution:
            wallets = wallets.filter(institution=institution)
        return wallets.aggregate(total=Sum('balance'))['total'] or 0.00

    @staticmethod
    def top_up_summary(days=30, institution=None):
        """
        Aggregated credit transactions (top-ups) in the last `days`.
        """
        since = timezone.now() - timedelta(days=days)
        txns = WalletTransaction.objects.filter(type='credit', created_at__gte=since)
        if institution:
            txns = txns.filter(wallet__institution=institution)

        return (
            txns.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

    @staticmethod
    def top_spending_students(limit=5, institution=None):
        """
        Top students by total wallet spending.
        """
        txns = WalletTransaction.objects.filter(type='debit')
        if institution:
            txns = txns.filter(wallet__institution=institution)

        return (
            txns
            .values(
                'wallet__student__id',
                'wallet__student__user__first_name',
                'wallet__student__user__last_name'
            )
            .annotate(total_spent=Sum('amount'))
            .order_by('-total_spent')[:limit]
        )

    @staticmethod
    def most_paid_micro_fees(limit=5):
        """
        Micro fees with the highest number of students who paid.
        """
        return (
            MicroFee.objects
            .annotate(paid_count=Count('payments'))
            .order_by('-paid_count')[:limit]
        )

    @staticmethod
    def collection_rate_summary():
        """
        Summary of collection rates for all active micro fees.
        """
        data = []
        micro_fees = MicroFee.objects.filter(is_active=True)
        for fee in micro_fees:
            targeted = fee.students.count()
            paid = fee.payments.count()
            rate = (paid / targeted) * 100 if targeted else 0
            data.append({
                "fee_title": fee.title,
                "created_by": f"{fee.teacher.first_name} {fee.teacher.last_name}",
                "total_targeted": targeted,
                "total_paid": paid,
                "collection_rate": round(rate, 2),
                "due_date": fee.due_date
            })
        return data

    @staticmethod
    def average_balance_per_student(institution=None):
        """
        Institution-wide average wallet balance.
        """
        wallets = Wallet.objects.all()
        if institution:
            wallets = wallets.filter(institution=institution)

        return wallets.aggregate(avg=Avg('balance'))['avg'] or 0.00

    @staticmethod
    def daily_transaction_volume(days=30, institution=None):
        """
        Combined daily transaction volume over the last N days.
        """
        since = timezone.now() - timedelta(days=days)
        txns = WalletTransaction.objects.filter(created_at__gte=since)
        if institution:
            txns = txns.filter(wallet__institution=institution)

        return (
            txns.annotate(day=TruncDay('created_at'))
            .values('day')
            .annotate(total=Sum('amount'))
            .order_by('day')
        )

    @staticmethod
    def teacher_fee_posting_summary(teacher_id):
        """
        Summary of micro fees posted by a specific teacher.
        """
        return (
            MicroFee.objects
            .filter(teacher_id=teacher_id)
            .annotate(total_collected=Sum('payments__amount'))
            .values('title', 'due_date', 'total_collected')
        )

    @staticmethod
    def student_wallet_statement(student_id, limit=10):
        """
        Last N wallet transactions for a given student.
        """
        return (
            WalletTransaction.objects
            .filter(wallet__student__id=student_id)
            .order_by('-created_at')[:limit]
            .values('type', 'amount', 'purpose', 'reference', 'created_at')
        )
