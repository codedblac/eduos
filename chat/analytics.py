from django.db.models import Count, Q, Avg, Max, Min
from django.utils import timezone
from datetime import timedelta
from .models import ChatRoom, ChatMessage, ChatRoomMembership, MessageReaction, ChatStatus
from accounts.models import CustomUser


# 1. Total messages per room
def get_message_counts_per_room():
    return ChatRoom.objects.annotate(
        total_messages=Count('chatmessage')
    ).values('id', 'name', 'total_messages')


# 2. Active users in the last X minutes
def get_active_users(minutes=5):
    since = timezone.now() - timedelta(minutes=minutes)
    return ChatStatus.objects.filter(
        Q(is_online=True) | Q(last_seen__gte=since)
    ).select_related('user')


# 3. Top contributors (by message count)
def get_top_senders(limit=10):
    return CustomUser.objects.annotate(
        message_count=Count('chatmessage')
    ).order_by('-message_count')[:limit]


# 4. Message volume over time (daily)
def get_daily_message_volume(days=7):
    since = timezone.now() - timedelta(days=days)
    return ChatMessage.objects.filter(created_at__gte=since).extra(
        select={'day': "DATE(created_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')


# 5. Most active rooms by number of messages
def get_most_active_rooms(limit=5):
    return ChatRoom.objects.annotate(
        message_count=Count('chatmessage')
    ).order_by('-message_count')[:limit]


# 6. Emoji reaction frequency
def get_emoji_usage():
    return MessageReaction.objects.values('emoji').annotate(
        count=Count('id')
    ).order_by('-count')


# 7. New rooms created over time
def get_room_creation_trend(days=30):
    since = timezone.now() - timedelta(days=days)
    return ChatRoom.objects.filter(created_at__gte=since).extra(
        select={'day': "DATE(created_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')


# 8. Read vs Unread ratio
def get_read_unread_ratio():
    total = ChatMessage.objects.count()
    seen = ChatMessage.objects.filter(status='seen').count()
    return {
        'total': total,
        'seen': seen,
        'unseen': total - seen,
        'seen_percentage': round((seen / total) * 100, 2) if total else 0
    }


# 9. Average messages per user per day
def get_avg_messages_per_user_per_day(days=7):
    since = timezone.now() - timedelta(days=days)
    total_msgs = ChatMessage.objects.filter(created_at__gte=since).count()
    user_count = CustomUser.objects.count()
    return round(total_msgs / (user_count * days), 2) if user_count else 0


# 10. Dormant users (joined but not sent messages)
def get_dormant_users():
    return CustomUser.objects.annotate(
        msg_count=Count('chatmessage')
    ).filter(msg_count=0)


# 11. Participation trends
def get_participation_trend(days=14):
    since = timezone.now() - timedelta(days=days)
    return ChatRoomMembership.objects.filter(joined_at__gte=since).extra(
        select={'day': "DATE(joined_at)"}
    ).values('day').annotate(count=Count('id')).order_by('day')

