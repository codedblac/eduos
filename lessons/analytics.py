from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import LessonPlan, LessonSchedule, LessonSession
from subjects.models import Subject
from institutions.models import Institution


class LessonAnalytics:
    """
    Central analytics engine for extracting insights from the lessons module.
    """

    @staticmethod
    def coverage_summary_by_teacher(teacher_id, term_id=None):
        plans = LessonPlan.objects.filter(teacher_id=teacher_id)
        if term_id:
            plans = plans.filter(term_id=term_id)

        total = plans.count()
        approved = plans.filter(is_approved=True).count()
        delivered = LessonSession.objects.filter(
            lesson_schedule__lesson_plan__in=plans,
            coverage_status='covered'
        ).count()

        return {
            'total_plans': total,
            'approved': approved,
            'delivered_sessions': delivered,
            'coverage_rate': round((delivered / total) * 100, 2) if total else 0
        }

    @staticmethod
    def subject_wise_lesson_stats(subject_id, term_id=None):
        plans = LessonPlan.objects.filter(subject_id=subject_id)
        if term_id:
            plans = plans.filter(term_id=term_id)

        sessions = LessonSession.objects.filter(lesson_schedule__lesson_plan__in=plans)

        return {
            'total_lesson_plans': plans.count(),
            'sessions_held': sessions.count(),
            'covered': sessions.filter(coverage_status='covered').count(),
            'skipped': sessions.filter(coverage_status='skipped').count(),
            'cancelled': sessions.filter(coverage_status='cancelled').count(),
            'postponed': sessions.filter(coverage_status='postponed').count(),
        }

    @staticmethod
    def delivery_trends(institution_id, recent_days=30):
        start_date = timezone.now().date() - timedelta(days=recent_days)
        sessions = LessonSession.objects.filter(
            lesson_schedule__lesson_plan__institution_id=institution_id,
            delivered_on__gte=start_date,
            coverage_status='covered'
        ).values('delivered_on').annotate(
            total=Count('id')
        ).order_by('delivered_on')

        return list(sessions)

    @staticmethod
    def missed_or_skipped_alerts(class_level_id=None, term_id=None):
        sessions = LessonSession.objects.filter(
            coverage_status__in=['skipped', 'cancelled']
        )

        if class_level_id:
            sessions = sessions.filter(lesson_schedule__lesson_plan__class_level_id=class_level_id)
        if term_id:
            sessions = sessions.filter(lesson_schedule__lesson_plan__term_id=term_id)

        return sessions.values(
            'lesson_schedule__lesson_plan__subject__name',
            'lesson_schedule__lesson_plan__teacher__id'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

    @staticmethod
    def weekly_lesson_distribution(teacher_id):
        """
        Count of sessions delivered by a teacher per week in current term.
        """
        from django.db.models.functions import ExtractWeek

        sessions = LessonSession.objects.filter(
            lesson_schedule__lesson_plan__teacher_id=teacher_id,
            coverage_status='covered'
        ).annotate(
            week=ExtractWeek('delivered_on')
        ).values('week').annotate(
            total=Count('id')
        ).order_by('week')

        return list(sessions)

    @staticmethod
    def lesson_plan_approval_stats(institution_id):
        total = LessonPlan.objects.filter(institution_id=institution_id).count()
        approved = LessonPlan.objects.filter(institution_id=institution_id, is_approved=True).count()
        pending = total - approved

        return {
            "total_plans": total,
            "approved": approved,
            "pending": pending,
            "approval_rate": round((approved / total) * 100, 2) if total else 0
        }
