from datetime import timedelta
from django.utils import timezone
from .models import RoomAllocation, HostelLeaveRequest, HostelInspection
from students.models import Student
from accounts.models import CustomUser
from django.db.models import Count

class HostelAIAssistant:
    """
    AI Assistant for managing hostel tasks, student habits, and forecasting logistics.
    """

    @staticmethod
    def predict_overcapacity_risks(institution):
        allocations = RoomAllocation.objects.filter(institution=institution)
        overbooked_rooms = allocations.values('room').annotate(count=Count('id')).filter(count__gt=1)
        return overbooked_rooms

    @staticmethod
    def students_frequently_on_leave(institution, threshold=3):
        recent_leaves = HostelLeaveRequest.objects.filter(
            institution=institution,
            leave_date__gte=timezone.now() - timedelta(days=90)
        )
        student_counts = recent_leaves.values('student').annotate(count=Count('id')).filter(count__gte=threshold)
        return student_counts

    @staticmethod
    def generate_cleaning_schedule(institution):
        students = Student.objects.filter(institution=institution)
        rooms = RoomAllocation.objects.filter(institution=institution)
        schedule = {}
        for room in rooms:
            occupants = students.filter(roomallocation__room=room)
            schedule[room.name] = [s.user.get_full_name() for s in occupants]
        return schedule

    @staticmethod
    def inspection_reminders_due():
        today = timezone.now().date()
        inspections = HostelInspection.objects.filter(date=today)
        return inspections

    @staticmethod
    def suggest_reallocation(institution):
        soon_expiring = RoomAllocation.objects.filter(
            institution=institution,
            allocated_until__lte=timezone.now().date() + timedelta(days=5)
        )
        return soon_expiring
