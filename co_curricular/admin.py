from django.contrib import admin
from .models import (
    ActivityCategory,
    Activity,
    StudentActivityParticipation,
    ActivityEvent,
    StudentAward,
    StudentReflection,
    ActivitySession,
    ActivityAttendance,
    TalentRecommendation,
    StudentProfile,
    CoachFeedback,
    ActivityPerformance,
    CoachAssignmentHistory
)

# Inlines
class StudentActivityParticipationInline(admin.TabularInline):
    model = StudentActivityParticipation
    extra = 0
    readonly_fields = ('joined_on',)


class ActivitySessionInline(admin.TabularInline):
    model = ActivitySession
    extra = 0
    readonly_fields = ('created_by',)


class ActivityAttendanceInline(admin.TabularInline):
    model = ActivityAttendance
    extra = 0
    autocomplete_fields = ('student',)


# Admin registrations
@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category_type', 'institution', 'is_active')
    list_filter = ('category_type', 'institution', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('category_type', 'name')


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'coach_or_patron', 'capacity', 'is_competitive', 'institution', 'is_active')
    list_filter = ('category', 'is_active', 'is_competitive', 'institution')
    search_fields = ('name', 'description', 'coach_or_patron__username')
    inlines = [StudentActivityParticipationInline, ActivitySessionInline]
    autocomplete_fields = ('category', 'coach_or_patron', 'institution')


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('student', 'created_at', 'updated_at')
    search_fields = ('student__user__username', 'interests', 'long_term_goals')
    autocomplete_fields = ('student',)
    filter_horizontal = ('preferred_categories',)


@admin.register(StudentActivityParticipation)
class StudentActivityParticipationAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'joined_on', 'skill_level', 'status', 'is_active')
    list_filter = ('skill_level', 'status', 'is_active', 'joined_on')
    search_fields = ('student__user__username', 'activity__name', 'notes')
    autocomplete_fields = ('student', 'activity')


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'activity', 'start_date', 'end_date', 'venue', 'created_by', 'institution')
    list_filter = ('start_date', 'activity__category', 'institution')
    search_fields = ('name', 'venue', 'description')
    autocomplete_fields = ('activity', 'created_by', 'institution')


@admin.register(StudentAward)
class StudentAwardAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'activity', 'level', 'date_awarded', 'status')
    list_filter = ('level', 'status', 'date_awarded', 'activity__category')
    search_fields = ('title', 'description', 'student__user__username')
    autocomplete_fields = ('student', 'activity')


@admin.register(StudentReflection)
class StudentReflectionAdmin(admin.ModelAdmin):
    list_display = ('participation', 'author', 'date', 'status')
    list_filter = ('date', 'author', 'status')
    search_fields = ('reflection', 'participation__student__user__username')
    autocomplete_fields = ('participation', 'author')


@admin.register(ActivitySession)
class ActivitySessionAdmin(admin.ModelAdmin):
    list_display = ('activity', 'date', 'start_time', 'end_time', 'venue', 'created_by')
    list_filter = ('date', 'activity__category')
    search_fields = ('activity__name', 'venue', 'notes')
    autocomplete_fields = ('activity', 'created_by')
    inlines = [ActivityAttendanceInline]


@admin.register(ActivityAttendance)
class ActivityAttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'session', 'status')
    list_filter = ('status', 'session__activity__name', 'session__date')
    search_fields = ('student__user__username', 'session__activity__name')
    autocomplete_fields = ('student', 'session')


@admin.register(TalentRecommendation)
class TalentRecommendationAdmin(admin.ModelAdmin):
    list_display = ('student', 'area', 'recommended_date', 'suggested_by', 'status')
    list_filter = ('area', 'recommended_date', 'status')
    search_fields = ('student__user__username', 'area', 'notes')
    autocomplete_fields = ('student', 'suggested_by')


@admin.register(CoachFeedback)
class CoachFeedbackAdmin(admin.ModelAdmin):
    list_display = ('participation', 'coach', 'date', 'rating')
    list_filter = ('coach', 'date')
    search_fields = ('feedback', 'participation__student__user__username')
    autocomplete_fields = ('participation', 'coach')


@admin.register(ActivityPerformance)
class ActivityPerformanceAdmin(admin.ModelAdmin):
    list_display = ('participation', 'date', 'score', 'rating')
    list_filter = ('date',)
    search_fields = ('comments', 'participation__student__user__username')
    autocomplete_fields = ('participation',)


@admin.register(CoachAssignmentHistory)
class CoachAssignmentHistoryAdmin(admin.ModelAdmin):
    list_display = ('activity', 'coach', 'assigned_on', 'ended_on')
    list_filter = ('assigned_on', 'ended_on')
    search_fields = ('activity__name', 'coach__username')
    autocomplete_fields = ('activity', 'coach')
