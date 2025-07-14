from rest_framework import serializers
from .models import ClassLevel, Stream
from institutions.serializers import InstitutionMinimalSerializer
from academics.serializers import AcademicYearMinimalSerializer
from teachers.serializers import TeacherMinimalSerializer


# ===============================
# 🎯 Class Level Serializers
# ===============================

class ClassLevelMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ['id', 'name', 'code']


class ClassLevelSerializer(serializers.ModelSerializer):
    institution = InstitutionMinimalSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel._meta.get_field('institution').related_model.objects.all(),
        source='institution',
        write_only=True
    )
    default_promotion_class = ClassLevelMinimalSerializer(read_only=True)
    default_promotion_class_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source='default_promotion_class',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = ClassLevel
        fields = [
            'id', 'institution', 'institution_id',
            'name', 'code', 'order', 'description',
            'is_graduating_level', 'requires_national_exam',
            'default_promotion_class', 'default_promotion_class_id',
            'created_at', 'updated_at'
        ]
        read_only_fields = ('created_at', 'updated_at')


# ===============================
# 🚀 Stream Serializers
# ===============================

class StreamMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ['id', 'name', 'code']


class StreamSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMinimalSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source='class_level',
        write_only=True
    )
    academic_year = AcademicYearMinimalSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=Stream._meta.get_field('academic_year').related_model.objects.all(),
        source='academic_year',
        write_only=True
    )
    institution = InstitutionMinimalSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        queryset=Stream._meta.get_field('institution').related_model.objects.all(),
        source='institution',
        write_only=True
    )
    class_teacher = TeacherMinimalSerializer(read_only=True)
    class_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Stream._meta.get_field('class_teacher').related_model.objects.all(),
        source='class_teacher',
        write_only=True,
        required=False,
        allow_null=True
    )

    current_student_count = serializers.IntegerField(read_only=True)
    is_over_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Stream
        fields = [
            'id', 'name', 'code', 'order', 'description',
            'class_level', 'class_level_id',
            'academic_year', 'academic_year_id',
            'institution', 'institution_id',
            'capacity', 'current_student_count', 'is_over_capacity',
            'class_teacher', 'class_teacher_id',
            'is_active', 'auto_promote_enabled',
            'average_score', 'average_attendance_rate', 'rank_within_class_level',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'created_at', 'updated_at',
            'average_score', 'average_attendance_rate',
            'rank_within_class_level', 'current_student_count'
        ]

    def get_is_over_capacity(self, obj):
        return obj.is_over_capacity() if hasattr(obj, 'is_over_capacity') else None
