"""
FastAPI server with integrated Telegram bot
Runs both the web server and bot polling in the same process
This is necessary for Render's free tier which only allows one process
"""

import os
import sys
import threading
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

# Global bot thread
bot_thread = None


def start_bot_thread():
    """Start the Telegram bot in a separate thread"""
    def bot_worker():
        try:
            logger.info("Initializing Telegram bot in background thread...")
            from telegram_bot import build_application
            from dotenv import load_dotenv
            
            load_dotenv(dotenv_path='.env')
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            
            if not token:
                logger.error("TELEGRAM_BOT_TOKEN not set! Bot will not start.")
                return
            
            application = build_application(token)
            logger.info("Starting Telegram bot polling...")
            # run_polling() blocks in this thread, which is what we want
            application.run_polling(
                allowed_updates=None,
                drop_pending_updates=False,
                read_timeout=20,
                write_timeout=20,
                connect_timeout=20,
                pool_timeout=20
            )
        except Exception as e:
            logger.error(f"Fatal error in bot: {e}", exc_info=True)
    
    # Run bot in daemon thread (won't block server shutdown)
    thread = threading.Thread(target=bot_worker, daemon=True)
    thread.start()
    return thread


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage FastAPI lifespan events"""
    global bot_thread
    
    # Startup
    try:
        logger.info("Server starting up...")
        
        # Start bot in background thread (not async)
        bot_thread = start_bot_thread()
        logger.info("Bot thread started")
        
        # Give bot a moment to initialize
        import time
        time.sleep(2)
        
        yield
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        yield
    
    finally:
        # Shutdown
        logger.info("Server shutting down...")
        # Bot thread is daemon, so it will be terminated automatically
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
        "bot_running": bot_thread is not None and bot_thread.is_alive()
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    bot_status = "running" if (bot_thread and bot_thread.is_alive()) else "stopped"
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
