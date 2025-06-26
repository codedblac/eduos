from rest_framework import serializers
from .models import (
    Staff, StaffProfile, EmploymentHistory,
    StaffQualification, StaffLeave, StaffDisciplinaryAction, StaffAttendance
)
from accounts.serializers import UserSerializer


class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['id', 'date_joined']


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StaffProfile
        fields = '__all__'
        read_only_fields = ['id', 'created_at']


class EmploymentHistorySerializer(serializers.ModelSerializer):
    staff = StaffSerializer(read_only=True)

    class Meta:
        model = EmploymentHistory
        fields = '__all__'
        read_only_fields = ['id']


class StaffQualificationSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StaffQualification
        fields = '__all__'
        read_only_fields = ['id']


class StaffLeaveSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = StaffLeave
        fields = '__all__'
        read_only_fields = ['id']


class StaffDisciplinaryActionSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(read_only=True)
    resolved_by = UserSerializer(read_only=True)

    class Meta:
        model = StaffDisciplinaryAction
        fields = '__all__'
        read_only_fields = ['id']


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = StaffAttendance
        fields = '__all__'
        read_only_fields = ['id']
