# exams/tasks.py

from celery import shared_task
from django.utils import timezone
from django.db.models import Avg, Max, Min, Count
from django.core.exceptions import ObjectDoesNotExist

from exams.models import (
    Exam, ExamSubject, ExamResult, StudentScore,
    ExamInsight, ExamPrediction, GradeBoundary
)
from students.models import Student
from subjects.models import Subject
from syllabus.models import SyllabusTopic
from teachers.models import Teacher

from .ai import ExamAIEngine
from .grading_engine import get_grade_boundaries, get_grade


@shared_task
def generate_exam_insights(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return f"Exam with id {exam_id} does not exist."

    for exam_subject in exam.subjects.all():
        subject = exam_subject.subject
        scores = StudentScore.objects.filter(exam_subject=exam_subject)

        if not scores.exists():
            continue

        aggregate = scores.aggregate(
            avg=Avg('score'),
            high=Max('score'),
            low=Min('score')
        )

        most_common = scores.values('grade').annotate(freq=Count('grade')).order_by('-freq').first()
        most_common_grade = most_common['grade'] if most_common else "N/A"

        ExamInsight.objects.update_or_create(
            exam=exam,
            subject=subject,
            defaults={
                'average_score': round(aggregate['avg'], 2) if aggregate['avg'] else 0,
                'highest_score': aggregate['high'] or 0,
                'lowest_score': aggregate['low'] or 0,
                'most_common_grade': most_common_grade,
                'insight_summary': f"Avg: {aggregate['avg']:.2f}, High: {aggregate['high']}, "
                                   f"Low: {aggregate['low']}, Grade: {most_common_grade}",
                'generated_at': timezone.now()
            }
        )


@shared_task
def auto_generate_exam_prediction(subject_id, class_level_id, stream_id, term, year, institution_id, user_id):
    try:
        subject = Subject.objects.get(id=subject_id)
        class_level = subject.classlevel_set.get(id=class_level_id)
        stream = class_level.stream_set.get(id=stream_id)
    except ObjectDoesNotExist:
        return "Invalid subject/class_level/stream specified."

    topics = SyllabusTopic.objects.filter(
        curriculum_subject__subject=subject,
        curriculum_subject__class_level=class_level,
        curriculum_subject__term=term
    )

    if not topics.exists():
        return "No syllabus topics found for this configuration."

    try:
        predicted_questions, source_summary, latex_exam, marking_scheme = ExamAIEngine.generate_exam_from_topics(topics)
    except Exception as e:
        return f"AI Exam generation failed: {str(e)}"

    ExamPrediction.objects.create(
        subject=subject,
        class_level=class_level,
        stream=stream,
        term=term,
        year=year,
        institution_id=institution_id,
        predicted_questions=predicted_questions,
        source_summary=source_summary,
        auto_generated_exam=latex_exam,
        auto_generated_marking_scheme=marking_scheme,
        created_by_id=user_id
    )


@shared_task
def auto_grade_exam(exam_id):
    try:
        exam = Exam.objects.get(id=exam_id)
    except Exam.DoesNotExist:
        return f"Exam with id {exam_id} does not exist."

    for exam_subject in exam.subjects.all():
        boundaries = get_grade_boundaries(exam.institution, exam_subject.subject)
        scores = StudentScore.objects.filter(exam_subject=exam_subject)

        for score in scores:
            score.grade = get_grade(score.score, boundaries)
            score.save(update_fields=["grade"])


@shared_task
def archive_old_exams():
    """
    Automatically archive exams older than 1 year.
    """
    year_threshold = timezone.now().year - 1
    old_exams = Exam.objects.filter(year__lte=year_threshold, archived=False)

    for exam in old_exams:
        exam.archived = True
        exam.save(update_fields=["archived"])


@shared_task
def notify_teachers_missing_scores():
    """
    Notify teachers if they haven't submitted full scores for their subjects.
    Replace with actual notification logic (email, in-app).
    """
    active_exams = Exam.objects.filter(archived=False)

    for exam in active_exams:
        for exam_subject in exam.subjects.all():
            expected_count = Student.objects.filter(
                class_level=exam.class_level,
                stream=exam.stream,
                institution=exam.institution
            ).count()

            submitted_count = StudentScore.objects.filter(exam_subject=exam_subject).count()

            if submitted_count < expected_count:
                teacher = exam_subject.teacher
                if teacher and teacher.user.email:
                    # TODO: Integrate with `notifications` app or `send_mail`
                    print(f"Notify {teacher.user.email} => {submitted_count}/{expected_count} scores submitted for {exam_subject.subject.name} in {exam.name}")
