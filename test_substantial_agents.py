#!/usr/bin/env python3
"""
Tests for substantial agent capabilities
Tests the real implementations of Table Merger, Data Cleaner, and Report Generator
"""

import sys
import os
import tempfile
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def create_test_data():
    """Create test data files"""
    test_dir = tempfile.mkdtemp()
    
    # Create test file 1
    df1 = pd.DataFrame({
        'Email': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
        'Name': ['Alice Smith', 'Bob Jones', 'Charlie Brown'],
        'Score1': [85, 92, 78]
    })
    file1 = Path(test_dir) / 'test1.xlsx'
    df1.to_excel(file1, index=False)
    
    # Create test file 2
    df2 = pd.DataFrame({
        'email': ['alice@example.com', 'bob@example.com', 'david@example.com'],
        'name': ['Alice Smith', 'Bob Jones', 'David Wilson'],
        'Score2': [90, 88, 95]
    })
    file2 = Path(test_dir) / 'test2.xlsx'
    df2.to_excel(file2, index=False)
    
    # Create dirty data file
    df_dirty = pd.DataFrame({
        'Name': ['  Alice  ', 'Bob', 'Charlie', 'Alice', ''],
        'Email': ['ALICE@example.com', 'bob@example.com  ', 'charlie@example.com', 'ALICE@example.com', 'N/A'],
        'Score': [85, None, 78, 85, 90]
    })
    file_dirty = Path(test_dir) / 'dirty_data.xlsx'
    df_dirty.to_excel(file_dirty, index=False)
    
    return test_dir, file1, file2, file_dirty


