# MLJ Results Compiler

Hybrid Telegram Bot + Web App for consolidating test results with AI assistance.

**Status:** Production Ready | 100% Test Coverage

## Key Features

- **Telegram Bot + Web Mini App** - Dual interface access
- **Automatic Consolidation** - Email-matched result merging
- **Participation Bonuses** - Grade 6 intelligent bonus calculation
- **Clean UI Design** - Technical logic hidden from users
- **AI Assistant** - Conversational analysis and support
- **Design Study Section** - Non-technical model explanation
- **Session Management** - Keepalive prevents hibernation
- **Deployment Ready** - Auto-deploy to Render

## Quick Start

### Via Telegram
1. Find `@mlj_results_compiler_bot` on Telegram
2. `/start` to begin
3. Upload Excel files
4. Consolidation happens automatically
5. Download results

### Via Web App
1. Visit https://mljresultscompiler.onrender.com
2. Upload tab → Select files
3. Click "Consolidate Files"
4. Download from Results tab

### Local Testing
```bash
pip install -r requirements.txt
python test_web_live.py    # Run comprehensive tests
```

## Pre-Deployment

```bash
# Verify build before deploying
.\verify-build.ps1
```

## Project Structure

```
src/
  web_ui_clean.py         # Clean web UI (4 tabs)
  ai_assistant.py         # Conversational AI
  hybrid_bridge.py        # Session-based API
  excel_processor.py      # Data consolidation
  participation_bonus.py  # Bonus calculation

server.py                 # FastAPI + Bot orchestrator
telegram_bot.py          # Telegram integration
test_web_live.py         # Comprehensive test suite
verify-build.ps1         # Pre-deployment verification
requirements.txt         # Python dependencies
.env                     # Environment config
```

## Dependencies

11 core packages:
- FastAPI, Uvicorn (web server)
- python-telegram-bot (bot framework)
- Openpyxl (Excel processing)
- Aiohttp (async HTTP)
- Requests (HTTP client)

## Testing

All tests passing:
- Module imports
- AI Assistant chat
- Session management
- API endpoints (8)
- UI template validation
- Excel processing
- Data flow validation
- Security features
- Environment setup

## Deployment

Auto-deploys to Render on `git push`:
```bash
git add .
git commit -m "Your message"
git push origin main
```

## Documentation

- `BUILD_VERIFICATION_GUIDE.md` - Pre-deployment script guide
- Code comments explain key functions
- Tests serve as usage examples
