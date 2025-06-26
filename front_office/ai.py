from datetime import timedelta
from django.utils import timezone
from .models import (
    VisitorLog, Appointment, ParcelDelivery, GatePass,
    FrontDeskTicket, SecurityLog
)
from django.db.models import Count, Q
import random


class FrontOfficeAIEngine:

    @staticmethod
    def suggest_visit_times(user):
        """
        Suggest optimal visit times based on historical visitor data (least traffic).
        """
        visit_counts = VisitorLog.objects \
            .filter(institution=user.institution) \
            .extra({'hour': "EXTRACT(hour FROM visit_time)"}) \
            .values('hour') \
            .annotate(count=Count('id')) \
            .order_by('count')

        return [entry['hour'] for entry in visit_counts[:3]]  # top 3 least busy hours

    @staticmethod
    def predict_gate_pass_risk():
        """
        Predict gate pass requests that may be risky based on timing, repetition, or unusual reasons.
        """
        recent_passes = GatePass.objects \
            .filter(status='pending', exit_time__gte=timezone.now() - timedelta(days=30)) \
            .annotate(reason_length=Count('reason'))

        flagged = []
        for gate_pass in recent_passes:
            if gate_pass.reason.lower() in ['unknown', 'not sure', 'personal'] or \
               gate_pass.reason_length < 5:
                flagged.append(gate_pass.id)
        return flagged

    @staticmethod
    def prioritize_tickets():
        """
        Use keyword-based analysis to suggest priority levels for newly submitted tickets.
        """
        keywords = {
            'urgent': 'high',
            'accident': 'high',
            'lost': 'medium',
            'help': 'medium',
            'inquiry': 'low',
            'suggestion': 'low'
        }

        tickets = FrontDeskTicket.objects.filter(status='pending')
        updates = {}

        for ticket in tickets:
            content = ticket.description.lower()
            for word, priority in keywords.items():
                if word in content:
                    updates[ticket.id] = priority
                    break

        return updates

    @staticmethod
    def analyze_security_entries(institution):
        """
        Provide basic anomaly detection in security logs (e.g., too many vehicle entries at odd hours).
        """
        night_entries = SecurityLog.objects.filter(
            timestamp__hour__lt=6, institution=institution
        )
        vehicle_count = night_entries.exclude(vehicle_plate='').count()

        if vehicle_count > 10:
            return f"High volume of vehicle entries before 6 AM: {vehicle_count} entries"
        return "No anomaly detected"

    @staticmethod
    def delivery_trends(institution):
        """
        Returns the most common delivery times and senders.
        """
        deliveries = ParcelDelivery.objects.filter(institution=institution)
        hour_counts = deliveries.extra({'hour': "EXTRACT(hour FROM delivered_on)"}).values('hour').annotate(count=Count('id')).order_by('-count')
        top_senders = deliveries.values('sender_name').annotate(count=Count('id')).order_by('-count')[:5]
        return {
            'peak_hours': hour_counts[:3],
            'top_senders': list(top_senders)
        }
