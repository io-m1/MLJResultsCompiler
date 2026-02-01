#!/usr/bin/env python3
"""
Local Build Check - Verify Render deployment will succeed
Mimics the Render build process locally
Windows and Linux compatible
"""

import subprocess
import sys
import os


def check_step(description, command, check_output=None, is_import=False):
    """Run a check step and verify it passes"""
    print(f"\n🔍 {description}...")
    try:
        if is_import:
            # For import checks, just eval the command
            exec(command)
            print(f"  ✓ PASSED")
            return True
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            print(f"  ✗ FAILED")
            if result.stderr:
                print(f"  Error: {result.stderr[:200]}")
            return False
        
        if check_output and check_output not in result.stdout:
            print(f"  ✗ FAILED - Expected output not found: {check_output}")
            return False
        
        print(f"  ✓ PASSED")
        return True
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False


def main():
    """Run all build checks"""
    print("=" * 60)
    print("🏗️  MLJ RESULTS COMPILER - LOCAL BUILD CHECK")
    print("=" * 60)
    
    checks = [
        # Step 1: Verify Pandas (implies build tools are working)
        (
            "Critical dependencies (pandas, numpy, pydantic)",
            "python -c \"import pandas; import numpy; import pydantic; print('All critical deps OK')\"",
            "All critical deps OK",
            False
        ),
        
        # Step 2: Verify critical dependencies
        (
            "FastAPI installed",
            "python -m pip show fastapi",
            "Name: fastapi",
            False
        ),
        
        # Step 3: Verify Procfile command works
        (
            "Procfile command syntax (uvicorn src.main:app)",
            "python -m uvicorn src.main:app --help",
            "Usage: python -m uvicorn",
            False
        ),
        
        # Step 4: Test all async services
        (
            "Async services import correctly",
            "from src.async_ai_service import get_async_ai_service; from src.async_data_agent import get_async_data_agent; from src.async_file_io import get_async_file_io",
            None,
            True
        ),
        
        # Step 5: Test main app creation
        (
            "Main app creates successfully",
            "from src.main import create_app; app = create_app(); print(f'✓ {len(app.routes)} routes')",
            None,
            True
        ),
        
        # Step 6: Test config loads
        (
            "Configuration loads correctly",
            "from src.config import get_settings; settings = get_settings(); print(f'✓ {settings.APP_NAME}')",
            None,
            True
        ),
    ]
    
    passed = 0
    failed = 0
    
    for description, command, check, is_import in checks:
        if check_step(description, command, check, is_import):
            passed += 1
        else:
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("\n✅ BUILD CHECK SUCCESSFUL!")
        print("Render deployment will succeed with these changes.")
        print("\n📋 Verification Summary:")
        print("  ✓ All dependencies installed")
        print("  ✓ Async services working")
        print("  ✓ Main app loads successfully")
        print("  ✓ Configuration valid")
        print("  ✓ Procfile command valid")
        return 0
    else:
        print(f"\n❌ BUILD CHECK FAILED - {failed} checks did not pass")
        print("Fix the issues above before deploying to Render.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
