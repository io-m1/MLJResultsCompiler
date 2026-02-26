import logging
import os
from contextlib import contextmanager
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy import create_engine, Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, BigInteger
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.pool import NullPool

from .models import Channel, ContentPost, Schedule, ChannelAdmin, BotPersona

logger = logging.getLogger(__name__)

Base = declarative_base()

class DBChannelAdmin(Base):
    __tablename__ = 'channel_admins'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), index=True)
    user_id = Column(BigInteger, index=True)
    role = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    channel = relationship("DBChannel", back_populates="admins")

    def to_dataclass(self) -> ChannelAdmin:
        return ChannelAdmin(
            id=self.id,
            channel_id=self.channel_id,
            user_id=self.user_id,
            role=self.role,
            added_at=self.added_at
        )

class DBBotPersona(Base):
    __tablename__ = 'bot_personas'
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), unique=True, index=True)
    bot_name = Column(String, nullable=False, default="MLJCM Bot")
    greeting = Column(Text, default="")
    sign_off = Column(Text, default="")
    created_by = Column(BigInteger, nullable=False)

    channel = relationship("DBChannel", back_populates="persona")

    def to_dataclass(self) -> BotPersona:
        return BotPersona(
            id=self.id,
            channel_id=self.channel_id,
            bot_name=self.bot_name or "MLJCM Bot",
            greeting=self.greeting or "",
            sign_off=self.sign_off or "",
            created_by=self.created_by
        )

