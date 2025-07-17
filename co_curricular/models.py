from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
from students.models import Student

User = settings.AUTH_USER_MODEL


class ActivityCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category_type = models.CharField(max_length=50, choices=[
        ('creative', 'Creative'),
        ('physical', 'Physical'),
        ('technical', 'Technical'),
        ('leadership', 'Leadership'),
        ('spiritual', 'Spiritual')
    ])
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Activity(models.Model):
    category = models.ForeignKey(ActivityCategory, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    coach_or_patron = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    is_competitive = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CoachAssignmentHistory(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    assigned_on = models.DateField(default=timezone.now)
    ended_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)


class StudentProfile(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    interests = models.TextField(blank=True)
    long_term_goals = models.TextField(blank=True)
    preferred_categories = models.ManyToManyField(ActivityCategory, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile of {self.student}"


class StudentActivityParticipation(models.Model):
    PARTICIPATION_STATUS = [
        ('active', 'Active'),
        ('left', 'Left'),
        ('suspended', 'Suspended'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    joined_on = models.DateField(default=timezone.now)
    left_on = models.DateField(null=True, blank=True)
    skill_level = models.CharField(max_length=50, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    status = models.CharField(max_length=20, choices=PARTICIPATION_STATUS, default='active')
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'activity')

    def __str__(self):
        return f"{self.student} - {self.activity}"


class CoachFeedback(models.Model):
    participation = models.ForeignKey(StudentActivityParticipation, on_delete=models.CASCADE)
    coach = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    date = models.DateField(default=timezone.now)
    rating = models.IntegerField(null=True, blank=True)
    feedback = models.TextField()

    def __str__(self):
        return f"Feedback for {self.participation.student} by {self.coach}"


class ActivityPerformance(models.Model):
    participation = models.ForeignKey(StudentActivityParticipation, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    rating = models.CharField(max_length=50, blank=True)
    metrics = models.JSONField(blank=True, null=True)
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"Performance for {self.participation}"


class ActivityEvent(models.Model):
    name = models.CharField(max_length=255)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.activity.name})"


class StudentAward(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    level = models.CharField(max_length=50, choices=[
        ('class', 'Class'),
        ('school', 'School'),
        ('zonal', 'Zonal'),
        ('regional', 'Regional'),
        ('national', 'National'),
        ('international', 'International')
    ])
    date_awarded = models.DateField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='approved')
    evidence = models.FileField(upload_to='co_curricular/awards/', blank=True, null=True)

    def __str__(self):
        return f"{self.title} - {self.student}"


class StudentReflection(models.Model):
    participation = models.ForeignKey(StudentActivityParticipation, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    reflection = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ], default='approved')

    def __str__(self):
        return f"Reflection by {self.author} for {self.participation.student}"


class ActivitySession(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    venue = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.activity.name} on {self.date}"


class ActivityAttendance(models.Model):
    session = models.ForeignKey(ActivitySession, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=[
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('excused', 'Excused')
    ])
    reason = models.TextField(blank=True)

    class Meta:
        unique_together = ('session', 'student')

    def __str__(self):
        return f"{self.student} - {self.session} - {self.status}"


class TalentRecommendation(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    suggested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    area = models.CharField(max_length=100)
    recommended_date = models.DateField(default=timezone.now)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ], default='pending')

    def __str__(self):
        return f"{self.area} recommendation for {self.student}"
