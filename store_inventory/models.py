from django.db import models
from django.utils import timezone
from accounts.models import CustomUser
from institutions.models import Institution
from students.models import Student
from finance.models import StudentInvoice


class ItemCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ItemUnit(models.Model):
    name = models.CharField(max_length=50)
    abbreviation = models.CharField(max_length=10)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.abbreviation


class Item(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True)
    unit = models.ForeignKey(ItemUnit, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    min_stock_level = models.PositiveIntegerField(default=5)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def current_stock(self):
        stock_in = self.stock_entries.aggregate(total=models.Sum('quantity'))['total'] or 0
        issued = self.issues.aggregate(total=models.Sum('quantity'))['total'] or 0
        returned = self.returns.aggregate(total=models.Sum('quantity'))['total'] or 0
        damaged = self.damages.aggregate(total=models.Sum('quantity'))['total'] or 0
        return stock_in - issued + returned - damaged


class Supplier(models.Model):
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ItemStockEntry(models.Model):
    item = models.ForeignKey(Item, related_name='stock_entries', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    supplier = models.ForeignKey(Supplier, on_delete=models.SET_NULL, null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    received_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    date_received = models.DateTimeField(default=timezone.now)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity * (self.price_per_unit or 0)
        super().save(*args, **kwargs)


class ItemIssue(models.Model):
    item = models.ForeignKey(Item, related_name='issues', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    issued_to_student = models.ForeignKey(Student, on_delete=models.SET_NULL, null=True, blank=True)
    issued_to_user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='store_issues')
    issued_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='store_issuers')
    department = models.CharField(max_length=100, blank=True)
    purpose = models.TextField(blank=True)
    date_issued = models.DateTimeField(default=timezone.now)
    linked_invoice = models.ForeignKey(StudentInvoice, on_delete=models.SET_NULL, null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class ItemReturn(models.Model):
    item = models.ForeignKey(Item, related_name='returns', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    returned_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    return_reason = models.TextField(blank=True)
    date_returned = models.DateTimeField(default=timezone.now)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class ItemDamage(models.Model):
    item = models.ForeignKey(Item, related_name='damages', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    reported_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    damage_reason = models.TextField(blank=True)
    date_reported = models.DateTimeField(default=timezone.now)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class StoreRequisition(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    requested_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    department = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    approved_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='requisition_approver')
    request_date = models.DateTimeField(default=timezone.now)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class StockAlert(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    alert_triggered = models.BooleanField(default=False)
    triggered_at = models.DateTimeField(null=True, blank=True)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Alert for {self.item.name} (Below Min Stock)"
