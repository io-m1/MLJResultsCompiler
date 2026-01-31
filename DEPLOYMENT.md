# Deployment Guide: MLJ Results Compiler Bot on Render

## Overview
This bot runs 24/7 on Render (free tier) with webhooks. No local terminal needed after deploy.

---

## Quick Start (5 mins)

### 1. Push Code to GitHub
```bash
git add requirements.txt .gitignore
git commit -m "Deploy: Fix pandas, add webhook server, ignore .env"
git push origin main
```

### 2. Create Render Account
- Go to https://render.com
- Sign up with GitHub (easier)
- Authorize access to `io-m1/MLJResultsCompiler`

### 3. Deploy Web Service
1. Dashboard → **New** → **Web Service**
2. Select repo: `io-m1/MLJResultsCompiler`
3. Branch: `main`
4. Fill form:
   - **Name**: `mlj-bot`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (plenty for this bot)

### 4. Set Environment Variables
Before clicking "Create Web Service", click **Advanced**:
- Add these env vars:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `8444096191:AAGNqie79FQ0oixHOgPX-oh2EwlnkDRSq-I` |
| `WEBHOOK_SECRET` | `your-super-secret-random-string-xyz` |

### 5. Deploy & Note Your URL
- Click **Create Web Service**
- Wait 2-3 mins for build
- Copy your service URL from dashboard (e.g., `https://mlj-bot.onrender.com`)

### 6. Set WEBHOOK_BASE_URL
1. Render Dashboard → Your Service → **Environment**
2. Click **Edit**
3. Add: `WEBHOOK_BASE_URL` = `https://mlj-bot.onrender.com` (your actual URL)
4. Click **Save** (auto-redeploys with webhook set)

### 7. Verify Deployment
- Open `https://<your-service>.onrender.com/` → should see `{"status":"ok"}`
- In Telegram: send `/start` to **@mlj_results_compiler_bot**
- Should respond with welcome message ✅

---

## What Happens on Deploy
1. Render clones your repo
2. Installs `requirements.txt` (pandas, fastapi, telegram bot, etc.)
3. Runs `uvicorn server:app --host 0.0.0.0 --port $PORT`
4. `server.py` starts, initializes bot, and auto-sets webhook on startup
5. Bot listens on `https://your-service.onrender.com/webhook/<WEBHOOK_SECRET>`
6. Telegram sends updates to webhook URL → bot processes instantly

---

## Webhook Flow
```
User sends /start to bot
    ↓
Telegram → WEBHOOK_BASE_URL/webhook/WEBHOOK_SECRET (POST)
    ↓
FastAPI endpoint validates secret, feeds update to bot
    ↓
Bot processes, sends response back to Telegram
    ↓
User sees response in chat
```

---

## Files Explained
- `server.py` - FastAPI webhook server (receives Telegram updates)
- `telegram_bot.py` - Bot logic (handlers, processing)
- `requirements.txt` - Dependencies (pandas 2.2.3, fastapi, uvicorn, etc.)
- `.gitignore` - Excludes `.env` (secrets stay local)

---

## Troubleshooting

### Bot not responding
1. Check Render logs: Dashboard → Your Service → **Logs**
2. Verify env vars are set (copy exact values, no typos)
3. Check WEBHOOK_BASE_URL matches your Render service URL

### "Connection refused" or 502 error
- Render is still building (wait 2-3 mins)
- Or check if Start Command is correct: `uvicorn server:app --host 0.0.0.0 --port $PORT`

### Webhook not being called
- Telegram might still have old polling config
- Delete webhook: `curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook?drop_pending_updates=true"`
- Server will auto-set new webhook on restart

---

## Local Testing (Optional)
To test locally before deploying:
```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN=<your token>
export WEBHOOK_SECRET=test-secret
export WEBHOOK_BASE_URL=http://localhost:8000

uvicorn server:app --reload --port 8000
```
Use ngrok or similar for HTTPS tunnel if testing webhooks locally.

---

## Monitoring & Logs
1. Render Dashboard → Your Service → **Logs**
2. See bot activity in real-time
3. Errors/warnings appear here

---

## Next Steps
✅ Code ready
✅ Secrets in .env (ignored in git)
✅ Webhook server configured
→ Just deploy on Render!

**Questions?** Check Render docs: https://render.com/docs
