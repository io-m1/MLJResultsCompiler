import logging
from datetime import datetime
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram.ext import ExtBot
from telegram.constants import ParseMode

from .storage import CMStorage
from .models import Schedule

logger = logging.getLogger(__name__)

class CMScheduler:
    """Wrapper around APScheduler to manage content posting jobs"""
    
    def __init__(self, bot: ExtBot, storage: CMStorage):
        self.bot = bot
        self.storage = storage
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """Start the scheduler and load all active jobs from the database"""
        self._load_active_schedules()
        self.scheduler.start()
        logger.info("MLJCM Scheduler started")
        
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("MLJCM Scheduler stopped")
        
    def _load_active_schedules(self):
        schedules = self.storage.get_all_schedules(active_only=True)
        count = 0
        for sched in schedules:
            if self.add_job_for_schedule(sched):
                count += 1
        logger.info(f"Loaded {count} active schedules from storage")

    def add_job_for_schedule(self, schedule: Schedule) -> bool:
        """Add or update an APScheduler job for a database schedule"""
        job_id = f"schedule_{schedule.id}"
        
        # Check if already exists to avoid duplicates
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)

        try:
            tz = pytz.timezone(schedule.timezone)
        except Exception as e:
            logger.error(f"Invalid timezone {schedule.timezone}, falling back to UTC")
            tz = pytz.UTC

        # Create interval trigger
        trigger = IntervalTrigger(hours=schedule.interval_hours, timezone=tz)
        
        # Fetch content and channel
        content = self.storage.get_content(schedule.content_id)
        channel = self.storage.get_channel(schedule.channel_id)
        
        if not content or not channel:
            logger.error(f"Cannot add job {job_id}: missing content or channel")
            return False

        self.scheduler.add_job(
            self._post_content_job,
            trigger=trigger,
            id=job_id,
            args=[schedule.id, channel.id, content.body, schedule.repeat_until],
            replace_existing=True
        )
        return True

    def remove_job_for_schedule(self, schedule_id: int):
        """Remove a job from the scheduler"""
        job_id = f"schedule_{schedule_id}"
        if self.scheduler.get_job(job_id):
            self.scheduler.remove_job(job_id)
            
    async def _post_content_job(self, schedule_id: int, channel_id: int, text: str, repeat_until: datetime):
        """The actual coroutine that posts the message to Telegram"""
        now = datetime.utcnow()
        
        if repeat_until and now > repeat_until:
            logger.info(f"Schedule {schedule_id} has expired. Deactivating.")
            self.storage.update_schedule_status(schedule_id, False)
            self.remove_job_for_schedule(schedule_id)
            return

        channel = self.storage.get_channel(channel_id)
        if not channel:
            logger.error(f"Cannot post schedule {schedule_id}: channel {channel_id} not found")
            return

        try:
            # Try to send as HTML (bold, italic, etc), fallback to plain text if malformed HTML
            try:
                msg = await self.bot.send_message(chat_id=channel.chat_id, text=text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            except Exception:
                msg = await self.bot.send_message(chat_id=channel.chat_id, text=text, disable_web_page_preview=True)
                
            logger.info(f"Successfully posted schedule {schedule_id} to chat {channel.chat_id}")
            
            # Post to linked chat if requested
            if channel.linked_chat_id and channel.post_to_linked:
                try:
                    await self.bot.forward_message(chat_id=channel.linked_chat_id, from_chat_id=channel.chat_id, message_id=msg.message_id)
                    logger.info(f"Successfully forwarded schedule {schedule_id} to linked chat {channel.linked_chat_id}")
                except Exception as e:
                    logger.error(f"Failed to forward schedule {schedule_id} to linked chat {channel.linked_chat_id}: {e}")
            
            self.storage.update_last_posted(schedule_id, now)
        except Exception as e:
            logger.error(f"Failed to post schedule {schedule_id} to chat {channel.chat_id}: {e}")
