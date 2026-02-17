#!/usr/bin/env python3
"""
Comprehensive Test Suite for MANUS/JARVIS Systems

Tests all components:
1. God Cycle
2. Chained Ask Cycle
3. Always Listening
4. Hands-Free Cursor Control
5. Intelligent Warm Recycle
6. MANUS Unified Control
7. Keyboard Shortcuts
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
import traceback
import logging
logger = logging.getLogger("test_all_manus_jarvis_systems")


script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Test results
test_results = {
    "timestamp": datetime.now().isoformat(),
    "tests": [],
    "passed": 0,
    "failed": 0,
    "skipped": 0
}


def log_test(name: str, status: str, message: str = "", details: dict = None):
    """Log a test result"""
    result = {
        "name": name,
        "status": status,
        "message": message,
        "details": details or {}
    }
    test_results["tests"].append(result)

    if status == "passed":
        test_results["passed"] += 1
        icon = "✅"
    elif status == "failed":
        test_results["failed"] += 1
        icon = "❌"
    else:
        test_results["skipped"] += 1
        icon = "⏭️"

    print(f"   {icon} {name}: {status.upper()}")
    if message:
        print(f"      {message}")


def test_god_cycle():
    """Test JARVIS God Cycle"""
    print("\n" + "="*60)
    print("🧪 Test 1: JARVIS God Cycle")
    print("="*60)

    try:
        from jarvis_god_cycle import JARVISGodCycle, CycleHealth, CycleMetrics, ConversationMemory

        # Test 1.1: Import
        log_test("God Cycle Import", "passed")

        # Test 1.2: Initialization
        god_cycle = JARVISGodCycle()
        log_test("God Cycle Initialization", "passed", 
                f"Health: {god_cycle.health.value}")

        # Test 1.3: Metrics
        metrics = god_cycle.metrics
        assert metrics.total_cycles == 0
        log_test("Metrics Initialization", "passed")

        # Test 1.4: Memory
        god_cycle.memory.add_interaction("test", "response")
        assert len(god_cycle.memory.recent_commands) == 1
        log_test("Conversation Memory", "passed")

        # Test 1.5: Status
        status = god_cycle.get_status()
        assert "running" in status
        assert "health" in status
        log_test("Status Reporting", "passed")

        # Test 1.6: Status Response
        response = god_cycle._get_status_response()
        assert "God Cycle" in response
        log_test("Status Response Generation", "passed")

    except ImportError as e:
        log_test("God Cycle Import", "failed", str(e))
    except Exception as e:
        log_test("God Cycle Test", "failed", str(e))


def test_always_listening():
    """Test Always Listening"""
    print("\n" + "="*60)
    print("🧪 Test 2: Always Listening")
    print("="*60)

    try:
        from jarvis_always_listening import JARVISAlwaysListening, AZURE_SPEECH_AVAILABLE

        # Test 2.1: Import
        log_test("Always Listening Import", "passed")

        # Test 2.2: Azure Speech SDK
        if AZURE_SPEECH_AVAILABLE:
            log_test("Azure Speech SDK", "passed")
        else:
            log_test("Azure Speech SDK", "skipped", "Not installed")

        # Test 2.3: Initialization
        listener = JARVISAlwaysListening()
        log_test("Always Listening Initialization", "passed")

        # Test 2.4: Azure credentials
        if listener.azure_speech_key:
            log_test("Azure Speech Credentials", "passed", "Key retrieved from vault")
        else:
            log_test("Azure Speech Credentials", "skipped", "Key not available")

        # Test 2.5: Transcription queue
        assert listener.transcription_queue is not None
        log_test("Transcription Queue", "passed")

    except ImportError as e:
        log_test("Always Listening Import", "failed", str(e))
    except Exception as e:
        log_test("Always Listening Test", "failed", str(e))


def test_hands_free_control():
    """Test Hands-Free Cursor Control"""
    print("\n" + "="*60)
    print("🧪 Test 3: Hands-Free Cursor Control")
    print("="*60)

    try:
        from jarvis_hands_free_cursor_control import (
            JARVISHandsFreeCursorControl,
            KeyboardShortcutExecutor,
            PYNPUT_AVAILABLE
        )

        # Test 3.1: Import
        log_test("Hands-Free Control Import", "passed")

        # Test 3.2: Pynput availability
        if PYNPUT_AVAILABLE:
            log_test("Pynput Library", "passed")
        else:
            log_test("Pynput Library", "skipped", "Not installed")

        # Test 3.3: Keyboard executor
        if PYNPUT_AVAILABLE:
            executor = KeyboardShortcutExecutor()
            assert executor.keyboard is not None
            log_test("Keyboard Executor", "passed")

            # Test 3.4: Shortcut registry
            shortcuts = executor.CURSOR_SHORTCUTS
            assert "cursor_chat" in shortcuts
            assert "save_file" in shortcuts
            assert "toggle_terminal" in shortcuts
            log_test("Shortcut Registry", "passed", f"{len(shortcuts)} shortcuts registered")
        else:
            log_test("Keyboard Executor", "skipped", "Pynput not available")
            log_test("Shortcut Registry", "skipped", "Pynput not available")

        # Test 3.5: Control initialization
        control = JARVISHandsFreeCursorControl()
        log_test("Hands-Free Control Initialization", "passed")

        # Test 3.6: Command parsing
        intent = control._parse_command_intent("open chat")
        assert intent["type"] == "open_chat"
        log_test("Command Parsing", "passed", f"Type: {intent['type']}")

    except ImportError as e:
        log_test("Hands-Free Control Import", "failed", str(e))
    except Exception as e:
        log_test("Hands-Free Control Test", "failed", str(e))


def test_warm_recycle():
    """Test Intelligent Warm Recycle"""
    print("\n" + "="*60)
    print("🧪 Test 4: Intelligent Warm Recycle")
    print("="*60)

    try:
        from cursor_intelligent_warm_recycle import (
            CursorIntelligentWarmRecycle,
            RecycleReason,
            RecycleDecision,
            CursorProcessInfo
        )

        # Test 4.1: Import
        log_test("Warm Recycle Import", "passed")

        # Test 4.2: Initialization
        recycle = CursorIntelligentWarmRecycle()
        log_test("Warm Recycle Initialization", "passed")

        # Test 4.3: Process detection
        processes = recycle.find_cursor_processes()
        log_test("Cursor Process Detection", "passed", f"Found {len(processes)} processes")

        # Test 4.4: Recycle decision
        decision = recycle.should_recycle()
        log_test("Recycle Decision Engine", "passed", 
                f"Should recycle: {decision.should_recycle}, Reason: {decision.reason}")

        # Test 4.5: Thresholds
        assert recycle.MEMORY_THRESHOLD_MB > 0
        assert recycle.CPU_THRESHOLD_PERCENT > 0
        log_test("Threshold Configuration", "passed",
                f"Memory: {recycle.MEMORY_THRESHOLD_MB}MB, CPU: {recycle.CPU_THRESHOLD_PERCENT}%")

    except ImportError as e:
        log_test("Warm Recycle Import", "failed", str(e))
    except Exception as e:
        log_test("Warm Recycle Test", "failed", str(e))


def test_chained_ask_cycle():
    """Test Chained Ask Cycle"""
    print("\n" + "="*60)
    print("🧪 Test 5: Chained Ask Cycle")
    print("="*60)

    try:
        from manus_chained_ask_cycle import (
            MANUSChainedAskCycle,
            CycleState,
            AskCycleEvent
        )

        # Test 5.1: Import
        log_test("Chained Ask Cycle Import", "passed")

        # Test 5.2: Initialization
        cycle = MANUSChainedAskCycle()
        log_test("Chained Ask Cycle Initialization", "passed")

        # Test 5.3: State
        assert cycle.current_state == CycleState.IDLE
        log_test("Initial State", "passed", f"State: {cycle.current_state.value}")

        # Test 5.4: Configuration
        assert cycle.config is not None
        assert "auto_recycle_check_interval" in cycle.config
        log_test("Configuration", "passed")

        # Test 5.5: Status
        status = cycle.get_status()
        assert "running" in status
        log_test("Status Method", "passed")

    except ImportError as e:
        log_test("Chained Ask Cycle Import", "failed", str(e))
    except Exception as e:
        log_test("Chained Ask Cycle Test", "failed", str(e))


def test_manus_unified_control():
    """Test MANUS Unified Control"""
    print("\n" + "="*60)
    print("🧪 Test 6: MANUS Unified Control")
    print("="*60)

    try:
        from manus_unified_control import (
            MANUSUnifiedControl,
            ControlArea,
            ControlOperation
        )

        # Test 6.1: Import
        log_test("MANUS Unified Control Import", "passed")

        # Test 6.2: Control areas
        areas = list(ControlArea)
        log_test("Control Areas", "passed", f"{len(areas)} areas defined")

        # Test 6.3: Initialization
        project_root = Path(__file__).parent.parent.parent
        control = MANUSUnifiedControl(project_root=project_root)
        log_test("MANUS Unified Control Initialization", "passed")

        # Test 6.4: Health check
        health = control.get_health_status()
        log_test("Health Check", "passed", f"Status: {health.get('overall_status', 'unknown')}")

    except ImportError as e:
        log_test("MANUS Unified Control Import", "failed", str(e))
    except Exception as e:
        log_test("MANUS Unified Control Test", "failed", str(e))


def test_manus_cursor_controller():
    """Test MANUS Cursor Controller"""
    print("\n" + "="*60)
    print("🧪 Test 7: MANUS Cursor Controller")
    print("="*60)

    try:
        from manus_cursor_controller import (
            ManusCursorController,
            CursorState,
            TroubleshootingAction,
            PYNPUT_AVAILABLE
        )

        # Test 7.1: Import
        log_test("MANUS Cursor Controller Import", "passed")

        # Test 7.2: Pynput
        if PYNPUT_AVAILABLE:
            log_test("Pynput for Cursor Controller", "passed")
        else:
            log_test("Pynput for Cursor Controller", "skipped", "Not installed")

        # Test 7.3: Initialization
        controller = ManusCursorController()
        log_test("Cursor Controller Initialization", "passed")

        # Test 7.4: Troubleshooting actions
        actions = controller.troubleshooting_actions
        log_test("Troubleshooting Actions", "passed", f"{len(actions)} actions registered")

        # Test 7.5: State retrieval
        state = controller.get_cursor_state()
        log_test("Cursor State Retrieval", "passed")

    except ImportError as e:
        log_test("MANUS Cursor Controller Import", "failed", str(e))
    except Exception as e:
        log_test("MANUS Cursor Controller Test", "failed", str(e))


def test_keyboard_shortcuts():
    """Test Keyboard Shortcuts"""
    print("\n" + "="*60)
    print("🧪 Test 8: Keyboard Shortcuts")
    print("="*60)

    try:
        from jarvis_hands_free_cursor_control import KeyboardShortcutExecutor, PYNPUT_AVAILABLE

        if not PYNPUT_AVAILABLE:
            log_test("Keyboard Shortcuts", "skipped", "Pynput not available")
            return

        executor = KeyboardShortcutExecutor()

        # Test 8.1: Shortcut definitions
        shortcuts = executor.CURSOR_SHORTCUTS

        required_shortcuts = [
            "cursor_chat", "open_file", "save_file", "new_file",
            "format_document", "toggle_terminal", "start_debugging"
        ]

        for shortcut in required_shortcuts:
            if shortcut in shortcuts:
                log_test(f"Shortcut: {shortcut}", "passed")
            else:
                log_test(f"Shortcut: {shortcut}", "failed", "Not defined")

        # Test 8.2: Window detection
        window = executor.find_cursor_window()
        if window:
            log_test("Cursor Window Detection", "passed")
        else:
            log_test("Cursor Window Detection", "skipped", "Cursor not running")

    except Exception as e:
        log_test("Keyboard Shortcuts Test", "failed", str(e))


def test_docker_file():
    """Test Dockerfile structure"""
    print("\n" + "="*60)
    print("🧪 Test 9: Dockerfile")
    print("="*60)

    try:
        dockerfile_path = Path(__file__).parent.parent.parent / "containerization" / "services" / "manus-mcp-server" / "Dockerfile"

        if not dockerfile_path.exists():
            log_test("Dockerfile Exists", "failed", "File not found")
            return

        log_test("Dockerfile Exists", "passed")

        content = dockerfile_path.read_text()

        # Check for required elements
        checks = [
            ("FROM python", "Base Image"),
            ("COPY scripts/python/jarvis_god_cycle.py", "God Cycle Script"),
            ("COPY scripts/python/manus_chained_ask_cycle.py", "Chained Ask Cycle Script"),
            ("COPY scripts/python/jarvis_always_listening.py", "Always Listening Script"),
            ("COPY scripts/python/cursor_intelligent_warm_recycle.py", "Warm Recycle Script"),
            ("HEALTHCHECK", "Health Check"),
            ("ENTRYPOINT", "Entry Point"),
        ]

        for check_str, check_name in checks:
            if check_str in content:
                log_test(f"Dockerfile: {check_name}", "passed")
            else:
                log_test(f"Dockerfile: {check_name}", "failed", f"'{check_str}' not found")

    except Exception as e:
        log_test("Dockerfile Test", "failed", str(e))


def test_requirements():
    """Test requirements.txt"""
    print("\n" + "="*60)
    print("🧪 Test 10: Requirements")
    print("="*60)

    try:
        requirements_path = Path(__file__).parent.parent.parent / "containerization" / "services" / "manus-mcp-server" / "requirements.txt"

        if not requirements_path.exists():
            log_test("Requirements File Exists", "failed", "File not found")
            return

        log_test("Requirements File Exists", "passed")

        content = requirements_path.read_text()

        required_packages = ["mcp", "azure-cognitiveservices-speech", "psutil", "pynput"]

        for pkg in required_packages:
            if pkg in content:
                log_test(f"Requirement: {pkg}", "passed")
            else:
                log_test(f"Requirement: {pkg}", "failed", "Not in requirements")

    except Exception as e:
        log_test("Requirements Test", "failed", str(e))


def main():
    try:
        """Run all tests"""
        print("="*70)
        print("🧪 MANUS/JARVIS Comprehensive Test Suite")
        print("="*70)
        print(f"   Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        start_time = time.time()

        # Run all tests
        test_god_cycle()
        test_always_listening()
        test_hands_free_control()
        test_warm_recycle()
        test_chained_ask_cycle()
        test_manus_unified_control()
        test_manus_cursor_controller()
        test_keyboard_shortcuts()
        test_docker_file()
        test_requirements()

        elapsed = time.time() - start_time

        # Summary
        print("\n" + "="*70)
        print("📊 TEST SUMMARY")
        print("="*70)
        print(f"   ✅ Passed:  {test_results['passed']}")
        print(f"   ❌ Failed:  {test_results['failed']}")
        print(f"   ⏭️  Skipped: {test_results['skipped']}")
        print(f"   ⏱️  Time:    {elapsed:.2f}s")
        print()

        total = test_results['passed'] + test_results['failed']
        if total > 0:
            success_rate = (test_results['passed'] / total) * 100
            print(f"   📈 Success Rate: {success_rate:.1f}%")

        print()

        if test_results['failed'] == 0:
            print("   🎉 ALL TESTS PASSED!")
        else:
            print(f"   ⚠️  {test_results['failed']} test(s) failed")

        print("="*70)

        # Save results
        results_file = Path(__file__).parent.parent.parent / "data" / "test_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)

        with open(results_file, 'w') as f:
            json.dump(test_results, f, indent=2)

        print(f"\n📄 Results saved to: {results_file}")

        return test_results['failed'] == 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()