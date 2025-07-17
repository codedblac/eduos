from celery import shared_task
from django.utils import timezone
from .models import ChatMessage, ChatRoom, ChatStatus, MuteRoom, ChatbotResponse
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task
def notify_new_message(message_id):
    """
    Trigger WebSocket or Push Notification for a new message.
    """
    from .utils import notify_room_users  # assumes this exists or is to be created
    notify_room_users(message_id)
    return f"Notification triggered for message {message_id}"


@shared_task
def auto_delete_expired_messages():
    """
    Periodic task to delete expired messages.
    """
    now = timezone.now()
    expired = ChatMessage.objects.filter(expires_at__lte=now, is_deleted=False)
    count = expired.update(is_deleted=True, delete_reason="Expired by system")
    return f"{count} messages auto-deleted"


@shared_task
def reset_inactive_users_status():
    """
    Sets user online status to offline if last_seen is too old.
    """
    threshold = timezone.now() - timezone.timedelta(minutes=10)
    updated = ChatStatus.objects.filter(is_online=True, last_seen__lt=threshold).update(is_online=False)
    return f"{updated} users set to offline"


@shared_task
def clean_muted_rooms():
    """
    Remove mute entries that have expired.
    """
    now = timezone.now()
    removed = MuteRoom.objects.filter(muted_until__lte=now).delete()
    return f"{removed[0]} mute entries removed"


@shared_task
def respond_to_bot_trigger(message_id):
    """
    Check if a message triggers a chatbot response.
    """
    try:
        message = ChatMessage.objects.get(id=message_id)
        match = ChatbotResponse.objects.filter(trigger_text__iexact=message.content.strip()).first()
        if match:
            ChatMessage.objects.create(
                room=message.room,
                sender=None,  # or system bot user
                content=match.response_text,
                status='sent'
            )
            return f"Bot responded to message {message_id}"
    except ChatMessage.DoesNotExist:
        return f"Message {message_id} not found"
    return f"No bot response triggered for message {message_id}"
