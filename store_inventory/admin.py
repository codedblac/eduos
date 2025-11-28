from django.contrib import admin
from .models import (
    ItemCategory, ItemUnit, Item, Supplier,
    ItemStockEntry, ItemIssue, ItemReturn,
    ItemDamage, StoreRequisition, StockAlert
)


class BaseInstitutionAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(institution=request.user.institution)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.institution = request.user.institution
        obj.save()


@admin.register(ItemCategory)
class ItemCategoryAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'institution', 'created_at']
    search_fields = []
    list_filter = ['institution']


@admin.register(ItemUnit)
class ItemUnitAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'abbreviation', 'institution']
    search_fields = [ 'abbreviation']
    list_filter = ['institution']


@admin.register(Item)
class ItemAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'category', 'unit', 'min_stock_level', 'institution']
    search_fields = [ 'description']
    list_filter = ['institution', 'category', 'unit']


@admin.register(Supplier)
class SupplierAdmin(BaseInstitutionAdmin):
    list_display = ['name', 'contact_person', 'phone', 'email', 'institution']
    search_fields = [ 'contact_person']
    list_filter = ['institution']


@admin.register(ItemStockEntry)
class ItemStockEntryAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'quantity', 'supplier', 'date_received', 'institution']
    search_fields = ['item__name', 'supplier__name']
    list_filter = ['institution', 'supplier', 'date_received']
    date_hierarchy = 'date_received'


@admin.register(ItemIssue)
class ItemIssueAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'quantity', 'issued_to_user', 'issued_to_student', 'date_issued', 'institution']
    list_filter = ['institution', 'date_issued', 'issued_to_user']
    search_fields = ['item__name', 'issued_to_user__email']
    date_hierarchy = 'date_issued'


@admin.register(ItemReturn)
class ItemReturnAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'quantity', 'date_returned', 'institution']
    list_filter = ['institution', 'date_returned']
    search_fields = ['item__name']
    date_hierarchy = 'date_returned'


@admin.register(ItemDamage)
class ItemDamageAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'quantity', 'date_reported', 'institution']
    list_filter = ['institution', 'date_reported']
    search_fields = ['item__name']
    date_hierarchy = 'date_reported'


@admin.register(StoreRequisition)
class StoreRequisitionAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'quantity', 'department', 'status', 'request_date', 'institution']
    list_filter = ['institution', 'status', 'department']
    search_fields = ['item__name', 'department']
    date_hierarchy = 'request_date'


@admin.register(StockAlert)
class StockAlertAdmin(BaseInstitutionAdmin):
    list_display = ['item', 'institution', 'alert_triggered', 'created_at']
    list_filter = ['institution', 'alert_triggered']
    date_hierarchy = 'created_at'
    search_fields = ['item__name']
