# alumni/ai.py

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from sklearn.cluster import KMeans
import numpy as np

from .models import (
    AlumniProfile, AlumniDonation, AlumniMentorship,
    AlumniEventRegistration, AlumniEmployment
)


class AlumniAIAgent:
    """
    AI-powered engine to derive insights and recommendations
    for alumni engagement, donation prediction, and mentorship matching.
    """

    def __init__(self, institution):
        self.institution = institution

    def predict_top_donors(self, top_n=5):
        """
        Predict alumni who are likely to donate based on past donations and engagement.
        """
        alumni = AlumniProfile.objects.filter(institution=self.institution).annotate(
            total_donations=Count('alumnidonation'),
            events_attended=Count('eventregistration'),
            mentorships=Count('mentorships')
        )

        ranked = sorted(
            alumni,
            key=lambda a: (
                getattr(a, 'total_donations', 0) * 2 +
                getattr(a, 'events_attended', 0) +
                getattr(a, 'mentorships', 0)
            ),
            reverse=True
        )
        return ranked[:top_n]

    def alumni_engagement_score(self, alumni):
        """
        Compute an engagement score for a given alumni.
        """
        donations = AlumniDonation.objects.filter(alumni=alumni).count()
        registrations = AlumniEventRegistration.objects.filter(alumni=alumni).count()
        mentorships = AlumniMentorship.objects.filter(mentor=alumni).count()

        score = donations * 2 + registrations + mentorships
        return score

    def identify_inactive_alumni(self, days_inactive=365):
        """
        Identify alumni who haven't interacted recently (events, donations, etc.).
        """
        cutoff = timezone.now() - timedelta(days=days_inactive)

        inactive = AlumniProfile.objects.filter(
            institution=self.institution
        ).exclude(
            Q(alumnidonation__donated_on__gte=cutoff) |
            Q(eventregistration__registered_on__gte=cutoff) |
            Q(mentorships__start_date__gte=cutoff)
        ).distinct()

        return inactive

    def mentorship_recommendations(self, student):
        """
        Recommend mentors to a student based on course/profession matching.
        """
        student_course = student.current_class.course if hasattr(student, 'current_class') else None

        recommended = AlumniProfile.objects.filter(
            institution=self.institution,
            course__iexact=student_course
        ).order_by('-joined_on')[:5]

        return recommended

    def cluster_alumni_by_employment(self, num_clusters=3):
        """
        Use KMeans clustering to segment alumni based on employment features.
        """
        alumni_qs = AlumniProfile.objects.filter(institution=self.institution).annotate(
            job_count=Count('employment_records'),
            avg_duration=Avg('employment_records__end_date')
        )

        data = []
        alumni_list = []
        for alumni in alumni_qs:
            job_count = alumni.job_count or 0
            # Dummy value for clustering, replace with proper numeric encoding if available
            avg_duration = (alumni.avg_duration - timezone.now().date()).days if alumni.avg_duration else 0
            data.append([job_count, avg_duration])
            alumni_list.append(alumni)

        if len(data) < num_clusters:
            return {}

        kmeans = KMeans(n_clusters=num_clusters, random_state=0).fit(data)
        clusters = {}
        for i, alumni in enumerate(alumni_list):
            cluster = kmeans.labels_[i]
            clusters.setdefault(cluster, []).append(alumni)

        return clusters
