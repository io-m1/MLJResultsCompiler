"""
Minimal FastAPI server for Render deployment
Serves health checks while the Telegram bot runs in the background
"""

import os
from fastapi import FastAPI
import logging

app = FastAPI(title="MLJ Results Compiler Bot")
logger = logging.getLogger(__name__)


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


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
