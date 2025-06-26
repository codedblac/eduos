# maintenance/ai.py

from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import MaintenanceRequest, Equipment, Technician, MaintenanceLog


class MaintenanceAIEngine:

    @staticmethod
    def recommend_technician(equipment):
        """
        Recommend a technician based on past successful maintenance logs for this type of equipment.
        """
        logs = MaintenanceLog.objects.filter(equipment__category=equipment.category)
        technician_scores = logs.values('technician').annotate(count=Count('id')).order_by('-count')

        if technician_scores:
            top_technician_id = technician_scores[0]['technician']
            return Technician.objects.filter(id=top_technician_id).first()
        return None

    @staticmethod
    def predict_equipment_failure(equipment):
        """
        Predict failure risk based on request frequency and completion delays.
        Returns: 'High', 'Medium', or 'Low'
        """
        recent_requests = MaintenanceRequest.objects.filter(
            equipment=equipment,
            created_at__gte=timezone.now() - timedelta(days=90)
        )

        frequency = recent_requests.count()
        avg_delay = recent_requests.annotate(
            delay=Avg('completed_at') - Avg('created_at')
        ).aggregate(avg=Avg('delay'))['avg'] or timedelta(0)

        if frequency >= 5 or avg_delay > timedelta(days=7):
            return "High"
        elif frequency >= 3:
            return "Medium"
        return "Low"

    @staticmethod
    def generate_equipment_health_report():
        """
        Generate a summarized report on equipment health for dashboard analytics.
        Returns a list of equipment with status.
        """
        report = []
        for equipment in Equipment.objects.all():
            status = MaintenanceAIEngine.predict_equipment_failure(equipment)
            report.append({
                'equipment': equipment.name,
                'category': equipment.category.name,
                'risk': status,
                'last_maintenance': equipment.maintenance_logs.order_by('-completed_at').first(),
                'open_requests': MaintenanceRequest.objects.filter(equipment=equipment, status__in=['pending', 'approved']).count()
            })
        return report

    @staticmethod
    def upcoming_maintenance_schedule():
        """
        Suggest equipment that will need preventive maintenance soon.
        """
        soon = timezone.now() + timedelta(days=30)
        equipment_due = Equipment.objects.filter(next_maintenance_due__lte=soon)
        return equipment_due

