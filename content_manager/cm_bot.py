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

COMPOSING = 0
PERSONA_INPUT = 1

class ContentManagerBot:
    
    def __init__(self, token: str, storage: CMStorage):
        self.token = token
        self.storage = storage
        self.application = Application.builder().token(token).job_queue(None).build()
        self.scheduler = CMScheduler(self.application.bot, self.storage)
        self._setup_handlers()

    def _setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("dashboard", self.cmd_dashboard))
        
        compose_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start_compose, pattern="^new_content$")],
            states={
                COMPOSING: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_compose)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cmd_cancel_conv),
                CallbackQueryHandler(self.cmd_cancel_callback, pattern="^cancel_conv$")
            ]
        )
        self.application.add_handler(compose_conv)

        persona_conv = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.start_persona_setup, pattern="^persona_set_")],
            states={
                PERSONA_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_persona_input)]
            },
            fallbacks=[
                CommandHandler("cancel", self.cmd_cancel_conv),
                CallbackQueryHandler(self.cmd_cancel_callback, pattern="^cancel_conv$")
            ]
        )
        self.application.add_handler(persona_conv)
        
        self.application.add_handler(CallbackQueryHandler(self.show_main_menu, pattern="^main_menu$"))
        self.application.add_handler(CallbackQueryHandler(self.show_dashboard, pattern="^dashboard$"))
        
        self.application.add_handler(CallbackQueryHandler(self.show_bucket, pattern="^bucket_list$"))
        self.application.add_handler(CallbackQueryHandler(self.view_content, pattern="^view_content_"))
        self.application.add_handler(CallbackQueryHandler(self.edit_content_preview, pattern="^edit_preview$"))
        self.application.add_handler(CallbackQueryHandler(self.save_content_confirm, pattern="^save_content$"))
        self.application.add_handler(CallbackQueryHandler(self.delete_content, pattern="^del_content_"))
        
        self.application.add_handler(CallbackQueryHandler(self.start_schedule, pattern="^sched_start_"))
        self.application.add_handler(CallbackQueryHandler(self.select_channel, pattern="^sched_chan_"))
        self.application.add_handler(CallbackQueryHandler(self.finalize_schedule, pattern="^sched_int_"))
        
        self.application.add_handler(CallbackQueryHandler(self.show_schedules, pattern="^schedules_list$"))
        self.application.add_handler(CallbackQueryHandler(self.toggle_schedule, pattern="^sched_toggle_"))
        self.application.add_handler(CallbackQueryHandler(self.delete_schedule, pattern="^sched_del_"))
        
        self.application.add_handler(CallbackQueryHandler(self.show_channels, pattern="^channels_list$"))
        self.application.add_handler(CallbackQueryHandler(self.toggle_linked_group, pattern="^toggle_linked_"))
        
        self.application.add_handler(CallbackQueryHandler(self.show_persona_menu, pattern="^persona_menu$"))
        self.application.add_handler(CallbackQueryHandler(self.view_persona, pattern="^persona_view_"))
        self.application.add_handler(CallbackQueryHandler(self.delete_persona, pattern="^persona_del_"))
        
        self.application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.handle_new_chat_members))

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

    def get_main_menu_keyboard(self):
        keyboard = [
            [InlineKeyboardButton("📊 Dashboard", callback_data="dashboard")],
            [InlineKeyboardButton("📝 Document Bucket", callback_data="bucket_list")],
            [InlineKeyboardButton("⏰ Schedules", callback_data="schedules_list")],
            [InlineKeyboardButton("📻 Channels", callback_data="channels_list")],
            [InlineKeyboardButton("⚙️ Bot Identity", callback_data="persona_menu")]
        ]
        return InlineKeyboardMarkup(keyboard)

    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        text = (
            "👋 <b>Welcome to MLJCM — Content Manager</b>\n\n"
            "Organize, schedule, and broadcast content to your channels automatically.\n"
            "Add me to a channel as Admin to get started.\n\n"
            "Use the menu below to navigate."
        )
        await update.effective_message.reply_text(
            text,
            parse_mode=ParseMode.HTML,
            reply_markup=self.get_main_menu_keyboard()
        )

    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await self.cmd_start(update, context)

    async def cmd_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = update.effective_user.id
        text = self._build_dashboard_text(user_id)
        keyboard = [
            [InlineKeyboardButton("✏️ New Post", callback_data="new_content"),
             InlineKeyboardButton("📝 Bucket", callback_data="bucket_list")],
            [InlineKeyboardButton("⏰ Schedules", callback_data="schedules_list"),
             InlineKeyboardButton("📻 Channels", callback_data="channels_list")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="dashboard")]
        ]
        await update.effective_message.reply_text(
            text, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def show_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        text = "🎛 <b>Main Menu</b>\n\nSelect an operation:"
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=self.get_main_menu_keyboard())

    async def show_dashboard(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        user_id = update.effective_user.id
        text = self._build_dashboard_text(user_id)
        keyboard = [
            [InlineKeyboardButton("✏️ New Post", callback_data="new_content"),
             InlineKeyboardButton("📝 Bucket", callback_data="bucket_list")],
            [InlineKeyboardButton("⏰ Schedules", callback_data="schedules_list"),
             InlineKeyboardButton("📻 Channels", callback_data="channels_list")],
            [InlineKeyboardButton("🔄 Refresh", callback_data="dashboard"),
             InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
        ]
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    def _build_dashboard_text(self, user_id: int) -> str:
        stats = self.storage.get_dashboard_stats(user_id)
        
        text = "📊 <b>Dashboard Overview</b>\n"
        text += "━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        text += f"📝 <b>Content</b> — {stats['content_count']} post(s)\n"
        if stats['recent_content']:
            for c in stats['recent_content']:
                text += f"   • {c.title}\n"
        else:
            text += "   <i>No content yet</i>\n"
        
        text += f"\n⏰ <b>Schedules</b> — {stats['total_schedules']} total\n"
        text += f"   🟢 {stats['active_schedules']} active  ·  🔴 {stats['paused_schedules']} paused\n"
        
        text += f"\n📻 <b>Channels</b> — {stats['channel_count']} registered\n"
        if stats['channels']:
            for ch_data in stats['channels']:
                ch = ch_data['channel']
                persona = ch_data['persona']
                persona_label = f" [{persona.bot_name}]" if persona else ""
                text += f"   • {ch.title}{persona_label}\n"
        else:
            text += "   <i>No channels yet</i>\n"
        
        text += "\n━━━━━━━━━━━━━━━━━━━━━"
        return text

    async def show_bucket(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        contents = self.storage.get_all_content(update.effective_user.id)
        keyboard = [[InlineKeyboardButton("✏️ Compose New Post", callback_data="new_content")]]
        
        for c in contents:
            keyboard.append([InlineKeyboardButton(f"📄 {c.title}", callback_data=f"view_content_{c.id}")])
            
        keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="main_menu")])
        
        count = len(contents)
        await query.edit_message_text(
            f"📝 <b>Document Bucket</b> — {count} post(s)\n\nTap a post to view, schedule, or delete.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def view_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[2])
        content = self.storage.get_content(content_id, update.effective_user.id)
        
        if not content:
            await query.edit_message_text(
                "❌ Content not found.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bucket", callback_data="bucket_list")]])
            )
            return
        
        body_preview = content.body[:500] + "..." if len(content.body) > 500 else content.body
        text = f"<b>Subject:</b> {content.title}\n━━━━━━━━━━━━━━━━━━━━━\n{body_preview}"
        
        keyboard = [
            [InlineKeyboardButton("⏰ Schedule", callback_data=f"sched_start_{content.id}"),
             InlineKeyboardButton("❌ Delete", callback_data=f"del_content_{content.id}")],
            [InlineKeyboardButton("🔙 Bucket", callback_data="bucket_list")]
        ]
        
        await query.edit_message_text(
            text, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard),
            disable_web_page_preview=True
        )

    async def delete_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        content_id = int(query.data.split('_')[2])
        self.storage.delete_content(content_id)
        await self.show_bucket(update, context)

    async def start_compose(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")]]
        await query.edit_message_text(
            "✏️ <b>Compose New Post</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Type your post below in <b>one message</b>:\n\n"
            "<i>First line</i> → Subject line\n"
            "<i>Everything after</i> → Body content\n\n"
            "<b>Example:</b>\n"
            "<code>Weekly Job Openings\n"
            "🔥 Hot vacancies this week:\n"
            "1. Senior Developer — Lagos\n"
            "2. Product Manager — Remote\n"
            "Apply now at example.com</code>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return COMPOSING

    async def handle_compose(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        raw = update.message.text.strip()
        lines = raw.split('\n', 1)
        
        title = lines[0].strip()
        body = lines[1].strip() if len(lines) > 1 else title
        
        context.user_data['draft_title'] = title
        context.user_data['draft_body'] = body
        
        body_preview = body[:400] + "..." if len(body) > 400 else body
        preview = (
            "📋 <b>Preview</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Subject:</b> {title}\n\n"
            f"{body_preview}\n"
            "━━━━━━━━━━━━━━━━━━━━━"
        )
        
        keyboard = [
            [InlineKeyboardButton("💾 Save", callback_data="save_content"),
             InlineKeyboardButton("✏️ Re-compose", callback_data="edit_preview")],
            [InlineKeyboardButton("❌ Discard", callback_data="cancel_conv")]
        ]
        
        await update.effective_message.reply_text(
            preview, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationHandler.END

    async def edit_content_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")]]
        await query.edit_message_text(
            "✏️ <b>Re-compose</b>\n\nSend your updated post as one message (first line = subject):",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def save_content_confirm(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        title = context.user_data.get('draft_title', 'Untitled')
        body = context.user_data.get('draft_body', '')
        user_id = update.effective_user.id
        
        self.storage.create_content(title=title, body=body, created_by=user_id)
        context.user_data.pop('draft_title', None)
        context.user_data.pop('draft_body', None)
        
        keyboard = [
            [InlineKeyboardButton("📝 View Bucket", callback_data="bucket_list"),
             InlineKeyboardButton("✏️ Compose Another", callback_data="new_content")],
            [InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
        ]
        
        await query.edit_message_text(
            f"✅ <b>Saved!</b>\n\n<b>{title}</b> has been added to your Document Bucket.",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def cmd_cancel_conv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        context.user_data.clear()
        await update.effective_message.reply_text(
            "❌ Cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

    async def cmd_cancel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        context.user_data.clear()
        await query.edit_message_text(
            "❌ Cancelled.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
        )
        return ConversationHandler.END

    async def start_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        content_id = int(query.data.split('_')[2])
        channels = self.storage.get_all_channels(update.effective_user.id)
        
        if not channels:
            await query.edit_message_text(
                "You have no registered channels. Add me to a channel as Admin first.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data=f"view_content_{content_id}")]])
            )
            return
            
        keyboard = []
        for c in channels:
            keyboard.append([InlineKeyboardButton(c.title, callback_data=f"sched_chan_{content_id}_{c.id}")])
        keyboard.append([InlineKeyboardButton("🔙 Cancel", callback_data=f"view_content_{content_id}")])
        
        await query.edit_message_text(
            "📻 <b>Select destination channel:</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def select_channel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        parts = query.data.split('_')
        content_id = int(parts[2])
        channel_id = int(parts[3])
        
        keyboard = [
            [InlineKeyboardButton("1h", callback_data=f"sched_int_{content_id}_{channel_id}_1"),
             InlineKeyboardButton("3h", callback_data=f"sched_int_{content_id}_{channel_id}_3"),
             InlineKeyboardButton("6h", callback_data=f"sched_int_{content_id}_{channel_id}_6")],
            [InlineKeyboardButton("12h", callback_data=f"sched_int_{content_id}_{channel_id}_12"),
             InlineKeyboardButton("24h", callback_data=f"sched_int_{content_id}_{channel_id}_24"),
             InlineKeyboardButton("48h", callback_data=f"sched_int_{content_id}_{channel_id}_48")],
            [InlineKeyboardButton("🔙 Cancel", callback_data=f"view_content_{content_id}")]
        ]
        
        await query.edit_message_text(
            "⏰ <b>Posting Interval</b>\n\nHow often should this be posted?",
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
        
        content = self.storage.get_content(content_id)
        channel = self.storage.get_channel(channel_id)
        
        schedule = self.storage.create_schedule(
            content_id=content_id,
            channel_id=channel_id,
            interval_hours=interval,
            start_time="",
            timezone="Africa/Lagos"
        )
        self.scheduler.add_job_for_schedule(schedule)
        
        c_title = content.title if content else "Content"
        ch_title = channel.title if channel else "Channel"
        
        await query.edit_message_text(
            f"✅ <b>Scheduled!</b>\n\n"
            f"<b>{c_title}</b> → <b>{ch_title}</b>\n"
            f"Posting every <b>{interval}h</b>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⏰ View Schedules", callback_data="schedules_list"),
                 InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
            ])
        )

    async def show_schedules(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        user_id = update.effective_user.id
        schedules = self.storage.get_all_schedules(user_id)
        
        if not schedules:
            await query.edit_message_text(
                "⏰ <b>No schedules yet.</b>\n\nCreate content first, then schedule it to a channel.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
            )
            return

        text = "⏰ <b>Schedules</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        keyboard = []
        
        for s in schedules:
            content = self.storage.get_content(s.content_id, user_id)
            channel = self.storage.get_channel(s.channel_id)
            c_title = content.title if content else "Deleted"
            ch_title = channel.title if channel else "Deleted"
            status = "🟢" if s.is_active else "🔴"
            
            text += f"{status} <b>{c_title}</b> → {ch_title} · {s.interval_hours}h\n"
            
            row = [
                InlineKeyboardButton(f"{'⏸' if s.is_active else '▶️'} #{s.id}", callback_data=f"sched_toggle_{s.id}"),
                InlineKeyboardButton(f"❌ #{s.id}", callback_data=f"sched_del_{s.id}")
            ]
            keyboard.append(row)
            
        keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="main_menu")])
        
        await query.edit_message_text(
            text, parse_mode=ParseMode.HTML,
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

    async def show_channels(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        channels = self.storage.get_all_channels(update.effective_user.id)
        text = "📻 <b>Channels</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        keyboard = []
        
        if not channels:
            text += "<i>None yet. Add me to a channel as Admin.</i>"
        else:
            for c in channels:
                persona = self.storage.get_persona(c.id)
                persona_label = f" [{persona.bot_name}]" if persona else ""
                text += f"• <b>{c.title}</b>{persona_label}"
                if c.linked_chat_id:
                    status = "✅" if c.post_to_linked else "❌"
                    text += f" · linked: {status}"
                    keyboard.append([InlineKeyboardButton(f"Toggle linked — {c.title}", callback_data=f"toggle_linked_{c.id}")])
                text += "\n"
                
        keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="main_menu")])
                
        await query.edit_message_text(
            text, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def toggle_linked_group(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        channel_id = int(query.data.split('_')[2])
        channel = self.storage.get_channel(channel_id)
        if channel and channel.linked_chat_id:
            new_state = not channel.post_to_linked
            self.storage.update_linked_chat(channel_id, channel.linked_chat_id, new_state)
        await self.show_channels(update, context)

    async def show_persona_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        channels = self.storage.get_all_channels(update.effective_user.id)
        
        if not channels:
            await query.edit_message_text(
                "⚙️ <b>Bot Identity</b>\n\nNo channels registered yet. Add me to a channel first.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]])
            )
            return

        text = "⚙️ <b>Bot Identity</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        text += "Define how your bot appears when posting to each channel.\n\n"
        keyboard = []
        
        for c in channels:
            persona = self.storage.get_persona(c.id)
            if persona:
                text += f"• <b>{c.title}</b> → <i>{persona.bot_name}</i>\n"
                keyboard.append([
                    InlineKeyboardButton(f"✏️ {c.title}", callback_data=f"persona_set_{c.id}"),
                    InlineKeyboardButton(f"👁 View", callback_data=f"persona_view_{c.id}"),
                    InlineKeyboardButton(f"🗑", callback_data=f"persona_del_{c.id}")
                ])
            else:
                text += f"• <b>{c.title}</b> → <i>Default</i>\n"
                keyboard.append([InlineKeyboardButton(f"⚙️ Set identity for {c.title}", callback_data=f"persona_set_{c.id}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Menu", callback_data="main_menu")])
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def start_persona_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        query = update.callback_query
        await query.answer()
        
        channel_id = int(query.data.split('_')[2])
        context.user_data['persona_channel_id'] = channel_id
        
        channel = self.storage.get_channel(channel_id)
        ch_name = channel.title if channel else "this channel"
        
        keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_conv")]]
        await query.edit_message_text(
            f"⚙️ <b>Set Bot Identity for {ch_name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Send one message with these lines:\n\n"
            "<code>Name: JobBot\n"
            "Greeting: 🔥 Fresh from our desk:\n"
            "Sign-off: — Powered by MLJCM</code>\n\n"
            "<i>All three fields are optional. Skip a line to leave it default.</i>",
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return PERSONA_INPUT

    async def handle_persona_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        raw = update.message.text.strip()
        channel_id = context.user_data.get('persona_channel_id')
        user_id = update.effective_user.id
        
        bot_name = "MLJCM Bot"
        greeting = ""
        sign_off = ""
        
        for line in raw.split('\n'):
            line = line.strip()
            lower = line.lower()
            if lower.startswith('name:'):
                bot_name = line.split(':', 1)[1].strip()
            elif lower.startswith('greeting:'):
                greeting = line.split(':', 1)[1].strip()
            elif lower.startswith('sign-off:') or lower.startswith('signoff:') or lower.startswith('sign off:'):
                greeting_parts = line.split(':', 1)
                sign_off = greeting_parts[1].strip() if len(greeting_parts) > 1 else ""
        
        persona = self.storage.set_persona(
            channel_id=channel_id,
            bot_name=bot_name,
            greeting=greeting,
            sign_off=sign_off,
            created_by=user_id
        )
        
        context.user_data.pop('persona_channel_id', None)
        
        preview = (
            f"✅ <b>Identity Set!</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Name:</b> {persona.bot_name}\n"
            f"<b>Greeting:</b> {persona.greeting or '(none)'}\n"
            f"<b>Sign-off:</b> {persona.sign_off or '(none)'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━"
        )
        
        await update.effective_message.reply_text(
            preview, parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("⚙️ Identity Menu", callback_data="persona_menu"),
                 InlineKeyboardButton("🔙 Menu", callback_data="main_menu")]
            ])
        )
        return ConversationHandler.END

    async def view_persona(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        channel_id = int(query.data.split('_')[2])
        persona = self.storage.get_persona(channel_id)
        channel = self.storage.get_channel(channel_id)
        ch_name = channel.title if channel else "Unknown"
        
        if not persona:
            await query.edit_message_text(
                f"No identity set for <b>{ch_name}</b>.",
                parse_mode=ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="persona_menu")]])
            )
            return
        
        text = (
            f"⚙️ <b>Identity — {ch_name}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>Name:</b> {persona.bot_name}\n"
            f"<b>Greeting:</b> {persona.greeting or '(none)'}\n"
            f"<b>Sign-off:</b> {persona.sign_off or '(none)'}\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"<i>Posts to this channel will include the greeting above and sign-off below your content.</i>"
        )
        
        keyboard = [
            [InlineKeyboardButton("✏️ Edit", callback_data=f"persona_set_{channel_id}"),
             InlineKeyboardButton("🗑 Remove", callback_data=f"persona_del_{channel_id}")],
            [InlineKeyboardButton("🔙 Back", callback_data="persona_menu")]
        ]
        await query.edit_message_text(text, parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

    async def delete_persona(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        channel_id = int(query.data.split('_')[2])
        self.storage.delete_persona(channel_id)
        await self.show_persona_menu(update, context)

    async def handle_new_chat_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        bot_id = self.application.bot.id
        for member in update.message.new_chat_members:
            if member.id == bot_id:
                chat = update.effective_chat
                user_id = update.message.from_user.id
                
                channel, is_new = self.storage.add_channel(
                    chat_id=chat.id,
                    title=chat.title,
                    chat_type=chat.type,
                    added_by=user_id
                )
                
                logger.info(f"MLJCM Bot added to {chat.type}: {chat.title} ({chat.id}) - New: {is_new}")
                
                try:
                    full_chat = await context.bot.get_chat(chat.id)
                    if full_chat.linked_chat_id:
                        self.storage.update_linked_chat(channel.id, full_chat.linked_chat_id, True)
                except Exception as e:
                    logger.warning(f"Could not check linked chat for {chat.title}: {e}")
                
                if not is_new:
                    try:
                        await context.bot.send_message(
                            chat_id=user_id,
                            text=f"⚠️ <b>Already Registered</b>\n\n<b>{chat.title}</b> is already linked to your account.",
                            parse_mode=ParseMode.HTML,
                            reply_markup=self.get_main_menu_keyboard()
                        )
                    except Exception:
                        pass
                    return

                try:
                    text = f"✅ <b>Registered {chat.title}!</b>\n\nNow available for content scheduling."
                    if getattr(channel, 'linked_chat_id', None):
                        text += "\n\n<i>Linked discussion group detected and enabled.</i>"
                    await context.bot.send_message(
                        chat_id=user_id, text=text,
                        parse_mode=ParseMode.HTML,
                        reply_markup=self.get_main_menu_keyboard()
                    )
                except Exception:
                    pass
