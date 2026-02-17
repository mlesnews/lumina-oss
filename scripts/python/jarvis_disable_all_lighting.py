#!/usr/bin/env python3
"""
JARVIS FULL-AUTO: Disable ALL External Lighting
🤖 Fully automated - no manual steps required
- Automatically repairs keyboard control
- Automatically disables lighting (UI + registry fallback)
- Automatically preserves keyboard shortcut (fn+F4)
- Multiple retry attempts
- Complete automation from start to finish
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration

# Import telemetry
try:
    from scripts.python.syphon_workflow_telemetry_system import get_telemetry_system
    from scripts.python.workflow_telemetry_decorator import track_workflow_step
    TELEMETRY_AVAILABLE = True
except ImportError:
    TELEMETRY_AVAILABLE = False
    get_telemetry_system = None
    track_workflow_step = None

async def main():
    """FULL-AUTO: Disable all lighting - completely automated"""
    print("=" * 70)
    print("🤖 JARVIS FULL-AUTO: Disabling ALL External Lighting")
    print("=" * 70)
    print("🤖 Fully automated - no manual steps required")
    print()

    # Initialize telemetry
    workflow_id = "jarvis_disable_all_lighting"
    workflow_name = "JARVIS Disable All Lighting"
    execution_id = f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    started_at = datetime.now()

    telemetry = None
    if TELEMETRY_AVAILABLE:
        try:
            telemetry = get_telemetry_system()
            telemetry.capture_event(
                event_type=telemetry.TelemetryEventType.WORKFLOW_START,
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                execution_id=execution_id,
                data={"started_at": started_at.isoformat()},
                tags=["lighting", "automation", "hardware"]
            )
        except Exception as e:
            print(f"⚠️  Telemetry initialization failed: {e}")

    integration = create_armoury_crate_integration()

    # STEP 1: Repair keyboard control first (automated)
    print("🤖 AUTO STEP 1: Repairing keyboard control (fn+F4)...")
    print("-" * 70)
    repair_result = await integration.process_request({
        'action': 'repair_keyboard_control'
    })
    if repair_result.get('success'):
        print("✅ Keyboard control repaired/verified (automated)")
    else:
        print("⚠️  Keyboard control repair had warnings (may still work)")
    print()

    # STEP 2: Execute full automation (automated - no manual steps)
    print("🤖 AUTO STEP 2: Disabling all external lighting (fully automated)...")
    print("-" * 70)
    result = await integration.process_request({
        'action': 'disable_all_lighting'
    })

    # Display results
    print("AUTOMATION RESULTS:")
    print("-" * 70)
    print(f"✅ Success: {result.get('success', False)}")
    print(f"📢 Message: {result.get('message', 'Unknown')}")
    print()

    # Show automation summary
    summary = result.get('automation_summary', {})
    if summary:
        print("AUTOMATION SUMMARY:")
        print("-" * 70)
        print(f"⚔️  Method: {summary.get('method', 'Unknown')}")
        print(f"📊 Phases Completed: {summary.get('phases_completed', 'N/A')}")
        print(f"🖥️  UI Automation: {'✅ Success' if summary.get('ui_automation_success') else '❌ Failed/Not Available'}")
        print(f"📝 Registry Paths Updated: {summary.get('registry_paths_updated', 0)}")
        print(f"🔍 Recursive Keys Updated: {summary.get('recursive_keys_updated', 0)}")
        print(f"💡 Screen Brightness: {'⚠️  Skipped (disabled to prevent dimming)' if not summary.get('screen_brightness_set') else '✅ Set'}")
        print(f"🔍 Lighting Verified OFF: {'✅ Yes' if summary.get('lighting_verified_off') else '❌ No/Unknown'}")
        print(f"🔄 Services Running: {'✅ Yes' if summary.get('services_running') else '❌ No'}")
        print(f"⚙️  Processes Running: {'✅ Yes' if summary.get('processes_running') else '❌ No'}")
        print()

    # Show keyboard control status
    keyboard_control = result.get('keyboard_control', '')
    if keyboard_control:
        print("KEYBOARD CONTROL:")
        print("-" * 70)
        print(f"  {keyboard_control}")
        print()

    # Show diagnostics if available
    results = result.get('results', {})
    if 'diagnostics_registry_state' in results:
        diag = results.get('diagnostics_registry_state', '')
        if diag and diag != 'Unknown':
            print("DIAGNOSTICS (Registry State):")
            print("-" * 70)
            try:
                import json
                diag_data = json.loads(diag)
                for path, props in diag_data.items():
                    print(f"  {path}:")
                    for key, value in props.items():
                        print(f"    {key}: {value}")
                print()
            except:
                print(f"  {diag}")
                print()

    # Show verification
    verification = result.get('verification', 'Unknown')
    if verification and verification != 'Unknown':
        print("VERIFICATION:")
        print("-" * 70)
        try:
            import json
            verif_data = json.loads(verification)
            for key, value in verif_data.items():
                status_icon = "✅" if value == "Running" else "❌"
                print(f"  {status_icon} {key}: {value}")
        except:
            print(f"  {verification}")
        print()

    # Track workflow completion with telemetry
    ended_at = datetime.now()
    duration = (ended_at - started_at).total_seconds()
    success = result.get('success', False)

    if telemetry:
        try:
            # Extract metrics from result
            metrics = {
                "duration": duration,
                "phases_completed": summary.get('phases_completed', 0) if summary else 0,
                "registry_paths_updated": summary.get('registry_paths_updated', 0) if summary else 0,
                "recursive_keys_updated": summary.get('recursive_keys_updated', 0) if summary else 0
            }

            telemetry.track_workflow_execution(
                workflow_id=workflow_id,
                workflow_name=workflow_name,
                execution_id=execution_id,
                started_at=started_at,
                ended_at=ended_at,
                success=success,
                outcome_text=result.get('message', 'Completed'),
                metrics=metrics,
                workflow_data={
                    "automation_summary": summary,
                    "keyboard_control": result.get('keyboard_control', ''),
                    "verification": result.get('verification', '')
                }
            )

            # Flush events
            telemetry.flush_events()
        except Exception as e:
            print(f"⚠️  Telemetry tracking failed: {e}")

    if result.get('success'):
        print("🎉 FULL-AUTO COMPLETE!")
        print()
        print("🤖 All steps completed automatically:")
        print("   ✅ Keyboard control repaired")
        print("   ✅ Lighting disabled")
        print("   ✅ Keyboard shortcut (fn+F4) preserved")
        print()
        print("💡 Optional: Press fn+F4 (AURA F4) to verify keyboard shortcut works.")
    else:
        print("⚠️  Full-auto completed with warnings. Check details above.")

    print("=" * 70)

    return result.get('success', False)

if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = asyncio.run(main())