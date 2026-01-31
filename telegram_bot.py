"""
MLJ Results Compiler - Telegram Bot
Allows users to upload test files and get consolidated results via Telegram
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

# Load environment variables
load_dotenv()

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

# User session storage
user_sessions = {}

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
        """Handle uploaded documents"""
        user_id = update.effective_user.id
        
        if user_id not in user_sessions:
            user_sessions[user_id] = {
                'files': [],
                'temp_dir': tempfile.mkdtemp()
            }
        
        session = user_sessions[user_id]
        
        try:
            # Get the file
            document = update.message.document
            
            if not document.file_name.lower().endswith('.xlsx'):
                await update.message.reply_text(
                    "❌ Please send Excel (.xlsx) files only!"
                )
                return SELECTING_FORMAT
            
            # Download file
            file = await context.bot.get_file(document.file_id)
            file_path = Path(session['temp_dir']) / document.file_name
            await file.download_to_drive(file_path)
            
            session['files'].append(str(file_path))
            
            await update.message.reply_text(
                f"✅ File received: {document.file_name}\n"
                f"📦 Total files: {len(session['files'])}\n\n"
                f"📤 Send more files or click below to consolidate:"
            )
            
            # Show format selection after first file
            if len(session['files']) >= 1:
                return await self.show_format_selection(update, context)
            
            return SELECTING_FORMAT
            
        except Exception as e:
            logger.error(f"Error handling document for user {user_id}: {str(e)}")
            await update.message.reply_text(
                f"❌ Error processing file: {str(e)}"
            )
            return SELECTING_FORMAT
    
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
        """Handle format selection"""
        query = update.callback_query
        user_id = update.effective_user.id
        await query.answer()
        
        if user_id not in user_sessions or not user_sessions[user_id]['files']:
            await query.edit_message_text(
                "❌ No files found. Please upload files first with /start"
            )
            return ConversationHandler.END
        
        session = user_sessions[user_id]
        format_choice = query.data.split('_')[1]  # Extract 'xlsx', 'pdf', or 'docx'
        
        if format_choice == 'cancel':
            await query.edit_message_text("❌ Operation cancelled")
            self.cleanup_session(user_id)
            return ConversationHandler.END
        
        try:
            await query.edit_message_text(
                "⏳ Processing your files...\n"
                "This may take a moment..."
            )
            
            # Create processor with session temp directory
            input_dir = Path(session['temp_dir'])
            output_dir = Path(tempfile.mkdtemp())
            
            processor = ExcelProcessor(str(input_dir), str(output_dir))
            
            # Load uploaded files
            loaded = processor.load_all_tests(max_tests=5)
            
            if loaded == 0:
                await query.edit_message_text(
                    "❌ No valid test files found. Please check your files."
                )
                self.cleanup_session(user_id)
                return ConversationHandler.END
            
            logger.info(f"User {user_id}: Loaded {loaded} test files")
            
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
    
    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Handle /cancel command"""
        user_id = update.effective_user.id
        self.cleanup_session(user_id)
        
        await update.message.reply_text("❌ Operation cancelled. Start over with /start")
        return ConversationHandler.END
    
    @staticmethod
    def cleanup_session(user_id):
        """Clean up temporary files for a user"""
        if user_id in user_sessions:
            import shutil
            temp_dir = user_sessions[user_id]['temp_dir']
            if Path(temp_dir).exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
            del user_sessions[user_id]

def main():
    """Start the Telegram bot"""
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        raise ValueError("Please set TELEGRAM_BOT_TOKEN in .env file")
    
    # Create the Application
    application = Application.builder().token(token).build()
    handler = TelegramBotHandler(token)
    
    # Create conversation handler
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
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", handler.help_command))
    application.add_handler(CommandHandler("start", handler.start))
    
    # Start the bot
    logger.info("Starting MLJ Results Compiler Telegram Bot")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
