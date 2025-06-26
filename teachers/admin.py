from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Teacher

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'institution', 'is_active', 'date_joined')
    search_fields = ('first_name', 'last_name', 'email', 'institution__name')
    list_filter = ('is_active', 'institution')
    readonly_fields = ('date_joined',)
