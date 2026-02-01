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
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import asyncio
from src.excel_processor import ExcelProcessor
from src.participation_bonus import ParticipationBonusCalculator
from src.session_manager import SessionManager
from src.ai_assistant import get_assistant
from src.async_ai_service import get_async_ai_service

router = APIRouter(prefix="/api/hybrid", tags=["hybrid"])

# In-memory session storage (in production, use Redis/database)
UPLOAD_SESSIONS = {}
SESSION_TIMEOUT = 3600  # 1 hour
LAST_ACTIVITY = datetime.now()  # Track last API activity

session_manager = SessionManager()

def cleanup_old_sessions():
    """Remove expired sessions (both memory and filesystem)"""
    now = datetime.now()
    expired = [sid for sid, data in UPLOAD_SESSIONS.items() 
               if now - data['created'] > timedelta(seconds=SESSION_TIMEOUT)]
    for sid in expired:
        # CRITICAL FIX: Also clean up filesystem
        temp_dir = Path(f"temp_uploads/{sid}")
        if temp_dir.exists():
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as e:
                import logging
                logging.warning(f"Failed to cleanup {temp_dir}: {e}")
        
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
        processor = ExcelProcessor("temp_uploads", "temp_uploads")
        
        # Load each file as a test (numbered 1, 2, 3, etc.)
        for idx, file_path in enumerate(file_paths, start=1):
            success = processor.load_test_file(Path(file_path), test_number=idx)
            if not success:
                raise Exception(f"Failed to load file: {file_path}")
        
        # Consolidate all loaded tests
        consolidated_data = processor.consolidate_results()
        
        if not consolidated_data:
            raise Exception("No data could be consolidated from the uploaded files")
        
        # Add bonus if requested
        if include_grade_6:
            bonus_calc = ParticipationBonusCalculator()
            # Determine test numbers from the data
            test_numbers = []
            if consolidated_data:
                first_entry = next(iter(consolidated_data.values()))
                for key in first_entry.keys():
                    if key.startswith('test_') and key.endswith('_score'):
                        try:
                            test_num = int(key.split('_')[1])
                            test_numbers.append(test_num)
                        except (ValueError, IndexError):
                            pass
            test_numbers = sorted(test_numbers) if test_numbers else [1, 2, 3, 4, 5]
            consolidated_data = bonus_calc.apply_bonuses_to_consolidated(consolidated_data, test_numbers)
        
        # Store result
        result_id = str(uuid.uuid4())
        output_dir = Path(f"temp_uploads/{session_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        result_filename = f"consolidated_{result_id}.xlsx"
        
        # Use absolute path to ensure file is found
        result_path = str(output_dir.resolve() / result_filename)
        
        # Save using the correct method - set output_dir as Path object
        processor.output_dir = output_dir
        processor.save_consolidated_file(consolidated_data, result_filename)
        
        # Verify file was saved
        if not os.path.exists(result_path):
            raise Exception(f"Failed to save result file: {result_path}")
        
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

async def execute_data_transformations(session_id: str, actions: list) -> dict:
    """
    CRITICAL FIX: Execute data transformations for chat-initiated requests.
    This bridges the gap between chat interface and data execution pipeline.
    """
    if session_id not in UPLOAD_SESSIONS:
        return {"success": False, "error": "Session not found"}
    
    session = UPLOAD_SESSIONS[session_id]
    
    if not session.get("consolidation_result"):
        return {"success": False, "error": "No consolidated data available"}
    
    try:
        assistant = get_assistant()
        assistant.session_context = {
            "files_count": len(session.get("files", [])),
            "status": session.get("status"),
            "has_results": True,
            "result_path": session["consolidation_result"].get("path")
        }
        
        result = assistant.execute_data_actions(session_id, actions)
        return result
    except Exception as e:
        import logging
        logging.error(f"Data transformation error: {e}")
        return {"success": False, "error": str(e)}

@router.post("/ai-assist")
async def ai_assist(request: Request):
    """Augmented Intelligence endpoint - context-aware assistance"""
    record_activity()
    
    try:
        body = await request.json()
        message = body.get('message', '')
        session_id = body.get('session_id')
        
        if not message:
            return {"error": "No message provided"}
        
        # Build session context for awareness
        context = {}
        if session_id and session_id in UPLOAD_SESSIONS:
            session = UPLOAD_SESSIONS[session_id]
            context = {
                "files_count": len(session.get("files", [])),
                "status": session.get("status"),
                "has_results": session.get("consolidation_result") is not None,
                "error": session.get("error")
            }
        
        # Get assistant with context
        assistant = get_assistant()
        
        # CRITICAL FIX: Check if user is asking for data actions
        data_request = assistant.parse_data_request(message)
        
        if data_request.get("execute") and data_request.get("actions"):
            # User is asking for data manipulation - execute directly
            # Get consolidated data first
            if session_id and session_id in UPLOAD_SESSIONS:
                session = UPLOAD_SESSIONS[session_id]
                if session.get("consolidation_result"):
                    # Execute data actions and return result
                    try:
                        result = await execute_data_transformations(
                            session_id=session_id,
                            actions=data_request.get("actions")
                        )
                        return {
                            "response": f"✓ Completed: {message}. Your results are ready to download.",
                            "intent": "data_action",
                            "action_result": result,
                            "success": result.get("success", False),
                            "timestamp": datetime.now().isoformat(),
                            "augmented": True,
                            "data_modified": True
                        }
                    except Exception as action_error:
                        return {
                            "error": str(action_error),
                            "response": f"I understood your request, but encountered an error: {str(action_error)}",
                            "intent": "data_action",
                            "success": False
                        }
                else:
                    return {
                        "response": "I understand you want to modify data, but no consolidation results found. Please upload and consolidate files first.",
                        "intent": "data_action",
                        "action_result": None,
                        "success": False
                    }
            else:
                return {
                    "response": "I understand you want to modify data, but no session found. Please create a session first.",
                    "intent": "data_action",
                    "action_result": None,
                    "success": False
                }
        
        # Otherwise, analyze with context awareness (conversational response)
        async_ai = get_async_ai_service()
        analysis = await async_ai.analyze_message_async(message, session_id, context)
        
        # Handle suggested action if any
        action_result = None
        if analysis.get("action"):
            assistant = get_assistant()
            action_result = assistant.execute_action(analysis["action"], session_id)
        
        return {
            "response": analysis["response"],
            "intent": analysis.get("intent"),
            "action": action_result,
            "timestamp": analysis["timestamp"],
            "augmented": analysis.get("augmented", False),
            "data_modified": False
        }
    except Exception as e:
        import traceback
        return {
            "error": str(e),
            "response": "Sorry, I encountered an issue. Could you try that again?",
            "trace": traceback.format_exc()
        }

@router.post("/ai-mode")
async def set_ai_mode(request: Request):
    """Switch AI assistant mode (consolidation / cold_email)"""
    record_activity()
    
    try:
        body = await request.json()
        mode = body.get('mode', 'consolidation')
        
        assistant = get_assistant()
        result = assistant.set_mode(mode)
        
        return {
            "success": result["success"],
            "mode": assistant.get_mode(),
            "message": f"Switched to {mode} mode" if result["success"] else result.get("error")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/ai-mode")
async def get_ai_mode():
    """Get current AI assistant mode"""
    record_activity()
    assistant = get_assistant()
    return {"mode": assistant.get_mode()}


@router.post("/cold-email/generate")
async def generate_cold_email(request: Request):
    """
    Generate precision cold email with explicit reasoning.
    
    Request body:
    {
        "recipient_name": "John Smith",
        "company": "TechCorp",
        "role_focus": "SaaS growth marketing",
        "research_notes": "Recently launched new product...",
        "links": ["https://techcorp.com", "https://linkedin.com/in/johnsmith"],
        "your_offering": "AI-powered email outreach automation",
        "your_credentials": "Helped 50+ companies increase response rates by 3x",
        "your_name": "Jane Doe",
        "your_title": "Founder"
    }
    """
    record_activity()
    
    try:
        body = await request.json()
        
        # Set mode to cold_email
        assistant = get_assistant()
        assistant.set_mode("cold_email")
        
        # Generate
        result = assistant.generate_cold_email(body)
        
        return result
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }


@router.get("/ai-health")
async def ai_health():
    """
    Get AI assistant health report.
    Returns system status, error rates, and recommendations.
    """
    record_activity()
    assistant = get_assistant()
    return assistant.get_health_report()


@router.post("/ai-diagnose")
async def ai_diagnose():
    """
    Trigger self-diagnosis and get actionable insights.
    This is the 'agentic rescue' capability - the AI checks itself.
    """
    record_activity()
    assistant = get_assistant()
    return assistant.trigger_self_diagnosis()


@router.get("/ai-logs")
async def ai_logs(hours: int = Query(24, description="Hours of logs to retrieve")):
    """
    Get recent AI error and health logs.
    Useful for debugging and monitoring.
    """
    record_activity()
    
    from pathlib import Path
    from datetime import datetime, timedelta
    import json
    
    logs = {
        "errors": [],
        "health": [],
        "recoveries": [],
        "period_hours": hours
    }
    
    log_dir = Path("logs/ai_health")
    cutoff = datetime.now() - timedelta(hours=hours)
    
    def read_recent_logs(path, key):
        if path.exists():
            try:
                with open(path, 'r') as f:
                    for line in f:
                        try:
                            entry = json.loads(line)
                            ts = datetime.fromisoformat(entry.get("timestamp", "2000-01-01"))
                            if ts > cutoff:
                                logs[key].append(entry)
                        except:
                            continue
            except Exception as e:
                logs[key] = [{"error": str(e)}]
    
    read_recent_logs(log_dir / "error_log.jsonl", "errors")
    read_recent_logs(log_dir / "health_log.jsonl", "health")
    read_recent_logs(log_dir / "recovery_log.jsonl", "recoveries")
    
    # Summary
    logs["summary"] = {
        "total_errors": len(logs["errors"]),
        "total_recoveries": len(logs["recoveries"]),
        "health_checks": len(logs["health"]),
        "recovery_rate": len([r for r in logs["recoveries"] if r.get("success")]) / max(len(logs["recoveries"]), 1)
    }
    
    return logs


# ==================== AGENTIC DATA MANIPULATION ====================

@router.post("/data-action/{session_id}")
async def execute_data_action(session_id: str, request: Request):
    """
    Execute data manipulation actions on consolidated data.
    
    This is TRUE AGENTIC capability - the AI modifies data based on natural language.
    
    Request body can be either:
    1. Natural language: {"message": "Add random scores and grade them pass/fail"}
    2. Direct actions: {"actions": [{"action": "add_random_scores", "params": {...}}]}
    """
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    
    if session.get("status") != "completed" or not session.get("consolidation_result"):
        return {
            "success": False,
            "error": "No consolidated data available. Please consolidate files first."
        }
    
    try:
        body = await request.json()
        assistant = get_assistant()
        
        # Pass session context including result path
        result_info = session["consolidation_result"]
        assistant.session_context = {
            "files_count": len(session.get("files", [])),
            "status": session.get("status"),
            "has_results": True,
            "result_path": result_info.get("path")
        }
        
        # Determine if natural language or direct actions
        if "message" in body:
            # Parse natural language into actions
            message = body["message"]
            parsed = assistant.parse_data_request(message)
            
            if not parsed["execute"] or not parsed["actions"]:
                return {
                    "success": False,
                    "error": "Could not understand the data modification request",
                    "understood": parsed["understood"],
                    "hint": "Try: 'Add random scores', 'Add grades based on Score', 'Add pass/fail status'"
                }
            
            actions = parsed["actions"]
        else:
            # Direct actions provided
            actions = body.get("actions", [])
        
        if not actions:
            return {
                "success": False,
                "error": "No actions specified"
            }
        
        # Execute the actions
        result = assistant.execute_data_actions(session_id, actions)
        
        if result["success"]:
            # Update session with modification info
            session["last_modification"] = {
                "timestamp": datetime.now().isoformat(),
                "actions": [a["action"] for a in actions],
                "columns_added": result.get("stats", {}).get("columns_added", [])
            }
        
        return result
        
    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }


