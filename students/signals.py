from django.db.models.signals import post_save
from django.dispatch import receiver
from exams.models import ExamResult
from .models import Student
from .ai_engine import StudentAIAnalyzer


@receiver(post_save, sender=ExamResult)
def exam_result_post_save(sender, instance, created, **kwargs):
    """
    When an ExamResult is saved (new or updated marks), trigger AI analysis
    for that student to generate feedback, comments, suggestions.
    """
    student = instance.student

    # Run AI analysis (implement this function in ai_engine.py)
    insights = StudentAIAnalyzer(student)

    # Save or update student's AI insights (adjust based on your model design)
    student.ai_insights = insights.get('summary', '')
    student.performance_comments = insights.get('comments', '')
    student.suggested_books = insights.get('recommended_books', [])
    student.suggested_teachers = insights.get('recommended_teachers', [])
    student.save(update_fields=['ai_insights', 'performance_comments'])
