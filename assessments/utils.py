from django.utils import timezone
from django.db import transaction
from .models import (
    Assessment, Question, AnswerChoice, AssessmentSession,
    AssessmentTemplate, StudentAnswer
)
from students.models import Student
from syllabus.models import SyllabusTopic, LearningOutcome
import random


def generate_assessment_from_template(template, subject, class_level, term, scheduled_date, created_by=None, institution=None):
    """
    Auto-generate an assessment using a predefined template.
    """
    from institutions.models import Institution

    institution = institution or subject.institution_set.first()

    # Create the Assessment
    assessment = Assessment.objects.create(
        institution=institution,
        title=f"{template.name} - {subject.name} {scheduled_date.strftime('%Y-%m-%d')}",
        subject=subject,
        class_level=class_level,
        term=term,
        type=template.type,
        template=template,
        scheduled_date=scheduled_date,
        duration_minutes=template.duration_minutes,
        total_marks=template.total_marks,
        created_by=created_by,
        is_published=False
    )

    # For demo purposes: randomly generate 5 questions
    sample_question_types = ['mcq', 'short', 'essay', 'code']
    total_marks = template.total_marks
    num_questions = 5
    marks_per_question = total_marks // num_questions

    for i in range(num_questions):
        question = Question.objects.create(
            assessment=assessment,
            text=f"Auto-generated Question {i+1}: Explain the concept of ...",
            type=random.choice(sample_question_types),
            marks=marks_per_question,
            difficulty_level=random.choice(['Easy', 'Medium', 'Hard']),
            order=i+1,
        )

        # Add dummy choices for MCQs
        if question.type == 'mcq':
            correct_index = random.randint(0, 3)
            for j in range(4):
                AnswerChoice.objects.create(
                    question=question,
                    text=f"Option {chr(65+j)}",
                    is_correct=(j == correct_index)
                )

    return assessment


def distribute_assessment_to_students(assessment, delivery_mode="online", stream=None):
    """
    Assign an assessment to students.
    `delivery_mode` can be:
        - "online": assign to be done in app
        - "print": teacher will print and distribute
    """
    if not stream:
        raise ValueError("Stream must be provided to distribute assessment.")

    students = Student.objects.filter(stream=stream, is_active=True)

    with transaction.atomic():
        for student in students:
            AssessmentSession.objects.get_or_create(
                student=student,
                assessment=assessment,
                defaults={
                    "started_at": timezone.now() if delivery_mode == "online" else None
                }
            )


def auto_schedule_home_assessments(institution, subject, class_level, term, frequency='weekly', created_by=None):
    """
    Automatically create and assign assessments for students learning from home.
    `frequency` can be 'weekly', 'biweekly', etc.
    """
    today = timezone.now().date()

    # Pick an active template
    template = AssessmentTemplate.objects.filter(
        type__name__icontains='homework', is_active=True
    ).first()

    if not template:
        raise ValueError("No active homework template found.")

    # Estimate next date (today for now)
    next_date = timezone.datetime.combine(today, timezone.datetime.min.time())

    # Generate and assign
    assessment = generate_assessment_from_template(
        template=template,
        subject=subject,
        class_level=class_level,
        term=term,
        scheduled_date=next_date,
        created_by=created_by,
        institution=institution
    )

    # Distribute to students
    stream = subject.subjectclasslevel_set.filter(class_level=class_level).first().stream_set.first()
    distribute_assessment_to_students(assessment, delivery_mode='online', stream=stream)

    return assessment


def grade_auto_markable_answers(session):
    """
    Grade all MCQ and auto-gradable questions in a session.
    """
    total_score = 0.0

    for answer in session.answers.select_related('question'):
        if answer.question.type == 'mcq' and answer.selected_choice:
            if answer.selected_choice.is_correct:
                answer.marks_awarded = answer.question.marks
            else:
                answer.marks_awarded = 0
            answer.auto_graded = True
            answer.save()
            total_score += float(answer.marks_awarded or 0)

    session.score = total_score
    session.is_graded = True
    session.save()
