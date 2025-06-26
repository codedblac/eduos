from rest_framework import serializers
from .models import Guardian, GuardianStudentLink, GuardianNotification
from students.models import Student

class GuardianSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guardian
        fields = '__all__'
        read_only_fields = ['institution', 'user']


class GuardianStudentLinkSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.full_name')

    class Meta:
        model = GuardianStudentLink
        fields = '__all__'
        read_only_fields = ['guardian']


class GuardianNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GuardianNotification
        fields = '__all__'
        read_only_fields = ['guardian', 'institution', 'timestamp']
