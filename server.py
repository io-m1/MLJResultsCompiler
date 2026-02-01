"""
FastAPI server with integrated Telegram bot
Runs both the web server and bot polling in the same process
This is necessary for Render's free tier which only allows one process
"""

import os
import sys
import asyncio
import aiohttp
import logging
from pathlib import Path
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Global tasks
bot_task = None
keepalive_task = None


async def start_bot():
    """Start the Telegram bot polling"""
    try:
        logger.info("Initializing Telegram bot...")
        # Import here to avoid issues if token is not set during import
        from telegram_bot import build_application
        from dotenv import load_dotenv
        
        load_dotenv(dotenv_path='.env')
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        
        if not token:
            logger.error("TELEGRAM_BOT_TOKEN not set! Bot will not start.")
            return
        
        application = build_application(token)
        logger.info("Starting Telegram bot polling...")
        await application.run_polling(
            allowed_updates=None,
            drop_pending_updates=False,
            read_timeout=20,
            write_timeout=20,
            connect_timeout=20,
            pool_timeout=20
        )
    except Exception as e:
        logger.error(f"Fatal error in bot: {e}", exc_info=True)
        # Restart bot after 10 seconds
        await asyncio.sleep(10)
        await start_bot()


async def keepalive_worker():
    """Background task that pings Telegram to keep connection alive"""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            logger.debug("Keepalive tick")
        except asyncio.CancelledError:
            logger.info("Keepalive worker cancelled")
            break
        except Exception as e:
            logger.warning(f"Keepalive error: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI lifespan events"""
    global bot_task, keepalive_task
    
    # Startup
    try:
        logger.info("Server starting up...")
        
        # Start bot polling in background task
        bot_task = asyncio.create_task(start_bot())
        logger.info("Bot task created")
        
        # Start keepalive worker
        keepalive_task = asyncio.create_task(keepalive_worker())
        logger.info("Keepalive worker started")
        
        # Give bot a moment to start
        await asyncio.sleep(2)
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        yield
    
    finally:
        # Shutdown
        logger.info("Server shutting down...")
        
        if bot_task:
            bot_task.cancel()
            try:
                await bot_task
            except asyncio.CancelledError:
                pass
        
        if keepalive_task:
            keepalive_task.cancel()
            try:
                await keepalive_task
            except asyncio.CancelledError:
                pass
        
        logger.info("Server shutdown complete")


app = FastAPI(
    title="MLJ Results Compiler Bot",
    description="Telegram bot for consolidating test results",
    lifespan=lifespan
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "MLJ Results Compiler Bot",
        "version": "1.0",
        "bot_running": bot_task is not None and not bot_task.done() if bot_task else False
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    bot_status = "running" if (bot_task and not bot_task.done()) else "stopped"
    return {
        "status": "healthy",
        "bot": bot_status
    }


@app.get("/logs")
async def get_logs():
    """Get recent bot logs"""
    try:
        if os.path.exists('telegram_bot.log'):
            with open('telegram_bot.log', 'r') as f:
                lines = f.readlines()
                return {
                    "lines": len(lines),
                    "recent": lines[-50:] if len(lines) > 50 else lines
                }
        return {"message": "No logs yet"}
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
