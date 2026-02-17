#!/usr/bin/env python3
"""
Cleanup VA Windows - Kill all VA sprites/widgets/avatars except ACE

After testing cycles, clean up all virtual assistant windows and processes,
but keep ACE running (since it's from Armoury Crate, not our Python process).

Tags: #CLEANUP #VA #WINDOWS #TESTING @JARVIS @LUMINA
"""

import sys
import os
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

logger = get_logger("CleanupVAWindows")


def kill_va_windows():
    """Kill all VA windows/processes except ACE

    Also checks visible windows to ensure cleanup is complete.
    """
    killed_count = 0

    # First, try to capture desktop to see what's visible (optional - don't fail if NAS unavailable)
    try:
        from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture
        from screen_capture_system import ScreenCaptureSystem
        logger.info("📸 Attempting desktop screenshot (optional)...")
        screen_cap = ScreenCaptureSystem()
        screenshot_path = screen_cap.capture_screenshot("cleanup_check.png")
        logger.info(f"   Screenshot saved: {screenshot_path}")
    except Exception as e:
        logger.debug(f"Could not capture desktop (NAS may be unavailable): {e}")

    try:
        import psutil
    except ImportError:
        logger.warning("⚠️  psutil not available - using basic process killing")
        # Fallback to basic method
        try:
            import subprocess
            # Kill Python processes with VA-related window titles
            va_titles = [
                "JARVIS",
                "Kenny",
                "IMVA",
                "Ultron",
                "Ultimate Iron Man",
                "Virtual Assistant",
                "Desktop Assistant"
            ]
            for title in va_titles:
                try:
                    subprocess.run(
                        ['taskkill', '/F', '/FI', f'WINDOWTITLE eq *{title}*'],
                        capture_output=True,
                        timeout=2
                    )
                except:
                    pass
            logger.info("✅ Attempted to kill VA windows (basic method)")
            return
        except Exception as e:
            logger.error(f"❌ Could not kill processes: {e}")
            return

    current_pid = os.getpid()

    # VA process patterns to kill (but NOT ACE)
    va_patterns = [
        'jarvis_wandering',
        'jarvis_desktop_assistant',
        'kenny_imva_enhanced',
        'start_jarvis_wandering',
        'start_animated_vas_wandering',
        'start_kenny',
        'start_vas',
        'ultron_desktop_assistant',
        'ultimate_iron_man_desktop_assistant',
        'ironman_animated_va',
        'show_vas',
        'render_va_desktop_widgets',
        'ironman_virtual_assistant',
        'show_iron_man_vas',
        'show_jarvis_imva',
        'ensure_all_vas_visible'
    ]

    # Patterns that indicate ACE (should NOT kill)
    ace_patterns = [
        'armoury',
        'acva_armoury_crate',  # Our integration script is OK, but actual ACE process is from Armoury Crate
    ]

    logger.info("=" * 80)
    logger.info("🧹 CLEANING UP VA WINDOWS")
    logger.info("=" * 80)
    logger.info("   Keeping ACE (Armoury Crate - not our process)")
    logger.info("   Killing all other VA processes...")
    logger.info("")

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'exe']):
        try:
            # Skip current process
            if proc.info['pid'] == current_pid:
                continue

            # Only check Python processes
            if not proc.info['name'] or 'python' not in proc.info['name'].lower():
                continue

            cmdline = proc.info.get('cmdline', [])
            if not cmdline:
                continue

            cmdline_str = ' '.join(str(arg) for arg in cmdline).lower()

            # Check if this is a VA process (but not ACE)
            is_va_process = False
            for pattern in va_patterns:
                if pattern.lower() in cmdline_str:
                    is_va_process = True
                    break

            if is_va_process:
                # Double-check it's not ACE (ACE is from Armoury Crate, not our Python process)
                # Our acva_armoury_crate_integration.py script is OK to kill, but actual ACE window is from Armoury Crate
                is_ace = any(ace_pattern in cmdline_str for ace_pattern in ace_patterns)
                # Also check if it's the actual Armoury Crate executable (not Python)
                exe_path = proc.info.get('exe', '')
                if exe_path and ('armoury' in exe_path.lower() or 'asus' in exe_path.lower()):
                    is_ace = True

                if is_ace:
                    logger.info(f"   ⏭️  Skipping ACE (Armoury Crate process)")
                    continue

                logger.info(f"   🗑️  Killing: PID {proc.info['pid']} - {cmdline_str[:80]}")
                try:
                    proc.kill()
                    killed_count += 1
                except psutil.NoSuchProcess:
                    pass
                except psutil.AccessDenied:
                    logger.warning(f"   ⚠️  Access denied for PID {proc.info['pid']}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not kill PID {proc.info['pid']}: {e}")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
        except Exception as e:
            logger.debug(f"Error checking process: {e}")

    logger.info("")
    logger.info("=" * 80)
    logger.info(f"✅ Cleanup complete - killed {killed_count} VA process(es)")
    logger.info("   ACE is still running (as intended)")
    logger.info("=" * 80)

    return killed_count


def main():
    """Main cleanup function"""
    print("=" * 80)
    print("🧹 CLEANUP VA WINDOWS")
    print("=" * 80)
    print()
    print("This will kill all VA windows/processes EXCEPT ACE")
    print("(ACE is from Armoury Crate and should remain running)")
    print()

    killed = kill_va_windows()

    print()
    if killed > 0:
        print(f"✅ Killed {killed} VA process(es)")
    else:
        print("✅ No VA processes found to kill")
    print()
    print("ACE is still running (as intended)")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Cleanup cancelled")
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)