from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from uuid import uuid4
import json

from .models import ChatRoom, ChatMessage, ChatRoomMembership, ChatMessage, MessageReadReceipt

User = get_user_model()


def get_or_create_dm(user1, user2):
    """
    Retrieve or create a DM room between two users.
    """
    existing = ChatRoom.objects.filter(
        room_type='dm',
        members=user1
    ).filter(members=user2).distinct()

    if existing.exists():
        return existing.first()

    room = ChatRoom.objects.create(room_type='dm', is_private=True)
    room.members.add(user1, user2)
    return room


def notify_new_message(message):
    """
    Push new message event via Redis/WebSocket.
    """
    channel_layer = get_channel_layer()
    payload = {
        "type": "new.message",
        "message_id": str(message.id),
        "room_id": str(message.room.id),
        "sender": message.sender.id,
        "content": message.content,
        "timestamp": message.created_at.isoformat(),
    }

    async_to_sync(channel_layer.group_send)(
        f"chatroom_{message.room.id}",
        {
            "type": "chat.message",
            "message": json.dumps(payload)
        }
    )


def notify_user_event(user_id, event_type, data):
    """
    Send user-specific event via WebSocket.
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            "type": event_type,
            "message": json.dumps(data)
        }
    )


def mark_read(user, message):
    """
    Create or update a read receipt.
    """
    receipt, created = MessageReadReceipt.objects.update_or_create(
        message=message,
        user=user,
        defaults={"read_at": timezone.now()}
    )
    return receipt


def pin_message(message):
    """
    Pin a message in a room.
    """
    pinned, created = ChatMessage.objects.get_or_create(
        message=message,
        room=message.room
    )
    return pinned


def soft_delete_message(message):
    """
    Soft-delete a message.
    """
    message.is_deleted = True
    message.deleted_at = timezone.now()
    message.save()


def generate_uuid():
    """
    Return a unique UUID string.
    """
    return str(uuid4())


def is_user_in_room(user, room):
    return ChatRoomMembership.objects.filter(user=user, room=room).exists()
