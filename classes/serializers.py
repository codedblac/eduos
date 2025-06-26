# classes/serializers.py
from rest_framework import serializers
from .models import ClassLevel, Stream

class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = [
            'id', 'institution', 'name', 'code', 'order', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')

class StreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = [
            'id', 'class_level', 'name', 'code', 'order', 'description', 'timetable',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')
