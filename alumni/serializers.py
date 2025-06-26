from rest_framework import serializers
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration,
    AlumniDonation, AlumniMentorship, AlumniAchievement,
    AlumniNotification, AlumniFeedback, AlumniMembership,
    AlumniEmployment, AlumniVolunteer
)
from students.serializers import StudentMinimalSerializer
from accounts.serializers import UserMinimalSerializer


class AlumniProfileSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)

    class Meta:
        model = AlumniProfile
        fields = '__all__'


class AlumniEventSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = AlumniEvent
        fields = '__all__'


class AlumniEventRegistrationSerializer(serializers.ModelSerializer):
    event = AlumniEventSerializer(read_only=True)
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniEventRegistration
        fields = '__all__'


class AlumniDonationSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniDonation
        fields = '__all__'


class AlumniMentorshipSerializer(serializers.ModelSerializer):
    mentor = AlumniProfileSerializer(read_only=True)
    mentee = StudentMinimalSerializer(read_only=True)

    class Meta:
        model = AlumniMentorship
        fields = '__all__'


class AlumniAchievementSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniAchievement
        fields = '__all__'


class AlumniNotificationSerializer(serializers.ModelSerializer):
    recipient = AlumniProfileSerializer(read_only=True)
    sent_by = UserMinimalSerializer(read_only=True)

    class Meta:
        model = AlumniNotification
        fields = '__all__'


class AlumniFeedbackSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniFeedback
        fields = '__all__'


class AlumniMembershipSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniMembership
        fields = '__all__'


class AlumniEmploymentSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniEmployment
        fields = '__all__'


class AlumniVolunteerSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)

    class Meta:
        model = AlumniVolunteer
        fields = '__all__'
