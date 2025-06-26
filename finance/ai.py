from django.utils import timezone
from students.models import Student
from finance.models import (
    StudentFinanceSnapshot,
    ScholarshipCandidate,
    AnomalyFlag,
)
from django.db.models import Q
import random
import logging

logger = logging.getLogger(__name__)


class FinanceAIEngine:
    """
    Core AI engine for financial insights, predictions, and automation.
    Extensible with ML scoring models for production use.
    """

    def __init__(self, academic_year, term, seed=None):
        self.academic_year = academic_year
        self.term = term
        if seed is not None:
            random.seed(seed)

    def predict_default_risk(self, student):
        """
        Predict a student's likelihood of defaulting on fees.
        Replace with ML-based probability models in future.
        """
        try:
            snapshot = StudentFinanceSnapshot.objects.get(
                student=student,
                academic_year=self.academic_year,
                term=self.term
            )

            if snapshot.total_invoiced == 0:
                return "Unknown"

            ratio = snapshot.total_paid / snapshot.total_invoiced

            if ratio < 0.3:
                return "High"
            elif ratio < 0.7:
                return "Medium"
            else:
                return "Low"

        except StudentFinanceSnapshot.DoesNotExist:
            logger.warning(f"[DefaultRisk] No snapshot for {student}")
            return "Unknown"

    def recommend_scholarship_candidates(self, threshold=0.8):
        """
        Recommend students for scholarships based on financial need + academic potential.
        Scoring is placeholder. Replace with real need + performance metrics or ML.
        """
        candidates = []

        eligible_students = Student.objects.filter(is_active=True)

        for student in eligible_students:
            # Placeholder scoring logic
            need_score = random.uniform(0, 1)         # e.g., income, guardianship, orphan, etc.
            performance_score = random.uniform(0, 1)  # e.g., academic grades or co-curricular
            combined_score = (need_score + performance_score) / 2

            if combined_score >= threshold:
                candidate, _ = ScholarshipCandidate.objects.update_or_create(
                    student=student,
                    academic_year=self.academic_year,
                    defaults={
                        "score": performance_score,
                        "need_score": need_score,
                        "recommended_by_ai": True,
                    }
                )
                candidates.append(candidate)

        logger.info(f"[Scholarships] {len(candidates)} candidates recommended (Threshold ≥ {threshold})")
        return candidates

    def flag_financial_anomalies(self):
        """
        Detect students with suspicious payment behavior — overpayments or deep underpayments.
        """
        flags = []

        snapshots = StudentFinanceSnapshot.objects.filter(
            academic_year=self.academic_year,
            term=self.term
        ).select_related("student")

        for snapshot in snapshots:
            try:
                if snapshot.total_invoiced == 0:
                    continue

                overpay_ratio = snapshot.total_paid / snapshot.total_invoiced

                if overpay_ratio > 1.5:
                    flag, created = AnomalyFlag.objects.get_or_create(
                        student=snapshot.student,
                        description="Unusual overpayment detected."
                    )
                    if created:
                        flags.append(flag)

                elif overpay_ratio < 0.2:
                    flag, created = AnomalyFlag.objects.get_or_create(
                        student=snapshot.student,
                        description="Potential default or severe underpayment."
                    )
                    if created:
                        flags.append(flag)

            except Exception as e:
                logger.error(f"[Anomaly] Error for {snapshot.student}: {e}")

        logger.info(f"[Anomaly] Total anomalies flagged: {len(flags)}")
        return flags
