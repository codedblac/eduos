from rest_framework import serializers
from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, FrontAnnouncement, SecurityLog
)
from students.models import Student
from accounts.models import CustomUser


class VisitorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisitorLog
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    meeting_with_name = serializers.CharField(source='meeting_with.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class ParcelDeliverySerializer(serializers.ModelSerializer):
    recipient_student_name = serializers.CharField(source='recipient_student.full_name', read_only=True)
    recipient_staff_name = serializers.CharField(source='recipient_staff.get_full_name', read_only=True)

    class Meta:
        model = ParcelDelivery
        fields = '__all__'


class GatePassSerializer(serializers.ModelSerializer):
    issued_to_student_name = serializers.CharField(source='issued_to_student.full_name', read_only=True)
    issued_to_staff_name = serializers.CharField(source='issued_to_staff.get_full_name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = GatePass
        fields = '__all__'


class FrontDeskTicketSerializer(serializers.ModelSerializer):
    submitted_by_name = serializers.CharField(source='submitted_by.get_full_name', read_only=True)

    class Meta:
        model = FrontDeskTicket
        fields = '__all__'


class FrontAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrontAnnouncement
        fields = '__all__'


class SecurityLogSerializer(serializers.ModelSerializer):
    recorded_by_name = serializers.CharField(source='recorded_by.get_full_name', read_only=True)

    class Meta:
        model = SecurityLog
        fields = '__all__'
