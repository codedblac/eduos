from rest_framework import serializers
from .models import Student, ParentStudentRelationship, MedicalFlag, StudentHistory
from accounts.serializers import UserMiniSerializer
from classes.serializers import StreamMiniSerializer, ClassLevelMiniSerializer
from .ai_engine import StudentAIAnalyzer


class StudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'id', 'institution', 'first_name', 'last_name', 'middle_name', 'admission_number',
            'national_id', 'birth_certificate_number', 'date_of_birth', 'gender',
            'photo', 'stream', 'class_level', 'assigned_class_teacher', 'enrollment_status'
        ]


class StudentListSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMiniSerializer()
    stream = StreamMiniSerializer()
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'admission_number', 'full_name', 'gender', 'date_of_birth',
            'class_level', 'stream', 'enrollment_status', 'photo'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()


class StudentAIReportSerializer(serializers.Serializer):
    insights = serializers.ListField(child=serializers.CharField())
    suggestions = serializers.ListField(child=serializers.CharField())
    feedback_comment = serializers.CharField()


class StudentDetailSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMiniSerializer()
    stream = StreamMiniSerializer()
    assigned_class_teacher = UserMiniSerializer()
    full_name = serializers.SerializerMethodField()

    # Add AI fields
    ai_report = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'id', 'institution', 'admission_number', 'first_name', 'middle_name', 'last_name',
            'full_name', 'national_id', 'birth_certificate_number', 'gender', 'date_of_birth',
            'photo', 'class_level', 'stream', 'assigned_class_teacher', 'enrollment_status',
            'date_joined', 'date_left', 'ai_report'
        ]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.middle_name or ''} {obj.last_name}".strip()

    def get_ai_report(self, obj):
        analyzer = StudentAIAnalyzer(obj)
        report = analyzer.run_full_analysis()
        serializer = StudentAIReportSerializer(report)
        return serializer.data


class ParentStudentRelationshipSerializer(serializers.ModelSerializer):
    parent = UserMiniSerializer()
    student = StudentListSerializer()

    class Meta:
        model = ParentStudentRelationship
        fields = ['id', 'parent', 'student', 'relationship']


class ParentStudentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParentStudentRelationship
        fields = ['id', 'parent', 'student', 'relationship']


class MedicalFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalFlag
        fields = ['id', 'student', 'condition', 'notes', 'critical', 'created_at']


class StudentHistorySerializer(serializers.ModelSerializer):
    changed_by = UserMiniSerializer()
    old_class = ClassLevelMiniSerializer()
    new_class = ClassLevelMiniSerializer()
    old_stream = StreamMiniSerializer()
    new_stream = StreamMiniSerializer()

    class Meta:
        model = StudentHistory
        fields = [
            'id', 'student', 'change_type', 'changed_by',
            'old_class', 'new_class', 'old_stream', 'new_stream',
            'notes', 'date_changed'
        ]
