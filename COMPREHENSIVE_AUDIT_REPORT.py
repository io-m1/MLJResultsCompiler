#!/usr/bin/env python3
"""
COMPREHENSIVE REPOSITORY AUDIT & BUG REPORT
Generated: February 1, 2026
Scope: Full system analysis for production readiness
"""

FINDINGS = {
    "CRITICAL_BUGS": [
        {
            "id": "BUG-001",
            "severity": "CRITICAL",
            "title": "Missing Dependencies in requirements.txt",
            "description": "pandas and numpy are used in multiple files but NOT in requirements.txt",
            "affected_files": [
                "compiler_v2.py (line 20-21)",
                "src/data_agent.py (line 22)",
                "src/ai_assistant.py (line 719)",
                "src/hybrid_bridge.py (line 605)",
                "test_production_e2e.py (line 19)",
                "verify_groq_production.py (line 126)",
                "src/batch_processor.py (line 12)"
            ],
            "impact": "RuntimeError: No module named 'pandas' when dependencies are installed",
            "fix": """
Add to requirements.txt:
  pandas==2.0.3
  numpy==1.24.3
            """,
            "priority": "IMMEDIATELY"
        },
        {
            "id": "BUG-002",
            "severity": "CRITICAL",
            "title": "Relative Path Issues in ExcelProcessor",
            "description": "ExcelProcessor.output_dir initialization may not create directories properly",
            "affected_files": [
                "src/excel_processor.py (line 32-33)",
                "src/hybrid_bridge.py (line 159-200)"
            ],
            "current_code": """
self.output_dir = Path(output_dir)
            """,
            "issue": "output_dir is not created if it doesn't exist, may cause write failures",
            "fix": """
self.output_dir = Path(output_dir)
self.output_dir.mkdir(parents=True, exist_ok=True)
            """,
            "priority": "HIGH"
        },
        {
            "id": "BUG-003",
            "severity": "HIGH",
            "title": "Data Loss Risk in Excel Consolidation",
            "description": "No validation that all loaded tests are actually used in consolidation",
            "affected_files": [
                "src/excel_processor.py (lines 325-390)"
            ],
            "issue": """
If test_data has Test 1, 2, 3 but consolidation only uses Test 1 as base
and Test 2 is never merged, no warning is issued.
            """,
            "risk": "Silent data loss if merge fails for certain tests",
            "priority": "HIGH"
        },
        {
            "id": "BUG-004",
            "severity": "CRITICAL",
            "title": "Session Data Loss on Server Restart",
            "description": "All upload sessions stored in memory (UPLOAD_SESSIONS dict)",
            "affected_files": [
                "src/hybrid_bridge.py (line 26-27)"
            ],
            "current_code": """
# In-memory session storage (in production, use Redis/database)
UPLOAD_SESSIONS = {}
            """,
            "issue": "When server restarts (Render), all user sessions are lost",
            "impact": "Users lose uploaded files and consolidation state",
            "workaround": "Document that server restart loses sessions",
            "priority": "MEDIUM (architecture limitation)"
        },
        {
            "id": "BUG-005",
            "severity": "HIGH",
            "title": "No Error Recovery for Failed Email Parsing",
            "description": "Email parsing silently accepts non-standard formats",
            "affected_files": [
                "src/excel_processor.py (line 76)",
                "src/validators.py"
            ],
            "code": """
email = clean_email(row[email_col - 1] if email_col <= len(row) else "")
            """,
            "issue": "Invalid emails not caught - may cause merge failures",
            "priority": "MEDIUM"
        }
    ],
    
    "LOGIC_ERRORS": [
        {
            "id": "LOGIC-001",
            "severity": "MEDIUM",
            "title": "AI Assistant Mode Not Thread-Safe",
            "description": "current_mode can be changed while processing requests",
            "affected_files": [
                "src/ai_assistant.py (line 59, 216-219)"
            ],
            "issue": """
Multiple concurrent requests could interfere with each other's mode setting.
If request A sets mode='cold_email' and request B sets mode='consolidation',
A might process with wrong system prompt.
            """,
            "fix": "Use threading.Lock() for mode changes or use thread-local storage",
            "priority": "MEDIUM"
        },
        {
            "id": "LOGIC-002", 
            "severity": "HIGH",
            "title": "Download Endpoint Path Traversal Risk",
            "description": "result_path stored from user-controlled session could be modified",
            "affected_files": [
                "src/hybrid_bridge.py (lines 216-235)"
            ],
            "current_code": """
result_path = session["consolidation_result"]["path"]
if not os.path.exists(result_path):
    raise HTTPException(status_code=404, detail="File not found")
return FileResponse(result_path, ...)
            """,
            "risk": "If result_path is ever user-controllable, could access arbitrary files",
            "fix": "Validate that result_path is within temp_uploads directory",
            "priority": "MEDIUM (currently safe, but add validation)"
        },
        {
            "id": "LOGIC-003",
            "severity": "HIGH",
            "title": "Uncaught Exception in Deduplication Reports",
            "description": "dedup_report may contain non-serializable objects",
            "affected_files": [
                "compiler_v2.py (lines 368-377)",
                "src/hybrid_bridge.py (line 315)"
            ],
            "issue": """
If df.to_dict('records') contains Timestamp or NaN, JSON serialization fails
            """,
            "fix": """
dedup_report['duplicates'] = dupes.to_dict('records')
May fail if Timestamp columns exist. Add default=str to json.dump()
            """,
            "priority": "MEDIUM"
        }
    ],
    
    "POTENTIAL_RUNTIME_ERRORS": [
        {
            "id": "RUNTIME-001",
            "severity": "MEDIUM",
            "title": "Score Parsing May Fail on Non-Numeric Data",
            "description": "parse_score() may not handle all edge cases",
            "affected_files": [
                "src/validators.py",
                "compiler_v2.py (line 449)"
            ],
            "code": """
pd.to_numeric(..., errors='coerce')
            """,
            "issue": """
If score column contains text like "ABSENT" or "PASS", coerces to NaN.
No validation that sufficient numeric scores exist.
            """,
            "risk": "Consolidation may succeed with all NaN scores (silently bad)",
            "priority": "MEDIUM"
        },
        {
            "id": "RUNTIME-002",
            "severity": "MEDIUM",
            "title": "Column Name Mismatch Risk",
            "description": "Fuzzy column detection may pick wrong columns if headers are ambiguous",
            "affected_files": [
                "compiler_v2.py (lines 260-300)"
            ],
            "example": """
If file has columns: "Name", "Email", "% Score", "% Complete"
Fuzzy detector might pick "% Complete" instead of "% Score"
            """,
            "fix": "Refine scoring - prioritize column position and exact matches",
            "priority": "MEDIUM"
        },
        {
            "id": "RUNTIME-003",
            "severity": "LOW",
            "title": "Temporary Files May Not Be Cleaned Up",
            "description": "temp_uploads directory grows indefinitely",
            "affected_files": [
                "src/hybrid_bridge.py (lines 31-35)"
            ],
            "current_code": """
def cleanup_old_sessions():
    now = datetime.now()
    expired = [sid for sid, data in UPLOAD_SESSIONS.items() 
               if now - data['created'] > timedelta(seconds=SESSION_TIMEOUT)]
    for sid in expired:
        del UPLOAD_SESSIONS[sid]
            """,
            "issue": """
Removes session from memory but NOT from filesystem.
temp_uploads/session_id directories accumulate disk space.
            """,
            "fix": """
Also delete: shutil.rmtree(f'temp_uploads/{sid}', ignore_errors=True)
            """,
            "priority": "LOW (Render free tier has limited storage)"
        }
    ],
    
    "CONFIGURATION_ISSUES": [
        {
            "id": "CONFIG-001",
            "severity": "MEDIUM",
            "title": "GROQ_API_KEY Optional but Not Documented",
            "description": ".env.example doesn't show GROQ_API_KEY needed for AI features",
            "affected_files": [
                ".env.example",
                "src/ai_assistant.py (line 80)"
            ],
            "issue": """
Users won't know to set GROQ_API_KEY in .env.
AI falls back silently to generic responses.
            """,
            "fix": "Add GROQ_API_KEY=your_key_here to .env.example",
            "priority": "LOW (documented elsewhere)"
        },
        {
            "id": "CONFIG-002",
            "severity": "HIGH",
            "title": "No Validation of Required Environment Variables",
            "description": "TELEGRAM_BOT_TOKEN not validated at startup",
            "affected_files": [
                "server.py (lines 58-62)",
                "telegram_bot.py"
            ],
            "issue": """
If .env missing or empty, bot won't start but error is logged late in startup
            """,
            "fix": """
At server startup, validate all required env vars before starting:
    required = ['TELEGRAM_BOT_TOKEN', 'WEBHOOK_BASE_URL']
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise RuntimeError(f"Missing env vars: {missing}")
            """,
            "priority": "MEDIUM"
        }
    ],
    
    "DEPENDENCY_ISSUES": [
        {
            "id": "DEP-001",
            "severity": "CRITICAL",
            "title": "Missing pandas and numpy in requirements.txt",
            "current": [
                "openpyxl==3.1.5",
                "python-telegram-bot==20.3",
                "fastapi==0.110.0",
                "groq==0.4.2"
            ],
            "missing": [
                "pandas==2.0.3",
                "numpy==1.24.3"
            ],
            "fix": "Add the missing packages to requirements.txt",
            "priority": "CRITICAL"
        }
    ],
    
    "ARCHITECTURAL_CONCERNS": [
        {
            "id": "ARCH-001",
            "severity": "MEDIUM",
            "title": "Two Compiler Implementations (Old and New)",
            "description": "ExcelProcessor and compiler_v2 both do consolidation",
            "files": [
                "src/excel_processor.py - Original (863 lines)",
                "compiler_v2.py - Enhanced (759 lines)"
            ],
            "issue": """
Maintenance burden - bug fixes needed in both.
Users may use the wrong one.
No clear migration path.
            """,
            "recommendation": """
1. Keep compiler_v2 as primary
2. Deprecate old ExcelProcessor
3. Update all imports to use compiler_v2
4. Plan removal of ExcelProcessor
            """,
            "priority": "MEDIUM"
        },
        {
            "id": "ARCH-002",
            "severity": "LOW",
            "title": "Inconsistent Error Handling",
            "description": "Some modules return False, others raise Exceptions",
            "examples": [
                "ExcelProcessor.load_test_file() returns bool",
                "compiler_v2 raises DataLossError, ColumnDetectionError",
                "API handlers raise HTTPException"
            ],
            "recommendation": "Standardize on exceptions for better error context",
            "priority": "LOW"
        }
    ]
}

