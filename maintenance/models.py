from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from institutions.models import Institution


class MaintenanceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Equipment(models.Model):
    name = models.CharField(max_length=255)
    serial_number = models.CharField(max_length=100, unique=True, blank=True)
    category = models.CharField(max_length=100, blank=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('active', 'Active'),
        ('under_maintenance', 'Under Maintenance'),
        ('decommissioned', 'Decommissioned'),
    ], default='active')
    location = models.CharField(max_length=255, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.serial_number or 'N/A'}"


class MaintenanceSchedule(models.Model):
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    schedule_type = models.CharField(max_length=50, choices=[
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('annually', 'Annually'),
    ])
    next_due_date = models.DateField()
    last_maintenance_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.equipment.name} - {self.schedule_type} due on {self.next_due_date}"

class MaintenanceAsset(models.Model):
    name = models.CharField(max_length=100)
    asset_tag = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255)
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.SET_NULL, null=True)
    purchase_date = models.DateField(null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.asset_tag}"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.ForeignKey(MaintenanceCategory, on_delete=models.SET_NULL, null=True)
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.SET_NULL, null=True, blank=True)
    location = models.CharField(max_length=255)
    requested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='maintenance_requests')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High')], default='medium')
    assigned_to = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_maintenance')
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class MaintenanceLog(models.Model):
    maintenance_request = models.ForeignKey(MaintenanceRequest, on_delete=models.CASCADE, related_name='logs')
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    notes = models.TextField()
    work_done_on = models.DateTimeField(default=timezone.now)
    cost_incurred = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"Log for {self.maintenance_request.title} - {self.work_done_on.strftime('%Y-%m-%d')}"

class MaintenanceStaff(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=[
        ('technician', 'Technician'),
        ('supervisor', 'Supervisor'),
        ('external_contractor', 'External Contractor'),
    ])
    phone = models.CharField(max_length=20, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.role}"


class PreventiveMaintenance(models.Model):
    asset = models.ForeignKey(MaintenanceAsset, on_delete=models.CASCADE)
    description = models.TextField()
    schedule_date = models.DateField()
    completed = models.BooleanField(default=False)
    completed_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.asset.name} - Scheduled on {self.schedule_date}"
