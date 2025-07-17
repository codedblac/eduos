import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage
from .tasks import notify_new_message
from .signals import notify_new_message as signal_notify_new_message  # NEW
from .presence import mark_user_online, mark_user_offline  # NEW

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f"chat_{self.room_id}"
        self.user = self.scope["user"]

        # Join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Mark user as online (updates ChatStatus)
        await mark_user_online(self.user)

        # Notify others in the room (system message)
        await self.send_join_message()

    async def disconnect(self, close_code):
        # Leave group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Mark user as offline (updates ChatStatus)
        await mark_user_offline(self.user)

        # Optional: system leave message
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{self.user.username} left the chat."
            }
        )

    async def receive(self, text_data):
        """
        Handles data from WebSocket client.
        """
        data = json.loads(text_data)
        msg_type = data.get("type", "message")
        message = data.get("message", "")
        reply_to = data.get("reply_to", None)

        if msg_type == "typing":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "typing_indicator",
                    "user_id": self.user.id,
                    "username": self.user.username,
                }
            )

        elif msg_type == "message":
            # Save to DB
            msg_obj = await self.save_message(message, reply_to)

            # Trigger notifications
            await database_sync_to_async(notify_new_message)(msg_obj.id)

            # Broadcast to group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message_id": str(msg_obj.id),
                    "user_id": self.user.id,
                    "username": self.user.username,
                    "content": msg_obj.content,
                    "timestamp": msg_obj.created_at.isoformat(),
                    "reply_to": reply_to,
                }
            )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "message",
            "message_id": event["message_id"],
            "user_id": event["user_id"],
            "username": event["username"],
            "content": event["content"],
            "timestamp": event["timestamp"],
            "reply_to": event.get("reply_to"),
        }))

    async def typing_indicator(self, event):
        await self.send(text_data=json.dumps({
            "type": "typing",
            "user_id": event["user_id"],
            "username": event["username"]
        }))

    async def send_join_message(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "system_message",
                "message": f"{self.user.username} joined the chat."
            }
        )

    async def system_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "system",
            "message": event["message"]
        }))

    @database_sync_to_async
    def save_message(self, content, reply_to_id):
        room = ChatRoom.objects.get(id=self.room_id)
        reply_to = None
        if reply_to_id:
            try:
                reply_to = ChatMessage.objects.get(id=reply_to_id)
            except ChatMessage.DoesNotExist:
                reply_to = None
        return ChatMessage.objects.create(
            room=room,
            sender=self.user,
            content=content,
            reply_to=reply_to
        )
