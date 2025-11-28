import django_filters
from django.db.models import Q
from .models import ChatRoom, ChatMessage, ChatRoomMembership, MessageReaction


class ChatRoomFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    room_type = django_filters.ChoiceFilter(choices=ChatRoom.ROOM_TYPES)
    is_private = django_filters.BooleanFilter()
    created_by = django_filters.NumberFilter(field_name='created_by__id')
    institution = django_filters.NumberFilter(field_name='institution__id')
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = ChatRoom
        fields = [ 'room_type', 'is_private', 'created_by', 'institution', 'created_at']


class ChatMessageFilter(django_filters.FilterSet):
    room = django_filters.UUIDFilter(field_name='room__id')
    sender = django_filters.NumberFilter(field_name='sender__id')
    content = django_filters.CharFilter(method='filter_content')
    status = django_filters.ChoiceFilter(choices=ChatMessage.STATUS_CHOICES)
    created_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = ChatMessage
        fields = ['room', 'sender', 'status', 'created_at']

    def filter_content(self, queryset, name, value):
        return queryset.filter(Q(content__icontains=value))


class ChatRoomMembershipFilter(django_filters.FilterSet):
    user = django_filters.NumberFilter(field_name='user__id')
    room = django_filters.UUIDFilter(field_name='room__id')
    is_admin = django_filters.BooleanFilter()
    joined_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = ChatRoomMembership
        fields = ['user', 'room', 'is_admin', 'joined_at']


class MessageReactionFilter(django_filters.FilterSet):
    message = django_filters.UUIDFilter(field_name='message__id')
    user = django_filters.NumberFilter(field_name='user__id')
    emoji = django_filters.CharFilter(lookup_expr='iexact')
    reacted_at = django_filters.DateFromToRangeFilter()

    class Meta:
        model = MessageReaction
        fields = ['message', 'user', 'emoji', 'reacted_at']
