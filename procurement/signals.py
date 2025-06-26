from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import (
    ProcurementRequest, Quotation, PurchaseOrder,
    GoodsReceivedNote, SupplierInvoice, Payment, ProcurementApproval
)
from procurement.models import ProcurementLog
from notifications.utils import send_notification


# ----------------------------
# Notify procurement after approval
# ----------------------------
@receiver(post_save, sender=ProcurementApproval)
def notify_procurement_after_approval(sender, instance, created, **kwargs):
    if created and instance.status == 'approved':
        request = instance.request
        approvals = request.approvals.all()
        if approvals.filter(status='rejected').exists():
            return  # Stop if rejected at any level

        # Notify if all required roles have approved
        required_roles = ['department_head', 'finance_manager']
        approved_roles = approvals.values_list('role', flat=True)
        if all(role in approved_roles for role in required_roles):
            request.status = 'approved'
            request.save()
            send_notification(
                user_ids=None,
                title="Procurement Request Approved",
                message=f"The request for {request.item_name} has been approved.",
                target_roles=['procurement_officer'],
                institution_id=request.institution_id,
                category='approval'
            )
            ProcurementLog.objects.create(
                actor=instance.approved_by,
                action="Request Fully Approved",
                timestamp=timezone.now(),
                related_request=request,
                details=f"Approved by all required roles."
            )


# ----------------------------
# Notify when PO is created
# ----------------------------
@receiver(post_save, sender=PurchaseOrder)
def notify_on_po_created(sender, instance, created, **kwargs):
    if created:
        send_notification(
            user_ids=None,
            title="New Purchase Order Issued",
            message=f"PO #{instance.po_number} has been issued to {instance.supplier.name}.",
            target_roles=['store_clerk', 'procurement_officer'],
            institution_id=instance.institution_id,
            category="po"
        )


# ----------------------------
# Notify finance when invoice saved
# ----------------------------
@receiver(post_save, sender=SupplierInvoice)
def notify_finance_on_invoice(sender, instance, created, **kwargs):
    if created:
        send_notification(
            user_ids=None,
            title="Supplier Invoice Received",
            message=f"Invoice #{instance.invoice_number} has been received for PO #{instance.po.po_number}.",
            target_roles=['finance_manager'],
            institution_id=instance.po.institution_id,
            category="invoice"
        )


# ----------------------------
# Mark invoice as paid if fully settled
# ----------------------------
@receiver(post_save, sender=Payment)
def auto_mark_invoice_paid(sender, instance, created, **kwargs):
    if created:
        invoice = instance.invoice
        total_paid = sum(p.amount for p in invoice.payment_set.all())
        if total_paid >= invoice.amount:
            invoice.is_paid = True
            invoice.save()
            send_notification(
                user_ids=None,
                title="Invoice Paid",
                message=f"Invoice #{invoice.invoice_number} is now fully paid.",
                target_roles=['finance_manager', 'procurement_officer'],
                institution_id=invoice.po.institution_id,
                category="payment"
            )


# ----------------------------
# Mark PO as fulfilled when GRN saved
# ----------------------------
@receiver(post_save, sender=GoodsReceivedNote)
def flag_po_on_grn(sender, instance, created, **kwargs):
    if created:
        po = instance.po
        ProcurementLog.objects.create(
            actor=instance.received_by,
            action="Goods Received",
            timestamp=timezone.now(),
            related_request=po.request,
            details=f"Quantity received: {instance.quantity_received}"
        )
        send_notification(
            user_ids=None,
            title="Goods Received",
            message=f"Goods for PO #{po.po_number} received by store clerk.",
            target_roles=['procurement_officer'],
            institution_id=po.institution_id,
            category="delivery"
        )
