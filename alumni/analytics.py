from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import timedelta
from .models import (
    AlumniProfile, AlumniEvent, AlumniEventRegistration,
    AlumniDonation, AlumniMentorship, AlumniEmployment,
    AlumniFeedback, AlumniMembership
)
from institutions.models import Institution


class AlumniAnalyticsEngine:
    def __init__(self, institution: Institution):
        self.institution = institution

    def alumni_count(self):
        total = AlumniProfile.objects.filter(institution=self.institution).count()
        verified = AlumniProfile.objects.filter(institution=self.institution, is_verified=True).count()
        with_employment = AlumniEmployment.objects.filter(alumni__institution=self.institution, currently_employed=True).values('alumni').distinct().count()

        return {
            "total_alumni": total,
            "verified_alumni": verified,
            "currently_employed": with_employment
        }

    def employment_industry_breakdown(self):
        industries = AlumniEmployment.objects.filter(
            alumni__institution=self.institution
        ).values('industry').annotate(count=Count('id')).order_by('-count')

        return [{"industry": i['industry'] or "Unspecified", "count": i['count']} for i in industries]

    def top_employers(self, limit=10):
        top = AlumniEmployment.objects.filter(
            alumni__institution=self.institution
        ).values('company_name').annotate(count=Count('id')).order_by('-count')[:limit]

        return [{"company": entry['company_name'], "alumni_count": entry['count']} for entry in top]

    def donations_summary(self):
        total_amount = AlumniDonation.objects.filter(institution=self.institution).aggregate(total=Sum('amount'))['total'] or 0
        recent = AlumniDonation.objects.filter(institution=self.institution).order_by('-donated_on')[:5]

        return {
            "total_donated": total_amount,
            "recent_donations": [
                {
                    "alumni": d.alumni.student.full_name(),
                    "amount": d.amount,
                    "purpose": d.purpose,
                    "date": d.donated_on
                } for d in recent
            ]
        }

    def event_participation_stats(self):
        events = AlumniEvent.objects.filter(institution=self.institution).annotate(
            registration_count=Count('registrations'),
            attendance_count=Count('registrations', filter=Q(registrations__is_attended=True))
        ).order_by('-event_date')

        return [
            {
                "event": e.title,
                "date": e.event_date,
                "registrations": e.registration_count,
                "attended": e.attendance_count
            } for e in events
        ]

    def mentorship_activity(self):
        total = AlumniMentorship.objects.filter(institution=self.institution).count()
        active = AlumniMentorship.objects.filter(institution=self.institution, status='active').count()
        ended = total - active

        return {
            "total_mentorships": total,
            "active": active,
            "ended": ended
        }

    def feedback_summary(self):
        total = AlumniFeedback.objects.filter(institution=self.institution).count()
        responded = AlumniFeedback.objects.filter(institution=self.institution, responded=True).count()

        return {
            "total_feedback": total,
            "responded": responded,
            "pending": total - responded
        }

    def membership_insights(self):
        active = AlumniMembership.objects.filter(institution=self.institution, is_active_member=True).count()
        overdue = AlumniMembership.objects.filter(
            institution=self.institution,
            is_active_member=True,
            next_due_date__lt=timezone.now().date()
        ).count()

        return {
            "active_memberships": active,
            "overdue_renewals": overdue
        }

    def alumni_engagement_trend(self, days=30):
        cutoff = timezone.now() - timedelta(days=days)
        new_alumni = AlumniProfile.objects.filter(institution=self.institution, joined_on__gte=cutoff).count()
        recent_donations = AlumniDonation.objects.filter(institution=self.institution, donated_on__gte=cutoff).count()
        recent_registrations = AlumniEventRegistration.objects.filter(event__institution=self.institution, registered_on__gte=cutoff).count()

        return {
            "new_alumni_last_30_days": new_alumni,
            "donations_last_30_days": recent_donations,
            "event_registrations_last_30_days": recent_registrations
        }
