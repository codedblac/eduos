from .models import ChatbotResponse, ChatMessage, ChatRoom
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# A special system user for bot messages (can be seeded during migration or startup)
SYSTEM_BOT_USERNAME = "systembot"

def get_or_create_system_bot():
    return User.objects.get_or_create(
        username=SYSTEM_BOT_USERNAME,
        defaults={"email": "bot@eduos.ai", "is_active": True, "is_staff": False}
    )[0]


def handle_bot_response(room: ChatRoom, user_input: str) -> ChatMessage | None:
    """
    Checks if the user_input triggers any known bot response.
    If found, sends it as a system message.
    """
    bot_user = get_or_create_system_bot()

    # Match the input with available chatbot triggers
    responses = ChatbotResponse.objects.all()

    for response in responses:
        triggers = [t.strip().lower() for t in response.trigger_text.split(",")]
        if any(trigger in user_input.lower() for trigger in triggers):
            return ChatMessage.objects.create(
                room=room,
                sender=bot_user,
                content=response.response_text,
                status="sent",
                created_at=timezone.now(),
            )

    return None
