#!/usr/bin/env python3
"""
Store Memory: Military TLA Background and Acronym Preference

User background: 8 years active duty U.S. Air Force (20s-30s)
Preference: Heavy use of acronyms (TLAs - Three-Letter Acronyms)
This explains the communication style and acronym usage throughout the project.

Tags: #memory #background #military #TLA #acronyms #communication
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority

logger = get_logger("StoreMilitaryTLAMemory")

def main():
    """Store the military background and TLA preference memory"""
    try:
        project_root = Path(__file__).parent.parent.parent
        memory = JARVISPersistentMemory(project_root)

        content = """User Background: 8 years active duty U.S. Air Force (20s to 30s)

Communication Style: Heavy preference for acronyms, especially TLAs (Three-Letter Acronyms)

Context:
- Military background heavily influences communication style
- TLAs (Three-Letter Acronyms) are standard in military communication
- Acronyms are efficient, precise, and culturally familiar
- Examples: @AMP, @WOPR, @TLA, @DOIT, etc.

Implications:
- Acronym usage throughout codebase is intentional and preferred
- Should accommodate and support acronym-heavy communication
- Acronyms serve as both identifiers and cultural markers
- Documentation should explain acronyms but respect the preference

This explains:
- Why acronyms are used extensively in project
- Why systems are named with acronyms (@AMP, @WOPR, etc.)
- Why communication style favors brevity and precision
- Why military-style organization and terminology appears

Respect this communication preference - it's part of the user's professional identity and background."""

        memory_id = memory.store_memory(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.HIGH,
            context={
                "category": "user_background",
                "military_service": "8_years_active_duty_usaf",
                "age_range": "20s_to_30s",
                "communication_style": "TLA_preference",
                "cultural_marker": "military"
            },
            tags=[
                "military",
                "air_force",
                "usaf",
                "TLA",
                "acronyms",
                "communication_style",
                "user_background",
                "cultural_context",
                "8_years_active_duty"
            ],
            source="store_military_tla_preference_memory.py"
            )

        logger.info("=" * 80)
        logger.info("💾 MEMORY STORED: Military TLA Background")
        logger.info("=" * 80)
        logger.info(f"Memory ID: {memory_id}")
        logger.info("Content: 8 years active duty U.S. Air Force background")
        logger.info("Preference: Heavy use of TLAs (Three-Letter Acronyms)")
        logger.info("Priority: HIGH")
        logger.info("Type: LONG_TERM")
        logger.info("=" * 80)
        logger.info("")
        logger.info("✅ This explains the acronym-heavy communication style")
        logger.info("✅ JARVIS will remember and accommodate this preference")
        logger.info("✅ Acronym usage is intentional and culturally appropriate")
        logger.info("")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()