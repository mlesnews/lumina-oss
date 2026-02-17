#!/usr/bin/env python3
"""
Store MDV Usage Status in Persistent Memory

Stores information about whether MDV (MANUS Desktop Videofeed) is being used in the system.

IMPORTANT: MDV = MANUS Desktop Videofeed (NOT markdown viewer)

Tags: #MDV #MANUS #DESKTOP_VIDEOFEED #PERSISTENT_MEMORY @JARVIS @LUMINA
"""

import contextlib
import logging
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("StoreMDVMemory")


@contextlib.contextmanager
def safe_operation(operation_name: str) -> Generator[None, None, None]:
    """Context manager for safe operations with cleanup and logging"""
    try:
        logger.info(f"Starting: {operation_name}")
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info(f"Completed: {operation_name}")


def validate_file_path(path: Path, must_exist: bool = False) -> bool:
    try:
        """Validate file path before use with proper error messages"""
        if not isinstance(path, Path):
            path = Path(path)
        if must_exist and not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not must_exist and path.exists():
            raise FileExistsError(f"File already exists: {path}")
        return True


    except Exception as e:
        logger.error(f"Error in validate_file_path: {e}", exc_info=True)
        raise
def validate_input(value: Any, expected_type: type, param_name: str) -> bool:
    """Validate input parameters with proper type checking"""
    if not isinstance(value, expected_type):
        raise TypeError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")
    return True

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_persistent_memory import JARVISPersistentMemory, MemoryPriority, MemoryType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("StoreMDVMemory")


def check_mdv_usage() -> Dict[str, Any]:
    """Check if MDV (MANUS Desktop Videofeed) is being used in the system"""
    # MDV = MANUS Desktop Videofeed (not markdown viewer)

    with safe_operation("check_mdv_usage"):
        # Check for MDV-related scripts
        mdv_scripts = [
            "jarvis_mdv_conference_call.py",
            "jarvis_auto_mdv_activator.py",
            "jarvis_mdv_accessibility_enhancements.py"
        ]

        mdv_scripts_found = []
        for script_name in mdv_scripts:
            script_path = script_dir / script_name
            try:
                if script_path.exists():
                    mdv_scripts_found.append(script_name)
            except (OSError, PermissionError) as e:
                logger.warning(f"Could not check script path {script_path}: {e}")

        # Check if MDV functionality is imported/used
        mdv_used = len(mdv_scripts_found) > 0

        # Check if MANUS systems are available
        manus_available = False
        try:
            # Check for MANUS-related imports
            manus_rdp = script_dir / "manus_rdp_capture.py"
            manus_unified = script_dir / "manus_unified_control.py"
            manus_vision = script_dir / "manus_vision_control.py"
            if any(p.exists() for p in [manus_rdp, manus_unified, manus_vision]):
                manus_available = True
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not check MANUS systems: {e}")

        return {
            "mdv_scripts_found": mdv_scripts_found,
            "mdv_scripts_count": len(mdv_scripts_found),
            "manus_available": manus_available,
            "currently_used": mdv_used
        }


def store_mdv_usage_memory() -> Optional[str]:
    """Store MDV usage status in persistent memory"""
    with safe_operation("store_mdv_usage_memory"):
        print("=" * 80)
        print("💾 STORING MDV USAGE STATUS IN PERSISTENT MEMORY")
        print("=" * 80)
        print()

        # Check MDV usage
        mdv_status = check_mdv_usage()

        print("📊 MDV (MANUS Desktop Videofeed) Status Check:")
        print(f"   MDV Scripts Found: {mdv_status['mdv_scripts_count']}")
        for script in mdv_status['mdv_scripts_found']:
            print(f"      ✅ {script}")
        print(f"   MANUS Systems Available: {'✅ YES' if mdv_status['manus_available'] else '❌ NO'}")
        print(f"   Currently Used: {'✅ YES' if mdv_status['currently_used'] else '❌ NO'}")
        print()

        # Validate project_root
        validate_input(project_root, Path, "project_root")

        # Store in persistent memory
        memory_system = None
        try:
            memory_system = JARVISPersistentMemory(project_root)
        except (ImportError, OSError, PermissionError) as e:
            logger.error(f"Failed to initialize persistent memory: {e}")
            print(f"❌ Error initializing memory system: {e}")
            return None

        memory_content = f"""MDV (MANUS Desktop Videofeed) Usage Status

IMPORTANT: MDV = MANUS Desktop Videofeed (NOT markdown viewer)

Current Status:
- MDV Scripts Found: {mdv_status['mdv_scripts_count']}
  {chr(10).join(f'  • {script}' for script in mdv_status['mdv_scripts_found'])}
- MANUS Systems Available: {'YES' if mdv_status['manus_available'] else 'NO'}
- Currently Used in System: {'YES' if mdv_status['currently_used'] else 'NO'}

Question: Are we using @mdv (MANUS Desktop Videofeed)?

Answer: {'YES - MDV (MANUS Desktop Videofeed) is implemented and available in the system' if mdv_status['currently_used'] else 'NO - MDV (MANUS Desktop Videofeed) is not currently being used in the system'}

MDV Scripts:
{chr(10).join(f'- {script}' for script in mdv_status['mdv_scripts_found'])}

Note: User asked about @mdv usage and requested this be stored in persistent memory with CRITICAL importance (+++++).
"""

        memory_id = None
        try:
            memory_id = memory_system.store_memory(
                memory_type=MemoryType.LONG_TERM,
                priority=MemoryPriority.CRITICAL,  # 5/5 importance (+++++)
                content=memory_content,
                context={
                    "mdv_status": mdv_status,
                    "check_timestamp": str(datetime.now()),
                    "question": "Are we using @mdv?",
                    "importance": "CRITICAL (5/5 - +++++ persistent memory)"
                },
                tags=["mdv", "manus_desktop_videofeed", "manus", "desktop_videofeed", "user_question", "persistent_memory"],
                source="user_directive"
            )
        except (OSError, PermissionError, ValueError) as e:
            logger.error(f"Failed to store memory: {e}")
            print(f"❌ Error storing memory: {e}")
            return None

        print(f"✅ Memory stored with ID: {memory_id}")
        print("   Type: LONG_TERM")
        print("   Priority: CRITICAL (5/5 - +++++ importance)")
        print()

        # Verify storage
        try:
            memory = memory_system.retrieve_memory(memory_id)
            if memory:
                print("✅ Memory verification:")
                print(f"   ID: {memory.memory_id}")
                print(f"   Priority: {memory.priority.value} ({memory.priority.to_importance_rating()}/5)")
                print(f"   Tags: {', '.join(memory.tags)}")
                print()
            else:
                print("⚠️  Memory verification failed - memory not found")
                print()
        except (OSError, PermissionError, ValueError) as e:
            logger.warning(f"Could not verify memory storage: {e}")
            print(f"⚠️  Memory verification failed: {e}")
            print()

        # Summary
        print("=" * 80)
        print("SUMMARY")
        print("=" * 80)
        print(f"MDV Usage: {'✅ YES' if mdv_status['currently_used'] else '❌ NO'}")
        print("Memory Stored: ✅ YES (CRITICAL priority)")
        print("=" * 80)
        print()

        return memory_id


if __name__ == "__main__":
    """Main entry point with proper error handling"""
    try:
        result = store_mdv_usage_memory()
        if result:
            # Run twice as per original implementation
            result2 = store_mdv_usage_memory()
            sys.exit(0 if result2 else 1)
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        sys.exit(1)

    store_mdv_usage_memory()
    store_mdv_usage_memory()
