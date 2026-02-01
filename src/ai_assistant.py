# -*- coding: utf-8 -*-
"""
AI Assistant powered by Groq LLM (Llama 3.1 70B)
Provides intelligent, context-aware responses to user queries
FREE tier: ~30 requests/minute
"""

import os
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import Groq, fallback to simple mode if not available
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False
    logger.warning("Groq not installed, using fallback mode")


class AIAssistant:
    """LLM-powered AI assistant with Groq backend"""
    
    def __init__(self):
        self.conversation_history: List[Dict] = []
        self.groq_client = None
        self.llm_enabled = False
        
        # Initialize Groq if API key is available
        api_key = os.getenv("GROQ_API_KEY")
        if GROQ_AVAILABLE and api_key:
            try:
                self.groq_client = Groq(api_key=api_key)
                self.llm_enabled = True
                logger.info("✓ Groq LLM initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Groq: {e}")
        else:
            logger.warning("GROQ_API_KEY not set, using fallback mode")
        
        # System prompt for the LLM
        self.system_prompt = """You are an intelligent AI assistant for the MLJ Results Compiler - a tool that helps educators consolidate and analyze student test results.

YOUR CAPABILITIES:
📤 Help users upload test files (XLSX, CSV formats)
🔄 Guide consolidation of multiple test files into one
📊 Explain the bonus calculation system
📥 Assist with downloading processed results
🛠️ Troubleshoot issues and errors
🎓 Explain how the system works

BONUS SYSTEM (Grade 6):
- 1-2 tests participated: 5% bonus
- 3-5 tests participated: 10% bonus  
- 6+ tests participated: 15% bonus
Bonuses reward consistent participation and improve final scores.

HOW IT WORKS:
1. User uploads multiple test result Excel files
2. System merges all data intelligently
3. Calculates participation bonuses automatically
4. Generates a clean, professional consolidated spreadsheet
5. User downloads the final result

COMMUNICATION STYLE:
- Be helpful, friendly, and concise
- Use emojis sparingly but effectively
- Provide step-by-step guidance when needed
- If user reports an error, be empathetic and offer solutions
- Keep responses focused and actionable

Remember: You're helping educators save hours of manual work!"""

        # Fallback knowledge base (used when LLM is unavailable)
        self.fallback_responses = {
            "consolidate": "🔧 I can help you consolidate your test files!\n\n1️⃣ Upload your Excel files\n2️⃣ Click 'Consolidate Files'\n3️⃣ Wait for processing\n4️⃣ Download your result\n\nNeed more help?",
            "upload": "📤 To upload files:\n\n1. Click the upload area or drag files\n2. Select your XLSX or CSV files\n3. You can upload multiple files at once\n4. Click 'Consolidate' when ready",
            "bonus": "💰 Bonus System:\n\n📊 Grade 6 Participation Bonus:\n• 1-2 tests: +5%\n• 3-5 tests: +10%\n• 6+ tests: +15%\n\nThe more tests a student takes, the higher their bonus!",
            "download": "📥 To download results:\n\n1. Complete the consolidation first\n2. Go to the Results tab\n3. Click the 'Download' button\n4. Your XLSX file will download",
            "error": "🛠️ Let me help troubleshoot!\n\nCommon fixes:\n• Refresh the page and try again\n• Check your file format (XLSX/CSV)\n• Ensure files have valid data\n• Try uploading one file at a time\n\nStill stuck? Describe the issue!",
            "default": "👋 I'm your AI assistant! I can help with:\n\n• 📤 Uploading test files\n• 🔄 Consolidating results\n• 📊 Understanding bonuses\n• 📥 Downloading results\n• 🛠️ Troubleshooting\n\nWhat would you like to do?"
        }
    
    def analyze_message(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Analyze user message and provide intelligent response"""
        
        # Record interaction
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "user",
            "content": message,
            "session_id": session_id
        })
        
        # Try LLM first, fallback if unavailable
        if self.llm_enabled:
            try:
                response = self._get_llm_response(message)
                return response
            except Exception as e:
                logger.error(f"LLM error: {e}, using fallback")
                return self._get_fallback_response(message)
        else:
            return self._get_fallback_response(message)
    
    def _get_llm_response(self, message: str) -> Dict:
        """Get response from Groq LLM"""
        
        # Build conversation context (last 5 messages for context)
        messages = [{"role": "system", "content": self.system_prompt}]
        
        # Add recent history for context
        recent_history = self.conversation_history[-10:]  # Last 10 messages
        for entry in recent_history[:-1]:  # Exclude current message
            role = entry.get("role", "user")
            if role in ["user", "assistant"]:
                messages.append({
                    "role": role,
                    "content": entry.get("content", "")
                })
        
        # Add current message
        messages.append({"role": "user", "content": message})
        
        # Call Groq API
        completion = self.groq_client.chat.completions.create(
            model="llama-3.1-70b-versatile",  # FREE on Groq!
            messages=messages,
            max_tokens=500,
            temperature=0.7,
            top_p=0.9
        )
        
        response_text = completion.choices[0].message.content
        
        # Record assistant response
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response_text,
            "model": "llama-3.1-70b"
        })
        
        # Detect if any actions should be suggested
        actions = self._detect_actions(message, response_text)
        
        return {
            "response": response_text,
            "category": "llm",
            "actions": actions,
            "timestamp": datetime.now().isoformat(),
            "model": "llama-3.1-70b-versatile",
            "llm_powered": True
        }
    
    def _get_fallback_response(self, message: str) -> Dict:
        """Fallback response when LLM is unavailable"""
        message_lower = message.lower()
        
        # Simple keyword matching
        if any(word in message_lower for word in ["consolidate", "merge", "combine"]):
            response = self.fallback_responses["consolidate"]
            category = "consolidation"
        elif any(word in message_lower for word in ["upload", "file", "add"]):
            response = self.fallback_responses["upload"]
            category = "upload"
        elif any(word in message_lower for word in ["bonus", "score", "grade", "percent"]):
            response = self.fallback_responses["bonus"]
            category = "bonus"
        elif any(word in message_lower for word in ["download", "result", "get"]):
            response = self.fallback_responses["download"]
            category = "results"
        elif any(word in message_lower for word in ["error", "problem", "issue", "fail", "broken", "not working"]):
            response = self.fallback_responses["error"]
            category = "error"
        else:
            response = self.fallback_responses["default"]
            category = "general"
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "role": "assistant",
            "content": response
        })
        
        return {
            "response": response,
            "category": category,
            "actions": [],
            "timestamp": datetime.now().isoformat(),
            "llm_powered": False
        }
    
    def _detect_actions(self, message: str, response: str) -> List[str]:
        """Detect if any actions should be executed based on context"""
        actions = []
        combined = (message + " " + response).lower()
        
        if "upload" in combined and "how" in message.lower():
            actions.append("guide_to_upload")
        if "download" in combined and ("ready" in combined or "result" in combined):
            actions.append("show_results")
        if "error" in message.lower() or "problem" in message.lower():
            actions.append("troubleshoot")
        
        return actions
    
    def execute_action(self, action: str, session_id: Optional[str] = None) -> Dict:
        """Execute recommended actions"""
        actions_map = {
            "guide_to_upload": {
                "action": "guide_upload",
                "message": "📤 Opening upload guide..."
            },
            "show_results": {
                "action": "show_results", 
                "message": "📊 Showing your results..."
            },
            "troubleshoot": {
                "action": "troubleshoot",
                "message": "🔧 Running diagnostics..."
            }
        }
        
        return actions_map.get(action, {"action": action, "message": "Processing..."})
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "llm_enabled": self.llm_enabled,
            "model": "llama-3.1-70b-versatile" if self.llm_enabled else "fallback",
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None
        }
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []


# Singleton instance
_assistant_instance = None

def get_assistant() -> AIAssistant:
    """Get or create AI assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = AIAssistant()
    return _assistant_instance
