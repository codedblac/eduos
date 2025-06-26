from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    ChatRoom, ChatRoomMembership, ChatMessage, MediaAttachment, 
    MessageReaction, ChatbotResponse, ChatSetting, ChatStatus, 
    MuteRoom, MessageEditHistory, PinnedMessage, ReadReceipt,
    ChannelAnnouncement
)

User = get_user_model()

# ========== USER SERIALIZER (light) ==========
class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email')


# ========== CHAT ROOM ==========
class ChatRoomSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)
    member_ids = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)

    class Meta:
        model = ChatRoom
        fields = '__all__'

    def create(self, validated_data):
        members = validated_data.pop('member_ids', [])
        room = ChatRoom.objects.create(**validated_data)
        for user in members:
            ChatRoomMembership.objects.create(user=user, room=room)
        return room


# ========== CHAT ROOM MEMBERSHIP ==========
class ChatRoomMembershipSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = ChatRoomMembership
        fields = '__all__'


# ========== MESSAGE ==========
class ChatMessageSerializer(serializers.ModelSerializer):
    sender = UserMiniSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ChatMessage
        fields = '__all__'

    def get_attachments(self, obj):
        return MediaAttachmentSerializer(obj.attachments.all(), many=True).data

    def get_replies(self, obj):
        return ChatMessageSerializer(obj.replies.all(), many=True).data if obj.replies.exists() else []


# ========== MEDIA ==========
class MediaAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaAttachment
        fields = '__all__'


# ========== REACTION ==========
class MessageReactionSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = MessageReaction
        fields = '__all__'


# ========== PINNED ==========
class PinnedMessageSerializer(serializers.ModelSerializer):
    message = ChatMessageSerializer(read_only=True)

    class Meta:
        model = PinnedMessage
        fields = '__all__'


# ========== ANNOUNCEMENT ==========
class ChannelAnnouncementSerializer(serializers.ModelSerializer):
    created_by = UserMiniSerializer(read_only=True)

    class Meta:
        model = ChannelAnnouncement
        fields = '__all__'


# ========== EDIT HISTORY ==========
class MessageEditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageEditHistory
        fields = '__all__'


# ========== READ RECEIPTS ==========
class ReadReceiptSerializer(serializers.ModelSerializer):
    user = UserMiniSerializer(read_only=True)

    class Meta:
        model = ReadReceipt
        fields = '__all__'


# ========== SETTINGS ==========
class ChatSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatSetting
        fields = '__all__'


class ChatStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatStatus
        fields = '__all__'


class MuteRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = MuteRoom
        fields = '__all__'


# ========== BOT ==========
class ChatbotResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotResponse
        fields = '__all__'
