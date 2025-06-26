from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json


def notify_new_message(message):
    """
    Broadcast new message to WebSocket group.
    """
    channel_layer = get_channel_layer()
    room_group_name = f"chat_{str(message.room.id)}"

    async_to_sync(channel_layer.group_send)(
        room_group_name,
        {
            "type": "chat.message",
            "message_id": str(message.id),
            "room_id": str(message.room.id),
            "sender": message.sender.username,
            "content": message.content,
            "timestamp": message.created_at.isoformat(),
        }
    )


def join_room_as_bot(room):
    """
    Add a system bot user to the room automatically.
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()

    bot_user, _ = User.objects.get_or_create(
        username="eduos_bot",
        defaults={"is_active": True, "email": "bot@eduos.com"}
    )

    room.members.add(bot_user)
