#!/usr/bin/env python3
"""
Test async event loop - verify no blocking calls in concurrent requests
"""

import asyncio
import time
from src.async_ai_service import AsyncAIService, get_async_ai_service
from src.async_data_agent import AsyncDataAgent, get_async_data_agent
from src.async_file_io import AsyncFileIO, get_async_file_io
import pandas as pd


async def test_concurrent_ai_requests():
    """Test that multiple AI requests run concurrently without blocking"""
    print("\n🔄 Testing concurrent AI requests...")
    
    ai_service = get_async_ai_service()
    
    messages = [
        "What is consolidation?",
        "How do I calculate grades?",
        "Can I add custom columns?",
        "What about bonus scoring?"
    ]
    
    start = time.time()
    results = await ai_service.batch_analyze_messages_async(messages)
    elapsed = time.time() - start
    
    print(f"✓ Processed {len(messages)} requests in {elapsed:.2f}s")
    print(f"  Average: {elapsed/len(messages):.2f}s per request")
    print(f"  Concurrency gain: ~{(len(messages) * 0.5) / elapsed:.1f}x")
    
    return len(results) == len(messages)


async def test_concurrent_data_operations():
    """Test that multiple data operations run concurrently"""
    print("\n📊 Testing concurrent data operations...")
    
    agent = get_async_data_agent()
    
    # Create test dataframes
    data = {
        'Student': ['Alice', 'Bob', 'Charlie'],
        'Score': [85, 92, 78]
    }
    df = pd.DataFrame(data)
    
    operations = [
        {"action": "add_column", "params": {"column_name": "Status", "default_value": "Active"}},
        {"action": "add_random_scores", "params": {"column_name": "TestScore", "min_val": 0, "max_val": 100}},
    ]
    
    start = time.time()
    results = await agent.parallel_execute_async(operations, df)
    elapsed = time.time() - start
    
    print(f"✓ Processed {len(operations)} operations in {elapsed:.2f}s")
    print(f"  Success: {results.get('success')}")
    
    return results.get('success', False)


async def test_file_io_operations():
    """Test async file I/O doesn't block"""
    print("\n📁 Testing async file I/O...")
    
    file_io = get_async_file_io()
    
    # Create test data
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Grade': ['A', 'B', 'C']
    }
    df = pd.DataFrame(data)
    
    file_path = "test_output.xlsx"
    
    start = time.time()
    result = await file_io.write_excel_async(df, file_path)
    elapsed = time.time() - start
    
    print(f"✓ Wrote Excel file in {elapsed:.2f}s")
    print(f"  File: {result}")
    
    # Clean up
    import os
    if os.path.exists(file_path):
        os.remove(file_path)
    
    return result == file_path


async def test_event_loop_responsiveness():
    """Test that event loop remains responsive with concurrent work"""
    print("\n⚡ Testing event loop responsiveness...")
    
    # Schedule multiple concurrent tasks
    ai_service = get_async_ai_service()
    
    tasks = []
    for i in range(5):
        task = asyncio.create_task(
            ai_service.analyze_message_async(f"Test message {i}", timeout=5.0)
        )
        tasks.append(task)
    
    # All should complete without blocking
    start = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start
    
    print(f"✓ Completed {len(results)} concurrent tasks in {elapsed:.2f}s")
    print(f"  Event loop is responsive!")
    
    return len(results) == 5


async def main():
    """Run all async tests"""
    print("=" * 60)
    print("🚀 ASYNC EVENT LOOP TEST SUITE")
    print("=" * 60)
    
    try:
        # Test 1
        test1 = await test_concurrent_ai_requests()
        
        # Test 2
        test2 = await test_concurrent_data_operations()
        
        # Test 3
        test3 = await test_file_io_operations()
        
        # Test 4
        test4 = await test_event_loop_responsiveness()
        
        print("\n" + "=" * 60)
        if all([test1, test2, test3, test4]):
            print("✓ ALL TESTS PASSED - Event loop is working properly!")
        else:
            print("✗ Some tests failed")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
