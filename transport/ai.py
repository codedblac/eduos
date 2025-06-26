from datetime import timedelta
from django.utils import timezone
from transport.models import TransportRoute, TransportVehicle, StudentTransportAssignment, TripAttendance
from students.models import Student
from accounts.models import CustomUser
from django.db.models import Count, Avg, Q

class TransportAIEngine:
    """
    AI assistant for Transport Management in EduOS.
    Supports smart routing, efficiency tracking, and proactive recommendations.
    """

    def __init__(self, institution):
        self.institution = institution

    def suggest_optimal_routes(self):
        """
        Suggests route optimization based on number of students, stop proximity, and trip delays.
        """
        routes = TransportRoute.objects.filter(institution=self.institution)
        suggestions = []
        for route in routes:
            student_count = StudentTransportAssignment.objects.filter(route=route).count()
            avg_delay = TripAttendance.objects.filter(route=route).aggregate(avg_delay=Avg('delay_minutes'))['avg_delay'] or 0
            if student_count > 50 or avg_delay > 15:
                suggestions.append({
                    'route': route.name,
                    'student_count': student_count,
                    'average_delay': avg_delay,
                    'recommendation': 'Consider splitting or adjusting this route.'
                })
        return suggestions

    def vehicle_efficiency_analysis(self):
        """
        Analyzes vehicle usage, capacity, and issues.
        """
        vehicles = TransportVehicle.objects.filter(institution=self.institution)
        insights = []
        for vehicle in vehicles:
            assigned_students = StudentTransportAssignment.objects.filter(vehicle=vehicle).count()
            if vehicle.capacity and assigned_students > vehicle.capacity:
                insights.append({
                    'vehicle': vehicle.registration_number,
                    'capacity': vehicle.capacity,
                    'assigned_students': assigned_students,
                    'issue': 'Over-assigned'
                })
        return insights

    def attendance_issues(self):
        """
        Flags routes with chronic absentees or late pickups.
        """
        week_ago = timezone.now() - timedelta(days=7)
        issues = []
        qs = TripAttendance.objects.filter(institution=self.institution, timestamp__gte=week_ago)
        flagged = qs.values('student').annotate(absent_days=Count('id', filter=Q(status='absent'))).filter(absent_days__gte=3)
        for entry in flagged:
            student = Student.objects.get(id=entry['student'])
            issues.append({
                'student': student.full_name(),
                'absent_days': entry['absent_days'],
                'note': 'Student frequently missing transport.'
            })
        return issues

    def maintenance_prediction(self):
        """
        Predicts vehicles likely due for maintenance.
        """
        upcoming = []
        vehicles = TransportVehicle.objects.filter(institution=self.institution)
        for v in vehicles:
            if v.last_service_date:
                days_since = (timezone.now().date() - v.last_service_date).days
                if days_since >= 180:
                    upcoming.append({
                        'vehicle': v.registration_number,
                        'last_serviced': v.last_service_date,
                        'note': 'Due for service (6-month cycle)'
                    })
        return upcoming

    def get_summary(self):
        return {
            'route_recommendations': self.suggest_optimal_routes(),
            'vehicle_issues': self.vehicle_efficiency_analysis(),
            'transport_absentees': self.attendance_issues(),
            'maintenance_due': self.maintenance_prediction()
        }
