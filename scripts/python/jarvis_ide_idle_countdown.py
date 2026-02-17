#!/usr/bin/env python3
"""
JARVIS IDE Idle Countdown Timer

Displays idle countdown timer in IDE footer showing time remaining until restrictions.
Updates in real-time with proper scrolling and word-wrapping.

@JARVIS #IDLE_COUNTDOWN #IDE_FOOTER #STATUS_BAR #REALTIME
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IDEIdleCountdown")

try:
    from operator_idleness_restriction import get_operator_idleness_restriction
    IDLENESS_AVAILABLE = True
except ImportError:
    IDLENESS_AVAILABLE = False
    get_operator_idleness_restriction = None
    logger.warning("⚠️  Operator idleness restriction not available")


class JARVISIDEIdleCountdown:
    """
    JARVIS IDE Idle Countdown Timer

    Displays countdown timer in IDE footer showing:
    - Time remaining until restrictions (10-minute breather)
    - Current idle duration
    - Status (ACTIVE, IDLE, RESTRICTED)
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "ide_countdown"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.status_file = self.data_dir / "countdown_status.json"

        # Initialize idleness restriction
        self.idleness_restriction = None
        if IDLENESS_AVAILABLE:
            try:
                self.idleness_restriction = get_operator_idleness_restriction(project_root)
                self.logger.info("✅ Idleness restriction initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Idleness restriction initialization failed: {e}")

        # Update thread
        self.update_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.update_interval = 1.0  # Update every second

        # Start updating
        self.start_updates()

        self.logger.info("✅ JARVIS IDE Idle Countdown initialized")

    def get_countdown_status(self) -> Dict[str, Any]:
        """Get current countdown status"""
        if not self.idleness_restriction:
            return {
                "status": "unavailable",
                "message": "Idleness restriction not available",
                "countdown_seconds": None,
                "countdown_display": "N/A"
            }

        # Get current state
        state = self.idleness_restriction.check_idleness()
        idle_duration = self.idleness_restriction._get_idle_duration()

        # Calculate countdown
        timeout_seconds = self.idleness_restriction.restriction.idle_timeout_seconds
        if idle_duration != float('inf'):
            countdown_seconds = max(0, timeout_seconds - idle_duration)
        else:
            countdown_seconds = timeout_seconds

        # Format countdown display
        if countdown_seconds > 0:
            minutes = int(countdown_seconds // 60)
            seconds = int(countdown_seconds % 60)
            countdown_display = f"{minutes:02d}:{seconds:02d}"
        else:
            countdown_seconds = 0
            countdown_display = "00:00"

        # Format idle duration display
        if idle_duration != float('inf'):
            idle_minutes = int(idle_duration // 60)
            idle_seconds = int(idle_duration % 60)
            idle_display = f"{idle_minutes:02d}:{idle_seconds:02d}"
        else:
            idle_display = "00:00"

        # Status message
        if state.value == "active":
            status_message = f"🟢 ACTIVE - Breather: {countdown_display}"
        elif state.value == "idle":
            status_message = f"🟡 IDLE - Breather: {countdown_display}"
        else:  # restricted
            status_message = f"🔴 RESTRICTED - Idle: {idle_display}"

        return {
            "status": state.value,
            "status_message": status_message,
            "countdown_seconds": countdown_seconds,
            "countdown_display": countdown_display,
            "idle_duration_seconds": idle_duration if idle_duration != float('inf') else None,
            "idle_display": idle_display,
            "timeout_seconds": timeout_seconds,
            "timeout_minutes": timeout_seconds / 60,
            "timestamp": datetime.now().isoformat()
        }

    def update_status_file(self):
        """Update status file for IDE to read"""
        try:
            status = self.get_countdown_status()

            # Add formatted display strings for IDE footer
            status["footer_display"] = self._format_footer_display(status)
            status["footer_display_short"] = self._format_footer_display_short(status)
            status["footer_display_full"] = self._format_footer_display_full(status)

            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)

            self.logger.debug(f"✅ Status updated: {status['status_message']}")
        except Exception as e:
            self.logger.error(f"❌ Failed to update status: {e}")

    def _format_footer_display(self, status: Dict[str, Any]) -> str:
        """Format footer display (compact, scrollable, word-wrapping)"""
        state = status['status']
        countdown = status['countdown_display']

        if state == "active":
            return f"🟢 @OP ACTIVE | Breather: {countdown}"
        elif state == "idle":
            return f"🟡 @OP IDLE | Breather: {countdown}"
        else:  # restricted
            idle = status['idle_display']
            return f"🔴 @OP RESTRICTED | Idle: {idle}"

    def _format_footer_display_short(self, status: Dict[str, Any]) -> str:
        """Format short footer display (minimal)"""
        state = status['status']
        countdown = status['countdown_display']

        if state == "active":
            return f"🟢 {countdown}"
        elif state == "idle":
            return f"🟡 {countdown}"
        else:  # restricted
            return f"🔴 RESTRICTED"

    def _format_footer_display_full(self, status: Dict[str, Any]) -> str:
        """Format full footer display (detailed, word-wrapping)"""
        state = status['status']
        countdown = status['countdown_display']
        timeout_min = status['timeout_minutes']

        if state == "active":
            return f"🟢 @OP ACTIVE | Breather Remaining: {countdown} (of {timeout_min:.0f}min) | Restrictions: INACTIVE"
        elif state == "idle":
            return f"🟡 @OP IDLE | Breather Remaining: {countdown} (of {timeout_min:.0f}min) | Restrictions: PENDING"
        else:  # restricted
            idle = status['idle_display']
            idle_min = status['idle_duration_seconds'] / 60 if status['idle_duration_seconds'] else 0
            return f"🔴 @OP RESTRICTED | Idle: {idle} ({idle_min:.1f}min) | Restrictions: ACTIVE | Actions: BLOCKED"

    def start_updates(self):
        """Start background update thread"""
        if self.update_thread and self.update_thread.is_alive():
            return

        self.stop_event.clear()
        self.update_thread = threading.Thread(target=self._update_loop, daemon=True)
        self.update_thread.start()
        self.logger.info("✅ Countdown update thread started")

    def stop_updates(self):
        """Stop background update thread"""
        self.stop_event.set()
        if self.update_thread:
            self.update_thread.join(timeout=2.0)
        self.logger.info("✅ Countdown update thread stopped")

    def _update_loop(self):
        """Background update loop"""
        while not self.stop_event.is_set():
            try:
                self.update_status_file()
                time.sleep(self.update_interval)
            except Exception as e:
                self.logger.error(f"Update loop error: {e}")
                time.sleep(self.update_interval)

    def get_footer_html(self) -> str:
        """Generate HTML for IDE footer (if supported) with proper scrolling and word-wrapping"""
        status = self.get_countdown_status()
        footer_display = status['footer_display']

        # HTML with proper word-wrapping and scrolling
        # Supports both horizontal scrolling and word-wrapping
        html = f"""
        <div style="
            display: inline-block;
            padding: 2px 8px;
            font-family: 'Segoe UI', monospace;
            font-size: 11px;
            white-space: normal;
            overflow-x: auto;
            overflow-y: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
            hyphens: auto;
            line-height: 1.4;
        ">
            {footer_display}
        </div>
        """
        return html

    def get_footer_html_scrolling(self) -> str:
        """Generate HTML for IDE footer with horizontal scrolling (no word-wrap)"""
        status = self.get_countdown_status()
        footer_display = status['footer_display']

        # HTML with horizontal scrolling only
        html = f"""
        <div style="
            display: inline-block;
            padding: 2px 8px;
            font-family: 'Segoe UI', monospace;
            font-size: 11px;
            white-space: nowrap;
            overflow-x: auto;
            overflow-y: hidden;
            text-overflow: ellipsis;
            max-width: 100%;
            scrollbar-width: thin;
        ">
            {footer_display}
        </div>
        """
        return html

    def get_footer_html_wrapping(self) -> str:
        """Generate HTML for IDE footer with word-wrapping (no scrolling)"""
        status = self.get_countdown_status()
        footer_display = status['footer_display']

        # HTML with word-wrapping only
        html = f"""
        <div style="
            display: inline-block;
            padding: 2px 8px;
            font-family: 'Segoe UI', monospace;
            font-size: 11px;
            white-space: normal;
            overflow: hidden;
            max-width: 100%;
            word-wrap: break-word;
            word-break: break-word;
            overflow-wrap: break-word;
            line-height: 1.4;
        ">
            {footer_display}
        </div>
        """
        return html

    def get_footer_text(self) -> str:
        """Get plain text for IDE footer"""
        status = self.get_countdown_status()
        return self._format_footer_display(status)

    def get_footer_text_short(self) -> str:
        """Get short text for IDE footer"""
        status = self.get_countdown_status()
        return self._format_footer_display_short(status)

    def get_footer_text_full(self) -> str:
        """Get full text for IDE footer (word-wrapping)"""
        status = self.get_countdown_status()
        return self._format_footer_display_full(status)


# Global instance
_global_countdown: Optional[JARVISIDEIdleCountdown] = None


def get_ide_countdown(project_root: Optional[Path] = None) -> JARVISIDEIdleCountdown:
    try:
        """Get or create global IDE countdown instance"""
        global _global_countdown

        if _global_countdown is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_countdown = JARVISIDEIdleCountdown(project_root)

        return _global_countdown


    except Exception as e:
        logger.error(f"Error in get_ide_countdown: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS IDE Idle Countdown Timer")
    parser.add_argument("--status", action="store_true", help="Show current status")
    parser.add_argument("--footer", action="store_true", help="Get footer text")
    parser.add_argument("--footer-short", action="store_true", help="Get short footer text")
    parser.add_argument("--footer-full", action="store_true", help="Get full footer text (word-wrapping)")
    parser.add_argument("--html", action="store_true", help="Get HTML footer")
    parser.add_argument("--watch", action="store_true", help="Watch countdown in real-time")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    countdown = JARVISIDEIdleCountdown(project_root)

    if args.status:
        status = countdown.get_countdown_status()
        print("\n" + "="*80)
        print("IDE IDLE COUNTDOWN STATUS")
        print("="*80)
        print(f"Status: {status['status']}")
        print(f"Status Message: {status['status_message']}")
        print(f"Countdown: {status['countdown_display']} ({status['countdown_seconds']}s)")
        if status['idle_duration_seconds']:
            print(f"Idle Duration: {status['idle_display']} ({status['idle_duration_seconds']:.0f}s)")
        print(f"Timeout: {status['timeout_seconds']}s ({status['timeout_minutes']:.1f} minutes)")
        print(f"Timestamp: {status['timestamp']}")
        print("="*80)

    if args.footer:
        print(countdown.get_footer_text())

    if args.footer_short:
        print(countdown.get_footer_text_short())

    if args.footer_full:
        print(countdown.get_footer_text_full())

    if args.html:
        print(countdown.get_footer_html())

    if args.watch:
        print("\n" + "="*80)
        print("WATCHING IDLE COUNTDOWN (Ctrl+C to stop)")
        print("="*80)
        try:
            while True:
                status = countdown.get_countdown_status()
                footer = countdown.get_footer_text()
                print(f"\r{footer}", end="", flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n✅ Stopped watching")

    if not any([args.status, args.footer, args.footer_short, args.footer_full, args.html, args.watch]):
        parser.print_help()


if __name__ == "__main__":


    main()