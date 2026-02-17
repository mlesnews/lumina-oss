#!/usr/bin/env python3
"""
JARVIS GAZE SYNC Avatar Integration

Integrates GAZE SYNC system with avatar rendering for visual cues (iris twinkle).

Tags: #GAZE_SYNC #AVATAR_INTEGRATION #VISUAL_CUE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_gaze_sync_system import get_gaze_sync_system
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("GazeSyncAvatarIntegration")
    logger.warning(f"Import error: {e}")

logger = get_logger("GazeSyncAvatarIntegration")


def create_iris_twinkle_effect(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create iris twinkle effect for avatar

    Args:
        params: Effect parameters
            - duration: float (default: 0.5)
            - intensity: float (default: 0.3, subtle)
            - color: str (default: "#00D4FF" - JARVIS cyan)

    Returns:
        Effect configuration for avatar system
    """
    duration = params.get("duration", 0.5)
    intensity = params.get("intensity", 0.3)
    color = params.get("color", "#00D4FF")

    effect = {
        "type": "iris_twinkle",
        "duration": duration,
        "intensity": intensity,
        "color": color,
        "animation": "subtle_pulse",
        "repeat": 1
    }

    logger.info(f"✨ Created iris twinkle effect: {effect}")
    return effect


def integrate_gaze_sync_with_avatar(avatar_system=None):
    """
    Integrate GAZE SYNC system with avatar rendering

    Args:
        avatar_system: Avatar rendering system (optional)
    """
    logger.info("🔗 Integrating GAZE SYNC with avatar system...")

    # Get gaze sync system
    gaze_sync = get_gaze_sync_system()

    # Set up visual cue callback
    def iris_twinkle_callback(cue_type: str, params: Dict[str, Any]):
        """Callback for iris twinkle visual cue"""
        logger.info(f"✨ Triggering iris twinkle: {cue_type}")

        # Create effect
        effect = create_iris_twinkle_effect(params)

        # Apply to avatar system if available
        if avatar_system:
            try:
                # Integrate with avatar rendering
                # This is a placeholder - actual implementation depends on avatar system
                if hasattr(avatar_system, 'apply_effect'):
                    avatar_system.apply_effect(effect)
                elif hasattr(avatar_system, 'trigger_iris_twinkle'):
                    avatar_system.trigger_iris_twinkle(effect)
                else:
                    logger.warning("Avatar system doesn't support effect application")
            except Exception as e:
                logger.error(f"Error applying iris twinkle to avatar: {e}")
        else:
            logger.debug("Avatar system not provided - using default implementation")

    # Set up audible cue callback
    def chime_callback(cue_type: str, params: Dict[str, Any]):
        """Callback for JARVIS chime audible cue"""
        logger.info(f"🔔 Triggering JARVIS chime: {cue_type}")

        # Default implementation uses winsound
        try:
            import winsound
            frequency = params.get("frequency", 800)
            duration_ms = int(params.get("duration", 0.3) * 1000)

            # Two-tone ascending chime
            winsound.Beep(frequency, duration_ms // 2)
            import time
            time.sleep(0.05)
            winsound.Beep(int(frequency * 1.25), duration_ms // 2)
        except ImportError:
            logger.warning("winsound not available - chime not played")
        except Exception as e:
            logger.error(f"Error playing chime: {e}")

    # Set up flow state callback
    def flow_state_callback(state_info: Dict[str, Any]):
        """Callback for flow state detection"""
        logger.info(f"🌟 Flow state detected: {state_info}")
        # Can trigger additional visual/audible cues here

    # Set up control relinquish callback
    def control_relinquish_callback(control_info: Dict[str, Any]):
        """Callback for control relinquishing"""
        logger.info(f"🔄 Control relinquished: {control_info}")
        # Can update avatar state to show operator control

    # Register callbacks
    gaze_sync.set_visual_cue_callback(iris_twinkle_callback)
    gaze_sync.set_audible_cue_callback(chime_callback)
    gaze_sync.set_flow_state_callback(flow_state_callback)
    gaze_sync.set_control_relinquish_callback(control_relinquish_callback)

    logger.info("✅ GAZE SYNC integrated with avatar system")

    return gaze_sync


if __name__ == "__main__":
    # Example integration
    print("=" * 80)
    print("JARVIS GAZE SYNC AVATAR INTEGRATION")
    print("=" * 80)
    print()

    # Integrate (without avatar system for now)
    gaze_sync = integrate_gaze_sync_with_avatar()

    print("✅ Integration complete")
    print("   System is monitoring gaze sync...")
    print("   Visual and audible cues will trigger automatically")
    print()

    # Show status
    import time
    try:
        while True:
            status = gaze_sync.get_status()
            print(f"\rState: {status['state']} | Sync: {status['sync_duration_seconds']:.1f}s | Flow: {status['in_flow_state']}", end='')
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping...")
        gaze_sync.stop_monitoring()
