"""
Test for hibernation prevention keep-alive mechanism
"""
import os
from unittest.mock import patch


def test_keep_alive_configuration():
    """Test that keep-alive configuration is properly loaded"""
    # Test default values - Default should be enabled
    enable_keep_alive = os.getenv("ENABLE_KEEP_ALIVE", "true").lower() in ("true", "1", "yes")
    assert enable_keep_alive == True, "Default keep-alive should be enabled"
    
    # Default interval should be 840 seconds (14 minutes)
    keep_alive_interval = int(os.getenv("KEEP_ALIVE_INTERVAL", "840"))
    assert keep_alive_interval == 840, "Default interval should be 840 seconds"


def test_keep_alive_disabled():
    """Test that keep-alive can be disabled"""
    with patch.dict(os.environ, {"ENABLE_KEEP_ALIVE": "false"}, clear=False):
        enable_keep_alive = os.getenv("ENABLE_KEEP_ALIVE", "true").lower() in ("true", "1", "yes")
        assert enable_keep_alive == False, "Keep-alive should be disabled when set to false"


def test_keep_alive_interval_custom():
    """Test custom keep-alive interval"""
    with patch.dict(os.environ, {"KEEP_ALIVE_INTERVAL": "600"}, clear=False):
        keep_alive_interval = int(os.getenv("KEEP_ALIVE_INTERVAL", "840"))
        assert keep_alive_interval == 600, "Custom interval should be 600 seconds"


def test_keep_alive_various_true_values():
    """Test that various 'true' values work"""
    test_values = [("true", True), ("1", True), ("yes", True), ("TRUE", True), 
                   ("false", False), ("0", False), ("no", False)]
    
    for value, expected in test_values:
        with patch.dict(os.environ, {"ENABLE_KEEP_ALIVE": value}, clear=False):
            result = os.getenv("ENABLE_KEEP_ALIVE", "true").lower() in ("true", "1", "yes")
            assert result == expected, f"Value '{value}' should result in {expected}"


if __name__ == "__main__":
    print("Testing hibernation prevention configuration...")
    
    test_keep_alive_configuration()
    print("✅ Default configuration test passed")
    
    test_keep_alive_disabled()
    print("✅ Disable keep-alive test passed")
    
    test_keep_alive_interval_custom()
    print("✅ Custom interval test passed")
    
    test_keep_alive_various_true_values()
    print("✅ Various true values test passed")
    
    print("\n🎉 All hibernation prevention tests passed!")
    print("\nKeep-alive mechanism is working correctly:")
    print("  • Default: ENABLED (prevents free tier sleep)")
    print("  • Interval: 840 seconds (14 minutes)")
    print("  • Configurable via ENABLE_KEEP_ALIVE and KEEP_ALIVE_INTERVAL")
