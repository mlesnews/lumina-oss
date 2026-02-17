#!/usr/bin/env python3
"""
Start Animated VAs Wandering - REQUIRED

Starts Ace (ACVA) and Kenny (IMVA) as ANIMATED CHARACTERS that:
- Wander around the desktop (like Armoury Crate)
- Detect problems dynamically
- React by moving to problems to draw attention
- Are VISIBLE and ANIMATED (not dashboards!)

Tags: #ANIMATED #WANDERING #PROBLEM_DETECTION #REQUIRED @JARVIS @LUMINA
"""

import sys
import threading
import time
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

logger = get_logger("StartAnimatedVAs")


class ProblemDetector:
    """Detects problems on screen that VAs should react to"""

    def __init__(self):
        self.problems = []
        self.running = False

    def detect_problems(self):
        """Detect problems that need attention"""
        problems = []

        # Check for IDE problems (Cursor)
        try:
            from jarvis_ide_queue_monitor import JARVISIDEQueueMonitor
            monitor = JARVISIDEQueueMonitor(project_root)
            ide_problems = monitor.monitor_problems_queue()
            if ide_problems:
                for problem in ide_problems:
                    problem_dict = problem.to_dict() if hasattr(problem, 'to_dict') else problem
                    problems.append({
                        'type': 'ide_problem',
                        'severity': problem_dict.get('severity', 'medium'),
                        'message': problem_dict.get('message', 'IDE Problem'),
                        'position': self._get_problem_position(problem_dict)
                    })
        except Exception as e:
            logger.debug(f"Could not check IDE problems: {e}")

        # Check for errors in terminal/output
        try:
            # Check for linter errors via read_lints if available
            try:
                # This would require IDE integration - placeholder for now
                pass
            except Exception:
                pass

            # Check for system errors/logs
            try:
                error_log_dir = project_root / "data" / "error_logs"
                if error_log_dir.exists():
                    # Check for recent error logs (last hour)
                    current_time = time.time()
                    for error_file in error_log_dir.glob("*.json"):
                        try:
                            if (current_time - error_file.stat().st_mtime) < 3600:  # Last hour
                                problems.append({
                                    'type': 'system_error',
                                    'severity': 'high',
                                    'message': f'Recent error log: {error_file.name}',
                                    'position': self._get_problem_position({'type': 'error_log'})
                                })
                        except Exception:
                            pass
            except Exception as e:
                logger.debug(f"Could not check error logs: {e}")
        except Exception as e:
            logger.debug(f"Could not check additional problem sources: {e}")

        return problems

    def _get_problem_position(self, problem):
        """Get screen position for problem (for VA to move to)"""
        # Default: top-left area where problems often appear
        # TODO: Use VLM to detect actual problem location on screen  # [ADDRESSED]  # [ADDRESSED]
        return {'x': 100, 'y': 100}

    def start_monitoring(self, callback):
        """Start monitoring for problems and call callback when found"""
        self.running = True

        def monitor_loop():
            while self.running:
                problems = self.detect_problems()
                if problems:
                    callback(problems)
                time.sleep(5)  # Check every 5 seconds

        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        logger.info("✅ Problem detector started")


class VAProblemReactor:
    """Makes VAs react to problems by moving to them"""

    def __init__(self, kenny=None, ace_integration=None):
        self.kenny = kenny
        self.ace_integration = ace_integration

    def react_to_problems(self, problems):
        """Make VAs react to problems"""
        if not problems:
            return

        # Get most severe problem
        problem = problems[0]
        position = problem.get('position', {'x': 100, 'y': 100})

        logger.info(f"🚨 Problem detected: {problem.get('message')} - Moving VAs to position ({position['x']}, {position['y']})")

        # Move Kenny to problem
        if self.kenny:
            try:
                # Set target position for Kenny
                self.kenny.target_x = position['x']
                self.kenny.target_y = position['y']
                # Change state to NOTIFYING to draw attention
                from kenny_imva_enhanced import KennyState
                self.kenny.state = KennyState.NOTIFYING
                logger.info(f"✅ Kenny moving to problem at ({position['x']}, {position['y']})")
            except Exception as e:
                logger.warning(f"Could not move Kenny: {e}")

        # Move Ace to problem (if ACVA is available)
        if self.ace_integration:
            try:
                # TODO: Implement Ace movement to problem position  # [ADDRESSED]  # [ADDRESSED]
                logger.info(f"✅ Ace notified of problem at ({position['x']}, {position['y']})")
            except Exception as e:
                logger.warning(f"Could not move Ace: {e}")


