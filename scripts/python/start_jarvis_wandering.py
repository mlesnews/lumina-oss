#!/usr/bin/env python3
"""
Start JARVIS Wandering - Desktop Animated Assistant

Starts JARVIS as an animated character that wanders around the desktop,
with support for different character "hats" (personas).

Tags: #JARVIS #WANDERING #ANIMATED #CHARACTER_HATS @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartJARVISWandering")


def start_jarvis(character_hat: str = None, size: int = 120):
    """Start JARVIS as animated wandering character

    Args:
        character_hat: Character hat ID to use (default: "jarvis_base")
        size: Window size (default: 120 to match ACE)
    """
    try:
        from jarvis_wandering_system import JARVISWanderingSystem
        logger.info("🤖 Starting JARVIS wandering...")

        jarvis = JARVISWanderingSystem(
            character_hat=character_hat,
            size=size
        )

        # Start JARVIS - this will block (tkinter mainloop)
        # Run in a separate thread so we can return the instance
        def start_jarvis_thread():
            try:
                jarvis.start()
            except Exception as e:
                logger.error(f"Error starting JARVIS: {e}")
                import traceback
                traceback.print_exc()

        thread = threading.Thread(target=start_jarvis_thread, daemon=False)
        thread.start()

        # Give it a moment to create window
        time.sleep(1)

        logger.info("✅ JARVIS started (should be visible and wandering)")
        return jarvis
    except Exception as e:
        logger.error(f"❌ Failed to start JARVIS: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function"""
    import argparse
    parser = argparse.ArgumentParser(description="Start JARVIS Wandering")
    parser.add_argument("--hat", type=str, help="Character hat ID (jarvis_base, ultron, ultimate_iron_man, jedi)")
    parser.add_argument("--size", type=int, default=120, help="Window size")
    args = parser.parse_args()

    print("=" * 80)
    print("🤖 STARTING JARVIS WANDERING")
    print("=" * 80)
    print()
    print("Features:")
    print("  ✅ Wanders around desktop (like ACE)")
    print("  ✅ Smooth movement and visual effects")
    print("  ✅ Character 'hats' support (different personas)")
    print()

    if args.hat:
        print(f"Character Hat: {args.hat}")
    else:
        print("Character Hat: jarvis_base (default)")
    print()
    print("=" * 80)
    print()

    jarvis = start_jarvis(character_hat=args.hat, size=args.size)

    if jarvis:
        print("✅ JARVIS is now wandering on your desktop!")
        print()
        print("Available character hats:")
        for hat_id, hat in jarvis.character_hats.items():
            status = "✓" if hat_id == jarvis.current_hat_id else " "
            print(f"  {status} {hat_id}: {hat.name} - {hat.description}")
        print()
        print("To switch character hat, use:")
        print("  jarvis.switch_character_hat('hat_id')")
        print()
        print("Press Ctrl+C to stop")
        print("=" * 80)
        print()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping JARVIS...")
            jarvis.stop()
            print("✅ Stopped")

            # Cleanup all VA windows except ACE
            print()
            print("🧹 Cleaning up VA windows (keeping ACE)...")
            try:
                from cleanup_va_windows import kill_va_windows
                kill_va_windows()
            except Exception as e:
                logger.debug(f"Cleanup error: {e}")
    else:
        print("❌ Failed to start JARVIS")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)