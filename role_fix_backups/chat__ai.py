import os
import openai
from django.conf import settings
from .models import ChatRoom
from django.contrib.auth import get_user_model
from .models import ChatMessage
from django.utils import timezone

User = get_user_model()

# Ensure you’ve set OPENAI_API_KEY in your Django settings or environment
openai.api_key = getattr(settings, "OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))

# Optional: You can seed a special AI bot user for attribution
AI_BOT_USERNAME = "aibot"

def get_or_create_ai_bot():
    """
    Returns a special system AI bot user.
    """
    return User.objects.get_or_create(
        username=AI_BOT_USERNAME,
        defaults={
            "email": "aibot@eduos.ai",
            "is_active": True,
            "is_staff": False,
        },
    )[0]


def ask_ai(prompt: str, context: str = "") -> str:
    """
    Sends prompt to OpenAI and returns response text.
    Extend this for your own LLM or model.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo" for cheaper/faster
            messages=[
                {'primary_role': "system", "content": context or "You are a helpful learning assistant for students."},
                {'primary_role': "user", "content": prompt}
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message["content"].strip()
    except Exception as e:
        return "🤖 Sorry, I couldn't process that right now."


def generate_ai_reply(room: ChatRoom, user_input: str) -> ChatMessage:
    """
    Triggers AI response and saves it as a message in the room.
    """
    ai_user = get_or_create_ai_bot()

    reply_text = ask_ai(user_input)

    ai_msg = ChatMessage.objects.create(
        room=room,
        sender=ai_user,
        content=reply_text,
        status="sent",
        created_at=timezone.now(),
    )

    return ai_msg
