from django.db.models import Avg, Count, Q
from django.utils import timezone

from exams.models import ExamResult
from attendance.models import ClassAttendanceRecord
from departments.models import Department, Subject, DepartmentUser
from accounts.models import CustomUser


class DepartmentAIEngine:
    """
    AI-powered engine to assist Heads of Departments (HODs) with insights and analytics.
    """

    def __init__(self, department: Department):
        self.department = department

    def get_average_score_by_subject(self):
        """
        Returns average score for each examable subject in the department.
        """
        subjects = Subject.objects.filter(department=self.department, is_examable=True)
        data = []
        for subject in subjects:
            avg_score = ExamResult.objects.filter(subject=subject).aggregate(
                average=Avg('score')
            )['average']
            data.append({
                'subject': subject.name,
                'code': subject.code,
                'average_score': round(avg_score or 0.0, 2),
            })
        return data

    def get_underperforming_students(self, threshold=40):
        """
        Identifies students scoring below threshold in any subject of the department.
        """
        results = ExamResult.objects.filter(
            subject__department=self.department,
            score__lt=threshold
        ).select_related('student', 'subject')

        underperformers = []
        for result in results:
            underperformers.append({
                'student_id': result.student.id,
                'student_name': result.student.get_full_name(),
                'subject': result.subject.name,
                'score': result.score
            })
        return underperformers

    def get_teacher_attendance_summary(self):
        """
        Computes current month's attendance rate per teacher in the department.
        """
        current_month = timezone.now().month
        current_year = timezone.now().year

        teacher_ids = DepartmentUser.objects.filter(
            department=self.department,
            is_active=True
        ).values_list('user_id', flat=True)

        data = []
        for teacher in CustomUser.objects.filter(id__in=teacher_ids, is_active=True):
            records = ClassAttendanceRecord.objects.filter(
                teacher=teacher,
                date__year=current_year,
                date__month=current_month
            )
            total = records.count()
            present = records.filter(status='present').count()
            attendance_rate = round((present / total) * 100, 1) if total > 0 else 0.0

            data.append({
                'teacher_id': teacher.id,
                'teacher_name': teacher.get_full_name(),
                'attendance_rate': attendance_rate
            })
        return data

    def get_subject_assignment_gaps(self):
        """
        Lists subjects in the department without assigned teachers.
        """
        unassigned = Subject.objects.filter(
            department=self.department,
            assigned_teacher__isnull=True
        )
        return [
            {
                'subject': s.name,
                'code': s.code
            } for s in unassigned
        ]

    def get_subject_load_distribution(self):
        """
        Returns number of subjects each teacher in the department is handling.
        """
        subject_counts = Subject.objects.filter(
            department=self.department,
            assigned_teacher__isnull=False
        ).values(
            'assigned_teacher__id',
            'assigned_teacher__first_name',
            'assigned_teacher__last_name'
        ).annotate(subject_count=Count('id')).order_by('-subject_count')

        return [
            {
                'teacher_id': entry['assigned_teacher__id'],
                'teacher_name': f"{entry['assigned_teacher__first_name']} {entry['assigned_teacher__last_name']}".strip(),
                'subject_count': entry['subject_count']
            }
            for entry in subject_counts
        ]

    def get_student_subject_distribution(self):
        """
        Placeholder: Returns student count per subject if subject enrollment model exists.
        """
        return []

    def summary_dashboard(self):
        """
        Returns all compiled insights for the department's performance dashboard.
        """
        return {
            'average_scores_by_subject': self.get_average_score_by_subject(),
            'underperforming_students': self.get_underperforming_students(),
            'teacher_attendance_summary': self.get_teacher_attendance_summary(),
            'unassigned_subjects': self.get_subject_assignment_gaps(),
            'teacher_subject_load': self.get_subject_load_distribution()
        }
