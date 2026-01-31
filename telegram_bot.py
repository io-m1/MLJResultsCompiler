"""
MLJ Results Compiler - Telegram Bot
Allows users to upload test files and get consolidated results via Telegram
Session-aware, agentic workflow: collect files → consolidate on demand
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import Dict
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.error import TelegramError

from src.excel_processor import ExcelProcessor
from src.session_manager import SessionManager, WorkflowAgent

# Load environment variables
load_dotenv(dotenv_path='.env')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_FORMAT = 1
CONFIRMING_PREVIEW = 2
SELECTING_OUTPUT_FORMAT = 3

# Global session manager (persists across requests)
session_manager = SessionManager()

class TelegramBotHandler:
    """Handles Telegram bot interactions"""
    
    def __init__(self, token):
        self.token = token
        self.bot_token = token
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user_id = update.effective_user.id
        
        welcome_text = """
👋 Welcome to MLJ Results Compiler Bot!

I can help you consolidate test results from multiple Excel files.

📋 **How to use:**
1. Send me 1-5 XLSX test files (Test 1.xlsx, Test 2.xlsx, etc.)
2. I'll consolidate them by participant
3. Choose your output format
4. Get your results instantly!

📤 **Send your files now** or use /help for more info
        """
        
        await update.message.reply_text(welcome_text)
        logger.info(f"User {user_id} started the bot")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """
🤖 **Bot Commands:**

/start - Show welcome message
/help - Show this help message
/cancel - Cancel current operation

📝 **File Requirements:**
- Format: .xlsx (Excel files)
- Columns needed: Full Name, Email, Score/Result
- Files: Test 1.xlsx, Test 2.xlsx, ... Test 5.xlsx

🎨 **Color Coding:**
- Test 1: White
- Test 2: Sky Blue
- Test 3: Yellow
- Test 4: Lemon Green
- Test 5: Red

✨ **Supported Output Formats:**
- Excel (XLSX) - Color-coded spreadsheet
- PDF - Professional report
- Word (DOCX) - Formatted document

