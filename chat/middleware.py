import datetime
from django.utils.deprecation import MiddlewareMixin
from django.utils.timezone import now
from django.conf import settings
from django.urls import resolve
from chat.models import ChatStatus

User = settings.AUTH_USER_MODEL


class ChatPresenceMiddleware(MiddlewareMixin):
    """
    Middleware to update user online status for chat activity.
    Only applies if user is authenticated.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return

        try:
            # Optionally restrict to chat-related views
            current_view = resolve(request.path_info).app_name
            if current_view == "chat":
                ChatStatus.objects.update_or_create(
                    user=request.user,
                    defaults={"is_online": True, "last_seen": now()}
                )
        except Exception:
            pass  # Avoid breaking the app for non-chat views


class ChatActivityLoggerMiddleware(MiddlewareMixin):
    """
    Optional: Logs chat-related requests for auditing/debugging.
    """

    def process_request(self, request):
        if request.user.is_authenticated and "chat" in request.path:
            print(f"[ChatLog] {request.user.username} accessed {request.path} at {datetime.datetime.now()}")
