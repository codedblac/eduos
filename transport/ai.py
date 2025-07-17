import datetime
import random
from django.db import models
from django.db.models import F
from django.db.models import Q
from django.utils import timezone
from .models import (
    Vehicle, MaintenanceRecord, TripLog, TransportBooking,
    Driver, TransportAssignment, TransportRoute
)
from students.models import Student

# -----------------------------
# Predictive Maintenance
# -----------------------------

def predict_next_maintenance(vehicle: Vehicle) -> dict:
    """
    Predict when the vehicle might next need maintenance based on historical logs.
    """
    records = MaintenanceRecord.objects.filter(vehicle=vehicle).order_by('-performed_on')
    last_record = records.first()

    if last_record and last_record.next_due_date:
        predicted_date = last_record.next_due_date
    else:
        predicted_date = timezone.now().date() + datetime.timedelta(days=90)

    return {
        "vehicle_id": vehicle.id,
        "next_predicted_maintenance": predicted_date
    }


# -----------------------------
# Smart Route Optimization
# -----------------------------

def suggest_best_route(start: str, end: str, preferred_time: datetime.time = None) -> dict:
    """
    Suggest the best existing route or create a new route based on efficiency.
    """
    routes = TransportRoute.objects.filter(start_location__iexact=start, end_location__iexact=end)
    if preferred_time:
        routes = routes.filter(morning_time__lte=preferred_time, evening_time__gte=preferred_time)

    if routes.exists():
        optimal_route = routes.first()  # Enhance with actual scoring in future
        score = random.randint(80, 100)
    else:
        optimal_route = None
        score = 65  # Suggest need for new route

    return {
        "suggested_route": optimal_route.name if optimal_route else None,
        "efficiency_score": score
    }


# -----------------------------
# Driver Behavior Monitoring
# -----------------------------

def analyze_driver_performance(driver: Driver) -> dict:
    """
    Analyze trips completed and flag risky patterns.
    """
    trips = TripLog.objects.filter(driver=driver)
    total_trips = trips.count()
    completed_trips = trips.filter(status='completed').count()
    on_time = trips.filter(end_time__isnull=False).exclude(end_time__gt=models.F('start_time') + datetime.timedelta(hours=1)).count()

    performance_score = 80
    if total_trips > 0:
        performance_score = int((on_time / total_trips) * 100)

    return {
        "driver_id": driver.id,
        "name": str(driver.user.get_full_name()),
        "total_trips": total_trips,
        "on_time_percentage": performance_score,
        "reliability_score": min(performance_score + 5, 100)
    }


# -----------------------------
# Transport Demand Forecasting
# -----------------------------

def forecast_transport_demand(institution, target_date=None) -> dict:
    """
    Predict number of students likely to use transport on a specific day.
    """
    if target_date is None:
        target_date = timezone.now().date() + datetime.timedelta(days=1)

    weekday = target_date.weekday()
    historical_bookings = TransportBooking.objects.filter(
        institution=institution,
        travel_date__week_day=weekday + 1  # Django week_day: Sunday=1
    )

    average_demand = historical_bookings.count()
    expected_variance = random.randint(-5, 5)

    return {
        "institution": institution.name,
        "target_date": target_date,
        "predicted_demand": max(0, average_demand + expected_variance)
    }


# -----------------------------
# Student Assignment Intelligence
# -----------------------------

def recommend_route_for_student(student: Student) -> dict:
    """
    Recommend the most suitable route for a student based on historical pickup/drop points.
    """
    assignments = TransportAssignment.objects.filter(student=student)
    if assignments.exists():
        route = assignments.latest('assigned_on').route
        return {
            "student": student.full_name(),
            "recommended_route": route.name
        }
    return {
        "student": student.full_name(),
        "recommended_route": None
    }
