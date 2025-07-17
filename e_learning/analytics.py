from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from .models import (
    Course, Lesson, StudentLessonProgress, CourseEnrollment,
    AssignmentSubmission, QuizSubmission, TeacherActivityLog
)
from students.models import Student
from notifications.utils import notify_user


# ---------------------------
# 📊 Student & Course Analytics
# ---------------------------

def get_student_course_progress(student, course):
    """
    Calculates percentage progress for a student in a course.
    """
    lessons = Lesson.objects.filter(chapter__course=course)
    total_lessons = lessons.count()
    if total_lessons == 0:
        return 0

    completed = StudentLessonProgress.objects.filter(
        student=student,
        lesson__in=lessons,
        is_completed=True
    ).count()

    return round((completed / total_lessons) * 100, 2)


def get_course_completion_stats(course):
    """
    Returns average progress across all students enrolled in a course.
    """
    enrollments = CourseEnrollment.objects.filter(course=course, is_active=True)
    total_students = enrollments.count()
    if total_students == 0:
        return 0

    total_progress = 0
    for enrollment in enrollments:
        student = enrollment.student
        total_progress += get_student_course_progress(student, course)

    return round(total_progress / total_students, 2)


def get_course_engagement_metrics(course):
    """
    Returns key engagement metrics for a course.
    """
    total_students = CourseEnrollment.objects.filter(course=course, is_active=True).count()
    total_lessons = Lesson.objects.filter(chapter__course=course).count()

    video_watch_sum = StudentLessonProgress.objects.filter(
        lesson__chapter__course=course
    ).aggregate(total_watch=Sum('watched_duration'))['total_watch'] or 0

    quiz_attempts = QuizSubmission.objects.filter(quiz__course=course).count()
    assignment_submissions = AssignmentSubmission.objects.filter(assignment__course=course).count()

    return {
        "students_enrolled": total_students,
        "total_lessons": total_lessons,
        "video_watch_time": video_watch_sum,
        "quiz_attempts": quiz_attempts,
        "assignments_submitted": assignment_submissions
    }


def get_student_overview(student):
    """
    Compiles performance and activity metrics for a student.
    """
    enrollments = CourseEnrollment.objects.filter(student=student, is_active=True)
    total_courses = enrollments.count()

    avg_quiz_score = QuizSubmission.objects.filter(
        student=student
    ).aggregate(avg=Avg('score'))['avg'] or 0

    completed_lessons = StudentLessonProgress.objects.filter(
        student=student,
        is_completed=True
    ).count()

    assignments_submitted = AssignmentSubmission.objects.filter(student=student).count()

    return {
        "total_courses": total_courses,
        "average_quiz_score": round(avg_quiz_score, 2),
        "lessons_completed": completed_lessons,
        "assignments_submitted": assignments_submitted
    }


# ---------------------------
# 👨‍🏫 Teacher Activity Logging
# ---------------------------

def log_teacher_activity(teacher, course, action):
    """
    Stores a log entry of a teacher's activity.
    """
    TeacherActivityLog.objects.create(
        teacher=teacher,
        course=course,
        action=action
    )


# ---------------------------
# 📈 System-Wide Reports
# ---------------------------

def identify_high_dropout_courses(threshold=30):
    """
    Returns list of courses where the average student progress is below threshold %.
    """
    flagged = []
    for course in Course.objects.all():
        avg_progress = get_course_completion_stats(course)
        if avg_progress < threshold:
            flagged.append({
                "course": course.title,
                "average_progress": avg_progress
            })
    return flagged


def top_performing_students(limit=10):
    """
    Returns top N students by average quiz score.
    """
    students = Student.objects.all()
    student_scores = []

    for student in students:
        avg_score = QuizSubmission.objects.filter(
            student=student
        ).aggregate(avg=Avg('score'))['avg'] or 0

        student_scores.append({
            "student": student.full_name,
            "average_score": round(avg_score, 2)
        })

    return sorted(student_scores, key=lambda x: x["average_score"], reverse=True)[:limit]


def notify_low_engagement_students(threshold=25):
    """
    Notify students with low course completion percentage.
    """
    enrollments = CourseEnrollment.objects.filter(is_active=True)
    for enrollment in enrollments:
        progress = get_student_course_progress(enrollment.student, enrollment.course)
        if progress < threshold:
            notify_user(
                user=enrollment.student.user,
                title="Low Engagement Alert",
                message=f"You're below {threshold}% in {enrollment.course.title}. Consider catching up!",
                category="e_learning"
            )


def course_completion_trend(course, days=30):
    """
    Shows trend of how many students completed lessons over the last N days.
    """
    recent_progress = StudentLessonProgress.objects.filter(
        lesson__chapter__course=course,
        is_completed=True,
        last_accessed__gte=timezone.now() - timedelta(days=days)
    ).extra({'date': "date(last_accessed)"}).values('date').annotate(total=Count('id')).order_by('date')

    return list(recent_progress)
