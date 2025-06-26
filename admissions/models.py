from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from django.conf import settings
from institutions.models import Institution
from academics.models import AcademicYear
from classes.models import ClassLevel

User = settings.AUTH_USER_MODEL

class AdmissionSession(models.Model):
    name = models.CharField(max_length=255)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    intake_date = models.DateField()
    application_deadline = models.DateField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    level = models.ForeignKey(ClassLevel, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Applicant(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    ORPHAN_STATUS = [
        ('none', 'Not Orphaned'),
        ('partial', 'Partial Orphan'),
        ('full', 'Full Orphan'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    other_names = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    nationality = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, blank=True)
    previous_school = models.CharField(max_length=255, blank=True)
    previous_class = models.CharField(max_length=100, blank=True)
    entry_class_level = models.ForeignKey(ClassLevel, on_delete=models.SET_NULL, null=True)
    admission_session = models.ForeignKey(AdmissionSession, on_delete=models.CASCADE)
    parent_name = models.CharField(max_length=255)
    parent_phone = models.CharField(max_length=20)
    parent_email = models.EmailField(blank=True, null=True)
    guardian_name = models.CharField(max_length=255, blank=True)
    guardian_phone = models.CharField(max_length=20, blank=True)
    guardian_email = models.EmailField(blank=True, null=True)
    orphan_status = models.CharField(max_length=10, choices=ORPHAN_STATUS, default='none')
    orphan_proof = models.FileField(upload_to='admissions/orphan_proofs/', blank=True, null=True)
    has_disability = models.BooleanField(default=False)
    disability_details = models.TextField(blank=True)
    has_chronic_illness = models.BooleanField(default=False)
    illness_details = models.TextField(blank=True)
    doctor_report = models.FileField(upload_to='admissions/doctor_reports/', blank=True, null=True)
    career_dream = models.CharField(max_length=255, blank=True)
    talents = models.TextField(blank=True)
    allergies = models.TextField(blank=True)
    passport_photo = models.ImageField(upload_to='admissions/photos/', blank=True, null=True)
    application_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('shortlisted', 'Shortlisted'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('enrolled', 'Enrolled')
    ], default='pending')
    submitted_on = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.admission_session.name})"


class AdmissionDocument(models.Model):
    DOCUMENT_TYPES = [
        ('birth_cert', 'Birth Certificate'),
        ('kcpe_result', 'KCPE Result Slip'),
        ('id_card', 'ID Card'),
        ('doctor_report', 'Doctor Report'),
        ('orphan_cert', 'Orphan Certificate'),
        ('other', 'Other'),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50, choices=DOCUMENT_TYPES)
    file = models.FileField(upload_to='admissions/documents/')
    uploaded_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_type} for {self.applicant}"


class EntranceExam(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    exam_date = models.DateField()
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    remarks = models.TextField(blank=True)
    passed = models.BooleanField(default=False)

    def __str__(self):
        return f"Exam for {self.applicant} on {self.exam_date}"


class AdmissionOffer(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
        ('expired', 'Expired'),
    ]

    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE)
    offer_letter = models.FileField(upload_to='admissions/offers/')
    issued_on = models.DateField()
    expiry_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Offer to {self.applicant} - {self.status}"


class AdmissionComment(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment on {self.applicant} by {self.author}"
