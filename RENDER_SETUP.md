# Render Deployment Setup Guide

## Overview
MLJ Results Compiler is deployed on Render.com (free tier) with FastAPI + Telegram bot integration.

## Prerequisites
- Render account (free tier available)
- GitHub repository linked to Render
- Telegram Bot Token
- Groq API Key

## Current Deployment Status

**Service URL:** https://mlj-results-compiler.onrender.com  
**Status:** Active (free tier with keepalive system)  
**Last Deploy:** See Render dashboard  
**Python Version:** 3.13.4  

## Environment Variables Required

### 1. **TELEGRAM_BOT_TOKEN** ✅ (Already Set)
Your Telegram bot token for @MLJ_Results_Bot  
Do NOT share this publicly.

### 2. **GROQ_API_KEY** ⚠️ (NEEDS TO BE ADDED)
Enable LLM capabilities with free Groq tier.

**Setup Steps:**

1. Get your Groq API key from https://console.groq.com
2. Go to [Render Dashboard](https://dashboard.render.com)
3. Click on your service: **MLJ-Results-Compiler**
4. Navigate to **Environment**
5. Click **Add Environment Variable**
6. Key: `GROQ_API_KEY`
7. Value: `[YOUR_GROQ_API_KEY_HERE]` (paste your key from Groq console)
8. Click **Save Changes**
9. Service automatically redeploys (check **Deploys** tab)

### Optional Environment Variables

```env
# Debug mode (default: False)
DEBUG=False

# Log level (default: INFO)
LOG_LEVEL=INFO

# Max file size for uploads (MB, default: 50)
MAX_UPLOAD_SIZE_MB=50

# Session timeout (seconds, default: 3600)
SESSION_TIMEOUT=3600
```

## Verifying Deployment

### 1. **Check Service Status**
```bash
curl https://mlj-results-compiler.onrender.com/status
```

Expected response:
```json
{
  "status": "active",
  "version": "1.0.0",
  "features": {
    "telegram_bot": true,
    "web_ui": true,
    "ai_assistant": true,
    "data_agent": true,
    "self_healing": true
  }
}
```

### 2. **Test Telegram Bot**
- Open Telegram
- Search for **@MLJ_Results_Bot**
- Send `/start`
- Should receive welcome message

### 3. **Test Web UI**
- Open https://mlj-results-compiler.onrender.com
- Create a session
- Try uploading a test file
- Run consolidation

### 4. **Test LLM Integration**
After setting GROQ_API_KEY:
- Use web UI to consolidate files
- Click "Ask AI Assistant"
- Type: "Add random scores between 70 and 100"
- Should receive AI suggestions with data modifications

### 5. **Test Data Agent**
- Complete consolidation
- Ask AI: "Add letter grades and pass/fail status"
- Watch real data transformations happen

## Health Monitoring

### Keepalive System
The service includes automatic keepalive to prevent Render free tier sleep:
- Runs every 5 minutes
- Pings `/keepalive` endpoint
- Logs to `logs/keepalive.log`

### Self-Healing Engine
Autonomous error detection and recovery:
- Monitors all API calls
- Detects and logs errors
- Attempts auto-recovery for common issues
- Creates GitHub issues if errors exceed threshold
- Health logs: `logs/ai_health/health_log.jsonl`

### Check Health Status
```bash
curl https://mlj-results-compiler.onrender.com/api/hybrid/ai-health
```

## Troubleshooting

### Issue: "AI Assistant not responding"
1. Check GROQ_API_KEY is set in Environment
2. Verify API key hasn't expired or reached limits
3. Check health endpoint: `/api/hybrid/ai-health`
4. Check logs in Render dashboard

### Issue: "File upload fails"
1. Check file size < 50MB
2. Verify file is valid Excel (.xlsx)
3. Check server logs for specific error

### Issue: "Telegram bot not responding"
1. Check TELEGRAM_BOT_TOKEN in Environment
2. Verify bot is still active in BotFather
3. Check server logs for webhook errors
4. Try `/help` command in Telegram

### Issue: "Data consolidation hangs"
1. Check input file isn't corrupted
2. Verify test data has consistent columns
3. Check server resources (Render free tier has limits)
4. Try smaller file first

## Performance Tips

### For Render Free Tier (Limited Resources)

1. **Batch Processing**
   - Use batch processor for multiple files
   - Process one file at a time instead of parallel uploads
   - Avoid uploading files > 10MB

2. **Data Agent Limits**
   - Data transformations are fast (< 1s for 1000 rows)
   - Preview mode shows changes before execution
   - Batch process large data manipulations

3. **LLM Rate Limits**
   - Groq free tier: ~30 requests/minute
   - Self-healing engine respects these limits
   - Caches responses when appropriate

4. **Session Management**
   - Sessions timeout after 1 hour
   - Download results before session expires
   - Manual cleanup: `DELETE /api/hybrid/delete/{session_id}`

## API Endpoints (Deployed)

### Core Consolidation
- `POST /api/session/create` - Create session
- `POST /api/upload/{session_id}` - Upload test files
- `GET /api/consolidate/{session_id}` - Run consolidation
- `GET /api/download/{session_id}/{result_id}` - Download results

### AI Assistant
- `POST /api/ai-assist` - Ask AI for analysis
- `POST /api/ai-mode` - Switch AI modes
- `GET /api/ai-health` - Check AI health

### Data Agent (NEW)
- `POST /api/data-action/{session_id}` - Execute data transformation
- `GET /api/data-preview/{session_id}` - Preview changes
- `GET /api/data-actions` - List available actions

### Cold Email (NEW)
- `POST /api/cold-email/generate` - Generate cold emails

### Utilities
- `GET /status` - Service status
- `GET /keepalive` - Health check
- `DELETE /api/delete/{session_id}` - Clean up session

## Deployment Pipeline

### Local Development → GitHub → Render

1. **Make changes locally**
   ```bash
   git add .
   git commit -m "Feature: Description"
   ```

2. **Push to GitHub**
   ```bash
   git push origin main
   ```

3. **Render Auto-Deploys**
   - Webhook detects push to main
   - Installs dependencies from requirements.txt
   - Runs Procfile command
   - Service redeployed in ~1-2 minutes

4. **Verify Deployment**
   - Check Render dashboard
   - Monitor `/status` endpoint
   - Test functionality

## Manual Redeployment

If you need to manually redeploy:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Select **MLJ-Results-Compiler**
3. Click **Manual Deploy** → **Deploy latest**
4. Monitor **Logs** tab for deployment progress
5. Service goes live once deployment completes

## Scaling Future Considerations

If free tier becomes insufficient:

1. **Upgrade to Paid Tier**
   - Allocates more CPU/RAM
   - No sleep/suspension
   - Better performance

2. **Database Migration**
   - Currently: In-memory sessions + local files
   - Future: PostgreSQL for session persistence
   - Future: Cloud storage (AWS S3, Google Cloud)

3. **Distributed Processing**
   - Use Celery + Redis for background tasks
   - Queue large consolidations
   - Parallel batch processing

## Support & Monitoring

### Where to Check Issues
1. Render Dashboard → **Logs** tab
2. Local: `logs/` directory
3. AI Health: `/api/hybrid/ai-logs`
4. GitHub Issues: Auto-created by self-healing engine

### Getting Help
- Check `README.md` for quick start
- Review `logs/` for error details
- Check `src/data_integrity.py` output for data issues
- Contact Groq support for LLM issues

## Next Steps

✅ **Complete:**
- Telegram bot deployed
- FastAPI server deployed
- Web UI deployed
- Data consolidation working
- Self-healing engine active

🔄 **NEXT - Set GROQ_API_KEY:**
1. Go to Render dashboard
2. Add `GROQ_API_KEY` environment variable
3. Service auto-redeploys
4. Test AI features on `/status`

📋 **Future Enhancements:**
- GraphQL API for complex queries
- WebSocket for real-time updates
- Advanced analytics dashboard
- Export to different formats (CSV, PDF, etc.)
- Scheduled batch processing
- Custom validation rules
