from rest_framework import serializers
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration, AlumniDonation, AlumniMentorship,
    AlumniAchievement, AlumniNotification, AlumniFeedback, AlumniMembership, AlumniEmployment,
    AlumniVolunteer, AlumniTestimonial, AlumniJobOpportunity
)
from students.serializers import StudentSerializer
from accounts.serializers import UserMinimalSerializer


class AlumniProfileSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile._meta.get_field('student').related_model.objects.all(), source='student', write_only=True)

    class Meta:
        model = AlumniProfile
        fields = '__all__'
        read_only_fields = ['institution', 'joined_on']


class AlumniEventSerializer(serializers.ModelSerializer):
    created_by = UserMinimalSerializer(read_only=True)
    created_by_id = serializers.PrimaryKeyRelatedField(queryset=AlumniEvent._meta.get_field('created_by').related_model.objects.all(), source='created_by', write_only=True)

    class Meta:
        model = AlumniEvent
        fields = '__all__'
        read_only_fields = ['institution', 'created_at']


class AlumniEventRegistrationSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)
    event = AlumniEventSerializer(read_only=True)
    event_id = serializers.PrimaryKeyRelatedField(queryset=AlumniEvent.objects.all(), source='event', write_only=True)

    class Meta:
        model = AlumniEventRegistration
        fields = ['id', 'event', 'event_id', 'alumni', 'alumni_id', 'registered_on', 'is_attended']
        read_only_fields = ['registered_on']


class AlumniDonationSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniDonation
        fields = '__all__'
        read_only_fields = ['donated_on', 'institution']


class AlumniMentorshipSerializer(serializers.ModelSerializer):
    mentor = AlumniProfileSerializer(read_only=True)
    mentor_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='mentor', write_only=True)
    mentee = StudentSerializer(read_only=True)
    mentee_id = serializers.PrimaryKeyRelatedField(queryset=AlumniMentorship._meta.get_field('mentee').related_model.objects.all(), source='mentee', write_only=True)

    class Meta:
        model = AlumniMentorship
        fields = '__all__'
        read_only_fields = ['institution']


class AlumniAchievementSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniAchievement
        fields = '__all__'
        read_only_fields = ['institution']


class AlumniNotificationSerializer(serializers.ModelSerializer):
    recipient = AlumniProfileSerializer(read_only=True)
    recipient_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='recipient', write_only=True)
    sent_by = UserMinimalSerializer(read_only=True)
    sent_by_id = serializers.PrimaryKeyRelatedField(queryset=AlumniNotification._meta.get_field('sent_by').related_model.objects.all(), source='sent_by', write_only=True)

    class Meta:
        model = AlumniNotification
        fields = '__all__'
        read_only_fields = ['sent_on', 'institution']


class AlumniFeedbackSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniFeedback
        fields = '__all__'
        read_only_fields = ['submitted_on', 'institution']


class AlumniMembershipSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniMembership
        fields = '__all__'
        read_only_fields = ['institution']


class AlumniEmploymentSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniEmployment
        fields = '__all__'
        read_only_fields = ['institution']


class AlumniVolunteerSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniVolunteer
        fields = '__all__'
        read_only_fields = ['registered_on', 'institution']


class AlumniTestimonialSerializer(serializers.ModelSerializer):
    alumni = AlumniProfileSerializer(read_only=True)
    alumni_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='alumni', write_only=True)

    class Meta:
        model = AlumniTestimonial
        fields = '__all__'
        read_only_fields = ['submitted_on', 'institution']


class AlumniJobOpportunitySerializer(serializers.ModelSerializer):
    posted_by = AlumniProfileSerializer(read_only=True)
    posted_by_id = serializers.PrimaryKeyRelatedField(queryset=AlumniProfile.objects.all(), source='posted_by', write_only=True)

    class Meta:
        model = AlumniJobOpportunity
        fields = '__all__'
        read_only_fields = ['posted_on', 'institution']
