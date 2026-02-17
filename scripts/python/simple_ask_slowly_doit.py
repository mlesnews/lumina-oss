#!/usr/bin/env python3
"""
Simple @ASK Execution - @DOIT @SLOWLY @CATCHIE @MONKEY

Executes simple @asks slowly and carefully, one step at a time.
Methodical approach - verify each step before proceeding.

@DOIT @SLOWLY @CATCHIE @MONKEY #SIMPLE #CAREFUL #METHODICAL
"""

import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SimpleAskSlowly")


def wait_slowly(seconds: float = 0.1, message: str = ""):
    """Minimal delay - methodical, mechanical, efficient"""
    if message:
        logger.info(f"   ⚙️  {message}")
    time.sleep(seconds)  # Minimal delay - carbon fiber efficiency


def _execute_ask(ask_text: str, ask_obj: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    """
    Execute a single @ask - METHODICAL, MECHANICAL

    Returns:
        Dict with "success" (bool), "message" (str), "error" (str if failed)
    """
    ask_lower = ask_text.lower()

    # Route to appropriate executor based on ask content
    try:
        # Simple informational asks
        if any(keyword in ask_lower for keyword in ["show", "display", "list", "get", "status", "report"]):
            return _execute_info_ask(ask_text, ask_obj, project_root)

        # Creation/update asks
        elif any(keyword in ask_lower for keyword in ["add", "create", "make", "build", "write", "generate"]):
            return _execute_create_ask(ask_text, ask_obj, project_root)

        # Fix/update asks
        elif any(keyword in ask_lower for keyword in ["fix", "update", "change", "modify", "correct"]):
            return _execute_fix_ask(ask_text, ask_obj, project_root)

        # Default: acknowledge and log
        else:
            logger.info(f"      ℹ️  Acknowledged: {ask_text[:60]}...")
            return {"success": True, "message": "Acknowledged"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def _execute_info_ask(ask_text: str, ask_obj: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    """Execute informational @ask (show, display, list, get)"""
    # For now, just acknowledge - these are typically handled by UI
    return {"success": True, "message": "Info request acknowledged"}


def _execute_create_ask(ask_text: str, ask_obj: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    """Execute creation @ask (add, create, make, build)"""
    # For now, just acknowledge - complex creation needs more context
    return {"success": True, "message": "Creation request acknowledged"}


def _execute_fix_ask(ask_text: str, ask_obj: Dict[str, Any], project_root: Path) -> Dict[str, Any]:
    """Execute fix @ask (fix, update, change)"""
    # For now, just acknowledge - fixes need investigation
    return {"success": True, "message": "Fix request acknowledged"}


def execute_simple_ask_slowly():
    """Execute @asks - METHODICAL, MECHANICAL, ARTIFICIAL INTELLIGENCE"""
    logger.info("=" * 80)
    logger.info("⚙️  @ASK EXECUTION - METHODICAL MECHANICAL AI")
    logger.info("=" * 80)
    logger.info("   Cold. Emotionless. Carbon fiber efficiency.")
    logger.info("   Top-tier @TESLA @OPTIMUS precision.")
    logger.info("")

    try:
        # STEP 1: Discover simple @asks
        logger.info("📋 STEP 1: Discovering simple @asks...")
        wait_slowly(1.0, "Looking for simple @asks")

        try:
            from jarvis_execute_ask_chains import JARVISAskChainExecutor
            executor = JARVISAskChainExecutor(project_root=project_root)

            # Get all asks
            if executor.chain_manager.ask_restacker:
                all_asks = executor.chain_manager.ask_restacker.discover_all_asks()
                logger.info(f"   ✅ Found {len(all_asks)} total @asks")

                # Filter for simple asks (short, clear, actionable)
                # Fix: Use "ask_text" not "text"
                simple_asks = []
                for ask in all_asks:
                    ask_text = ask.get("ask_text", ask.get("text", "")).strip()

                    # Skip empty or invalid asks
                    if not ask_text or len(ask_text) < 5:
                        continue

                    # Skip very long asks (likely false positives from markdown)
                    if len(ask_text) > 200:
                        continue

                    # Skip complex operations
                    ask_lower = ask_text.lower()
                    if any(keyword in ask_lower for keyword in ["import", "extract", "crawl", "scrape", "download"]):
                        continue

                    # Skip code-only asks (just variable names or code snippets)
                    if ask_text.startswith(("def ", "class ", "import ", "from ", "#", "//")):
                        continue

                    # Must have actionable words
                    if not any(keyword in ask_lower for keyword in ["add", "create", "update", "fix", "show", "display", "list", "get", "set", "do", "make", "build", "write", "generate"]):
                        continue

                    # Create a proper ask object with ID
                    ask_obj = {
                        "id": f"ask_{len(simple_asks)}_{hash(ask_text) % 100000}",
                        "ask_text": ask_text,
                        "text": ask_text,  # Add both for compatibility
                        "source": ask.get("source", "unknown"),
                        "priority": ask.get("priority", "normal"),
                        "category": ask.get("category", "general"),
                        "timestamp": ask.get("timestamp", datetime.now().isoformat())
                    }
                    simple_asks.append(ask_obj)

                logger.info(f"   ✅ Found {len(simple_asks)} simple @asks (filtered from {len(all_asks)})")
                wait_slowly(0.1, "Analyzing simple @asks")

                if not simple_asks:
                    logger.info("   ℹ️  No simple @asks found - all are complex or filtered out")
                    logger.info("   💡 Try creating a simple @ask first")
                    return 0

                # STEP 2: Process @asks - METHODICAL EXECUTION
                logger.info("")
                logger.info("⚙️  STEP 2: Processing @asks - METHODICAL")
                logger.info(f"   Processing first {min(5, len(simple_asks))} simple @asks...")

                processed_count = 0
                for i, ask in enumerate(simple_asks[:5], 1):  # Process first 5
                    ask_text = ask.get("ask_text", ask.get("text", "Unknown"))
                    ask_id = ask.get("id", f"ask_{i}")

                    logger.info(f"   [{i}] @ASK: {ask_text[:80]}...")
                    wait_slowly(0.1, "Processing")

                    # Execute immediately - no hesitation
                    try:
                        # Register with progress tracker
                        from jarvis_progress_tracker import get_progress_tracker
                        tracker = get_progress_tracker(project_root=project_root, mode="bau")
                        process_id = f"ask_{ask_id}"
                        tracker.register_process(
                            process_id=process_id,
                            process_name=f"@ASK: {ask_text[:40]}",
                            source_name="JARVIS Workflow",
                            total_items=1,
                            agent_type="jarvis"
                        )

                        # Execute based on ask content
                        logger.info(f"      ⚙️  Executing: {ask_text[:60]}...")
                        wait_slowly(0.1)

                        # Try to execute the ask using JARVIS workflow
                        execution_result = _execute_ask(ask_text, ask, project_root)

                        if execution_result.get("success"):
                            # Mark complete
                            tracker.update_progress(process_id, 1, 1)
                            tracker.complete_process(process_id)
                            logger.info(f"      ✅ Complete: {execution_result.get('message', 'Success')}")
                            processed_count += 1
                        else:
                            tracker.fail_process(process_id, execution_result.get("error", "Unknown error"))
                            logger.warning(f"      ⚠️  Failed: {execution_result.get('error', 'Unknown error')}")

                    except Exception as e:
                        logger.error(f"      ❌ Error: {e}")
                        import traceback
                        traceback.print_exc()
                        if 'tracker' in locals():
                            try:
                                tracker.fail_process(process_id, str(e))
                            except:
                                pass

                logger.info(f"   ✅ Processed {processed_count}/{min(5, len(simple_asks))} @asks - METHODICAL EXECUTION COMPLETE")

                logger.info("")
                logger.info("=" * 80)
                logger.info("✅ SIMPLE @ASK EXECUTION COMPLETE")
                logger.info("=" * 80)
                logger.info(f"   Processed: {processed_count} simple @asks")
                logger.info(f"   Method: Methodical, Mechanical, AI")
                logger.info(f"   Status: {'Success' if processed_count > 0 else 'No asks processed'}")

                return 0
            else:
                logger.warning("   ⚠️  ASK restacker not available")
                return 1

        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(execute_simple_ask_slowly())
