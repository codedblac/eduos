from datetime import date
from django.utils import timezone
from django.db.models import Count, Avg

from departments.models import Department, DepartmentUser, Subject
from exams.models import ExamResult
from attendance.models import ClassAttendanceRecord
from accounts.models import CustomUser


class DepartmentAnalyticsEngine:
    """
    Analytics engine providing statistical summaries and operational data
    for departmental oversight and dashboards.
    """

    def __init__(self, department: Department):
        self.department = department
        self.current_month = timezone.now().month
        self.current_year = timezone.now().year

    def count_department_users(self):
        """
        Returns a count of users per role (e.g. HOD, deputy, member).
        """
        role_counts = DepartmentUser.objects.filter(
            department=self.department,
            is_active=True
        ).values('role').annotate(total=Count('id'))

        return {
            entry['role']: entry['total'] for entry in role_counts
        }

    def count_subjects(self):
        """
        Calculates total subjects and assigned vs unassigned ones.
        """
        total = Subject.objects.filter(department=self.department).count()
        assigned = Subject.objects.filter(
            department=self.department,
            assigned_teacher__isnull=False
        ).count()

        return {
            'total_subjects': total,
            'assigned_subjects': assigned,
            'unassigned_subjects': total - assigned
        }

    def recent_exam_performance_summary(self):
        """
        Provides average, max, and min score for each subject in recent exams.
        """
        subjects = Subject.objects.filter(department=self.department, is_examable=True)
        summary = []

        for subject in subjects:
            results = ExamResult.objects.filter(subject=subject)

            if not results.exists():
                continue

            aggregated = results.aggregate(average=Avg('score'))

            summary.append({
                'subject': subject.name,
                'code': subject.code,
                'entries': results.count(),
                'average_score': round(aggregated['average'] or 0.0, 2),
                'highest_score': results.order_by('-score').first().score,
                'lowest_score': results.order_by('score').first().score,
            })

        return summary

    def teacher_attendance_summary(self):
        """
        Returns average attendance rate this month per teacher in the department.
        """
        teacher_ids = DepartmentUser.objects.filter(
            department=self.department,
            is_active=True
        ).values_list('user_id', flat=True)

        summary = []

        for teacher in CustomUser.objects.filter(id__in=teacher_ids, is_active=True):
            records = ClassAttendanceRecord.objects.filter(
                teacher=teacher,
                date__year=self.current_year,
                date__month=self.current_month
            )

            total = records.count()
            present = records.filter(status='present').count()
            attendance_rate = round((present / total) * 100, 1) if total > 0 else 0.0

            summary.append({
                'teacher_id': teacher.id,
                'teacher_name': teacher.get_full_name(),
                'attendance_rate': attendance_rate,
                'total_classes': total
            })

        return summary

    def full_report(self):
        """
        Returns a consolidated analytics report for the department.
        """
        return {
            'department_id': self.department.id,
            'department_name': self.department.name,
            'user_distribution': self.count_department_users(),
            'subject_distribution': self.count_subjects(),
            'exam_performance': self.recent_exam_performance_summary(),
            'teacher_attendance': self.teacher_attendance_summary(),
        }
