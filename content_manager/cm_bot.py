import logging
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters
)
from telegram.constants import ParseMode, ChatMemberStatus

from .storage import CMStorage
from .scheduler import CMScheduler

logger = logging.getLogger(__name__)

# Conversation States
(
    CONTENT_TITLE,
    CONTENT_BODY,
    SCHED_SELECT_CONTENT,
    SCHED_SELECT_CHANNEL,
    SCHED_INTERVAL
) = range(5)

class ContentManagerBot:
    """Telegram Bot handler for MLJCM Content Manager"""
    
    def __init__(self, token: str, storage: CMStorage):
        self.token = token
        self.storage = storage
        self.application = Application.builder().token(token).build()
        self.scheduler = CMScheduler(self.application.bot, self.storage)
        self._setup_handlers()

    def _setup_handlers(self):
        # Basic commands
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("channels", self.cmd_channels))
        self.application.add_handler(CommandHandler("status", self.cmd_status))
        self.application.add_handler(CommandHandler("addchannel", self.cmd_addchannel))
        
        # New Content Flow
        conv_content = ConversationHandler(
            entry_points=[CommandHandler("newcontent", self.start_new_content)],
            states={
                CONTENT_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_content_title)],
                CONTENT_BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_content_body)]
            },
            fallbacks=[CommandHandler("cancel", self.cmd_cancel)],
            allow_reentry=True
        )
        self.application.add_handler(conv_content)
        
        # Scheduling Flow
        conv_schedule = ConversationHandler(
            entry_points=[CommandHandler("schedule", self.start_schedule)],
            states={
                SCHED_SELECT_CONTENT: [CallbackQueryHandler(self.handle_sched_content, pattern="^content_")],
                SCHED_SELECT_CHANNEL: [CallbackQueryHandler(self.handle_sched_channel, pattern="^channel_")],
                SCHED_INTERVAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_sched_interval)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cmd_cancel),
                CallbackQueryHandler(self.cmd_cancel, pattern="^cancel$")
            ],
            allow_reentry=True
        )
        self.application.add_handler(conv_schedule)
        
        # Catch-all for when bot is added to a channel (chat member updates)
        self.application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_chat_members))

    # --- Lifecycle ---

    async def initialize(self):
        await self.application.initialize()
        self.scheduler.start()
        logger.info("MLJCM Bot initialized and scheduler started")

    async def start_polling(self):
        await self.application.start()
        await self.application.updater.start_polling(drop_pending_updates=True)

    async def shutdown(self):
        self.scheduler.stop()
        await self.application.updater.stop()
        await self.application.stop()
        await self.application.shutdown()

    # --- Basic Commands ---

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(
            "👋 <b>Welcome to MLJCM - Content Manager!</b>\n\n"
            "I organize and automatically broadcast your regular posts to channels and groups.\n\n"
            "<b>Setup Steps:</b>\n"
            "1. Add me as an admin to your channel.\n"
            "2. Send /addchannel to register it.\n"
            "3. Send /newcontent to save a post design.\n"
            "4. Send /schedule to set up the auto-posting.",
            parse_mode=ParseMode.HTML
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(
            "📋 <b>MLJCM Commands:</b>\n\n"
            "/newcontent - Create a new saved content post\n"
            "/schedule - Assign content to post to a channel automatically\n"
            "/channels - List your registered channels\n"
            "/addchannel - Instructions for adding a channel\n"
            "/status - View all active schedules\n"
            "/cancel - Cancel any current operation",
            parse_mode=ParseMode.HTML
        )

    async def cmd_cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        if update.callback_query:
            await update.callback_query.answer()
            await update.callback_query.edit_message_text("❌ Operation cancelled.")
        else:
            await update.effective_message.reply_text("❌ Operation cancelled.")
        context.user_data.clear()
        return ConversationHandler.END

    # --- Channel Management ---

    async def cmd_addchannel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.effective_message.reply_text(
            "To add a channel to MLJCM:\n\n"
            "1. Go to your Channel's Info page.\n"
            "2. Go to Administrators -> Add Admin.\n"
            "3. Search for my bot name and add me with 'Post Messages' permission.\n"
            "4. Once added, I will automatically detect the channel and register it!",
            parse_mode=ParseMode.HTML
        )

    async def cmd_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        channels = self.storage.get_all_channels()
        if not channels:
            await update.effective_message.reply_text("No channels registered yet.\nUse /addchannel to see instructions.")
            return
            
        text = "📻 <b>Registered Channels:</b>\n\n"
        for c in channels:
            text += f"• <b>{c.title}</b> (Added: {c.added_at.strftime('%Y-%m-%d')})\n"
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)

    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Automatically detect when bot is added to a channel/group"""
        bot_id = self.application.bot.id
        for member in update.message.new_chat_members:
            if member.id == bot_id:
                chat = update.effective_chat
                user_id = update.message.from_user.id
                
                # Register channel
                self.storage.add_channel(
                    chat_id=chat.id,
                    title=chat.title,
                    chat_type=chat.type,
                    added_by=user_id
                )
                
                logger.info(f"MLJCM Bot added to {chat.type}: {chat.title} ({chat.id})")
                
                # Try to DM the user who added the bot
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"✅ <b>Successfully registered!</b>\n\nI've been added to <b>{chat.title}</b> and it is now available for scheduled posts.\n\nUse /newcontent to start preparing posts.",
                        parse_mode=ParseMode.HTML
                    )
                except Exception:
                    pass  # User might not have DMed the bot first

    # --- Content Creation Flow ---

    async def start_new_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        await update.effective_message.reply_text(
            "📝 Let's create a new Content Post.\n\n"
            "First, send me a <b>Title/Label</b> for this content (e.g., 'Job Vacancy Rules'). This is just for your reference.",
            parse_mode=ParseMode.HTML
        )
        return CONTENT_TITLE

    async def handle_content_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        title = update.message.text.strip()
        context.user_data['content_title'] = title
        
        await update.effective_message.reply_text(
            f"Great. Title set to: <b>{title}</b>\n\n"
            "Now, send me the <b>Full Content Text</b>. You can include links, emojis, and lots of text!",
            parse_mode=ParseMode.HTML
        )
        return CONTENT_BODY

    async def handle_content_body(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        body = update.message.text
        title = context.user_data.get('content_title')
        user_id = update.effective_user.id
        
        # Save to DB
        content = self.storage.create_content(title=title, body=body, created_by=user_id)
        
        await update.effective_message.reply_text(
            f"✅ <b>Content Saved!</b>\n\n"
            f"Title: {title}\n"
            f"ID: #{content.id}\n\n"
            f"You can now use /schedule to assign this content to post automatically.",
            parse_mode=ParseMode.HTML
        )
        context.user_data.clear()
        return ConversationHandler.END

    # --- Scheduling Flow ---

    async def start_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        contents = self.storage.get_all_content()
        if not contents:
            await update.effective_message.reply_text("You have no saved content. Use /newcontent first.")
            return ConversationHandler.END
            
        keyboard = []
        for c in contents:
            keyboard.append([InlineKeyboardButton(c.title, callback_data=f"content_{c.id}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.effective_message.reply_text("Select the content you want to schedule:", reply_markup=reply_markup)
        return SCHED_SELECT_CONTENT

    async def handle_sched_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[1])
        context.user_data['sched_content_id'] = content_id
        
        channels = self.storage.get_all_channels()
        if not channels:
            await query.edit_message_text("You have no registered channels. Add me to a channel as Admin first.")
            return ConversationHandler.END
            
        keyboard = []
        for c in channels:
            keyboard.append([InlineKeyboardButton(c.title, callback_data=f"channel_{c.id}")])
        keyboard.append([InlineKeyboardButton("❌ Cancel", callback_data="cancel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Select the destination channel:", reply_markup=reply_markup)
        return SCHED_SELECT_CHANNEL

    async def handle_sched_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        channel_id = int(query.data.split('_')[1])
        context.user_data['sched_channel_id'] = channel_id
        
        await query.edit_message_text(
            "⏰ <b>Set Interval</b>\n\n"
            "How often should this post be sent?\n"
            "Reply with a number of hours (e.g., '3' for every 3 hours, '0.5' for every 30 mins).",
            parse_mode=ParseMode.HTML
        )
        return SCHED_INTERVAL

    async def handle_sched_interval(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        text = update.message.text.strip()
        try:
            interval_hours = float(text)
            if interval_hours <= 0:
                raise ValueError()
        except ValueError:
            await update.effective_message.reply_text("Please reply with a valid positive number (e.g. '6').")
            return SCHED_INTERVAL
            
        content_id = context.user_data['sched_content_id']
        channel_id = context.user_data['sched_channel_id']
        
        # Save schedule to DB
        schedule = self.storage.create_schedule(
            content_id=content_id,
            channel_id=channel_id,
            interval_hours=interval_hours,
            start_time="",  # Posts immediately, then interval
            timezone="Africa/Lagos"  # WAT default
        )
        
        # Add to live APScheduler
        self.scheduler.add_job_for_schedule(schedule)
        
        content = self.storage.get_content(content_id)
        channel = self.storage.get_channel(channel_id)
        
        await update.effective_message.reply_text(
            f"✅ <b>Successfully Scheduled!</b>\n\n"
            f"Content: <i>{content.title}</i>\n"
            f"Destination: <i>{channel.title}</i>\n"
            f"Interval: Every <b>{interval_hours} hours</b>\n"
            f"Timezone: WAT (Africa/Lagos)\n\n"
            f"The first post will be sent shortly, and then repeat automatically. Use /status to view active schedules.",
            parse_mode=ParseMode.HTML
        )
        context.user_data.clear()
        return ConversationHandler.END

    # --- Dashboards ---

    async def cmd_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        schedules = self.storage.get_all_schedules(active_only=True)
        if not schedules:
            await update.effective_message.reply_text("No active schedules found.")
            return
            
        text = "📊 <b>Active Schedules:</b>\n\n"
        for s in schedules:
            content = self.storage.get_content(s.content_id)
            channel = self.storage.get_channel(s.channel_id)
            
            c_title = content.title if content else "Deleted Content"
            ch_title = channel.title if channel else "Deleted Channel"
            last_post = s.last_posted_at.strftime('%Y-%m-%d %H:%M') if s.last_posted_at else 'Never'
            
            text += (
                f"<b>ID #{s.id}: {c_title}</b> → {ch_title}\n"
                f"⏱️ Every {s.interval_hours}h | Last: {last_post}\n\n"
            )
            
        await update.effective_message.reply_text(text, parse_mode=ParseMode.HTML)
