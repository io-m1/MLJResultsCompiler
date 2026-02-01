"""
Persistent Session Storage - Fixes daily data loss issue
Replaces in-memory storage with SQLite database
"""

import sqlite3
import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class SessionDatabase:
    """
    CRITICAL FIX: Persistent storage for user sessions.
    Replaces UPLOAD_SESSIONS dict (lost on restart) with SQLite database.
    """
    
    def __init__(self, db_path: str = "data/sessions.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    @contextmanager
    def get_connection(self):
        """Get database connection with proper cleanup"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _init_db(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL,
                    source TEXT,
                    status TEXT DEFAULT 'uploading',
                    error TEXT,
                    last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS uploads (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    size INTEGER,
                    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success',
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS consolidation_results (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    result_type TEXT,
                    file_path TEXT,
                    metadata JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE
                );
                
                CREATE TABLE IF NOT EXISTS transformations (
                    id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    action_type TEXT,
                    parameters JSON,
                    result_id TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'completed',
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE CASCADE,
                    FOREIGN KEY(result_id) REFERENCES consolidation_results(id) ON DELETE SET NULL
                );
                
                CREATE TABLE IF NOT EXISTS audit_log (
                    id TEXT PRIMARY KEY,
                    session_id TEXT,
                    event_type TEXT,
                    details JSON,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(session_id) REFERENCES sessions(id) ON DELETE SET NULL
                );
                
                CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
                CREATE INDEX IF NOT EXISTS idx_sessions_expires ON sessions(expires_at);
                CREATE INDEX IF NOT EXISTS idx_uploads_session ON uploads(session_id);
                CREATE INDEX IF NOT EXISTS idx_results_session ON consolidation_results(session_id);
                CREATE INDEX IF NOT EXISTS idx_transformations_session ON transformations(session_id);
            """)
    
    def create_session(self, source: str = "web", expires_in: int = 3600) -> str:
        """Create new session and return session_id"""
        session_id = str(uuid.uuid4())
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO sessions (id, expires_at, source)
                   VALUES (?, ?, ?)""",
                (session_id, expires_at.isoformat(), source)
            )
        
        logger.info(f"Session created: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM sessions WHERE id = ?",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None
    
    def update_session(self, session_id: str, **kwargs):
        """Update session fields"""
        allowed_fields = {"status", "error"}
        fields = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not fields:
            return
        
        fields["last_activity"] = datetime.now().isoformat()
        
        with self.get_connection() as conn:
            set_clause = ", ".join([f"{k} = ?" for k in fields])
            values = list(fields.values()) + [session_id]
            
            conn.execute(
                f"UPDATE sessions SET {set_clause} WHERE id = ?",
                values
            )
    
    def add_upload(self, session_id: str, filename: str, size: int) -> str:
        """Record file upload"""
        upload_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO uploads (id, session_id, filename, size)
                   VALUES (?, ?, ?, ?)""",
                (upload_id, session_id, filename, size)
            )
        
        logger.info(f"Upload recorded: {upload_id} ({filename})")
        return upload_id
    
    def get_uploads(self, session_id: str) -> List[Dict]:
        """Get all uploads for a session"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM uploads WHERE session_id = ? ORDER BY uploaded_at",
                (session_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    def add_consolidation_result(self, session_id: str, file_path: str, 
                                 result_type: str = "consolidation", 
                                 metadata: Dict = None) -> str:
        """Record consolidation result"""
        result_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO consolidation_results 
                   (id, session_id, file_path, result_type, metadata)
                   VALUES (?, ?, ?, ?, ?)""",
                (result_id, session_id, file_path, result_type, json.dumps(metadata or {}))
            )
        
        self.update_session(session_id, status="completed")
        logger.info(f"Result recorded: {result_id}")
        return result_id
    
    def get_consolidation_result(self, session_id: str) -> Optional[Dict]:
        """Get latest consolidation result for session"""
        with self.get_connection() as conn:
            cursor = conn.execute(
                """SELECT * FROM consolidation_results 
                   WHERE session_id = ? 
                   ORDER BY created_at DESC LIMIT 1""",
                (session_id,)
            )
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result["metadata"] = json.loads(result["metadata"])
                return result
        return None
    
    def add_transformation(self, session_id: str, action_type: str, 
                         parameters: Dict, result_id: str = None) -> str:
        """Record data transformation"""
        transformation_id = str(uuid.uuid4())
        
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO transformations 
                   (id, session_id, action_type, parameters, result_id)
                   VALUES (?, ?, ?, ?, ?)""",
                (transformation_id, session_id, action_type, json.dumps(parameters), result_id)
            )
        
        logger.info(f"Transformation recorded: {transformation_id} ({action_type})")
        return transformation_id
    
    def cleanup_expired_sessions(self, hours: int = 24):
        """Remove expired sessions and their data"""
        cutoff_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        with self.get_connection() as conn:
            # Get sessions to delete
            cursor = conn.execute(
                "SELECT id FROM sessions WHERE expires_at < ?",
                (cutoff_time,)
            )
            expired_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete them (cascades delete uploads, results, transformations)
            for session_id in expired_ids:
                conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
                logger.info(f"Cleaned up expired session: {session_id}")
        
        return len(expired_ids)
    
    def get_session_statistics(self) -> Dict:
        """Get database statistics"""
        with self.get_connection() as conn:
            stats = {}
            
            cursor = conn.execute("SELECT COUNT(*) FROM sessions")
            stats["total_sessions"] = cursor.fetchone()[0]
            
            cursor = conn.execute(
                "SELECT COUNT(*) FROM sessions WHERE status = 'completed'"
            )
            stats["completed_sessions"] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM uploads")
            stats["total_uploads"] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM consolidation_results")
            stats["total_results"] = cursor.fetchone()[0]
            
            cursor = conn.execute("SELECT COUNT(*) FROM transformations")
            stats["total_transformations"] = cursor.fetchone()[0]
        
        return stats


# Singleton instance
_db_instance: Optional[SessionDatabase] = None


def get_session_db() -> SessionDatabase:
    """Get or create session database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = SessionDatabase()
    return _db_instance
