from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, F
from .models import (
    SchoolAttendanceRecord,
    ClassAttendanceRecord,
    AttendanceStatus,
)
from students.models import Student
from accounts.models import CustomUser


class AttendanceAnalytics:
    """
    Centralized analytics for institutional, class, and user-based attendance insights.
    """

    def __init__(self, institution, academic_year=None, term=None):
        self.institution = institution
        self.academic_year = academic_year
        self.term = term
        self.today = timezone.now().date()

    # -----------------------------
    # 🔷 SCHOOL-WIDE ANALYTICS
    # -----------------------------

    def daily_school_summary(self, date=None):
        """
        Summary of school attendance for a specific date.
        """
        date = date or self.today

        records = SchoolAttendanceRecord.objects.filter(
            institution=self.institution,
            date=date
        )

        present = records.filter(entry_time__isnull=False).count()
        absent = CustomUser.objects.filter(
            institution=self.institution,
            is_active=True
        ).exclude(id__in=records.values_list('user', flat=True)).count()

        return {
            "date": date,
            "present": present,
            "absent": absent,
            "total_users": present + absent,
        }

    def late_arrivals_summary(self, after_time="08:30"):
        """
        Number of late arrivals for today or the past 7 days.
        """
        late_records = SchoolAttendanceRecord.objects.filter(
            institution=self.institution,
            entry_time__gt=after_time,
            date__gte=self.today - timedelta(days=7)
        )

        return {
            "late_entries": late_records.count(),
            "unique_users": late_records.values('user').distinct().count()
        }

    # -----------------------------
    # 🔷 STUDENT ATTENDANCE METRICS
    # -----------------------------

    def student_attendance_rate(self, student: Student, days=30):
        """
        Calculates attendance rate for a student over the past `days`.
        """
        start_date = self.today - timedelta(days=days)

        total_classes = ClassAttendanceRecord.objects.filter(
            student=student,
            date__range=(start_date, self.today)
        ).count()

        present_count = ClassAttendanceRecord.objects.filter(
            student=student,
            status=AttendanceStatus.PRESENT,
            date__range=(start_date, self.today)
        ).count()

        rate = (present_count / total_classes) * 100 if total_classes > 0 else 0
        return {
            "student": student.full_name,
            "rate": round(rate, 2),
            "total_classes": total_classes,
            "attended": present_count
        }

    def top_absentees(self, limit=10, days=30):
        """
        Lists top students with the highest number of absences.
        """
        start_date = self.today - timedelta(days=days)
        absences = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            student__isnull=False,
            status=AttendanceStatus.ABSENT,
            date__range=(start_date, self.today)
        ).values('student__id', 'student__full_name').annotate(
            absence_count=Count('id')
        ).order_by('-absence_count')[:limit]

        return [
            {
                "student_id": entry["student__id"],
                "name": entry["student__full_name"],
                "absences": entry["absence_count"]
            } for entry in absences
        ]

    # -----------------------------
    # 🔷 TEACHER ATTENDANCE ANALYTICS
    # -----------------------------

    def teacher_missed_lessons(self, days=30):
        """
        Lists teachers and how many classes they missed recently.
        """
        start_date = self.today - timedelta(days=days)

        missed = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            teacher__isnull=False,
            status=AttendanceStatus.ABSENT,
            date__range=(start_date, self.today)
        ).values('teacher__id', 'teacher__full_name').annotate(
            missed_lessons=Count('id')
        ).order_by('-missed_lessons')

        return [
            {
                "teacher_id": row["teacher__id"],
                "name": row["teacher__full_name"],
                "missed_lessons": row["missed_lessons"]
            } for row in missed
        ]

    def teacher_participation_summary(self, teacher: CustomUser, days=30):
        """
        Shows summary of teacher presence in class attendance.
        """
        start = self.today - timedelta(days=days)
        total = ClassAttendanceRecord.objects.filter(
            teacher=teacher,
            date__range=(start, self.today)
        ).count()
        present = ClassAttendanceRecord.objects.filter(
            teacher=teacher,
            status=AttendanceStatus.PRESENT,
            date__range=(start, self.today)
        ).count()

        rate = (present / total) * 100 if total > 0 else 0
        return {
            "teacher": teacher.full_name,
            "attendance_rate": round(rate, 2),
            "total_classes": total,
            "present": present
        }

    # -----------------------------
    # 🔷 HEATMAP & TRENDS
    # -----------------------------

    def weekly_absence_trend(self):
        """
        Returns list of absences grouped by weekday (Mon–Sun).
        """
        records = ClassAttendanceRecord.objects.filter(
            institution=self.institution,
            status=AttendanceStatus.ABSENT,
            date__gte=self.today - timedelta(days=30)
        )

        weekday_data = records.annotate(
            weekday=F('date__week_day')
        ).values('weekday').annotate(
            total=Count('id')
        ).order_by('weekday')

        return [
            {
                "weekday": row['weekday'],
                "absences": row['total']
            } for row in weekday_data
        ]
