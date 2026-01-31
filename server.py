"""
FastAPI webhook runner for MLJ Results Compiler bot.
Uses Telegram webhooks so the bot can stay online on a host (Render/Railway/Fly/etc.).
"""

import asyncio
import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from telegram import Update

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

if not TELEGRAM_BOT_TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN is required")
if not WEBHOOK_SECRET:
    raise RuntimeError("WEBHOOK_SECRET is required (choose a long random string)")
if not WEBHOOK_BASE_URL:
    logger.warning("WEBHOOK_BASE_URL is not set; remember to set it on your host before production")

app = FastAPI()
application = build_application(TELEGRAM_BOT_TOKEN)


@app.on_event("startup")
async def startup() -> None:
    # Initialize PTB application and set webhook
    await application.initialize()
    await application.start()

    if not WEBHOOK_BASE_URL:
        logger.warning("Skipping set_webhook because WEBHOOK_BASE_URL is missing")
        return

    webhook_url = f"{WEBHOOK_BASE_URL.rstrip('/')}/webhook/{WEBHOOK_SECRET}"
    await application.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
    logger.info("Webhook set to %s", webhook_url)


@app.on_event("shutdown")
async def shutdown() -> None:
    await application.stop()
    await application.shutdown()


@app.get("/")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


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
