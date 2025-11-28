from rest_framework import serializers
from .models import (
    DisciplineCategory,
    DisciplineCase,
    DisciplinaryAction
)
from students.models import Student
from classes.models import ClassLevel, Stream
from accounts.models import CustomUser


class DisciplineCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DisciplineCategory
        fields = ['id', 'institution', 'description']
        read_only_fields = ['id', 'institution']


class DisciplinaryActionSerializer(serializers.ModelSerializer):
    assigned_by = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = DisciplinaryAction
        fields = [
            'id', 'discipline_case', 'action_taken',
            'description', 'assigned_by',
            'date_assigned', 'follow_up_required'
        ]
        read_only_fields = ['id', 'assigned_by']


class DisciplineCaseSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all())
    class_level = serializers.PrimaryKeyRelatedField(queryset=ClassLevel.objects.all(), required=False)
    stream = serializers.PrimaryKeyRelatedField(queryset=Stream.objects.all(), required=False)
    category = serializers.PrimaryKeyRelatedField(queryset=DisciplineCategory.objects.all())
    reported_by = serializers.PrimaryKeyRelatedField(read_only=True)
    witnesses = serializers.PrimaryKeyRelatedField(queryset=CustomUser.objects.all(), many=True, required=False)

    actions = DisciplinaryActionSerializer(many=True, read_only=True)

    class Meta:
        model = DisciplineCase
        fields = [
            'id', 'institution', 'student', 'class_level', 'stream',
            'category', 'description', 'severity', 'incident_date',
            'location', 'reported_by', 'witnesses', 'status', 'created_at',
            'actions'
        ]
        read_only_fields = ['id', 'institution', 'reported_by', 'created_at']

    def create(self, validated_data):
        validated_data['institution'] = self.context['request'].user.institution
        validated_data['reported_by'] = self.context['request'].user
        witnesses = validated_data.pop('witnesses', [])
        case = DisciplineCase.objects.create(**validated_data)
        case.witnesses.set(witnesses)
        return case
