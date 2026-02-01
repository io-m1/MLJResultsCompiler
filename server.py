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
bot_stop_event = None
bot_lock = threading.Lock()
bot_initialized = False


def start_bot_thread():
    """Start the Telegram bot in a separate thread (thread-safe)"""
    global bot_thread, bot_initialized
    
    # Prevent multiple bot instances from starting
    with bot_lock:
        if bot_initialized and bot_thread and bot_thread.is_alive():
            logger.warning("Bot already running, skipping duplicate initialization")
            return bot_thread
        
        if bot_initialized:
            logger.info("Previous bot instance detected, waiting for cleanup...")
            import time
            time.sleep(3)  # Wait longer for old instance to fully disconnect
        
        bot_initialized = True
    
    def bot_worker():
        try:
            import asyncio
            import time
            from telegram.error import Conflict, NetworkError
            
            logger.info("Initializing Telegram bot in background thread...")
            from telegram_bot import build_application
            from dotenv import load_dotenv
            
            load_dotenv(dotenv_path='.env')
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            
            if not token:
                logger.error("TELEGRAM_BOT_TOKEN not set! Bot will not start.")
                return
            
            # Create a new event loop for this thread
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            retry_count = 0
            max_retries = 5
            
            try:
                application = build_application(token)
                logger.info("Building bot application...")
                loop.run_until_complete(application.initialize())
                logger.info("Bot initialized")
                
                loop.run_until_complete(application.start())
                logger.info("Bot started")
                
                # Add small delay to ensure previous instance fully disconnected
                time.sleep(2)
                
                # Start the updater (handles incoming updates) with retry logic
                while retry_count < max_retries:
                    try:
                        logger.info(f"Starting polling (attempt {retry_count + 1}/{max_retries})...")
                        loop.run_until_complete(application.updater.start_polling(
                            allowed_updates=None,
                            drop_pending_updates=True,  # Drop pending to avoid old updates
                            read_timeout=20,
                            write_timeout=20,
                            connect_timeout=20,
                            pool_timeout=20
                        ))
                        
                        logger.info("Bot polling active and listening for updates")
                        retry_count = 0  # Reset retry count on success
                        
                        # Keep the loop running indefinitely
                        loop.run_forever()
                    
                    except Conflict as conflict_err:
                        retry_count += 1
                        wait_time = min(2 ** retry_count, 32)  # Exponential backoff, max 32s
                        logger.warning(f"Conflict error (attempt {retry_count}/{max_retries}): {conflict_err}")
                        logger.info(f"Another bot instance detected. Waiting {wait_time}s before retry...")
                        
                        if retry_count >= max_retries:
                            logger.error(f"Max retries exceeded. Giving up.")
                            break
                        
                        time.sleep(wait_time)
                    
                    except (NetworkError, asyncio.CancelledError) as err:
                        logger.error(f"Network/cancellation error: {err}")
                        retry_count += 1
                        
                        if retry_count >= max_retries:
                            logger.error(f"Max retries exceeded after network errors.")
                            break
                        
                        wait_time = min(2 ** retry_count, 32)
                        logger.info(f"Waiting {wait_time}s before retry...")
                        time.sleep(wait_time)
            
            except asyncio.CancelledError:
                logger.info("Bot polling cancelled")
            except Exception as poll_err:
                logger.error(f"Unexpected polling error: {poll_err}", exc_info=True)
            finally:
                # Graceful shutdown sequence
                try:
                    logger.info("Stopping updater...")
                    loop.run_until_complete(application.updater.stop())
                    logger.info("Stopping application...")
                    loop.run_until_complete(application.stop())
                    logger.info("Shutting down application...")
                    loop.run_until_complete(application.shutdown())
                    logger.info("Bot shutdown complete")
                except Exception as shutdown_err:
                    logger.warning(f"Shutdown error: {shutdown_err}")
                loop.close()
        except Exception as e:
            logger.error(f"Fatal error in bot: {e}", exc_info=True)
        finally:
            global bot_initialized
            with bot_lock:
                bot_initialized = False
    
    # Run bot in non-daemon thread (will continue even if FastAPI shuts down)
    # This keeps the bot responsive during Render spin-downs
    thread = threading.Thread(target=bot_worker, daemon=False)
    thread.start()
    logger.info("Bot thread started")
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

# Include web UI router
from src.web_ui import router as ui_router
app.include_router(ui_router)

# Include hybrid bot+web bridge API
from src.hybrid_bridge import router as hybrid_router
app.include_router(hybrid_router)


@app.get("/api/status")
async def status():
    """API status endpoint"""
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
