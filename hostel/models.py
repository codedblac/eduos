from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from students.models import Student
from institutions.models import Institution


class Hostel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    capacity = models.PositiveIntegerField()
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('mixed', 'Mixed')])
    warden = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='hostel_warden')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class HostelRoom(models.Model):
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms')
    name = models.CharField(max_length=50)
    bed_capacity = models.PositiveIntegerField()
    capacity = models.PositiveIntegerField(default=0)  # Added for admin list_display
    room_type = models.CharField(max_length=20, choices=[('single', 'Single'), ('double', 'Double'), ('dorm', 'Dorm')], default='dorm')
    floor = models.PositiveIntegerField(default=1)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.hostel.name} - Room {self.name}"

    def current_occupancy(self):
        return self.allocations.filter(is_active=True).count()

    def is_full(self):
        return self.current_occupancy() >= self.bed_capacity


class RoomAllocation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE, related_name='allocations')
    start_date = models.DateField(default=timezone.now)  # Added for admin list_display
    date_allocated = models.DateTimeField(default=timezone.now)
    allocated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'room')

    def __str__(self):
        return f"{self.student.full_name()} → {self.room}"


class HostelLeaveRequest(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    reason = models.TextField()
    approved = models.BooleanField(null=True)  # None = pending
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    requested_at = models.DateTimeField(auto_now_add=True)
    leave_date = models.DateField()
    return_date = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class HostelInspection(models.Model):
    room = models.ForeignKey(HostelRoom, on_delete=models.CASCADE)
    inspected_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    notes = models.TextField(blank=True)
    cleanliness_score = models.PositiveSmallIntegerField(default=0)
    damages_reported = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class HostelViolation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    room = models.ForeignKey(HostelRoom, on_delete=models.SET_NULL, null=True)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    description = models.TextField()
    action_taken = models.TextField(blank=True)
    date_reported = models.DateTimeField(default=timezone.now)
    resolved = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class HostelAnnouncement(models.Model):
    title = models.CharField(max_length=100)
    message = models.TextField()
    target_hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE)
    posted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='hostel_announcements_created')  # Added for admin list_display
    timestamp = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
