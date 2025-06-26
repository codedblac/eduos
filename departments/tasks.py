from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Avg, Count, Q

from .models import Department, Subject, DepartmentUser
from exams.models import ExamResult  # assuming this exists
from attendance.models import TeacherAttendance  # assuming this exists
from notifications.utils import send_notification  # abstracted notification function


@shared_task
def send_department_role_notification(department_user_id):
    try:
        dept_user = DepartmentUser.objects.select_related('user', 'department').get(id=department_user_id)
        message = f"You have been assigned the role of {dept_user.get_role_display()} in the {dept_user.department.name} Department."
        send_notification(
            user=dept_user.user,
            title="New Department Role",
            message=message,
            target="departments"
        )
    except DepartmentUser.DoesNotExist:
        pass


@shared_task
def notify_underperforming_students(subject_id, threshold=40):
    try:
        subject = Subject.objects.get(id=subject_id)
        results = ExamResult.objects.filter(subject=subject, score__lt=threshold)
        for result in results:
            send_notification(
                user=result.student.guardian,  # assuming linked
                title=f"Low Performance in {subject.name}",
                message=f"{result.student.get_full_name()} scored {result.score} in {subject.name}.",
                target="exams"
            )
    except Subject.DoesNotExist:
        pass


@shared_task
def compute_department_performance(department_id):
    try:
        department = Department.objects.prefetch_related('subjects').get(id=department_id)
        subjects = department.subjects.all()
        performance = {}
        for subject in subjects:
            avg_score = ExamResult.objects.filter(subject=subject).aggregate(avg=Avg('score'))['avg']
            if avg_score is not None:
                performance[subject.name] = round(avg_score, 2)
        return performance
    except Department.DoesNotExist:
        return {}


@shared_task
def compute_teacher_attendance(department_id):
    try:
        department = Department.objects.get(id=department_id)
        teachers = DepartmentUser.objects.filter(department=department, is_active=True)
        attendance_data = {}
        for user in teachers:
            attendance_rate = TeacherAttendance.objects.filter(
                teacher=user.user,
                date__month=timezone.now().month
            ).aggregate(rate=Avg('status'))['rate']  # assuming binary attendance (1 or 0)
            attendance_data[user.user.get_full_name()] = round(attendance_rate * 100, 1) if attendance_rate else 0
        return attendance_data
    except Department.DoesNotExist:
        return {}
