from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Channel:
    """Represents a Telegram channel or group managed by MLJCM"""
    id: int
    chat_id: int
    title: str
    type: str  # 'channel' or 'group'
    added_by: int
    added_at: datetime
    linked_chat_id: Optional[int] = None
    post_to_linked: bool = False

@dataclass
class ChannelAdmin:
    """RBAC representation connecting users to channels as managers"""
    id: int
    channel_id: int
    user_id: int
    role: str  # 'owner', 'admin'
    added_at: datetime

@dataclass
class ContentPost:
    """Represents a piece of content (like a job format or rules list) saved by the admin"""
    id: int
    title: str
    body: str
    created_by: int
    created_at: datetime
    updated_at: datetime

@dataclass
class Schedule:
    """Represents a scheduling rule for a ContentPost into a Channel"""
    id: int
    content_id: int
    channel_id: int
    interval_hours: float
    start_time: str  # e.g. "12:00"
    timezone: str    # e.g. "Africa/Lagos" (WAT default)
    is_active: bool
    repeat_until: Optional[datetime]
    last_posted_at: Optional[datetime]
    created_at: datetime
