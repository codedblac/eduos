# departments/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Q
from django.conf import settings

from departments.models import Department, Subject, DepartmentUser
from exams.models import ExamResult
from attendance.models import ClassAttendanceRecord
from notifications.utils import send_notification  # Your project-specific util


@shared_task
def send_department_role_notification(department_user_id):
    """
    Notify a user when they are assigned a new department role.
    """
    try:
        dept_user = DepartmentUser.objects.select_related('user', 'department').get(id=department_user_id)
        message = (
            f"You have been assigned the role of {dept_user.get_role_display()} "
            f"in the {dept_user.department.name} department."
        )
        send_notification(
            user=dept_user.user,
            title="Department Role Assigned",
            message=message,
            target="departments"
        )
    except DepartmentUser.DoesNotExist:
        pass


@shared_task
def notify_underperforming_students(subject_id, threshold=40):
    """
    Notify guardians of students who scored below the threshold in a subject.
    """
    try:
        subject = Subject.objects.get(id=subject_id)
        results = ExamResult.objects.select_related('student', 'student__guardian').filter(
            subject=subject, score__lt=threshold
        )
        for result in results:
            guardian = getattr(result.student, 'guardian', None)
            if guardian:
                send_notification(
                    user=guardian,
                    title=f"Low Performance Alert: {subject.name}",
                    message=(
                        f"{result.student.get_full_name()} scored {result.score} in {subject.name}. "
                        f"Please take appropriate academic support actions."
                    ),
                    target="exams"
                )
    except Subject.DoesNotExist:
        pass


@shared_task
def compute_department_performance(department_id):
    """
    Compute average score for each subject in a department.
    Returns: { 'Math': 68.5, 'Science': 74.0, ... }
    """
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
    """
    Compute attendance percentage for each teacher in a department.
    Returns: { 'Mr. John Doe': 95.0, 'Ms. Jane Smith': 88.5, ... }
    """
    try:
        department = Department.objects.get(id=department_id)
        members = DepartmentUser.objects.filter(department=department, is_active=True)

        attendance_data = {}
        current_month = timezone.now().month

        for member in members:
            records = ClassAttendanceRecord.objects.filter(
                teacher=member.user,
                date__month=current_month
            )
            if records.exists():
                avg_status = records.aggregate(rate=Avg('status'))['rate']  # Assuming status is 1 (present) or 0 (absent)
                attendance_data[member.user.get_full_name()] = round(avg_status * 100, 1)
            else:
                attendance_data[member.user.get_full_name()] = 0.0  # No data defaults to 0%

        return attendance_data
    except Department.DoesNotExist:
        return {}
