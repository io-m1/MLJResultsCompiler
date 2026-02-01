"""
Simple Groq API Test - Verify LLM is working
"""

import os
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("ERROR: GROQ_API_KEY not set")
    exit(1)

print(f"Testing Groq with API key: {api_key[:20]}...")

try:
    client = Groq(api_key=api_key)
    
    # Simple message without special characters
    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[
            {"role": "user", "content": "Hello, how are you?"}
        ],
        max_tokens=50
    )
    
    print("\nSUCCESS: Groq API is working!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"\nERROR: {str(e)}")
    import traceback
    traceback.print_exc()
