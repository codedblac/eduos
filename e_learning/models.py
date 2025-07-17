from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from students.models import Student
from accounts.models import CustomUser
from subjects.models import Subject
from classes.models import ClassLevel, Stream

User = CustomUser

# -------------------------------
# COURSE STRUCTURE
# -------------------------------
class Course(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='elearning_courses')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='elearning/course_thumbnails/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['institution', 'subject', 'title']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} [{self.subject.name}]"


class CourseChapter(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = ['course', 'order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    LESSON_TYPE_CHOICES = [
        ('video', 'Video'),
        ('pdf', 'PDF'),
        ('slide', 'Slide'),
        ('doc', 'Document'),
        ('whiteboard', 'Whiteboard'),
        ('external', 'External Link')
    ]

    chapter = models.ForeignKey(CourseChapter, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    lesson_type = models.CharField(max_length=20, choices=LESSON_TYPE_CHOICES)
    video_file = models.FileField(upload_to='elearning/lessons/videos/', null=True, blank=True)
    document_file = models.FileField(upload_to='elearning/lessons/docs/', null=True, blank=True)
    embedded_url = models.URLField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_downloadable = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"


class LessonDiscussion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='discussions')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)


class LessonAccessControl(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    allowed_roles = models.JSONField(default=list)  # e.g. ['student', 'teacher']


# -------------------------------
# CLASSROOM + ENROLLMENT
# -------------------------------
class CourseEnrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='elearning_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['student', 'course']


class CourseCohortLink(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['course', 'class_level', 'stream']


# -------------------------------
# LIVE CLASSES
# -------------------------------
class LiveClassSession(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='live_sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    platform = models.CharField(max_length=50, choices=[('zoom', 'Zoom'), ('jitsi', 'Jitsi'), ('eduos', 'EduOS Live')])
    meeting_link = models.URLField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_recorded = models.BooleanField(default=False)
    attendance_required = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


# -------------------------------
# ASSESSMENTS
# -------------------------------
class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='elearning/assignments/', null=True, blank=True)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='elearning/submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ['assignment', 'student']


class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    is_timed = models.BooleanField(default=False)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=[('mcq', 'Multiple Choice'), ('truefalse', 'True/False'), ('short', 'Short Answer')])
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.TextField()


class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    answers = models.JSONField()

    class Meta:
        unique_together = ['quiz', 'student']


# -------------------------------
# CERTIFICATES & REVIEWS
# -------------------------------
class CourseCompletion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    certificate_issued = models.BooleanField(default=False)
    certificate_file = models.FileField(upload_to='elearning/certificates/', null=True, blank=True)

    class Meta:
        unique_together = ['student', 'course']


class CourseReview(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'student']


# -------------------------------
# COMMUNICATION
# -------------------------------
class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class MessageThread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    participants = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)


class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# -------------------------------
# ANALYTICS & AI
# -------------------------------
class StudentLessonProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watched_duration = models.PositiveIntegerField(default=0)
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'lesson']


class TeacherActivityLog(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


class AIPredictedScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    predicted_score = models.DecimalField(max_digits=5, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)


class PlagiarismReport(models.Model):
    submission = models.ForeignKey(AssignmentSubmission, on_delete=models.CASCADE)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2)
    checked_at = models.DateTimeField(auto_now_add=True)
    report_file = models.FileField(upload_to='elearning/plagiarism_reports/', null=True, blank=True)


class LessonDownloadLog(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    downloaded_at = models.DateTimeField(auto_now_add=True)


# -------------------------------
# INTERNATIONALIZATION
# -------------------------------
class CourseTranslation(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    language_code = models.CharField(max_length=10)
    translated_title = models.CharField(max_length=255)
    translated_description = models.TextField()


# -------------------------------
# METADATA & TAGGING
# -------------------------------
class CourseMetadata(models.Model):
    course = models.OneToOneField(Course, on_delete=models.CASCADE)
    tags = models.JSONField(blank=True, null=True)
    seo_keywords = models.TextField(blank=True)


class InstructorProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='elearning/instructors/', null=True, blank=True)
    expertise = models.CharField(max_length=255, blank=True)


class Badge(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.ImageField(upload_to='elearning/badges/')


class StudentBadge(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_at = models.DateTimeField(auto_now_add=True)


# Optional tagging model (if you're not using JSONField in CourseMetadata)
class CourseTag(models.Model):
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='tags')
    tag = models.CharField(max_length=50)

    class Meta:
        unique_together = ['course', 'tag']

    def __str__(self):
        return f"{self.course.title} - {self.tag}"


# More detailed certificate object (optional but useful if you want more than file in CourseCompletion)
class CourseCertificate(models.Model):
    course_completion = models.OneToOneField('CourseCompletion', on_delete=models.CASCADE, related_name='certificate')
    title = models.CharField(max_length=255, default="Certificate of Completion")
    issue_date = models.DateField(auto_now_add=True)
    signature = models.ImageField(upload_to='elearning/certificates/signatures/', null=True, blank=True)
    certificate_file = models.FileField(upload_to='elearning/certificates/files/', null=True, blank=True)

    def __str__(self):
        return f"Certificate for {self.course_completion.student} - {self.course_completion.course}"
