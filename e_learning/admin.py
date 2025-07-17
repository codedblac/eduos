from django.contrib import admin
from .models import (
    Course, CourseChapter, Lesson, LessonDiscussion, LessonAccessControl,
    CourseEnrollment, CourseCohortLink, LiveClassSession,
    Assignment, AssignmentSubmission,
    Quiz, QuizQuestion, QuizSubmission,
    CourseAnnouncement, Message, MessageThread,
    StudentLessonProgress, TeacherActivityLog, AIPredictedScore,
    CourseCompletion, CourseReview,
    LessonDownloadLog, CourseTranslation, PlagiarismReport,
    InstructorProfile, Badge, StudentBadge, CourseMetadata
)

class ChapterInline(admin.TabularInline):
    model = CourseChapter
    extra = 0

class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 0

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'institution', 'created_by', 'is_published', 'is_featured')
    list_filter = ('is_published', 'is_featured', 'institution')
    search_fields = ('title', 'description')
    inlines = [ChapterInline]

@admin.register(CourseChapter)
class CourseChapterAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'order')
    ordering = ('course', 'order')
    inlines = [LessonInline]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('title', 'chapter', 'lesson_type', 'order', 'is_downloadable')
    list_filter = ('lesson_type',)
    search_fields = ('title',)

@admin.register(LessonDiscussion)
class LessonDiscussionAdmin(admin.ModelAdmin):
    list_display = ('lesson', 'user', 'created_at', 'edited_at')
    search_fields = ('comment',)

@admin.register(LessonAccessControl)
class LessonAccessControlAdmin(admin.ModelAdmin):
    list_display = ('lesson',)
    search_fields = ('lesson__title',)

@admin.register(CourseEnrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at', 'is_active')
    list_filter = ('is_active',)

@admin.register(CourseCohortLink)
class CohortAdmin(admin.ModelAdmin):
    list_display = ('course', 'class_level', 'stream')
    list_filter = ('class_level', 'stream')

@admin.register(LiveClassSession)
class LiveClassAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'platform')
    list_filter = ('platform',)

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'due_date', 'created_by')
    list_filter = ('course',)

@admin.register(AssignmentSubmission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'submitted_at', 'marks')
    list_filter = ('assignment',)

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'start_time', 'end_time', 'is_timed')
    list_filter = ('is_timed',)

@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'question_text', 'question_type')
    search_fields = ('question_text',)

@admin.register(QuizSubmission)
class QuizSubmissionAdmin(admin.ModelAdmin):
    list_display = ('quiz', 'student', 'submitted_at', 'score')

@admin.register(CourseAnnouncement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'course', 'created_by', 'created_at')
    search_fields = ('title', 'message')

@admin.register(MessageThread)
class MessageThreadAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'created_at')
    filter_horizontal = ('participants',)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'thread', 'timestamp')
    search_fields = ('content',)

@admin.register(StudentLessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'is_completed', 'watched_duration')

@admin.register(TeacherActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'course', 'action', 'timestamp')

@admin.register(AIPredictedScore)
class AIPredictedScoreAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'predicted_score', 'generated_at')

@admin.register(CourseCompletion)
class CourseCompletionAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'completed_at', 'certificate_issued')

@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ('course', 'student', 'rating', 'submitted_at')

@admin.register(LessonDownloadLog)
class LessonDownloadLogAdmin(admin.ModelAdmin):
    list_display = ('student', 'lesson', 'downloaded_at')

@admin.register(CourseTranslation)
class CourseTranslationAdmin(admin.ModelAdmin):
    list_display = ('course', 'language_code', 'translated_title')

@admin.register(PlagiarismReport)
class PlagiarismReportAdmin(admin.ModelAdmin):
    list_display = ('submission', 'similarity_score', 'checked_at')

@admin.register(InstructorProfile)
class InstructorProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'expertise')
    search_fields = ('expertise',)

@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

@admin.register(StudentBadge)
class StudentBadgeAdmin(admin.ModelAdmin):
    list_display = ('student', 'badge', 'awarded_at')

@admin.register(CourseMetadata)
class CourseMetadataAdmin(admin.ModelAdmin):
    list_display = ('course',)
