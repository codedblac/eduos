from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    ActivityCategory, Activity, StudentActivityParticipation, ActivityEvent,
    StudentAward, StudentReflection, ActivitySession, ActivityAttendance,
    TalentRecommendation
)


# Inline for participations in Activity
class StudentActivityParticipationInline(admin.TabularInline):
    model = StudentActivityParticipation
    extra = 0
    readonly_fields = ('joined_on',)


# Inline for ActivitySessions within an Activity
class ActivitySessionInline(admin.TabularInline):
    model = ActivitySession
    extra = 0
    readonly_fields = ('created_by',)


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


@admin.register(StudentActivityParticipation)
class StudentActivityParticipationAdmin(admin.ModelAdmin):
    list_display = ('student', 'activity', 'joined_on', 'skill_level', 'is_active')
    list_filter = ('skill_level', 'is_active', 'joined_on')
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
    list_display = ('title', 'student', 'activity', 'level', 'date_awarded')
    list_filter = ('level', 'date_awarded', 'activity__category')
    search_fields = ('title', 'description', 'student__user__username')
    autocomplete_fields = ('student', 'activity')


@admin.register(StudentReflection)
class StudentReflectionAdmin(admin.ModelAdmin):
    list_display = ('participation', 'author', 'date')
    list_filter = ('date', 'author')
    search_fields = ('reflection', 'participation__student__user__username')
    autocomplete_fields = ('participation', 'author')


# Inline attendance inside a session
class ActivityAttendanceInline(admin.TabularInline):
    model = ActivityAttendance
    extra = 0
    autocomplete_fields = ('student',)


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
    list_display = ('student', 'area', 'recommended_date', 'suggested_by')
    list_filter = ('area', 'recommended_date')
    search_fields = ('student__user__username', 'area', 'notes')
    autocomplete_fields = ('student', 'suggested_by')
