# staff/ai.py

from django.db.models import Count, Q, Avg
from datetime import timedelta
from django.utils import timezone
from .models import Staff, StaffAttendance
from accounts.models import CustomUser


class StaffAIEngine:
    """
    AI Engine for HR insights in EduOS staff app.
    """

    def __init__(self, institution):
        self.institution = institution

    def get_staff_summary(self):
        """
        Returns staff counts by category (teaching, non-teaching, support)
        """
        data = Staff.objects.filter(institution=self.institution)
        return {
            "total_staff": data.count(),
            "teaching_staff": data.filter(is_teaching=True).count(),
            "non_teaching_staff": data.filter(is_teaching=False).count(),
            "support_staff": data.filter(staff_type="support").count(),
        }

    def identify_understaffed_departments(self):
        """
        Suggests departments that may be understaffed based on subject load
        and active teaching staff.
        """
        from departments.models import Department, Subject

        understaffed = []
        departments = Department.objects.filter(institution=self.institution)

        for dept in departments:
            subjects = Subject.objects.filter(department=dept)
            teaching_staff_count = Staff.objects.filter(
                institution=self.institution,
                is_teaching=True,
                department=dept
            ).count()

            if subjects.count() > teaching_staff_count:
                understaffed.append({
                    "department": dept.name,
                    "subjects": subjects.count(),
                    "teachers": teaching_staff_count,
                    "gap": subjects.count() - teaching_staff_count
                })

        return understaffed

    def get_attendance_summary(self):
        """
        Analyzes staff attendance over the past 30 days.
        """
        today = timezone.now().date()
        last_month = today - timedelta(days=30)

        attendance = StaffAttendance.objects.filter(
            staff__institution=self.institution,
            date__range=(last_month, today)
        )

        total_records = attendance.count()
        present_count = attendance.filter(status='present').count()
        absent_count = attendance.filter(status='absent').count()

        return {
            "total_records": total_records,
            "present": present_count,
            "absent": absent_count,
            "attendance_rate": round((present_count / total_records) * 100, 2) if total_records else 0
        }

    def predict_overworked_staff(self):
        """
        Uses workload and recent attendance to identify overworked staff.
        """
        flagged = []
        staff_qs = Staff.objects.filter(institution=self.institution, is_teaching=True)

        for staff in staff_qs:
            subjects_count = staff.subjects.count()
            recent_attendance = staff.attendance_records.filter(
                date__gte=timezone.now().date() - timedelta(days=30)
            )
            absence_count = recent_attendance.filter(status='absent').count()

            if subjects_count > 4 and absence_count >= 3:
                flagged.append({
                    "staff": staff.get_full_name(),
                    "email": staff.user.email,
                    "subjects_assigned": subjects_count,
                    "absences_last_30_days": absence_count
                })

        return flagged

    def recommend_training_areas(self):
        """
        Recommends training needs based on repeated absences or department gaps.
        """
        flagged = []
        staff_qs = Staff.objects.filter(institution=self.institution)

        for staff in staff_qs:
            recent_absences = staff.attendance_records.filter(
                status='absent',
                date__gte=timezone.now().date() - timedelta(days=90)
            ).count()

            if recent_absences >= 5:
                flagged.append({
                    "staff": staff.get_full_name(),
                    "email": staff.user.email,
                    "suggested_training": "Workplace Wellness or Time Management"
                })

        return flagged
