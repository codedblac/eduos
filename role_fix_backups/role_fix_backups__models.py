from django.db import models
from django.utils import timezone
from django.conf import settings
from institutions.models import Institution
from store_inventory.models import ItemCategory
# from finance.models import BudgetCode

User = settings.AUTH_USER_MODEL


class Supplier(models.Model):
    """
    Represents a supplier or vendor.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='procurement_suppliers')
    name = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    tax_id = models.CharField(max_length=100, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name


class ProcurementRequest(models.Model):
    """
    Represents a request to procure an item.
    """
    REQUEST_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('quoted', 'Quotations Received'),
        ('ordered', 'PO Generated'),
    ]

    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='procurement_requests')
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='procurement_requests')
    department = models.CharField(max_length=100)
    item_name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(ItemCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='procurement_requests')
    quantity = models.PositiveIntegerField()
    # budget_code = models.ForeignKey(BudgetCode, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=REQUEST_STATUS, default='pending')
    required_by = models.DateField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.item_name} ({self.quantity})"


class Tender(models.Model):
    """
    Represents a tender for a procurement request.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='procurement_tenders')
    title = models.CharField(max_length=255)
    description = models.TextField()
    request = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='tenders')
    published_date = models.DateTimeField(default=timezone.now)
    closing_date = models.DateTimeField()
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Quotation(models.Model):
    """
    Represents a quotation provided by a supplier for a request.
    """
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='quotations')
    request = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='quotations')
    tender = models.ForeignKey(Tender, on_delete=models.SET_NULL, null=True, blank=True, related_name='quotations')
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2)
    delivery_time_days = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    attachment = models.FileField(upload_to='quotations/', blank=True, null=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    is_selected = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.supplier.name} - {self.request.item_name}"


class PurchaseOrder(models.Model):
    """
    Represents a purchase order issued to a supplier.
    """
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name='purchase_orders')
    po_number = models.CharField(max_length=100, unique=True)
    request = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='purchase_orders')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='purchase_orders')
    quotation = models.ForeignKey(Quotation, on_delete=models.CASCADE, related_name='purchase_orders')
    total_price = models.DecimalField(max_digits=14, decimal_places=2)
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='issued_purchase_orders')
    issue_date = models.DateField(default=timezone.now)
    expected_delivery_date = models.DateField()

    def __str__(self):
        return f"PO#{self.po_number}"


class GoodsReceivedNote(models.Model):
    """
    Confirms goods received against a purchase order.
    """
    po = models.OneToOneField(PurchaseOrder, on_delete=models.CASCADE, related_name='grn')
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_goods')
    received_date = models.DateField(default=timezone.now)
    quantity_received = models.PositiveIntegerField()
    notes = models.TextField(blank=True)
    file_upload = models.FileField(upload_to='grn_docs/', blank=True, null=True)

    def __str__(self):
        return f"GRN for {self.po}"


class SupplierInvoice(models.Model):
    """
    Represents an invoice submitted by a supplier.
    """
    po = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE, related_name='invoices')
    invoice_number = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    invoice_date = models.DateField()
    due_date = models.DateField()
    document = models.FileField(upload_to='invoices/')
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Invoice {self.invoice_number}"


class Payment(models.Model):
    """
    Payment record for a supplier invoice.
    """
    invoice = models.ForeignKey(SupplierInvoice, on_delete=models.CASCADE, related_name='payments')
    paid_on = models.DateField()
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    method = models.CharField(max_length=100, choices=[
        ('bank_transfer', 'Bank Transfer'),
        ('cheque', 'Cheque'),
        ('mpesa', 'M-Pesa'),
        ('cash', 'Cash'),
    ])
    reference = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Payment for {self.invoice.invoice_number}"


class ProcurementApproval(models.Model):
    """
    Tracks approval of procurement requests.
    """
    request = models.ForeignKey(ProcurementRequest, on_delete=models.CASCADE, related_name='approvals')
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='procurement_approvals')
    role = models.CharField(max_length=100)
    approved_on = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ])
    comments = models.TextField(blank=True)

    def __str__(self):
        return f"{self.role} - {self.status}"


class ProcurementLog(models.Model):
    """
    Audit trail of actions on procurement requests.
    """
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='procurement_logs')
    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(default=timezone.now)
    related_request = models.ForeignKey(ProcurementRequest, on_delete=models.SET_NULL, null=True, blank=True, related_name='logs')
    details = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action} by {self.actor}"
