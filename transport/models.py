from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from students.models import Student
from institutions.models import Institution

User = CustomUser

# ----------------------------------
# ROUTE & VEHICLE STRUCTURE
# ----------------------------------
class TransportRoute(models.Model):
    name = models.CharField(max_length=100)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    estimated_duration = models.DurationField(null=True, blank=True)
    morning_time = models.TimeField()
    evening_time = models.TimeField()
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.start_location} → {self.end_location})"


class RouteStopPoint(models.Model):
    route = models.ForeignKey(TransportRoute, on_delete=models.CASCADE, related_name='stop_points')
    name = models.CharField(max_length=100)
    gps_coordinates = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name} ({self.route.name})"


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    capacity = models.PositiveIntegerField()
    assigned_route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} ({self.model})"


class MaintenanceRecord(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    maintenance_type = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    performed_on = models.DateField(default=timezone.now)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    performed_by = models.CharField(max_length=100, blank=True)
    next_due_date = models.DateField(null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vehicle} - {self.maintenance_type} on {self.performed_on}"


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    license_number = models.CharField(max_length=50)
    license_expiry = models.DateField()
    assigned_vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.license_number}"


# ----------------------------------
# STUDENT TRANSPORT MANAGEMENT
# ----------------------------------
class TransportBooking(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True, blank=True)
    pickup_point = models.CharField(max_length=255)
    drop_point = models.CharField(max_length=255)
    travel_date = models.DateField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='pending')
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.student.full_name()} - {self.travel_date} - {self.status}"


class TransportAssignment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True)
    pickup_point = models.CharField(max_length=255)
    drop_point = models.CharField(max_length=255)
    assigned_on = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'route')

    def __str__(self):
        return f"{self.student.full_name()} - {self.route.name}"


class TransportAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('present', 'Present'), ('absent', 'Absent')])
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('student', 'date')


# ----------------------------------
# MONITORING & LOGGING
# ----------------------------------
class VehicleLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    distance_travelled_km = models.DecimalField(max_digits=6, decimal_places=2)
    fuel_used_litres = models.DecimalField(max_digits=6, decimal_places=2)
    issues_reported = models.TextField(blank=True)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.vehicle} Log - {self.date}"


class TripLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('ongoing', 'Ongoing'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='ongoing')
    remarks = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)

    def duration(self):
        if self.end_time:
            return self.end_time - self.start_time
        return None

    def __str__(self):
        return f"{self.vehicle.plate_number} | {self.route.name} | {self.status}"


class GPSLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    speed_kmh = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)


class EmergencyAlert(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    driver = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    triggered_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)


class TransportNotification(models.Model):
    recipient_guardian = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True)
    message = models.TextField()
    type = models.CharField(max_length=30, choices=[
        ('boarding', 'Boarding'),
        ('drop', 'Drop-off'),
        ('delay', 'Delay'),
        ('route_change', 'Route Change'),
        ('payment_due', 'Payment Due'),
    ])
    sent_at = models.DateTimeField(auto_now_add=True)
    is_sent = models.BooleanField(default=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)


# ----------------------------------
# FINANCIAL
# ----------------------------------
class TransportFee(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    route = models.ForeignKey(TransportRoute, on_delete=models.SET_NULL, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    term = models.CharField(max_length=20)
    year = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)


class FeePaymentLog(models.Model):
    fee = models.ForeignKey(TransportFee, on_delete=models.CASCADE, related_name='payments')
    paid_on = models.DateTimeField(default=timezone.now)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)


# ----------------------------------
# AI & FEEDBACK
# ----------------------------------
class AIDriverEfficiencyScore(models.Model):
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=5, decimal_places=2)
    calculated_at = models.DateTimeField(auto_now_add=True)


class ParentTransportFeedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
