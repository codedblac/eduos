from rest_framework import serializers
from .models import (
    TransportRoute, RouteStopPoint, Vehicle, Driver, TransportAssignment,
    TransportAttendance, VehicleLog, TransportNotification,
    MaintenanceRecord, TripLog, GPSLog, EmergencyAlert,
    TransportFee, FeePaymentLog, AIDriverEfficiencyScore, ParentTransportFeedback
)
from students.serializers import StudentSerializer
from accounts.serializers import UserMinimalSerializer
from .models import TransportBooking
from students.serializers import StudentSerializer
from accounts.serializers import UserMinimalSerializer
# from .serializers import TransportRouteSerializer, VehicleSerializer


class TransportRouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportRoute
        fields = '__all__'
        read_only_fields = ['institution']


class RouteStopPointSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteStopPoint
        fields = '__all__'


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
    user = UserMinimalSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(queryset=Driver._meta.get_field('user').related_model.objects.all(), write_only=True, source='user')

    assigned_vehicle = VehicleSerializer(read_only=True)
    assigned_vehicle_id = serializers.PrimaryKeyRelatedField(queryset=Vehicle.objects.all(), source='assigned_vehicle', write_only=True, allow_null=True)

    class Meta:
        model = Driver
        fields = ['id', 'user', 'user_id', 'license_number', 'license_expiry', 'assigned_vehicle', 'assigned_vehicle_id', 'institution']
        read_only_fields = ['institution']


class TransportAssignmentSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=TransportAssignment._meta.get_field('student').related_model.objects.all(), source='student', write_only=True)

    route = TransportRouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(queryset=TransportRoute.objects.all(), source='route', write_only=True)

    class Meta:
        model = TransportAssignment
        fields = ['id', 'student', 'student_id', 'route', 'route_id', 'pickup_point', 'drop_point',
                  'assigned_on', 'is_active', 'institution']
        read_only_fields = ['assigned_on', 'institution']


class TransportAttendanceSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
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
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=TransportNotification._meta.get_field('student').related_model.objects.all(), source='student', write_only=True, allow_null=True)

    recipient_guardian = UserMinimalSerializer(read_only=True)
    recipient_guardian_id = serializers.PrimaryKeyRelatedField(queryset=TransportNotification._meta.get_field('recipient_guardian').related_model.objects.all(), source='recipient_guardian', write_only=True, allow_null=True)

    class Meta:
        model = TransportNotification
        fields = ['id', 'recipient_guardian', 'recipient_guardian_id', 'student', 'student_id',
                  'message', 'type', 'sent_at', 'is_sent', 'institution']
        read_only_fields = ['sent_at', 'institution']


class MaintenanceRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = MaintenanceRecord
        fields = '__all__'
        read_only_fields = ['institution']


class TripLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLog
        fields = '__all__'
        read_only_fields = ['institution']


class GPSLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GPSLog
        fields = '__all__'
        read_only_fields = ['institution']


class EmergencyAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyAlert
        fields = '__all__'
        read_only_fields = ['sent_at', 'institution']


class TransportFeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransportFee
        fields = '__all__'
        read_only_fields = ['institution']


class FeePaymentLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeePaymentLog
        fields = '__all__'
        read_only_fields = ['timestamp', 'institution']


class AIDriverEfficiencyScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIDriverEfficiencyScore
        fields = '__all__'
        read_only_fields = ['calculated_at']


class ParentTransportFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentTransportFeedback
        fields = '__all__'
        read_only_fields = ['submitted_at']


class TransportBookingSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=TransportBooking._meta.get_field('student').related_model.objects.all(),
        source='student',
        write_only=True
    )

    vehicle = VehicleSerializer(read_only=True)
    vehicle_id = serializers.PrimaryKeyRelatedField(
        queryset=TransportBooking._meta.get_field('vehicle').related_model.objects.all(),
        source='vehicle',
        write_only=True,
        allow_null=True
    )

    route = TransportRouteSerializer(read_only=True)
    route_id = serializers.PrimaryKeyRelatedField(
        queryset=TransportBooking._meta.get_field('route').related_model.objects.all(),
        source='route',
        write_only=True,
        allow_null=True
    )

    booked_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = TransportBooking
        fields = [
            'id', 'student', 'student_id',
            'vehicle', 'vehicle_id',
            'route', 'route_id',
            'pickup_point', 'drop_point',
            'travel_date', 'status',
            'booked_by', 'timestamp',
            'institution'
        ]
        read_only_fields = ['booked_by', 'timestamp', 'institution']

    def create(self, validated_data):
        validated_data['booked_by'] = self.context['request'].user
        return super().create(validated_data)
