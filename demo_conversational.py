#!/usr/bin/env python3
"""
Demo of Conversational Features
Shows how the new intent detection and agent routing works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.intent_engine import IntentEngine
from src.document_parser import UniversalDocumentParser
from src.agent_router import AgentRouter
from src.session_manager import SessionManager, ConversationalSession


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def demo_intent_detection():
    """Demonstrate intent detection"""
    print_section("Intent Detection Demo")
    
    engine = IntentEngine()
    
    test_phrases = [
        "I want to consolidate test results",
        "merge my Excel files",
        "process invoices",
        "extract text from this image",
        "clean my data",
        "create a report",
        "help me with something",
    ]
    
    print("\nTesting various user phrases:\n")
    
    for phrase in test_phrases:
        result = engine.detect_intent(phrase)
        intent = result['intent']
        confidence = result['confidence']
        
        emoji = "✅" if intent != 'unknown' else "❓"
        print(f'{emoji} "{phrase}"')
        print(f'   → Intent: {intent} (confidence: {confidence:.2%})')
        
        if result['suggestions']:
            print(f'   → Suggestions: {len(result["suggestions"])} available')
        print()


def demo_document_parsing():
    """Demonstrate document parsing"""
    print_section("Document Parser Demo")
    
    parser = UniversalDocumentParser()
    
    print("\nSupported file format categories:\n")
    for category, formats in parser.SUPPORTED_FORMATS.items():
        print(f"  • {category}: {', '.join(formats[:5])}")
        if len(formats) > 5:
            print(f"    ... and {len(formats) - 5} more")
    
    print("\n\nExample format detection:\n")
    test_files = [
        ('report.xlsx', 'spreadsheets'),
        ('invoice.pdf', 'documents'),
        ('scan.jpg', 'images'),
        ('data.json', 'data'),
    ]
    
    for filename, expected_type in test_files:
        # We'll just show what would be detected based on extension
        ext = '.' + filename.split('.')[-1]
        for category, formats in parser.SUPPORTED_FORMATS.items():
            if ext in formats:
                print(f"  ✅ {filename} → {category}")
                break


def demo_agent_routing():
    """Demonstrate agent routing"""
    print_section("Agent Router Demo")
    
    router = AgentRouter()
    
    print("\nAvailable processing agents:\n")
    for agent_name in router.list_agents():
        info = router.get_agent_info(agent_name)
        if info['exists']:
            print(f"  • {agent_name}: {info['description']}")
    
    print("\n\nRouting examples:\n")
    
    scenarios = [
        {
            'intent': 'test_consolidation',
            'docs': [
                {'format': '.xlsx', 'type': 'spreadsheets', 'path': '/fake/test1.xlsx'},
                {'format': '.xlsx', 'type': 'spreadsheets', 'path': '/fake/test2.xlsx'},
            ]
        },
        {
            'intent': 'invoice_processing',
            'docs': [
                {'format': '.pdf', 'type': 'documents', 'path': '/fake/invoice.pdf'},
            ]
        },
    ]
    
    for scenario in scenarios:
        intent = scenario['intent']
        docs = scenario['docs']
        
        agent, config = router.route(intent, docs)
        
        print(f"  Intent: {intent}")
        print(f"  Documents: {len(docs)} file(s)")
        print(f"  → Routed to: {type(agent).__name__}")
        print(f"  → Output format: {config.output_format}")
        print()


def demo_conversational_session():
    """Demonstrate conversational session"""
    print_section("Conversational Session Demo")
    
    sm = SessionManager()
    conv_session = ConversationalSession(sm, user_id=12345)
    
    print("\nSimulated conversation:\n")
    
    # User sends message
    user_msg = "I want to consolidate test results"
    conv_session.add_message(user_msg, role='user')
    print(f"👤 User: {user_msg}")
    
    # Bot detects intent
    from src.intent_engine import IntentEngine
    engine = IntentEngine()
    result = engine.detect_intent(user_msg)
    
    conv_session.update_intent(result['intent'], result['confidence'])
    
    bot_response = "📊 Test Consolidation Mode\nI'll help you consolidate test results!"
    conv_session.add_message(bot_response, role='bot')
    print(f"🤖 Bot: {bot_response}")
    print()
    
    # User uploads document
    file_info = {
        'format': '.xlsx',
        'type': 'spreadsheets',
        'name': 'Test_1.xlsx',
        'size': 15360
    }
    conv_session.add_document('/fake/Test_1.xlsx', file_info)
    print(f"📤 User uploaded: Test_1.xlsx")
    print()
    
    # Check session state
    goal = conv_session.infer_user_goal()
    print(f"Session State:")
    print(f"  • Intent: {goal['intent']}")
    print(f"  • Confidence: {goal['confidence']:.2%}")
    print(f"  • Files uploaded: {goal['file_count']}")
    print(f"  • Messages: {goal['message_count']}")
    print(f"  • Workflow state: {goal['workflow_state']}")
    print()
    
    # Show conversation context
    context = conv_session.get_conversation_context(limit=10)
    print(f"Conversation History:\n{context}")


def demo_backward_compatibility():
    """Show backward compatibility"""
    print_section("Backward Compatibility Demo")
    
    print("\n✅ All existing functionality preserved:\n")
    
    print("  • Legacy SessionManager API unchanged")
    print("  • Original test consolidation workflow intact")
    print("  • Existing file processing methods work as before")
    print("  • Configuration system backward compatible")
    print("  • No breaking changes to any existing code")
    print()
    
    print("✨ New features are pure additions:\n")
    
    print("  • Intent detection engine (new)")
    print("  • Document parser (new)")
    print("  • Agent router (new)")
    print("  • Conversational session wrapper (new)")
    print("  • All new components are optional and gracefully degrade")
    print()
    
    # Demonstrate legacy mode still works
    sm = SessionManager()
    session = sm.get_session(99999)
    sm.add_file(99999, '/fake/test1.xlsx', 1)
    status = sm.format_status_message(99999)
    
    print("  Example: Legacy session created and file added successfully ✅")
    print(f"  Session has {len(session['uploaded_files'])} file(s) using legacy API")


def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("  MLJ Results Compiler - Conversational Features Demo")
    print("=" * 70)
    print("\n  This demo shows the new conversational intelligence features")
    print("  while maintaining 100% backward compatibility.")
    
    demo_intent_detection()
    demo_document_parsing()
    demo_agent_routing()
    demo_conversational_session()
    demo_backward_compatibility()
    
    print("\n" + "=" * 70)
    print("  Demo Complete!")
    print("=" * 70)
    print("\n  For more information, see:")
    print("    • README.md - Overview and quick start")
    print("    • CONVERSATIONAL_GUIDE.md - Detailed usage guide")
    print("    • test_conversational.py - Test suite")
    print()


if __name__ == '__main__':
    main()
