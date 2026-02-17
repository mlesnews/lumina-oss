#!/usr/bin/env python3
"""
Quick Check: What AI Model is Cursor Using Right Now?

When Cursor is set to "Auto", this script helps you see:
1. What model is configured as default
2. What models are available
3. How to see the active model in Cursor's UI

Usage:
    python check_active_model.py
"""

import json
from pathlib import Path
import sys

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from cursor_active_model_tracker import CursorActiveModelTracker
except ImportError:
    print("❌ Could not import cursor_active_model_tracker")
    sys.exit(1)

try:
    from token_gauge_display import TokenGaugeDisplay
    HAS_TOKEN_GAUGES = True
except ImportError:
    HAS_TOKEN_GAUGES = False


def print_model_info():
    """Print current model information."""
    tracker = CursorActiveModelTracker()

    # Get current status
    status = tracker.get_status()

    # Also get fresh model details
    model_details = tracker.get_active_model()

    print("\n" + "=" * 70)
    print("🤖 CURSOR ACTIVE MODEL CHECK")
    print("=" * 70)
    print()

    # Show active model
    active_model = status.get('active_model', 'Unknown')
    model_type = status.get('model_type', 'unknown')
    is_auto = status.get('is_auto_mode', False)

    print(f"📊 CURRENT STATUS:")
    # Format display: AUTO\MODEL or just MODEL
    if is_auto or active_model.startswith("AUTO\\"):
        display_model = active_model if active_model.startswith("AUTO\\") else f"AUTO\\{active_model}"
        print(f"   Active Model: {display_model}")
    else:
        print(f"   Active Model: {active_model}")
    print(f"   Model Type: {model_type}")

    if status.get('provider') and status.get('provider') != 'unknown':
        print(f"   Provider: {status.get('provider')}")

    if status.get('endpoint'):
        print(f"   Endpoint: {status.get('endpoint')}")

    if status.get('is_local'):
        print(f"   🌐 Local Model: Yes")
    else:
        print(f"   ☁️  Cloud Model: Yes")

    print()
    print("=" * 70)
    print()

    # If Auto mode, explain how to see actual model
    if is_auto or active_model.startswith("AUTO\\"):
        print("⚠️  CURSOR IS IN AUTO MODE")
        print()
        actual_model = active_model.replace("AUTO\\", "") if active_model.startswith("AUTO\\") else active_model
        print(f"   Detected Model: {actual_model}")
        print()
        print("   When Auto mode is active, Cursor dynamically selects models.")
        print("   The format 'AUTO\\MODEL' shows Auto mode with detected model.")
        print()
        print("   To see which model is ACTUALLY being used:")
        print("   1. Look at the chat input dropdown in Cursor UI")
        print("   2. Check the network tab (F12) during a request")
        print("   3. The status file tracks the last detected model")
        print()
    else:
        print(f"✅ Model is explicitly set to: {active_model}")
        print()

    # Show available models
    print("=" * 70)
    print("📋 AVAILABLE MODELS:")
    print("=" * 70)

    try:
        settings_path = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)

            # Check chat models
            chat_models = settings.get("cursor.chat.customModels", [])
            if chat_models:
                print("\n   Chat Models:")
                for model in chat_models:
                    name = model.get("name", "Unknown")
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase", "default")
                    print(f"      • {name} ({provider})")
                    if endpoint != "default":
                        print(f"        └─ {endpoint}")

            # Check composer models
            composer_models = settings.get("cursor.composer.customModels", [])
            if composer_models:
                print("\n   Composer Models:")
                for model in composer_models:
                    name = model.get("name", "Unknown")
                    provider = model.get("provider", "unknown")
                    endpoint = model.get("apiBase", "default")
                    print(f"      • {name} ({provider})")
                    if endpoint != "default":
                        print(f"        └─ {endpoint}")
    except Exception as e:
        print(f"   ⚠️  Could not read available models: {e}")

    print()
    print("=" * 70)
    print()

    # Token usage gauges
    if HAS_TOKEN_GAUGES:
        print()
        print("=" * 70)
        print("💰 TOKEN USAGE GAUGES")
        print("=" * 70)
        try:
            gauge_display = TokenGaugeDisplay()
            print(gauge_display.get_compact_display())
        except Exception as e:
            print(f"   ⚠️  Could not load token gauges: {e}")
        print()

    # Quick tips
    print("💡 QUICK TIPS:")
    print("   • To see model in UI: Look at chat input dropdown")
    print("   • To change model: Click model selector in chat")
    print("   • To check status: Run 'python check_active_model.py'")
    print("   • To monitor: Run 'python cursor_active_model_tracker.py --monitor'")
    print("   • Token gauges: Run 'python token_gauge_display.py'")
    print()


if __name__ == "__main__":
    print_model_info()
