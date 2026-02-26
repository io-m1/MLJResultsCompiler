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

# State for adding new content
(WAITING_FOR_TITLE, WAITING_FOR_BODY) = range(2)

class ContentManagerBot:
    """Telegram Bot handler for MLJCM Content Manager using Inline Keyboard Navigation"""
    
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
        
        # New Content Conversation
        conv_content = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start_add_content, pattern="^new_content$")],
            states={
                WAITING_FOR_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_content_title)],
                WAITING_FOR_BODY: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_content_body)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cmd_cancel_conv),
                CallbackQueryHandler(self.cmd_cancel_callback, pattern="^cancel_conv$")
            ]
        )
        self.application.add_handler(conv_content)
        
        # Navigation Callbacks
        self.application.add_handler(CallbackQueryHandler(self.show_main_menu, pattern="^main_menu$"))
        
        # Bucket Navigation
        self.application.add_handler(CallbackQueryHandler(self.show_bucket, pattern="^bucket_list$"))
        self.application.add_handler(CallbackQueryHandler(self.view_content, pattern="^view_content_"))
        self.application.add_handler(CallbackQueryHandler(self.delete_content, pattern="^del_content_"))
        
        # Scheduling Navigation
        self.application.add_handler(CallbackQueryHandler(self.start_schedule, pattern="^sched_start_"))
        self.application.add_handler(CallbackQueryHandler(self.select_channel, pattern="^sched_chan_"))
        self.application.add_handler(CallbackQueryHandler(self.finalize_schedule, pattern="^sched_int_"))
        
        # Manage Active Schedules
        self.application.add_handler(CallbackQueryHandler(self.show_schedules, pattern="^schedules_list$"))
        self.application.add_handler(CallbackQueryHandler(self.toggle_schedule, pattern="^sched_toggle_"))
        self.application.add_handler(CallbackQueryHandler(self.delete_schedule, pattern="^sched_del_"))
        
        # Channels Navigation
        self.application.add_handler(CallbackQueryHandler(self.show_channels, pattern="^channels_list$"))
        
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

    # --- UI Components ---

    def get_main_menu_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("📝 Document Bucket (Content)", callback_data="bucket_list")],
            [InlineKeyboardButton("⏰ Active Schedules", callback_data="schedules_list")],
            [InlineKeyboardButton("📻 Registered Channels", callback_data="channels_list")]
        ]
        return InlineKeyboardMarkup(keyboard)

    # --- Entry points ---

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = (
            "👋 <b>Welcome to MLJCM - Content Manager!</b>\n\n"
            "I organize and automatically broadcast your regular posts to channels and groups.\n"
            "To get started, add me to your channel as an Admin, then use the menu below."
        )
        await update.effective_message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=self.get_main_menu_keyboard()
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.cmd_start(update, context)

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        text = "🎛 <b>Main Menu</b>\n\nSelect an operation:"
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=self.get_main_menu_keyboard())

    # --- Document Bucket (Content Management) ---

    async def show_bucket(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        contents = self.storage.get_all_content()
        keyboard = [[InlineKeyboardButton("➕ Add New Content", callback_data="new_content")]]
        
        for c in contents:
            keyboard.append([InlineKeyboardButton(f"📄 {c.title}", callback_data=f"view_content_{c.id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])
        
        await query.edit_message_text(
            "📝 <b>Document Bucket</b>\n\nManage your saved posts here.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def view_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[2])
        content = self.storage.get_content(content_id)
        
        if not content:
            await query.edit_message_text(
                "❌ Content not found.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bucket", callback_data="bucket_list")]])
            )
            return
            
        text = f"📄 <b>{content.title}</b>\n\n{content.body}"
        
        keyboard = [
            [InlineKeyboardButton("⏰ Schedule This Post", callback_data=f"sched_start_{content.id}")],
            [InlineKeyboardButton("❌ Delete Content", callback_data=f"del_content_{content.id}")],
            [InlineKeyboardButton("🔙 Back to Bucket", callback_data="bucket_list")]
        ]
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )

    async def delete_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[2])
        self.storage.delete_content(content_id)
        
        await self.show_bucket(update, context)

    # --- New Content Conversation ---
    
    async def start_add_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")]]
        await query.edit_message_text(
            "📝 <b>New Content Post</b>\n\n"
            "First, send me a <b>Title/Label</b> for this content (e.g., 'Job Vacancy Rules'). This is just for your reference.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_FOR_TITLE

    async def handle_content_title(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data['temp_title'] = update.message.text.strip()
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")]]
        await update.effective_message.reply_text(
            f"Great. Title set to: <b>{context.user_data['temp_title']}</b>\n\n"
            "Now, send me the <b>Full Content Text</b>. You can include links, emojis, and formatting.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return WAITING_FOR_BODY

    async def handle_content_body(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        body = update.message.text
        title = context.user_data.get('temp_title')
        user_id = update.effective_user.id
        
        self.storage.create_content(title=title, body=body, created_by=user_id)
        context.user_data.clear()
        
        await update.effective_message.reply_text(
            "✅ <b>Content Saved!</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Bucket", callback_data="bucket_list")]])
        )
        return ConversationHandler.END

    async def cmd_cancel_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
        await update.effective_message.reply_text(
            "❌ Operation cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

    async def cmd_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        context.user_data.clear()
        
        await query.edit_message_text(
            "❌ Operation cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

    # --- Inline Scheduling Flow ---

    async def start_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[2])
        channels = self.storage.get_all_channels()
        
        if not channels:
            await query.edit_message_text(
                "You have no registered channels. Add me to a channel as Admin first.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"view_content_{content_id}")]])
            )
            return
            
        keyboard = []
        for c in channels:
            # Pass content_id and channel_id
            keyboard.append([InlineKeyboardButton(c.title, callback_data=f"sched_chan_{content_id}_{c.id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data=f"view_content_{content_id}")])
        
        await query.edit_message_text("📻 Select the destination channel:", reply_markup=InlineKeyboardMarkup(keyboard))

    async def select_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        content_id = int(parts[2])
        channel_id = int(parts[3])
        
        # Predefined intervals to keep it inline
        keyboard = [
            [
                InlineKeyboardButton("1 Hour", callback_data=f"sched_int_{content_id}_{channel_id}_1"),
                InlineKeyboardButton("3 Hours", callback_data=f"sched_int_{content_id}_{channel_id}_3")
            ],
            [
                InlineKeyboardButton("6 Hours", callback_data=f"sched_int_{content_id}_{channel_id}_6"),
                InlineKeyboardButton("12 Hours", callback_data=f"sched_int_{content_id}_{channel_id}_12")
            ],
            [
                InlineKeyboardButton("24 Hours", callback_data=f"sched_int_{content_id}_{channel_id}_24")
            ],
            [InlineKeyboardButton("🔙 Cancel", callback_data=f"view_content_{content_id}")]
        ]
        
        await query.edit_message_text(
            "⏰ <b>Select Posting Interval</b>\n\nHow often should this be posted?",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def finalize_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        content_id = int(parts[2])
        channel_id = int(parts[3])
        interval = float(parts[4])
        
        schedule = self.storage.create_schedule(
            content_id=content_id,
            channel_id=channel_id,
            interval_hours=interval,
            start_time="",
            timezone="Africa/Lagos"
        )
        
        self.scheduler.add_job_for_schedule(schedule)
        
        await query.edit_message_text(
            f"✅ <b>Successfully Scheduled!</b>\n\n"
            f"Posting every {interval} hour(s).\n\n"
            f"Check Active Schedules to manage.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])
        )

    # --- Manage Schedules ---

    async def show_schedules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        schedules = self.storage.get_all_schedules()
        
        if not schedules:
            await query.edit_message_text(
                "No active schedules.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])
            )
            return

        text = "⏰ <b>Active Schedules</b>\n\n"
        keyboard = []
        
        for s in schedules:
            content = self.storage.get_content(s.content_id)
            channel = self.storage.get_channel(s.channel_id)
            c_title = content.title if content else "Deleted"
            ch_title = channel.title if channel else "Deleted"
            status = "🟢 ON" if s.is_active else "🔴 OFF"
            
            text += f"<b>#{s.id}</b>: {status} | {c_title} → {ch_title} (Every {s.interval_hours}h)\n"
            
            row = [
                InlineKeyboardButton(f"{'⏸ Pause' if s.is_active else '▶️ Resume'} #{s.id}", callback_data=f"sched_toggle_{s.id}"),
                InlineKeyboardButton(f"❌ Del #{s.id}", callback_data=f"sched_del_{s.id}")
            ]
            keyboard.append(row)
            
        keyboard.append([InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")])
        
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def toggle_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        schedule_id = int(query.data.split('_')[2])
        
        schedule = self.storage.get_schedule(schedule_id)
        if schedule:
            new_state = not schedule.is_active
            self.storage.update_schedule_status(schedule_id, new_state)
            
            if new_state:
                schedule.is_active = True
                self.scheduler.add_job_for_schedule(schedule)
            else:
                self.scheduler.remove_job_for_schedule(schedule_id)
                
        await self.show_schedules(update, context)

    async def delete_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        schedule_id = int(query.data.split('_')[2])
        
        self.scheduler.remove_job_for_schedule(schedule_id)
        self.storage.delete_schedule(schedule_id)
        
        await self.show_schedules(update, context)

    # --- Channels ---

    async def show_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        channels = self.storage.get_all_channels()
        text = "📻 <b>Registered Channels</b>\n\n"
        
        if not channels:
            text += "None yet. Add me to a channel as an Admin to register it."
        else:
            for c in channels:
                text += f"• <b>{c.title}</b>\n"
                
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Main Menu", callback_data="main_menu")]])
        )

    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Automatically detect when bot is added to a channel/group"""
        bot_id = self.application.bot.id
        for member in update.message.new_chat_members:
            if member.id == bot_id:
                chat = update.effective_chat
                user_id = update.message.from_user.id
                
                self.storage.add_channel(
                    chat_id=chat.id,
                    title=chat.title,
                    chat_type=chat.type,
                    added_by=user_id
                )
                
                logger.info(f"MLJCM Bot added to {chat.type}: {chat.title} ({chat.id})")
                
                try:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"✅ <b>Successfully registered {chat.title}!</b>\n\nIt is now available for scheduled posts.",
                        parse_mode=ParseMode.HTML,
                        reply_markup=self.get_main_menu_keyboard()
                    )
                except Exception:
                    pass
