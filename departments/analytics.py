from django.db.models import Count, Avg, Q
from datetime import date
from .models import Department, DepartmentUser, Subject
from exams.models import ExamResult
from attendance.models import TeacherAttendance
from accounts.models import CustomUser


class DepartmentAnalyticsEngine:
    def __init__(self, department: Department):
        self.department = department

    def count_department_users(self):
        """
        Total users per role in department.
        """
        role_counts = DepartmentUser.objects.filter(
            department=self.department,
            is_active=True
        ).values('role').annotate(total=Count('id'))

        # Format: {'role': 'hod', 'total': 3}
        return {
            entry['role']: entry['total'] for entry in role_counts
        }

    def count_subjects(self):
        """
        Total subjects, assigned vs unassigned.
        """
        total = Subject.objects.filter(department=self.department).count()
        assigned = Subject.objects.filter(department=self.department, assigned_teacher__isnull=False).count()
        return {
            'total_subjects': total,
            'assigned': assigned,
            'unassigned': total - assigned
        }

    def recent_exam_performance_summary(self):
        """
        Summary stats for recent exams — average, highest, lowest scores per subject.
        """
        subjects = Subject.objects.filter(department=self.department, is_examable=True)
        data = []

        for subject in subjects:
            results = ExamResult.objects.filter(subject=subject)
            count = results.count()
            if count == 0:
                continue
            avg_score = round(results.aggregate(Avg('score'))['score__avg'], 2)
            top_score = results.order_by('-score').first().score
            lowest_score = results.order_by('score').first().score
            data.append({
                'subject': subject.name,
                'average_score': avg_score,
                'highest_score': top_score,
                'lowest_score': lowest_score,
                'entries': count
            })
        return data

    def teacher_attendance_summary(self):
        """
        Calculates total attendance % for department teachers.
        """
        users = DepartmentUser.objects.filter(department=self.department, is_active=True).values_list('user_id', flat=True)
        teachers = CustomUser.objects.filter(id__in=users)
        summary = []

        for teacher in teachers:
            records = TeacherAttendance.objects.filter(teacher=teacher)
            total = records.count()
            present = records.filter(status='present').count()
            attendance_rate = round((present / total) * 100, 1) if total > 0 else 0.0
            summary.append({
                'teacher': teacher.get_full_name(),
                'attendance_rate': attendance_rate
            })
        return summary

    def full_report(self):
        """
        Combines analytics into a single structured report.
        """
        return {
            'user_distribution': self.count_department_users(),
            'subject_distribution': self.count_subjects(),
            'exam_performance': self.recent_exam_performance_summary(),
            'teacher_attendance': self.teacher_attendance_summary(),
        }
