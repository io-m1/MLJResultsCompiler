"""
MLJ Results Compiler - Telegram Bot
Allows users to upload test files and get consolidated results via Telegram
Session-aware, agentic workflow: collect files → consolidate on demand
"""

import os
import logging
import tempfile
from pathlib import Path
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
- Test 4: Army Green
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
                    "⚠️ Could not detect test number from filename.\n"
                    "Use format: 'Test 1.xlsx', 'Test 2.xlsx', etc."
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
        """Extract test number from filename (e.g., 'Test 1.xlsx' -> 1)"""
        import re
        match = re.search(r'[Tt]est\s*(\d+)', filename)
        return int(match.group(1)) if match else None
    
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
    
    async def format_selected(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle format selection - consolidate and export"""
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
            
            # Consolidate
            consolidated_data = processor.consolidate_results()
            
            if not consolidated_data:
                await query.edit_message_text(
                    "❌ Failed to consolidate results"
                )
                self.cleanup_session(user_id)
                return ConversationHandler.END
            
            # Save in selected format
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
                text=f"✅ Results consolidated!\n📊 {len(consolidated_data)} participants processed"
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
            logger.error(f"Error processing files for user {user_id}: {str(e)}")
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
