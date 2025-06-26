from rest_framework import serializers
from .models import (
    Hostel, HostelRoom, RoomAllocation,
    HostelLeaveRequest, HostelInspection,
    HostelViolation, HostelAnnouncement
)


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        fields = '__all__'


class HostelRoomSerializer(serializers.ModelSerializer):
    current_occupancy = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)

    class Meta:
        model = HostelRoom
        fields = '__all__'


class RoomAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomAllocation
        fields = '__all__'


class HostelLeaveRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelLeaveRequest
        fields = '__all__'


class HostelInspectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelInspection
        fields = '__all__'


class HostelViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelViolation
        fields = '__all__'


class HostelAnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = HostelAnnouncement
        fields = '__all__'
