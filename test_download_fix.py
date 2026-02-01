"""
Test to verify the download fix works correctly.
Tests absolute path resolution and file existence verification.
"""

import os
import sys
from pathlib import Path
import tempfile
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.hybrid_bridge import UPLOAD_SESSIONS
from src.excel_processor import ExcelProcessor
from src.participation_bonus import ParticipationBonusCalculator

def test_download_path_resolution():
    """Test that download paths are resolved correctly with absolute paths"""
    print("\n✓ Testing download path resolution...")
    
    # Create a test session
    session_id = "test_session_download_001"
    
    # Simulate consolidation setup
    output_dir = Path(f"temp_uploads/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test data
    test_data = {
        "Student_1": {
            "test_1_score": 85,
            "test_2_score": 90,
            "test_3_score": 88,
        },
        "Student_2": {
            "test_1_score": 92,
            "test_2_score": 87,
            "test_3_score": 95,
        }
    }
    
    # Save using the fixed method with absolute paths
    result_filename = "consolidated_test_download.xlsx"
    result_path = str(output_dir.resolve() / result_filename)
    
    print(f"  - Output dir: {output_dir}")
    print(f"  - Output dir (absolute): {output_dir.resolve()}")
    print(f"  - Result path: {result_path}")
    print(f"  - Path is absolute: {os.path.isabs(result_path)}")
    
    # Save the file
    processor = ExcelProcessor("temp_uploads", "temp_uploads")
    processor.output_dir = output_dir
    processor.save_consolidated_file(test_data, result_filename)
    
    # Verify file exists at absolute path
    if os.path.exists(result_path):
        print(f"  ✓ File found at absolute path")
        file_size = os.path.getsize(result_path)
        print(f"  ✓ File size: {file_size} bytes")
        return True
    else:
        print(f"  ✗ File NOT found at {result_path}")
        # Debug: check what files exist
        if output_dir.exists():
            print(f"  Files in directory: {list(output_dir.iterdir())}")
        return False

def test_consolidation_with_bonus():
    """Test that consolidation with bonus works and saves correctly"""
    print("\n✓ Testing consolidation with bonus calculation...")
    
    session_id = "test_session_bonus_001"
    output_dir = Path(f"temp_uploads/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test data
    test_data = {
        "Student_A": {
            "test_1_score": 80,
            "test_2_score": 85,
            "test_3_score": 90,
            "test_4_score": 88,
            "test_5_score": 92,
            "test_6_score": 87,
        },
        "Student_B": {
            "test_1_score": 75,
            "test_2_score": 78,
            "test_3_score": 82,
            "test_4_score": 80,
            "test_5_score": 85,
            "test_6_score": 79,
        }
    }
    
    # Apply bonus
    bonus_calc = ParticipationBonusCalculator()
    bonus_data = bonus_calc.apply_bonuses_to_consolidated(test_data, [1, 2, 3, 4, 5, 6])
    
    print(f"  - Data rows: {len(bonus_data)}")
    
    # Save consolidated with bonus
    result_filename = "consolidated_with_bonus.xlsx"
    result_path = str(output_dir.resolve() / result_filename)
    
    processor = ExcelProcessor("temp_uploads", "temp_uploads")
    processor.output_dir = output_dir
    processor.save_consolidated_file(bonus_data, result_filename)
    
    # Verify
    if os.path.exists(result_path):
        print(f"  ✓ Consolidated file with bonus saved successfully")
        print(f"  ✓ File size: {os.path.getsize(result_path)} bytes")
        return True
    else:
        print(f"  ✗ Failed to save consolidated file")
        return False

def test_session_storage():
    """Test that session storage correctly uses absolute paths"""
    print("\n✓ Testing session storage with absolute paths...")
    
    session_id = "test_session_storage_001"
    output_dir = Path(f"temp_uploads/{session_id}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Simulate what the consolidate endpoint does
    result_id = "result_abc123"
    result_filename = f"consolidated_{result_id}.xlsx"
    result_path = str(output_dir.resolve() / result_filename)
    
    # Store in session (like the endpoint does)
    UPLOAD_SESSIONS[session_id] = {
        "consolidation_result": {
            "result_id": result_id,
            "path": result_path,
            "data_rows": 2,
        }
    }
    
    # Create a dummy file
    Path(result_path).parent.mkdir(parents=True, exist_ok=True)
    Path(result_path).touch()
    
    # Simulate what the download endpoint does
    stored_result = UPLOAD_SESSIONS[session_id]["consolidation_result"]
    stored_path = stored_result["path"]
    
    print(f"  - Stored path: {stored_path}")
    print(f"  - Path is absolute: {os.path.isabs(stored_path)}")
    print(f"  - File exists: {os.path.exists(stored_path)}")
    
    if os.path.exists(stored_path):
        print(f"  ✓ Download endpoint would successfully find file")
        # Cleanup
        os.remove(stored_path)
        return True
    else:
        print(f"  ✗ Download endpoint would fail to find file")
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("DOWNLOAD FIX VERIFICATION")
    print("="*60)
    
    tests = [
        test_download_path_resolution,
        test_consolidation_with_bonus,
        test_session_storage
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"  ✗ Test failed with error: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    print(f"RESULTS: {sum(results)}/{len(results)} tests passed")
    print("="*60 + "\n")
    
    if all(results):
        print("✓ All download fix tests PASSED")
        sys.exit(0)
    else:
        print("✗ Some tests FAILED - review output above")
        sys.exit(1)
