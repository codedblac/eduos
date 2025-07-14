from rest_framework import serializers
from exams.models import (
    Exam, ExamSubject, StudentScore, ExamResult, GradeBoundary, ExamInsight,
    ExamPrediction, ExamTemplate, ExamArchive, ExamSchedule, GradingEngineLog,
    ExamTask, RecurringExamRule
)
from students.serializers import StudentSerializer
from subjects.serializers import SubjectSerializer
from classes.serializers import StreamSerializer, ClassLevelSerializer
from institutions.serializers import InstitutionSerializer
# from users.serializers import UserSerializer  # Uncomment if available

# ========================
# Main Serializers
# ========================

class ExamSerializer(serializers.ModelSerializer):
    class_level = ClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        source='class_level', queryset=Exam._meta.get_field('class_level').related_model.objects.all(), write_only=True
    )
    stream = StreamSerializer(read_only=True)
    stream_id = serializers.PrimaryKeyRelatedField(
        source='stream', queryset=Exam._meta.get_field('stream').related_model.objects.all(), write_only=True
    )
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        source='institution', queryset=Exam._meta.get_field('institution').related_model.objects.all(), write_only=True
    )
    # created_by = UserSerializer(read_only=True)

    class Meta:
        model = Exam
        fields = '__all__'


class ExamSubjectSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject', queryset=ExamSubject._meta.get_field('subject').related_model.objects.all(), write_only=True
    )
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam', queryset=ExamSubject._meta.get_field('exam').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = ExamSubject
        fields = '__all__'


class StudentScoreSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student', queryset=StudentScore._meta.get_field('student').related_model.objects.all(), write_only=True
    )
    exam_subject = ExamSubjectSerializer(read_only=True)
    exam_subject_id = serializers.PrimaryKeyRelatedField(
        source='exam_subject', queryset=StudentScore._meta.get_field('exam_subject').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = StudentScore
        fields = '__all__'


class ExamResultSerializer(serializers.ModelSerializer):
    student = StudentSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source='student', queryset=ExamResult._meta.get_field('student').related_model.objects.all(), write_only=True
    )
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam', queryset=ExamResult._meta.get_field('exam').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = ExamResult
        fields = '__all__'


class GradeBoundarySerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject', queryset=GradeBoundary._meta.get_field('subject').related_model.objects.all(), write_only=True
    )
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        source='institution', queryset=GradeBoundary._meta.get_field('institution').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = GradeBoundary
        fields = '__all__'


class ExamInsightSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam', queryset=ExamInsight._meta.get_field('exam').related_model.objects.all(), write_only=True
    )
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject', queryset=ExamInsight._meta.get_field('subject').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = ExamInsight
        fields = '__all__'


class ExamPredictionSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject', queryset=ExamPrediction._meta.get_field('subject').related_model.objects.all(), write_only=True
    )
    class_level = ClassLevelSerializer(read_only=True)
    class_level_id = serializers.PrimaryKeyRelatedField(
        source='class_level', queryset=ExamPrediction._meta.get_field('class_level').related_model.objects.all(), write_only=True
    )
    stream = StreamSerializer(read_only=True)
    stream_id = serializers.PrimaryKeyRelatedField(
        source='stream', queryset=ExamPrediction._meta.get_field('stream').related_model.objects.all(), write_only=True
    )
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        source='institution', queryset=ExamPrediction._meta.get_field('institution').related_model.objects.all(), write_only=True
    )
    # created_by = UserSerializer(read_only=True)

    class Meta:
        model = ExamPrediction
        fields = '__all__'


class ExamTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamTemplate
        fields = '__all__'


class ExamArchiveSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source='subject', queryset=ExamArchive._meta.get_field('subject').related_model.objects.all(), write_only=True
    )
    extracted_text = serializers.CharField(source='ocr_result.text', read_only=True)

    class Meta:
        model = ExamArchive
        fields = '__all__'


class ExamScheduleSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam', queryset=ExamSchedule._meta.get_field('exam').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = ExamSchedule
        fields = '__all__'


class GradingEngineLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradingEngineLog
        fields = '__all__'


class ExamTaskSerializer(serializers.ModelSerializer):
    exam = ExamSerializer(read_only=True)
    exam_id = serializers.PrimaryKeyRelatedField(
        source='exam', queryset=ExamTask._meta.get_field('exam').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = ExamTask
        fields = '__all__'


class RecurringExamRuleSerializer(serializers.ModelSerializer):
    exam_template = ExamTemplateSerializer(read_only=True)
    exam_template_id = serializers.PrimaryKeyRelatedField(
        source='exam_template', queryset=RecurringExamRule._meta.get_field('exam_template').related_model.objects.all(), write_only=True
    )
    institution = InstitutionSerializer(read_only=True)
    institution_id = serializers.PrimaryKeyRelatedField(
        source='institution', queryset=RecurringExamRule._meta.get_field('institution').related_model.objects.all(), write_only=True
    )

    class Meta:
        model = RecurringExamRule
        fields = '__all__'
