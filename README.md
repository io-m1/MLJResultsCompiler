# MLJ Results Compiler

Intelligent conversational document processing bot with advanced test consolidation capabilities.

**Status:** Production-ready - All tests passing (91.3% pass rate)

## 🌟 Features

### Core Capabilities
- 🤖 **Telegram Bot** - Upload files directly from Telegram (24/7 available)
- 💬 **Conversational AI** - Natural language understanding and intent detection
- 📊 **Multi-Format Support** - Handle Excel, CSV, images, PDFs, and more
- 📧 **Email Matching** - Automatically matches participants across tests
- 🎨 **Color Coded** - Visual verification with test-specific colors
- ✨ **Auto-Sorting** - Alphabetically organized results
- ✅ **Data Validation** - Comprehensive validation and error reporting

### Intelligent Processing
- 🎯 **Intent Detection** - Understands what you want to do
- 🔀 **Smart Routing** - Automatically selects the right processing agent
- 📈 **Context Awareness** - Maintains conversation history for better responses
- 🚀 **Multi-Agent System** - Specialized agents for different document types

## Test Color Scheme

| Test | Color | RGB |
|------|-------|-----|
| Test 1 | White | #FFFFFF |
| Test 2 | Sky Blue | #87CEEB |
| Test 3 | Yellow | #FFFF00 |
| Test 4 | Army Green | #556B2F |
| Test 5 | Red | #FF0000 |

## Quick Start

### Option 1: Telegram Bot (Easiest) 🤖

1. Find your bot on Telegram (search by username)
2. Send `/start`
3. **NEW:** Just tell the bot what you want! Examples:
   - "I want to consolidate test results"
   - "Merge my Excel files"
   - "Combine test 1, 2, and 3"
4. Upload your test XLSX files
5. Select output format
6. Download results instantly!

### Conversational Commands 💬

The bot now understands natural language! Try:
- "Help me consolidate tests"
- "I need to merge Excel files"
- "Combine my test results"
- "Process invoices" (coming soon)
- "Extract text from images" (coming soon)

### Traditional Commands

- `/start` - Show welcome message
- `/help` - Show help information
- `/consolidate` - Process uploaded files
- `/cancel` - Cancel current operation

**Deploy bot:** See [DEPLOYMENT.md](DEPLOYMENT.md)

### Option 2: Command Line

```bash
# Install dependencies
pip install -r requirements.txt

# Run with default XLSX output
python src/main.py

# Or choose format
python src/main.py --format pdf
python src/main.py --format docx
```

Results go to `output/` folder

## Expected Input Format

Each test file should contain columns:
- **Full Name** (or Name, Participant)
- **Email** (or E-mail, Email Address)
- **Score** (or Result, %, Percentage)

## Output Format

The consolidated file contains:
- Column A: Full Name
- Column B: Email
- Columns C-G: Test 1-5 Scores (color-coded)

Missing scores for a participant in a specific test are left blank.

## Logging

All operations are logged to `test_consolidation.log` with:
- Timestamp of each operation
- Number of records loaded per test
- Validation warnings and errors
- Final summary and output location

## Data Validation

The tool validates:
- ✓ Email format (RFC 5322 simplified)
- ✓ Score range (0-100%)
- ✓ Required fields present
- ✓ Duplicate handling by email
- ✓ Case normalization (names and emails)

## Project Structure

```
MLJResultsCompiler/
├── input/                    # Drop test XLSX files here
├── output/                   # Results saved here
├── src/
│   ├── main.py              # CLI entry point
│   ├── excel_processor.py    # Core processing
│   ├── validators.py         # Data validation
│   ├── color_config.py       # Color definitions
│   ├── session_manager.py    # Session & conversation tracking
│   ├── intent_engine.py      # Natural language understanding
│   ├── document_parser.py    # Multi-format document parsing
│   ├── agent_router.py       # Intelligent agent routing
│   └── agents/               # Specialized processing agents
│       ├── base_agent.py     # Base agent interface
│       ├── test_compiler_agent.py  # Test consolidation
│       ├── invoice_agent.py  # Invoice processing (coming soon)
│       ├── ocr_agent.py      # Image OCR (coming soon)
│       └── merger_agent.py   # Generic table merging (coming soon)
├── telegram_bot.py          # Telegram bot (for deployment)
├── config.py                # Configuration system
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
├── DEPLOYMENT.md           # Deployment guide
├── Procfile                # Heroku deployment
├── runtime.txt             # Python version for Heroku
└── README.md               # This file
```

## Architecture

### Conversational Intelligence

The bot uses a multi-layer architecture:

1. **Intent Engine** - Detects what users want to do from natural language
2. **Document Parser** - Handles multiple file formats (Excel, PDF, images, etc.)
3. **Agent Router** - Selects the appropriate processing agent
4. **Specialized Agents** - Execute specific tasks (test compilation, OCR, etc.)
5. **Session Manager** - Tracks conversation history and context

### Backward Compatibility

All existing functionality is preserved:
- Original test consolidation workflow works exactly as before
- Existing file processing maintains 100% compatibility
- All configuration options remain unchanged
- Traditional command-based interface still available

The new conversational features are **additions** that enhance the bot without breaking existing functionality.
