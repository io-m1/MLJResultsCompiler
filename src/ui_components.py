"""
Native App UI Components for Telegram Bot
Polished button designs, keyboard layouts, and visual feedback
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Tuple
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

# ============================================================================
# ENUMS FOR COLORS & STYLES
# ============================================================================

class ButtonStyle(Enum):
    """Button styling options"""
    PRIMARY = "🟦"      # Main action (blue)
    SUCCESS = "🟩"      # Positive action (green)
    WARNING = "🟨"      # Attention needed (yellow)
    DANGER = "🔴"       # Destructive action (red)
    NEUTRAL = "⬜"      # Secondary action (gray)
    INFO = "🔵"         # Information (blue circle)


class MenuState(Enum):
    """Navigation states"""
    MAIN = "main"
    UPLOAD = "upload"
    FORMAT = "format"
    CONSOLIDATE = "consolidate"
    RESULT = "result"
    SETTINGS = "settings"


# ============================================================================
# BUTTON BUILDERS
# ============================================================================

class NativeButton:
    """Native app-style button builder"""
    
    @staticmethod
    def create_inline_button(
        text: str,
        callback_data: str,
        style: ButtonStyle = ButtonStyle.NEUTRAL,
        emoji: str = ""
    ) -> InlineKeyboardButton:
        """Create a styled inline button"""
        full_text = f"{emoji} {text}" if emoji else text
        return InlineKeyboardButton(text=full_text, callback_data=callback_data)
    
    @staticmethod
    def create_url_button(
        text: str,
        url: str,
        emoji: str = ""
    ) -> InlineKeyboardButton:
        """Create a URL button"""
        full_text = f"{emoji} {text}" if emoji else text
        return InlineKeyboardButton(text=full_text, url=url)
    
    @staticmethod
    def create_keyboard(
        buttons: List[List[InlineKeyboardButton]]
    ) -> InlineKeyboardMarkup:
        """Create inline keyboard from button grid"""
        return InlineKeyboardMarkup(buttons)


# ============================================================================
# KEYBOARD LAYOUTS (Main Menu Styles)
# ============================================================================

class KeyboardLayouts:
    """Pre-built keyboard layouts for native feel"""
    
    @staticmethod
    def main_menu() -> InlineKeyboardMarkup:
        """Main menu with primary actions"""
        keyboard = [
            [
                InlineKeyboardButton("📤 Upload Tests", callback_data="upload_tests"),
                InlineKeyboardButton("⚙️ Format Select", callback_data="select_format"),
            ],
            [
                InlineKeyboardButton("📊 Consolidate", callback_data="consolidate"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ],
            [
                InlineKeyboardButton("⏹️ Cancel", callback_data="cancel"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def upload_prompt() -> InlineKeyboardMarkup:
        """Keyboard during file upload"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Done Uploading", callback_data="upload_done"),
                InlineKeyboardButton("📋 View Files", callback_data="view_files"),
            ],
            [
                InlineKeyboardButton("🔄 Clear Files", callback_data="clear_files"),
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def format_selection() -> InlineKeyboardMarkup:
        """Format selection keyboard"""
        keyboard = [
            [
                InlineKeyboardButton("📊 Excel (.xlsx)", callback_data="format_excel"),
                InlineKeyboardButton("📄 Word (.docx)", callback_data="format_docx"),
            ],
            [
                InlineKeyboardButton("🎨 PDF", callback_data="format_pdf"),
                InlineKeyboardButton("🗒️ CSV", callback_data="format_csv"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def consolidate_confirm() -> InlineKeyboardMarkup:
        """Consolidation confirmation"""
        keyboard = [
            [
                InlineKeyboardButton("✅ Start Consolidation", callback_data="start_consolidate"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_consolidate"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def result_actions(task_id: str) -> InlineKeyboardMarkup:
        """Result action buttons"""
        keyboard = [
            [
                InlineKeyboardButton("📥 Download", callback_data=f"download_{task_id}"),
                InlineKeyboardButton("👁️ Preview", callback_data=f"preview_{task_id}"),
            ],
            [
                InlineKeyboardButton("🔄 Start Over", callback_data="back_to_main"),
                InlineKeyboardButton("📊 View Stats", callback_data=f"stats_{task_id}"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def settings_menu() -> InlineKeyboardMarkup:
        """Settings menu"""
        keyboard = [
            [
                InlineKeyboardButton("🎨 Theme: Light", callback_data="theme_dark"),
            ],
            [
                InlineKeyboardButton("🔔 Notifications: ON", callback_data="notifications_off"),
            ],
            [
                InlineKeyboardButton("📝 About", callback_data="about"),
                InlineKeyboardButton("🔗 GitHub", callback_data="github"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Help menu"""
        keyboard = [
            [
                InlineKeyboardButton("📖 Getting Started", callback_data="help_start"),
                InlineKeyboardButton("🎯 Features", callback_data="help_features"),
            ],
            [
                InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
                InlineKeyboardButton("🐛 Report Bug", callback_data="help_bug"),
            ],
            [
                InlineKeyboardButton("⬅️ Back", callback_data="back_to_main"),
            ]
        ]
        return InlineKeyboardMarkup(keyboard)


# ============================================================================
# MESSAGE TEMPLATES (Native App Styling)
# ============================================================================

class MessageTemplates:
    """Pre-built message templates with native styling"""
    
    @staticmethod
    def welcome_message() -> str:
        """Welcome message"""
        return """
╔════════════════════════════════════╗
║  🚀 MLJ Results Compiler           ║
║     Hypersonic Document Platform   ║
╚════════════════════════════════════╝

👋 Welcome! I'm your intelligent document processor.

✨ What I can do:
  • 📤 Consolidate test results
  • 📊 Merge Excel files
  • 🧠 Learn document formats
  • ⚡ Process at hypersonic speed

🎯 Ready to get started?

Select an action above or type /help for more information.
        """
    
    @staticmethod
    def status_uploading(file_count: int) -> str:
        """Status during upload"""
        return f"""
╔════════════════════════════════════╗
║  📤 UPLOAD IN PROGRESS             ║
╚════════════════════════════════════╝

✅ Files received: {file_count}

📋 Test files uploaded:
"""
    
    @staticmethod
    def status_consolidating() -> str:
        """Status during consolidation"""
        return """
╔════════════════════════════════════╗
║  ⚙️  PROCESSING...                 ║
╚════════════════════════════════════╝

🔄 Consolidating test results...

⏱️  This usually takes 1-2 seconds
        """
    
    @staticmethod
    def result_success(stats: Dict[str, Any]) -> str:
        """Success result message"""
        return f"""
╔════════════════════════════════════╗
║  ✅ CONSOLIDATION COMPLETE         ║
╚════════════════════════════════════╝

📊 Results Summary:
  • Total participants: {stats.get('total_participants', 0)}
  • Tests processed: {stats.get('tests_processed', 0)}
  • Format: {stats.get('format', 'XLSX')}
  • File size: {stats.get('file_size', '0 MB')}

⏱️  Processing time: {stats.get('time_ms', 0)}ms

Your consolidated results are ready to download! 📥
        """
    
    @staticmethod
    def error_message(error: str, suggestion: str = "") -> str:
        """Error message with suggestion"""
        msg = f"""
╔════════════════════════════════════╗
║  ❌ ERROR OCCURRED                 ║
╚════════════════════════════════════╝

⚠️  {error}
"""
        if suggestion:
            msg += f"\n💡 Suggestion: {suggestion}\n"
        return msg
    
    @staticmethod
    def file_list(files: List[str]) -> str:
        """Display list of uploaded files"""
        msg = "📋 Uploaded Files:\n\n"
        for i, file in enumerate(files, 1):
            msg += f"  {i}. ✅ {file}\n"
        return msg
    
    @staticmethod
    def progress_bar(current: int, total: int, label: str = "") -> str:
        """Visual progress bar"""
        percentage = (current / total) * 100 if total > 0 else 0
        filled = int(percentage / 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        
        msg = f"\n{label}\n{bar} {percentage:.0f}%\n"
        return msg


# ============================================================================
# BREADCRUMB NAVIGATION
# ============================================================================

class Breadcrumb:
    """Navigation breadcrumb helper"""
    
    def __init__(self):
        self.path: List[str] = []
    
    def add(self, step: str):
        """Add breadcrumb step"""
        self.path.append(step)
    
    def pop(self):
        """Remove last step"""
        if self.path:
            self.path.pop()
    
    def reset(self):
        """Clear breadcrumb"""
        self.path = []
    
    def render(self) -> str:
        """Render breadcrumb"""
        if not self.path:
            return ""
        return " > ".join(self.path)
    
    def render_with_emoji(self) -> str:
        """Render breadcrumb with emoji separator"""
        emojis = {
            "Main": "🏠",
            "Upload": "📤",
            "Format": "⚙️",
            "Consolidate": "📊",
            "Result": "✅",
        }
        
        parts = []
        for step in self.path:
            emoji = emojis.get(step, "➡️")
            parts.append(f"{emoji} {step}")
        
        return " > ".join(parts) if parts else ""


# ============================================================================
# NOTIFICATION BADGES
# ============================================================================

class Badge:
    """Status badge indicators"""
    
    @staticmethod
    def success(text: str) -> str:
        return f"✅ {text}"
    
    @staticmethod
    def error(text: str) -> str:
        return f"❌ {text}"
    
    @staticmethod
    def warning(text: str) -> str:
        return f"⚠️  {text}"
    
    @staticmethod
    def info(text: str) -> str:
        return f"ℹ️  {text}"
    
    @staticmethod
    def processing(text: str) -> str:
        return f"⏳ {text}"
    
    @staticmethod
    def new(text: str) -> str:
        return f"🆕 {text}"


# ============================================================================
# CARD LAYOUTS (For structured display)
# ============================================================================

class Card:
    """Card-style message layout"""
    
    @staticmethod
    def simple(title: str, content: str, emoji: str = "📌") -> str:
        """Simple card"""
        return f"""
╔═══════════════════════════════════╗
║ {emoji} {title:<25} ║
╠═══════════════════════════════════╣
║ {content}
╚═══════════════════════════════════╝
        """
    
    @staticmethod
    def stat_card(title: str, value: str, unit: str = "") -> str:
        """Stat card for displaying numbers"""
        return f"""
┌─────────────────────────┐
│ {title}
│ 
│ {value} {unit}
└─────────────────────────┘
        """
    
    @staticmethod
    def action_card(title: str, actions: List[str]) -> str:
        """Action card with list of options"""
        msg = f"\n{title}\n\n"
        for action in actions:
            msg += f"  • {action}\n"
        return msg


# ============================================================================
# QUICK STATS DISPLAY
# ============================================================================

class StatsDisplay:
    """Display statistics in native app style"""
    
    @staticmethod
    def summary(stats: Dict[str, Any]) -> str:
        """Display stats summary"""
        return f"""
╔══════════════════════════════════╗
║  📊 CONSOLIDATION STATS          ║
╠══════════════════════════════════╣
║
║  👥 Participants:     {stats.get('participants', 0):>15}
║  📋 Tests:            {stats.get('tests', 0):>15}
║  ✅ Success Rate:     {stats.get('success_rate', 0):>14}%
║  ⏱️  Processing Time:  {stats.get('time_ms', 0):>13}ms
║  💾 File Size:        {stats.get('file_size', '0MB'):>15}
║
╚══════════════════════════════════╝
        """
    
    @staticmethod
    def detailed(stats: Dict[str, Any]) -> str:
        """Display detailed stats"""
        msg = """
╔══════════════════════════════════╗
║  📈 DETAILED ANALYSIS            ║
╠══════════════════════════════════╣
"""
        for key, value in stats.items():
            msg += f"║  {key:<18} {str(value):>13} ║\n"
        msg += "╚══════════════════════════════════╝\n"
        return msg


# ============================================================================
# CONFIRMATION DIALOGS
# ============================================================================

class Dialog:
    """Dialog for confirmations and decisions"""
    
    @staticmethod
    def confirm(title: str, message: str) -> Tuple[str, InlineKeyboardMarkup]:
        """Confirmation dialog"""
        text = f"""
╔════════════════════════════════════╗
║  ❓ {title:<27} ║
╠════════════════════════════════════╣
║  {message}
╚════════════════════════════════════╝
        """
        
        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("✅ Yes", callback_data="confirm_yes"),
                InlineKeyboardButton("❌ No", callback_data="confirm_no"),
            ]
        ])
        
        return text, keyboard
    
    @staticmethod
    def choice(title: str, options: Dict[str, str]) -> Tuple[str, InlineKeyboardMarkup]:
        """Choice dialog"""
        text = f"❓ {title}\n\nSelect one:\n"
        
        buttons = [
            [InlineKeyboardButton(label, callback_data=callback)]
            for callback, label in options.items()
        ]
        
        keyboard = InlineKeyboardMarkup(buttons)
        return text, keyboard


# ============================================================================
# LOADING ANIMATIONS
# ============================================================================

class Loader:
    """Loading animations"""
    
    SPINNERS = [
        "⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"
    ]
    
    @staticmethod
    def get_spinner(frame: int) -> str:
        """Get spinner frame"""
        return Loader.SPINNERS[frame % len(Loader.SPINNERS)]
    
    @staticmethod
    def progress_dot(current: int) -> str:
        """Dot progress indicator"""
        dots = ["●○○", "○●○", "○○●"]
        return dots[current % len(dots)]


if __name__ == "__main__":
    # Example usage
    print(MessageTemplates.welcome_message())
    print("\n" + "="*40 + "\n")
    print(MessageTemplates.status_uploading(3))
    print(MessageTemplates.file_list(["Test 1.xlsx", "Test 2.xlsx", "Test 3.xlsx"]))
    print("\n" + "="*40 + "\n")
    print(StatsDisplay.summary({
        'participants': 150,
        'tests': 3,
        'success_rate': 98.5,
        'time_ms': 245,
        'file_size': '2.3 MB'
    }))
