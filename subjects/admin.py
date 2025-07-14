from django.contrib import admin
from .models import (
    SubjectCategory, Subject, SubjectClassLevel, SubjectTeacher,
    SubjectPrerequisite, SubjectAssessmentWeight, SubjectGradingScheme,
    SubjectResource, SubjectVersion, SubjectAnalyticsLog
)


@admin.register(SubjectCategory)
class SubjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')
    ordering = ('name',)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'category', 'curriculum_type', 'is_core', 'is_elective', 'is_active', 'archived', 'created_at')
    list_filter = ('institution', 'category', 'curriculum_type', 'is_core', 'is_elective', 'is_active', 'archived')
    search_fields = ('name', 'code', 'description')
    ordering = ('name',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SubjectClassLevel)
class SubjectClassLevelAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_level', 'compulsory')
    list_filter = ('class_level', 'compulsory')
    search_fields = ('subject__name', 'class_level__name')
    ordering = ('subject__name',)


@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'is_head', 'assigned_at')
    list_filter = ('is_head', 'subject', 'teacher')
    search_fields = (
        'subject__name',
        'teacher__user__first_name',
        'teacher__user__last_name',
        'teacher__user__email'
    )
    ordering = ('subject__name',)


@admin.register(SubjectPrerequisite)
class SubjectPrerequisiteAdmin(admin.ModelAdmin):
    list_display = ('subject', 'prerequisite', 'is_corequisite')
    search_fields = ('subject__name', 'prerequisite__name')
    ordering = ('subject__name',)


@admin.register(SubjectAssessmentWeight)
class SubjectAssessmentWeightAdmin(admin.ModelAdmin):
    list_display = ('subject', 'term', 'component', 'weight_percentage')
    list_filter = ('term', 'component')
    search_fields = ('subject__name', 'component')
    ordering = ('subject__name', 'term')


@admin.register(SubjectGradingScheme)
class SubjectGradingSchemeAdmin(admin.ModelAdmin):
    list_display = ('subject', 'grade', 'min_score', 'max_score', 'remarks')
    search_fields = ('subject__name', 'grade', 'remarks')
    ordering = ('subject__name', '-max_score')


@admin.register(SubjectResource)
class SubjectResourceAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'type', 'uploaded_by', 'uploaded_at')
    list_filter = ('type', 'subject')
    search_fields = ('title', 'url')
    ordering = ('-uploaded_at',)
    readonly_fields = ('uploaded_at',)


@admin.register(SubjectVersion)
class SubjectVersionAdmin(admin.ModelAdmin):
    list_display = ('subject', 'version_number', 'created_by', 'created_at')
    list_filter = ('subject', 'created_by')
    search_fields = ('subject__name', 'version_number', 'changelog')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(SubjectAnalyticsLog)
class SubjectAnalyticsLogAdmin(admin.ModelAdmin):
    list_display = ('subject', 'average_score', 'highest_score', 'lowest_score', 'recorded_at')
    list_filter = ('subject',)
    ordering = ('-recorded_at',)
    date_hierarchy = 'recorded_at'
    readonly_fields = ('recorded_at',)
