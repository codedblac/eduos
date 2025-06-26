from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import (
    ChatRoomViewSet, ChatMessageViewSet, ReadReceiptView,
    AnnouncementViewSet, ReactionViewSet, AttachmentViewSet
)

# Top-level router for rooms
router = DefaultRouter()
router.register(r'rooms', ChatRoomViewSet, basename='chat-room')
router.register(r'announcements', AnnouncementViewSet, basename='announcements')
router.register(r'reactions', ReactionViewSet, basename='reactions')
router.register(r'attachments', AttachmentViewSet, basename='attachments')

# Nested router for messages under rooms
room_router = NestedDefaultRouter(router, r'rooms', lookup='room')
room_router.register(r'messages', ChatMessageViewSet, basename='chat-message')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(room_router.urls)),

    # Read receipts endpoint (non-viewset)
    path('messages/<uuid:message_id>/read/', ReadReceiptView.as_view(), name='message-read-receipt'),
]
