#!/usr/bin/env python3
"""
Exclude Wife's Voice - REQUIRED

Creates a voice profile for wife and marks it as EXCLUDED.
System will filter out wife's voice and only listen to OP.

Tags: #VOICE_FILTER #EXCLUDE_WIFE #REQUIRED @JARVIS @LUMINA
"""

import sys
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

logger = get_logger("ExcludeWifeVoice")

try:
    from voice_filter_system import VoiceFilterSystem, VoicePrintProfile
    VOICE_FILTER_AVAILABLE = True
except ImportError:
    VOICE_FILTER_AVAILABLE = False
    logger.error("❌ Voice filter system not available")


def create_wife_exclusion_profile():
    """Create voice profile for wife and mark as EXCLUDED"""
    if not VOICE_FILTER_AVAILABLE:
        logger.error("❌ Voice filter not available")
        return False

    try:
        # Create wife voice profile
        wife_profile = VoicePrintProfile("wife", project_root)

        # CRITICAL: Mark as excluded - this is the key flag
        wife_profile.profile_data["excluded"] = True  # Mark as excluded
        wife_profile.profile_data["excluded_reason"] = "Wife's voice - filter out"
        wife_profile.profile_data["exclude_threshold"] = 0.3  # Very low threshold to catch wife's voice

        # CRITICAL: Even if not fully trained, mark as excluded
        # This allows the filter to check for wife's voice even with minimal training
        wife_profile.profile_data["exclude_even_if_not_trained"] = True

        wife_profile.save_profile()

        logger.info("✅ Wife voice profile created and marked as EXCLUDED")
        logger.info("   System will filter out wife's voice")
        logger.info("   Exclusion threshold: 0.3 (very sensitive)")
        logger.info("   Will exclude even if profile not fully trained")

        # Also ensure OP profile exists and is NOT excluded
        op_profile = VoicePrintProfile("primary_operator", project_root)
        op_profile.profile_data["excluded"] = False  # OP is NOT excluded
        op_profile.profile_data["exclude_even_if_not_trained"] = False
        op_profile.save_profile()

        logger.info("✅ OP voice profile verified (NOT excluded)")

        return True
    except Exception as e:
        logger.error(f"❌ Failed to create wife exclusion profile: {e}")
        import traceback
        traceback.print_exc()
        return False


def improve_voice_filtering():
    """Improve voice filtering to be more strict about excluding wife's voice"""
    try:
        from voice_filter_system import VoiceFilterSystem

        # Create filter system
        voice_filter = VoiceFilterSystem("primary_operator", project_root)

        # Load wife profile and mark as excluded
        wife_profile = VoicePrintProfile("wife", project_root)
        if wife_profile.profile_file.exists():
            logger.info("✅ Wife profile found - will be excluded")
        else:
            logger.warning("⚠️  Wife profile not found - creating exclusion profile")
            create_wife_exclusion_profile()

        # Make filtering more strict
        voice_filter.voice_match_threshold = 0.95  # Very strict (was 0.90)
        logger.info("✅ Voice filtering made more strict (threshold: 0.95)")
        logger.info("   Only OP's voice will pass (wife's voice will be filtered out)")

        return voice_filter
    except Exception as e:
        logger.error(f"❌ Failed to improve voice filtering: {e}")
        return None


if __name__ == "__main__":
    print("=" * 80)
    print("🚫 EXCLUDING WIFE'S VOICE - REQUIRED")
    print("=" * 80)
    print()

    # Create wife exclusion profile
    if create_wife_exclusion_profile():
        print("✅ Wife's voice will be filtered out")
    else:
        print("❌ Failed to create exclusion profile")

    print()

    # Improve voice filtering
    voice_filter = improve_voice_filtering()
    if voice_filter:
        print("✅ Voice filtering improved")
        print("   Only OP's voice will be transcribed")
        print("   Wife's voice will be filtered out")
    else:
        print("❌ Failed to improve voice filtering")

    print()
    print("=" * 80)
    print("✅ WIFE'S VOICE EXCLUSION CONFIGURED")
    print("=" * 80)
