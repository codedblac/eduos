from django.shortcuts import render

# Create your views here.
from rest_framework import generics, viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import (
    ChatRoom, ChatMessage, MessageReadReceipt, MessageEditHistory,
    ChannelAnnouncement, MediaAttachment, MessageReaction, ChatRoomMembership
)
from .serializers import (
    ChatRoomSerializer, ChatMessageSerializer, MessageEditHistorySerializer,
    ReadReceiptSerializer, ChannelAnnouncementSerializer,
    MediaAttachmentSerializer, MessageReactionSerializer
)
from .permissions import IsRoomMember, IsSenderOrReadOnly


class ChatRoomViewSet(viewsets.ModelViewSet):
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(members=self.request.user)

    def perform_create(self, serializer):
        room = serializer.save(created_by=self.request.user)
        ChatRoomMembership.objects.create(user=self.request.user, room=room, primary_role='admin')

    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        room = self.get_object()
        room.is_archived = True
        room.save()
        return Response({'status': 'archived'})


class ChatMessageViewSet(viewsets.ModelViewSet):
    serializer_class = ChatMessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsRoomMember]

    def get_queryset(self):
        room_id = self.kwargs['room_id']
        return ChatMessage.objects.filter(room_id=room_id, is_deleted=False)

    def perform_create(self, serializer):
        room = get_object_or_404(ChatRoom, id=self.kwargs['room_id'])
        serializer.save(sender=self.request.user, room=room)

    @action(detail=True, methods=['post'], permission_classes=[IsSenderOrReadOnly])
    def edit(self, request, room_id=None, pk=None):
        message = self.get_object()
        serializer = MessageEditSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        MessageEditHistory.objects.create(message=message, content=message.content)
        message.content = serializer.validated_data['content']
        message.edited_at = timezone.now()
        message.save()
        return Response(ChatMessageSerializer(message).data)

    @action(detail=True, methods=['post'], permission_classes=[IsSenderOrReadOnly])
    def soft_delete(self, request, room_id=None, pk=None):
        message = self.get_object()
        message.is_deleted = True
        message.delete_reason = request.data.get("reason", "")
        message.save()
        return Response({"status": "deleted"})


class ReadReceiptView(generics.CreateAPIView):
    serializer_class = ReadReceiptSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        message = get_object_or_404(ChatMessage, pk=self.kwargs['message_id'])
        serializer.save(message=message, user=self.request.user)


class AnnouncementViewSet(viewsets.ModelViewSet):
    serializer_class = ChannelAnnouncementSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChannelAnnouncement.objects.filter(room__members=self.request.user)

    def perform_create(self, serializer):
        serializer.save(posted_by=self.request.user)


class ReactionViewSet(viewsets.ModelViewSet):
    serializer_class = MessageReactionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageReaction.objects.filter(user=self.request.user)


class AttachmentViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAttachmentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MediaAttachment.objects.filter(message__room__members=self.request.user)
