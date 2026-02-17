#!/usr/bin/env python3
"""
Display Active Model with Token Usage Gauges
=============================================

Combined display showing:
- Active AI Model (AUTO\\MODEL format)
- Token Usage Gauges (Min/Current/Max)
- Subscription Usage
- Cost Tracking (Local vs Cloud)

Perfect for header display in Cursor IDE or terminal.
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from cursor_active_model_tracker import CursorActiveModelTracker
    from token_gauge_display import TokenGaugeDisplay
    from token_hud_display import TokenHUDDisplay
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


def get_combined_header() -> str:
    """Get combined header string with model and token gauges."""
    # Get active model
    tracker = CursorActiveModelTracker()
    status = tracker.get_status()

    active_model = status.get('active_model', 'Unknown')
    is_auto = status.get('is_auto_mode', False)

    # Format model display
    if is_auto or active_model.startswith("AUTO\\"):
        model_display = active_model if active_model.startswith("AUTO\\") else f"AUTO\\{active_model}"
    else:
        model_display = active_model

    # Get HUD display (Iron Man style)
    try:
        hud_display = TokenHUDDisplay()
        token_info = hud_display.get_compact_hud()
    except Exception:
        # Fallback to regular gauge
        try:
            gauge_display = TokenGaugeDisplay()
            token_info = gauge_display.get_compact_display()
        except Exception:
            token_info = "Token Usage: Not available"

    # Combine
    header = f"MODEL: {model_display} | {token_info}"

    return header


def print_full_display():
    """Print full combined display."""
    # Model info
    tracker = CursorActiveModelTracker()
    status = tracker.get_status()

    active_model = status.get('active_model', 'Unknown')
    is_auto = status.get('is_auto_mode', False)
    model_type = status.get('model_type', 'unknown')

    if is_auto or active_model.startswith("AUTO\\"):
        model_display = active_model if active_model.startswith("AUTO\\") else f"AUTO\\{active_model}"
    else:
        model_display = active_model

    print("\n" + "=" * 100)
    print("🤖 ACTIVE MODEL & TOKEN USAGE")
    print("=" * 100)
    print()
    print(f"📊 ACTIVE MODEL: {model_display} ({model_type})")
    if status.get('endpoint'):
        print(f"   Endpoint: {status.get('endpoint')}")
    print()

    # Token HUD (Iron Man style)
    try:
        hud_display = TokenHUDDisplay()
        print(hud_display.get_hud_display())
    except Exception as e:
        # Fallback to regular gauge
        try:
            gauge_display = TokenGaugeDisplay()
            print(gauge_display.get_header_display())
        except Exception as e2:
            print(f"   ⚠️  Token displays unavailable: {e}, {e2}")

    print()
    print("=" * 100)
    print()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Display Active Model with Token Usage (Iron Man HUD)")
    parser.add_argument("--header", action="store_true", help="Print single-line header with HUD")
    parser.add_argument("--full", action="store_true", help="Print full display with HUD")
    parser.add_argument("--hud-only", action="store_true", help="Print HUD only (Iron Man style)")

    args = parser.parse_args()

    if args.header:
        print(get_combined_header())
    elif args.hud_only:
        try:
            hud_display = TokenHUDDisplay()
            hud_display.print_hud()
        except Exception as e:
            print(f"❌ HUD error: {e}")
    else:
        print_full_display()


if __name__ == "__main__":


    main()