class DBChannel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    title = Column(String)
    type = Column(String, default="channel")
    added_by = Column(BigInteger, nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    linked_chat_id = Column(BigInteger, nullable=True)
    post_to_linked = Column(Boolean, default=False)
    
    schedules = relationship("DBSchedule", back_populates="channel", cascade="all, delete-orphan")
    admins = relationship("DBChannelAdmin", back_populates="channel", cascade="all, delete-orphan")
    persona = relationship("DBBotPersona", back_populates="channel", uselist=False, cascade="all, delete-orphan")

    def to_dataclass(self) -> Channel:
        return Channel(
            id=self.id,
            chat_id=self.chat_id,
            title=self.title or "",
            type=self.type or "channel",
            added_by=self.added_by,
            added_at=self.added_at,
            linked_chat_id=self.linked_chat_id,
            post_to_linked=self.post_to_linked
        )


class DBContentPost(Base):
    __tablename__ = 'content_posts'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    created_by = Column(BigInteger, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    schedules = relationship("DBSchedule", back_populates="content", cascade="all, delete-orphan")

    def to_dataclass(self) -> ContentPost:
        return ContentPost(
            id=self.id,
            title=self.title,
            body=self.body,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class DBSchedule(Base):
    __tablename__ = 'schedules'
    id = Column(Integer, primary_key=True)
    content_id = Column(Integer, ForeignKey('content_posts.id'), nullable=False)
    channel_id = Column(Integer, ForeignKey('channels.id'), nullable=False)
    interval_hours = Column(Float, nullable=False)
    start_time = Column(String(5))
    timezone = Column(String(50), default="Africa/Lagos")
    is_active = Column(Boolean, default=True)
    repeat_until = Column(DateTime, nullable=True)
    last_posted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    content = relationship("DBContentPost", back_populates="schedules")
    channel = relationship("DBChannel", back_populates="schedules")

    def to_dataclass(self) -> Schedule:
        return Schedule(
            id=self.id,
            content_id=self.content_id,
            channel_id=self.channel_id,
            interval_hours=self.interval_hours,
            start_time=self.start_time or "",
            timezone=self.timezone or "Africa/Lagos",
            is_active=self.is_active,
            repeat_until=self.repeat_until,
            last_posted_at=self.last_posted_at,
            created_at=self.created_at
        )


class CMStorage:
    
    def __init__(self, db_url: Optional[str] = None):
        if not db_url:
            db_url = os.environ.get('DATABASE_URL')
            
        if not db_url:
            db_path = os.path.join(os.getcwd(), 'data', 'mljcm.db')
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            db_url = f"sqlite:///{db_path}"
            logger.info(f"MLJCM using local SQLite storage: {db_path}")
            self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            if db_url.startswith("postgres://"):
                db_url = db_url.replace("postgres://", "postgresql://", 1)
            logger.info("MLJCM using external PostgreSQL database")
            self.engine = create_engine(db_url, poolclass=NullPool)
            
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        
    @contextmanager
    def get_session(self):
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_channel(self, chat_id: int, title: str, chat_type: str, added_by: int) -> tuple[Optional[Channel], bool]:
        with self.get_session() as session:
            db_channel = session.query(DBChannel).filter(DBChannel.chat_id == chat_id).first()
            if db_channel:
                return db_channel.to_dataclass(), False
            
            db_channel = DBChannel(
                chat_id=chat_id,
                title=title,
                type=chat_type,
                added_by=added_by
            )
            session.add(db_channel)
            session.flush()
            
            admin = DBChannelAdmin(
                channel_id=db_channel.id,
                user_id=added_by,
                role='owner'
            )
            session.add(admin)
            session.flush()
            
            return db_channel.to_dataclass(), True

    def get_channel(self, channel_id: int) -> Optional[Channel]:
        with self.get_session() as session:
            db_channel = session.query(DBChannel).filter(DBChannel.id == channel_id).first()
            return db_channel.to_dataclass() if db_channel else None

    def get_all_channels(self, user_id: int) -> List[Channel]:
        with self.get_session() as session:
            query = session.query(DBChannel).join(DBChannelAdmin).filter(DBChannelAdmin.user_id == user_id)
            return [c.to_dataclass() for c in query.all()]
            
    def update_linked_chat(self, channel_id: int, linked_chat_id: Optional[int], post_to_linked: bool) -> bool:
        with self.get_session() as session:
            db_channel = session.query(DBChannel).filter(DBChannel.id == channel_id).first()
            if db_channel:
                db_channel.linked_chat_id = linked_chat_id
                db_channel.post_to_linked = post_to_linked
                return True
            return False

    def create_content(self, title: str, body: str, created_by: int) -> ContentPost:
        with self.get_session() as session:
            db_content = DBContentPost(
                title=title,
                body=body,
                created_by=created_by
            )
            session.add(db_content)
            session.flush()
            return db_content.to_dataclass()
            
    def get_content(self, content_id: int, user_id: Optional[int] = None) -> Optional[ContentPost]:
        with self.get_session() as session:
            query = session.query(DBContentPost).filter(DBContentPost.id == content_id)
            if user_id is not None:
                query = query.filter(DBContentPost.created_by == user_id)
            db_content = query.first()
            return db_content.to_dataclass() if db_content else None
            
    def get_all_content(self, user_id: Optional[int] = None) -> List[ContentPost]:
        with self.get_session() as session:
            query = session.query(DBContentPost)
            if user_id is not None:
                query = query.filter(DBContentPost.created_by == user_id)
            return [c.to_dataclass() for c in query.all()]

    def update_content(self, content_id: int, title: str, body: str) -> Optional[ContentPost]:
        with self.get_session() as session:
            db_content = session.query(DBContentPost).filter(DBContentPost.id == content_id).first()
            if not db_content:
                return None
            db_content.title = title
            db_content.body = body
            session.flush()
            return db_content.to_dataclass()

    def delete_content(self, content_id: int) -> bool:
        with self.get_session() as session:
            db_content = session.query(DBContentPost).filter(DBContentPost.id == content_id).first()
            if db_content:
                session.delete(db_content)
                return True
            return False

    def set_persona(self, channel_id: int, bot_name: str, greeting: str, sign_off: str, created_by: int) -> BotPersona:
        with self.get_session() as session:
            db_persona = session.query(DBBotPersona).filter(DBBotPersona.channel_id == channel_id).first()
            if db_persona:
                db_persona.bot_name = bot_name
                db_persona.greeting = greeting
                db_persona.sign_off = sign_off
            else:
                db_persona = DBBotPersona(
                    channel_id=channel_id,
                    bot_name=bot_name,
                    greeting=greeting,
                    sign_off=sign_off,
                    created_by=created_by
                )
                session.add(db_persona)
            session.flush()
            return db_persona.to_dataclass()

    def get_persona(self, channel_id: int) -> Optional[BotPersona]:
        with self.get_session() as session:
            db_persona = session.query(DBBotPersona).filter(DBBotPersona.channel_id == channel_id).first()
            return db_persona.to_dataclass() if db_persona else None

    def delete_persona(self, channel_id: int) -> bool:
        with self.get_session() as session:
            db_persona = session.query(DBBotPersona).filter(DBBotPersona.channel_id == channel_id).first()
            if db_persona:
                session.delete(db_persona)
                return True
            return False

    def create_schedule(self, content_id: int, channel_id: int, interval_hours: float, 
                        start_time: str, timezone: str, repeat_until: Optional[datetime] = None) -> Schedule:
        with self.get_session() as session:
            db_schedule = DBSchedule(
                content_id=content_id,
                channel_id=channel_id,
                interval_hours=interval_hours,
                start_time=start_time,
                timezone=timezone,
                repeat_until=repeat_until,
                is_active=True
            )
            session.add(db_schedule)
            session.flush()
            return db_schedule.to_dataclass()

    def get_all_schedules(self, user_id: Optional[int] = None, active_only: bool = False) -> List[Schedule]:
        with self.get_session() as session:
            query = session.query(DBSchedule)
            if user_id is not None:
                query = query.join(DBContentPost).filter(DBContentPost.created_by == user_id)
                
            if active_only:
                query = query.filter(DBSchedule.is_active == True)
            return [s.to_dataclass() for s in query.all()]
            
    def get_schedule(self, schedule_id: int) -> Optional[Schedule]:
        with self.get_session() as session:
            db_schedule = session.query(DBSchedule).filter(DBSchedule.id == schedule_id).first()
            return db_schedule.to_dataclass() if db_schedule else None

    def update_schedule_status(self, schedule_id: int, is_active: bool) -> bool:
        with self.get_session() as session:
            db_schedule = session.query(DBSchedule).filter(DBSchedule.id == schedule_id).first()
            if db_schedule:
                db_schedule.is_active = is_active
                return True
            return False
            
    def update_last_posted(self, schedule_id: int, time_posted: datetime) -> bool:
        with self.get_session() as session:
            db_schedule = session.query(DBSchedule).filter(DBSchedule.id == schedule_id).first()
            if db_schedule:
                db_schedule.last_posted_at = time_posted
                return True
            return False

    def delete_schedule(self, schedule_id: int) -> bool:
        with self.get_session() as session:
            db_schedule = session.query(DBSchedule).filter(DBSchedule.id == schedule_id).first()
            if db_schedule:
                session.delete(db_schedule)
                return True
            return False

    def get_dashboard_stats(self, user_id: int) -> Dict[str, Any]:
        with self.get_session() as session:
            content_count = session.query(DBContentPost).filter(DBContentPost.created_by == user_id).count()
            recent_content = session.query(DBContentPost).filter(
                DBContentPost.created_by == user_id
            ).order_by(DBContentPost.created_at.desc()).limit(5).all()
            
            channels = session.query(DBChannel).join(DBChannelAdmin).filter(
                DBChannelAdmin.user_id == user_id
            ).all()
            
            total_schedules = session.query(DBSchedule).join(DBContentPost).filter(
                DBContentPost.created_by == user_id
            ).count()
            active_schedules = session.query(DBSchedule).join(DBContentPost).filter(
                DBContentPost.created_by == user_id, DBSchedule.is_active == True
            ).count()

            channel_personas = []
            for ch in channels:
                persona = session.query(DBBotPersona).filter(DBBotPersona.channel_id == ch.id).first()
                channel_personas.append({
                    "channel": ch.to_dataclass(),
                    "persona": persona.to_dataclass() if persona else None
                })
            
            return {
                "content_count": content_count,
                "recent_content": [c.to_dataclass() for c in recent_content],
                "channel_count": len(channels),
                "channels": channel_personas,
                "total_schedules": total_schedules,
                "active_schedules": active_schedules,
                "paused_schedules": total_schedules - active_schedules
            }
