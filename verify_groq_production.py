"""
Verify Groq Integration & Production Readiness
Tests the actual LLM connection and data manipulation
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_groq_connection():
    """Test 1: Groq API Connection"""
    print("\n" + "="*60)
    print("TEST 1: Groq API Connection")
    print("="*60)
    
    try:
        from groq import Groq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            print("GROQ_API_KEY not found in environment")
            return False
        
        print(f"GROQ_API_KEY found (length: {len(api_key)} chars)")
        
        # Create client
        client = Groq(api_key=api_key)
        print(f"Groq client created successfully")
        
        # Make test request
        message = client.chat.completions.create(
            model="llama-3.1-70b-versatile",
            messages=[
                {"role": "user", "content": "Say 'Hello from Groq' in one sentence."}
            ],
            max_tokens=50
        )
        
        response = message.choices[0].message.content
        print(f"LLM Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"Groq Connection Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_assistant():
    """Test 2: AI Assistant with LLM"""
    print("\n" + "="*60)
    print("TEST 2: AI Assistant with LLM")
    print("="*60)
    
    try:
        from src.ai_assistant import AugmentedAssistant
        
        ai = AugmentedAssistant()
        
        # Test with sample data
        sample_data = {
            'alice@test.com': {'Full Name': 'Alice', 'Test_1_Score': 85, 'Test_2_Score': 90},
            'bob@test.com': {'Full Name': 'Bob', 'Test_1_Score': 92, 'Test_2_Score': 87}
        }
        
        response = ai.analyze_message(
            "Summarize these test results",
            sample_data,
            {'participant_count': 2, 'test_count': 2}
        )
        
        print(f"AI Generated Analysis:")
        preview = str(response)[:200]
        print(f"   {preview}...")
        
        return True
        
    except Exception as e:
        print(f"AI Assistant Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_render_endpoint():
    """Test 3: Render Endpoint Accessibility"""
    print("\n" + "="*60)
    print("TEST 3: Render Service Health")
    print("="*60)
    
    try:
        import requests
        
        url = "https://mlj-results-compiler.onrender.com/status"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Render service is UP")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Features: {data.get('features', {})}")
            return True
        else:
            print(f"Render returned status {response.status_code}")
            print(f"   Note: Service may still be deploying or in sleep mode")
            return None
            
    except Exception as e:
        print(f"Render endpoint not accessible: {str(e)}")
        print("   Note: This may be expected if service is spinning up")
        return None


def test_data_agent_with_lvm():
    """Test 4: Data Agent with LLM Integration"""
    print("\n" + "="*60)
    print("TEST 4: Data Agent with LLM")
    print("="*60)
    
    try:
        from src.data_agent import DataAgent
        import pandas as pd
        
        agent = DataAgent()
        
        # Create test data
        df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Email': ['a@test.com', 'b@test.com', 'c@test.com'],
            'Score': [85, 92, 78]
        })
        
        # Test preview mode
        preview = agent.preview_action(
            "add_grades",
            df,
            {'score_column': 'Score', 'grades_column': 'Grade'}
        )
        
        if preview['success']:
            print(f"✅ Preview Mode Works")
            print(f"   Changes: {preview['preview']['changes']}")
            return True
        else:
            print(f"❌ Preview Mode Failed: {preview.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Data Agent Failed: {str(e)}")
        return False


def run_verification():
    """Run all verification tests"""
    print("\n" + "="*70)
    print("GROQ INTEGRATION VERIFICATION")
    print("="*70)
    
    results = {
        "Groq API Connection": test_groq_connection(),
        "AI Assistant": test_ai_assistant(),
        "Render Service": test_render_endpoint(),
        "Data Agent": test_data_agent_with_lvm()
    }
    
    # Summary
    print("\n" + "="*70)
    print("VERIFICATION SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        if result is True:
            status = "PASS"
        elif result is None:
            status = "UNAVAILABLE"
        else:
            status = "FAIL"
        print(f"{status}: {test_name}")
    
    # Determine overall status
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    unavailable = sum(1 for r in results.values() if r is None)
    
    print(f"\nTotal: {passed} passed, {failed} failed, {unavailable} unavailable")
    
    if failed == 0 and passed >= 2:
        print("\nPRODUCTION VERIFICATION SUCCESSFUL")
        print("Groq integration is working!")
        return True
    else:
        print("\nSome tests failed or unavailable")
        print("Check errors above")
        return False


if __name__ == "__main__":
    success = run_verification()
    sys.exit(0 if success else 1)
