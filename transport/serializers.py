from rest_framework import serializers
from .models import (
    TransportRoute, Vehicle, Driver, TransportAssignment,
    TransportAttendance, VehicleLog, TransportNotification
)
from students.serializers import StudentMinimalSerializer
from accounts.serializers import CustomUserMinimalSerializer


class TransportRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRoute
        fields = '__all__'
        read_only_fields = ['institution']


class VehicleSerializer(serializers.ModelSerializer):
    assigned_route = TransportRouteSerializer(read_only=True)
    assigned_route_id = serializers.PrimaryKeyRelatedField(
        queryset=TransportRoute.objects.all(), source='assigned_route', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Vehicle
        fields = ['id', 'plate_number', 'model', 'capacity', 'assigned_route', 'assigned_route_id',
                  'insurance_expiry', 'last_service_date', 'notes', 'institution']
        read_only_fields = ['institution']


class DriverSerializer(serializers.ModelSerializer):
    user = CustomUserMinimalSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=Driver._meta.get_field('user').related_model.objects.all(), write_only=True, source='user')

    assigned_vehicle = VehicleSerializer(read_only=True)
    assigned_vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source='assigned_vehicle', write_only=True, allow_null=True)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'user_id', 'license_number', 'license_expiry', 'assigned_vehicle', 'assigned_vehicle_id', 'institution']
        read_only_fields = ['institution']


class TransportAssignmentSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=TransportAssignment._meta.get_field('student').related_model.objects.all(), source='student', write_only=True)

    route = TransportRouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(queryset=TransportRoute.objects.all(), source='route', write_only=True)

    class Meta:
        model = TransportAssignment
        fields = ['id', 'student', 'student_id', 'route', 'route_id', 'pickup_point', 'drop_point',
                  'assigned_on', 'is_active', 'institution']
        read_only_fields = ['assigned_on', 'institution']


class TransportAttendanceSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=TransportAttendance._meta.get_field('student').related_model.objects.all(), source='student', write_only=True)

    class Meta:
        model = TransportAttendance
        fields = ['id', 'student', 'student_id', 'date', 'status', 'recorded_by', 'institution']
        read_only_fields = ['recorded_by', 'institution']


class VehicleLogSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source='vehicle', write_only=True)

    class Meta:
        model = VehicleLog
        fields = ['id', 'vehicle', 'vehicle_id', 'date', 'distance_travelled_km', 'fuel_used_litres',
                  'issues_reported', 'recorded_by', 'institution']
        read_only_fields = ['recorded_by', 'institution']


class TransportNotificationSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=TransportNotification._meta.get_field('student').related_model.objects.all(), source='student', write_only=True, allow_null=True)

    recipient_guardian = CustomUserMinimalSerializer(read_only=True)
    recipient_guardian_id = serializers.PrimaryKeyRelatedField(queryset=TransportNotification._meta.get_field('recipient_guardian').related_model.objects.all(), source='recipient_guardian', write_only=True, allow_null=True)

    class Meta:
        model = TransportNotification
        fields = ['id', 'recipient_guardian', 'recipient_guardian_id', 'student', 'student_id',
                  'message', 'type', 'sent_at', 'is_sent', 'institution']
        read_only_fields = ['sent_at', 'institution']
