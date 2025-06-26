from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from students.models import Student
from institutions.models import Institution


class AlumniProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='alumni_profile')
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    current_city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=255, blank=True)
    course = models.CharField(max_length=255, blank=True)
    profession = models.CharField(max_length=255, blank=True)
    organization = models.CharField(max_length=255, blank=True)
    linkedin_url = models.URLField(blank=True)
    profile_picture = models.ImageField(upload_to='alumni_profiles/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name()} - {self.profession}"


class AlumniEvent(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_date = models.DateField()
    event_time = models.TimeField()
    location = models.CharField(max_length=255)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AlumniEventRegistration(models.Model):
    event = models.ForeignKey(AlumniEvent, on_delete=models.CASCADE, related_name='registrations')
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    registered_on = models.DateTimeField(auto_now_add=True)
    is_attended = models.BooleanField(default=False)

    class Meta:
        unique_together = ('event', 'alumni')


class AlumniDonation(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    purpose = models.CharField(max_length=255, blank=True)
    donated_on = models.DateTimeField(auto_now_add=True)
    receipt_number = models.CharField(max_length=100, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.alumni.student.full_name()} - {self.amount}"


class AlumniMentorship(models.Model):
    mentor = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='mentorships')
    mentee = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='alumni_mentees')
    start_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('ended', 'Ended')], default='active')
    notes = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('mentor', 'mentee')


class AlumniAchievement(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='achievements')
    title = models.CharField(max_length=255)
    description = models.TextField()
    date_achieved = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} - {self.alumni.student.full_name()}"


class AlumniNotification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    recipient = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='notifications')
    sent_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    sent_on = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=30, choices=[
        ('event', 'Event'),
        ('donation', 'Donation'),
        ('announcement', 'Announcement'),
        ('mentorship', 'Mentorship'),
    ])
    is_read = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class AlumniFeedback(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    message = models.TextField()
    submitted_on = models.DateTimeField(auto_now_add=True)
    responded = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


class AlumniMembership(models.Model):
    alumni = models.OneToOneField(AlumniProfile, on_delete=models.CASCADE)
    is_active_member = models.BooleanField(default=False)
    membership_paid_on = models.DateField(null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    membership_number = models.CharField(max_length=100, unique=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.alumni.student.full_name()} - {self.membership_number}"


class AlumniEmployment(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE, related_name='employment_records')
    company_name = models.CharField(max_length=255)
    position = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    currently_employed = models.BooleanField(default=True)
    location = models.CharField(max_length=255, blank=True)
    industry = models.CharField(max_length=255, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.alumni.student.full_name()} at {self.company_name}"


class AlumniVolunteer(models.Model):
    alumni = models.ForeignKey(AlumniProfile, on_delete=models.CASCADE)
    area_of_interest = models.CharField(max_length=255)  # e.g., Mentoring, Speaking, Event Support
    notes = models.TextField(blank=True)
    availability = models.CharField(max_length=100, blank=True)  # e.g., Weekends only
    registered_on = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.alumni.student.full_name()} - {self.area_of_interest}"
