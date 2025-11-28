from rest_framework import serializers
from .models import (
    Student,
    GuardianRelationship,
    StudentDocument,
    StudentExitRecord,
    AcademicSnapshot,
    MedicalFlag,
    StudentHistory
)
from classes.models import ClassLevel, Stream
from teachers.models import Teacher
from guardians.models import GuardianStudentLink


class ClassLevelMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'order']


class StreamMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['id', 'code']


class TeacherMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'user', 'staff_id']


class StudentDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentDocument
        fields = '__all__'
        read_only_fields = ['uploaded_at']


class MedicalFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalFlag
        fields = '__all__'
        read_only_fields = ['created_at']


class StudentHistorySerializer(serializers.ModelSerializer):
    old_class = ClassLevelMiniSerializer(read_only=True)
    new_class = ClassLevelMiniSerializer(read_only=True)
    old_stream = StreamMiniSerializer(read_only=True)
    new_stream = StreamMiniSerializer(read_only=True)
    changed_by_name = serializers.CharField(source="changed_by.get_full_name", read_only=True)

    class Meta:
        model = StudentHistory
        fields = [
            'id', 'student', 'change_type', 'changed_by_name',
            'old_class', 'new_class', 'old_stream', 'new_stream',
            'date_changed', 'notes'
        ]


class StudentExitRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentExitRecord
        fields = '__all__'


class AcademicSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicSnapshot
        fields = '__all__'
        read_only_fields = ['recorded_at']


class GuardianRelationshipSerializer(serializers.ModelSerializer):
    guardian_name = serializers.CharField(source='guardian.user.get_full_name', read_only=True)

    class Meta:
        model = GuardianRelationship
        fields = ['id', 'guardian', 'guardian_name', 'student', 'relationship', 'is_primary']


class StudentSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMiniSerializer(read_only=True)
    stream = StreamMiniSerializer(read_only=True)
    assigned_class_teacher = TeacherMiniSerializer(read_only=True)

    documents = StudentDocumentSerializer(many=True, read_only=True)
    medical_flags = MedicalFlagSerializer(many=True, read_only=True)
    history = StudentHistorySerializer(many=True, read_only=True)
    exit_record = StudentExitRecordSerializer(read_only=True)
    academic_snapshots = AcademicSnapshotSerializer(many=True, read_only=True)
    linked_guardians = GuardianRelationshipSerializer(many=True, read_only=True)

    class Meta:
        model = Student
        fields = [
            'id', 'institution', 'first_name', 'last_name', 'middle_name',
            'admission_number', 'national_id', 'birth_certificate_number',
            'date_of_birth', 'gender', 'photo', 'class_level', 'stream',
            'enrollment_status', 'date_joined', 'date_left',
            'assigned_class_teacher', 'religion', 'disability', 'health_notes',
            'wallet_balance', 'is_boarding', 'parent_access_code',

            # AI-enhanced fields
            'ai_insights', 'performance_comments',
            'recommended_books', 'recommended_teachers',

            # Related data
            'documents', 'medical_flags', 'history',
            'exit_record', 'academic_snapshots', 'linked_guardians',

            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at', 'ai_insights',
            'performance_comments', 'recommended_books', 'recommended_teachers'
        ]


class StudentCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'institution', 'first_name', 'last_name', 'middle_name',
            'admission_number', 'national_id', 'birth_certificate_number',
            'date_of_birth', 'gender', 'photo', 'stream', 'class_level',
            'enrollment_status', 'date_joined', 'date_left',
            'assigned_class_teacher', 'religion', 'disability', 'health_notes',
            'wallet_balance', 'is_boarding', 'parent_access_code']
