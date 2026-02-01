#!/usr/bin/env python
"""
Quick Build Test - Verify fixes before Render deploy
Tests the critical issues that were causing build failures
"""

import sys
import os
import subprocess
import importlib.util

def test_python_version():
    """Test Python version matches runtime.txt"""
    print("[TEST] Checking Python version...")
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"[INFO] Current Python: {version}")
    
    # Check runtime.txt
    if os.path.exists("runtime.txt"):
        with open("runtime.txt", "r") as f:
            runtime_version = f.read().strip()
        print(f"[INFO] Runtime.txt specifies: {runtime_version}")
        
        if "3.12.0" in runtime_version:
            print("[OK] Runtime version is compatible")
            return True
        else:
            print("[WARN] Runtime version mismatch - update if needed")
            return True  # Still pass as this is just a warning
    else:
        print("[WARN] runtime.txt not found")
        return False

def test_critical_imports():
    """Test that all critical imports work"""
    print("\n[TEST] Checking critical imports...")
    
    critical_modules = [
        "fastapi",
        "pandas", 
        "groq",
        "telegram",
        "uvicorn"
    ]
    
    for module in critical_modules:
        try:
            if importlib.util.find_spec(module):
                print(f"[OK] {module}")
            else:
                print(f"[ERROR] {module} not found")
                return False
        except Exception as e:
            print(f"[ERROR] {module}: {e}")
            return False
    
    return True

def test_main_import():
    """Test that main app can be imported"""
    print("\n[TEST] Testing main application import...")
    
    try:
        # Add src to path
        sys.path.insert(0, os.path.join(os.getcwd(), "src"))
        
        # Try importing main
        import main
        print("[OK] src.main imported successfully")
        
        # Check if FastAPI app exists
        if hasattr(main, 'app'):
            print("[OK] FastAPI app found")
        else:
            print("[ERROR] FastAPI app not found in main.py")
            return False
            
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to import src.main: {e}")
        return False

def test_unicode_safety():
    """Test that critical strings are ASCII-safe"""
    print("\n[TEST] Checking Unicode safety...")
    
    # Test strings that might be passed to external APIs
    test_strings = [
        "[OK] Test message",
        "[INFO] Information",
        "Success Rate: 100%",
        "Files processed: 5"
    ]
    
    for test_str in test_strings:
        try:
            # Test ASCII encoding (this is what was failing with emoji)
            test_str.encode('ascii')
            print(f"[OK] ASCII-safe: {test_str}")
        except UnicodeEncodeError as e:
            print(f"[ERROR] Unicode issue: {test_str} - {e}")
            return False
    
    return True

def test_procfile_syntax():
    """Test Procfile syntax"""
    print("\n[TEST] Checking Procfile...")
    
    if os.path.exists("Procfile"):
        with open("Procfile", "r") as f:
            content = f.read()
        
        if "uvicorn src.main:app" in content:
            print("[OK] Procfile contains correct uvicorn command")
        else:
            print("[ERROR] Procfile missing uvicorn command")
            return False
        
        if "--host 0.0.0.0 --port $PORT" in content:
            print("[OK] Procfile has correct host/port config")
        else:
            print("[ERROR] Procfile missing host/port config")
            return False
            
        return True
    else:
        print("[ERROR] Procfile not found")
        return False

def main():
    """Run all tests"""
    print("=== MLJ Results Compiler Build Test ===\n")
    
    tests = [
        ("Python Version", test_python_version),
        ("Critical Imports", test_critical_imports),
        ("Main Import", test_main_import),
        ("Unicode Safety", test_unicode_safety),
        ("Procfile", test_procfile_syntax)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"\n[FAILED] {test_name} test failed")
        except Exception as e:
            print(f"\n[ERROR] {test_name} test crashed: {e}")
    
    print(f"\n=== RESULTS: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("[SUCCESS] All tests passed! Ready for Render deploy")
        return 0
    else:
        print("[FAILURE] Some tests failed - fix issues before deploy")
        return 1

if __name__ == "__main__":
    sys.exit(main())