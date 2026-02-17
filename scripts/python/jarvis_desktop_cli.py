#!/usr/bin/env python3
"""
JARVIS Desktop Full Control CLI

Command-line interface for JARVIS control over the entire desktop.
Provides easy access to all desktop control features.

Tags: #JARVIS #DESKTOP #CLI #FULL_CONTROL @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Optional

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

logger = get_logger("JARVISDesktopCLI")

try:
    from jarvis_desktop_full_control import JARVISDesktopFullControl
except ImportError:
    logger.error("❌ JARVIS Desktop Full Control not available")
    sys.exit(1)


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Desktop Full Control CLI - Control entire desktop/PC",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List all windows
  jarvis-desktop windows

  # Control window
  jarvis-desktop window "Notepad" focus
  jarvis-desktop window "Notepad" minimize

  # Launch application
  jarvis-desktop launch notepad.exe

  # Simulate keyboard
  jarvis-desktop keyboard "Hello World"
  jarvis-desktop keyboard "ctrl+c" --modifiers ctrl

  # Simulate mouse
  jarvis-desktop mouse click --x 100 --y 200

  # Take screenshot
  jarvis-desktop screenshot screenshot.png

  # Get system info
  jarvis-desktop system-info

  # List processes
  jarvis-desktop processes
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Windows
    windows_parser = subparsers.add_parser("windows", help="List all windows")

    # Window control
    window_parser = subparsers.add_parser("window", help="Control window")
    window_parser.add_argument("title", help="Window title")
    window_parser.add_argument("action", choices=["focus", "minimize", "maximize", "restore", "close", "move", "resize"],
                               help="Action to perform")
    window_parser.add_argument("--x", type=int, help="X coordinate (for move/resize)")
    window_parser.add_argument("--y", type=int, help="Y coordinate (for move/resize)")
    window_parser.add_argument("--width", type=int, help="Width (for resize)")
    window_parser.add_argument("--height", type=int, help="Height (for resize)")

    # Launch application
    launch_parser = subparsers.add_parser("launch", help="Launch application")
    launch_parser.add_argument("app", help="Application name/path")
    launch_parser.add_argument("--args", nargs="*", help="Application arguments")

    # Keyboard
    keyboard_parser = subparsers.add_parser("keyboard", help="Simulate keyboard")
    keyboard_parser.add_argument("keys", help="Keys to type")
    keyboard_parser.add_argument("--modifiers", nargs="+", help="Modifiers (ctrl, alt, shift)")

    # Mouse
    mouse_parser = subparsers.add_parser("mouse", help="Simulate mouse")
    mouse_parser.add_argument("action", choices=["click", "move", "drag", "scroll"], help="Mouse action")
    mouse_parser.add_argument("--x", type=int, help="X coordinate")
    mouse_parser.add_argument("--y", type=int, help="Y coordinate")
    mouse_parser.add_argument("--button", default="left", choices=["left", "right", "middle"], help="Mouse button")

    # Screenshot
    screenshot_parser = subparsers.add_parser("screenshot", help="Take screenshot")
    screenshot_parser.add_argument("path", help="Path to save screenshot")
    screenshot_parser.add_argument("--region", nargs=4, type=int, metavar=("LEFT", "TOP", "WIDTH", "HEIGHT"),
                                   help="Screen region to capture")

    # System info
    system_info_parser = subparsers.add_parser("system-info", help="Get system information")

    # Processes
    processes_parser = subparsers.add_parser("processes", help="List running processes")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    control = JARVISDesktopFullControl()

    try:
        if args.command == "windows":
            windows = control.get_window_list()
            print(json.dumps(windows, indent=2))
            return 0

        elif args.command == "window":
            params = {}
            if args.x is not None:
                params["x"] = args.x
            if args.y is not None:
                params["y"] = args.y
            if args.width is not None:
                params["width"] = args.width
            if args.height is not None:
                params["height"] = args.height

            success = control.control_window(args.title, args.action, **params)
            if success:
                print(f"✅ Window '{args.title}' {args.action} successful")
                return 0
            else:
                print(f"❌ Failed to {args.action} window '{args.title}'")
                return 1

        elif args.command == "launch":
            success = control.launch_application(args.app, args.args)
            if success:
                print(f"✅ Launched {args.app}")
                return 0
            else:
                print(f"❌ Failed to launch {args.app}")
                return 1

        elif args.command == "keyboard":
            success = control.simulate_keyboard(args.keys, args.modifiers)
            if success:
                print(f"✅ Keyboard input sent: {args.keys}")
                return 0
            else:
                print(f"❌ Failed to simulate keyboard")
                return 1

        elif args.command == "mouse":
            success = control.simulate_mouse(args.action, args.x, args.y, args.button)
            if success:
                print(f"✅ Mouse {args.action} successful")
                return 0
            else:
                print(f"❌ Failed to simulate mouse")
                return 1

        elif args.command == "screenshot":
            region = None
            if args.region:
                region = {
                    "left": args.region[0],
                    "top": args.region[1],
                    "width": args.region[2],
                    "height": args.region[3]
                }

            success = control.capture_screen(args.path, region)
            if success:
                print(f"✅ Screenshot saved to {args.path}")
                return 0
            else:
                print(f"❌ Failed to capture screenshot")
                return 1

        elif args.command == "system-info":
            info = control.get_system_info()
            print(json.dumps(info, indent=2))
            return 0

        elif args.command == "processes":
            processes = control.get_running_processes()
            print(json.dumps(processes, indent=2))
            return 0

        else:
            parser.print_help()
            return 1

    except Exception as e:
        logger.error(f"Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())