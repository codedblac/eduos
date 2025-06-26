from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Subject, SubjectClassLevel, SubjectTeacher


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'institution', 'is_core', 'is_elective')
    search_fields = ('name', 'code')
    list_filter = ('is_core', 'is_elective', 'institution')


@admin.register(SubjectClassLevel)
class SubjectClassLevelAdmin(admin.ModelAdmin):
    list_display = ('subject', 'class_level', 'compulsory')
    list_filter = ('class_level', 'compulsory')


@admin.register(SubjectTeacher)
class SubjectTeacherAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject')
    search_fields = ('teacher__full_name', 'subject__name')