def test_table_merger():
    """Test table merger agent"""
    print("\n" + "="*70)
    print("Testing Table Merger Agent")
    print("="*70)
    
    from src.agents.merger_agent import GenericTableMergerAgent
    
    # Create test data
    test_dir, file1, file2, _ = create_test_data()
    
    try:
        agent = GenericTableMergerAgent()
        
        # Test 1: Can handle
        documents = [
            {'path': str(file1), 'format': '.xlsx', 'type': 'spreadsheets'},
            {'path': str(file2), 'format': '.xlsx', 'type': 'spreadsheets'}
        ]
        
        can_handle = agent.can_handle(documents, 'table_merge')
        assert can_handle, "Agent should be able to handle table merge"
        print("✅ Test 1 passed: Agent can handle table merge")
        
        # Test 2: Validate inputs
        is_valid, errors = agent.validate_inputs(documents)
        assert is_valid, f"Validation should pass: {errors}"
        print("✅ Test 2 passed: Input validation works")
        
        # Test 3: Process merge
        config = {'output_format': 'xlsx'}
        result = agent.process(documents, config)
        
        assert result.success, f"Merge should succeed: {result.message}"
        assert result.output_file is not None, "Should generate output file"
        assert result.metadata['tables_merged'] == 2, "Should merge 2 tables"
        print(f"✅ Test 3 passed: Merged {result.metadata['tables_merged']} tables")
        print(f"   Merge column: {result.metadata['merge_column']}")
        print(f"   Total rows: {result.metadata['total_rows']}")
        print(f"   Total columns: {result.metadata['total_columns']}")
        
        # Test 4: Verify merged data
        if result.output_file:
            merged_df = pd.read_excel(result.output_file)
            assert len(merged_df) >= 3, "Should have at least 3 rows"
            assert 'Email' in merged_df.columns or 'email' in merged_df.columns, "Should have email column"
            print(f"✅ Test 4 passed: Merged file has {len(merged_df)} rows")
        
        print("\n✅ All table merger tests passed!")
        return True
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def test_data_cleaner():
    """Test data cleaning agent"""
    print("\n" + "="*70)
    print("Testing Data Cleaning Agent")
    print("="*70)
    
    from src.agents.data_cleaning_agent import DataCleaningAgent
    
    # Create test data
    test_dir, _, _, file_dirty = create_test_data()
    
    try:
        agent = DataCleaningAgent()
        
        # Test 1: Can handle
        documents = [
            {'path': str(file_dirty), 'format': '.xlsx', 'type': 'spreadsheets'}
        ]
        
        can_handle = agent.can_handle(documents, 'data_cleaning')
        assert can_handle, "Agent should be able to handle data cleaning"
        print("✅ Test 1 passed: Agent can handle data cleaning")
        
        # Test 2: Process cleaning
        config = {'output_format': 'xlsx'}
        result = agent.process(documents, config)
        
        assert result.success, f"Cleaning should succeed: {result.message}"
        assert result.output_file is not None, "Should generate output file"
        print(f"✅ Test 2 passed: Cleaned {result.metadata['files_processed']} file(s)")
        print(f"   Rows before: {result.metadata['total_rows_before']}")
        print(f"   Rows after: {result.metadata['total_rows_after']}")
        print(f"   Duplicates removed: {result.metadata['duplicates_removed']}")
        print(f"   Cells cleaned: {result.metadata['cells_cleaned']}")
        
        # Test 3: Verify cleaned data
        if result.output_file:
            cleaned_df = pd.read_excel(result.output_file)
            
            # Check that whitespace was trimmed
            assert all(not str(name).startswith(' ') for name in cleaned_df['Name'] if pd.notna(name)), \
                "Names should have no leading whitespace"
            
            # Check that emails were lowercased
            emails = cleaned_df['Email'].dropna()
            assert all(str(email).islower() for email in emails if email != ''), \
                "Emails should be lowercase"
            
            # Check duplicates removed
            assert len(cleaned_df[cleaned_df.duplicated()]) == 0, "Should have no duplicates"
            
            print(f"✅ Test 3 passed: Data properly cleaned ({len(cleaned_df)} rows)")
        
        print("\n✅ All data cleaning tests passed!")
        return True
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def test_report_generator():
    """Test report generator agent"""
    print("\n" + "="*70)
    print("Testing Report Generator Agent")
    print("="*70)
    
    from src.agents.report_generator_agent import ReportGeneratorAgent
    
    # Create test data
    test_dir, file1, _, _ = create_test_data()
    
    try:
        agent = ReportGeneratorAgent()
        
        # Test 1: Can handle
        documents = [
            {'path': str(file1), 'format': '.xlsx', 'type': 'spreadsheets'}
        ]
        
        can_handle = agent.can_handle(documents, 'report_generation')
        assert can_handle, "Agent should be able to handle report generation"
        print("✅ Test 1 passed: Agent can handle report generation")
        
        # Test 2: Process report generation
        config = {'output_format': 'xlsx'}
        result = agent.process(documents, config)
        
        assert result.success, f"Report generation should succeed: {result.message}"
        assert result.output_file is not None, "Should generate output file"
        print(f"✅ Test 2 passed: Generated {result.metadata['reports_generated']} report(s)")
        
        # Test 3: Verify report structure
        if result.output_file:
            # Read Excel file and check sheets
            excel_file = pd.ExcelFile(result.output_file)
            sheets = excel_file.sheet_names
            
            expected_sheets = ['Summary', 'Data Preview', 'Column Analysis', 
                             'Missing Data', 'Numeric Statistics']
            
            for expected_sheet in expected_sheets:
                assert expected_sheet in sheets, f"Should have {expected_sheet} sheet"
            
            print(f"✅ Test 3 passed: Report has {len(sheets)} sheets")
            print(f"   Sheets: {', '.join(sheets)}")
            
            # Check summary sheet
            summary_df = pd.read_excel(result.output_file, sheet_name='Summary')
            assert len(summary_df) > 0, "Summary sheet should have data"
            print(f"   Summary metrics: {len(summary_df)}")
        
        print("\n✅ All report generator tests passed!")
        return True
        
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir, ignore_errors=True)


def main():
    """Run all substantial capability tests"""
    print("=" * 70)
    print("Testing Substantial Agent Capabilities")
    print("=" * 70)
    print("\nThese tests verify the REAL implementations of:")
    print("  • Table Merger - Intelligent column matching and merging")
    print("  • Data Cleaner - Duplicate removal, standardization")
    print("  • Report Generator - Statistics and formatted reports")
    print()
    
    tests = [
        ("Table Merger", test_table_merger),
        ("Data Cleaner", test_data_cleaner),
        ("Report Generator", test_report_generator),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
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
    
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {passed}/{len(tests)}")
    print(f"❌ Failed: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("🎉 All substantial capability tests passed!")
        print("\nThe bot now has REAL, working implementations for:")
        print("  ✅ Table merging with intelligent column matching")
        print("  ✅ Data cleaning with duplicate removal and standardization")
        print("  ✅ Report generation with multi-sheet analysis")
        print()
        return 0
    else:
        print(f"⚠️  {failed} test(s) failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
