from django.db.models import Count, Avg, Q
from teachers.models import Teacher
from timetable.models import PeriodTemplate
from subjects.models import SubjectAssignment
from exams.models import ExamResult
from classes.models import Stream, ClassLevel
from datetime import date


class TeacherAnalytics:
    """
    Provides analytics for a given institution’s teachers.
    """

    def __init__(self, institution):
        self.institution = institution

    def total_teachers(self):
        return Teacher.objects.filter(institution=self.institution).count()

    def active_teachers(self):
        return Teacher.objects.filter(institution=self.institution, is_active=True).count()

    def gender_distribution(self):
        return Teacher.objects.filter(institution=self.institution).values('user__gender').annotate(
            total=Count('id')
        )

    def teachers_by_department(self):
        return Teacher.objects.filter(institution=self.institution).values('department__name').annotate(
            total=Count('id')
        ).order_by('-total')

    def top_performing_teachers(self, limit=5):
        return ExamResult.objects.filter(
            subject__assigned_teachers__institution=self.institution
        ).values(
            'subject__assigned_teachers__id',
            'subject__assigned_teachers__first_name',
            'subject__assigned_teachers__last_name'
        ).annotate(avg_score=Avg('marks')).order_by('-avg_score')[:limit]

    def most_loaded_teachers(self, limit=5):
        return Teacher.objects.filter(
            institution=self.institution
        ).annotate(
            total_periods=Count('timetable_entries')
        ).values(
            'id', 'user__first_name', 'user__last_name', 'total_periods'
        ).order_by('-total_periods')[:limit]

    def teacher_subject_distribution(self):
        return Teacher.objects.filter(institution=self.institution).annotate(
            total_subjects=Count('assignments')
        ).values('user__first_name', 'user__last_name', 'total_subjects').order_by('-total_subjects')

    def teachers_per_stream(self):
        return Stream.objects.filter(
            teachers__institution=self.institution
        ).annotate(total_teachers=Count('teachers')).values('name', 'total_teachers').order_by('-total_teachers')

    def teachers_per_class_level(self):
        return ClassLevel.objects.filter(
            teachers__institution=self.institution
        ).annotate(total_teachers=Count('teachers')).values('name', 'total_teachers')

    def generate_summary(self):
        return {
            "total_teachers": self.total_teachers(),
            "active_teachers": self.active_teachers(),
            "gender_distribution": list(self.gender_distribution()),
            "teachers_by_department": list(self.teachers_by_department()),
            "top_performing_teachers": list(self.top_performing_teachers()),
            "most_loaded_teachers": list(self.most_loaded_teachers()),
            "teacher_subject_distribution": list(self.teacher_subject_distribution()),
            "teachers_per_stream": list(self.teachers_per_stream()),
            "teachers_per_class_level": list(self.teachers_per_class_level()),
        }
