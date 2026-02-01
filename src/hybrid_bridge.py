"""
Hybrid Bot + Web API Bridge
Enables seamless handoff between Telegram bot and web interface
Includes keepalive mechanisms to prevent Render hibernation
Includes AI Assistant for conversational analysis
"""

from fastapi import APIRouter, File, UploadFile, Query, HTTPException, BackgroundTasks, Request
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
from src.excel_processor import ExcelProcessor
from src.participation_bonus import ParticipationBonusCalculator
from src.session_manager import SessionManager
from src.ai_assistant import get_assistant

router = APIRouter(prefix="/api/hybrid", tags=["hybrid"])

# In-memory session storage (in production, use Redis/database)
UPLOAD_SESSIONS = {}
SESSION_TIMEOUT = 3600  # 1 hour
LAST_ACTIVITY = datetime.now()  # Track last API activity

session_manager = SessionManager()

def cleanup_old_sessions():
    """Remove expired sessions"""
    now = datetime.now()
    expired = [sid for sid, data in UPLOAD_SESSIONS.items() 
               if now - data['created'] > timedelta(seconds=SESSION_TIMEOUT)]
    for sid in expired:
        del UPLOAD_SESSIONS[sid]

def record_activity():
    """Record API activity (prevents hibernation)"""
    global LAST_ACTIVITY
    LAST_ACTIVITY = datetime.now()

@router.get("/keepalive")
async def keepalive():
    """Keepalive endpoint - ping this regularly to prevent hibernation"""
    record_activity()
    return {
        "status": "alive",
        "timestamp": datetime.now().isoformat(),
        "uptime_seconds": (datetime.now() - LAST_ACTIVITY).total_seconds()
    }

@router.post("/session/create")
async def create_session(source: str = Query("web", description="Source: web or telegram")):
    """Create a new upload session"""
    record_activity()
    cleanup_old_sessions()
    
    session_id = str(uuid.uuid4())
    UPLOAD_SESSIONS[session_id] = {
        "created": datetime.now(),
        "source": source,
        "files": [],
        "status": "uploading",
        "consolidation_result": None,
        "last_activity": datetime.now()
    }
    
    return {
        "session_id": session_id,
        "web_url": f"https://mljresultscompiler.onrender.com/app?session={session_id}",
        "expires_in": SESSION_TIMEOUT
    }

@router.post("/upload/{session_id}")
async def upload_file(
    session_id: str,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    """Upload test file to session"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    session["last_activity"] = datetime.now()
    
    try:
        # Save file temporarily
        temp_dir = Path(f"temp_uploads/{session_id}")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = temp_dir / file.filename
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        session["files"].append({
            "name": file.filename,
            "size": len(content),
            "uploaded_at": datetime.now().isoformat(),
            "path": str(file_path)
        })
        
        return {
            "status": "success",
            "message": f"File '{file.filename}' uploaded",
            "files_count": len(session["files"]),
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session details and current status"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    session["last_activity"] = datetime.now()
    
    return {
        "session_id": session_id,
        "source": session["source"],
        "files": session["files"],
        "status": session["status"],
        "files_count": len(session["files"]),
        "web_url": f"https://mljresultscompiler.onrender.com/app?session={session_id}"
    }

@router.post("/consolidate/{session_id}")
async def consolidate_results(
    session_id: str,
    include_grade_6: bool = Query(True, description="Include Grade 6 bonus calculation"),
    background_tasks: BackgroundTasks = None
):
    """Consolidate uploaded files"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    session["last_activity"] = datetime.now()
    
    if not session["files"]:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    try:
        session["status"] = "consolidating"
        
        # Process files
        file_paths = [f["path"] for f in session["files"]]
        processor = ExcelProcessor()
        
        # Consolidate
        consolidated_data = processor.consolidate_multiple_files(file_paths)
        
        # Add bonus if requested
        if include_grade_6:
            bonus_calc = ParticipationBonusCalculator()
            consolidated_data = bonus_calc.calculate_bonuses(consolidated_data)
        
        # Store result
        result_id = str(uuid.uuid4())
        result_path = f"temp_uploads/{session_id}/consolidated_{result_id}.xlsx"
        processor.save_xlsx(consolidated_data, result_path)
        
        session["status"] = "completed"
        session["consolidation_result"] = {
            "result_id": result_id,
            "path": result_path,
            "data_rows": len(consolidated_data),
            "completed_at": datetime.now().isoformat()
        }
        
        return {
            "status": "success",
            "message": "Consolidation completed",
            "result_id": result_id,
            "data_rows": len(consolidated_data),
            "download_url": f"/api/hybrid/download/{session_id}/{result_id}",
            "telegram_share": f"Your results are ready! View them here: https://mljresultscompiler.onrender.com/app?session={session_id}&result={result_id}"
        }
    except Exception as e:
        session["status"] = "error"
        raise HTTPException(status_code=500, detail=f"Consolidation failed: {str(e)}")

@router.get("/download/{session_id}/{result_id}")
async def download_result(session_id: str, result_id: str):
    """Download consolidated result file"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    session["last_activity"] = datetime.now()
    
    if not session["consolidation_result"] or session["consolidation_result"]["result_id"] != result_id:
        raise HTTPException(status_code=404, detail="Result not found")
    
    result_path = session["consolidation_result"]["path"]
    if not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        result_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"consolidated_results_{result_id}.xlsx"
    )

@router.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete session and cleanup files"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Cleanup files
    temp_dir = Path(f"temp_uploads/{session_id}")
    if temp_dir.exists():
        import shutil
        shutil.rmtree(temp_dir)
    
    del UPLOAD_SESSIONS[session_id]
    
    return {"status": "success", "message": "Session deleted"}

@router.get("/status")
async def api_status():
    """Get API and system status"""
    record_activity()
    
    time_since_activity = (datetime.now() - LAST_ACTIVITY).total_seconds()
    
    return {
        "status": "online",
        "active_sessions": len(UPLOAD_SESSIONS),
        "last_activity_seconds_ago": time_since_activity,
        "hibernation_risk": "low" if time_since_activity < 600 else "high",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/ai-assist")
async def ai_assist(request: Request):
    """AI Assistant endpoint for conversational analysis"""
    record_activity()
    
    try:
        body = await request.json()
        message = body.get('message', '')
        session_id = body.get('session_id')
        history = body.get('history', [])
        
        if not message:
            return {"error": "No message provided"}
        
        # Get AI assistant
        assistant = get_assistant()
        
        # Analyze message
        analysis = assistant.analyze_message(message, session_id)
        
        # Execute recommended actions if needed
        actions_to_execute = []
        for action in analysis.get("actions", []):
            result = assistant.execute_action(action, session_id)
            actions_to_execute.append(result)
        
        return {
            "response": analysis["response"],
            "category": analysis["category"],
            "actions_executed": actions_to_execute,
            "timestamp": analysis["timestamp"]
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "response": "Sorry, I encountered an error. Please try again.",
            "trace": traceback.format_exc()
        }
    except Exception as e:
        return {
            "error": str(e),
            "response": "Sorry, I encountered an error. Please try again."
        }
