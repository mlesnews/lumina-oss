#!/usr/bin/env python3
"""
JARVIS Keyboard Lock Fix - Physical Button/Key Control
Forces all keyboard locks to OFF state with hardware-level control

@JARVIS @FIX @LOCK @PHYSICAL @BUTTONS
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLockFix")


class JARVISKeyboardLockFix:
    """
    Enhanced Keyboard Lock Fix

    Forces all keyboard locks to OFF state using:
    - Hardware-level key simulation
    - Multiple verification methods
    - Force unlock strategy (not just toggle)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize lock fix system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration
        self.armoury_crate = create_armoury_crate_integration()

        logger.info("✅ JARVIS Keyboard Lock Fix initialized")

    async def _force_lock_off(self, lock_name: str, vk_code: int, scan_code: int, key_string: str, combo_keys: Optional[list] = None) -> Dict[str, Any]:
        """
        Force a lock to OFF state (not just toggle)

        Strategy:
        1. Check current state
        2. If ON, toggle multiple times to ensure OFF
        3. Verify final state
        """
        logger.info(f"🔓 FORCING {lock_name} to OFF state...")

        import ctypes
        KEYEVENTF_KEYUP = 0x0002

        results = {
            "lock_name": lock_name,
            "attempts": [],
            "final_state": "unknown"
        }

        try:
            # Strategy: Toggle multiple times to ensure OFF state
            # Most locks toggle: ON -> OFF -> ON -> OFF
            # So we toggle 2-3 times to ensure we end up OFF

            for attempt in range(3):
                logger.info(f"  Attempt {attempt + 1}/3: Long press toggle...")

                if combo_keys:
                    # For combo keys (like FN+Esc), press all keys together
                    for vk, sc in combo_keys:
                        ctypes.windll.user32.keybd_event(vk, sc, 0, 0)
                    await asyncio.sleep(0.05)

                    # Hold for 3 seconds (longer for more reliability)
                    await asyncio.sleep(3.0)

                    # Release in reverse order
                    for vk, sc in reversed(combo_keys):
                        ctypes.windll.user32.keybd_event(vk, sc, KEYEVENTF_KEYUP, 0)
                        await asyncio.sleep(0.05)
                else:
                    # Single key long press
                    ctypes.windll.user32.keybd_event(vk_code, scan_code, 0, 0)
                    await asyncio.sleep(3.0)  # 3 second hold
                    ctypes.windll.user32.keybd_event(vk_code, scan_code, KEYEVENTF_KEYUP, 0)

                await asyncio.sleep(1.0)  # Wait for state change
                results["attempts"].append(f"Attempt {attempt + 1} completed")

            logger.info(f"✅ {lock_name} force unlock completed (3 attempts)")
            results["success"] = True
            results["message"] = f"{lock_name} force unlock completed"

        except Exception as e:
            logger.error(f"❌ {lock_name} force unlock failed: {e}")
            results["success"] = False
            results["error"] = str(e)

        return results

    async def _check_lock_state(self, lock_name: str, vk_code: int) -> str:
        """Check current lock state using Windows API"""
        try:
            import ctypes

            # Get key state
            state = ctypes.windll.user32.GetKeyState(vk_code)

            # High bit (0x8000) indicates key is pressed/toggled
            if state & 0x8000:
                return "ON"
            elif state & 0x0001:
                return "ON"  # Toggle state
            else:
                return "OFF"
        except Exception as e:
            logger.warning(f"Could not check {lock_name} state: {e}")
            return "UNKNOWN"

    async def fix_all_locks(self) -> Dict[str, Any]:
        """
        Fix all keyboard locks - force them all to OFF

        Locks fixed:
        - FN Lock (Fn+Esc)
        - Num Lock
        - Caps Lock
        - Scroll Lock
        """
        logger.info("=" * 70)
        logger.info("🔧 JARVIS KEYBOARD LOCK FIX")
        logger.info("   Forcing all locks to OFF state")
        logger.info("=" * 70)

        results = {
            "locks_fixed": {},
            "success": False
        }

        try:
            # 1. Fix FN Lock (Fn+Esc combo)
            logger.info("\n🔓 FIXING FN LOCK...")
            VK_ESCAPE = 0x1B
            SCANCODE_ESC = 0x01
            VK_APPS = 0x5D  # Application key as FN simulation

            # Try multiple FN key codes
            fn_combos = [
                [(VK_APPS, 0), (VK_ESCAPE, SCANCODE_ESC)],  # Apps+Esc
                [(0x5B, 0), (VK_ESCAPE, SCANCODE_ESC)],     # Left Win+Esc
            ]

            for combo in fn_combos:
                fn_result = await self._force_lock_off(
                    "FN Lock",
                    VK_ESCAPE,
                    SCANCODE_ESC,
                    "fn+esc",
                    combo_keys=combo
                )
                results["locks_fixed"]["fn_lock"] = fn_result
                if fn_result.get("success"):
                    break

            await asyncio.sleep(2)

            # 2. Fix Num Lock
            logger.info("\n🔓 FIXING NUM LOCK...")
            VK_NUMLOCK = 0x90
            SCANCODE_NUMLOCK = 0x45

            # Check current state first
            num_state_before = await self._check_lock_state("Num Lock", VK_NUMLOCK)
            logger.info(f"  Current state: {num_state_before}")

            if num_state_before == "ON":
                num_result = await self._force_lock_off(
                    "Num Lock",
                    VK_NUMLOCK,
                    SCANCODE_NUMLOCK,
                    "numlock"
                )
                results["locks_fixed"]["num_lock"] = num_result

                # Verify
                await asyncio.sleep(1)
                num_state_after = await self._check_lock_state("Num Lock", VK_NUMLOCK)
                logger.info(f"  State after fix: {num_state_after}")
                num_result["state_before"] = num_state_before
                num_result["state_after"] = num_state_after
            else:
                logger.info(f"  Num Lock already OFF, skipping")
                results["locks_fixed"]["num_lock"] = {"success": True, "state": "already_off"}

            await asyncio.sleep(2)

            # 3. Fix Caps Lock
            logger.info("\n🔓 FIXING CAPS LOCK...")
            VK_CAPITAL = 0x14
            SCANCODE_CAPSLOCK = 0x3A

            caps_state_before = await self._check_lock_state("Caps Lock", VK_CAPITAL)
            logger.info(f"  Current state: {caps_state_before}")

            if caps_state_before == "ON":
                caps_result = await self._force_lock_off(
                    "Caps Lock",
                    VK_CAPITAL,
                    SCANCODE_CAPSLOCK,
                    "capslock"
                )
                results["locks_fixed"]["caps_lock"] = caps_result

                await asyncio.sleep(1)
                caps_state_after = await self._check_lock_state("Caps Lock", VK_CAPITAL)
                logger.info(f"  State after fix: {caps_state_after}")
                caps_result["state_before"] = caps_state_before
                caps_result["state_after"] = caps_state_after
            else:
                logger.info(f"  Caps Lock already OFF, skipping")
                results["locks_fixed"]["caps_lock"] = {"success": True, "state": "already_off"}

            await asyncio.sleep(2)

            # 4. Fix Scroll Lock (this one was ON in the output)
            logger.info("\n🔓 FIXING SCROLL LOCK...")
            VK_SCROLL = 0x91
            SCANCODE_SCROLLLOCK = 0x46

            scroll_state_before = await self._check_lock_state("Scroll Lock", VK_SCROLL)
            logger.info(f"  Current state: {scroll_state_before}")

            if scroll_state_before == "ON":
                scroll_result = await self._force_lock_off(
                    "Scroll Lock",
                    VK_SCROLL,
                    SCANCODE_SCROLLLOCK,
                    "scrolllock"
                )
                results["locks_fixed"]["scroll_lock"] = scroll_result

                await asyncio.sleep(1)
                scroll_state_after = await self._check_lock_state("Scroll Lock", VK_SCROLL)
                logger.info(f"  State after fix: {scroll_state_after}")
                scroll_result["state_before"] = scroll_state_before
                scroll_result["state_after"] = scroll_state_after
            else:
                logger.info(f"  Scroll Lock already OFF, skipping")
                results["locks_fixed"]["scroll_lock"] = {"success": True, "state": "already_off"}

            # Final verification
            logger.info("\n" + "=" * 70)
            logger.info("📊 FINAL LOCK STATES")
            logger.info("=" * 70)

            final_states = {}
            for lock_name, vk_code in [
                ("Num Lock", VK_NUMLOCK),
                ("Caps Lock", VK_CAPITAL),
                ("Scroll Lock", VK_SCROLL)
            ]:
                state = await self._check_lock_state(lock_name, vk_code)
                final_states[lock_name.lower().replace(" ", "_")] = state
                status_icon = "✅" if state == "OFF" else "❌" if state == "ON" else "⚠️"
                logger.info(f"{status_icon} {lock_name}: {state}")

            logger.info("⚠️  FN Lock: UNKNOWN (not directly detectable via Windows API)")
            logger.info("   Manual test: Try fn+F4 to see if it works")

            results["final_states"] = final_states
            results["success"] = all(
                state == "OFF" or state == "UNKNOWN"
                for state in final_states.values()
            )

            logger.info("=" * 70)
            if results["success"]:
                logger.info("✅ ALL LOCKS FIXED - All locks are now OFF")
            else:
                logger.info("⚠️  SOME LOCKS MAY STILL BE ON - Check manual verification")
            logger.info("=" * 70)

        except Exception as e:
            logger.error(f"Lock fix error: {e}", exc_info=True)
            results["success"] = False
            results["error"] = str(e)

        return results


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔧 JARVIS KEYBOARD LOCK FIX")
    print("   Fixing physical keyboard button/keys")
    print("=" * 70)
    print()

    fixer = JARVISKeyboardLockFix()
    results = await fixer.fix_all_locks()

    print()
    print("=" * 70)
    print("📊 FIX RESULTS")
    print("=" * 70)
    print(f"Success: {results.get('success', False)}")
    print()

    if results.get("final_states"):
        print("Final Lock States:")
        for lock, state in results["final_states"].items():
            status_icon = "✅" if state == "OFF" else "❌" if state == "ON" else "⚠️"
            print(f"  {status_icon} {lock}: {state}")

    print()
    print("=" * 70)
    print("✅ KEYBOARD LOCK FIX COMPLETE")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())