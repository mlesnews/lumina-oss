#!/usr/bin/env python3
"""
Launch Animated Virtual Assistants - JARVIS, Ultron, Ultimate Iron Man

Launches multiple animated desktop assistants that walk around the screen,
similar to ACE. Each assistant appears in its own window and can move around.

Tags: #ANIMATED #DESKTOP_ASSISTANTS #JARVIS #ULTRON #ULTIMATE_IRON_MAN @LUMINA
"""

import sys
import subprocess
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

logger = get_logger("LaunchAnimatedVAs")


def launch_jarvis_animated():
    """Launch JARVIS as high-quality animated desktop assistant"""
    # Check magic words first
    try:
        from iron_man_assistant_manager import IronManAssistantManager
        manager = IronManAssistantManager(project_root=project_root)
        can_activate, reason = manager.can_activate("jarvis", bypass_magic_words=False)
        if not can_activate:
            logger.warning(f"⚠️  Cannot launch JARVIS: {reason}")
            logger.warning("   Say 'Jarvis Iron Legion' to activate")
            return False
    except Exception as e:
        logger.debug(f"Could not check magic words: {e}")

    logger.info("🚀 Launching JARVIS animated assistant...")
    try:
        script_path = script_dir / "jarvis_desktop_assistant.py"
        if script_path.exists():
            result = subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            logger.info("✅ JARVIS launched")
            return True
        else:
            logger.error(f"❌ Script not found: {script_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error launching JARVIS: {e}")
        return False


def launch_ultron_animated():
    """Launch Ultron as high-quality animated desktop assistant"""
    logger.info("🚀 Launching Ultron animated assistant (HQ)...")
    try:
        # Note: Ultron is not an Iron Man persona, so we'll use a separate approach
        # For now, use ultimate persona as Ultron
        script_path = script_dir / "ultron_desktop_assistant.py"
        if script_path.exists():
            subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            logger.info("✅ Ultron launched")
            return True
        else:
            logger.error(f"❌ Script not found: {script_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error launching Ultron: {e}")
        return False


def launch_ultimate_iron_man_animated():
    """Launch Ultimate Iron Man as high-quality animated desktop assistant"""
    # Check magic words first
    try:
        from iron_man_assistant_manager import IronManAssistantManager
        manager = IronManAssistantManager(project_root=project_root)
        can_activate, reason = manager.can_activate("ultimate", bypass_magic_words=False)
        if not can_activate:
            logger.warning(f"⚠️  Cannot launch Ultimate Iron Man: {reason}")
            logger.warning("   Say 'Jarvis Iron Legion' to activate")
            return False
    except Exception as e:
        logger.debug(f"Could not check magic words: {e}")

    logger.info("🚀 Launching Ultimate Iron Man animated assistant (High Fidelity)...")
    try:
        script_path = script_dir / "ultimate_iron_man_desktop_assistant_hq.py"
        if script_path.exists():
            subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            logger.info("✅ Ultimate Iron Man launched (High Fidelity)")
            return True
        else:
            logger.error(f"❌ Script not found: {script_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error launching Ultimate Iron Man: {e}")
        return False


def launch_ace_animated():
    """Launch ACE (Anakin Combat Virtual Assistant) as animated desktop assistant"""
    logger.info("🚀 Launching ACE animated assistant...")
    try:
        script_path = script_dir / "anakin_combat_virtual_assistant.py"
        if script_path.exists():
            subprocess.Popen(
                [sys.executable, str(script_path)],
                cwd=str(project_root),
                creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
            )
            logger.info("✅ ACE launched")
            return True
        else:
            logger.error(f"❌ Script not found: {script_path}")
            return False
    except Exception as e:
        logger.error(f"❌ Error launching ACE: {e}")
        return False


def launch_all_animated_assistants():
    """Launch all animated virtual assistants"""
    print("=" * 80)
    print("🚀 LAUNCHING ANIMATED VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    results = {
        "JARVIS": False,
        "Ultron": False,
        "Ultimate Iron Man": False,
        "ACE": False
    }

    # Launch each assistant with a small delay to avoid conflicts
    print("Launching JARVIS...")
    results["JARVIS"] = launch_jarvis_animated()
    time.sleep(1)

    print("Launching Ultron...")
    results["Ultron"] = launch_ultron_animated()
    time.sleep(1)

    print("Launching Ultimate Iron Man...")
    results["Ultimate Iron Man"] = launch_ultimate_iron_man_animated()
    time.sleep(1)

    print("Launching ACE...")
    results["ACE"] = launch_ace_animated()
    time.sleep(1)

    print()
    print("=" * 80)
    print("✅ LAUNCH COMPLETE")
    print("=" * 80)
    print()

    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"{status} {name}: {'Launched' if success else 'Failed'}")

    print()
    print("All animated assistants should now be visible on your desktop!")
    print("They will appear as separate windows that can move around.")
    print()

    return results


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Launch Animated Virtual Assistants")
    parser.add_argument("--jarvis", action="store_true", help="Launch JARVIS only")
    parser.add_argument("--ultron", action="store_true", help="Launch Ultron only")
    parser.add_argument("--ultimate", action="store_true", help="Launch Ultimate Iron Man only")
    parser.add_argument("--ace", action="store_true", help="Launch ACE only")
    parser.add_argument("--all", action="store_true", help="Launch all assistants")

    args = parser.parse_args()

    if args.all:
        launch_all_animated_assistants()
    elif args.jarvis:
        launch_jarvis_animated()
    elif args.ultron:
        launch_ultron_animated()
    elif args.ultimate:
        launch_ultimate_iron_man_animated()
    elif args.ace:
        launch_ace_animated()
    else:
        # Default: launch all
        launch_all_animated_assistants()


if __name__ == "__main__":


    main()