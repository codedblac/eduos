from django.db import models
from django.conf import settings
from django.utils import timezone
from institutions.models import Institution
import uuid

User = settings.AUTH_USER_MODEL


class ChatRoom(models.Model):
    ROOM_TYPES = [
        ('dm', 'Direct Message'),
        ('group', 'Group Chat'),
        ('channel', 'Broadcast Channel'),
        ('community', 'Community'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, default='dm')
    members = models.ManyToManyField(User, through='ChatRoomMembership')
    is_private = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_rooms')
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, null=True, blank=True)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name or f"Room-{self.id}"


class ChatRoomMembership(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('member', 'Member'),
        ('guest', 'Guest'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    primary_role= models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'room')


class ChatMessage(models.Model):
    STATUS_CHOICES = [
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('seen', 'Seen'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='sent')
    reply_to = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='replies')
    is_pinned = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    delete_reason = models.TextField(blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(null=True, blank=True)
    forwarded_from = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='forwards')
    


    def __str__(self):
        return f"Message by {self.sender} in {self.room}"


class MessageEditHistory(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='edit_history')
    content = models.TextField()
    edited_at = models.DateTimeField(auto_now_add=True)


class MessageReadReceipt(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='read_receipts')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seen_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user')


class ChannelAnnouncement(models.Model):
    room = models.OneToOneField(ChatRoom, on_delete=models.CASCADE, related_name='announcement')
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    posted_at = models.DateTimeField(auto_now_add=True)


class MediaAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('sticker', 'Sticker'),
        ('gif', 'GIF'),
        ('voice', 'Voice Message'),
    ]

    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='chat/attachments/')
    attachment_type = models.CharField(max_length=20, choices=ATTACHMENT_TYPES)
    uploaded_at = models.DateTimeField(auto_now_add=True)


class MessageReaction(models.Model):
    message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='reactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=10)
    reacted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('message', 'user', 'emoji')


class ChatbotResponse(models.Model):
    trigger_text = models.CharField(max_length=255)
    response_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.trigger_text


class ChatSetting(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online_visible = models.BooleanField(default=True)
    read_receipts_enabled = models.BooleanField(default=True)
    custom_theme = models.CharField(max_length=50, blank=True)
    last_seen_enabled = models.BooleanField(default=True)


class ChatStatus(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_online = models.BooleanField(default=False)
    last_seen = models.DateTimeField(default=timezone.now)


class MuteRoom(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    muted_until = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'room')