@router.get("/data-actions")
async def get_available_data_actions():
    """Get list of available data manipulation actions"""
    record_activity()
    
    try:
        from src.data_agent import get_data_agent
        agent = get_data_agent()
        return {
            "success": True,
            "actions": agent.get_available_actions(),
            "examples": [
                {"message": "Add random scores to each participant"},
                {"message": "Add letter grades based on Score column"},
                {"message": "Add pass/fail status with threshold 60"},
                {"message": "Collate all score columns and get the average"},
                {"message": "Add rankings based on Total_Score"},
                {"message": "Sort by Score descending"},
                {"message": "Apply participation bonus based on tests taken"}
            ]
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/data-preview/{session_id}")
async def preview_data(session_id: str, rows: int = Query(10, description="Number of rows to preview")):
    """Preview consolidated data (first N rows)"""
    record_activity()
    
    if session_id not in UPLOAD_SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = UPLOAD_SESSIONS[session_id]
    
    if session.get("status") != "completed" or not session.get("consolidation_result"):
        return {
            "success": False,
            "error": "No consolidated data available"
        }
    
    try:
        import pandas as pd
        result_path = session["consolidation_result"]["path"]
        data = pd.read_excel(result_path)
        
        return {
            "success": True,
            "total_rows": len(data),
            "columns": list(data.columns),
            "preview": data.head(rows).to_dict(orient="records"),
            "last_modification": session.get("last_modification")
        }
    except Exception as e:
        return {"success": False, "error": str(e)}