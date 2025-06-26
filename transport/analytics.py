# transport/analytics.py

from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import Vehicle, TripLog, MaintenanceRecord, TransportBooking
from institutions.models import Institution

class TransportAnalyticsEngine:
    def __init__(self, institution: Institution):
        self.institution = institution

    def vehicle_utilization_summary(self):
        vehicles = Vehicle.objects.filter(institution=self.institution)
        data = []

        for vehicle in vehicles:
            trip_count = TripLog.objects.filter(vehicle=vehicle).count()
            total_distance = TripLog.objects.filter(vehicle=vehicle).aggregate(Sum('distance_km'))['distance_km__sum'] or 0
            total_fuel = TripLog.objects.filter(vehicle=vehicle).aggregate(Sum('fuel_used_liters'))['fuel_used_liters__sum'] or 0
            avg_efficiency = total_distance / total_fuel if total_fuel else 0

            data.append({
                "vehicle": str(vehicle),
                "total_trips": trip_count,
                "total_distance_km": total_distance,
                "total_fuel_liters": total_fuel,
                "average_efficiency_km_per_liter": round(avg_efficiency, 2),
            })

        return data

    def maintenance_summary(self):
        records = MaintenanceRecord.objects.filter(institution=self.institution)
        recent = records.order_by('-date')[:10]
        upcoming_due = Vehicle.objects.filter(
            institution=self.institution,
            next_service_due__lte=timezone.now() + timedelta(days=30)
        )

        return {
            "recent_maintenance": [
                {
                    "vehicle": str(r.vehicle),
                    "service_type": r.service_type,
                    "date": r.date,
                    "notes": r.notes,
                }
                for r in recent
            ],
            "upcoming_due_vehicles": [
                {
                    "vehicle": str(v),
                    "due_date": v.next_service_due,
                    "assigned_driver": str(v.assigned_driver) if v.assigned_driver else None
                }
                for v in upcoming_due
            ]
        }

    def booking_statistics(self):
        total = TransportBooking.objects.filter(institution=self.institution).count()
        approved = TransportBooking.objects.filter(institution=self.institution, status='approved').count()
        rejected = TransportBooking.objects.filter(institution=self.institution, status='rejected').count()
        pending = TransportBooking.objects.filter(institution=self.institution, status='pending').count()

        return {
            "total_bookings": total,
            "approved": approved,
            "rejected": rejected,
            "pending": pending,
        }

    def weekly_trip_heatmap(self):
        today = timezone.now().date()
        last_7_days = [today - timedelta(days=i) for i in range(6, -1, -1)]
        data = []

        for day in last_7_days:
            trips = TripLog.objects.filter(
                institution=self.institution,
                trip_date=day
            ).count()
            data.append({"date": day.strftime("%Y-%m-%d"), "trips": trips})

        return data

    def driver_activity_report(self):
        drivers = TripLog.objects.filter(institution=self.institution).values('driver').annotate(
            trip_count=Count('id'),
            total_km=Sum('distance_km'),
            total_fuel=Sum('fuel_used_liters')
        ).order_by('-trip_count')

        return [
            {
                "driver_id": entry['driver'],
                "trip_count": entry['trip_count'],
                "total_km": entry['total_km'],
                "total_fuel_liters": entry['total_fuel']
            }
            for entry in drivers
        ]
