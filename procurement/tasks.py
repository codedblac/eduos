from datetime import timedelta
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from procurement.models import (
    Tender, ProcurementRequest, PurchaseOrder, GoodsReceivedNote, SupplierInvoice, ProcurementLog
)
from accounts.models import CustomUser
from notifications.utils import send_notification  # assuming you have a central notifier

User = settings.AUTH_USER_MODEL


# ----------------------------
# 1. Auto-close expired tenders
# ----------------------------
def auto_close_expired_tenders():
    now = timezone.now()
    expired = Tender.objects.filter(closing_date__lt=now, is_closed=False)
    for tender in expired:
        tender.is_closed = True
        tender.save()
        send_notification(
            user_ids=None,  # you can target specific roles later
            title="Tender Closed",
            message=f"Tender '{tender.title}' has automatically closed.",
            target_roles=['procurement_officer'],
            institution_id=tender.institution_id,
            category="tender"
        )
        ProcurementLog.objects.create(
            actor=None,
            action="Tender Auto-Closed",
            timestamp=timezone.now(),
            related_request=tender.request,
            details=f"Closed on expiry: {tender.closing_date}"
        )


# ----------------------------
# 2. Alert procurement officers of late deliveries
# ----------------------------
def alert_late_po_deliveries():
    today = timezone.now().date()
    late_pos = PurchaseOrder.objects.filter(
        expected_delivery_date__lt=today
    ).exclude(grn__isnull=False)
    for po in late_pos:
        send_notification(
            user_ids=None,
            title="Delivery Delay Alert",
            message=f"PO #{po.po_number} from {po.supplier.name} is overdue for delivery.",
            target_roles=['procurement_officer', 'store_clerk'],
            institution_id=po.institution_id,
            category="delivery"
        )
        ProcurementLog.objects.create(
            actor=None,
            action="Late Delivery Alert",
            timestamp=timezone.now(),
            related_request=po.request,
            details=f"PO #{po.po_number} overdue since {po.expected_delivery_date}"
        )


# ----------------------------
# 3. Notify about pending approvals
# ----------------------------
def notify_pending_approvals():
    pending_requests = ProcurementRequest.objects.filter(status='pending')
    for request in pending_requests:
        send_notification(
            user_ids=None,
            title="Procurement Approval Pending",
            message=f"Approval needed for request: {request.item_name} ({request.quantity})",
            target_roles=['department_head', 'finance_manager'],
            institution_id=request.institution_id,
            category="approval"
        )


# ----------------------------
# 4. Detect duplicate invoices
# ----------------------------
def detect_duplicate_invoices():
    seen = set()
    duplicates = []
    for inv in SupplierInvoice.objects.all():
        key = (inv.invoice_number, inv.po.supplier_id)
        if key in seen:
            duplicates.append(inv)
        else:
            seen.add(key)
    for dup in duplicates:
        send_notification(
            user_ids=None,
            title="Duplicate Invoice Detected",
            message=f"Invoice #{dup.invoice_number} may be a duplicate.",
            target_roles=['finance_manager'],
            institution_id=dup.po.institution_id,
            category="invoice"
        )
        ProcurementLog.objects.create(
            actor=None,
            action="Duplicate Invoice Flagged",
            timestamp=timezone.now(),
            related_request=dup.po.request,
            details=f"Invoice #{dup.invoice_number} submitted twice."
        )


# ----------------------------
# Optional: Chain all tasks
# ----------------------------
def run_all_procurement_tasks():
    auto_close_expired_tenders()
    alert_late_po_deliveries()
    notify_pending_approvals()
    detect_duplicate_invoices()
