"""
FastAPI webhook runner for MLJ Results Compiler bot.
Uses Telegram webhooks so the bot can stay online on a host (Render/Railway/Fly/etc.).
Includes keep-alive mechanism to prevent free tier hibernation.
"""

import asyncio
import logging
import os
from typing import Optional
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update
import httpx

from telegram_bot import build_application

# Load env vars early
load_dotenv(dotenv_path=".env")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

TELEGRAM_BOT_TOKEN: Optional[str] = os.getenv("TELEGRAM_BOT_TOKEN")
WEBHOOK_SECRET: Optional[str] = os.getenv("WEBHOOK_SECRET")
WEBHOOK_BASE_URL: Optional[str] = os.getenv("WEBHOOK_BASE_URL")  # e.g. https://your-app.onrender.com
ENABLE_KEEP_ALIVE: bool = os.getenv("ENABLE_KEEP_ALIVE", "true").lower() in ("true", "1", "yes")
KEEP_ALIVE_INTERVAL: int = int(os.getenv("KEEP_ALIVE_INTERVAL", "840"))  # 14 minutes default

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
if not WEBHOOK_SECRET:
    raise RuntimeError("WEBHOOK_SECRET is required (choose a long random string)")
if not WEBHOOK_BASE_URL:
    logger.warning("WEBHOOK_BASE_URL is not set; remember to set it on your host before production")

app = FastAPI()
application = build_application(TELEGRAM_BOT_TOKEN)

# Background task for keep-alive
keep_alive_task: Optional[asyncio.Task] = None


async def keep_alive_ping() -> None:
    """
    Background task that periodically pings the health endpoint to prevent
    the service from sleeping on free tier hosting (Render, Railway, etc.).
    
    This runs every 14 minutes by default (configurable via KEEP_ALIVE_INTERVAL).
    Free tier services typically sleep after 15 minutes of inactivity.
    """
    if not WEBHOOK_BASE_URL:
        logger.warning("Keep-alive disabled: WEBHOOK_BASE_URL not set")
        return
    
    health_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/health"
    logger.info(f"Keep-alive task started: pinging {health_url} every {KEEP_ALIVE_INTERVAL}s")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                await asyncio.sleep(KEEP_ALIVE_INTERVAL)
                response = await client.get(health_url, timeout=10.0)
                if response.status_code == 200:
                    logger.debug(f"Keep-alive ping successful at {datetime.now()}")
                else:
                    logger.warning(f"Keep-alive ping returned status {response.status_code}")
            except Exception as e:
                logger.error(f"Keep-alive ping failed: {e}")


@app.on_event("startup")
async def startup() -> None:
    global keep_alive_task
    
    logger.info("🚀 Starting MLJ Results Compiler Bot...")
    logger.info(f"Keep-alive: {'ENABLED' if ENABLE_KEEP_ALIVE else 'DISABLED'}")
    
    # Initialize PTB application and set webhook
    await application.initialize()
    await application.start()

    if not WEBHOOK_BASE_URL:
        logger.warning("Skipping set_webhook because WEBHOOK_BASE_URL is missing")
        return

    webhook_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/webhook/{WEBHOOK_SECRET}"
    await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
    logger.info("Webhook set to %s", webhook_url)
    
    # Start keep-alive task if enabled
    if ENABLE_KEEP_ALIVE:
        keep_alive_task = asyncio.create_task(keep_alive_ping())
        logger.info("✅ Keep-alive task started to prevent hibernation")


@app.on_event("shutdown")
async def shutdown() -> None:
    global keep_alive_task
    
    logger.info("🛑 Shutting down MLJ Results Compiler Bot...")
    
    # Cancel keep-alive task
    if keep_alive_task:
        keep_alive_task.cancel()
        try:
            await keep_alive_task
        except asyncio.CancelledError:
            logger.info("Keep-alive task cancelled")
    
    await application.stop()
    await application.shutdown()


@app.get("/")
async def root() -> JSONResponse:
    """Root endpoint - redirects to health check"""
    return JSONResponse({"status": "ok", "message": "MLJ Results Compiler Bot is running"})


@app.get("/health")
async def health() -> JSONResponse:
    """
    Health check endpoint used by monitoring services and internal keep-alive.
    Returns current status and timestamp to verify the service is responsive.
    """
    return JSONResponse({
        "status": "ok",
        "service": "MLJ Results Compiler Bot",
        "timestamp": datetime.now().isoformat(),
        "keep_alive": ENABLE_KEEP_ALIVE
    })


@app.post(f"/webhook/{{secret}}")
async def telegram_webhook(request: Request, secret: str) -> JSONResponse:
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")

    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return JSONResponse({"ok": True})


# For local manual run (optional): uvicorn server:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), reload=True)
