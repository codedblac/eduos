# academics/serializers.py

from rest_framework import serializers
from .models import (
    AcademicYear,
    Term,
    HolidayBreak,
    AcademicEvent,
    AcademicAuditLog
)

# ===============================
# ✅ MINIMAL SERIALIZERS
# ===============================

class AcademicYearMinimalSerializer(serializers.ModelSerializer):
    """
    Lightweight AcademicYear serializer (used in nested relationships).
    """
    class Meta:
        model = AcademicYear
        fields = ['id', 'name']


class TermMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal term serializer for nested displays.
    """
    class Meta:
        model = Term
        fields = ['id', 'name']


# ===============================
# 📅 Academic Year Serializers
# ===============================

class AcademicYearCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = [
            'id', 'institution', 'name', 'start_date', 'end_date',
            'is_current', 'notes'
        ]
        read_only_fields = ['id']


class TermSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', 'name', 'start_date', 'end_date', 'is_active']


class AcademicYearSerializer(serializers.ModelSerializer):
    terms = TermSimpleSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicYear
        fields = [
            'id', 'institution', 'name', 'start_date', 'end_date',
            'is_current', 'notes', 'terms', 'created_at', 'updated_at'
        ]


# ===============================
# 📘 Term Serializers
# ===============================

class TermCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = [
            'id', 'academic_year', 'name', 'start_date', 'end_date',
            'is_active', 'midterm_date', 'closing_remarks'
        ]
        read_only_fields = ['id']


class TermSerializer(serializers.ModelSerializer):
    breaks = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Term
        fields = [
            'id', 'academic_year', 'name', 'start_date', 'end_date',
            'is_active', 'midterm_date', 'closing_remarks',
            'created_at', 'updated_at', 'breaks'
        ]


# ===============================
# 🏖️ Holiday / Break Serializers
# ===============================

class HolidayBreakCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = HolidayBreak
        fields = ['id', 'term', 'title', 'start_date', 'end_date', 'description']
        read_only_fields = ['id']


class HolidayBreakSerializer(serializers.ModelSerializer):
    term_name = serializers.CharField(source='term.name', read_only=True)

    class Meta:
        model = HolidayBreak
        fields = ['id', 'term', 'term_name', 'title', 'start_date', 'end_date', 'description']


# ===============================
# 📌 Academic Event Serializers
# ===============================

class AcademicEventCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicEvent
        fields = [
            'id', 'institution', 'academic_year', 'term',
            'title', 'description', 'start_date', 'end_date',
            'is_school_wide', 'color_code'
        ]
        read_only_fields = ['id']


class AcademicEventSerializer(serializers.ModelSerializer):
    term_name = serializers.CharField(source='term.name', read_only=True)
    year_name = serializers.CharField(source='academic_year.name', read_only=True)

    class Meta:
        model = AcademicEvent
        fields = [
            'id', 'institution', 'academic_year', 'year_name',
            'term', 'term_name', 'title', 'description',
            'start_date', 'end_date', 'is_school_wide', 'color_code'
        ]


# ===============================
# 🧾 Audit Log Serializer
# ===============================

class AcademicAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.get_full_name', read_only=True)

    class Meta:
        model = AcademicAuditLog
        fields = [
            'id', 'actor', 'actor_name', 'action', 'model_name',
            'record_id', 'timestamp', 'notes'
        ]
