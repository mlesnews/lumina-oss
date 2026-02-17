#!/usr/bin/env python3
"""
Track Cursor Workflow - Record Exact Steps for Automation

Records every click, keyboard press, and action in Cursor
so we can automate it completely.
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import logging
logger = logging.getLogger("track_cursor_workflow")


try:
    import keyboard
    import mouse
    KEYBOARD_AVAILABLE = True
    MOUSE_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    MOUSE_AVAILABLE = False
    print("⚠️  Install: pip install keyboard mouse")

class CursorWorkflowTracker:
    """Track all user actions in Cursor"""

    def __init__(self, output_file: Path):
        self.output_file = output_file
        self.workflow = {
            "started": datetime.now().isoformat(),
            "application": "Cursor IDE",
            "goal": "Voice transcription automation",
            "steps": []
        }
        self.recording = False

    def start_recording(self):
        """Start recording workflow"""
        if not KEYBOARD_AVAILABLE or not MOUSE_AVAILABLE:
            print("❌ Required libraries not available")
            return False

        print("📹 Starting workflow recording...")
        print("   - All keyboard presses will be recorded")
        print("   - All mouse clicks will be recorded")
        print("   - Press ESC to stop recording")
        print()

        self.recording = True

        # Hook keyboard
        keyboard.on_press(self._on_key_press)
        keyboard.on_release(self._on_key_release)

        # Hook mouse
        mouse.on_click(self._on_mouse_click)

        # Wait for ESC
        keyboard.wait('esc')

        self.stop_recording()
        return True

    def _on_key_press(self, event):
        """Record keyboard press"""
        if not self.recording:
            return

        step = {
            "timestamp": datetime.now().isoformat(),
            "type": "keyboard_press",
            "key": event.name,
            "scan_code": event.scan_code
        }
        self.workflow["steps"].append(step)
        print(f"⌨️  Key: {event.name}")

    def _on_key_release(self, event):
        """Record keyboard release"""
        if not self.recording:
            return

        step = {
            "timestamp": datetime.now().isoformat(),
            "type": "keyboard_release",
            "key": event.name
        }
        self.workflow["steps"].append(step)

    def _on_mouse_click(self, event):
        """Record mouse click"""
        if not self.recording:
            return

        step = {
            "timestamp": datetime.now().isoformat(),
            "type": "mouse_click",
            "button": str(event.button),
            "position": {"x": event.x, "y": event.y}
        }
        self.workflow["steps"].append(step)
        print(f"🖱️  Click: {event.button} at ({event.x}, {event.y})")

    def stop_recording(self):
        try:
            """Stop recording and save"""
            self.recording = False
            self.workflow["ended"] = datetime.now().isoformat()
            self.workflow["total_steps"] = len(self.workflow["steps"])

            # Save workflow
            with open(self.output_file, 'w') as f:
                json.dump(self.workflow, f, indent=2)

            print()
            print(f"💾 Workflow saved: {self.output_file}")
            print(f"📊 Total steps recorded: {self.workflow['total_steps']}")


        except Exception as e:
            self.logger.error(f"Error in stop_recording: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent
        workflow_dir = project_root / "data" / "cursor_workflows"
        workflow_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = workflow_dir / f"cursor_workflow_{timestamp}.json"

        print("="*80)
        print("📹 Cursor Workflow Tracker")
        print("="*80)
        print()
        print("This will record ALL your actions in Cursor:")
        print("  - Every keyboard press")
        print("  - Every mouse click")
        print("  - Exact sequence of actions")
        print()
        print("Purpose: Automate voice transcription workflow")
        print()

        tracker = CursorWorkflowTracker(output_file)

        print("Press ENTER to start recording...")
        input()

        tracker.start_recording()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()