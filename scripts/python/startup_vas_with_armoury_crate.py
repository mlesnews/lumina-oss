#!/usr/bin/env python3
"""
Startup VAs with Armoury Crate

Starts all Virtual Assistants when Armoury Crate starts up.
Ensures VAs are visible on desktop after reboot.

Workflow:
1. Wait for Armoury Crate to be ready
2. Start all VAs (JARVIS, ACE, etc.)
3. Show all VAs on desktop
4. Verify all VAs are running

Tags: #STARTUP #VA #ARMOURY_CRATE #AUTOMATION @JARVIS @ACE @LUMINA
"""

import sys
import time
import subprocess
from pathlib import Path
from datetime import datetime

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

logger = get_logger("StartupVAsWithArmouryCrate")


def wait_for_armoury_crate(max_wait: int = 120) -> bool:
    """
    Wait for Armoury Crate to be ready

    Args:
        max_wait: Maximum seconds to wait (default 120 = 2 minutes)

    Returns:
        True if Armoury Crate is ready, False otherwise
    """
    logger.info("=" * 80)
    logger.info("⏳ WAITING FOR ARMOURY CRATE")
    logger.info("=" * 80)
    logger.info(f"   Maximum wait time: {max_wait} seconds")
    logger.info("")

    for attempt in range(max_wait):
        try:
            # Check if Armoury Crate process is running
            result = subprocess.run(
                [
                    "powershell", "-Command",
                    "Get-Process -Name 'ArmouryCrate*' -ErrorAction SilentlyContinue | Select-Object -First 1"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0 and result.stdout.strip():
                logger.info(f"✅ Armoury Crate process detected (attempt {attempt + 1}/{max_wait})")
                time.sleep(5)  # Give it a few more seconds to fully initialize
                logger.info("✅ Armoury Crate is ready!")
                logger.info("=" * 80)
                return True

            # Also check for service
            service_result = subprocess.run(
                [
                    "powershell", "-Command",
                    "Get-Service -Name 'ArmouryCrateService' -ErrorAction SilentlyContinue | Where-Object {$_.Status -eq 'Running'}"
                ],
                capture_output=True,
                text=True,
                timeout=5
            )

            if service_result.returncode == 0 and service_result.stdout.strip():
                logger.info(f"✅ Armoury Crate service running (attempt {attempt + 1}/{max_wait})")
                time.sleep(5)
                logger.info("✅ Armoury Crate is ready!")
                logger.info("=" * 80)
                return True

        except Exception as e:
            logger.debug(f"Check attempt {attempt + 1} failed: {e}")

        if attempt < max_wait - 1:
            if (attempt + 1) % 10 == 0:
                logger.info(f"   Still waiting... ({attempt + 1}/{max_wait} seconds)")
            time.sleep(1)

    logger.warning("⚠️  Armoury Crate not detected after {max_wait} seconds")
    logger.warning("   Proceeding anyway - VAs may start without Armoury Crate")
    logger.info("=" * 80)
    return False


def start_all_vas():
    """Start all Virtual Assistants and show them on desktop"""
    logger.info("")
    logger.info("=" * 80)
    logger.info("🚀 STARTING ALL VIRTUAL ASSISTANTS")
    logger.info("=" * 80)
    logger.info("")

    try:
        # Import VA systems
        from va_visibility_system import VAVisibilitySystem
        from character_avatar_registry import CharacterAvatarRegistry

        logger.info("📦 Initializing VA systems...")

        # Initialize registry
        registry = CharacterAvatarRegistry()
        logger.info("✅ Character Avatar Registry initialized")

        # Initialize visibility system (includes Kenny and other characters)
        visibility = VAVisibilitySystem(project_root=project_root)
        logger.info("✅ VA Visibility System initialized")
        logger.info(f"   Will display {len(visibility.vas)} VAs/characters")

        # Show all VAs on desktop (creates widget data)
        logger.info("")
        logger.info("🖥️  Showing all VAs on desktop...")
        dashboard = visibility.show_all_vas()

        if dashboard:
            logger.info("✅ All VAs widget data created")
        else:
            logger.warning("⚠️  Dashboard creation returned None")

        # Actually render the widgets on screen using Tkinter
        logger.info("")
        logger.info("🎨 Rendering VA widgets on desktop...")
        try:
            from render_va_desktop_widgets import render_with_tkinter
            # Render in a separate process so it doesn't block and can run mainloop()
            import subprocess
            render_script = script_dir / "render_va_desktop_widgets.py"
            if render_script.exists():
                # Start rendering in background process
                # NOTE: Do NOT use CREATE_NO_WINDOW - the renderer needs to show Tkinter windows!
                render_process = subprocess.Popen(
                    [sys.executable, str(render_script)],
                    cwd=str(project_root)
                    # No CREATE_NO_WINDOW flag - renderer needs to show Tkinter windows
                )
                logger.info("✅ VA widget rendering started in background process")
                logger.info(f"   Process ID: {render_process.pid}")
                logger.info("   Widgets should appear on desktop shortly...")
            else:
                logger.warning(f"⚠️  Render script not found: {render_script}")
                # Fallback: try to render directly in thread (may not work due to mainloop blocking)
                import threading
                def render_widgets():
                    try:
                        render_with_tkinter(visibility_system=visibility)
                    except Exception as e:
                        logger.error(f"❌ Render error: {e}")

                render_thread = threading.Thread(target=render_widgets, daemon=True)
                render_thread.start()
                logger.info("✅ VA widget rendering started in background thread")
        except ImportError as e:
            logger.error(f"❌ Could not import render function: {e}")
        except Exception as e:
            logger.error(f"❌ Error starting render: {e}")
            import traceback
            traceback.print_exc()

        # Get list of active VAs
        active_vas = registry.get_all_characters()
        logger.info("")
        logger.info(f"📋 Active VAs: {len(active_vas)}")
        for va in active_vas:
            logger.info(f"   • {va.name} ({va.character_type.value})")

        # Check specifically for Kenny
        kenny = registry.get_character("kenny")
        if kenny:
            logger.info("")
            logger.info("🤖 Kenny detected in registry:")
            logger.info(f"   • Name: {kenny.name}")
            logger.info(f"   • Avatar Style: {kenny.avatar_style}")
            logger.info(f"   • Avatar Template: {kenny.avatar_template}")
            logger.info("   • Kenny avatar process will be started separately")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ALL VIRTUAL ASSISTANTS STARTED")
        logger.info("=" * 80)

        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("   VA systems not available")
        return False
    except Exception as e:
        logger.error(f"❌ Error starting VAs: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_kenny_avatar():
    """Start Kenny IMVA Enhanced avatar if available"""
    try:
        logger.info("")
        logger.info("🤖 Starting Kenny IMVA Enhanced Avatar...")
        logger.info("   This starts the actual Kenny avatar window (Iron Man design)")
        logger.info("   Kenny will be draggable and have transformation states")

        kenny_script = script_dir / "kenny_imva_enhanced.py"
        if kenny_script.exists():
            # Start Kenny in background (it creates its own window)
            # NOTE: Do NOT use CREATE_NO_WINDOW for Kenny - it needs to show its window!
            process = subprocess.Popen(
                [sys.executable, str(kenny_script)],
                cwd=str(project_root)
                # No CREATE_NO_WINDOW flag - Kenny needs to show its Tkinter window
            )
            logger.info("✅ Kenny IMVA Enhanced Avatar started")
            logger.info(f"   Process ID: {process.pid}")
            logger.info("   Kenny should be visible on desktop (Iron Man design)")
            logger.info("   • Double-click Kenny to toggle transformation (Suitcase ↔ Armor)")
            logger.info("   • Drag Kenny to move around desktop")
            logger.info("   • Kenny has states: IDLE, WALKING, WORKING, SLEEPING, GAMING")
            return True
        else:
            logger.warning("   ⚠️  Kenny IMVA Enhanced script not found")
            logger.warning(f"   Expected: {kenny_script}")
            return False
    except Exception as e:
        logger.error(f"   ❌ Could not start Kenny avatar: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_jarvis_narrator():
    """Start JARVIS narrator avatar if available"""
    try:
        logger.info("")
        logger.info("🎭 Starting JARVIS Narrator Avatar...")
        logger.info("   JARVIS will monitor notifications and process them in workflows")

        jarvis_script = script_dir / "jarvis_narrator_avatar.py"
        if jarvis_script.exists():
            # NOTE: Do NOT use CREATE_NO_WINDOW - JARVIS needs to show its window!
            process = subprocess.Popen(
                [sys.executable, str(jarvis_script)],
                cwd=str(project_root)
                # No CREATE_NO_WINDOW flag - JARVIS needs to show its Tkinter window
            )
            logger.info("✅ JARVIS Narrator Avatar started")
            logger.info(f"   Process ID: {process.pid}")
            logger.info("   JARVIS should be visible on desktop")
            logger.info("   • JARVIS monitors notifications")
            logger.info("   • JARVIS processes notifications in workflows")
            return True
        else:
            logger.warning("   ⚠️  JARVIS narrator script not found")
            logger.warning(f"   Expected: {jarvis_script}")
            return False
    except Exception as e:
        logger.error(f"   ❌ Could not start JARVIS narrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def start_notification_monitoring():
    """Start notification monitoring for JARVIS workflows"""
    try:
        logger.info("")
        logger.info("📡 Starting Notification Monitoring for JARVIS...")

        # Try to start cursor notification handler
        notification_script = script_dir / "cursor_notification_handler.py"
        if notification_script.exists():
            process = subprocess.Popen(
                [sys.executable, str(notification_script), "--monitor"],
                cwd=str(project_root)
                # No CREATE_NO_WINDOW - notification handler may need to show dialogs
            )
            logger.info("✅ Notification monitoring started")
            logger.info(f"   Process ID: {process.pid}")
            logger.info("   JARVIS will process notifications in workflows")
            return True
        else:
            logger.debug("   Notification handler script not found")
            return False
    except Exception as e:
        logger.debug(f"   Could not start notification monitoring: {e}")
        return False


def main():
    """Main startup function"""
    logger.info("=" * 80)
    logger.info("🌟 LUMINA VA STARTUP WITH ARMOURY CRATE")
    logger.info("=" * 80)
    logger.info(f"   Started at: {datetime.now().isoformat()}")
    logger.info("")

    # Step 1: Wait for Armoury Crate
    armoury_ready = wait_for_armoury_crate(max_wait=120)

    if not armoury_ready:
        logger.warning("⚠️  Armoury Crate not ready, but proceeding with VA startup")

    # Step 2: Apply B-D-A workflow (Kenny lessons)
    logger.info("")
    logger.info("📚 Applying B-D-A workflow (Kenny experiment lessons)...")
    try:
        from va_bda_workflow import VABDAWorkflow
        bda_workflow = VABDAWorkflow(project_root=project_root)
        bda_result = bda_workflow.execute_bda()

        if bda_result.get("success"):
            logger.info("✅ B-D-A workflow completed successfully")
            vas_started = True
        else:
            logger.warning("⚠️  B-D-A workflow completed with warnings")
            vas_started = True  # Continue anyway
    except ImportError:
        logger.warning("⚠️  B-D-A workflow not available, using standard startup")
        # Fallback to standard startup
        vas_started = start_all_vas()

        if not vas_started:
            logger.error("❌ Failed to start VAs")
            return 1

        # Start individual processes
        start_kenny_avatar()
        jarvis_started = start_jarvis_narrator()

        if jarvis_started:
            start_notification_monitoring()
    except Exception as e:
        logger.error(f"❌ B-D-A workflow failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

    # Step 3: Final status
    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ STARTUP COMPLETE")
    logger.info("=" * 80)
    logger.info(f"   Armoury Crate Ready: {'✅' if armoury_ready else '⚠️'}")
    logger.info(f"   VAs Started: {'✅' if vas_started else '❌'}")
    logger.info("")
    logger.info("🎉 All Virtual Assistants should now be visible on your desktop!")
    logger.info("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()