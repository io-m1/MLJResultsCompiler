# MLJ Results Compiler

**Intelligent conversational document processing bot with advanced test consolidation capabilities.**

Version: 0.2.0 | Status: **Alpha** | License: MIT

⚡ **NEW:** Built-in hibernation prevention for free tier hosting - bot stays responsive 24/7!

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

## Currently Implemented ✅

### Core Consolidation
- ✅ Load Excel files with multiple results
- ✅ Match students by email address
- ✅ Merge duplicate entries
- ✅ Calculate participation bonuses (Grade 6 specific)
- ✅ Generate pass/fail determination
- ✅ Export consolidated results to Excel

### Interfaces
- ✅ Web UI: Upload files, view results, download consolidation
- ✅ Telegram Bot: Conversational and command-driven interaction
- ✅ REST API: Programmatic access (hybrid_bridge endpoints)

### Data & Operations
- ✅ **Session persistence**: Survives server restarts (SQLite backend)
- ✅ **Security**: Path traversal protection for file operations
- ✅ Automatic cleanup: Expired sessions removed daily
- ✅ CI/CD automation: Tests run on every commit
- ✅ Error tracking: Structured logging for debugging

## Quick Start

### Via Telegram
1. Find your bot on Telegram (search by username)
2. Send `/start`
3. Just tell the bot what you want! Examples:
   - "I want to consolidate test results"
   - "Merge my Excel files"
4. Upload your test XLSX files
5. Download results instantly!

### Via Web
Visit: `https://mljresultscompiler.onrender.com`
Upload → Consolidate → Download

## Architecture

### Multi-Agent System
The bot uses a modular agent-based architecture:
1. **Intent Engine** - Detects user intent from natural language
2. **Document Parser** - Handles multiple file formats
3. **Agent Router** - Selects the appropriate processing agent
4. **Specialized Agents** - Execute specific tasks (test compilation, OCR, etc.)

## Deployment

Auto-deploys to Render on `git push`:
```bash
git add .
git commit -m "Your message"
git push origin main
```

**Important for Free Tier Hosting:**
- Set `ENABLE_KEEP_ALIVE=true` to prevent inactivity hibernation.
- Ping interval is managed via GitHub Actions.
