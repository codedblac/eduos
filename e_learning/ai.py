from django.utils import timezone
from django.db.models import Avg, Q
from .models import (
    Course, Lesson, Assignment, Quiz, QuizSubmission, AssignmentSubmission,
    StudentLessonProgress, CourseEnrollment, AIPredictedScore
)
from students.models import Student
from exams.models import ExamResult
from notifications.utils import notify_user
from institutions.models import Institution


class ELearningAIAssistant:
    def __init__(self, user):
        self.user = user
        self.institution = user.institution

    # ------------------------
    #  STUDENT MODULES
    # ------------------------

    def personalized_learning_path(self):
        """Suggests next lessons per enrolled course."""
        student = self.user.student
        enrollments = CourseEnrollment.objects.filter(student=student, is_active=True)
        path = []

        for enrollment in enrollments:
            course = enrollment.course
            progress = StudentLessonProgress.objects.filter(
                student=student, lesson__chapter__course=course
            )
            completed_lessons = progress.filter(is_completed=True).values_list('lesson_id', flat=True)
            next_lessons = Lesson.objects.filter(
                chapter__course=course
            ).exclude(id__in=completed_lessons).order_by('order')[:3]
            path.extend(next_lessons)

        return path

    def recommend_resources(self):
        """Recommends lessons from courses where the student scored poorly in quizzes."""
        student = self.user.student
        weak_courses = QuizSubmission.objects.filter(
            student=student,
            score__lt=50
        ).values_list('quiz__course', flat=True).distinct()

        return Lesson.objects.filter(
            chapter__course__in=weak_courses
        ).order_by('?')[:5]

    def incomplete_work_alerts(self):
        """Returns pending assignments and quizzes."""
        student = self.user.student
        enrolled_courses = CourseEnrollment.objects.filter(student=student).values('course')

        pending_assignments = Assignment.objects.filter(
            course__in=enrolled_courses,
            due_date__gte=timezone.now()
        ).exclude(id__in=AssignmentSubmission.objects.filter(student=student).values('assignment'))

        pending_quizzes = Quiz.objects.filter(
            course__in=enrolled_courses,
            end_time__gte=timezone.now()
        ).exclude(id__in=QuizSubmission.objects.filter(student=student).values('quiz'))

        return {
            'assignments': pending_assignments,
            'quizzes': pending_quizzes,
        }

    def nudge_notifications(self):
        """Sends reminders to students with pending work."""
        data = self.incomplete_work_alerts()
        if data['assignments'] or data['quizzes']:
            notify_user(
                user=self.user,
                title="Pending Academic Tasks",
                message=f"You have {len(data['assignments'])} assignments and {len(data['quizzes'])} quizzes pending.",
                category="e_learning"
            )

    # ------------------------
    #  TEACHER MODULES
    # ------------------------

    def lesson_plan_suggestions(self):
        """Suggests content ideas for teachers per course."""
        courses = Course.objects.filter(created_by=self.user)
        return {
            course.title: [f"💡 Suggestion: Add a video or quiz to chapter {i + 1}" for i in range(3)]
            for course in courses
        }

    def class_insights(self):
        """Generates average scores per student for teacher's class."""
        students = Student.objects.filter(
            institution=self.institution,
            class_level=getattr(self.user.teacher, 'class_level', None)
        )
        insights = []
        for student in students:
            avg_score = QuizSubmission.objects.filter(student=student).aggregate(Avg('score'))['score__avg'] or 0
            insights.append({
                'student': student.full_name,
                'average_score': round(avg_score, 2)
            })
        return sorted(insights, key=lambda x: x['average_score'])

    def feedback_suggestions(self, submission):
        """Returns feedback string based on score."""
        score = submission.score or 0
        if score < 40:
            return "⚠️ Needs improvement — review related lessons and ask questions."
        elif 40 <= score < 70:
            return "📘 Fair work — revisit the material and retry the quiz."
        return "✅ Excellent work! Keep it up!"

    # ------------------------
    #  ADMIN MODULES
    # ------------------------

    def underperforming_overview(self):
        """Detects subjects with low performance across the school."""
        results = ExamResult.objects.filter(institution=self.institution)
        subjects = results.values_list('subject__name', flat=True).distinct()
        overview = {}

        for subject in subjects:
            avg = results.filter(subject__name=subject).aggregate(Avg('score'))['score__avg'] or 0
            if avg < 50:
                overview[subject] = round(avg, 2)

        return overview

    def predictive_insights(self):
        """Returns top 10 AI-predicted performers."""
        return AIPredictedScore.objects.filter(
            course__institution=self.institution
        ).order_by('-predicted_score')[:10]

    def schedule_recommendations(self):
        """Gives admin strategic planning tips."""
        return [
            "📅 Schedule Math live classes on Thursday mornings to avoid conflicts.",
            "🚫 Avoid e-learning events during exam week.",
            "🧠 Recommend a staff training workshop next term."
        ]

    # ------------------------
    #  PLATFORM INTELLIGENCE
    # ------------------------

    def multilingual_translate(self, text, language_code):
        """Stub: Translate text using multilingual models (placeholder)."""
        return f"[Translated to {language_code}]: {text}"

    def voice_assistant_stub(self, query):
        """Stub: Simulates voice query response."""
        return f"🎤 Voice assistant processed: '{query}'"

    def search_help(self, query):
        """Returns basic search result for lesson titles/descriptions."""
        return Lesson.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:5]
