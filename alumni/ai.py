from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q

from .models import AlumniProfile, AlumniContribution, AlumniEvent
from accounts.models import CustomUser

import random


class AlumniAIEngine:

    @staticmethod
    def predict_contribution_likelihood(alumni: AlumniProfile) -> float:
        """
        Predict the likelihood of an alumni making a contribution based on history and engagement.
        Returns a float between 0.0 and 1.0.
        """
        contributions = AlumniContribution.objects.filter(alumni=alumni)
        total = contributions.aggregate(Sum('amount'))['amount__sum'] or 0
        count = contributions.count()
        days_since_last = (timezone.now() - contributions.latest('date_contributed').date_contributed).days if count else 999

        engagement_score = alumni.engagement_score if hasattr(alumni, 'engagement_score') else 0.5
        recency_factor = max(0, 1 - (days_since_last / 180))

        likelihood = min(1.0, (count / 10.0) * 0.4 + (total / 10000.0) * 0.3 + recency_factor * 0.2 + engagement_score * 0.1)
        return round(likelihood, 2)

    @staticmethod
    def recommend_events_for_alumni(alumni: AlumniProfile, limit=3):
        """
        Recommend upcoming alumni events based on location, past interest, and institution.
        """
        return AlumniEvent.objects.filter(
            Q(target_year=alumni.graduation_year) |
            Q(location__icontains=alumni.location) |
            Q(institution=alumni.institution)
        ).order_by('event_date')[:limit]

    @staticmethod
    def generate_personalized_message(user: CustomUser, purpose: str = "contribution_request") -> str:
        """
        Generate a personalized AI message based on the user's profile and interaction history.
        """
        greeting = f"Dear {user.first_name},"
        base = "We hope you're doing well and thriving in your journey after graduation."

        if purpose == "contribution_request":
            message = (
                f"{greeting}\n\n{base}\n\n"
                f"As a valued member of the alumni network of {user.institution.name}, "
                f"your support helps empower future generations. "
                f"Would you consider making a contribution today?\n\nThank you for staying connected!"
            )
        elif purpose == "event_invitation":
            message = (
                f"{greeting}\n\n{base}\n\n"
                "You're warmly invited to our upcoming alumni event. We'd love to reconnect and celebrate our shared journey. "
                "Please check your email or app for details.\n\nLooking forward to seeing you!"
            )
        else:
            message = f"{greeting}\n\n{base}"

        return message

    @staticmethod
    def assign_engagement_score(alumni: AlumniProfile) -> float:
        """
        Calculate and assign an engagement score based on activity.
        """
        contributions = AlumniContribution.objects.filter(alumni=alumni).count()
        events_attended = alumni.events_attended.count() if hasattr(alumni, 'events_attended') else 0
        last_login = alumni.user.last_login or timezone.now() - timedelta(days=365)
        days_inactive = (timezone.now() - last_login).days

        score = min(1.0, (contributions * 0.1) + (events_attended * 0.2) + max(0, 1 - days_inactive / 365) * 0.7)
        alumni.engagement_score = round(score, 2)
        alumni.save()
        return alumni.engagement_score
