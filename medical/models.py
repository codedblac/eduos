from django.db import models

# Create your models here.
from django.db import models
from django.conf import settings
from students.models import Student
from institutions.models import Institution
import uuid


# ----------------------------
# Medicine Stock Inventory
# ----------------------------

class MedicineInventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=20, default="tablets")  # e.g., ml, tablets
    expiry_date = models.DateField()
    restock_level = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        unique_together = ('institution', 'name')

    def __str__(self):
        return f"{self.name} ({self.quantity} {self.unit})"


# ----------------------------
# Medical Visits (Sick Bay Log)
# ----------------------------

class MedicalVisit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='medical_visits')
    attended_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='handled_visits')  # Doctor/Nurse
    date_visited = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField()
    diagnosis = models.CharField(max_length=255)
    treatment = models.TextField()
    is_emergency = models.BooleanField(default=False)
    referred = models.BooleanField(default=False)
    referral_notes = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-date_visited']

    def __str__(self):
        return f"{self.student} visited on {self.date_visited.strftime('%Y-%m-%d')}"


class SickBayVisit(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    visit_date = models.DateTimeField(auto_now_add=True)
    symptoms = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment_given = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.visit_date.date()}"

# ----------------------------
# Medicine Dispensed
# ----------------------------

class DispensedMedicine(models.Model):
    visit = models.ForeignKey(MedicalVisit, on_delete=models.CASCADE, related_name='medicines_dispensed')
    medicine = models.ForeignKey(MedicineInventory, on_delete=models.CASCADE)
    quantity_dispensed = models.PositiveIntegerField()
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.quantity_dispensed} of {self.medicine.name} to {self.visit.student}"



class MedicalFlag(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    flag_type = models.CharField(max_length=100)  # e.g., "Allergy", "Chronic Illness"
    description = models.TextField()
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.flag_type}"
# ----------------------------
# AI-Generated Health Alerts
# ----------------------------

class HealthAlert(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='health_alerts')
    triggered_by_ai = models.BooleanField(default=True)
    alert_type = models.CharField(max_length=100)  # e.g., "Chronic Condition", "Frequent Visits", "Class Trend"
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    def __str__(self):
        return f"Alert: {self.alert_type} for {self.student}"


# ----------------------------
# Class/Stream-level AI Insights
# ----------------------------

class ClassHealthTrend(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='class_health_trends')
    class_level = models.CharField(max_length=50)  # e.g., Grade 7
    stream_name = models.CharField(max_length=50)  # e.g., 7 Blue
    most_common_illness = models.CharField(max_length=100)
    trend_notes = models.TextField()
    generated_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_on']

    def __str__(self):
        return f"Trend in {self.class_level} - {self.stream_name}"
