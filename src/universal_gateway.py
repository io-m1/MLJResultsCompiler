"""
Universal Document Processing Gateway
Unified entry point for all capabilities
Web API, CLI, and platform-specific interfaces
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from typing import List, Optional, Dict, Any
import asyncio
from pathlib import Path
import logging
import json
from datetime import datetime

from src.hypersonic_core import hypersonic_core, ProcessingTask
from src.data_source_manager import DataSource, data_source_manager
from src.document_learning_engine import learning_engine
from src.platform_adapter import platform_bridge, PlatformMessage, PlatformResponse

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Universal Document Processor",
    description="Hypersonic lightweight document processing platform",
    version="1.0.0"
)


# ============================================================================
# INITIALIZATION
# ============================================================================

@app.on_event("startup")
async def startup():
    """Initialize all systems"""
    logger.info("Starting Universal Document Processor")
    await hypersonic_core.initialize()
    logger.info("All systems ready")


@app.on_event("shutdown")
async def shutdown():
    """Graceful shutdown"""
    logger.info("Shutting down systems")
    await hypersonic_core.shutdown()


# ============================================================================
# CORE PROCESSING ENDPOINTS
# ============================================================================

@app.post("/api/process")
async def process_documents(
    task_type: str = Form(...),
    files: List[UploadFile] = File(None),
    config: Optional[str] = Form(None)
) -> JSONResponse:
    """
    Universal document processing endpoint
    
    Args:
        task_type: Type of processing (consolidation, merge, extract, transform)
        files: Input files to process
        config: JSON config for processing
    """
    try:
        # Parse config
        task_config = json.loads(config) if config else {}
        
        # Create task
        task = ProcessingTask(
            task_id=f"task_{datetime.now().timestamp()}",
            task_type=task_type,
            config=task_config,
            priority=task_config.get('priority', 5)
        )
        
        # Handle file uploads
        if files:
            temp_dir = Path("temp_uploads")
            temp_dir.mkdir(exist_ok=True)
            
            for file in files:
                file_path = temp_dir / file.filename
                with open(file_path, 'wb') as f:
                    f.write(await file.read())
                
                logger.info(f"Uploaded: {file.filename}")
        
        # Submit task
        task_id = await hypersonic_core.submit_task(task)
        
        return JSONResponse({
            "task_id": task_id,
            "status": "submitted",
            "task_type": task_type
        })
    
    except Exception as e:
        logger.error(f"Process endpoint error: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/task/{task_id}")
async def get_task_status(task_id: str) -> JSONResponse:
    """Get task status and results"""
    task = await hypersonic_core.get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return JSONResponse({
        "task_id": task.task_id,
        "status": task.status,
        "task_type": task.task_type,
        "created_at": task.created_at.isoformat(),
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "execution_time_ms": task.execution_time_ms,
        "results": task.results,
        "errors": task.errors
    })


# ============================================================================
# API INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/api/sources/register")
async def register_data_source(source_config: Dict[str, Any]) -> JSONResponse:
    """Register a new data source (API, website, RSS, etc.)"""
    try:
        source = DataSource(
            source_id=source_config.get('source_id'),
            source_type=source_config.get('source_type'),
            url=source_config.get('url'),
            auth=source_config.get('auth'),
            headers=source_config.get('headers', {}),
            params=source_config.get('params', {}),
            refresh_interval=source_config.get('refresh_interval', 3600)
        )
        
        data_source_manager.register_source(source)
        
        return JSONResponse({
            "status": "registered",
            "source_id": source.source_id,
            "source_type": source.source_type
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/sources/{source_id}/fetch")
async def fetch_from_source(source_id: str) -> JSONResponse:
    """Fetch data from a registered source"""
    try:
        records = await data_source_manager.fetch_from_source(source_id)
        
        return JSONResponse({
            "source_id": source_id,
            "records_fetched": len(records),
            "data": [
                {
                    "record_id": r.record_id,
                    "data": r.data,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in records[:100]  # Limit to 100 for preview
            ]
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/sources/fetch-all")
async def fetch_all_sources() -> JSONResponse:
    """Fetch from all registered sources concurrently"""
    try:
        results = await data_source_manager.fetch_all()
        
        return JSONResponse({
            "sources_queried": len(results),
            "total_records": sum(len(records) for records in results.values()),
            "results": {
                source_id: {
                    "record_count": len(records),
                    "first_record": records[0].data if records else None
                }
                for source_id, records in results.items()
            }
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ============================================================================
# LEARNING & FORMAT DETECTION ENDPOINTS
# ============================================================================

@app.post("/api/learn/analyze")
async def analyze_document(
    file: UploadFile = File(...)
) -> JSONResponse:
    """Analyze document and learn its format"""
    try:
        content = await file.read()
        
        # Try to parse as different formats
        try:
            data = json.loads(content)
        except:
            data = content.decode('utf-8')
        
        # Analyze
        fmt = learning_engine.analyze_document(file.filename, data)
        
        return JSONResponse({
            "format_id": fmt.format_id,
            "confidence": fmt.confidence,
            "source_app": fmt.source_app,
            "column_patterns": fmt.column_patterns,
            "data_types": fmt.data_types,
            "sample_count": fmt.sample_count
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/learn/formats")
async def get_learned_formats() -> JSONResponse:
    """Get all learned document formats"""
    formats = []
    for fmt in learning_engine.learned_formats.values():
        formats.append({
            "format_id": fmt.format_id,
            "file_extension": fmt.file_extension,
            "source_app": fmt.source_app,
            "confidence": fmt.confidence,
            "sample_count": fmt.sample_count
        })
    
    return JSONResponse({
        "total_formats": len(formats),
        "formats": formats
    })


@app.get("/api/learn/strategy/{format_id}")
async def get_processing_strategy(format_id: str) -> JSONResponse:
    """Get optimal processing strategy for a format"""
    fmt = learning_engine.learned_formats.get(format_id)
    if not fmt:
        raise HTTPException(status_code=404, detail="Format not found")
    
    strategy = learning_engine.get_processing_strategy(fmt)
    return JSONResponse(strategy)


# ============================================================================
# PLATFORM INTEGRATION ENDPOINTS
# ============================================================================

@app.post("/webhook/telegram")
async def telegram_webhook(update: Dict[str, Any]) -> JSONResponse:
    """Telegram webhook handler"""
    # This would be handled by existing telegram_bot.py
    return JSONResponse({"ok": True})


@app.post("/webhook/slack")
async def slack_webhook(body: Dict[str, Any]) -> JSONResponse:
    """Slack event handler"""
    try:
        # Create platform message
        msg = PlatformMessage(
            platform="slack",
            user_id=body.get('user_id'),
            username=body.get('username'),
            message_id=body.get('message_id'),
            content=body.get('text'),
            timestamp=datetime.now()
        )
        
        # Route through core
        response = await platform_bridge.route_message(msg)
        
        return JSONResponse({"ok": True})
    except Exception as e:
        logger.error(f"Slack webhook error: {e}")
        return JSONResponse({"ok": False, "error": str(e)})


# ============================================================================
# MONITORING & STATS ENDPOINTS
# ============================================================================

@app.get("/health")
async def health_check() -> JSONResponse:
    """Health check endpoint"""
    stats = hypersonic_core.get_performance_stats()
    cache_info = hypersonic_core.get_cache_info()
    
    return JSONResponse({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "performance": stats,
        "cache": cache_info,
        "workers": hypersonic_core.max_workers,
        "queue_size": hypersonic_core.task_queue.qsize()
    })


@app.get("/stats")
async def get_stats() -> JSONResponse:
    """Get comprehensive statistics"""
    return JSONResponse({
        "hypersonic_core": hypersonic_core.get_performance_stats(),
        "cache": hypersonic_core.get_cache_info(),
        "learned_formats": len(learning_engine.learned_formats),
        "data_sources": len(data_source_manager.sources),
        "timestamp": datetime.now().isoformat()
    })


# ============================================================================
# DOCUMENTATION
# ============================================================================

@app.get("/")
async def root() -> Dict[str, Any]:
    """Root endpoint with API documentation"""
    return {
        "name": "Universal Document Processor",
        "version": "1.0.0",
        "description": "Hypersonic lightweight platform for document processing and data integration",
        "endpoints": {
            "core_processing": [
                "POST /api/process - Submit processing task",
                "GET /api/task/{task_id} - Get task status"
            ],
            "data_integration": [
                "POST /api/sources/register - Register data source",
                "GET /api/sources/{source_id}/fetch - Fetch from source",
                "POST /api/sources/fetch-all - Fetch from all sources"
            ],
            "learning": [
                "POST /api/learn/analyze - Analyze document format",
                "GET /api/learn/formats - Get learned formats",
                "GET /api/learn/strategy/{format_id} - Get processing strategy"
            ],
            "monitoring": [
                "GET /health - Health check",
                "GET /stats - Comprehensive statistics"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