⚡ **Process:**
1. Upload your XLSX files
2. I'll detect all files automatically
3. Select your output format
4. Download consolidated results
        """
        
        await update.message.reply_text(help_text)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle uploaded documents - collect files without immediate processing"""
        user_id = update.effective_user.id
        
        try:
            document = update.message.document
            
            if not document.file_name.lower().endswith('.xlsx'):
                await update.message.reply_text(
                    "❌ Please send Excel (.xlsx) files only!"
                )
                return SELECTING_FORMAT
            
            # Get session and temp directory
            session = session_manager.get_session(user_id)
            temp_dir = Path(session['temp_dir'])
            
            # Download file
            file = await context.bot.get_file(document.file_id)
            file_path = temp_dir / document.file_name
            await file.download_to_drive(file_path)
            
            # Detect test number from filename (Test 1, Test 2, etc.)
            test_num = self._extract_test_number(document.file_name)
            
            if test_num is None:
                await update.message.reply_text(
                    "⚠️ **Could not detect test number from this filename**\n\n"
                    "📝 **Accepted formats:**\n"
                    "✅ 'Test 1.xlsx', 'test 1.xlsx', 'Test1.xlsx'\n"
                    "✅ '1.xlsx', 'result_1.xlsx', 'exam(1).xlsx'\n\n"
                    "🔹 The file must contain at least one number (1-9).\n"
                    "Please rename and try again.",
                    parse_mode="Markdown"
                )
                return SELECTING_FORMAT
            
            # Add file to session
            summary = session_manager.add_file(user_id, str(file_path), test_num)
            
            # Send status update
            status_msg = session_manager.format_status_message(user_id)
            await update.message.reply_text(status_msg, parse_mode="Markdown")
            
            # Agent reasoning: What's next?
            next_action = WorkflowAgent.get_next_action(session_manager.get_session(user_id))
            suggestion = WorkflowAgent.format_suggestion(next_action)
            
            await update.message.reply_text(
                f"ℹ️ {suggestion}\n\n"
                f"🔹 Send more files or use /consolidate to process"
            )
            
            return SELECTING_FORMAT
            
        except Exception as e:
            logger.error(f"Error handling document: {e}")
            await update.message.reply_text(
                "❌ Error processing file. Please try again."
            )
            return SELECTING_FORMAT
    
    @staticmethod
    def _extract_test_number(filename: str) -> int:
        """
        Extract test number from filename.
        Supports multiple formats:
        - 'Test 1.xlsx', 'test 1.xlsx', 'Test1.xlsx'
        - '1.xlsx', 'result_1.xlsx', 'exam(1).xlsx'
        - Any filename with a number in it
        """
        import re
        
        # Remove extension to focus on the name part
        name_without_ext = filename.rsplit('.', 1)[0] if '.' in filename else filename
        
        # Try 1: Look for "Test N" or "test N" format first (preferred)
        match = re.search(r'[Tt]est\s*(\d+)', name_without_ext)
        if match:
            return int(match.group(1))
        
        # Try 2: Look for any number in the filename (if no "Test" prefix)
        # This handles: "1.xlsx", "result_1", "exam(1)", etc.
        match = re.search(r'(\d+)', name_without_ext)
        if match:
            return int(match.group(1))
        
        # No number found
        return None
    
    async def show_format_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show format selection buttons"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Excel (XLSX)", callback_data='format_xlsx'),
                InlineKeyboardButton("📄 PDF Report", callback_data='format_pdf'),
            ],
            [
                InlineKeyboardButton("📝 Word (DOCX)", callback_data='format_docx'),
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data='cancel'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "📋 Choose your output format:",
            reply_markup=reply_markup
        )
        
        return SELECTING_FORMAT
    
    @staticmethod
    def _generate_preview(consolidated_data: Dict, max_rows: int = 10, validation_report: Dict = None) -> str:
        """Generate a text preview of consolidated results with validation warnings"""
        if not consolidated_data:
            return "❌ No data to preview"
        
        # Get summary stats
        total_participants = len(consolidated_data)
        test_nums = set()
        for data in consolidated_data.values():
            for key in data.keys():
                if key.startswith('test_') and key.endswith('_score'):
                    test_nums.add(int(key.split('_')[1]))
        
        test_nums = sorted(test_nums)
        
        # Build preview text
        preview = f"""
📊 **CONSOLIDATION PREVIEW**

📈 **Summary:**
• Total Participants: {total_participants}
• Tests Consolidated: {', '.join(f'Test {t}' for t in test_nums)}
"""
        
        # Add validation warnings if present
        if validation_report:
            if validation_report.get('missing_participants'):
                preview += f"\n⚠️ **MISSING SCORES:** {len(validation_report['missing_participants'])} participant(s) missing from some tests"
                for item in validation_report['missing_participants'][:3]:
                    preview += f"\n   • {item['name']} - missing in Test {item['missing_in_test']}"
                if len(validation_report['missing_participants']) > 3:
                    preview += f"\n   ... and {len(validation_report['missing_participants']) - 3} more"
            
            if validation_report.get('name_mismatches'):
                preview += f"\n🔴 **NAME MISMATCH:** {len(validation_report['name_mismatches'])} name conflict(s)"
                for item in validation_report['name_mismatches'][:2]:
                    preview += f"\n   • {item['email']}: Test 1='{item['test_1_name']}' vs Test {item['test_num']}='{item['conflicting_name']}'"
            
            if validation_report.get('duplicate_scores'):
                preview += f"\n❓ **IDENTICAL SCORES:** {len(validation_report['duplicate_scores'])} participant(s)"
                for item in validation_report['duplicate_scores'][:3]:
                    preview += f"\n   • {item['name']}: {item['score']} in all tests (possible error?)"
        
        preview += f"\n\n📋 **First {min(max_rows, total_participants)} Records:**\n"
        
        # Add sample rows
        for idx, (email, data) in enumerate(consolidated_data.items()):
            if idx >= max_rows:
                break
            
            name = data['name']
            scores = []
            for test_num in test_nums:
                score = data.get(f'test_{test_num}_score')
                if score is not None:
                    scores.append(f"T{test_num}:{score}")
                else:
                    scores.append(f"T{test_num}:—")
            
            score_str = " | ".join(scores)
            preview += f"\n{idx+1}. {name} ({email})\n   {score_str}"
        
        # Show if there are more
        if len(consolidated_data) > max_rows:
            preview += f"\n\n... and {len(consolidated_data) - max_rows} more participants"
        
        preview += "\n\n✅ **Look correct?**"
        return preview
    
    async def show_consolidation_preview(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Show preview of consolidated data before downloading"""
        user_id = update.effective_user.id
        
        # Get or create consolidated data from context
        if 'consolidated_data' not in context.user_data:
            await update.message.reply_text("❌ No consolidation in progress")
            return ConversationHandler.END
        
        consolidated_data = context.user_data['consolidated_data']
        preview = self._generate_preview(consolidated_data)
        
        keyboard = [
            [
                InlineKeyboardButton("✅ Looks Good!", callback_data='preview_confirm'),
                InlineKeyboardButton("❓ Show Full Data", callback_data='preview_full'),
            ],
            [
                InlineKeyboardButton("❌ Cancel", callback_data='preview_cancel'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            preview,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
        
        return CONFIRMING_PREVIEW
    
    async def handle_preview_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle user action on preview (confirm, show more, or cancel)"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        action = query.data.split('_')[1]  # confirm, full, or cancel
        
        if action == 'cancel':
            # Try to delete image message
            try:
                await query.delete_message()
            except:
                await query.edit_message_text("❌ Operation cancelled")
            return ConversationHandler.END
        
        elif action == 'full':
            # Show full data preview
            consolidated_data = context.user_data.get('consolidated_data', {})
            validation_report = context.user_data.get('validation_report')
            processor = context.user_data.get('processor')
            
            # Generate full preview image (all rows)
            if processor:
                full_image_path = processor.generate_preview_image(consolidated_data, max_rows=999)
                if full_image_path and full_image_path.exists():
                    try:
                        await query.delete_message()
                        await context.bot.send_photo(
                            chat_id=update.effective_chat.id,
                            photo=open(full_image_path, 'rb'),
                            caption="📊 **FULL CONSOLIDATION DATA** (all participants shown)\n\n_Use Back button to return to quick preview_",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        logger.error(f"Error sending full image: {str(e)}")
                        full_preview = self._generate_preview(consolidated_data, max_rows=999, validation_report=validation_report)
                        await query.edit_message_text(full_preview, parse_mode="Markdown")
                    return CONFIRMING_PREVIEW
            
            # Fallback to text
            full_preview = self._generate_preview(consolidated_data, max_rows=999, validation_report=validation_report)
            await query.edit_message_text(full_preview, parse_mode="Markdown")
            return CONFIRMING_PREVIEW
        
        elif action == 'confirm':
            # User confirmed, show format selection
            try:
                await query.delete_message()
            except:
                pass
            
            keyboard = [
                [
                    InlineKeyboardButton("📊 Excel (XLSX)", callback_data='format_xlsx'),
                    InlineKeyboardButton("📄 PDF Report", callback_data='format_pdf'),
                ],
                [
                    InlineKeyboardButton("📝 Word (DOCX)", callback_data='format_docx'),
                ],
                [
                    InlineKeyboardButton("❌ Cancel", callback_data='format_cancel'),
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="📋 Great! Choose your output format:",
                reply_markup=reply_markup
            )
            return SELECTING_OUTPUT_FORMAT
        
        return CONFIRMING_PREVIEW
    
    async def format_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle format selection - consolidate and show preview"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        # Get session
        session = session_manager.get_session(user_id)
        uploaded_files = session_manager.get_files_for_consolidation(user_id)
        
        if not uploaded_files:
            await query.edit_message_text(
                "❌ No files found. Please upload files first with /start"
            )
            return ConversationHandler.END
        
        format_choice = query.data.split('_')[1]  # Extract 'xlsx', 'pdf', or 'docx'
        
        if format_choice == 'cancel':
            await query.edit_message_text("❌ Operation cancelled")
            session_manager.clear_session(user_id)
            return ConversationHandler.END
        
        try:
            await query.edit_message_text(
                "⏳ Consolidating files...\n"
                "Merging all tests...",
                parse_mode="Markdown"
            )
            
            # Create processor with session files
            input_dir = Path(session['temp_dir'])
            output_dir = Path(tempfile.mkdtemp())
            
            processor = ExcelProcessor(str(input_dir), str(output_dir))
            
            # Load uploaded files dynamically (detects max test number)
            loaded = processor.load_all_tests()
            
            if loaded == 0:
                await query.edit_message_text(
                    "❌ No valid test files found. Please check your files."
                )
                session_manager.clear_session(user_id)
                return ConversationHandler.END
            
            logger.info(f"User {user_id}: Loaded {loaded} test files for consolidation")
            
            # Validate data integrity
            validation_report = processor.validate_data_integrity()
            context.user_data['validation_report'] = validation_report
            
            # Consolidate
            consolidated_data = processor.consolidate_results()
            
            if not consolidated_data:
                await query.edit_message_text(
                    "❌ Failed to consolidate results"
                )
                self.cleanup_session(user_id)
                return ConversationHandler.END
            
            # Store consolidated data and format choice for later use
            context.user_data['consolidated_data'] = consolidated_data
            context.user_data['processor'] = processor
            context.user_data['output_dir'] = str(output_dir)
            context.user_data['format_choice'] = format_choice
            
            # Generate visual preview image
            preview_image_path = processor.generate_preview_image(consolidated_data, max_rows=10)
            if preview_image_path and preview_image_path.exists():
                context.user_data['preview_image_path'] = str(preview_image_path)
                
                # Build validation warnings text
                warnings_text = ""
                if validation_report:
                    if validation_report.get('missing_participants'):
                        warnings_text += f"⚠️ **MISSING SCORES:** {len(validation_report['missing_participants'])} participant(s) missing from some tests\n"
                    if validation_report.get('name_mismatches'):
                        warnings_text += f"🔴 **NAME MISMATCH:** {len(validation_report['name_mismatches'])} name conflict(s)\n"
                    if validation_report.get('duplicate_scores'):
                        warnings_text += f"❓ **IDENTICAL SCORES:** {len(validation_report['duplicate_scores'])} participant(s)\n"
                
                caption = "📊 **VISUAL CONSOLIDATION PREVIEW**\n"
                if warnings_text:
                    caption += "\n" + warnings_text + "\n"
                caption += "_Click buttons below to proceed or see full data_"
                
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Looks Good!", callback_data='preview_confirm'),
                        InlineKeyboardButton("❓ Show Full Data", callback_data='preview_full'),
                    ],
                    [
                        InlineKeyboardButton("❌ Cancel", callback_data='preview_cancel'),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Delete text message and send photo with buttons
                await query.delete_message()
                await context.bot.send_photo(
                    chat_id=update.effective_chat.id,
                    photo=open(preview_image_path, 'rb'),
                    caption=caption,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            else:
                # Fallback to text preview if image generation failed
                logger.warning("Preview image generation failed, falling back to text preview")
                preview = self._generate_preview(consolidated_data, validation_report=validation_report)
                keyboard = [
                    [
                        InlineKeyboardButton("✅ Looks Good!", callback_data='preview_confirm'),
                        InlineKeyboardButton("❓ Show Full Data", callback_data='preview_full'),
                    ],
                    [
                        InlineKeyboardButton("❌ Cancel", callback_data='preview_cancel'),
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(
                    preview,
                    reply_markup=reply_markup,
                    parse_mode="Markdown"
                )
            
            return CONFIRMING_PREVIEW
            
        except Exception as e:
            logger.error(f"Error processing files for user {user_id}: {str(e)}")
            await query.edit_message_text(
                f"❌ Error: {str(e)}\n\nPlease try again or contact support."
            )
            self.cleanup_session(user_id)
            return ConversationHandler.END
    
    async def format_confirmed(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle format selection after preview is confirmed"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        format_choice = query.data.split('_')[1]  # Extract 'xlsx', 'pdf', or 'docx'
        
        if format_choice == 'cancel':
            await query.edit_message_text("❌ Operation cancelled")
            return ConversationHandler.END
        
        try:
            consolidated_data = context.user_data.get('consolidated_data', {})
            processor = context.user_data.get('processor')
            output_dir = Path(context.user_data.get('output_dir', tempfile.gettempdir()))
            
            if not consolidated_data or not processor:
                await query.edit_message_text("❌ Session expired. Please start over.")
                return ConversationHandler.END
            
            await query.edit_message_text(
                "⏳ Generating file...\n"
                f"Converting to {format_choice.upper()}...",
                parse_mode="Markdown"
            )
            
            # Generate file in selected format
            if format_choice == 'xlsx':
                output_file = output_dir / 'Consolidated_Results.xlsx'
                processor.save_consolidated_file(consolidated_data, output_file.name)
            elif format_choice == 'pdf':
                output_file = output_dir / 'Consolidated_Results.pdf'
                processor.save_as_pdf(consolidated_data, output_file.name)
            elif format_choice == 'docx':
                output_file = output_dir / 'Consolidated_Results.docx'
                processor.save_as_docx(consolidated_data, output_file.name)
            
            # Send file back
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"✅ File ready!\n📊 {len(consolidated_data)} participants\n📝 Format: {format_choice.upper()}"
            )
            
            with open(output_file, 'rb') as f:
                await context.bot.send_document(
                    chat_id=update.effective_chat.id,
                    document=f,
                    filename=output_file.name
                )
            
            logger.info(f"User {user_id}: Sent consolidated results ({format_choice})")
            
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="✨ Done! Upload more files or use /help for assistance."
            )
            
            self.cleanup_session(user_id)
            return ConversationHandler.END
            
        except Exception as e:
            logger.error(f"Error generating file for user {user_id}: {str(e)}")
            await query.edit_message_text(
                f"❌ Error: {str(e)}\n\nPlease try again or contact support."
            )
            self.cleanup_session(user_id)
            return ConversationHandler.END
    
    async def consolidate_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /consolidate command - process all uploaded files on demand"""
        user_id = update.effective_user.id
        
        # Get user session
        session = session_manager.get_session(user_id)
        uploaded_files = session_manager.get_files_for_consolidation(user_id)
        
        # Check if consolidation is possible
        if not WorkflowAgent.should_consolidate(session):
            await update.message.reply_text(
                "⚠️ **Cannot consolidate yet**\n\n"
                "Test 1 file is required as the base.\n"
                "Please upload Test 1 first.",
                parse_mode="Markdown"
            )
            return SELECTING_FORMAT
        
        if not uploaded_files:
            await update.message.reply_text(
                "📁 No files uploaded yet.\n"
                "Send files to get started."
            )
            return SELECTING_FORMAT
        
        # Show format selection
        return await self.show_format_selection(update, context)
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /cancel command"""
        user_id = update.effective_user.id
        self.cleanup_session(user_id)
        
        await update.message.reply_text("❌ Operation cancelled. Start over with /start")
        return ConversationHandler.END
    
    @staticmethod
    def cleanup_session(user_id):
        """Clean up temporary files for a user"""
        session_manager.clear_session(user_id)

def build_application(token: str) -> Application:
    """Construct the PTB Application with handlers registered."""
    application = Application.builder().token(token).build()
    handler = TelegramBotHandler(token)

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handler.start),
            MessageHandler(filters.Document.FileExtension("xlsx"), handler.handle_document),
        ],
        states={
            SELECTING_FORMAT: [
                MessageHandler(filters.Document.FileExtension("xlsx"), handler.handle_document),
                CallbackQueryHandler(handler.format_selected),
            ],
            CONFIRMING_PREVIEW: [
                CallbackQueryHandler(handler.handle_preview_action),
            ],
            SELECTING_OUTPUT_FORMAT: [
                CallbackQueryHandler(handler.format_confirmed),
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handler.cancel),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("consolidate", handler.consolidate_command))
    application.add_handler(CommandHandler("help", handler.help_command))
    application.add_handler(CommandHandler("start", handler.start))

    return application


def main():
    """Start the Telegram bot using long polling (local/dev)."""
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("Please set TELEGRAM_BOT_TOKEN in .env file")

    application = build_application(token)

    logger.info("Starting MLJ Results Compiler Telegram Bot (polling)")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
