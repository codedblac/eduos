from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from institutions.models import Institution
from students.models import Student
from accounts.models import CustomUser
from institutions.models import Institution
from subjects.models import Subject
from classes.models import ClassLevel, Stream

# -------------------------------
# COURSE STRUCTURE
# -------------------------------

class Course(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='elearning_courses')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='elearning/course_thumbnails/', null=True, blank=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
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

    def __str__(self):
        return f"{self.student.full_name} - {self.course.title}"

class CourseCohortLink(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    class_level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    stream = models.ForeignKey(Stream, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        unique_together = ['course', 'class_level', 'stream']

    def __str__(self):
        return f"{self.course.title} -> {self.class_level.name} {self.stream.name if self.stream else ''}"


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
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.course.title} - Live: {self.title}"


# -------------------------------
# ASSESSMENTS
# -------------------------------

class Assignment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='elearning/assignments/', null=True, blank=True)
    due_date = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class AssignmentSubmission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    file = models.FileField(upload_to='elearning/submissions/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ['assignment', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.assignment.title}"

class Quiz(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    is_timed = models.BooleanField(default=False)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    question_type = models.CharField(max_length=20, choices=[
        ('mcq', 'Multiple Choice'), 
        ('truefalse', 'True/False'), 
        ('short', 'Short Answer')
    ])
    options = models.JSONField(blank=True, null=True)
    correct_answer = models.TextField()

    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}"

class QuizSubmission(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    answers = models.JSONField()  # student answers per question

    class Meta:
        unique_together = ['quiz', 'student']

    def __str__(self):
        return f"{self.student.full_name} - {self.quiz.title}"


# -------------------------------
# MESSAGING & ANNOUNCEMENTS
# -------------------------------

class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class MessageThread(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    participants = models.ManyToManyField(CustomUser)
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    thread = models.ForeignKey(MessageThread, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)


# -------------------------------
# ANALYTICS
# -------------------------------

class StudentLessonProgress(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    watched_duration = models.PositiveIntegerField(default=0)  # in minutes
    last_accessed = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['student', 'lesson']

class TeacherActivityLog(models.Model):
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)


# -------------------------------
# AI / EXTRA INTELLIGENCE
# -------------------------------

class AIPredictedScore(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    predicted_score = models.DecimalField(max_digits=5, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)

