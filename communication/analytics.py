from django.db.models import Count, Q
from .models import CommunicationAnnouncement, CommunicationReadLog, CommunicationTarget


def announcement_engagement_summary():
    """
    Return a dictionary summarizing total announcements, read counts, and unread counts.
    """
    total_announcements = CommunicationAnnouncement.objects.count()
    total_reads = CommunicationReadLog.objects.count()
    total_users = CommunicationTarget.objects.values('user').distinct().count()

    return {
        'total_announcements': total_announcements,
        'total_reads': total_reads,
        'total_users': total_users,
        'total_unread': (total_users * total_announcements) - total_reads,
    }


def top_announcements_by_views(limit=5):
    """
    Return the top N announcements by views.
    """
    return CommunicationAnnouncement.objects.order_by('-total_views')[:limit]


def announcements_by_priority():
    """
    Return a count of announcements grouped by priority.
    """
    return CommunicationAnnouncement.objects.values('priority').annotate(count=Count('id')).order_by('-count')


def read_rate_per_announcement():
    """
    Return a list of announcements with their read rates.
    """
    results = []
    for announcement in CommunicationAnnouncement.objects.all():
        total_targets = CommunicationTarget.objects.filter(announcement=announcement).count()
        total_reads = CommunicationReadLog.objects.filter(announcement=announcement).count()
        read_rate = (total_reads / total_targets * 100) if total_targets > 0 else 0
        results.append({
            'announcement': announcement.title,
            'read_rate_percent': round(read_rate, 2),
        })
    return results


def unread_users_for_announcement(announcement):
    """
    Return list of users who haven't read a specific announcement.
    """
    target_users = CommunicationTarget.objects.filter(announcement=announcement).values_list('user', flat=True)
    read_users = CommunicationReadLog.objects.filter(announcement=announcement).values_list('user', flat=True)
    unread_user_ids = set(target_users) - set(read_users)
    return unread_user_ids
