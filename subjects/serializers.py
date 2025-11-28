from rest_framework import serializers
from .models import (
    SubjectCategory, Subject, SubjectClassLevel, SubjectTeacher,
    SubjectPrerequisite, SubjectAssessmentWeight, SubjectGradingScheme,
    SubjectResource, SubjectVersion, SubjectAnalyticsLog
)
from .models import Subject, SubjectAssignment
from rest_framework import serializers
from .models import SubjectAssignment
from classes.serializers import ClassLevelSerializer, StreamSerializer
from institutions.serializers import InstitutionSerializer
from teachers.serializers import TeacherSerializer
from classes.models import ClassLevel
from teachers.models import Teacher
from academics.models import Term
from accounts.models import CustomUser


class SubjectCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectCategory
        fields = '__all__'


class ClassLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'code']


class TeacherSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'full_name']

    def get_full_name(self, obj):
        return obj.user.get_full_name() if obj.user else ""


class SubjectTeacherSerializer(serializers.ModelSerializer):
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(source='teacher', queryset=Teacher.objects.all(), write_only=True)
    subject = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = SubjectTeacher
        fields = ['id', 'teacher', 'teacher_id', 'subject', 'is_head', 'assigned_at']


class SubjectClassLevelSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(source='class_level', queryset=ClassLevel.objects.all(), write_only=True)

    class Meta:
        model = SubjectClassLevel
        fields = ['id', 'subject', 'class_level', 'class_level_id', 'compulsory']


class SubjectSerializer(serializers.ModelSerializer):
    category = SubjectCategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(source='category', queryset=SubjectCategory.objects.all(), write_only=True)
    class_levels = serializers.SerializerMethodField()
    assigned_teachers = serializers.SerializerMethodField()
    curriculum_display = serializers.CharField(source='get_curriculum_type_display', read_only=True)

    class Meta:
        model = Subject
        fields = [
            'id', 'code', 'description', 'is_elective', 'is_core',
            'institution', 'category', 'category_id', 'curriculum_type', 'curriculum_display',
            'is_active', 'archived', 'created_at', 'updated_at',
            'class_levels', 'assigned_teachers']

    def get_class_levels(self, obj):
        return SubjectClassLevelSerializer(obj.class_levels.all(), many=True).data

    def get_assigned_teachers(self, obj):
        return SubjectTeacherSerializer(obj.teacher_links.all(), many=True).data


class SubjectPrerequisiteSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    prerequisite = serializers.StringRelatedField(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=Subject.objects.all(), write_only=True)
    prerequisite_id = serializers.PrimaryKeyRelatedField(source='prerequisite', queryset=Subject.objects.all(), write_only=True)

    class Meta:
        model = SubjectPrerequisite
        fields = ['id', 'subject', 'subject_id', 'prerequisite', 'prerequisite_id', 'is_corequisite']


class SubjectAssessmentWeightSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=Subject.objects.all(), write_only=True)
    term_id = serializers.PrimaryKeyRelatedField(source='term', queryset=Term.objects.all(), write_only=True)

    class Meta:
        model = SubjectAssessmentWeight
        fields = ['id', 'subject', 'subject_id', 'term_id', 'component', 'weight_percentage']


class SubjectGradingSchemeSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=Subject.objects.all(), write_only=True)

    class Meta:
        model = SubjectGradingScheme
        fields = ['id', 'subject', 'subject_id', 'grade', 'min_score', 'max_score', 'remarks']


class SubjectResourceSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=Subject.objects.all(), write_only=True)
    uploaded_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectResource
        fields = [
            'id', 'subject', 'subject_id', 'title', 'type', 'file',
            'url', 'uploaded_by', 'uploaded_by_name', 'uploaded_at'
        ]

    def get_uploaded_by_name(self, obj):
        return obj.uploaded_by.get_full_name() if obj.uploaded_by else None


class SubjectVersionSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=Subject.objects.all(), write_only=True)
    created_by_name = serializers.SerializerMethodField()

    class Meta:
        model = SubjectVersion
        fields = ['id', 'subject', 'subject_id', 'version_number', 'changelog', 'created_by', 'created_by_name', 'created_at']

    def get_created_by_name(self, obj):
        return obj.created_by.get_full_name() if obj.created_by else None


class SubjectAnalyticsLogSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField()

    class Meta:
        model = SubjectAnalyticsLog
        fields = ['id', 'subject', 'average_score', 'highest_score', 'lowest_score', 'recorded_at']

class SubjectAssignmentSerializer(serializers.ModelSerializer):
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(source='institution', queryset=SubjectAssignment._meta.get_field('institution').related_model.objects.all(), write_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(source='subject', queryset=SubjectAssignment._meta.get_field('subject').related_model.objects.all(), write_only=True)
    teacher = TeacherSerializer(read_only=True)
    teacher_id = serializers.PrimaryKeyRelatedField(source='teacher', queryset=SubjectAssignment._meta.get_field('teacher').related_model.objects.all(), write_only=True)
    class_level = ClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(source='class_level', queryset=SubjectAssignment._meta.get_field('class_level').related_model.objects.all(), write_only=True)
    stream = StreamSerializer(read_only=True)
    stream_id = serializers.PrimaryKeyRelatedField(source='stream', queryset=SubjectAssignment._meta.get_field('stream').related_model.objects.all(), write_only=True, required=False, allow_null=True)

    class Meta:
        model = SubjectAssignment
        fields = '__all__'
