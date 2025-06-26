from django.db.models import Avg, Count, Q
from exams.models import ExamResult
from attendance.models import TeacherAttendance
from .models import Department, Subject, DepartmentUser
from accounts.models import CustomUser


class DepartmentAIEngine:
    def __init__(self, department: Department):
        self.department = department

    def get_average_score_by_subject(self):
        """
        Returns average scores per subject in this department.
        """
        subjects = Subject.objects.filter(department=self.department, is_examable=True)
        data = []
        for subject in subjects:
            results = ExamResult.objects.filter(subject=subject)
            avg_score = round(results.aggregate(Avg('score'))['score__avg'] or 0.0, 2)
            data.append({
                'subject': subject.name,
                'subject_code': subject.code,
                'average_score': avg_score,
            })
        return data

    def get_underperforming_students(self, threshold=40):
        """
        Lists students scoring below threshold in any department subject.
        """
        underperformers = ExamResult.objects.filter(
            subject__department=self.department,
            score__lt=threshold
        ).values(
            'student__id', 'student__user__full_name', 'subject__name', 'score'
        )
        return list(underperformers)

    def get_teacher_attendance_summary(self):
        """
        Returns attendance rate per teacher in the department.
        """
        teachers = CustomUser.objects.filter(
            id__in=DepartmentUser.objects.filter(
                department=self.department,
                is_active=True
            ).values_list('user_id', flat=True)
        )

        data = []
        for teacher in teachers:
            records = TeacherAttendance.objects.filter(teacher=teacher)
            total = records.count()
            present = records.filter(status='present').count()
            attendance_rate = round((present / total) * 100, 1) if total > 0 else 0.0
            data.append({
                'teacher': teacher.get_full_name(),
                'attendance_rate': attendance_rate,
            })
        return data

    def get_subject_assignment_gaps(self):
        """
        Identifies subjects without assigned teachers.
        """
        unassigned = Subject.objects.filter(department=self.department, assigned_teacher__isnull=True)
        return [{
            'subject': sub.name,
            'code': sub.code
        } for sub in unassigned]

    def summary_dashboard(self):
        """
        Compiles a full AI dashboard for the HOD.
        """
        return {
            'average_scores': self.get_average_score_by_subject(),
            'teacher_attendance': self.get_teacher_attendance_summary(),
            'unassigned_subjects': self.get_subject_assignment_gaps(),
            'underperforming_students': self.get_underperforming_students(),
        }
