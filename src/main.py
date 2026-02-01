#!/usr/bin/env python
"""
MLJ Results Compiler - Main Entrypoint
Handles application startup, shutdown, and orchestration.

Single entry point for all deployment modes (web, bot, combined).
"""

import asyncio
import logging
import signal
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings, validate_settings
from src.session_storage import get_session_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Global app instance
app: FastAPI = None
shutdown_event: asyncio.Event = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Handles startup and graceful shutdown.
    """
    
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
        
        # Register shutdown signal handlers
        global shutdown_event
        shutdown_event = asyncio.Event()
        
        def signal_handler(sig, frame):
            logger.warning(f"Received signal {sig}, initiating shutdown...")
            shutdown_event.set()
        
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
        from src.hybrid_bridge import router as hybrid_router
        app.include_router(hybrid_router, prefix="/api")
        logger.info("✓ Registered hybrid API router")
    except Exception as e:
        logger.warning(f"Failed to load hybrid router: {e}")
    
    # Telegram bot (if enabled)
    if settings.ENABLE_TELEGRAM_BOT:
        try:
            from src import telegram_bot
            logger.info("✓ Telegram bot loaded (startup handled separately)")
        except Exception as e:
            logger.warning(f"Failed to load Telegram bot: {e}")
    
    return app


def main():
    """Main entry point - runs the application"""
    import uvicorn
    
    settings = get_settings()
    
    # Create app
    app = create_app()
    
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