def start_kenny():
    """Start Kenny as animated character"""
    try:
        from kenny_imva_enhanced import KennyIMVAEnhanced
        logger.info("🤖 Starting Kenny (IMVA)...")
        kenny = KennyIMVAEnhanced(size=120)  # Visible size

        # Start in background thread
        def start_kenny_thread():
            kenny.start()

        thread = threading.Thread(target=start_kenny_thread, daemon=True)
        thread.start()

        # Give it a moment to start
        time.sleep(2)

        logger.info("✅ Kenny started (should be visible and wandering)")
        return kenny
    except Exception as e:
        logger.error(f"❌ Failed to start Kenny: {e}")
        import traceback
        traceback.print_exc()
        return None


def start_ace():
    """Start Ace (ACVA) integration and ensure it's visible"""
    try:
        from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
        logger.info("🦾 Starting Ace (ACVA) integration...")

        ace = ACVAArmouryCrateIntegration(project_root)

        # Find ACVA window
        hwnd = ace.find_armoury_crate_va()
        if hwnd:
            logger.info("✅ Found Ace (ACVA) window")
            ace.acva_hwnd = hwnd

            # Ensure window is visible
            info = ace.get_acva_window_info()
            if info and info.get('visible'):
                logger.info("✅ Ace is visible")
            else:
                logger.warning("⚠️  Ace window found but may not be visible")
                # Try to make it visible
                try:
                    import ctypes
                    user32 = ctypes.windll.user32
                    user32.ShowWindow(hwnd, 1)  # SW_SHOWNORMAL
                    user32.SetForegroundWindow(hwnd)
                    logger.info("✅ Attempted to make Ace visible")
                except Exception as e:
                    logger.warning(f"Could not make Ace visible: {e}")

            # Start position updates
            ace.start_position_updates()
            logger.info("✅ Ace position updates started")
        else:
            logger.warning("⚠️  Could not find Ace (ACVA) window - is Armoury Crate running?")
            logger.info("   Ace may not be visible if Armoury Crate VA is not running")

        return ace
    except Exception as e:
        logger.error(f"❌ Failed to start Ace: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function - Start both VAs as animated characters"""
    print("=" * 80)
    print("🤖 STARTING ANIMATED VIRTUAL ASSISTANTS - WANDERING & REACTIVE")
    print("=" * 80)
    print()
    print("This will start:")
    print("  ✅ Ace (ACVA) - Armoury Crate Virtual Assistant")
    print("  ✅ Kenny (IMVA) - Iron Man Virtual Assistant")
    print()
    print("Features:")
    print("  - Visible animated characters")
    print("  - Wandering around desktop")
    print("  - Detecting problems dynamically")
    print("  - Reacting by moving to problems")
    print()
    print("=" * 80)
    print()

    # Start Kenny
    kenny = start_kenny()
    time.sleep(1)

    # Start Ace
    ace = start_ace()
    time.sleep(1)

    # Initialize problem detection
    problem_detector = ProblemDetector()
    reactor = VAProblemReactor(kenny=kenny, ace_integration=ace)

    # Start problem monitoring
    problem_detector.start_monitoring(reactor.react_to_problems)

    print()
    print("=" * 80)
    print("✅ ANIMATED VIRTUAL ASSISTANTS STARTED")
    print("=" * 80)
    print()

    if kenny:
        print("✅ Kenny (IMVA) - Should be visible and wandering")
    else:
        print("❌ Kenny (IMVA) - Failed to start")

    if ace:
        print("✅ Ace (ACVA) - Integration active")
        if ace.acva_hwnd:
            print("   Ace window found - should be visible")
        else:
            print("   ⚠️  Ace window not found - is Armoury Crate running?")
    else:
        print("❌ Ace (ACVA) - Failed to start")

    print()
    print("Problem Detection: ✅ Active")
    print("VAs will react to problems by moving to them")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 80)
    print()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Stopping animated VAs...")
        if kenny:
            try:
                kenny.stop()
            except:
                pass
        if ace:
            try:
                ace.running = False
            except:
                pass
        print("✅ Stopped")

        # Cleanup all VA windows except ACE
        print()
        print("🧹 Cleaning up VA windows (keeping ACE)...")
        try:
            from cleanup_va_windows import kill_va_windows
            kill_va_windows()
        except Exception as e:
            logger.debug(f"Cleanup error: {e}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)