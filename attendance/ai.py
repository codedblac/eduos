import logging
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q

from .models import ClassAttendanceRecord, SchoolAttendanceRecord, AttendanceStatus
from students.models import Student
from accounts.models import CustomUser
from institutions.models import Institution

logger = logging.getLogger(__name__)


class AttendanceAIEngine:
    """
    Smart engine for analyzing and predicting attendance patterns.
    """

    def __init__(self, institution: Institution, term=None):
        self.institution = institution
        self.term = term
        self.today = timezone.now().date()

    def flag_high_absentee_students(self, threshold=3, window_days=7):
        """
        Flags students who have missed `threshold` or more classes in the past `window_days`.
        """
        cutoff = self.today - timedelta(days=window_days)
        flagged = []

        absentees = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            status=AttendanceStatus.ABSENT,
            student__isnull=False,
            date__gte=cutoff
        ).values('student').annotate(
            total_absences=Count('id')
        ).filter(total_absences__gte=threshold)

        for entry in absentees:
            student_id = entry['student']
            total_absences = entry['total_absences']
            try:
                student = Student.objects.get(id=student_id)
                flagged.append({
                    "student": student,
                    "absences": total_absences,
                    "risk": self._get_risk_level(total_absences, threshold)
                })
            except Student.DoesNotExist:
                continue

        logger.info(f"[AttendanceAI] Flagged {len(flagged)} high-absence students")
        return flagged

    def predict_teacher_lateness_risk(self):
        """
        Identifies teachers likely to arrive late or miss class, based on past patterns.
        """
        recent_records = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            teacher__isnull=False,
            status=AttendanceStatus.ABSENT,
            date__gte=self.today - timedelta(days=30)
        ).values('teacher').annotate(total_absences=Count('id')).order_by('-total_absences')

        predictions = []
        for item in recent_records:
            teacher = CustomUser.objects.filter(id=item['teacher']).first()
            if teacher:
                predictions.append({
                    "teacher": teacher,
                    "absences": item['total_absences'],
                    "risk": self._get_risk_level(item['total_absences'], 3)
                })

        logger.info(f"[AttendanceAI] Teacher lateness predictions generated")
        return predictions

    def identify_late_school_entries(self, after_time="08:30"):
        """
        Detects users consistently entering school after a given time.
        """
        late_entries = SchoolAttendanceRecord.objects.filter(
            institution=self.institution,
            entry_time__gt=after_time,
            date__gte=self.today - timedelta(days=10)
        ).values('user').annotate(
            late_days=Count('id')
        ).order_by('-late_days')

        results = []
        for entry in late_entries:
            user = CustomUser.objects.filter(id=entry['user']).first()
            if user:
                results.append({
                    "user": user,
                    "late_days": entry['late_days'],
                })

        logger.info(f"[AttendanceAI] Found {len(results)} users with late entries")
        return results

    def absentee_heatmap_data(self, days=30):
        """
        Returns heatmap data: absences per day to visualize trends.
        """
        start_date = self.today - timedelta(days=days)
        qs = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            status=AttendanceStatus.ABSENT,
            date__range=(start_date, self.today)
        ).values('date').annotate(
            total=Count('id')
        ).order_by('date')

        return [{"date": row['date'], "absences": row['total']} for row in qs]

    def _get_risk_level(self, absences, threshold):
        """
        Simple logic for assigning risk levels.
        """
        if absences >= threshold + 3:
            return "High"
        elif absences >= threshold:
            return "Medium"
        else:
            return "Low"
