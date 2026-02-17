#!/usr/bin/env python3
"""
Control ASUS Armoury Crate Virtual Assistant (ACVA)

ACVA is the ASUS Armoury Crate Virtual Assistant that came stock with Windows.
We're 'hacking' it in a good way to make it do our bidding!

Find, control, and integrate with the real ACVA (ASUS Armoury Crate VA).

Tags: #ACVA #ARMOURY_CRATE #ASUS #HACK #INTEGRATION @JARVIS @TEAM
"""

import sys
import ctypes
from ctypes import wintypes
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsControlArmouryCrateACVA")


class VAsControlArmouryCrateACVA:
    """
    Control ASUS Armoury Crate Virtual Assistant (ACVA)

    ACVA is the stock ASUS Armoury Crate VA that came with Windows.
    We're 'hacking' it in a good way to make it do our bidding!
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ACVA controller"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if sys.platform != "win32":
            logger.warning("This script is designed for Windows")
            return

        # Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        logger.info("✅ ASUS Armoury Crate ACVA Controller initialized")
        logger.info("   ACVA = ASUS Armoury Crate Virtual Assistant (stock Windows app)")
        logger.info("   We're 'hacking' it in a good way to make it do our bidding!")

    def find_acva_window(self) -> Optional[int]:
        """Find ASUS Armoury Crate VA window"""
        logger.info("="*80)
        logger.info("🔍 FINDING ASUS ARMOURY CRATE ACVA")
        logger.info("="*80)

        # Possible window titles for ASUS Armoury Crate VA (stock Windows app)
        # ACVA = ASUS Armoury Crate Virtual Assistant (stock app, we're 'hacking' it!)
        acva_titles = [
            "Virtual Pet",  # ASUS ACVA window title
            "Armoury Crate",
            "Armory Crate",
            "ASUS Armoury Crate",
            "ASUS Armory Crate",
            "Armoury Crate Virtual Assistant",
            "Armory Crate Virtual Assistant",
            "AC VA",  # ASUS AC VA (Armoury Crate Virtual Assistant)
            "ACVA",
            "Virtual Assistant",  # Generic - might be ACVA
            "Anakin/Vader Combat VA",  # Our custom title if we renamed it
            "Anakin/Vader Combat VA - LUMINA"
        ]

        windows_found = []

        def callback(hwnd, lParam):
            if self.user32.IsWindowVisible(hwnd):
                buffer = ctypes.create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, buffer, 512)
                title = buffer.value
                if title:
                    # Check if it matches any ACVA title
                    title_lower = title.lower()
                    for acva_title in acva_titles:
                        if acva_title.lower() in title_lower:
                            windows_found.append((hwnd, title))
                            return True
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(EnumWindowsProc(callback), 0)

        if windows_found:
            hwnd, title = windows_found[0]
            logger.info(f"✅ Found ACVA window: {title} (HWND: {hwnd})")
            return hwnd
        else:
            logger.warning("⚠️  ACVA window not found")
            logger.info("   Searching for ASUS/Armoury processes...")
            return None

    def find_armoury_crate_process(self) -> List[Dict[str, Any]]:
        """Find ASUS Armoury Crate processes"""
        try:
            import psutil
            processes = []

            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cmdline']):
                try:
                    name = proc.info.get('name', '').lower()
                    exe = proc.info.get('exe', '')
                    cmdline_list = proc.info.get('cmdline', [])
                    cmdline = ' '.join(str(c) for c in cmdline_list).lower() if cmdline_list else ''

                    # Look for Armoury Crate related processes
                    if any(keyword in name or keyword in cmdline for keyword in 
                           ['armoury', 'armory', 'crate', 'asus', 'acva', 'rog']):
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info.get('name', 'Unknown'),
                            'exe': exe,
                            'cmdline': proc.info.get('cmdline', [])
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return processes
        except ImportError:
            logger.warning("⚠️  psutil not available - cannot find processes")
            return []

    def bring_acva_to_front(self) -> bool:
        """Bring ACVA window to front"""
        hwnd = self.find_acva_window()
        if not hwnd:
            return False

        try:
            # Restore if minimized
            self.user32.ShowWindow(hwnd, 9)  # SW_RESTORE

            # Bring to front
            self.user32.SetForegroundWindow(hwnd)
            self.user32.BringWindowToTop(hwnd)
            self.user32.SetActiveWindow(hwnd)

            # Set window position to top
            HWND_TOP = 0
            self.user32.SetWindowPos(hwnd, HWND_TOP, 0, 0, 0, 0, 0x0001 | 0x0002)

            logger.info("✅ ACVA brought to front")
            return True
        except Exception as e:
            logger.error(f"❌ Error bringing ACVA to front: {e}")
            return False

    def get_acva_info(self) -> Dict[str, Any]:
        """Get ACVA information"""
        info = {
            "window_found": False,
            "window_hwnd": None,
            "window_title": None,
            "processes_found": [],
            "status": "unknown"
        }

        # Find window
        hwnd = self.find_acva_window()
        if hwnd:
            info["window_found"] = True
            info["window_hwnd"] = hwnd
            buffer = ctypes.create_unicode_buffer(512)
            self.user32.GetWindowTextW(hwnd, buffer, 512)
            info["window_title"] = buffer.value
            info["status"] = "active"

        # Find processes
        processes = self.find_armoury_crate_process()
        info["processes_found"] = processes

        return info


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Control ASUS Armoury Crate ACVA")
    parser.add_argument("--find", action="store_true", help="Find ACVA window")
    parser.add_argument("--bring-front", action="store_true", help="Bring ACVA to front")
    parser.add_argument("--processes", action="store_true", help="List Armoury Crate processes")
    parser.add_argument("--info", action="store_true", help="Get ACVA info")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎮 Control ASUS Armoury Crate Virtual Assistant (ACVA)")
    print("   ACVA = Stock ASUS Armoury Crate VA (we're 'hacking' it in a good way!)")
    print("="*80 + "\n")

    controller = VAsControlArmouryCrateACVA()

    if args.find or args.info:
        hwnd = controller.find_acva_window()
        if hwnd:
            print(f"✅ ACVA window found: HWND {hwnd}")
        else:
            print("❌ ACVA window not found")

    if args.processes or args.info:
        processes = controller.find_armoury_crate_process()
        if processes:
            print(f"\n🔍 Found {len(processes)} Armoury Crate processes:")
            for proc in processes:
                print(f"   PID {proc['pid']}: {proc['name']}")
        else:
            print("\n⚠️  No Armoury Crate processes found")

    if args.bring_front:
        controller.bring_acva_to_front()

    if args.info:
        info = controller.get_acva_info()
        print("\n" + "="*80)
        print("📊 ACVA INFORMATION")
        print("="*80)
        print(f"Window Found: {'✅' if info['window_found'] else '❌'}")
        if info['window_found']:
            print(f"Window HWND: {info['window_hwnd']}")
            print(f"Window Title: {info['window_title']}")
        print(f"Processes Found: {len(info['processes_found'])}")
        print(f"Status: {info['status']}")
        print("="*80 + "\n")

    if not any([args.find, args.bring_front, args.processes, args.info]):
        print("Use --find to find ACVA window")
        print("Use --bring-front to bring ACVA to front")
        print("Use --processes to list Armoury Crate processes")
        print("Use --info to get complete ACVA information")
        print("="*80 + "\n")
