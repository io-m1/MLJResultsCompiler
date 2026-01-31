# Telegram Bot Deployment Guide

This guide covers deploying the MLJ Results Compiler Telegram Bot for 24/7 operation.

## Table of Contents
1. [Create Telegram Bot](#create-telegram-bot)
2. [Deploy to Railway (Recommended)](#deploy-to-railway-recommended)
3. [Deploy to Heroku](#deploy-to-heroku)
4. [Local Testing](#local-testing)

---

## Create Telegram Bot

### Step 1: Get Your Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot`
3. Follow the prompts:
   - Name: `MLJ Results Compiler` (or your preferred name)
   - Username: `mlj_results_compiler_bot` (must be unique)
4. Copy the **HTTP API token** (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

### Step 2: Create `.env` File

In your repository root, create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and replace with your actual token:

```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
```

⚠️ **Keep this file secret!** Never commit it to GitHub. It's already in `.gitignore`.

---

## Deploy to Railway (Recommended)

Railway is free, easy, and perfect for Telegram bots!

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up (use GitHub for easiest login)
3. Authorize Railway

### Step 2: Deploy from GitHub

1. Click **New Project** → **Deploy from GitHub repo**
2. Select your `MLJResultsCompiler` repository
3. Railway auto-detects Python and installs dependencies

### Step 3: Add Environment Variables

1. Go to **Variables** in your Railway project
2. Add: `TELEGRAM_BOT_TOKEN` = your token from @BotFather
3. Click **Deploy**

### Step 4: Run the Bot

1. Go to the **Deploy** tab
2. Find the **Start Command** section
3. Set start command to:

```
python telegram_bot.py
```

Railway will run your bot continuously! ✅

### Step 5: Monitor Logs

1. Click on your deployment
2. View real-time logs to confirm bot is running
3. Test by sending `/start` to your bot on Telegram

---

## Deploy to Heroku

Heroku has limited free tier but still works well.

### Step 1: Create Heroku Account

1. Go to [heroku.com](https://heroku.com)
2. Sign up and verify email
3. Create a new app

### Step 2: Add Files for Heroku

Create `Procfile` in repo root:

```
worker: python telegram_bot.py
```

Create `runtime.txt` in repo root:

```
python-3.12.0
```

### Step 3: Configure Deployment

```bash
# Install Heroku CLI
# (download from heroku.com/download)

# Login
heroku login

# Add remote
heroku git:remote -a your-app-name

# Set environment variable
heroku config:set TELEGRAM_BOT_TOKEN=123456:ABC-DEF...

# Deploy
git push heroku main
```

### Step 4: Start Bot

```bash
heroku ps:scale worker=1
heroku logs --tail
```

---

## Local Testing

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Create `.env` File

```bash
cp .env.example .env
# Edit .env with your bot token
```

### Step 3: Run Bot Locally

```bash
python telegram_bot.py
```

You'll see:
```
INFO - Starting MLJ Results Compiler Telegram Bot
```

### Step 4: Test with Telegram

1. Open Telegram
2. Find your bot (search by username)
3. Send `/start`
4. Upload test files from `input/` folder
5. Select format
6. Get results!

---

## Troubleshooting

### Bot doesn't respond

- Check `TELEGRAM_BOT_TOKEN` is set correctly
- Verify token hasn't expired
- Check logs for errors: `heroku logs --tail` or `railway logs`

### Files not uploading

- Ensure files are `.xlsx` format
- Check file size (Telegram limit: 50 MB)
- Verify temporary directory permissions

### Processing fails

- Check processor logs
- Ensure columns match expected names
- Verify email format is valid

### Bot crashed on Railway/Heroku

- Check environment variables are set
- Review logs for Python errors
- Restart deployment

---

## Keeping Bot Running

### Railway
- Automatically runs 24/7 ✅
- No configuration needed
- Free tier includes enough credits

### Heroku
- Free tier sleeps after 30 min of inactivity
- Use paid dyno ($7/month) for continuous operation
- Or use Railway (free alternative)

---

## Next Steps

1. **Monitor Usage:** Set up error notifications
2. **Add Admin Commands:** `/stats`, `/cleanlogs`
3. **Scale Processing:** Handle multiple concurrent users
4. **Analytics:** Track bot usage metrics

---

## Support

For issues:
1. Check bot logs: `heroku logs --tail`
2. Review `telegram_bot.log` file
3. Test locally first
4. Check @BotFather for token validity

---

## Advanced: Webhook vs Polling

This bot uses **polling** (simpler, works everywhere).

For production at scale, consider **webhooks**:
- Faster response time
- Lower resource usage
- Requires public URL

Current polling setup is fine for personal/small team use!
