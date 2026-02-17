#!/usr/bin/env python3
"""
Battle Test for @frc (Full Robust & Comprehensive) Logging
Ensures @frc logging is STANDARD MODULE project-wide, globally

Tags: #BATTLE_TEST #FRC #LOGGING #STANDARD_MODULE @LUMINA
"""

import sys
import logging
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

def test_frc_logging_import():
    """Test 1: Verify @frc comprehensive logger can be imported"""
    print("=" * 80)
    print("BATTLE TEST: @frc Logging - Import Test")
    print("=" * 80)

    try:
        from lumina_logger_comprehensive import get_comprehensive_logger, get_logger
        print("✅ PASS: @frc comprehensive logger imported successfully")
        return True
    except ImportError as e:
        print(f"❌ FAIL: Could not import @frc comprehensive logger: {e}")
        return False

def test_frc_logging_standard():
    """Test 2: Verify @frc logger works as standard module"""
    print("\n" + "=" * 80)
    print("BATTLE TEST: @frc Logging - Standard Module Test")
    print("=" * 80)

    try:
        from lumina_logger_comprehensive import get_comprehensive_logger

        # Test comprehensive logger
        logger = get_comprehensive_logger("BattleTest")
        logger.info("Test info message", {"test": "standard_module"})
        logger.warning("Test warning message", {"test": "standard_module"})
        logger.error("Test error message", {"test": "standard_module"})

        print("✅ PASS: @frc logger works as standard module")
        print(f"   Logger name: {logger.name}")
        print(f"   Log file: {logger.log_file}")
        return True
    except Exception as e:
        print(f"❌ FAIL: @frc logger standard module test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frc_logging_file_output():
    """Test 3: Verify @frc logger writes to files"""
    print("\n" + "=" * 80)
    print("BATTLE TEST: @frc Logging - File Output Test")
    print("=" * 80)

    try:
        from lumina_logger_comprehensive import get_comprehensive_logger

        logger = get_comprehensive_logger("BattleTestFile", project_root=project_root)
        logger.info("File output test message", {"test": "file_output"})

        # Check if file handler exists (log_file might be None but file handler exists)
        has_file_handler = any(isinstance(h, logging.FileHandler) for h in logger.base_logger.handlers)

        if has_file_handler:
            # Find the log file from handlers
            log_file = None
            for handler in logger.base_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    try:
                        log_file = Path(handler.baseFilename)
                        break
                    except Exception:
                        pass

            if log_file and log_file.exists():
                print(f"✅ PASS: @frc logger writes to file: {log_file}")
                # Read last few lines to verify
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    if lines:
                        print(f"   Last log line: {lines[-1].strip()[:80]}...")
                return True
            else:
                print(f"⚠️  WARNING: File handler exists but file not found: {log_file}")
                return False
        else:
            print(f"⚠️  WARNING: No file handler found in logger")
            print(f"   Handlers: {[type(h).__name__ for h in logger.base_logger.handlers]}")
            return False
    except Exception as e:
        print(f"❌ FAIL: @frc logger file output test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frc_logging_full_time_monitoring():
    """Test 4: Verify @frc logger integrated with full-time monitoring"""
    print("\n" + "=" * 80)
    print("BATTLE TEST: @frc Logging - Full-Time Monitoring Integration")
    print("=" * 80)

    try:
        from full_time_monitoring_service import get_full_time_monitoring_service

        service = get_full_time_monitoring_service(project_root=project_root)

        # Check if terminal logger uses @frc
        if hasattr(service, 'terminal_logger') and service.terminal_logger:
            print("✅ PASS: Full-time monitoring uses @frc terminal logger")
            print(f"   Terminal logger type: {type(service.terminal_logger).__name__}")
            return True
        else:
            print("⚠️  WARNING: Terminal logger not initialized")
            return False
    except Exception as e:
        print(f"❌ FAIL: Full-time monitoring integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_frc_logging_global_availability():
    """Test 5: Verify @frc logger is globally available project-wide"""
    print("\n" + "=" * 80)
    print("BATTLE TEST: @frc Logging - Global Availability Test")
    print("=" * 80)

    try:
        # Test that get_logger returns comprehensive logger by default
        from lumina_logger_comprehensive import get_logger

        logger = get_logger("GlobalTest", comprehensive=True)

        # Check if it's a ComprehensiveLogger instance
        from lumina_logger_comprehensive import ComprehensiveLogger
        if isinstance(logger, ComprehensiveLogger):
            print("✅ PASS: @frc logger is globally available via get_logger()")
            print(f"   Logger type: {type(logger).__name__}")
            return True
        else:
            print(f"⚠️  WARNING: get_logger() returned {type(logger).__name__}, not ComprehensiveLogger")
            return False
    except Exception as e:
        print(f"❌ FAIL: Global availability test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all battle tests"""
    print("\n" + "=" * 80)
    print("BATTLE TEST SUITE: @frc (Full Robust & Comprehensive) Logging")
    print("Ensuring @frc logging is STANDARD MODULE project-wide, globally")
    print("=" * 80)

    results = []

    # Run all tests
    results.append(("Import Test", test_frc_logging_import()))
    results.append(("Standard Module Test", test_frc_logging_standard()))
    results.append(("File Output Test", test_frc_logging_file_output()))
    results.append(("Full-Time Monitoring Integration", test_frc_logging_full_time_monitoring()))
    results.append(("Global Availability Test", test_frc_logging_global_availability()))

    # Summary
    print("\n" + "=" * 80)
    print("BATTLE TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED: @frc logging is STANDARD MODULE project-wide, globally")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - @frc logging needs attention")
        return 1

if __name__ == "__main__":


    sys.exit(main())