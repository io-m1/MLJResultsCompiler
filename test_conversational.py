#!/usr/bin/env python3
"""
Basic tests for conversational features
Verifies backward compatibility and new functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_intent_engine():
    """Test intent detection engine"""
    from src.intent_engine import IntentEngine
    
    engine = IntentEngine()
    
    # Test 1: Test consolidation intent
    result = engine.detect_intent('I want to consolidate test results')
    assert result['intent'] == 'test_consolidation', f"Expected test_consolidation, got {result['intent']}"
    assert result['confidence'] > 0.5, f"Confidence too low: {result['confidence']}"
    print("✅ Test 1 passed: Test consolidation intent detected")
    
    # Test 2: Invoice processing intent
    result = engine.detect_intent('process invoices')
    assert result['intent'] == 'invoice_processing', f"Expected invoice_processing, got {result['intent']}"
    print("✅ Test 2 passed: Invoice processing intent detected")
    
    # Test 3: Image extraction intent
    result = engine.detect_intent('extract text from image')
    assert result['intent'] == 'image_extraction', f"Expected image_extraction, got {result['intent']}"
    print("✅ Test 3 passed: Image extraction intent detected")
    
    # Test 4: Unknown intent
    result = engine.detect_intent('xyz abc 123')
    assert result['intent'] == 'unknown', f"Expected unknown, got {result['intent']}"
    print("✅ Test 4 passed: Unknown intent handled correctly")
    
    print("\n✅ All intent engine tests passed!")
    return True


def test_document_parser():
    """Test document parser"""
    from src.document_parser import UniversalDocumentParser
    import tempfile
    from pathlib import Path
    
    parser = UniversalDocumentParser()
    
    # Test 1: Check supported formats
    assert len(parser.SUPPORTED_FORMATS) >= 4, "Should support at least 4 format categories"
    print("✅ Test 1 passed: Parser supports multiple format categories")
    
    # Test 2: Detect Excel format
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as f:
        temp_path = f.name
    
    try:
        # Create empty file
        Path(temp_path).touch()
        
        file_info = parser.detect_format(temp_path)
        assert file_info['type'] == 'spreadsheets', f"Expected spreadsheets, got {file_info['type']}"
        assert file_info['format'] == '.xlsx', f"Expected .xlsx, got {file_info['format']}"
        print("✅ Test 2 passed: Excel format detected correctly")
    finally:
        Path(temp_path).unlink()
    
    # Test 3: Detect non-existent file
    file_info = parser.detect_format('/nonexistent/file.xyz')
    assert file_info['exists'] == False, "Should detect non-existent file"
    print("✅ Test 3 passed: Non-existent file handled correctly")
    
    print("\n✅ All document parser tests passed!")
    return True


def test_agent_router():
    """Test agent router"""
    from src.agent_router import AgentRouter
    
    router = AgentRouter()
    
    # Test 1: Check agents loaded
    agents = router.list_agents()
    assert len(agents) > 0, "Should have at least one agent"
    print(f"✅ Test 1 passed: {len(agents)} agent(s) loaded")
    
    # Test 2: Route test consolidation intent
    documents = [
        {'format': '.xlsx', 'type': 'spreadsheets', 'path': '/fake/test1.xlsx'}
    ]
    agent, config = router.route('test_consolidation', documents)
    assert agent is not None, "Should return an agent"
    assert config.intent == 'test_consolidation', "Config should match intent"
    print("✅ Test 2 passed: Test consolidation routed correctly")
    
    print("\n✅ All agent router tests passed!")
    return True


def test_session_manager():
    """Test session manager with conversational features"""
    from src.session_manager import SessionManager, ConversationalSession
    
    sm = SessionManager()
    
    # Test 1: Create session
    session = sm.get_session(12345)
    assert session is not None, "Should create session"
    assert session['user_id'] == 12345, "User ID should match"
    print("✅ Test 1 passed: Session created")
    
    # Test 2: Conversational session
    conv_session = ConversationalSession(sm, 12345)
    conv_session.add_message('Hello', role='user')
    
    history = conv_session.session['conversation_history']
    assert len(history) == 1, "Should have one message"
    assert history[0]['message'] == 'Hello', "Message should be stored"
    print("✅ Test 2 passed: Conversation history tracked")
    
    # Test 3: Update intent
    conv_session.update_intent('test_consolidation', 0.85)
    assert conv_session.session['detected_intent'] == 'test_consolidation', "Intent should be updated"
    assert conv_session.session['intent_confidence'] == 0.85, "Confidence should be stored"
    print("✅ Test 3 passed: Intent tracking works")
    
    # Test 4: Document tracking
    file_info = {'format': '.xlsx', 'type': 'spreadsheets', 'name': 'test.xlsx', 'size': 1024}
    conv_session.add_document('/fake/test.xlsx', file_info)
    assert conv_session.get_document_count() == 1, "Should have one document"
    print("✅ Test 4 passed: Document tracking works")
    
    print("\n✅ All session manager tests passed!")
    return True


def test_config():
    """Test conversational configuration"""
    from config import ConversationalConfig
    
    config = ConversationalConfig()
    
    # Test 1: Default values
    assert config.enable_intent_detection == True, "Intent detection should be enabled by default"
    assert config.intent_confidence_threshold == 0.7, "Default threshold should be 0.7"
    print("✅ Test 1 passed: Default config values correct")
    
    # Test 2: Customization
    custom_config = ConversationalConfig(
        enable_intent_detection=False,
        intent_confidence_threshold=0.8
    )
    assert custom_config.enable_intent_detection == False, "Custom value should be applied"
    assert custom_config.intent_confidence_threshold == 0.8, "Custom threshold applied"
    print("✅ Test 2 passed: Custom configuration works")
    
    print("\n✅ All config tests passed!")
    return True


def test_backward_compatibility():
    """Test that existing functionality still works"""
    from src.session_manager import SessionManager
    
    sm = SessionManager()
    
    # Test legacy session creation (as used by existing bot)
    session = sm.get_session(99999)
    
    # Check that all legacy fields still exist
    assert 'uploaded_files' in session, "Legacy uploaded_files field should exist"
    assert 'temp_dir' in session, "Legacy temp_dir field should exist"
    assert 'state' in session, "Legacy state field should exist"
    assert 'messages' in session, "Legacy messages field should exist"
    print("✅ Test 1 passed: Legacy session fields preserved")
    
    # Test legacy add_file method
    summary = sm.add_file(99999, '/fake/test1.xlsx', 1)
    assert 'tests_uploaded' in summary, "Legacy summary format preserved"
    assert 'can_consolidate' in summary, "Legacy summary fields preserved"
    print("✅ Test 2 passed: Legacy add_file method works")
    
    # Test legacy format_status_message
    status = sm.format_status_message(99999)
    assert '[FILE STATUS]' in status, "Legacy status format preserved"
    print("✅ Test 3 passed: Legacy status message format preserved")
    
    print("\n✅ All backward compatibility tests passed!")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("Running Conversational Features Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Intent Engine", test_intent_engine),
        ("Document Parser", test_document_parser),
        ("Agent Router", test_agent_router),
        ("Session Manager", test_session_manager),
        ("Configuration", test_config),
        ("Backward Compatibility", test_backward_compatibility),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        print(f"\n{'=' * 60}")
        print(f"Testing: {name}")
        print('=' * 60)
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
                print(f"❌ {name} tests failed")
        except Exception as e:
            failed += 1
            print(f"❌ {name} tests failed with error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
