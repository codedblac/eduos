from django.utils import timezone
from django.db.models import Count, Sum, Avg, F
from datetime import timedelta
from procurement.models import (
    Supplier, PurchaseOrder, ProcurementRequest, SupplierInvoice,
    GoodsReceivedNote, Payment, ProcurementApproval
)
from django.db.models.functions import TruncMonth


class ProcurementAnalyticsEngine:
    def __init__(self, institution_id=None):
        self.institution_id = institution_id

    def _filter_by_institution(self, queryset):
        if self.institution_id:
            return queryset.filter(institution_id=self.institution_id)
        return queryset

    # -------------------------------------
    # 1. Total Spend per Supplier
    # -------------------------------------
    def spending_by_supplier(self, top_n=5):
        qs = self._filter_by_institution(PurchaseOrder.objects.all())
        data = qs.values('supplier__name').annotate(
            total_spent=Sum('total_price')
        ).order_by('-total_spent')[:top_n]
        return list(data)

    # -------------------------------------
    # 2. Invoice Payment Status
    # -------------------------------------
    def invoice_status_summary(self):
        qs = self._filter_by_institution(SupplierInvoice.objects.all())
        paid = qs.filter(is_paid=True).count()
        unpaid = qs.filter(is_paid=False).count()
        overdue = qs.filter(is_paid=False, due_date__lt=timezone.now().date()).count()
        return {
            'paid': paid,
            'unpaid': unpaid,
            'overdue': overdue
        }

    # -------------------------------------
    # 3. Fulfillment Rate
    # -------------------------------------
    def fulfillment_rate(self):
        qs = self._filter_by_institution(PurchaseOrder.objects.all())
        total = qs.count()
        fulfilled = qs.filter(grn__isnull=False).count()
        if total == 0:
            return 0
        return round((fulfilled / total) * 100, 2)

    # -------------------------------------
    # 4. Average Approval Time
    # -------------------------------------
    def average_approval_time(self):
        qs = self._filter_by_institution(ProcurementRequest.objects.filter(status='approved'))
        total_days = 0
        count = 0
        for req in qs:
            first_approval = req.approvals.order_by('approved_on').first()
            if first_approval:
                days = (first_approval.approved_on.date() - req.created_at.date()).days
                total_days += days
                count += 1
        return round(total_days / count, 2) if count else 0

    # -------------------------------------
    # 5. Monthly Request Trends
    # -------------------------------------
    def monthly_request_volume(self, months_back=6):
        start_date = timezone.now() - timedelta(days=30 * months_back)
        qs = self._filter_by_institution(ProcurementRequest.objects.filter(created_at__gte=start_date))
        qs = qs.annotate(month=TruncMonth('created_at')).values('month').annotate(
            total=Count('id')
        ).order_by('month')
        return list(qs)

    # -------------------------------------
    # 6. Top Departments by Request Volume
    # -------------------------------------
    def top_departments(self, top_n=5):
        qs = self._filter_by_institution(ProcurementRequest.objects.all())
        return list(
            qs.values('department').annotate(total=Count('id')).order_by('-total')[:top_n]
        )

    # -------------------------------------
    # 7. Average Delivery Time
    # -------------------------------------
    def average_delivery_time(self):
        qs = self._filter_by_institution(PurchaseOrder.objects.filter(grn__isnull=False))
        total_days = 0
        count = 0
        for po in qs:
            if po.grn:
                days = (po.grn.received_date - po.issue_date).days
                total_days += days
                count += 1
        return round(total_days / count, 2) if count else 0
