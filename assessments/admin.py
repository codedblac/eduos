from django.contrib import admin
from .models import (
    AssessmentType, AssessmentTemplate, Assessment, Question, AnswerChoice,
    AssessmentSession, StudentAnswer, MarkingScheme, GradingRubric,
    Feedback, RetakePolicy
)


# -------------------- Inlines --------------------

class AnswerChoiceInline(admin.TabularInline):
    model = AnswerChoice
    extra = 1


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0
    show_change_link = True


class StudentAnswerInline(admin.TabularInline):
    model = StudentAnswer
    extra = 0
    autocomplete_fields = ('question', 'selected_choice')


class FeedbackInline(admin.TabularInline):
    model = Feedback
    extra = 0
    readonly_fields = ('created_at', 'created_by')


# -------------------- Admin Classes --------------------

@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)


@admin.register(AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'duration_minutes', 'total_marks', 'is_active')
    search_fields = ('name', 'description')
    list_filter = ('type', 'is_active')
    autocomplete_fields = ('type',)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 'subject', 'class_level', 'term', 'type',
        'scheduled_date', 'duration_minutes', 'total_marks', 'is_published'
    )
    list_filter = ('term', 'subject', 'class_level', 'type', 'is_published')
    search_fields = ('title', 'subject__name', 'class_level__name')
    autocomplete_fields = (
        'subject', 'class_level', 'term', 'type', 'template', 'created_by', 'institution'
    )
    ordering = ('-scheduled_date',)
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'assessment', 'type', 'marks', 'difficulty_level')
    list_filter = ('type', 'difficulty_level', 'assessment__subject')
    search_fields = ('text', 'assessment__title')
    autocomplete_fields = ('assessment', 'topic', 'outcome')
    inlines = [AnswerChoiceInline]


@admin.register(AnswerChoice)
class AnswerChoiceAdmin(admin.ModelAdmin):
    list_display = ('text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('text',)
    autocomplete_fields = ('question',)


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = (
        'student', 'assessment', 'started_at', 'submitted_at',
        'score', 'graded_by', 'is_graded', 'is_adaptive'
    )
    list_filter = ('is_graded', 'is_adaptive', 'assessment__term')
    search_fields = ('student__user__username', 'assessment__title')
    autocomplete_fields = ('student', 'assessment', 'graded_by')
    inlines = [StudentAnswerInline, FeedbackInline]


@admin.register(StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = (
        'session', 'question', 'selected_choice', 'marks_awarded', 'auto_graded'
    )
    list_filter = ('auto_graded', 'question__type')
    search_fields = ('question__text',)
    autocomplete_fields = ('session', 'question', 'selected_choice')


@admin.register(MarkingScheme)
class MarkingSchemeAdmin(admin.ModelAdmin):
    list_display = ('question', 'rubric_link')
    search_fields = ('guide',)
    autocomplete_fields = ('question',)


@admin.register(GradingRubric)
class GradingRubricAdmin(admin.ModelAdmin):
    list_display = ('question', 'criteria', 'max_score')
    search_fields = ('criteria',)
    autocomplete_fields = ('question',)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('session', 'created_by', 'created_at')
    search_fields = ('comment', 'created_by__username')
    readonly_fields = ('created_at',)
    autocomplete_fields = ('session', 'created_by')


@admin.register(RetakePolicy)
class RetakePolicyAdmin(admin.ModelAdmin):
    list_display = (
        'assessment', 'max_attempts', 'wait_time_hours', 'allow_partial_retake'
    )
    autocomplete_fields = ('assessment',)
