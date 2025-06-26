from rest_framework import permissions
from .models import ChatRoom, ChatRoomMembership


class IsRoomMember(permissions.BasePermission):
    """
    Allows access only to members of a chat room.
    """

    def has_object_permission(self, request, view, obj):
        # For ChatRoom object
        if isinstance(obj, ChatRoom):
            return ChatRoomMembership.objects.filter(room=obj, user=request.user).exists()

        # For related models like ChatMessage, PinnedMessage, etc. with .room
        if hasattr(obj, 'room'):
            return ChatRoomMembership.objects.filter(room=obj.room, user=request.user).exists()

        return False


class IsRoomAdminOrCreator(permissions.BasePermission):
    """
    Only room admins or the creator can perform write operations.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if isinstance(obj, ChatRoom):
            return obj.created_by == user or ChatRoomMembership.objects.filter(
                room=obj, user=user, is_admin=True
            ).exists()

        if hasattr(obj, 'room'):
            return obj.room.created_by == user or ChatRoomMembership.objects.filter(
                room=obj.room, user=user, is_admin=True
            ).exists()

        return False


class IsSenderOrReadOnly(permissions.BasePermission):
    """
    Only sender of a message can edit/delete it.
    Others can only read.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'sender', None) == request.user


class IsSelfOrReadOnly(permissions.BasePermission):
    """
    Used for user-specific settings or status. Only the user can modify.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return getattr(obj, 'user', None) == request.user


class IsBotOrAdmin(permissions.BasePermission):
    """
    Allow only admin or bot service to create/edit bot responses.
    """

    def has_permission(self, request, view):
        user = request.user
        return user.is_staff or user.is_superuser or getattr(user, 'is_bot', False)


class IsParticipantOfMessageRoom(permissions.BasePermission):
    """
    Checks if the user is part of the room a message belongs to.
    """

    def has_object_permission(self, request, view, obj):
        room = getattr(obj, 'room', None)
        if not room:
            return False
        return ChatRoomMembership.objects.filter(room=room, user=request.user).exists()


class CanMuteUnmuteRoom(permissions.BasePermission):
    """
    Users can mute/unmute rooms they are members of.
    """

    def has_permission(self, request, view):
        room_id = view.kwargs.get('room_id')
        if not room_id:
            return False
        return ChatRoomMembership.objects.filter(room_id=room_id, user=request.user).exists()


class IsRoomModerator(permissions.BasePermission):
    """
    Optional: Checks if user has a moderator role (if you later extend roles).
    """

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'room'):
            membership = ChatRoomMembership.objects.filter(room=obj.room, user=request.user).first()
            return getattr(membership, 'role', None) == 'moderator'
        return False
