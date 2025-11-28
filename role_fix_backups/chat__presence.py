from django.utils import timezone
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async
from .models import ChatStatus

User = get_user_model()

ONLINE_USERS = set()  # Optional: in-memory cache for fast access


@sync_to_async
def mark_user_online(user):
    """
    Mark user as online and update ChatStatus model.
    """
    status, _ = ChatStatus.objects.get_or_create(user=user)
    status.is_online = True
    status.save(update_fields = ['is_online'])
    ONLINE_USERS.add(user.id)


@sync_to_async
def mark_user_offline(user):
    """
    Mark user as offline and update last_seen.
    """
    try:
        status = ChatStatus.objects.get(user=user)
        status.is_online = False
        status.last_seen = timezone.now()
        status.save(update_fields = ['is_online', 'last_seen'])
        ONLINE_USERS.discard(user.id)
    except ChatStatus.DoesNotExist:
        pass


@sync_to_async
def get_online_users():
    """
    Return list of online user IDs.
    """
    return list(ChatStatus.objects.filter(is_online=True).values_list('user_id', flat=True))


@sync_to_async
def get_last_seen(user):
    """
    Get a user's last seen timestamp.
    """
    try:
        return ChatStatus.objects.get(user=user).last_seen
    except ChatStatus.DoesNotExist:
        return None
