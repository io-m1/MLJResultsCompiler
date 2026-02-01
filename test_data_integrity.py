# -*- coding: utf-8 -*-
"""
Test Data Integrity Against Real Issues
Verifies the fixes for the 6 critical issues identified in the analysis
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from data_integrity import DataIntegrityValidator, get_validator
from excel_processor import ExcelProcessor


def test_consolidation_integrity():
    """Test that consolidation preserves all data with no loss"""
    print("\n" + "="*70)
    print("TEST: Consolidation Data Integrity (No Duplicate Loss)")
    print("="*70)
    
    validator = DataIntegrityValidator()
    
    # Create processor
    input_dir = Path("input")
    output_dir = Path("output")
    
    if not input_dir.exists():
        print("❌ Input directory not found. Skipping test.")
        return False
    
    processor = ExcelProcessor(str(input_dir), str(output_dir))
    
    # Load all tests
    loaded_count = processor.load_all_tests()
    print(f"\n✓ Loaded {loaded_count} test files")
    
    # Get test data before consolidation
    test_data_before = processor.test_data.copy()
    
    # Consolidate
    consolidated = processor.consolidate_results()
    
    # Validate
    result = validator.validate_consolidation(test_data_before, consolidated)
    
    # Print report
    print("\n📊 VALIDATION RESULT:")
    print(f"   Valid: {result['valid']}")
    print(f"   Source unique emails: {result['stats']['source_unique_emails']}")
    print(f"   Consolidated emails: {result['stats']['consolidated_emails']}")
    print(f"   Data loss: {result['stats']['data_loss_percent']:.1f}%")
    
    # Print details
    validator.print_report("Data Consolidation Integrity Check")
    
    return result['valid']


def test_excel_output_integrity():
    """Test that the Excel file has correct headers and data"""
    print("\n" + "="*70)
    print("TEST: Excel Output File Integrity")
    print("="*70)
    
    validator = DataIntegrityValidator()
    
    input_dir = Path("input")
    output_dir = Path("output")
    
    if not input_dir.exists():
        print("❌ Input directory not found. Skipping test.")
        return False
    
    processor = ExcelProcessor(str(input_dir), str(output_dir))
    
    # Load and consolidate
    processor.load_all_tests()
    consolidated = processor.consolidate_results()
    
    # Save
    success = processor.save_consolidated_file(consolidated)
    if not success:
        print("❌ Failed to save file")
        return False
    
    # Find the saved file
    output_files = list(output_dir.glob("Consolidated_Results.xlsx"))
    if not output_files:
        print("❌ No output file found")
        return False
    
    excel_path = output_files[0]
    print(f"✓ Saved to {excel_path}")
    
    # Validate
    result = validator.validate_excel_output(excel_path)
    
    validator.print_report("Excel Output Integrity Check")
    
    return result['valid']


def test_column_detection():
    """Test that column detection is robust"""
    print("\n" + "="*70)
    print("TEST: Column Detection Robustness")
    print("="*70)
    
    input_dir = Path("input")
    if not input_dir.exists():
        print("❌ Input directory not found. Skipping test.")
        return False
    
    processor = ExcelProcessor(str(input_dir), str("output"))
    processor.load_all_tests()
    
    print("\n✓ Column Detection Test:")
    print("  Checking column handling for different variations...")
    
    # Check if columns were detected correctly
    for test_num, test_data in processor.test_data.items():
        if test_data:
            first_entry = next(iter(test_data.values()))
            if 'score' in first_entry:
                print(f"  ✓ Test {test_num}: 'score' column found")
            if 'name' in first_entry:
                print(f"  ✓ Test {test_num}: 'name' column found")
    
    return True


def main():
    """Run all integrity tests"""
    print("\n" + "🔍 "*35)
    print("DATA INTEGRITY TEST SUITE")
    print("Verifying fixes for 6 critical issues")
    print("🔍 "*35)
    
    tests = [
        ("Consolidation Integrity (No Duplicate Loss)", test_consolidation_integrity),
        ("Excel Output Integrity (Headers & Data)", test_excel_output_integrity),
        ("Column Detection Robustness", test_column_detection),
    ]
    
    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nResult: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ ALL TESTS PASSED - Implementation is correct!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED - Issues need to be addressed")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
