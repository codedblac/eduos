from rest_framework import serializers
from .models import AcademicYear, Term, HolidayBreak, AcademicEvent, AcademicAuditLog


class AcademicYearSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicYear
        fields = '__all__'


class TermSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source='academic_year', write_only=True
    )

    class Meta:
        model = Term
        fields = ['id', 'name', 'start_date', 'end_date', 'midterm_date', 'closing_remarks',
                  'is_active', 'created_at', 'academic_year', 'academic_year_id']


class HolidayBreakSerializer(serializers.ModelSerializer):
    term = TermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), source='term', write_only=True
    )

    class Meta:
        model = HolidayBreak
        fields = ['id', 'title', 'start_date', 'end_date', 'description', 'term', 'term_id']


class AcademicEventSerializer(serializers.ModelSerializer):
    academic_year = AcademicYearSerializer(read_only=True)
    academic_year_id = serializers.PrimaryKeyRelatedField(
        queryset=AcademicYear.objects.all(), source='academic_year', write_only=True
    )
    term = TermSerializer(read_only=True)
    term_id = serializers.PrimaryKeyRelatedField(
        queryset=Term.objects.all(), source='term', write_only=True
    )

    class Meta:
        model = AcademicEvent
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'is_school_wide',
                  'color_code', 'institution', 'academic_year', 'academic_year_id', 'term', 'term_id']


class AcademicAuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source='actor.username', read_only=True)

    class Meta:
        model = AcademicAuditLog
        fields = ['id', 'actor', 'actor_name', 'action', 'model_name', 'record_id', 'timestamp', 'notes']
