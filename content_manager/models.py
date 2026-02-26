from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Channel:
    id: int
    chat_id: int
    title: str
    type: str
    added_by: int
    added_at: datetime
    linked_chat_id: Optional[int] = None
    post_to_linked: bool = False

@dataclass
class ChannelAdmin:
    id: int
    channel_id: int
    user_id: int
    role: str
    added_at: datetime

@dataclass
class BotPersona:
    id: int
    channel_id: int
    bot_name: str
    greeting: str
    sign_off: str
    created_by: int

@dataclass
class ContentPost:
    id: int
    title: str
    body: str
    created_by: int
    created_at: datetime
    updated_at: datetime

@dataclass
class Schedule:
    id: int
    content_id: int
    channel_id: int
    interval_hours: float
    start_time: str
    timezone: str
    is_active: bool
    repeat_until: Optional[datetime]
    last_posted_at: Optional[datetime]
    created_at: datetime
