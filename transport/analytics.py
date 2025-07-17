from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import timedelta
from .models import (
    Vehicle, TripLog, VehicleLog,
    MaintenanceRecord, TransportBooking, Driver
)
from institutions.models import Institution


class TransportAnalyticsEngine:
    def __init__(self, institution: Institution):
        self.institution = institution

    def vehicle_utilization_summary(self, days=30):
        """
        Get distance and fuel stats for each vehicle in the past `days`.
        """
        cutoff = timezone.now().date() - timedelta(days=days)
        vehicles = Vehicle.objects.filter(institution=self.institution)
        data = []

        for vehicle in vehicles:
            logs = VehicleLog.objects.filter(vehicle=vehicle, date__gte=cutoff)
            total_distance = logs.aggregate(Sum('distance_travelled_km'))['distance_travelled_km__sum'] or 0
            total_fuel = logs.aggregate(Sum('fuel_used_litres'))['fuel_used_litres__sum'] or 0
            efficiency = (total_distance / total_fuel) if total_fuel else 0
            trip_count = TripLog.objects.filter(vehicle=vehicle, institution=self.institution).count()

            data.append({
                "vehicle": str(vehicle),
                "total_trips": trip_count,
                "total_distance_km": total_distance,
                "total_fuel_litres": total_fuel,
                "average_efficiency_km_per_litre": round(efficiency, 2),
            })

        return data

    def maintenance_summary(self):
        """
        Recent maintenance and upcoming due vehicles.
        """
        recent = MaintenanceRecord.objects.filter(institution=self.institution).order_by('-performed_on')[:10]
        due_soon = Vehicle.objects.filter(
            institution=self.institution,
            last_service_date__lte=timezone.now().date() - timedelta(days=180)  # semiannual check
        )

        return {
            "recent_maintenance": [
                {
                    "vehicle": str(r.vehicle),
                    "maintenance_type": r.maintenance_type,
                    "performed_on": r.performed_on,
                    "next_due_date": r.next_due_date,
                    "cost": float(r.cost or 0),
                }
                for r in recent
            ],
            "vehicles_due_soon": [
                {
                    "vehicle": str(v),
                    "last_service": v.last_service_date,
                    "assigned_route": str(v.assigned_route) if v.assigned_route else None,
                    "notes": v.notes
                }
                for v in due_soon
            ]
        }

    def booking_statistics(self):
        """
        Booking status breakdown.
        """
        qs = TransportBooking.objects.filter(institution=self.institution)
        return {
            "total_bookings": qs.count(),
            "confirmed": qs.filter(status='confirmed').count(),
            "pending": qs.filter(status='pending').count(),
            "cancelled": qs.filter(status='cancelled').count(),
        }

    def weekly_trip_heatmap(self):
        """
        Trips per day over the past week.
        """
        today = timezone.now().date()
        days = [today - timedelta(days=i) for i in range(6, -1, -1)]

        heatmap = []
        for day in days:
            trip_count = TripLog.objects.filter(
                institution=self.institution,
                start_time__date=day
            ).count()
            heatmap.append({"date": day.strftime("%Y-%m-%d"), "trip_count": trip_count})

        return heatmap

    def driver_activity_report(self):
        """
        Summary of trips and performance by driver.
        """
        stats = TripLog.objects.filter(
            institution=self.institution,
            status='completed'
        ).values('driver__id', 'driver__user__first_name', 'driver__user__last_name').annotate(
            total_trips=Count('id'),
            total_duration=Sum('end_time') - Sum('start_time'),
        ).order_by('-total_trips')

        return [
            {
                "driver_id": s["driver__id"],
                "name": f"{s['driver__user__first_name']} {s['driver__user__last_name']}",
                "total_trips": s["total_trips"],
                "estimated_hours": round((s["total_duration"].total_seconds() / 3600), 2) if s["total_duration"] else 0
            }
            for s in stats
        ]
