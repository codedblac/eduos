from django.utils import timezone
from django.db.models import Q
from students.models import Student
from finance.models import (
    StudentFinanceSnapshot,
    ScholarshipCandidate,
    AnomalyFlag,
)
import random
import logging

logger = logging.getLogger(__name__)


class FinanceAIEngine:
    """
    Core AI engine for financial insights, predictions, and automation.
    Extensible with ML scoring models or statistical heuristics.
    """

    def __init__(self, academic_year, term, seed=None):
        self.academic_year = academic_year
        self.term = term
        if seed is not None:
            random.seed(seed)

    def predict_default_risk(self, student):
        """
        Predict a student's default risk based on payment ratio.
        Replace with ML scoring model in production.
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
            logger.warning(f"[DefaultRisk] No snapshot found for student {student.id}")
            return "Unknown"

    def recommend_scholarship_candidates(self, threshold=0.8):
        """
        Recommends students for scholarship based on financial need + performance.
        Placeholder scoring logic. Replace with ML/scoring models in future.
        """
        candidates = []

        eligible_students = Student.objects.filter(is_active=True)

        for student in eligible_students:
            try:
                # TODO: Replace with actual need and academic performance data
                need_score = random.uniform(0, 1)
                performance_score = random.uniform(0, 1)
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

            except Exception as e:
                logger.error(f"[ScholarshipAI] Error evaluating {student.id}: {e}")

        logger.info(f"[Scholarships] {len(candidates)} candidates recommended (Threshold ≥ {threshold})")
        return candidates

    def flag_financial_anomalies(self):
        """
        Flags students with anomalous finance activity.
        Currently flags overpayment > 150% and underpayment < 20%.
        """
        anomalies = []

        snapshots = StudentFinanceSnapshot.objects.filter(
            academic_year=self.academic_year,
            term=self.term
        ).select_related("student")

        for snapshot in snapshots:
            try:
                if snapshot.total_invoiced == 0:
                    continue

                ratio = snapshot.total_paid / snapshot.total_invoiced

                if ratio > 1.5:
                    flag, created = AnomalyFlag.objects.get_or_create(
                        student=snapshot.student,
                        description="Unusual overpayment detected."
                    )
                    if created:
                        anomalies.append(flag)

                elif ratio < 0.2:
                    flag, created = AnomalyFlag.objects.get_or_create(
                        student=snapshot.student,
                        description="Potential default or severe underpayment."
                    )
                    if created:
                        anomalies.append(flag)

            except Exception as e:
                logger.error(f"[AnomalyDetection] Failed for {snapshot.student.id}: {e}")

        logger.info(f"[AnomalyDetection] Total anomalies flagged: {len(anomalies)}")
        return anomalies
