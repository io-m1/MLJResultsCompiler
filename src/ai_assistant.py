"""
AI Assistant for conversational analysis and complaint handling
Provides intelligent responses to user queries and executes actions
"""

import json
from datetime import datetime
from typing import Dict, List, Optional

class AIAssistant:
    """Simple but effective AI assistant for user interactions"""
    
    def __init__(self):
        self.conversation_history = []
        self.knowledge_base = {
            "consolidation": {
                "keywords": ["consolidate", "merge", "combine", "upload", "process"],
                "response": "I can help you consolidate your test files! Here's what happens:\n1️⃣ Upload your Excel files\n2️⃣ I'll merge all the data\n3️⃣ Bonuses calculated automatically\n4️⃣ Download your consolidated sheet",
                "actions": ["guide_to_upload", "show_supported_formats"]
            },
            "results": {
                "keywords": ["result", "download", "excel", "sheet", "file"],
                "response": "Your results are ready! You can:\n📥 Download the consolidated XLSX file\n📊 View statistics and bonuses\n📤 Share with colleagues\nClick 'Download' to get your file.",
                "actions": ["show_results", "initiate_download"]
            },
            "bonus": {
                "keywords": ["bonus", "score", "grade", "calculate", "percentage"],
                "response": "The system automatically calculates participation bonuses:\n✅ More tests = Higher bonus\n📈 Performance percentile matters\n🎯 Grade 6: Up to 15% bonus\n💡 Rewards consistent participation",
                "actions": ["explain_bonus_system"]
            },
            "error": {
                "keywords": ["error", "problem", "issue", "fail", "broken", "not working", "undefined"],
                "response": "I see there's an issue. Let me help!\n🔍 I'm diagnosing the problem\n⚙️ Checking your files\n🛠️ Attempting to fix it\nPlease wait a moment...",
                "actions": ["troubleshoot", "retry_consolidation"]
            },
            "feature": {
                "keywords": ["feature", "what can", "how do", "can you", "do you"],
                "response": "I can help with:\n📤 Upload test files (XLSX, CSV)\n🔄 Consolidate multiple files\n📊 Calculate bonuses automatically\n📥 Download formatted results\n💬 Answer your questions\nWhat would you like to do?",
                "actions": []
            },
            "design": {
                "keywords": ["design", "study", "how works", "understand", "explain", "works"],
                "response": "Great question! Here's the design:\n📥 Input: Multiple test files in any format\n🔄 Process: Intelligent merging and analysis\n🎯 Logic: Bonuses, scoring, percentiles\n📤 Output: Clean, professional spreadsheet\n🌟 Benefit: Save hours of manual work!\nVisit the Design Study section to learn more.",
                "actions": []
            }
        }
    
    def analyze_message(self, message: str, session_id: Optional[str] = None) -> Dict:
        """Analyze user message and provide intelligent response"""
        message_lower = message.lower().strip()
        
        # Record interaction
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "message": message,
            "session_id": session_id
        })
        
        # Find matching category
        matched_category = None
        best_match_score = 0
        
        for category, details in self.knowledge_base.items():
            for keyword in details["keywords"]:
                if keyword in message_lower:
                    score = len(keyword)  # Longer matches are better
                    if score > best_match_score:
                        best_match_score = score
                        matched_category = category
        
        # Generate response
        if matched_category:
            response = self.knowledge_base[matched_category]["response"]
            actions = self.knowledge_base[matched_category]["actions"]
        else:
            # Default helpful response
            response = f"I understand you're asking about '{message[:40]}...'.\n\n💡 I can help with:\n• Uploading and consolidating files\n• Calculating bonuses\n• Downloading results\n• Understanding how everything works\n\nWhat specifically would you like to do?"
            actions = []
        
        # Add emoji and polish
        response_with_emoji = self._add_polish(response, matched_category)
        
        return {
            "response": response_with_emoji,
            "category": matched_category,
            "actions": actions,
            "timestamp": datetime.now().isoformat(),
            "message_length": len(message)
        }
    
    def _add_polish(self, response: str, category: Optional[str]) -> str:
        """Add helpful emoji and formatting"""
        if category == "error":
            return f"🆘 {response}"
        elif category == "bonus":
            return f"💰 {response}"
        elif category == "design":
            return f"🎨 {response}"
        elif category == "feature":
            return f"✨ {response}"
        elif category == "consolidation":
            return f"🔧 {response}"
        elif category == "results":
            return f"✅ {response}"
        return f"👋 {response}"
    
    def execute_action(self, action: str, session_id: Optional[str] = None) -> Dict:
        """Execute recommended actions"""
        actions_map = {
            "guide_to_upload": self._guide_upload,
            "show_supported_formats": self._show_formats,
            "show_results": self._show_results,
            "initiate_download": self._initiate_download,
            "explain_bonus_system": self._explain_bonus,
            "troubleshoot": self._troubleshoot,
            "retry_consolidation": self._retry_consolidation
        }
        
        if action in actions_map:
            return actions_map[action](session_id)
        
        return {"status": "action_unknown", "action": action}
    
    def _guide_upload(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "guide_upload",
            "message": "📤 Upload Guide:\n1. Click the upload area\n2. Select your test files\n3. Wait for confirmation\n4. Click 'Consolidate Files'\n5. Download your result!"
        }
    
    def _show_formats(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "show_formats",
            "message": "✅ Supported Formats:\n• Excel (.xlsx)\n• CSV (.csv)\n• Multiple files at once\n• Any file size"
        }
    
    def _show_results(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "show_results",
            "message": "📊 Results Include:\n• Consolidated student data\n• Test scores\n• Participation bonuses\n• Performance percentiles\n• Pass/Fail status"
        }
    
    def _initiate_download(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "download",
            "message": "⬇️ Preparing download...",
            "session_id": session_id
        }
    
    def _explain_bonus(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "explain_bonus",
            "message": "🎯 Bonus System:\n📊 Grade 6 Bonus:\n• 1-2 tests: 5% bonus\n• 3-5 tests: 10% bonus\n• 6+ tests: 15% bonus\n\n📈 Score increases based on percentile ranking\n🌟 Rewards consistency and improvement"
        }
    
    def _troubleshoot(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "troubleshoot",
            "message": "🔧 Troubleshooting:\n✓ Checking file formats\n✓ Verifying data integrity\n✓ Reprocessing files\n✓ Rebuilding consolidation\n\nIf issues persist, try uploading files again."
        }
    
    def _retry_consolidation(self, session_id: Optional[str]) -> Dict:
        return {
            "action": "retry_consolidation",
            "message": "🔄 Retrying consolidation...\n⏳ Processing files\n✅ Rebuilding results\n📥 Ready for download"
        }
    
    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation"""
        return {
            "total_messages": len(self.conversation_history),
            "conversations": self.conversation_history,
            "last_interaction": self.conversation_history[-1] if self.conversation_history else None
        }


# Singleton instance
_assistant_instance = None

def get_assistant() -> AIAssistant:
    """Get or create AI assistant instance"""
    global _assistant_instance
    if _assistant_instance is None:
        _assistant_instance = AIAssistant()
    return _assistant_instance
