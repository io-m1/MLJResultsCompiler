"""
Session Management Agent for MLJ Bot
Tracks user sessions, uploaded files, and consolidation workflow state
"""

import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions and file tracking"""
    
    def __init__(self):
        self.sessions = {}  # {user_id: session_data}
    
    def get_session(self, user_id: int) -> Dict:
        """Get or create user session"""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'user_id': user_id,
                'created_at': datetime.now(),
                'uploaded_files': {},  # {test_num: file_path}
                'temp_dir': tempfile.mkdtemp(),
                'state': 'waiting_for_files',  # waiting_for_files, ready_to_consolidate
                'messages': []
            }
            logger.info(f"Created new session for user {user_id}")
        
        return self.sessions[user_id]
    
    def add_file(self, user_id: int, file_path: str, test_num: int) -> Dict:
        """Add a file to user session"""
        session = self.get_session(user_id)
        
        # If file for this test already exists, replace it
        if test_num in session['uploaded_files']:
            old_path = session['uploaded_files'][test_num]
            try:
                Path(old_path).unlink()
                logger.info(f"Replaced Test {test_num} file for user {user_id}")
            except Exception as e:
                logger.warning(f"Could not delete old file: {e}")
        
        session['uploaded_files'][test_num] = file_path
        session['messages'].append(f"[OK] Test {test_num} file received")
        
        # Update session state based on files
        session['state'] = self.determine_state(session)
        
        return self.get_session_summary(user_id)
    
    def get_session_summary(self, user_id: int) -> Dict:
        """Get session summary for user feedback"""
        session = self.get_session(user_id)
        uploaded = sorted(session['uploaded_files'].keys())
        
        return {
            'tests_uploaded': uploaded,
            'count': len(uploaded),
            'messages': session['messages'],
            'can_consolidate': 1 in uploaded,  # Test 1 must be present
            'state': self.determine_state(session)
        }
    
    def determine_state(self, session: Dict) -> str:
        """Agentic reasoning: Determine what state session should be in"""
        uploaded = session['uploaded_files']
        
        # Decision tree for state
        if 1 not in uploaded:
            return 'waiting_for_test1'  # Must have Test 1
        elif len(uploaded) == 1:
            return 'can_consolidate_alone'  # Can process Test 1 alone
        else:
            return 'ready_to_consolidate'  # Have Test 1 + others
    
    def get_files_for_consolidation(self, user_id: int) -> Dict[int, str]:
        """Get uploaded files ready for consolidation"""
        session = self.get_session(user_id)
        return session['uploaded_files'].copy()
    
    def clear_session(self, user_id: int) -> bool:
        """Clear session and cleanup temp files"""
        if user_id not in self.sessions:
            return False
        
        session = self.sessions[user_id]
        try:
            if Path(session['temp_dir']).exists():
                shutil.rmtree(session['temp_dir'])
            del self.sessions[user_id]
            logger.info(f"Cleared session for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error clearing session: {e}")
            return False
    
    def format_status_message(self, user_id: int) -> str:
        """Format session status as Telegram message"""
        summary = self.get_session_summary(user_id)
        tests = summary['tests_uploaded']
        state = summary['state']
        
        msg = "[FILE STATUS]\n\n"
        msg += f"Uploaded: {len(tests)} file(s)\n"
        
        if tests:
            msg += "[OK] Tests: " + ", ".join([f"Test {t}" for t in tests]) + "\n\n"
        else:
            msg += "No files uploaded yet\n\n"
        
        # State-based guidance
        if state == 'waiting_for_test1':
            msg += "[REQUIRED] Test 1 is required to start consolidation\n"
            msg += "Send Test 1 file first"
        elif state == 'can_consolidate_alone':
            msg += "[READY] You can:\n"
            msg += "- Send more tests (2-5) for comparison\n"
            msg += "- Or press /consolidate to process Test 1 alone"
        elif state == 'ready_to_consolidate':
            msg += f"[READY] Ready to consolidate!\n"
            msg += f"Press /consolidate to merge all {len(tests)} tests"
        
        return msg


class WorkflowAgent:
    """Agent for orchestrating consolidation workflow"""
    
    @staticmethod
    def should_consolidate(session: Dict) -> bool:
        """Agentic reasoning: Should consolidation happen?"""
        # Only consolidate if:
        # 1. User explicitly requests it (handled by command)
        # 2. Test 1 exists (required base)
        return 1 in session['uploaded_files']
    
    @staticmethod
    def get_next_action(session: Dict) -> str:
        """Agentic reasoning: What should bot do next?"""
        uploaded = session['uploaded_files']
        
        if not uploaded:
            return "ask_for_test1"
        elif 1 not in uploaded:
            return "ask_for_test1"
        elif len(uploaded) < 5:
            return "offer_consolidate_or_continue"  # Can accept more or consolidate
        else:
            return "ready_consolidate"
    
    @staticmethod
    def format_suggestion(action: str) -> str:
        """Format bot suggestion based on next action"""
        suggestions = {
            "ask_for_test1": "[INFO] Send Test 1 file first (required as base)",
            "offer_consolidate_or_continue": "[INFO] You can send more tests (2-5) or press /consolidate now",
            "ready_consolidate": "[OK] All 5 tests uploaded! Press /consolidate to process"
        }
        return suggestions.get(action, "Ready for next step")
