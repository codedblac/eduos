from django.contrib import admin
from assessments import models


@admin.register(models.AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active")
    search_fields = ("name",)


@admin.register(models.AssessmentTemplate)
class AssessmentTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "type", "duration_minutes", "total_marks", "is_active")
    list_filter = ("type", "is_active")
    search_fields = ("name", "description")


@admin.register(models.AssessmentGroup)
class AssessmentGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "term", "institution", "created_by", "created_at")
    list_filter = ("term", "institution")
    search_fields = ("name",)


@admin.register(models.Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "title", "subject", "class_level", "term", "type", "group",
        "scheduled_date", "is_published", "delivery_mode", "creation_method"
    )
    list_filter = ("subject", "class_level", "term", "type", "is_published", "delivery_mode")
    search_fields = ("title",)
    date_hierarchy = "scheduled_date"


@admin.register(models.AssessmentWeight)
class AssessmentWeightAdmin(admin.ModelAdmin):
    list_display = ("institution", "subject", "term", "type", "weight")
    list_filter = ("institution", "subject", "term")
    search_fields = ("subject__name",)


@admin.register(models.AssessmentLock)
class AssessmentLockAdmin(admin.ModelAdmin):
    list_display = ("assessment", "locked", "locked_at", "reason")
    list_filter = ("locked",)
    search_fields = ("assessment__title",)


class AnswerChoiceInline(admin.TabularInline):
    model = models.AnswerChoice
    extra = 1


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "assessment", "type", "order", "marks", "difficulty_level")
    list_filter = ("assessment", "type", "difficulty_level")
    inlines = [AnswerChoiceInline]
    search_fields = ("text",)


@admin.register(models.CodeTestCase)
class CodeTestCaseAdmin(admin.ModelAdmin):
    list_display = ("question", "weight")
    search_fields = ("question__text",)


@admin.register(models.AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ("student", "assessment", "started_at", "submitted_at", "is_graded", "is_adaptive")
    list_filter = ("assessment", "is_graded", "is_adaptive")
    search_fields = ("student__user__username", "assessment__title")


@admin.register(models.AssessmentVisibility)
class AssessmentVisibilityAdmin(admin.ModelAdmin):
    list_display = ("session", "can_view_score", "can_view_feedback", "released_at")
    list_filter = ("can_view_score", "can_view_feedback")


@admin.register(models.StudentAnswer)
class StudentAnswerAdmin(admin.ModelAdmin):
    list_display = ("session", "question", "selected_choice", "marks_awarded", "auto_graded")
    list_filter = ("auto_graded",)
    search_fields = ("question__text",)


@admin.register(models.MarkingScheme)
class MarkingSchemeAdmin(admin.ModelAdmin):
    list_display = ("question", "rubric_link")
    search_fields = ("question__text",)


@admin.register(models.GradingRubric)
class GradingRubricAdmin(admin.ModelAdmin):
    list_display = ("question", "criteria", "max_score")
    search_fields = ("criteria",)


@admin.register(models.Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("session", "created_by", "created_at")
    search_fields = ("session__student__user__username", "created_by__username")


@admin.register(models.RetakePolicy)
class RetakePolicyAdmin(admin.ModelAdmin):
    list_display = ("assessment", "max_attempts", "wait_time_hours", "allow_partial_retake")


@admin.register(models.PerformanceTrend)
class PerformanceTrendAdmin(admin.ModelAdmin):
    list_display = ("student", "subject", "term", "average_score", "assessment_count", "updated_at")
    list_filter = ("term", "subject")
    search_fields = ("student__user__username", "subject__name")
