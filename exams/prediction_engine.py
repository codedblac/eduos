# exams/prediction_engine.py

import random
from django.db.models import Q
from .models import PredictedExam, PredictedQuestion
from library.models import Material, Topic
from subjects.models import Subject
from classes.models import ClassLevel
from teachers.models import Teacher


from utils import extract_keywords, generate_questions_from_text

def fetch_learning_content(subject_id, class_level_id):
    """
    Crawls materials uploaded by teachers, public library, curriculum entries, etc.
    """
    filters = Q(subject_id=subject_id) & Q(class_level_id=class_level_id)

    # Combine relevant content sources
    # materials = Material.objects.filter(filters)
    # curriculum_entries = CurriculumEntry.objects.filter(filters)
    # topics = Topic.objects.filter(filters)

    combined_texts = []

    # for source in [materials, curriculum_entries, topics]:
    #     for item in source:
    #         combined_texts.append(item.content or item.description)

    return "\n".join(combined_texts)

def predict_exam(subject_id, class_level_id, stream_id, created_by):
    """
    Generates a full predicted exam with questions using AI NLP models.
    """
    # Fetch content to train question generator
    raw_text = fetch_learning_content(subject_id, class_level_id)

    if not raw_text.strip():
        raise ValueError("Insufficient learning materials to generate exam.")

    # Extract topics & generate questions
    topics = extract_keywords(raw_text)
    questions = generate_questions_from_text(raw_text, topics)

    # Create the exam record
    subject = Subject.objects.get(id=subject_id)
    class_level = ClassLevel.objects.get(id=class_level_id)

    exam = PredictedExam.objects.create(
        subject=subject,
        class_level=class_level,
        stream_id=stream_id,
        created_by=created_by,
        title=f"AI Predicted Exam: {subject.name} - {class_level.name}"
    )

    # Populate predicted questions
    for q in questions:
        PredictedQuestion.objects.create(
            exam=exam,
            question_text=q['question'],
            answer=q.get('answer'),
            topic=q.get('topic'),
            marks=q.get('marks', 1)
        )

    return exam

