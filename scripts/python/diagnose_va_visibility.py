#!/usr/bin/env python3
"""
Diagnose Virtual Assistant Visibility
Checks if Kenny and Ace are running and visible, provides diagnostics.

Tags: #KENNY #ACE #DIAGNOSTICS #VISIBILITY @JARVIS @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DiagnoseVA")

def check_python_processes():
    """Check for Python processes"""
    try:
        import psutil
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline:
                        cmdline_str = ' '.join(str(c) for c in cmdline)
                        if 'kenny' in cmdline_str.lower() or 'imva' in cmdline_str.lower():
                            processes.append({
                                'pid': proc.info['pid'],
                                'cmdline': cmdline_str,
                                'runtime': time.time() - proc.info['create_time']
                            })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return processes
    except ImportError:
        logger.warning("⚠️  psutil not available - cannot check processes")
        return []

def check_tkinter_windows():
    """Check for tkinter windows (Kenny uses tkinter)"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide test window

        # Get all tkinter windows
        # This is a simplified check - actual implementation would enumerate windows
        logger.info("✅ tkinter is available")
        root.destroy()
        return True
    except ImportError:
        logger.error("❌ tkinter not available - Kenny cannot run")
        return False
    except Exception as e:
        logger.warning(f"⚠️  tkinter check error: {e}")
        return False

def check_ace_window():
    """Check for Ace (ACVA) window"""
    try:
        from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
        ace = ACVAArmouryCrateIntegration(project_root)
        hwnd = ace.find_armoury_crate_va()

        if hwnd:
            info = ace.get_acva_window_info()
            return {
                'found': True,
                'hwnd': hwnd,
                'visible': info.get('visible', False) if info else False,
                'position': info.get('position', None) if info else None
            }
        return {'found': False}
    except Exception as e:
        logger.warning(f"⚠️  Could not check Ace: {e}")
        return {'found': False, 'error': str(e)}

def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("🔍 VIRTUAL ASSISTANT VISIBILITY DIAGNOSTICS")
    print("=" * 80)
    print()

    # Check Python processes
    print("📊 Checking Python Processes...")
    processes = check_python_processes()
    if processes:
        print(f"   ✅ Found {len(processes)} Kenny-related process(es):")
        for proc in processes:
            print(f"      PID {proc['pid']}: Running for {proc['runtime']:.1f}s")
            print(f"         Command: {proc['cmdline'][:100]}...")
    else:
        print("   ❌ No Kenny processes found")
        print("      Kenny is not running")
    print()

    # Check tkinter
    print("📊 Checking tkinter (Required for Kenny)...")
    tkinter_ok = check_tkinter_windows()
    if tkinter_ok:
        print("   ✅ tkinter is available")
    else:
        print("   ❌ tkinter not available - Kenny cannot run")
    print()

    # Check Ace
    print("📊 Checking Ace (ACVA)...")
    ace_status = check_ace_window()
    if ace_status.get('found'):
        print(f"   ✅ Ace window found (HWND: {ace_status.get('hwnd')})")
        if ace_status.get('visible'):
            print("   ✅ Ace is visible")
        else:
            print("   ⚠️  Ace window found but may not be visible")
        if ace_status.get('position'):
            pos = ace_status['position']
            print(f"   📍 Position: ({pos.get('x', '?')}, {pos.get('y', '?')})")
    else:
        print("   ⚠️  Ace window not found")
        print("      Is Armoury Crate running?")
    print()

    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print()

    if not processes:
        print("❌ Kenny is not running")
        print("   → Run: python scripts/python/start_kenny_visible.py")
        print("   → Or: python scripts/python/start_animated_vas_wandering.py")
    else:
        print("✅ Kenny process(es) found")
        print("   → If not visible, window might be off-screen")
        print("   → Run: python scripts/python/ensure_vas_visible.py")
        print("   → Check desktop corners and edges")

    if not tkinter_ok:
        print("❌ tkinter not available")
        print("   → Install: pip install tk")
        print("   → Or use system Python with tkinter")

    if not ace_status.get('found'):
        print("⚠️  Ace not found")
        print("   → Make sure Armoury Crate is running")
        print("   → Enable ACVA in Armoury Crate settings")

    print()
    print("=" * 80)
    print()
    print("🚀 Quick Start Commands:")
    print("   python scripts/python/start_kenny_visible.py")
    print("   python scripts/python/ensure_vas_visible.py")
    print("   python scripts/python/start_animated_vas_wandering.py")
    print()
    print("=" * 80)

if __name__ == "__main__":


    main()