from django.db.models import Count, Avg
from .models import RoomAllocation, HostelLeaveRequest, HostelInspection, HostelViolation


def hostel_analytics_overview(institution):
    return {
        "total_allocations": RoomAllocation.objects.filter(institution=institution).count(),
        "active_allocations": RoomAllocation.objects.filter(institution=institution, allocated_until__gte=None).count(),
        "students_on_leave": HostelLeaveRequest.objects.filter(institution=institution, status="approved").count(),
        "violations_reported": HostelViolation.objects.filter(institution=institution).count(),
        "inspections_conducted": HostelInspection.objects.filter(institution=institution).count()
    }


def violations_by_type(institution):
    return HostelViolation.objects.filter(institution=institution).values("violation_type").annotate(count=Count("id")).order_by("-count")


def leave_trends(institution):
    return HostelLeaveRequest.objects.filter(institution=institution).extra({
        'month': "strftime('%%Y-%%m', leave_date)"
    }).values('month').annotate(total=Count('id')).order_by('month')


def inspection_scores(institution):
    return HostelInspection.objects.filter(institution=institution).values('room__name').annotate(avg_score=Avg('score')).order_by('-avg_score')
