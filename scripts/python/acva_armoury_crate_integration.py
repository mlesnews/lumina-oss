#!/usr/bin/env python3
"""
ACVA Armoury Crate Integration - "Hacking" It In A Good Way!

Integrates with ASUS Armoury Crate Virtual Assistant (stock Windows app)
and makes it do our bidding - full LUMINA ecosystem integration.

Tags: #ACVA #ARMOURY_CRATE #ASUS #INTEGRATION #LUMINA @JARVIS @TEAM
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

logger = get_logger("ACVAArmouryCrateIntegration")


class ACVAArmouryCrateIntegration:
    """
    ACVA Armoury Crate Integration

    "Hacks" the ASUS Armoury Crate Virtual Assistant in a good way:
    - Finds the stock ACVA process/window
    - Integrates it with LUMINA ecosystem
    - Makes it do our bidding
    - Full control and visibility
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ACVA integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        if sys.platform != "win32":
            logger.warning("This integration is for Windows only")
            return

        # Windows API
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32

        # ACVA window handle
        self.acva_hwnd = None

        # Collaboration system integration
        self.collaboration = None
        self._init_collaboration()

        # Position update thread
        self.position_update_thread = None
        self.running = False

        logger.info("✅ ACVA Armoury Crate Integration initialized")
        logger.info("   'Hacking' ACVA in a good way - making it do our bidding!")
        logger.info("   Collaboration system: ENABLED - Ace can now work with Kenny!")

    def _init_collaboration(self):
        """Initialize collaboration system"""
        try:
            from kenny_aces_collaboration import get_collaboration
            self.collaboration = get_collaboration()
            logger.info("✅ Collaboration system loaded - Ace can communicate with Kenny!")
        except Exception as e:
            logger.debug(f"Collaboration system not available: {e}")
            self.collaboration = None

    def find_armoury_crate_va(self) -> Optional[int]:
        """Find ASUS Armoury Crate Virtual Assistant window"""
        logger.info("="*80)
        logger.info("🔍 FINDING ASUS ARMOURY CRATE VIRTUAL ASSISTANT")
        logger.info("="*80)

        # Possible window titles for Armoury Crate VA
        possible_titles = [
            "Armoury Crate",
            "ASUS Armoury Crate",
            "ArmouryCrate",
            "Virtual Assistant",
            "AC VA",
            "Armoury",
            "ASUS",
            "Virtual Pet",  # ACVA is often "Virtual Pet.exe"
            "Pet"
        ]

        # Also search by process name
        process_names = [
            "Virtual Pet.exe",
            "ArmouryCrateControlInterface.exe",
            "ArmouryCrate.exe",
            "ACVA.exe"
        ]

        windows_found = []

        # First, search by process name (more reliable)
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                proc_name = proc.info.get('name', '').lower()
                if any(pn.lower() in proc_name for pn in process_names):
                    # Found matching process - find its windows
                    pid = proc.info['pid']

                    def enum_for_process(hwnd, lParam):
                        process_id = wintypes.DWORD()
                        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))
                        if process_id.value == pid and self.user32.IsWindowVisible(hwnd):
                            buffer = ctypes.create_unicode_buffer(512)
                            self.user32.GetWindowTextW(hwnd, buffer, 512)
                            title = buffer.value
                            if title:  # Only windows with titles
                                windows_found.append((hwnd, title, proc_name))
                        return True

                    EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
                    self.user32.EnumWindows(EnumWindowsProc(enum_for_process), 0)
        except ImportError:
            logger.warning("⚠️  psutil not available - using window title search only")

        # Also search by window title (fallback)
        def enum_callback(hwnd, lParam):
            if self.user32.IsWindowVisible(hwnd):
                buffer = ctypes.create_unicode_buffer(512)
                self.user32.GetWindowTextW(hwnd, buffer, 512)
                title = buffer.value.lower()

                # Check if it matches any Armoury Crate pattern
                for pattern in possible_titles:
                    if pattern.lower() in title:
                        # Get process name to verify
                        process_id = wintypes.DWORD()
                        self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(process_id))

                        # Get process name
                        try:
                            import psutil
                            proc = psutil.Process(process_id.value)
                            proc_name = proc.name().lower()

                            # Check if it's Armoury Crate related
                            if any(keyword in proc_name for keyword in ['armoury', 'asus', 'ac', 'crate', 'virtual', 'pet']):
                                if (hwnd, buffer.value, proc_name) not in windows_found:
                                    windows_found.append((hwnd, buffer.value, proc_name))
                        except:
                            if (hwnd, buffer.value, "unknown") not in windows_found:
                                windows_found.append((hwnd, buffer.value, "unknown"))
            return True

        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)
        self.user32.EnumWindows(EnumWindowsProc(enum_callback), 0)

        if windows_found:
            logger.info(f"✅ Found {len(windows_found)} potential Armoury Crate windows:")
            for hwnd, title, proc in windows_found:
                logger.info(f"   HWND {hwnd}: {title} (Process: {proc})")

            # Use the first one (or most likely match)
            self.acva_hwnd = windows_found[0][0]
            logger.info(f"✅ ACVA window found: HWND {self.acva_hwnd}")
            return self.acva_hwnd
        else:
            logger.warning("⚠️  Armoury Crate VA window not found")
            logger.info("   Make sure Armoury Crate is running")
            return None

    def bring_acva_to_front(self) -> bool:
        """Bring ACVA window to front"""
        if not self.acva_hwnd:
            if not self.find_armoury_crate_va():
                return False

        try:
            SW_RESTORE = 9
            HWND_TOP = 0

            self.user32.ShowWindow(self.acva_hwnd, SW_RESTORE)
            self.user32.SetForegroundWindow(self.acva_hwnd)
            self.user32.BringWindowToTop(self.acva_hwnd)
            self.user32.SetActiveWindow(self.acva_hwnd)
            self.user32.SetWindowPos(self.acva_hwnd, HWND_TOP, 0, 0, 0, 0, 0x0001 | 0x0002)

            logger.info("✅ ACVA brought to front")
            return True
        except Exception as e:
            logger.error(f"❌ Error bringing ACVA to front: {e}")
            return False

    def get_acva_window_info(self) -> Dict[str, Any]:
        """Get ACVA window information"""
        if not self.acva_hwnd:
            if not self.find_armoury_crate_va():
                return {}

        try:
            # Get window title
            buffer = ctypes.create_unicode_buffer(512)
            self.user32.GetWindowTextW(self.acva_hwnd, buffer, 512)
            title = buffer.value

            # Get window position and size
            rect = wintypes.RECT()
            self.user32.GetWindowRect(self.acva_hwnd, ctypes.byref(rect))

            # Get process info
            process_id = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(self.acva_hwnd, ctypes.byref(process_id))

            proc_name = "unknown"
            try:
                import psutil
                proc = psutil.Process(process_id.value)
                proc_name = proc.name()
            except:
                pass

            return {
                "hwnd": self.acva_hwnd,
                "title": title,
                "position": {
                    "x": rect.left,
                    "y": rect.top,
                    "width": rect.right - rect.left,
                    "height": rect.bottom - rect.top
                },
                "process_id": process_id.value,
                "process_name": proc_name,
                "visible": self.user32.IsWindowVisible(self.acva_hwnd) != 0
            }
        except Exception as e:
            logger.error(f"❌ Error getting ACVA info: {e}")
            return {}

    def integrate_with_lumina(self) -> bool:
        """Integrate ACVA with LUMINA ecosystem"""
        logger.info("="*80)
        logger.info("🔗 INTEGRATING ACVA WITH LUMINA ECOSYSTEM")
        logger.info("   Making it do our bidding!")
        logger.info("="*80)

        if not self.find_armoury_crate_va():
            logger.error("❌ Cannot integrate - ACVA not found")
            return False

        # Integration steps
        logger.info("✅ ACVA found - beginning integration...")

        # Step 1: Bring to front
        self.bring_acva_to_front()

        # Step 2: Get window info
        info = self.get_acva_window_info()
        logger.info(f"   Window: {info.get('title', 'Unknown')}")
        logger.info(f"   Position: ({info.get('position', {}).get('x', 0)}, {info.get('position', {}).get('y', 0)})")
        logger.info(f"   Process: {info.get('process_name', 'Unknown')}")

        # Step 3: Register with JARVIS agent management
        try:
            from jarvis_peak_agent_management import JARVISPeakAgentManagement
            manager = JARVISPeakAgentManagement(project_root=self.project_root)

            acva_agent = manager.register_agent(
                agent_id="acva_armoury_crate",
                agent_name="ACVA - ASUS Armoury Crate Virtual Assistant",
                task="Stock ASUS Armoury Crate VA - integrated with LUMINA, doing our bidding",
                requirements={
                    "isolation": False,
                    "cpu": 5.0,
                    "memory": 200.0,
                    "windows_app": True,
                    "armoury_crate": True
                },
                command=None,  # External Windows app
                dependencies=[],
                peak_tool_selection={
                    "framework": "local",
                    "rationale": "Stock Windows app - direct integration via Windows API",
                    "alternatives_considered": []
                }
            )

            logger.info("✅ ACVA registered with JARVIS agent management")
        except Exception as e:
            logger.warning(f"⚠️  Could not register with JARVIS: {e}")

        # Step 4: Start position update loop (for collaboration)
        self.start_position_updates()

        logger.info("✅ ACVA integration complete - it's now doing our bidding!")
        logger.info("   🤝 Collaboration with Kenny: ENABLED")
        return True

    def start_position_updates(self):
        """Start position update loop for collaboration system"""
        if not self.collaboration:
            logger.warning("⚠️  Cannot start position updates - collaboration system not available")
            return

        if self.running:
            return

        self.running = True
        import threading
        self.position_update_thread = threading.Thread(target=self._position_update_loop, daemon=True)
        self.position_update_thread.start()
        logger.info("✅ Ace position update loop started - collaboration active!")

    def stop_position_updates(self):
        """Stop position update loop"""
        self.running = False
        if self.position_update_thread:
            self.position_update_thread.join(timeout=1.0)
        logger.info("🛑 Ace position update loop stopped")

    def _position_update_loop(self):
        """Update Ace's position to collaboration system"""
        import time
        while self.running:
            try:
                # Get Ace's current window position
                info = self.get_acva_window_info()
                if info and info.get('position'):
                    pos = info['position']
                    x = pos.get('x', 0)
                    y = pos.get('y', 0)
                    size = max(pos.get('width', 100), pos.get('height', 100))  # Use larger dimension

                    # Update position in collaboration system
                    if self.collaboration:
                        self.collaboration.update_ace_position(x, y, size)

                    # Check for messages from Kenny
                    self._check_collaboration_messages()

                # Update every 0.5 seconds (tortoise pace - slow and steady)
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Error in position update loop: {e}")
                time.sleep(1.0)

    def _check_collaboration_messages(self):
        """Check for messages from Kenny via collaboration system"""
        if not self.collaboration:
            return

        try:
            messages = self.collaboration.get_messages("ace")

            for msg in messages:
                if msg.message_type.value == "collision_warning":
                    # Handle collision warning - Ace should respond
                    distance = msg.payload.get('distance', 0)
                    logger.debug(f"⚠️  Ace received collision warning: {distance:.1f}px from Kenny")
                    # Ace could change direction or acknowledge
                    # For now, just log it (apathetic behavior - but at least aware)

                elif msg.message_type.value == "position_update":
                    # Kenny's position updated
                    logger.debug(f"📍 Ace knows Kenny is at ({msg.payload.get('x', 0)}, {msg.payload.get('y', 0)})")

                elif msg.message_type.value == "greeting":
                    # Kenny is greeting Ace
                    logger.info(f"👋 Ace received greeting from Kenny: {msg.payload}")
                    # Ace should respond (but currently apathetic - future enhancement)

            # Clear processed messages
            self.collaboration.clear_processed_messages("ace")
        except Exception as e:
            logger.debug(f"Could not check collaboration messages: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ACVA Armoury Crate Integration")
    parser.add_argument("--find", action="store_true", help="Find ACVA window")
    parser.add_argument("--bring-front", action="store_true", help="Bring ACVA to front")
    parser.add_argument("--info", action="store_true", help="Get ACVA window info")
    parser.add_argument("--integrate", action="store_true", help="Integrate with LUMINA")
    parser.add_argument("--full", action="store_true", help="Full integration workflow")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔗 ACVA Armoury Crate Integration")
    print("   'Hacking' It In A Good Way - Making It Do Our Bidding!")
    print("="*80 + "\n")

    integration = ACVAArmouryCrateIntegration()

    if args.full:
        integration.integrate_with_lumina()
    else:
        if args.find:
            integration.find_armoury_crate_va()
        if args.bring_front:
            integration.bring_acva_to_front()
        if args.info:
            info = integration.get_acva_window_info()
            print("\n📊 ACVA Window Info:")
            print("="*80)
            for key, value in info.items():
                print(f"   {key}: {value}")
            print("="*80)
        if args.integrate:
            integration.integrate_with_lumina()

        if not any([args.find, args.bring_front, args.info, args.integrate]):
            print("Use --full to run complete integration workflow")
            print("Or use individual flags: --find --bring-front --info --integrate")
            print("="*80 + "\n")
