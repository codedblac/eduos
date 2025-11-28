from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    ChatRoom, ChatRoomMembership, ChatMessage, MessageEditHistory,
    MessageReadReceipt, ChannelAnnouncement, MediaAttachment,
    MessageReaction, ChatbotResponse, ChatSetting, ChatStatus, MuteRoom
)


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'room_type', 'is_private', 'institution', 'created_by', 'is_archived', 'created_at')
    list_filter = ('room_type', 'is_private', 'is_archived', 'institution')
    search_fields = ('name', 'created_by__username')
    autocomplete_fields = ('created_by', 'institution')
    readonly_fields = ('created_at',)


@admin.register(ChatRoomMembership)
class ChatRoomMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'primary_role', 'joined_at', 'last_seen')
    list_filter = ('primary_role',)
    search_fields = ('user__username', 'room__name')
    autocomplete_fields = ('user', 'room')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'room', 'status', 'is_pinned', 'is_deleted', 'created_at', 'edited_at')
    list_filter = ('status', 'is_pinned', 'is_deleted')
    search_fields = ('content', 'sender__username', 'room__name')
    autocomplete_fields = ('sender', 'room', 'reply_to')
    readonly_fields = ('created_at', 'updated_at', 'edited_at')


@admin.register(MessageEditHistory)
class MessageEditHistoryAdmin(admin.ModelAdmin):
    list_display = ('message', 'edited_at')
    search_fields = ('message__content',)
    autocomplete_fields = ('message',)


@admin.register(MessageReadReceipt)
class MessageReadReceiptAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'seen_at')
    autocomplete_fields = ('message', 'user')


@admin.register(ChannelAnnouncement)
class ChannelAnnouncementAdmin(admin.ModelAdmin):
    list_display = ('room', 'posted_by', 'posted_at')
    search_fields = ('room__name', 'content')
    autocomplete_fields = ('room', 'posted_by')


@admin.register(MediaAttachment)
class MediaAttachmentAdmin(admin.ModelAdmin):
    list_display = ('message', 'attachment_type', 'uploaded_at')
    list_filter = ('attachment_type',)
    autocomplete_fields = ('message',)


@admin.register(MessageReaction)
class MessageReactionAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'emoji', 'reacted_at')
    search_fields = ('emoji', 'user__username', 'message__content')
    autocomplete_fields = ('message', 'user')


@admin.register(ChatbotResponse)
class ChatbotResponseAdmin(admin.ModelAdmin):
    list_display = ('trigger_text', 'response_text', 'created_at')
    search_fields = ('trigger_text', 'response_text')
    readonly_fields = ('created_at',)


@admin.register(ChatSetting)
class ChatSettingAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online_visible', 'read_receipts_enabled', 'last_seen_enabled')
    autocomplete_fields = ('user',)


@admin.register(ChatStatus)
class ChatStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_online', 'last_seen')
    autocomplete_fields = ('user',)


@admin.register(MuteRoom)
class MuteRoomAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'muted_until')
    autocomplete_fields = ('user', 'room')
