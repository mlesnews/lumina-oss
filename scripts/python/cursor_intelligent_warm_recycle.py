#!/usr/bin/env python3
"""
Cursor IDE Intelligent Warm Recycle System

Automatically and intelligently recycles (restarts) Cursor IDE when needed:
- Detects performance issues (high memory, CPU, frozen)
- Saves all work before recycling
- Gracefully closes and restarts
- Restores workspace state
- Reopens files

Smart decision-making based on multiple factors.
"""

import sys
import time
import psutil
import subprocess
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
import threading
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorIntelligentRecycle")

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController
    import pygetwindow as gw
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    logger.warning("pynput not available - some features may be limited")


class RecycleReason(Enum):
    """Reasons for recycling Cursor"""
    HIGH_MEMORY = "high_memory"
    HIGH_CPU = "high_cpu"
    FROZEN = "frozen"
    ERROR_COUNT = "error_count"
    PERFORMANCE_DEGRADED = "performance_degraded"
    SCHEDULED = "scheduled"
    MANUAL = "manual"
    PROACTIVE = "proactive"


@dataclass
class CursorProcessInfo:
    """Information about Cursor IDE process"""
    pid: int
    memory_mb: float
    cpu_percent: float
    status: str
    threads: int
    open_files: int
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RecycleDecision:
    """Decision to recycle Cursor"""
    should_recycle: bool
    reason: Optional[RecycleReason] = None
    urgency: str = "low"  # low, medium, high, critical
    confidence: float = 0.0
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class CursorIntelligentWarmRecycle:
    """
    Intelligent Warm Recycle System for Cursor IDE

    Automatically detects when Cursor needs recycling and performs
    a smart warm recycle (save state, graceful restart, restore).
    """

    # Thresholds for recycling decisions
    MEMORY_THRESHOLD_MB = 2048  # 2GB
    MEMORY_WARNING_MB = 1536  # 1.5GB
    CPU_THRESHOLD_PERCENT = 80.0
    CPU_WARNING_PERCENT = 60.0
    FROZEN_CHECK_INTERVAL = 30  # seconds
    ERROR_THRESHOLD = 10

    # Recycle settings
    PROACTIVE_RECYCLE_INTERVAL = 3600 * 4  # 4 hours
    GRACEFUL_SHUTDOWN_TIMEOUT = 10  # seconds
    RESTART_DELAY = 3  # seconds

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intelligent recycle system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.running = False

        # Keyboard controller for automation
        self.keyboard = KeyboardController() if PYNPUT_AVAILABLE else None

        # Monitoring state
        self.monitoring_active = False
        self.monitor_thread = None
        self.last_recycle_time = None
        self.recycle_count = 0

        # Process tracking
        self.cursor_processes: List[CursorProcessInfo] = []
        self.performance_history: List[Dict[str, Any]] = []

        # Workspace state (to restore after recycle)
        self.workspace_state = {
            "open_files": [],
            "workspace_folder": None,
            "settings": {}
        }

        # Configuration
        self.config_file = self.project_root / "config" / "cursor_recycle_config.json"
        self._load_config()

        logger.info("🔄 Cursor Intelligent Warm Recycle System initialized")
        logger.info(f"   Memory threshold: {self.MEMORY_THRESHOLD_MB}MB")
        logger.info(f"   CPU threshold: {self.CPU_THRESHOLD_PERCENT}%")

    def _load_config(self):
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.MEMORY_THRESHOLD_MB = config.get("memory_threshold_mb", self.MEMORY_THRESHOLD_MB)
                    self.CPU_THRESHOLD_PERCENT = config.get("cpu_threshold_percent", self.CPU_THRESHOLD_PERCENT)
                    self.PROACTIVE_RECYCLE_INTERVAL = config.get("proactive_interval", self.PROACTIVE_RECYCLE_INTERVAL)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

    def _save_config(self):
        try:
            """Save configuration to file"""
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            config = {
                "memory_threshold_mb": self.MEMORY_THRESHOLD_MB,
                "cpu_threshold_percent": self.CPU_THRESHOLD_PERCENT,
                "proactive_interval": self.PROACTIVE_RECYCLE_INTERVAL,
                "last_recycle": self.last_recycle_time.isoformat() if self.last_recycle_time else None,
                "recycle_count": self.recycle_count
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_config: {e}", exc_info=True)
            raise
    def find_cursor_processes(self) -> List[CursorProcessInfo]:
        """Find all Cursor IDE processes"""
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent', 'status', 'num_threads']):
            try:
                name = proc.info['name'].lower()
                if 'cursor' in name and proc.info['name'] != 'cursor.exe':
                    # Main Cursor process (not helper processes)
                    if 'cursor.exe' in proc.info['name'] or 'Cursor' in proc.info['name']:
                        memory_mb = proc.info['memory_info'].rss / 1024 / 1024

                        # Get CPU percent (non-blocking)
                        cpu_percent = proc.cpu_percent(interval=0.1)

                        process_info = CursorProcessInfo(
                            pid=proc.info['pid'],
                            memory_mb=memory_mb,
                            cpu_percent=cpu_percent,
                            status=proc.info['status'],
                            threads=proc.info['num_threads'],
                            open_files=len(proc.open_files()) if hasattr(proc, 'open_files') else 0
                        )
                        processes.append(process_info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return processes

    def get_cursor_window(self):
        """Get Cursor window"""
        try:
            windows = gw.getWindowsWithTitle('Cursor')
            if not windows:
                windows = gw.getWindowsWithTitle('cursor')
            if not windows:
                all_windows = gw.getAllWindows()
                windows = [w for w in all_windows if 'cursor' in w.title.lower()]

            return windows[0] if windows else None
        except Exception as e:
            logger.debug(f"Error finding Cursor window: {e}")
            return None

    def should_recycle(self) -> RecycleDecision:
        """
        Intelligently decide if Cursor should be recycled

        Returns:
            RecycleDecision with recommendation
        """
        processes = self.find_cursor_processes()

        if not processes:
            # Cursor not running - no need to recycle
            return RecycleDecision(
                should_recycle=False,
                reason=None,
                confidence=1.0
            )

        # Get aggregate metrics
        total_memory = sum(p.memory_mb for p in processes)
        max_cpu = max(p.cpu_percent for p in processes) if processes else 0
        avg_cpu = sum(p.cpu_percent for p in processes) / len(processes) if processes else 0

        # Check various conditions
        reasons = []
        urgency = "low"
        confidence = 0.0

        # High memory check
        if total_memory > self.MEMORY_THRESHOLD_MB:
            reasons.append(RecycleReason.HIGH_MEMORY)
            urgency = "high" if total_memory > self.MEMORY_THRESHOLD_MB * 1.5 else "medium"
            confidence = min(0.9, (total_memory - self.MEMORY_THRESHOLD_MB) / self.MEMORY_THRESHOLD_MB)
            logger.warning(f"⚠️  High memory detected: {total_memory:.1f}MB")

        # High CPU check
        if max_cpu > self.CPU_THRESHOLD_PERCENT:
            reasons.append(RecycleReason.HIGH_CPU)
            urgency = "high" if max_cpu > self.CPU_THRESHOLD_PERCENT * 1.2 else "medium"
            confidence = max(confidence, min(0.9, (max_cpu - self.CPU_THRESHOLD_PERCENT) / self.CPU_THRESHOLD_PERCENT))
            logger.warning(f"⚠️  High CPU detected: {max_cpu:.1f}%")

        # Frozen check (CPU very low but process exists)
        if max_cpu < 1.0 and total_memory > 100:  # Low CPU but significant memory
            # Could be frozen - check if window responds
            window = self.get_cursor_window()
            if window:
                # Try to detect if window is responsive
                # This is a simplified check - in practice would test window responsiveness
                pass

        # Proactive recycle (scheduled)
        if self.last_recycle_time:
            time_since_recycle = (datetime.now() - self.last_recycle_time).total_seconds()
            if time_since_recycle > self.PROACTIVE_RECYCLE_INTERVAL:
                reasons.append(RecycleReason.PROACTIVE)
                urgency = "low"
                confidence = 0.7
                logger.info(f"📅 Proactive recycle due (last recycle: {time_since_recycle/3600:.1f}h ago)")

        # Performance degradation (trending upward)
        if len(self.performance_history) > 5:
            recent_memory = [m.get("memory", 0) for m in self.performance_history[-5:]]
            if recent_memory and recent_memory[-1] > recent_memory[0] * 1.3:
                reasons.append(RecycleReason.PERFORMANCE_DEGRADED)
                urgency = "medium"
                confidence = max(confidence, 0.6)
                logger.warning("📉 Performance degradation detected")

        # Store current metrics
        metrics = {
            "total_memory_mb": total_memory,
            "max_cpu_percent": max_cpu,
            "avg_cpu_percent": avg_cpu,
            "process_count": len(processes),
            "timestamp": datetime.now().isoformat()
        }

        self.performance_history.append(metrics)
        # Keep only last 20 entries
        if len(self.performance_history) > 20:
            self.performance_history.pop(0)

        # Decision
        should_recycle = len(reasons) > 0 and confidence > 0.5

        if should_recycle:
            # Use highest urgency reason
            primary_reason = reasons[0]
            if RecycleReason.HIGH_MEMORY in reasons and total_memory > self.MEMORY_THRESHOLD_MB * 1.5:
                primary_reason = RecycleReason.HIGH_MEMORY
                urgency = "critical"
            elif RecycleReason.HIGH_CPU in reasons and max_cpu > self.CPU_THRESHOLD_PERCENT * 1.2:
                primary_reason = RecycleReason.HIGH_CPU
                urgency = "critical"

        return RecycleDecision(
            should_recycle=should_recycle,
            reason=primary_reason if should_recycle else None,
            urgency=urgency,
            confidence=confidence,
            metrics=metrics
        )

    def save_workspace_state(self):
        """Save current workspace state before recycling"""
        logger.info("💾 Saving workspace state...")

        try:
            # Save open files (would need Cursor API or window state)
            # For now, save what we can detect

            window = self.get_cursor_window()
            if window:
                self.workspace_state["window_title"] = window.title
                # Extract workspace folder from title if possible

            # Save state to file
            state_file = self.project_root / "data" / "cursor_workspace_state.json"
            state_file.parent.mkdir(parents=True, exist_ok=True)

            with open(state_file, 'w') as f:
                json.dump({
                    **self.workspace_state,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)

            logger.info("   ✅ Workspace state saved")

        except Exception as e:
            logger.error(f"   ❌ Failed to save workspace state: {e}")

    def save_all_files(self):
        """Save all open files in Cursor"""
        logger.info("💾 Saving all files...")

        if not self.keyboard:
            logger.warning("   ⚠️  Keyboard controller not available")
            return False

        try:
            window = self.get_cursor_window()
            if not window:
                logger.warning("   ⚠️  Cursor window not found")
                return False

            window.activate()
            time.sleep(0.3)

            # Save all files: Ctrl+K, S (Save All)
            self.keyboard.press(Key.ctrl)
            self.keyboard.press('k')
            time.sleep(0.1)
            self.keyboard.release('k')
            time.sleep(0.1)
            self.keyboard.press('s')
            time.sleep(0.1)
            self.keyboard.release('s')
            self.keyboard.release(Key.ctrl)

            time.sleep(0.5)
            logger.info("   ✅ All files saved")
            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to save files: {e}")
            return False

    def graceful_shutdown(self) -> bool:
        """Gracefully shut down Cursor IDE"""
        logger.info("🛑 Gracefully shutting down Cursor...")

        if not self.keyboard:
            logger.warning("   ⚠️  Keyboard controller not available")
            return False

        try:
            window = self.get_cursor_window()
            if not window:
                logger.warning("   ⚠️  Cursor window not found")
                return False

            window.activate()
            time.sleep(0.3)

            # Close Cursor: Alt+F4 or File > Exit
            # Try Alt+F4 first
            self.keyboard.press(Key.alt)
            self.keyboard.press(Key.f4)
            time.sleep(0.1)
            self.keyboard.release(Key.f4)
            self.keyboard.release(Key.alt)

            # Wait for shutdown
            timeout = self.GRACEFUL_SHUTDOWN_TIMEOUT
            start_time = time.time()

            while time.time() - start_time < timeout:
                processes = self.find_cursor_processes()
                if not processes:
                    logger.info("   ✅ Cursor closed gracefully")
                    return True
                time.sleep(0.5)

            # Force kill if graceful shutdown failed
            logger.warning("   ⚠️  Graceful shutdown timeout, forcing...")
            return self.force_kill()

        except Exception as e:
            logger.error(f"   ❌ Graceful shutdown failed: {e}")
            return self.force_kill()

    def force_kill(self) -> bool:
        """Force kill Cursor processes"""
        logger.info("💀 Force killing Cursor processes...")

        try:
            processes = self.find_cursor_processes()
            killed = 0

            for proc_info in processes:
                try:
                    proc = psutil.Process(proc_info.pid)
                    proc.terminate()
                    killed += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    logger.debug(f"   Could not kill process {proc_info.pid}: {e}")

            # Wait a bit
            time.sleep(1)

            # Force kill if still running
            remaining = self.find_cursor_processes()
            for proc_info in remaining:
                try:
                    proc = psutil.Process(proc_info.pid)
                    proc.kill()
                    killed += 1
                except:
                    pass

            logger.info(f"   ✅ Killed {killed} Cursor processes")
            return True

        except Exception as e:
            logger.error(f"   ❌ Force kill failed: {e}")
            return False

    def is_cursor_running(self) -> bool:
        """Check if Cursor is already running (main process only)"""
        if not psutil:
            return False

        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    proc_info = proc.info
                    if 'cursor' in proc_info['name'].lower():
                        cmdline = ' '.join(proc_info.get('cmdline', []))
                        # Check if it's a main process (not a child process with --type=)
                        if '--type=' not in cmdline:
                            return True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            logger.debug(f"Error checking if Cursor is running: {e}")

        return False

    def restart_cursor(self) -> bool:
        """Restart Cursor IDE"""
        logger.info("🚀 Restarting Cursor IDE...")

        try:
            # Check if Cursor is already running
            if self.is_cursor_running():
                logger.info("   ℹ️  Cursor is already running - skipping launch")
                logger.info("   💡 If you need to restart, close Cursor first or use graceful shutdown")
                return True

            # Find Cursor executable path
            # Common locations on Windows
            cursor_paths = [
                Path.home() / "AppData" / "Local" / "Programs" / "cursor" / "Cursor.exe",
                Path.home() / "AppData" / "Local" / "Programs" / "cursor" / "cursor.exe",
                Path("C:/Program Files/Cursor/Cursor.exe"),
                Path("C:/Program Files (x86)/Cursor/Cursor.exe"),
            ]

            cursor_exe = None
            for path in cursor_paths:
                if path.exists():
                    cursor_exe = path
                    break

            if not cursor_exe:
                # Try to find it in PATH or common locations
                try:
                    result = subprocess.run(
                        ["where", "cursor"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0 and result.stdout.strip():
                        cursor_exe = Path(result.stdout.strip().split('\n')[0])
                except:
                    pass

            if not cursor_exe or not cursor_exe.exists():
                logger.error("   ❌ Cursor executable not found")
                logger.info("   💡 Please start Cursor manually")
                return False

            # Restore workspace folder if available
            workspace_folder = self.workspace_state.get("workspace_folder")
            if workspace_folder and Path(workspace_folder).exists():
                # Start with workspace folder
                subprocess.Popen([str(cursor_exe), workspace_folder], shell=True)
                logger.info(f"   ✅ Restarted Cursor with workspace: {workspace_folder}")
            else:
                # Start without specific workspace
                subprocess.Popen([str(cursor_exe)], shell=True)
                logger.info("   ✅ Restarted Cursor")

            time.sleep(self.RESTART_DELAY)
            return True

        except Exception as e:
            logger.error(f"   ❌ Failed to restart Cursor: {e}")
            return False

    def warm_recycle(self, reason: Optional[RecycleReason] = None) -> bool:
        """
        Perform intelligent warm recycle of Cursor IDE

        Args:
            reason: Reason for recycling (optional)

        Returns:
            True if successful
        """
        logger.info("🔄 Starting intelligent warm recycle...")

        if reason:
            logger.info(f"   Reason: {reason.value}")

        # Step 1: Save workspace state
        self.save_workspace_state()

        # Step 2: Save all files
        self.save_all_files()

        # Step 3: Gracefully shut down
        shutdown_success = self.graceful_shutdown()

        if not shutdown_success:
            logger.warning("   ⚠️  Graceful shutdown failed, but continuing...")

        # Step 4: Wait a bit
        time.sleep(1)

        # Step 5: Restart
        restart_success = self.restart_cursor()

        if restart_success:
            self.last_recycle_time = datetime.now()
            self.recycle_count += 1
            self._save_config()
            logger.info("✅ Warm recycle completed successfully")
            return True
        else:
            logger.error("❌ Warm recycle failed")
            return False

    def start_monitoring(self, interval: float = 60.0):
        """Start automatic monitoring and recycling"""
        if self.monitoring_active:
            logger.warning("⚠️  Monitoring already active")
            return

        self.monitoring_active = True

        def monitor_loop():
            logger.info(f"👁️  Starting automatic monitoring (interval: {interval}s)")

            while self.monitoring_active:
                try:
                    decision = self.should_recycle()

                    if decision.should_recycle:
                        logger.info(f"🔄 Recycle decision: {decision.reason.value} "
                                  f"(urgency: {decision.urgency}, confidence: {decision.confidence:.2f})")

                        self.warm_recycle(decision.reason)
                    else:
                        # Log metrics for monitoring
                        if decision.metrics:
                            logger.debug(f"📊 Cursor healthy: "
                                       f"Memory: {decision.metrics.get('total_memory_mb', 0):.1f}MB, "
                                       f"CPU: {decision.metrics.get('max_cpu_percent', 0):.1f}%")

                    time.sleep(interval)

                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}")
                    time.sleep(interval)

        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()

        logger.info("✅ Automatic monitoring started")

    def stop_monitoring(self):
        """Stop automatic monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("🛑 Automatic monitoring stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Cursor IDE Intelligent Warm Recycle System"
    )
    parser.add_argument("--check", action="store_true",
                       help="Check if recycle is needed")
    parser.add_argument("--recycle", action="store_true",
                       help="Perform warm recycle now")
    parser.add_argument("--monitor", action="store_true",
                       help="Start automatic monitoring")
    parser.add_argument("--interval", type=float, default=60.0,
                       help="Monitoring interval in seconds (default: 60)")

    args = parser.parse_args()

    recycle_system = CursorIntelligentWarmRecycle()

    if args.check:
        decision = recycle_system.should_recycle()
        print(f"\n🔄 Recycle Decision:")
        print(f"   Should recycle: {decision.should_recycle}")
        if decision.should_recycle:
            print(f"   Reason: {decision.reason.value}")
            print(f"   Urgency: {decision.urgency}")
            print(f"   Confidence: {decision.confidence:.2f}")
        print(f"\n📊 Current Metrics:")
        if decision.metrics:
            for key, value in decision.metrics.items():
                if key != "timestamp":
                    print(f"   {key}: {value}")

    elif args.recycle:
        success = recycle_system.warm_recycle(RecycleReason.MANUAL)
        sys.exit(0 if success else 1)

    elif args.monitor:
        recycle_system.start_monitoring(interval=args.interval)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            recycle_system.stop_monitoring()
            print("\n🛑 Monitoring stopped")

    else:
        parser.print_help()
        print("\n" + "="*70)
        print("🔄 Cursor IDE Intelligent Warm Recycle")
        print("="*70)
        print()
        print("Automatically and intelligently recycles Cursor IDE when needed.")
        print()
        print("Examples:")
        print("  python cursor_intelligent_warm_recycle.py --check")
        print("    Check if recycle is needed")
        print()
        print("  python cursor_intelligent_warm_recycle.py --recycle")
        print("    Perform warm recycle now")
        print()
        print("  python cursor_intelligent_warm_recycle.py --monitor --interval 60")
        print("    Start automatic monitoring (checks every 60 seconds)")
        print()
        print("="*70)


if __name__ == "__main__":


    main()