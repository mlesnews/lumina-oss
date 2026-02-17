#!/usr/bin/env python3
"""
Diagnose MANUS Control Interference

Checks for MANUS control systems that might be interfering with existing functionality.
Identifies background processes, daemon threads, and automation that could break things.

Tags: #DIAGNOSTIC #MANUS #INTERFERENCE #DEBUG @JARVIS @TEAM
"""

import sys
import psutil
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import json
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DiagnoseManusInterference")


class ManusInterferenceDiagnostic:
    """
    Diagnose MANUS control interference with existing systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ MANUS Interference Diagnostic initialized")

    def check_python_processes(self) -> List[Dict[str, Any]]:
        """Check for Python processes that might be interfering"""
        logger.info("="*80)
        logger.info("🔍 Checking Python Processes")
        logger.info("="*80)

        processes = []
        manus_keywords = ['manus', 'cursor', 'control', 'automation', 'jarvis']

        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                proc_info = proc.info
                cmdline = proc_info.get('cmdline', [])
                if not cmdline:
                    continue

                # Check if it's a Python process
                if 'python' in proc_info.get('name', '').lower():
                    cmdline_str = ' '.join(cmdline).lower()

                    # Check if it's a MANUS-related process
                    is_manus = any(kw in cmdline_str for kw in manus_keywords)

                    if is_manus or 'lumina' in cmdline_str:
                        processes.append({
                            "pid": proc_info['pid'],
                            "name": proc_info['name'],
                            "cmdline": cmdline,
                            "is_manus_related": is_manus,
                            "create_time": datetime.fromtimestamp(proc_info['create_time']).isoformat() if proc_info.get('create_time') else None
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        logger.info(f"   Found {len(processes)} potentially relevant Python processes")
        for proc in processes:
            logger.info(f"   PID {proc['pid']}: {proc['name']} - {'MANUS-related' if proc['is_manus_related'] else 'LUMINA-related'}")
            logger.info(f"      CMD: {' '.join(proc['cmdline'][:3])}...")

        return processes

    def check_background_threads(self) -> Dict[str, Any]:
        """Check for background threads that might be interfering"""
        logger.info("="*80)
        logger.info("🔍 Checking Background Threads")
        logger.info("="*80)

        threads_info = {
            "total_threads": threading.active_count(),
            "threads": []
        }

        for thread in threading.enumerate():
            thread_info = {
                "name": thread.name,
                "daemon": thread.daemon,
                "alive": thread.is_alive(),
                "ident": thread.ident
            }

            # Check if it's MANUS-related
            if any(kw in thread.name.lower() for kw in ['manus', 'cursor', 'control', 'monitor', 'stats']):
                thread_info["is_manus_related"] = True
                logger.warning(f"   ⚠️  MANUS-related thread: {thread.name} (daemon={thread.daemon})")
            else:
                thread_info["is_manus_related"] = False

            threads_info["threads"].append(thread_info)

        logger.info(f"   Total threads: {threads_info['total_threads']}")
        manus_threads = [t for t in threads_info['threads'] if t.get('is_manus_related')]
        logger.info(f"   MANUS-related threads: {len(manus_threads)}")

        return threads_info

    def check_manus_control_systems(self) -> Dict[str, Any]:
        """Check for active MANUS control systems"""
        logger.info("="*80)
        logger.info("🔍 Checking MANUS Control Systems")
        logger.info("="*80)

        systems = {
            "live_stats": False,
            "full_control": False,
            "dashboard": False,
            "cursor_controller": False,
            "workstation_controller": False,
            "issues": []
        }

        # Check if live stats is running
        try:
            from jarvis_manus_cursor_live_stats import JARVISManusCursorLiveStats
            # Try to instantiate (will fail if already running or has issues)
            try:
                stats = JARVISManusCursorLiveStats(project_root=self.project_root)
                systems["live_stats"] = True
                logger.info("   ✅ JARVIS MANUS Cursor Live Stats available")
            except Exception as e:
                systems["live_stats"] = False
                systems["issues"].append(f"Live Stats: {str(e)}")
                logger.warning(f"   ⚠️  Live Stats issue: {e}")
        except ImportError as e:
            logger.debug(f"   Live Stats not importable: {e}")

        # Check if full control is running
        try:
            from jarvis_manus_cursor_full_control import JARVISManusCursorFullControl
            try:
                control = JARVISManusCursorFullControl(project_root=self.project_root)
                systems["full_control"] = True
                logger.info("   ✅ JARVIS MANUS Cursor Full Control available")
            except Exception as e:
                systems["full_control"] = False
                systems["issues"].append(f"Full Control: {str(e)}")
                logger.warning(f"   ⚠️  Full Control issue: {e}")
        except ImportError as e:
            logger.debug(f"   Full Control not importable: {e}")

        # Check MANUS unified control
        try:
            from manus_unified_control import MANUSUnifiedControl
            try:
                manus = MANUSUnifiedControl(project_root=self.project_root)
                if manus:
                    systems["cursor_controller"] = True
                    systems["workstation_controller"] = True
                    logger.info("   ✅ MANUS Unified Control available")
            except Exception as e:
                systems["issues"].append(f"MANUS Unified: {str(e)}")
                logger.warning(f"   ⚠️  MANUS Unified issue: {e}")
        except ImportError as e:
            logger.debug(f"   MANUS Unified not importable: {e}")

        return systems

    def check_window_interference(self) -> Dict[str, Any]:
        """Check for window-related interference"""
        logger.info("="*80)
        logger.info("🔍 Checking Window Interference")
        logger.info("="*80)

        interference = {
            "acva_window_found": False,
            "imva_window_found": False,
            "window_issues": []
        }

        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32

            # Check for ACVA window
            def enum_callback(hwnd, lParam):
                if user32.IsWindowVisible(hwnd):
                    buffer = ctypes.create_unicode_buffer(512)
                    user32.GetWindowTextW(hwnd, buffer, 512)
                    title = buffer.value.lower()
                    if 'mascot' in title or 'virtual pet' in title:
                        interference["acva_window_found"] = True
                    if 'iron man' in title or 'imva' in title:
                        interference["imva_window_found"] = True
                return True

            EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
            user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

            if not interference["acva_window_found"]:
                interference["window_issues"].append("ACVA window not found")
                logger.warning("   ⚠️  ACVA window not found")
            else:
                logger.info("   ✅ ACVA window found")

            if not interference["imva_window_found"]:
                interference["window_issues"].append("IMVA window not found")
                logger.warning("   ⚠️  IMVA window not found")
            else:
                logger.info("   ✅ IMVA window found")

        except Exception as e:
            interference["window_issues"].append(f"Window check error: {str(e)}")
            logger.error(f"   ❌ Window check error: {e}")

        return interference

    def run_full_diagnostic(self) -> Dict[str, Any]:
        """Run complete diagnostic"""
        logger.info("="*80)
        logger.info("🔬 MANUS INTERFERENCE DIAGNOSTIC")
        logger.info("="*80)
        logger.info("")

        result = {
            "timestamp": datetime.now().isoformat(),
            "python_processes": self.check_python_processes(),
            "background_threads": self.check_background_threads(),
            "manus_systems": self.check_manus_control_systems(),
            "window_interference": self.check_window_interference(),
            "recommendations": []
        }

        # Generate recommendations
        if result["background_threads"]["total_threads"] > 20:
            result["recommendations"].append("High thread count detected - may indicate background processes interfering")

        manus_threads = [t for t in result["background_threads"]["threads"] if t.get('is_manus_related')]
        if len(manus_threads) > 5:
            result["recommendations"].append(f"Multiple MANUS-related threads ({len(manus_threads)}) - may be interfering")

        if result["manus_systems"]["issues"]:
            result["recommendations"].append("MANUS control systems have issues - may need restart")

        if result["window_interference"]["window_issues"]:
            result["recommendations"].append("Window visibility issues detected - check if MANUS is blocking windows")

        # Save diagnostic report
        report_file = self.data_dir / f"manus_interference_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"   ✅ Diagnostic report saved: {report_file.name}")
        except Exception as e:
            logger.error(f"   ❌ Error saving report: {e}")

        logger.info("")
        logger.info("="*80)
        logger.info("📊 DIAGNOSTIC SUMMARY")
        logger.info("="*80)
        logger.info(f"   Python Processes: {len(result['python_processes'])}")
        logger.info(f"   Total Threads: {result['background_threads']['total_threads']}")
        logger.info(f"   MANUS Systems Active: {sum([result['manus_systems']['live_stats'], result['manus_systems']['full_control']])}")
        logger.info(f"   Window Issues: {len(result['window_interference']['window_issues'])}")
        logger.info(f"   Recommendations: {len(result['recommendations'])}")
        logger.info("")

        if result["recommendations"]:
            logger.warning("⚠️  RECOMMENDATIONS:")
            for rec in result["recommendations"]:
                logger.warning(f"   - {rec}")

        logger.info("="*80)

        return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔬 MANUS Interference Diagnostic")
    print("   Checking for MANUS control systems that might be breaking things")
    print("="*80 + "\n")

    diagnostic = ManusInterferenceDiagnostic()
    result = diagnostic.run_full_diagnostic()

    print("\n" + "="*80)
    print("📊 DIAGNOSTIC RESULTS")
    print("="*80)
    print(f"Python Processes Found: {len(result['python_processes'])}")
    print(f"Total Threads: {result['background_threads']['total_threads']}")
    print(f"MANUS Systems: Live Stats={result['manus_systems']['live_stats']}, Full Control={result['manus_systems']['full_control']}")
    print(f"Window Issues: {len(result['window_interference']['window_issues'])}")
    print()

    if result['recommendations']:
        print("⚠️  RECOMMENDATIONS:")
        for rec in result['recommendations']:
            print(f"   - {rec}")
        print()

    print("="*80 + "\n")
