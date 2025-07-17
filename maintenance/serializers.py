from rest_framework import serializers
from .models import (
    MaintenanceCategory,
    MaintenanceAsset,
    MaintenanceRequest,
    MaintenanceLog,
    MaintenanceSchedule,
    MaintenanceStaff,
)
from accounts.serializers import UserSerializer


class MaintenanceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceCategory
        fields = '__all__'


class MaintenanceAssetSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = MaintenanceAsset
        fields = '__all__'


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    reported_by_info = UserSerializer(source='reported_by', read_only=True)

    class Meta:
        model = MaintenanceRequest
        fields = '__all__'
        read_only_fields = ['reported_on']


class MaintenanceLogSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)
    performed_by_info = UserSerializer(source='performed_by', read_only=True)

    class Meta:
        model = MaintenanceLog
        fields = '__all__'


class MaintenanceScheduleSerializer(serializers.ModelSerializer):
    asset_name = serializers.CharField(source='asset.name', read_only=True)

    class Meta:
        model = MaintenanceSchedule
        fields = '__all__'


class MaintenanceStaffSerializer(serializers.ModelSerializer):
    user_info = UserSerializer(source='user', read_only=True)

    class Meta:
        model = MaintenanceStaff
        fields = '__all__'
