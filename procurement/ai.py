from datetime import datetime, timedelta
from django.db import models

from django.db.models import Avg, Count, Q, Sum
from .models import (
    Supplier, ProcurementRequest, Quotation, PurchaseOrder,
    GoodsReceivedNote, SupplierInvoice, Payment
)
from decimal import Decimal
import random


class ProcurementAIEngine:
    """
    AI tools for procurement analysis, prediction, and decision support.
    """

    def __init__(self, institution_id=None):
        self.institution_id = institution_id

    # ------------------------------------
    # 1. Predict Price for a Requested Item
    # ------------------------------------
    def predict_price(self, item_name):
        queryset = Quotation.objects.filter(
            request__item_name__icontains=item_name
        )
        if self.institution_id:
            queryset = queryset.filter(request__institution_id=self.institution_id)

        average = queryset.aggregate(avg=Avg('price_per_unit'))['avg']
        if average is None:
            return round(Decimal(random.uniform(1000, 5000)), 2)  # fallback
        return round(average, 2)

    # ------------------------------------
    # 2. Recommend Top Suppliers for an Item
    # ------------------------------------
    def recommend_suppliers(self, item_name, top_n=3):
        qs = Quotation.objects.filter(request__item_name__icontains=item_name)
        if self.institution_id:
            qs = qs.filter(request__institution_id=self.institution_id)

        results = {}

        for q in qs:
            supplier_id = q.supplier.id
            if supplier_id not in results:
                results[supplier_id] = {
                    "supplier": q.supplier,
                    "total_quotes": 0,
                    "avg_price": 0,
                    "delivery_speed": [],
                    "score": 0
                }

            result = results[supplier_id]
            result["total_quotes"] += 1
            result["avg_price"] += q.price_per_unit
            if q.request.status == 'ordered' and hasattr(q.request, 'purchaseorder'):
                po = q.request.purchaseorder
                if hasattr(po, 'grn'):
                    delivery_time = (po.grn.received_date - po.issue_date).days
                    result["delivery_speed"].append(delivery_time)

        scored_suppliers = []
        for r in results.values():
            avg_price = r["avg_price"] / r["total_quotes"]
            avg_delivery = sum(r["delivery_speed"]) / len(r["delivery_speed"]) if r["delivery_speed"] else 10
            r["score"] = round(1000 / (avg_price * avg_delivery + 1), 2)
            scored_suppliers.append(r)

        scored_suppliers.sort(key=lambda x: x["score"], reverse=True)
        return scored_suppliers[:top_n]

    # ------------------------------------
    # 3. Flag Duplicate Invoices or Overpayments
    # ------------------------------------
    def detect_anomalies(self):
        alerts = []

        # Duplicate invoices
        seen = set()
        for inv in SupplierInvoice.objects.all():
            key = (inv.invoice_number, inv.po.supplier_id)
            if key in seen:
                alerts.append(f"Duplicate invoice: {inv.invoice_number} for supplier {inv.po.supplier.name}")
            else:
                seen.add(key)

        # Overpaid invoices
        for inv in SupplierInvoice.objects.all():
            total_paid = sum(p.amount for p in inv.payment_set.all())
            if total_paid > inv.amount:
                alerts.append(f"Overpayment detected: Invoice {inv.invoice_number} paid {total_paid}, expected {inv.amount}")

        return alerts

    # ------------------------------------
    # 4. Procurement Summary Insights
    # ------------------------------------
    def get_summary(self):
        data = {}
        qs = ProcurementRequest.objects.all()
        if self.institution_id:
            qs = qs.filter(institution_id=self.institution_id)

        data['total_requests'] = qs.count()
        data['approved_requests'] = qs.filter(status='approved').count()
        data['ordered_requests'] = qs.filter(status='ordered').count()
        data['open_tenders'] = qs.filter(tenders__is_closed=False).distinct().count()
        data['pending_quotations'] = qs.filter(quotations__isnull=True).distinct().count()

        return data

    # ------------------------------------
    # 5. Predict Risk of Late Delivery for PO
    # ------------------------------------
    def predict_late_delivery_risk(self, po_id):
        try:
            po = PurchaseOrder.objects.get(id=po_id)
        except PurchaseOrder.DoesNotExist:
            return 0.0

        supplier_history = PurchaseOrder.objects.filter(
            supplier=po.supplier,
            grn__isnull=False
        )

        if supplier_history.exists():
            late_deliveries = supplier_history.filter(
                grn__received_date__gt=models.F('expected_delivery_date')
            ).count()
            total = supplier_history.count()
            return round((late_deliveries / total) * 100, 2)
        return 0.0
