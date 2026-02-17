#!/usr/bin/env python3
"""
Test File Auto-Close System - Comprehensive testing and validation
"""

import asyncio
import sys
import time
from pathlib import Path
from file_auto_close_manager import FileAutoCloseManager


async def test_basic_functionality():
    """Test basic file registration and pinning"""
    print("🧪 Testing basic functionality...")

    manager = FileAutoCloseManager()

    # Test file registration
    test_file = str(Path(__file__).resolve())
    manager.register_file_open(test_file, "test_workspace")

    # Verify registration
    status = manager.get_status_report()
    assert status['active_files'] >= 1, "File should be registered"

    # Test pinning
    manager.pin_file(test_file, "Test pin")
    status = manager.get_status_report()
    assert status['pinned_files'] >= 1, "File should be pinned"

    # Test unpinning
    manager.unpin_file(test_file)
    status = manager.get_status_report()
    assert status['pinned_files'] == 0, "File should be unpinned"

    print("✅ Basic functionality tests passed")


async def test_decision_engine():
    """Test V3 and JARVIS decisioning"""
    print("🧪 Testing decision engine...")

    manager = FileAutoCloseManager()

    # Create a test file session
    test_file = str(Path(__file__).resolve())
    manager.register_file_open(test_file)

    # Test evaluation (should not close recently opened file)
    should_close, reason, context = await manager.evaluate_file_for_close(test_file)
    assert not should_close, "Recently opened file should not be closed"
    assert "age_minutes" in context, "Context should include age information"

    print("✅ Decision engine tests passed")


async def test_auto_close_processing():
    """Test auto-close processing"""
    print("🧪 Testing auto-close processing...")

    manager = FileAutoCloseManager()

    # Add a test file
    test_file = str(Path(__file__).resolve())
    manager.register_file_open(test_file)

    # Process auto-close (should find the file but not close it since it's recent)
    results = await manager.process_auto_close()
    # Note: The file might not be processed if it's pinned or recently opened
    # The test just verifies the method runs without errors
    assert 'processed' in results, "Should return results dictionary"
    assert 'closed' in results, "Should include closed count"
    assert 'kept_open' in results, "Should include kept_open count"

    print("✅ Auto-close processing tests passed")


def test_cli_interface():
    """Test CLI interface components"""
    print("🧪 Testing CLI interface...")

    from file_pin_manager import main as pin_main

    # Test would require mocking stdin/stdout
    # For now, just verify imports work
    print("✅ CLI interface imports verified")


async def main():
    """Run all tests"""
    print("🚀 Starting File Auto-Close System Tests")
    print("=" * 50)

    try:
        await test_basic_functionality()
        await test_decision_engine()
        await test_auto_close_processing()
        test_cli_interface()

        print("=" * 50)
        print("🎉 All tests passed! File Auto-Close System is ready.")
        print("\n📋 Next Steps:")
        print("1. Install the VSCode extension: vscode-extensions/file-auto-close/")
        print("2. Use VSCode tasks for management")
        print("3. Pin important files to prevent auto-close")
        print("4. Monitor status with: File Auto-Close: Status")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":


    asyncio.run(main())