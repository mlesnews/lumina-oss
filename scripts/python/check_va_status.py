#!/usr/bin/env python3
"""
Check VA Status - Diagnostic Tool

Checks which VAs are running and visible on desktop.

Tags: #DIAGNOSTIC #VA #STATUS @JARVIS @LUMINA
"""

import sys
import subprocess
import psutil
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CheckVAStatus")


def check_running_processes():
    """Check which VA processes are running"""
    print("=" * 80)
    print("🔍 CHECKING RUNNING VA PROCESSES")
    print("=" * 80)
    print()

    va_scripts = {
        "JARVIS Narrator": "jarvis_narrator_avatar.py",
        "Kenny Avatar": "kenny_imva_enhanced.py",
        "ACE": "ace_control_bar.py",  # Or whatever ACE uses
        "VA Renderer": "render_va_desktop_widgets.py",
        "Notification Monitor": "cursor_notification_handler.py"
    }

    running = {}
    for name, script in va_scripts.items():
        script_path = script_dir / script
        if not script_path.exists():
            print(f"⚠️  {name}: Script not found ({script})")
            continue

        # Check for running Python processes with this script
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(str(script_path) in str(arg) for arg in cmdline):
                        running[name] = {
                            'pid': proc.info['pid'],
                            'cmdline': ' '.join(cmdline[:3])  # First few args
                        }
                        found = True
                        break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if not found:
            print(f"❌ {name}: Not running")
        else:
            print(f"✅ {name}: Running (PID: {running[name]['pid']})")

    print()
    return running


def check_registered_vas():
    """Check which VAs are registered"""
    print("=" * 80)
    print("📋 CHECKING REGISTERED VAs")
    print("=" * 80)
    print()

    try:
        registry = CharacterAvatarRegistry()
        all_chars = registry.get_all_characters()

        from character_avatar_registry import CharacterType
        vas = []
        for c in all_chars:
            if hasattr(c, 'character_type'):
                if (c.character_type == CharacterType.VIRTUAL_ASSISTANT or 
                    c.character_type == CharacterType.MINOR_CHARACTER):
                    # Also check if it has an avatar template (like Kenny)
                    if hasattr(c, 'avatar_template') and c.avatar_template:
                        vas.append(c)
                    elif c.character_type == CharacterType.VIRTUAL_ASSISTANT:
                        vas.append(c)

        print(f"Total VAs/Characters registered: {len(vas)}")
        print()
        for va in vas:
            print(f"  • {va.name} ({va.character_id})")
            print(f"    Type: {va.character_type.value}")
            print(f"    Avatar: {getattr(va, 'avatar_template', 'N/A')}")
            print()

        return vas
    except Exception as e:
        print(f"❌ Error checking registry: {e}")
        import traceback
        traceback.print_exc()
        return []


def check_widget_visibility():
    """Check if widgets are visible"""
    print("=" * 80)
    print("🖥️  CHECKING WIDGET VISIBILITY")
    print("=" * 80)
    print()

    try:
        from va_visibility_system import VAVisibilitySystem

        visibility = VAVisibilitySystem()
        widgets = visibility.viz.widgets

        print(f"Total widgets created: {len(widgets)}")
        print()

        visible_count = 0
        for widget_id, widget in widgets.items():
            status = "✅ Visible" if widget.visible else "❌ Hidden"
            if widget.visible:
                visible_count += 1
            print(f"  {status}: {widget.va_id} ({widget.widget_type.value})")

        print()
        print(f"Visible widgets: {visible_count}/{len(widgets)}")
        print()

        return widgets
    except Exception as e:
        print(f"❌ Error checking widgets: {e}")
        import traceback
        traceback.print_exc()
        return {}


def main():
    """Main diagnostic function"""
    print("=" * 80)
    print("🔍 LUMINA VA STATUS DIAGNOSTIC")
    print("=" * 80)
    print()

    # Check processes
    processes = check_running_processes()

    # Check registry
    vas = check_registered_vas()

    # Check widgets
    widgets = check_widget_visibility()

    # Summary
    print("=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print()
    print(f"Running processes: {len(processes)}")
    print(f"Registered VAs: {len(vas)}")
    print(f"Created widgets: {len(widgets)}")
    print()

    if len(processes) < 3:
        print("⚠️  WARNING: Not all expected processes are running!")
        print("   Expected: JARVIS Narrator, Kenny Avatar, VA Renderer")
        print()

    if len(widgets) == 0:
        print("⚠️  WARNING: No widgets created!")
        print("   Run: python startup_vas_with_armoury_crate.py")
        print()

    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()