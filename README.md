# MLJ Results Compiler

**Excel consolidation and grading system for educational results.**

Version: 0.2.0 | Status: **Alpha** | License: MIT

## What This Does

Takes messy Excel results from multiple sources, consolidates by email, applies business rules (bonuses, pass/fail), and delivers results via:
- **Telegram Bot** (real-time, mobile-friendly)
- **Web UI** (upload/download interface)

**Current Maturity:** Core pipeline works. Ready for low-volume use. Not yet enterprise-hardened.

## Proven Features ✅

- ✅ Email-matched consolidation (core logic)
- ✅ Participation bonus calculation (Grade 6)
- ✅ Clean web UI (simple upload/download)
- ✅ Telegram bot interface (command-driven)
- ✅ Session persistence (survives restarts)
- ✅ Automated CI/CD testing (GitHub Actions)

## Not Yet Ready ⚠️

- ❌ AI features (optional, feature-flagged, incomplete)
- ❌ Enterprise security (audit in progress)
- ❌ High-volume concurrency (tested for small schools)
- ❌ 100% test coverage (60% currently)

## Quick Start

### Via Telegram
```
1. @mlj_results_compiler_bot on Telegram
2. /start
3. Send Excel files
4. Results ready immediately
```

### Via Web
```
Visit: https://mljresultscompiler.onrender.com
Upload → Consolidate → Download
```

### Local Development
```bash
pip install -r requirements.txt
python -m pytest tests/
```
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
