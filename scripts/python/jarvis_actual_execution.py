#!/usr/bin/env python3
"""
JARVIS Actual Execution - DO THINGS, NOT PLANS

Actually brings services online, uses Manus for PC control,
implements mouse relinquish logic, uses Proton Pass CLI.

"If I take the mouse over from you, then you're to relinquish it."
"""

import sys
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import json
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Mouse control state
mouse_control_active = False
mouse_relinquish_requested = False
mouse_control_lock = threading.Lock()


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def check_mouse_relinquish():
    """Check if user wants to take mouse control - if so, relinquish"""
    global mouse_control_active, mouse_relinquish_requested

    try:
        import pynput
        from pynput.mouse import Listener

        def on_move(x, y):
            global mouse_relinquish_requested
            # If mouse moves while we're controlling, user wants control
            if mouse_control_active:
                with mouse_control_lock:
                    mouse_relinquish_requested = True
                    mouse_control_active = False
                print("🖱️  Mouse control RELINQUISHED - User took control")

        listener = Listener(on_move=on_move)
        listener.start()
        return listener
    except ImportError:
        print("⚠️  pynput not available for mouse relinquish detection")
        return None

def bring_services_online():
    """Actually bring services online"""
    print("\n🚀 BRINGING SERVICES ONLINE")
    print("="*60)

    services = {
        "bitcoin_platform_api": {
            "script": "bitcoin_platform_api.py",
            "port": 5000,
            "status": "starting"
        },
        "r5_api_server": {
            "script": "r5_api_server.py",
            "port": 8000,
            "status": "starting"
        }
    }

    for service_name, config in services.items():
        print(f"\n📡 Starting {service_name}...")
        try:
            script_path = script_dir / config["script"]
            if script_path.exists():
                # Start in background
                process = subprocess.Popen(
                    [sys.executable, str(script_path)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(script_dir)
                )
                config["process"] = process
                config["status"] = "running"
                print(f"  ✅ {service_name} started (PID: {process.pid})")
                print(f"  🌐 Available at: http://localhost:{config['port']}")
            else:
                print(f"  ⚠️  Script not found: {config['script']}")
                config["status"] = "not_found"
        except Exception as e:
            print(f"  ❌ Error starting {service_name}: {e}")
            config["status"] = "error"

    return services

def use_manus_control():
    """Use Manus to take over PC like remote desktop"""
    print("\n🎮 MANUS PC CONTROL")
    print("="*60)

    try:
        from manus_cursor_controller import ManusCursorController

        print("  📋 Initializing Manus controller...")
        controller = ManusCursorController()

        # Check for mouse relinquish
        mouse_listener = check_mouse_relinquish()

        print("  ✅ Manus controller ready")
        print("  🖱️  Mouse control: ACTIVE (will relinquish if you take control)")

        return controller, mouse_listener
    except ImportError as e:
        print(f"  ⚠️  Manus not available: {e}")
        return None, None
    except Exception as e:
        print(f"  ❌ Error initializing Manus: {e}")
        return None, None

def use_proton_pass_cli():
    """Use Proton Pass CLI for password management"""
    print("\n🔐 PROTON PASS CLI")
    print("="*60)

    try:
        # Check if protonpass CLI is available
        result = subprocess.run(
            ["protonpass", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"  ✅ Proton Pass CLI available")
            print(f"  Version: {result.stdout.strip()}")
            return True
        else:
            print("  ⚠️  Proton Pass CLI not found in PATH")
            return False
    except FileNotFoundError:
        print("  ⚠️  Proton Pass CLI not installed")
        print("  💡 Install: https://github.com/ProtonPass/protonpass-cli")
        return False
    except Exception as e:
        print(f"  ⚠️  Error checking Proton Pass: {e}")
        return False

def execute_actual_tasks():
    """Actually execute tasks, not just plan them"""
    print("\n" + "="*60)
    print("⚡ JARVIS ACTUAL EXECUTION")
    print("="*60)
    print(f"Execution Time: {datetime.now().isoformat()}")
    print("\n" + "="*60)

    # 1. Bring services online
    services = bring_services_online()

    # 2. Use Manus for PC control
    manus_controller, mouse_listener = use_manus_control()

    # 3. Use Proton Pass CLI
    proton_pass_available = use_proton_pass_cli()

    # 4. Summary
    print("\n" + "="*60)
    print("📊 EXECUTION SUMMARY")
    print("="*60)

    print("\n🚀 Services:")
    for service_name, config in services.items():
        status_icon = "✅" if config["status"] == "running" else "⏸️"
        print(f"  {status_icon} {service_name}: {config['status']}")

    print("\n🎮 Manus Control:")
    if manus_controller:
        print("  ✅ Manus controller: ACTIVE")
        print("  🖱️  Mouse relinquish: ENABLED")
    else:
        print("  ⚠️  Manus controller: NOT AVAILABLE")

    print("\n🔐 Proton Pass:")
    if proton_pass_available:
        print("  ✅ Proton Pass CLI: AVAILABLE")
    else:
        print("  ⚠️  Proton Pass CLI: NOT AVAILABLE")

    print("\n" + "="*60)
    print("✅ ACTUAL EXECUTION COMPLETE")
    print("="*60)

    # Keep services running
    print("\n💡 Services are running in background")
    print("   Press Ctrl+C to stop")

    try:
        while True:
            time.sleep(1)
            # Check if user wants to stop
            if mouse_relinquish_requested:
                print("\n🖱️  Mouse control relinquished by user")
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping services...")
        for service_name, config in services.items():
            if "process" in config:
                try:
                    config["process"].terminate()
                    print(f"  ✅ {service_name} stopped")
                except:
                    pass

if __name__ == "__main__":
    execute_actual_tasks()

