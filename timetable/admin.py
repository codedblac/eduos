from django.contrib import admin
from .models import Period, Room, SubjectAssignment, TimetableEntry


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('day', 'get_day_display', 'start_time', 'end_time', 'institution')
    list_filter = ('day', 'institution')
    search_fields = ('institution__name',)
    ordering = ('day', 'start_time')
    readonly_fields = ('institution',)

    def get_day_display(self, obj):
        return obj.get_day_display()
    get_day_display.short_description = 'Day'


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'institution', 'is_lab', 'capacity')
    list_filter = ('is_lab', 'institution')
    search_fields = ('name', 'institution__name')


@admin.register(SubjectAssignment)
class SubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ('teacher_full_name', 'subject', 'stream', 'lessons_per_week', 'institution')
    list_filter = ('teacher__user__is_active', 'subject', 'stream', 'institution')
    search_fields = (
        'teacher__user__first_name',
        'teacher__user__last_name',
        'subject__name',
        'stream__name',
        'stream__class_level__name',
        'institution__name',
    )

    def teacher_full_name(self, obj):
        return obj.teacher.user.get_full_name()
    teacher_full_name.short_description = 'Teacher'
    teacher_full_name.admin_order_field = 'teacher__user__last_name'


@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher_full_name', 'stream', 'period_display', 'room', 'institution', 'created_at')
    list_filter = ('period__day', 'teacher__user__is_active', 'stream__class_level', 'room', 'institution')
    search_fields = (
        'subject__name',
        'teacher__user__first_name',
        'teacher__user__last_name',
        'stream__name',
        'stream__class_level__name',
        'institution__name',
    )
    readonly_fields = ('created_at', 'institution')

    def teacher_full_name(self, obj):
        return obj.teacher.user.get_full_name()
    teacher_full_name.short_description = 'Teacher'
    teacher_full_name.admin_order_field = 'teacher__user__last_name'

    def period_display(self, obj):
        return f"{obj.period.get_day_display()} {obj.period.start_time.strftime('%H:%M')}–{obj.period.end_time.strftime('%H:%M')}"
    period_display.short_description = 'Period'
    period_display.admin_order_field = 'period__day'
