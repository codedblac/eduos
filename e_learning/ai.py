import datetime
from django.utils import timezone
from django.db.models import Avg, Q
from .models import (
    Course, Lesson, Assignment, Quiz, QuizSubmission, AssignmentSubmission,
    StudentLessonProgress, CourseEnrollment, AIPredictedScore
)
from students.models import Student
from exams.models import ExamResult
from notifications.utils import send_notification

class ELearningAIAssistant:

    def __init__(self, user):
        self.user = user
        self.institution = user.institution

    # ------------------------
    # 🎓 STUDENT MODULES
    # ------------------------

    def personalized_learning_path(self):
        student = self.user.student
        enrollments = CourseEnrollment.objects.filter(student=student, is_active=True)
        path = []

        for enrollment in enrollments:
            course = enrollment.course
            progress = StudentLessonProgress.objects.filter(student=student, lesson__chapter__course=course)
            completed_lessons = progress.filter(is_completed=True).values_list('lesson_id', flat=True)
            next_lessons = Lesson.objects.filter(
                chapter__course=course
            ).exclude(id__in=completed_lessons).order_by('order')[:3]
            path.extend(next_lessons)

        return path

    def recommend_resources(self):
        student = self.user.student
        weak_areas = QuizSubmission.objects.filter(
            student=student,
            score__lt=50
        ).values_list('quiz__course', flat=True).distinct()
        lessons = Lesson.objects.filter(
            chapter__course__in=weak_areas
        ).order_by('?')[:5]
        return lessons

    def incomplete_work_alerts(self):
        student = self.user.student
        pending_assignments = Assignment.objects.filter(
            course__in=CourseEnrollment.objects.filter(student=student).values('course'),
            due_date__gte=timezone.now()
        ).exclude(id__in=AssignmentSubmission.objects.filter(student=student).values('assignment'))

        pending_quizzes = Quiz.objects.filter(
            course__in=CourseEnrollment.objects.filter(student=student).values('course'),
            end_time__gte=timezone.now()
        ).exclude(id__in=QuizSubmission.objects.filter(student=student).values('quiz'))

        return {
            'assignments': pending_assignments,
            'quizzes': pending_quizzes,
        }

    def nudge_notifications(self):
        data = self.incomplete_work_alerts()
        if data['assignments'] or data['quizzes']:
            send_notification(
                user=self.user,
                title="Pending Academic Tasks",
                message=f"You have {len(data['assignments'])} assignments and {len(data['quizzes'])} quizzes pending.",
                category="e_learning"
            )

    # ------------------------
    # 🧑‍🏫 TEACHER MODULES
    # ------------------------

    def lesson_plan_suggestions(self):
        courses = Course.objects.filter(created_by=self.user)
        return {c.title: [f"Suggested: Add video for chapter {i+1}" for i in range(3)] for c in courses}

    def class_insights(self):
        students = Student.objects.filter(institution=self.institution, class_level=self.user.teacher.class_level)
        data = []
        for student in students:
            score = QuizSubmission.objects.filter(student=student).aggregate(Avg('score'))['score__avg'] or 0
            data.append({'student': student.full_name, 'avg_score': round(score, 2)})
        return sorted(data, key=lambda x: x['avg_score'])

    def feedback_suggestions(self, submission):
        if submission.score < 40:
            return "Needs improvement — review the related lesson and ask questions."
        elif 40 <= submission.score < 70:
            return "Fair work, but you can improve by revisiting the quiz."
        else:
            return "Excellent performance! Keep it up."

    # ------------------------
    # 🏫 ADMIN MODULES
    # ------------------------

    def underperforming_overview(self):
        results = ExamResult.objects.filter(institution=self.institution)
        subjects = results.values_list('subject__name', flat=True).distinct()
        overview = {}

        for subject in subjects:
            avg = results.filter(subject__name=subject).aggregate(Avg('score'))['score__avg'] or 0
            if avg < 50:
                overview[subject] = round(avg, 2)

        return overview

    def predictive_insights(self):
        scores = AIPredictedScore.objects.filter(course__institution=self.institution)
        return scores.order_by('-predicted_score')[:10]

    def schedule_recommendations(self):
        return [
            "Schedule Math live class on Thursday morning to avoid clashes.",
            "Avoid events during exam week.",
            "Recommend staff training session next term based on feedback."
        ]

    # ------------------------
    # PLATFORM-WIDE INTELLIGENCE
    # ------------------------

    def multilingual_translate(self, text, language_code):
        # Stub translation function (extend with actual LLM or translation API)
        return f"[Translated to {language_code}]: {text}"

    def voice_assistant_stub(self, query):
        # Stub function (replace with OpenAI Whisper / voice integration)
        return f"Voice assistant heard: '{query}' and is processing your request."

    def search_help(self, query):
        # Basic keyword match (extend to vector/semantic search)
        matched_lessons = Lesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))
        return matched_lessons[:5]
