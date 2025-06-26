# constants.py

# Room Types
ROOM_TYPES = [
    ('dm', 'Direct Message'),
    ('group', 'Group Chat'),
    ('channel', 'Broadcast Channel'),
    ('community', 'Community'),
]

ROOM_TYPE_DICT = dict(ROOM_TYPES)

# Roles (Advanced control for future)
ROOM_ROLES = [
    ('member', 'Member'),
    ('admin', 'Admin'),
    ('moderator', 'Moderator'),
    ('guest', 'Guest'),
]

ROOM_ROLE_DICT = dict(ROOM_ROLES)

# Message Statuses
MESSAGE_STATUSES = [
    ('sent', 'Sent'),
    ('delivered', 'Delivered'),
    ('seen', 'Seen'),
]

MESSAGE_STATUS_DICT = dict(MESSAGE_STATUSES)

# Attachment Types
ATTACHMENT_TYPES = [
    ('image', 'Image'),
    ('video', 'Video'),
    ('audio', 'Audio'),
    ('document', 'Document'),
    ('sticker', 'Sticker'),
    ('gif', 'GIF'),
    ('voice', 'Voice'),
]

ATTACHMENT_TYPE_DICT = dict(ATTACHMENT_TYPES)

# Reactions (you can extend or limit this list as needed)
DEFAULT_REACTIONS = ['👍', '❤️', '😂', '🎉', '😮', '😢', '😡']

# System Bot Constants
SYSTEM_BOT_USERNAME = "EduOSBot"
SYSTEM_BOT_USER_ID = "system_bot"  # If using a fixed UUID or User instance

# Default Expiry (for auto-deletion)
DEFAULT_MESSAGE_EXPIRY_DAYS = 30

# WebSocket Message Types
WS_TYPE_MESSAGE = "message"
WS_TYPE_TYPING = "typing"
WS_TYPE_SYSTEM = "system"
WS_TYPE_JOIN = "join"
WS_TYPE_LEAVE = "leave"
WS_TYPE_EDIT = "edit"
WS_TYPE_DELETE = "delete"
WS_TYPE_PRESENCE = "presence"

# Redis presence key template
PRESENCE_REDIS_KEY = "chat:presence:{user_id}"

# Search
SEARCH_INDEX_NAME = "chat_messages"
