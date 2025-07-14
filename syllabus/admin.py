from django.contrib import admin
from .models import (
    Curriculum, CurriculumSubject, SyllabusTopic, SyllabusSubtopic,
    LearningOutcome, TeachingResource, SyllabusProgress,
    SyllabusVersion, SyllabusAuditLog
)


class CurriculumSubjectInline(admin.TabularInline):
    model = CurriculumSubject
    extra = 0
    autocomplete_fields = ['subject', 'class_level', 'term']
    show_change_link = True


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'is_active', 'created_at')
    list_filter = ('is_active', 'institution')
    search_fields = ('name', 'code', 'description')
    inlines = [CurriculumSubjectInline]
    ordering = ['-created_at']


@admin.register(CurriculumSubject)
class CurriculumSubjectAdmin(admin.ModelAdmin):
    list_display = ('subject', 'curriculum', 'class_level', 'term', 'ordering')
    list_filter = ('curriculum', 'class_level', 'term')
    search_fields = ('subject__name', 'curriculum__name')
    ordering = ('curriculum', 'class_level', 'term', 'ordering')
    autocomplete_fields = ['curriculum', 'subject', 'class_level', 'term']


class SyllabusSubtopicInline(admin.TabularInline):
    model = SyllabusSubtopic
    extra = 0
    show_change_link = True


class LearningOutcomeInline(admin.TabularInline):
    model = LearningOutcome
    extra = 0
    show_change_link = True


@admin.register(SyllabusTopic)
class SyllabusTopicAdmin(admin.ModelAdmin):
    list_display = ('short_title', 'curriculum_subject', 'bloom_taxonomy_level', 'difficulty', 'order')
    list_filter = ('curriculum_subject__curriculum', 'difficulty', 'bloom_taxonomy_level')
    search_fields = ('title', 'description')
    ordering = ('curriculum_subject', 'order')
    inlines = [SyllabusSubtopicInline, LearningOutcomeInline]
    autocomplete_fields = ['curriculum_subject']

    def short_title(self, obj):
        return obj.title[:60] + '...' if len(obj.title) > 60 else obj.title
    short_title.short_description = "Title"


@admin.register(SyllabusSubtopic)
class SyllabusSubtopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'order')
    list_filter = ('topic__curriculum_subject__curriculum',)
    search_fields = ('title', 'notes')
    ordering = ('topic', 'order')
    autocomplete_fields = ['topic']


@admin.register(LearningOutcome)
class LearningOutcomeAdmin(admin.ModelAdmin):
    list_display = ('short_description', 'topic', 'competency_area', 'order')
    list_filter = ('topic__curriculum_subject__curriculum',)
    search_fields = ('description', 'indicators')
    ordering = ('topic', 'order')
    autocomplete_fields = ['topic']

    def short_description(self, obj):
        return obj.description[:80] + '...' if len(obj.description) > 80 else obj.description


@admin.register(TeachingResource)
class TeachingResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'type', 'subtopic', 'outcome', 'uploaded_by', 'created_at')
    list_filter = ('type', 'uploaded_by')
    search_fields = ('title', 'url')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['subtopic', 'outcome', 'uploaded_by']


@admin.register(SyllabusProgress)
class SyllabusProgressAdmin(admin.ModelAdmin):
    list_display = ('topic', 'teacher', 'status', 'coverage_date')
    list_filter = ('status', 'teacher')
    search_fields = ('topic__title', 'notes', 'teacher__username', 'teacher__first_name', 'teacher__last_name')
    ordering = ('teacher', 'topic')
    autocomplete_fields = ('topic', 'teacher')


@admin.register(SyllabusVersion)
class SyllabusVersionAdmin(admin.ModelAdmin):
    list_display = ('curriculum_subject', 'version_number', 'created_by', 'created_at')
    search_fields = ('version_number', 'change_log')
    list_filter = ('created_by',)
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    autocomplete_fields = ['curriculum_subject', 'created_by']


@admin.register(SyllabusAuditLog)
class SyllabusAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action', 'user', 'timestamp', 'curriculum_subject', 'topic')
    list_filter = ('action', 'user')
    search_fields = ('action', 'notes', 'user__username')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'
    autocomplete_fields = ['user', 'curriculum_subject', 'topic']
