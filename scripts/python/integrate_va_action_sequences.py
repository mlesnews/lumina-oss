#!/usr/bin/env python3
"""
Integrate Action Sequences into IM and AC Virtual Assistants

Adds comprehensive action sequence system with JARVIS/Lumina integration
to both Iron Man and Armory Crate virtual assistants.

Tags: #VA #INTEGRATION #JARVIS #LUMINA @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from va_action_sequence_system import VAActionSequenceSystem
from lumina_logger import get_logger

logger = get_logger("IntegrateVAActionSequences")


def integrate_action_sequences_im(va_instance):
    """
    Integrate action sequences into Iron Man virtual assistant

    Args:
        va_instance: IRONMANVirtualAssistant instance
    """
    try:
        # Initialize action sequence system
        va_instance.action_sequence_system = VAActionSequenceSystem(
            project_root=va_instance.project_root,
            va_type="ironman"
        )

        # Start action sequence system
        va_instance.action_sequence_system.start()

        logger.info("✅ Action sequences integrated into Iron Man VA")

        # Connect existing SYPHON enhancement to action sequence system
        if hasattr(va_instance, 'syphon') and va_instance.syphon:
            # Register SYPHON enhancement handler
            if "syphon_enhancement" in va_instance.action_sequence_system.sequences:
                seq = va_instance.action_sequence_system.sequences["syphon_enhancement"]
                # Override handler to use VA's existing SYPHON integration
                def enhanced_syphon_handler():
                    va_instance._syphon_enhancement_loop()
                seq.handler = enhanced_syphon_handler

        return True
    except Exception as e:
        logger.error(f"❌ Error integrating action sequences into IM VA: {e}")
        return False


def integrate_action_sequences_ac(va_instance):
    """
    Integrate action sequences into Armory Crate virtual assistant

    Args:
        va_instance: ACVirtualAssistant instance (or similar)
    """
    try:
        # Initialize action sequence system
        va_instance.action_sequence_system = VAActionSequenceSystem(
            project_root=va_instance.project_root,
            va_type="armory_crate"
        )

        # Start action sequence system
        va_instance.action_sequence_system.start()

        logger.info("✅ Action sequences integrated into Armory Crate VA")

        return True
    except Exception as e:
        logger.error(f"❌ Error integrating action sequences into AC VA: {e}")
        return False


def add_action_sequence_hooks_im(va_instance):
    """
    Add action sequence hooks to Iron Man VA methods

    Args:
        va_instance: IRONMANVirtualAssistant instance
    """
    # Store original methods
    original_wander = va_instance.start_wandering if hasattr(va_instance, 'start_wandering') else None
    original_animate = va_instance.start_animation if hasattr(va_instance, 'start_animation') else None

    # Wrap methods with action sequence integration
    if original_wander:
        def wrapped_wander():
            if hasattr(va_instance, 'action_sequence_system'):
                va_instance.action_sequence_system.enable_sequence("wandering")
            return original_wander()
        va_instance.start_wandering = wrapped_wander

    if original_animate:
        def wrapped_animate():
            if hasattr(va_instance, 'action_sequence_system'):
                va_instance.action_sequence_system.enable_sequence("animation")
            return original_animate()
        va_instance.start_animation = wrapped_animate


def main():
    """Main execution - demonstrate integration"""
    print("=" * 80)
    print("🔧 INTEGRATING ACTION SEQUENCES INTO VIRTUAL ASSISTANTS")
    print("=" * 80)
    print()

    # Test action sequence system
    print("📋 Testing action sequence system...")
    system = VAActionSequenceSystem(project_root, "ironman")

    print(f"✅ Initialized with {len(system.sequences)} sequences:")
    for seq_id, seq in system.sequences.items():
        print(f"   - {seq.name} ({seq.sequence_type.value}, priority: {seq.priority.value})")

    print()
    print("=" * 80)
    print("✅ INTEGRATION READY")
    print("=" * 80)
    print()
    print("To integrate into virtual assistants:")
    print("  1. Import: from integrate_va_action_sequences import integrate_action_sequences_im")
    print("  2. Call: integrate_action_sequences_im(va_instance)")
    print("  3. Action sequences will start automatically")


if __name__ == "__main__":


    main()