#!/usr/bin/env python
"""
MLJ Results Compiler - Main Entrypoint
Handles application startup, shutdown, and orchestration.

Single entry point for all deployment modes (web, bot, combined).
Replaces: server.py (merged here)
"""

import asyncio
import logging
import signal
import threading
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings, validate_settings
from src.session_storage import get_session_db
from src.async_ai_service import initialize_async_ai, shutdown_async_ai
from src.async_data_agent import initialize_async_data_agent, shutdown_async_data_agent
from src.async_file_io import initialize_async_file_io, shutdown_async_file_io

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global bot thread and state
bot_thread = None
bot_lock = threading.Lock()
bot_initialized = False


def start_bot_thread():
    """Start Telegram bot in background thread (if enabled)"""
    global bot_thread, bot_initialized
    
    settings = get_settings()
    if not settings.ENABLE_TELEGRAM_BOT:
        logger.info("Telegram bot disabled (ENABLE_TELEGRAM_BOT=false)")
        return None
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        logger.warning("TELEGRAM_BOT_TOKEN not set, bot will not start")
        return None
    
    with bot_lock:
        if bot_initialized and bot_thread and bot_thread.is_alive():
            logger.warning("Bot already running, skipping duplicate")
            return bot_thread
        bot_initialized = True
    
    def bot_worker():
        try:
            import time
            from dotenv import load_dotenv
            
            logger.info("Initializing Telegram bot in background thread...")
            
            # Wait for old instance to disconnect
            time.sleep(3)
            
            load_dotenv(dotenv_path='.env')
            
            # Import here to avoid circular imports
            try:
                from telegram_bot import build_application
                from telegram.error import Conflict, NetworkError, TelegramError
            except Exception as e:
                logger.error(f"Failed to import telegram_bot: {e}")
                return
            
            token = os.getenv('TELEGRAM_BOT_TOKEN')
            if not token:
                logger.error("TELEGRAM_BOT_TOKEN not available in bot thread")
                return
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            async def run_bot_with_retry():
                retry_count = 0
                max_retries = 10
                
                while retry_count < max_retries:
                    application = None
                    try:
                        application = build_application(token)
                        await application.initialize()
                        logger.info("✓ Bot initialized")
                        
                        # Delete any lingering webhook
                        try:
                            await application.bot.delete_webhook(drop_pending_updates=True)
                        except:
                            pass
                        
                        await application.start()
                        await application.updater.start_polling()
                        logger.info("✓ Bot started and polling")
                        logger.info("Bot is now listening for updates...")
                        
                        # Keep running until cancelled
                        while True:
                            await asyncio.sleep(3600)
                        
                    except Conflict as e:
                        retry_count += 1
                        wait_time = 15 if retry_count == 1 else min(3 ** retry_count, 120)
                        logger.error(f"Bot conflict #{retry_count}/{max_retries}: {e}")
                        logger.warning(f"Waiting {wait_time}s...")
                        
                        if application:
                            try:
                                await application.stop()
                            except:
                                pass
                        
                        await asyncio.sleep(wait_time)
                    
                    except (TelegramError, NetworkError) as e:
                        retry_count += 1
                        wait_time = min(2 ** retry_count, 60)
                        logger.warning(f"Bot network error #{retry_count}: {e}")
                        
                        if application:
                            try:
                                await application.stop()
                            except:
                                pass
                        
                        await asyncio.sleep(wait_time)
                    
                    except Exception as e:
                        retry_count += 1
                        logger.error(f"Bot error #{retry_count}: {e}", exc_info=True)
                        await asyncio.sleep(5)
                
                logger.error(f"Bot max retries ({max_retries}) exceeded")
            
            try:
                loop.run_until_complete(run_bot_with_retry())
            except Exception as e:
                logger.error(f"Fatal bot error: {e}", exc_info=True)
            finally:
                loop.close()
        
        except Exception as e:
            logger.error(f"Bot thread fatal error: {e}", exc_info=True)
        finally:
            global bot_initialized
            with bot_lock:
                bot_initialized = False
    
    thread = threading.Thread(target=bot_worker, daemon=False)
    thread.start()
    logger.info("✓ Bot thread started")
    return thread



