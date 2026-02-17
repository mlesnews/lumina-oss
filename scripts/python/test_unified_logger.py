#!/usr/bin/env python3
"""
Test script for unified logger
Verifies NAS integration and fallback behavior
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from lumina_unified_logger import get_unified_logger, LuminaUnifiedLogger

def test_unified_logger():
    try:
        """Test unified logger functionality"""
        print("=" * 70)
        print("TESTING UNIFIED LOGGER")
        print("=" * 70)
        print()

        # Test 1: Basic logger creation
        print("Test 1: Creating logger...")
        logger = get_unified_logger("Application", "TestService")
        print(f"✅ Logger created: {logger.name}")
        print()

        # Test 2: Log paths
        print("Test 2: Checking log paths...")
        logger_module = LuminaUnifiedLogger("Application", "TestService")
        paths = logger_module.log_paths
        print(f"   Local log: {paths['local']}")
        print(f"   NAS log: {paths['nas']}")
        print(f"   NAS available: {paths['nas_available']}")
        print()

        # Test 3: Write test messages
        print("Test 3: Writing test log messages...")
        logger.info("This is an INFO message")
        logger.warning("This is a WARNING message")
        logger.error("This is an ERROR message")
        print("✅ Test messages written")
        print()

        # Test 4: Verify files exist
        print("Test 4: Verifying log files exist...")
        local_path = Path(paths['local'])
        if local_path.exists():
            print(f"✅ Local log file exists: {local_path}")
            print(f"   Size: {local_path.stat().st_size} bytes")
        else:
            print(f"❌ Local log file missing: {local_path}")

        if paths['nas']:
            nas_path = Path(paths['nas'])
            if nas_path.exists():
                print(f"✅ NAS log file exists: {nas_path}")
                print(f"   Size: {nas_path.stat().st_size} bytes")
            else:
                print(f"⚠️  NAS log file not created (L: drive may not be available)")
        else:
            print("⚠️  NAS logging not available (L: drive not mounted)")
        print()

        # Test 5: Different categories
        print("Test 5: Testing different categories...")
        categories = ["Application", "System", "AI", "Security", "Network", "Performance"]
        for category in categories:
            test_logger = get_unified_logger(category, "TestService")
            test_logger.info(f"Test message for {category} category")
        print("✅ All categories tested")
        print()

        print("=" * 70)
        print("TEST COMPLETE")
        print("=" * 70)
        print()
        print("Check log files:")
        print(f"  Local: {paths['local']}")
        if paths['nas']:
            print(f"  NAS: {paths['nas']}")
        print()

    except Exception as e:
        logger.error(f"Error in test_unified_logger: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    test_unified_logger()
