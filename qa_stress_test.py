import os
import requests
import json
import time

RENDER_BASE_URL = "https://mljresultscompiler.onrender.com"

def test_endpoint(path):
    print(f"--- Testing {path} ---")
    start = time.time()
    try:
        response = requests.get(f"{RENDER_BASE_URL}{path}", timeout=10)
        elapsed = time.time() - start
        print(f"Status Code: {response.status_code} ({elapsed:.2f}s)")
        
        try:
            data = response.json()
            print(json.dumps(data, indent=2))
        except:
            print(response.text)
            
        return response.status_code == 200
    except Exception as e:
        print(f"Error accessing {path}: {e}")
        return False

def run_qa_tests():
    print("====================================")
    print(" MLJCM & Result Compiler QA Testing ")
    print("====================================\n")
    
    # Wait to ensure Render has fully rebuilt and deployed the latest changes
    # By now it should be live, but the ping ensures the instance is spun up.
    
    endpoints = [
        "/ping",
        "/health",
        "/bot-health",
        "/liveness",
        "/status"
    ]
    
    all_passed = True
    for ep in endpoints:
        success = test_endpoint(ep)
        if not success:
            all_passed = False
        print("\n")
        
    print("====================================")
    if all_passed:
        print("[PASS] ALL RENDER ENDPOINTS ACCESSIBLE")
    else:
        print("[!] SOME TESTS FAILED")
    print("====================================")

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    run_qa_tests()