@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Handles startup and graceful shutdown.
    """
    global bot_thread
    
    # STARTUP
    logger.info("=" * 60)
    logger.info("🚀 MLJ Results Compiler Starting")
    logger.info("=" * 60)
    
    try:
        # Validate settings
        logger.info("Validating configuration...")
        validate_settings()
        settings = get_settings()
        logger.info(f"  Environment: {settings.ENV}")
        logger.info(f"  Database: {settings.DATABASE_URL}")
        logger.info(f"  AI Enabled: {settings.ENABLE_AI_ASSISTANT}")
        logger.info(f"  Telegram Bot: {settings.ENABLE_TELEGRAM_BOT}")
        
        # Initialize database
        logger.info("Initializing database...")
        db = get_session_db()
        stats = db.get_session_statistics()
        logger.info(f"  Database initialized")
        logger.info(f"  Existing sessions: {stats['total_sessions']}")
        
        # Cleanup old sessions on startup
        logger.info("Cleaning up expired sessions...")
        cleaned = db.cleanup_expired_sessions()
        logger.info(f"  Removed {cleaned} expired sessions")
        
        # Initialize async services
        logger.info("Initializing async services...")
        await initialize_async_ai()
        await initialize_async_data_agent()
        await initialize_async_file_io()
        logger.info("✓ Async services initialized")
        
        # Start Telegram bot (if enabled)
        logger.info("Starting Telegram bot (if enabled)...")
        bot_thread = start_bot_thread()
        
        # Register shutdown signal handlers
        def signal_handler(sig, frame):
            logger.warning(f"Received signal {sig}, initiating shutdown...")
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        logger.info("✓ Application started successfully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Startup error: {e}", exc_info=True)
        raise
    
    yield  # Application is running
    
    # SHUTDOWN
    logger.info("=" * 60)
    logger.info("🛑 MLJ Results Compiler Shutting Down")
    logger.info("=" * 60)
    
    try:
        # Cleanup async services
        logger.info("Shutting down async services...")
        await shutdown_async_ai()
        await shutdown_async_data_agent()
        await shutdown_async_file_io()
        logger.info("✓ Async services shutdown")
        
        # Cleanup
        logger.info("Closing database connections...")
        db.cleanup_expired_sessions()
        logger.info("✓ Database cleaned up")
        
        # Cleanup old files
        settings = get_settings()
        upload_dir = Path(settings.UPLOAD_DIR)
        if upload_dir.exists():
            import shutil
            for item in upload_dir.iterdir():
                if item.is_dir():
                    try:
                        shutil.rmtree(item, ignore_errors=True)
                    except Exception as e:
                        logger.warning(f"Failed to cleanup {item}: {e}")
        
        logger.info("✓ Application shut down gracefully")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Shutdown error: {e}", exc_info=True)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    settings = get_settings()
    
    # Create app with lifespan context
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Excel consolidation and grading system with Telegram bot",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.DEBUG else ["https://mljresultscompiler.onrender.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Healthcheck endpoint for monitoring and load balancers"""
        try:
            db = get_session_db()
            stats = db.get_session_statistics()
            return {
                "status": "healthy",
                "version": settings.APP_VERSION,
                "environment": settings.ENV,
                "database": "ok",
                "sessions_active": stats["total_sessions"],
                "ai_enabled": settings.ENABLE_AI_ASSISTANT,
                "bot_enabled": settings.ENABLE_TELEGRAM_BOT,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "version": settings.APP_VERSION,
            }, 503
    
    # Ping endpoint for keepalive
    @app.get("/ping", tags=["ping"])
    async def ping():
        """Minimal ping endpoint for keepalive systems"""
        return {"status": "pong"}
    
    # Status endpoint
    @app.get("/status", tags=["status"])
    async def status():
        """Detailed system status"""
        db = get_session_db()
        stats = db.get_session_statistics()
        settings = get_settings()
        
        return {
            "app_name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENV,
            "database": {
                "url": settings.DATABASE_URL,
                "status": "ok",
            },
            "sessions": {
                "total": stats["total_sessions"],
                "completed": stats["completed_sessions"],
                "pending": stats["total_sessions"] - stats["completed_sessions"],
            },
            "operations": {
                "uploads": stats["total_uploads"],
                "consolidations": stats["total_results"],
                "transformations": stats["total_transformations"],
            },
            "features": {
                "ai_assistant": settings.ENABLE_AI_ASSISTANT,
                "telegram_bot": settings.ENABLE_TELEGRAM_BOT,
            },
        }
    
    # Import and register routers
    try:
        from src.web_ui_clean import router as web_ui_router
        app.include_router(web_ui_router)
        logger.info("✓ Registered web UI router")
    except Exception as e:
        logger.warning(f"Failed to load web UI router: {e}")
    
    try:
        from src.hybrid_bridge import router as hybrid_router
        app.include_router(hybrid_router, prefix="/api")
        logger.info("✓ Registered hybrid API router")
    except Exception as e:
        logger.warning(f"Failed to load hybrid router: {e}")
    
    return app


# Create global app instance for uvicorn/deployment
app = create_app()


def main():
    """Main entry point - runs the application"""
    import uvicorn
    
    settings = get_settings()
    
    # Run with Uvicorn
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        workers=1 if settings.DEBUG else settings.WORKERS,
        reload=settings.RELOAD and settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )


if __name__ == "__main__":
    main()
