from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    Hostel, HostelRoom, RoomAllocation,
    HostelLeaveRequest, HostelInspection,
    HostelViolation, HostelAnnouncement
)


class BaseInstitutionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(institution=request.user.institution)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.institution = request.user.institution
        obj.save()


@admin.register(Hostel)
class HostelAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'capacity', 'gender', 'institution']
    search_fields = []
    list_filter = ['institution', 'gender']


@admin.register(HostelRoom)
class HostelRoomAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'hostel', 'floor', 'room_type', 'capacity', 'institution']
    search_fields = []
    list_filter = ['hostel', 'room_type', 'institution']


@admin.register(RoomAllocation)
class RoomAllocationAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'room', 'start_date', 'is_active', 'institution']
    search_fields = ['student__user__full_name', 'room__name']
    list_filter = ['institution', 'is_active']


@admin.register(HostelLeaveRequest)
class HostelLeaveRequestAdmin(BaseInstitutionAdmin):
    list_display = ['student', 'leave_date', 'return_date', 'approved', 'institution']
    search_fields = ['student__user__full_name']
    list_filter = ['institution', 'approved']


@admin.register(HostelInspection)
class HostelInspectionAdmin(BaseInstitutionAdmin):
    list_display = ['room', 'inspected_by', 'date', 'institution']
    list_filter = ['institution', 'date']
    search_fields = ['room__name']
    date_hierarchy = 'date'


@admin.register(HostelViolation)
class HostelViolationAdmin(BaseInstitutionAdmin):
    list_display = ['room', 'reported_by', 'resolved', 'date_reported', 'institution']
    list_filter = ['institution', 'resolved']
    search_fields = ['description']
    date_hierarchy = 'date_reported'


@admin.register(HostelAnnouncement)
class HostelAnnouncementAdmin(BaseInstitutionAdmin):
    list_display = ['title', 'target_hostel', 'created_by', 'timestamp', 'institution']
    search_fields = ['title', 'message']
    list_filter = ['institution', 'target_hostel']
    date_hierarchy = 'timestamp'
