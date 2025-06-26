from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from students.models import Student
from institutions.models import Institution

# 1. Visitor Management
class VisitorLog(models.Model):
    name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    purpose = models.CharField(max_length=255, help_text="Reason for visit, e.g., 'Guardian meeting'")
    person_to_visit = models.CharField(max_length=255)
    check_in = models.DateTimeField(default=timezone.now)
    check_out = models.DateTimeField(null=True, blank=True)
    badge_number = models.CharField(max_length=50, blank=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.name} - {self.purpose}"

# 2. Appointment Scheduling
class Appointment(models.Model):
    visitor_name = models.CharField(max_length=255)
    contact = models.CharField(max_length=100, blank=True)
    purpose = models.CharField(max_length=255)
    meeting_with = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='appointments')
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('cancelled', 'Cancelled'), ('completed', 'Completed')], default='pending')
    remarks = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Appointment with {self.meeting_with} at {self.scheduled_time}"

# 3. Parcel and Delivery Tracking
class ParcelDelivery(models.Model):
    item_description = models.CharField(max_length=255)
    sender = models.CharField(max_length=255)
    recipient_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='parcel_deliveries')
    received_by = models.CharField(max_length=255)
    received_on = models.DateTimeField(default=timezone.now)
    picked_up_by = models.CharField(max_length=255, blank=True)
    picked_up_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('received', 'Received'), ('picked_up', 'Picked Up')], default='received')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"Parcel for {self.recipient_student or self.recipient_staff}"

# 4. Gate Pass Issuance
class GatePass(models.Model):
    issued_to_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    issued_to_staff = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    reason = models.CharField(max_length=255)
    time_out = models.DateTimeField(default=timezone.now)
    time_in = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='gatepass_approvals')
    is_returned = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        person = self.issued_to_student or self.issued_to_staff
        return f"GatePass for {person}"

# 5. Front Desk Ticketing
class FrontDeskTicket(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    submitted_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    category = models.CharField(max_length=100, choices=[
        ('inquiry', 'Inquiry'),
        ('complaint', 'Complaint'),
        ('service', 'Service Request')
    ])
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed')
    ], default='open')
    created_on = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.subject

# 6. Announcements for Walk-in Guests
class FrontAnnouncement(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    display_from = models.DateTimeField()
    display_until = models.DateTimeField()
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

# 7. Security Logs (e.g., vehicles, manual entries)
class SecurityLog(models.Model):
    ENTRY_TYPE = [
        ('staff', 'Staff'),
        ('student', 'Student'),
        ('visitor', 'Visitor'),
        ('vehicle', 'Vehicle'),
        ('other', 'Other'),
    ]
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPE)
    name_or_plate = models.CharField(max_length=255, help_text="Name for person, plate for vehicle")
    time_in = models.DateTimeField(default=timezone.now)
    time_out = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    recorded_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entry_type} - {self.name_or_plate}"
