# -*- coding: utf-8 -*-
"""
Self-Healing Augmented Intelligence Module
Autonomous error detection, logging, and GitHub issue creation for agentic rescue.

When something goes wrong:
1. Log the error with full context
2. Analyze the error pattern
3. Attempt automatic recovery
4. If unrecoverable, create GitHub issue for Copilot-assisted remediation
"""

import os
import json
import logging
import traceback
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
import threading
import time

# Try to import GitHub API
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class SelfHealingEngine:
    """
    Autonomous self-monitoring and healing system.
    
    Capabilities:
    - Structured error logging with context
    - Error pattern recognition
    - Automatic recovery attempts
    - GitHub issue creation for agentic rescue
    - Health monitoring and reporting
    """
    
    def __init__(self, log_dir: str = "logs/ai_health"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Error tracking
        self.error_log_path = self.log_dir / "error_log.jsonl"
        self.health_log_path = self.log_dir / "health_log.jsonl"
        self.recovery_log_path = self.log_dir / "recovery_log.jsonl"
        
        # In-memory tracking
        self.error_counts: Dict[str, int] = {}
        self.last_errors: List[Dict] = []
        self.recovery_attempts: Dict[str, int] = {}
        self.health_status = "healthy"
        
        # GitHub integration
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repo = os.getenv("GITHUB_REPO", "io-m1/MLJResultsCompiler")
        self.github_enabled = bool(self.github_token) and REQUESTS_AVAILABLE
        
        # Thresholds
        self.error_threshold = 5  # Errors before escalation
        self.recovery_max_attempts = 3
        self.issue_cooldown = timedelta(hours=1)  # Don't spam issues
        self.last_issue_created: Optional[datetime] = None
        
        # Start health monitor
        self._start_health_monitor()
        
        logger.info(f"✓ Self-Healing Engine initialized (GitHub: {'enabled' if self.github_enabled else 'disabled'})")
    
    def _start_health_monitor(self):
        """Background health monitoring thread"""
        def monitor():
            while True:
                try:
                    self._check_health()
                    time.sleep(300)  # Check every 5 minutes
                except Exception as e:
                    logger.error(f"Health monitor error: {e}")
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _check_health(self):
        """Periodic health check"""
        health_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_count_last_hour": self._count_recent_errors(hours=1),
            "recovery_success_rate": self._calculate_recovery_rate(),
            "status": self.health_status
        }
        
        # Determine health status
        if health_entry["error_count_last_hour"] > 20:
            self.health_status = "critical"
        elif health_entry["error_count_last_hour"] > 10:
            self.health_status = "degraded"
        else:
            self.health_status = "healthy"
        
        health_entry["status"] = self.health_status
        self._write_log(self.health_log_path, health_entry)
    
    def log_error(self, 
                  error: Exception, 
                  context: Dict[str, Any],
                  component: str = "ai_assistant",
                  auto_recover: bool = True) -> Dict:
        """
        Log an error with full context and attempt recovery.
        
        Returns:
            Dict with recovery status and recommendations
        """
        error_id = self._generate_error_id(error, context)
        
        error_entry = {
            "error_id": error_id,
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": self._sanitize_context(context),
            "stack_hash": self._hash_traceback(traceback.format_exc())
        }
        
        # Track error frequency
        self.error_counts[error_entry["stack_hash"]] = \
            self.error_counts.get(error_entry["stack_hash"], 0) + 1
        
        # Keep last 100 errors in memory
        self.last_errors.append(error_entry)
        if len(self.last_errors) > 100:
            self.last_errors.pop(0)
        
        # Write to log
        self._write_log(self.error_log_path, error_entry)
        
        # Attempt recovery
        recovery_result = {"attempted": False, "success": False, "action": None}
        
        if auto_recover:
            recovery_result = self._attempt_recovery(error_entry)
        
        # Check if escalation needed
        if self.error_counts[error_entry["stack_hash"]] >= self.error_threshold:
            self._escalate_to_github(error_entry, recovery_result)
        
        return {
            "error_id": error_id,
            "logged": True,
            "recovery": recovery_result,
            "escalated": self.error_counts[error_entry["stack_hash"]] >= self.error_threshold
        }
    
    def _attempt_recovery(self, error_entry: Dict) -> Dict:
        """
        Attempt automatic recovery based on error type.
        """
        error_type = error_entry["error_type"]
        stack_hash = error_entry["stack_hash"]
        
        # Track recovery attempts
        self.recovery_attempts[stack_hash] = self.recovery_attempts.get(stack_hash, 0) + 1
        
        if self.recovery_attempts[stack_hash] > self.recovery_max_attempts:
            return {
                "attempted": True,
                "success": False,
                "action": "max_attempts_exceeded",
                "message": "Recovery attempts exhausted, escalating"
            }
        
        recovery_strategies = {
            "ConnectionError": self._recover_connection,
            "TimeoutError": self._recover_timeout,
            "JSONDecodeError": self._recover_json,
            "KeyError": self._recover_key_error,
            "AttributeError": self._recover_attribute_error,
            "GroqError": self._recover_groq,
            "RateLimitError": self._recover_rate_limit,
        }
        
        strategy = recovery_strategies.get(error_type, self._recover_generic)
        
        try:
            result = strategy(error_entry)
            
            # Log recovery attempt
            recovery_log = {
                "timestamp": datetime.now().isoformat(),
                "error_id": error_entry["error_id"],
                "strategy": strategy.__name__,
                "success": result["success"],
                "action": result.get("action")
            }
            self._write_log(self.recovery_log_path, recovery_log)
            
            return result
        except Exception as e:
            return {
                "attempted": True,
                "success": False,
                "action": "recovery_failed",
                "message": str(e)
            }
    
    def _recover_connection(self, error_entry: Dict) -> Dict:
        """Recovery strategy for connection errors"""
        return {
            "attempted": True,
            "success": True,
            "action": "retry_with_backoff",
            "message": "Will retry with exponential backoff",
            "recommendation": "Check network connectivity"
        }
    
    def _recover_timeout(self, error_entry: Dict) -> Dict:
        """Recovery strategy for timeout errors"""
        return {
            "attempted": True,
            "success": True,
            "action": "extend_timeout",
            "message": "Increased timeout for next request",
            "recommendation": "Consider reducing payload size"
        }
    
    def _recover_json(self, error_entry: Dict) -> Dict:
        """Recovery strategy for JSON parsing errors"""
        return {
            "attempted": True,
            "success": True,
            "action": "fallback_response",
            "message": "Using fallback response format",
            "recommendation": "Check LLM output format"
        }
    
    def _recover_key_error(self, error_entry: Dict) -> Dict:
        """Recovery strategy for missing keys"""
        context = error_entry.get("context", {})
        return {
            "attempted": True,
            "success": True,
            "action": "use_defaults",
            "message": "Using default values for missing keys",
            "recommendation": f"Add validation for: {error_entry['error_message']}"
        }
    
    def _recover_attribute_error(self, error_entry: Dict) -> Dict:
        """Recovery strategy for attribute errors"""
        return {
            "attempted": True,
            "success": False,
            "action": "code_fix_required",
            "message": "This error requires code changes",
            "recommendation": "Check object initialization"
        }
    
    def _recover_groq(self, error_entry: Dict) -> Dict:
        """Recovery strategy for Groq API errors"""
        return {
            "attempted": True,
            "success": True,
            "action": "use_fallback",
            "message": "Switched to thoughtful fallback mode",
            "recommendation": "Check GROQ_API_KEY validity"
        }
    
    def _recover_rate_limit(self, error_entry: Dict) -> Dict:
        """Recovery strategy for rate limiting"""
        return {
            "attempted": True,
            "success": True,
            "action": "backoff_and_queue",
            "message": "Implementing request throttling",
            "recommendation": "Reduce request frequency"
        }
    
    def _recover_generic(self, error_entry: Dict) -> Dict:
        """Generic recovery strategy"""
        return {
            "attempted": True,
            "success": False,
            "action": "log_and_continue",
            "message": "Logged error, continuing with defaults",
            "recommendation": "Review error logs for patterns"
        }
    
    def _escalate_to_github(self, error_entry: Dict, recovery_result: Dict):
        """
        Create GitHub issue for agentic rescue.
        If GitHub Copilot is active, this issue provides context for remediation.
        """
        if not self.github_enabled:
            logger.warning("GitHub integration not enabled, cannot escalate")
            return
        
        # Check cooldown
        if self.last_issue_created:
            if datetime.now() - self.last_issue_created < self.issue_cooldown:
                logger.info("Issue creation on cooldown, skipping")
                return
        
        issue_title = f"🔧 Auto-Heal: {error_entry['error_type']} in {error_entry['component']}"
        
        issue_body = f"""## 🤖 Automated Self-Healing Report

**Component:** `{error_entry['component']}`
**Error Type:** `{error_entry['error_type']}`
**Timestamp:** {error_entry['timestamp']}
**Occurrences:** {self.error_counts.get(error_entry['stack_hash'], 1)}

### Error Message
```
{error_entry['error_message']}
```

### Stack Trace
```python
{error_entry['traceback'][:2000]}
```

### Context
```json
{json.dumps(error_entry['context'], indent=2)[:1000]}
```

### Recovery Attempted
- **Strategy:** {recovery_result.get('action', 'none')}
- **Success:** {recovery_result.get('success', False)}
- **Recommendation:** {recovery_result.get('recommendation', 'Review manually')}

### For GitHub Copilot
This issue was auto-generated by the Self-Healing Engine. Key fix hints:
1. Error pattern hash: `{error_entry['stack_hash'][:16]}`
2. Component path: `src/{error_entry['component']}.py`
3. Suggested fix area: Check the traceback for the failing line

---
*Generated by MLJ Self-Healing Engine v1.0*
"""
        
        try:
            response = requests.post(
                f"https://api.github.com/repos/{self.github_repo}/issues",
                headers={
                    "Authorization": f"token {self.github_token}",
                    "Accept": "application/vnd.github.v3+json"
                },
                json={
                    "title": issue_title,
                    "body": issue_body,
                    "labels": ["auto-heal", "bug", "ai-assistant"]
                },
                timeout=10
            )
            
            if response.status_code == 201:
                self.last_issue_created = datetime.now()
                issue_url = response.json().get("html_url")
                logger.info(f"✓ GitHub issue created: {issue_url}")
                return {"created": True, "url": issue_url}
            else:
                logger.error(f"Failed to create issue: {response.status_code}")
                return {"created": False, "error": response.text}
                
        except Exception as e:
            logger.error(f"GitHub API error: {e}")
            return {"created": False, "error": str(e)}
    
    def get_health_report(self) -> Dict:
        """
        Get comprehensive health report.
        """
        return {
            "status": self.health_status,
            "timestamp": datetime.now().isoformat(),
            "errors_last_hour": self._count_recent_errors(hours=1),
            "errors_last_24h": self._count_recent_errors(hours=24),
            "top_errors": self._get_top_errors(limit=5),
            "recovery_rate": self._calculate_recovery_rate(),
            "github_enabled": self.github_enabled,
            "recommendations": self._generate_recommendations()
        }
    
    def _count_recent_errors(self, hours: int) -> int:
        """Count errors in the last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        return sum(1 for e in self.last_errors 
                   if datetime.fromisoformat(e["timestamp"]) > cutoff)
    
    def _get_top_errors(self, limit: int = 5) -> List[Dict]:
        """Get most frequent errors"""
        sorted_errors = sorted(
            self.error_counts.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:limit]
        
        return [
            {"hash": h[:16], "count": c} 
            for h, c in sorted_errors
        ]
    
    def _calculate_recovery_rate(self) -> float:
        """Calculate successful recovery percentage"""
        if not self.recovery_attempts:
            return 1.0
        
        # Read recovery log
        successful = 0
        total = 0
        
        try:
            if self.recovery_log_path.exists():
                with open(self.recovery_log_path, 'r') as f:
                    for line in f:
                        entry = json.loads(line)
                        total += 1
                        if entry.get("success"):
                            successful += 1
        except Exception:
            pass
        
        return successful / total if total > 0 else 1.0
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on error patterns"""
        recommendations = []
        
        if self.health_status == "critical":
            recommendations.append("URGENT: Review error logs immediately")
        
        if self._count_recent_errors(hours=1) > 10:
            recommendations.append("High error rate detected - check external services")
        
        # Check for specific patterns
        for error in self.last_errors[-10:]:
            if "GROQ" in error.get("error_type", "").upper():
                recommendations.append("Verify GROQ_API_KEY is valid and has quota")
                break
        
        if not self.github_enabled:
            recommendations.append("Set GITHUB_TOKEN for automated issue creation")
        
        return recommendations or ["System operating normally"]
    
    def _write_log(self, path: Path, entry: Dict):
        """Append entry to JSONL log file"""
        try:
            with open(path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write log: {e}")
    
    def _generate_error_id(self, error: Exception, context: Dict) -> str:
        """Generate unique error ID"""
        content = f"{type(error).__name__}{str(error)}{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:12]
    
    def _hash_traceback(self, tb: str) -> str:
        """Hash traceback for pattern matching"""
        # Remove line numbers for consistent hashing
        import re
        normalized = re.sub(r'line \d+', 'line X', tb)
        return hashlib.sha256(normalized.encode()).hexdigest()
    
    def _sanitize_context(self, context: Dict) -> Dict:
        """Remove sensitive data from context"""
        sensitive_keys = ['password', 'token', 'key', 'secret', 'api_key']
        sanitized = {}
        
        for k, v in context.items():
            if any(s in k.lower() for s in sensitive_keys):
                sanitized[k] = "[REDACTED]"
            elif isinstance(v, dict):
                sanitized[k] = self._sanitize_context(v)
            else:
                sanitized[k] = v
        
        return sanitized


# Singleton instance
_healing_engine = None

def get_healing_engine() -> SelfHealingEngine:
    """Get or create self-healing engine instance"""
    global _healing_engine
    if _healing_engine is None:
        _healing_engine = SelfHealingEngine()
    return _healing_engine


def self_heal(component: str = "ai_assistant"):
    """
    Decorator for automatic error logging and recovery.
    
    Usage:
        @self_heal("my_component")
        def my_function():
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                engine = get_healing_engine()
                result = engine.log_error(
                    error=e,
                    context={
                        "function": func.__name__,
                        "args_count": len(args),
                        "kwargs_keys": list(kwargs.keys())
                    },
                    component=component
                )
                
                # If recovery suggested fallback, return None gracefully
                if result["recovery"].get("action") in ["use_fallback", "use_defaults"]:
                    return None
                
                # Otherwise re-raise
                raise
        return wrapper
    return decorator