def print_report():
    print("\n" + "="*80)
    print("COMPREHENSIVE REPOSITORY AUDIT REPORT")
    print("="*80 + "\n")
    
    # Critical bugs
    print("\n" + "="*80)
    print("CRITICAL BUGS FOUND")
    print("="*80)
    for bug in FINDINGS["CRITICAL_BUGS"]:
        print(f"\n[{bug['id']}] {bug['title']}")
        print(f"Severity: {bug['severity']}")
        print(f"Priority: {bug['priority']}")
        print(f"Description: {bug['description']}")
        print(f"Affected files: {bug['affected_files']}")
        print(f"Fix: {bug['fix']}")
    
    # Logic errors
    print("\n" + "="*80)
    print("LOGIC ERRORS")
    print("="*80)
    for error in FINDINGS["LOGIC_ERRORS"]:
        print(f"\n[{error['id']}] {error['title']}")
        print(f"Severity: {error['severity']}")
        print(f"Issue: {error['issue']}")
    
    # Runtime errors
    print("\n" + "="*80)
    print("POTENTIAL RUNTIME ERRORS")
    print("="*80)
    for error in FINDINGS["POTENTIAL_RUNTIME_ERRORS"]:
        print(f"\n[{error['id']}] {error['title']}")
        print(f"Risk: {error.get('risk', 'Unknown')}")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    total_bugs = (len(FINDINGS["CRITICAL_BUGS"]) + 
                  len(FINDINGS["LOGIC_ERRORS"]) +
                  len(FINDINGS["POTENTIAL_RUNTIME_ERRORS"]))
    print(f"\nTotal issues found: {total_bugs}")
    print(f"Critical: {len(FINDINGS['CRITICAL_BUGS'])}")
    print(f"Logic errors: {len(FINDINGS['LOGIC_ERRORS'])}")
    print(f"Runtime risks: {len(FINDINGS['POTENTIAL_RUNTIME_ERRORS'])}")
    print(f"Config issues: {len(FINDINGS['CONFIGURATION_ISSUES'])}")
    print(f"Dependency issues: {len(FINDINGS['DEPENDENCY_ISSUES'])}")
    
    print("\n" + "="*80)
    print("IMMEDIATE ACTIONS REQUIRED")
    print("="*80)
    print("""
1. ADD MISSING DEPENDENCIES (BUG-001)
   - Add pandas==2.0.3 to requirements.txt
   - Add numpy==1.24.3 to requirements.txt
   - Run: pip install -r requirements.txt

2. FIX OUTPUT DIR CREATION (BUG-002)
   - Update ExcelProcessor.__init__ to create output_dir

3. VALIDATE ENVIRONMENT AT STARTUP (CONFIG-002)
   - Add env var validation to server.py startup

4. PLAN COMPILER CONSOLIDATION (ARCH-001)
   - Decide between ExcelProcessor vs compiler_v2
   - Migrate all code to use one
    """)
    
    print("\n" + "="*80)
    print("PRODUCTION READINESS: NOT READY")
    print("="*80)
    print("""
The system has critical dependency issues that will cause immediate 
runtime failures. Missing pandas/numpy will crash on first consolidation.

Action required before production:
1. Fix dependency issues (CRITICAL)
2. Fix directory creation (HIGH)
3. Add env validation (HIGH)
4. Test with real data (HIGH)
    """)

if __name__ == "__main__":
    print_report()
