from rest_framework import serializers
from .models import (
    ItemCategory, ItemUnit, Item, Supplier,
    ItemStockEntry, ItemIssue, ItemReturn,
    ItemDamage, StoreRequisition, StockAlert
)

class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemCategory
        fields = '__all__'


class ItemUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemUnit
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    current_stock = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'

    def get_current_stock(self, obj):
        return obj.current_stock()


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = '__all__'


class ItemStockEntrySerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = ItemStockEntry
        fields = '__all__'


class ItemIssueSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    issued_to = serializers.SerializerMethodField()

    class Meta:
        model = ItemIssue
        fields = '__all__'

    def get_issued_to(self, obj):
        if obj.issued_to_student:
            return obj.issued_to_student.full_name
        elif obj.issued_to_user:
            return obj.issued_to_user.get_full_name()
        return None


class ItemReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemReturn
        fields = '__all__'


class ItemDamageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemDamage
        fields = '__all__'


class StoreRequisitionSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')
    requested_by_name = serializers.ReadOnlyField(source='requested_by.get_full_name')
    approved_by_name = serializers.ReadOnlyField(source='approved_by.get_full_name')

    class Meta:
        model = StoreRequisition
        fields = '__all__'


class StockAlertSerializer(serializers.ModelSerializer):
    item_name = serializers.ReadOnlyField(source='item.name')

    class Meta:
        model = StockAlert
        fields = '__all__'
