from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from e_wallet.models import WalletTransaction, MicroFee, StudentWallet
from students.models import Student
from finance.models import StudentFinanceSnapshot


class EWalletAIEngine:
    """
    Intelligent engine for analyzing e-wallet data, spending trends,
    and providing smart financial insights.
    """

    @staticmethod
    def get_top_spenders(limit=5):
        """
        Return top students by wallet spending.
        """
        return (
            WalletTransaction.objects
            .filter(type='debit')
            .values(
                'wallet__student__id',
                'wallet__student__user__first_name',
                'wallet__student__user__last_name'
            )
            .annotate(total_spent=Sum('amount'))
            .order_by('-total_spent')[:limit]
        )

    @staticmethod
    def get_wallet_balance_predictions(student):
        """
        Predict how long current wallet balance will last
        based on average daily spend.
        """
        txns = WalletTransaction.objects.filter(wallet__student=student, type='debit')

        if txns.count() < 3:
            return "Insufficient data for prediction."

        # Calculate average daily spend
        daily_spend = (
            txns.extra({'day': "date(created_at)"})
            .values('day')
            .annotate(total=Sum('amount'))
            .aggregate(avg=Avg('total'))['avg']
        )

        balance = student.wallet.balance
        if not daily_spend or daily_spend == 0:
            return "Unable to predict due to zero average daily spend."

        days_remaining = int(balance / daily_spend)
        return f"Estimated {days_remaining} days before balance runs out."

    @staticmethod
    def detect_unusual_spending(student):
        """
        Flag recent high transactions relative to student's average.
        """
        recent_txns = WalletTransaction.objects.filter(wallet__student=student, type='debit').order_by('-created_at')[:5]
        avg_amount = WalletTransaction.objects.filter(wallet__student=student, type='debit').aggregate(avg=Avg('amount'))['avg'] or 0

        unusual = []
        for txn in recent_txns:
            if avg_amount > 0 and txn.amount > avg_amount * 2:
                unusual.append({
                    "amount": txn.amount,
                    "reason": "Unusually high compared to historical average.",
                    "created_at": txn.created_at,
                    "reference": txn.reference
                })

        return unusual

    @staticmethod
    def predict_collection_rate(fee):
        """
        Estimate collection rate for a given MicroFee based on past similar charges.
        """
        similar = MicroFee.objects.filter(
            Q(title__icontains=fee.title) |
            Q(class_level=fee.class_level)
        ).exclude(id=fee.id)

        if not similar.exists():
            return "Insufficient data for estimating collection rate."

        total_students = similar.aggregate(total=Sum('students__count'))['total'] or 0
        total_paid = sum(microfee.payments.count() for microfee in similar)

        if total_students == 0:
            return "Unable to calculate — no student data."

        rate = (total_paid / total_students) * 100
        return f"Predicted collection rate: {round(rate, 1)}%"

    @staticmethod
    def recommend_payment_plan(student):
        """
        Suggest a smart top-up plan based on historical finance snapshots.
        """
        snapshots = StudentFinanceSnapshot.objects.filter(student=student).order_by('-last_updated')[:3]

        if snapshots.count() < 2:
            return ["Not enough financial history to recommend a plan."]

        avg_term_payment = snapshots.aggregate(avg=Avg('total_paid'))['avg'] or 0
        balance = student.wallet.balance

        advice = []
        if balance < avg_term_payment * 0.3:
            advice.append("Wallet balance is low. Recommend topping up 70% of average term spend.")
        else:
            advice.append("Current balance is healthy.")

        return advice
