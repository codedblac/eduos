from rest_framework import serializers
from django.db.models import Max

from academics.models import AcademicYear
from .models import (
    ClassLevel,
    Stream,
    StudentStreamEnrollment,
    StreamAnalytics,
    ClassLevelAnalytics,
)

from institutions.serializers import InstitutionMinimalSerializer
from academics.serializers import AcademicYearMinimalSerializer
from teachers.serializers import TeacherMinimalSerializer
from students.serializers import StudentMinimalSerializer


# ======================================================
# 🔹 CLASS LEVEL SERIALIZERS
# ======================================================

class ClassLevelMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassLevel
        fields = ["id", "name", "code"]


class ClassLevelSerializer(serializers.ModelSerializer):
    institution = InstitutionMinimalSerializer(read_only=True)

    class_teacher = TeacherMinimalSerializer(read_only=True)
    class_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel._meta.get_field("class_teacher")
        .remote_field.model.objects.all(),
        source="class_teacher",
        write_only=True,
        required=False,
        allow_null=True,
    )

    default_promotion_class = ClassLevelMinimalSerializer(read_only=True)
    default_promotion_class_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source="default_promotion_class",
        write_only=True,
        required=False,
        allow_null=True,
    )

    total_streams = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = ClassLevel
        fields = [
            "id",
            "institution",
            "name",
            "code",
            "order",
            "description",
            "is_graduating_level",
            "requires_national_exam",
            "class_teacher",
            "class_teacher_id",
            "default_promotion_class",
            "default_promotion_class_id",
            "total_streams",
            "total_students",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "institution",
            "total_streams",
            "total_students",
            "created_at",
            "updated_at",
        )

    # --------------------------------------------------
    # ✅ VALIDATION (NO DB SIDE EFFECTS)
    # --------------------------------------------------
    def validate(self, attrs):
        request = self.context["request"]
        institution = request.user.institution

        if not attrs.get("name"):
            raise serializers.ValidationError(
                {"name": "Class level name is required (e.g. Grade 1)."}
            )

        if not attrs.get("code"):
            attrs["code"] = attrs["name"].upper().replace(" ", "_")

        if attrs.get("order") is None:
            max_order = (
                ClassLevel.objects
                .filter(institution=institution)
                .aggregate(Max("order"))["order__max"]
            )
            attrs["order"] = (max_order or 0) + 1

        if (
            self.instance is not None
            and attrs.get("default_promotion_class") == self.instance
        ):
            raise serializers.ValidationError(
                {"default_promotion_class": "A class cannot promote to itself."}
            )

        return attrs

    # --------------------------------------------------
    # ✅ CREATE (NO ACADEMIC YEAR HERE)
    # --------------------------------------------------
    def create(self, validated_data):
        request = self.context["request"]
        validated_data.pop("academic_year", None)  # frontend safety
        validated_data["institution"] = request.user.institution
        return ClassLevel.objects.create(**validated_data)

    def get_total_streams(self, obj):
        return obj.streams.count()

    def get_total_students(self, obj):
        return StudentStreamEnrollment.objects.filter(
            stream__class_level=obj,
            status="active",
        ).count()


# ======================================================
# 🔹 STREAM SERIALIZERS
# ======================================================

class StreamMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stream
        fields = ["id", "name", "code"]


class StreamSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMinimalSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        queryset=ClassLevel.objects.all(),
        source="class_level",
        write_only=True,
    )

    academic_year = AcademicYearMinimalSerializer(read_only=True)

    stream_teacher = TeacherMinimalSerializer(read_only=True)
    stream_teacher_id = serializers.PrimaryKeyRelatedField(
        queryset=Stream._meta.get_field("stream_teacher")
        .remote_field.model.objects.all(),
        source="stream_teacher",
        write_only=True,
        required=False,
        allow_null=True,
    )

    current_student_count = serializers.SerializerMethodField()
    is_over_capacity = serializers.SerializerMethodField()

    class Meta:
        model = Stream
        fields = [
            "id",
            "name",
            "code",
            "order",
            "description",
            "class_level",
            "class_level_id",
            "academic_year",
            "capacity",
            "current_student_count",
            "is_over_capacity",
            "stream_teacher",
            "stream_teacher_id",
            "is_active",
            "auto_promote_enabled",
            "created_at",
            "updated_at",
        ]
        read_only_fields = (
            "id",
            "academic_year",
            "current_student_count",
            "is_over_capacity",
            "created_at",
            "updated_at",
        )

    # --------------------------------------------------
    # ✅ VALIDATION
    # --------------------------------------------------
    def validate(self, attrs):
        if not attrs.get("name"):
            raise serializers.ValidationError(
                {"name": "Stream name is required (e.g. Stream A)."}
            )

        if not attrs.get("code"):
            attrs["code"] = attrs["name"].upper().replace(" ", "_")

        if attrs.get("order") is None:
            max_order = (
                Stream.objects
                .filter(class_level=attrs["class_level"])
                .aggregate(Max("order"))["order__max"]
            )
            attrs["order"] = (max_order or 0) + 1

        return attrs

    # --------------------------------------------------
    # ✅ CREATE (ASSIGNS ACTIVE ACADEMIC YEAR)
    # --------------------------------------------------
    def create(self, validated_data):
        request = self.context["request"]

        academic_year = AcademicYear.objects.filter(
            institution=request.user.institution,
            is_current=True,
        ).first()

        if not academic_year:
            raise serializers.ValidationError(
                {"academic_year": "No active academic year found."}
            )

        validated_data["academic_year"] = academic_year
        return Stream.objects.create(**validated_data)

    # --------------------------------------------------
    # ✅ SAFE COMPUTED FIELDS
    # --------------------------------------------------
    def get_current_student_count(self, obj):
        # prefer annotation, fallback to property
        return getattr(obj, "current_student_count", obj.current_student_count)

    def get_is_over_capacity(self, obj):
        return obj.is_over_capacity_flag()


# ======================================================
# 🔹 STUDENT STREAM ENROLLMENT SERIALIZERS
# ======================================================

class StudentStreamEnrollmentSerializer(serializers.ModelSerializer):
    student = StudentMinimalSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        queryset=StudentStreamEnrollment._meta.get_field("student")
        .remote_field.model.objects.all(),
        source="student",
        write_only=True,
    )

    stream = StreamMinimalSerializer(read_only=True)
    stream_id = serializers.PrimaryKeyRelatedField(
        queryset=Stream.objects.all(),
        source="stream",
        write_only=True,
    )

    academic_year = AcademicYearMinimalSerializer(read_only=True)

    class Meta:
        model = StudentStreamEnrollment
        fields = [
            "id",
            "student",
            "student_id",
            "stream",
            "stream_id",
            "academic_year",
            "status",
            "date_assigned",
            "date_left",
        ]
        read_only_fields = (
            "academic_year",
            "date_assigned",
        )


# ======================================================
# 🔹 ANALYTICS SERIALIZERS (READ-ONLY)
# ======================================================

class StreamAnalyticsSerializer(serializers.ModelSerializer):
    stream = StreamMinimalSerializer(read_only=True)
    academic_year = AcademicYearMinimalSerializer(read_only=True)

    class Meta:
        model = StreamAnalytics
        fields = [
            "stream",
            "academic_year",
            "total_students",
            "average_score",
            "attendance_rate",
            "discipline_index",
            "calculated_at",
        ]
        read_only_fields = fields


class ClassLevelAnalyticsSerializer(serializers.ModelSerializer):
    class_level = ClassLevelMinimalSerializer(read_only=True)
    academic_year = AcademicYearMinimalSerializer(read_only=True)
    top_stream = StreamMinimalSerializer(read_only=True)

    class Meta:
        model = ClassLevelAnalytics
        fields = [
            "class_level",
            "academic_year",
            "total_students",
            "average_score",
            "top_stream",
            "calculated_at",
        ]
        read_only_fields = fields
