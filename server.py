"""
Minimal FastAPI server for Render deployment
Serves health checks while the Telegram bot runs in the background
Also implements keepalive pings to prevent inactivity timeout
"""

import os
import asyncio
import aiohttp
from fastapi import FastAPI
import logging

app = FastAPI(title="MLJ Results Compiler Bot")
logger = logging.getLogger(__name__)

# Keepalive task
keepalive_task = None


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "MLJ Results Compiler Bot",
        "version": "1.0"
    }


@app.get("/health")
async def health():
    """Health check for monitoring"""
    return {"status": "healthy"}


async def keepalive_worker():
    """Background task that pings this server to keep it alive"""
    while True:
        try:
            await asyncio.sleep(300)  # Every 5 minutes
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:8000/health", timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        logger.debug("Server keepalive ping successful")
                    else:
                        logger.warning(f"Keepalive ping returned status {resp.status}")
        except Exception as e:
            logger.warning(f"Keepalive ping failed: {e}")


@app.on_event("startup")
async def startup_event():
    """Start keepalive task on server startup"""
    global keepalive_task
    try:
        keepalive_task = asyncio.create_task(keepalive_worker())
        logger.info("Keepalive worker started")
    except Exception as e:
        logger.warning(f"Failed to start keepalive worker: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cancel keepalive task on shutdown"""
    global keepalive_task
    if keepalive_task:
        keepalive_task.cancel()
        try:
            await keepalive_task
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
