from rest_framework import serializers
from .models import Subject, SubjectClassLevel, SubjectTeacher


class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class SubjectClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectClassLevel
        fields = '__all__'


class SubjectTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectTeacher
        fields = '__all__'
