#!/usr/bin/env python3
"""
SYPHON Reality Processor - Process Data Through Two Simulated Worlds

Feed data into SYPHON, process through two simulated worlds that mirror our own.
Apply RAID 0 mirroring logic to keep realities in sync.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from syphon.core import SYPHONSystem, SYPHONConfig
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None

try:
    from reality_mirror_sync import RealityMirrorSync, RealityType
    REALITY_SYNC_AVAILABLE = True
except ImportError:
    REALITY_SYNC_AVAILABLE = False
    RealityMirrorSync = None
    RealityType = None

try:
    from deep_thought import DeepThought
    DEEP_THOUGHT_AVAILABLE = True
except ImportError:
    DEEP_THOUGHT_AVAILABLE = False
    DeepThought = None

logger = get_logger("SYPHONRealityProcessor")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SYPHONRealityProcessor:
    """
    SYPHON Reality Processor

    Process data through two simulated worlds that mirror our own.
    Apply RAID 0 mirroring logic to keep realities in sync.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON Reality Processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SYPHONRealityProcessor")

        # Initialize SYPHON
        self.syphon = None
        if SYPHON_AVAILABLE and SYPHONSystem:
            try:
                config = SYPHONConfig(project_root=self.project_root)
                self.syphon = SYPHONSystem(config)
                self.logger.info("  ✅ SYPHON system initialized")
            except Exception as e:
                self.logger.debug(f"  SYPHON init error: {e}")

        # Initialize Reality Mirror Sync
        self.reality_sync = RealityMirrorSync(project_root) if REALITY_SYNC_AVAILABLE and RealityMirrorSync else None

        # Initialize Deep Thought
        self.deep_thought = DeepThought(project_root) if DEEP_THOUGHT_AVAILABLE and DeepThought else None

        self.logger.info("🌐 SYPHON Reality Processor initialized")
        self.logger.info("   Two simulated worlds, like RAID 0 mirroring")
        self.logger.info("   Processing data through realities")

    def process_through_realities(self, data: Dict[str, Any], 
                                  source: str = "session_summary") -> Dict[str, Any]:
        """
        Process data through two simulated worlds

        Args:
            data: Data to process
            source: Source identifier

        Returns:
            Processed result with reality sync status
        """
        self.logger.info(f"  🌐 Processing data through realities...")
        self.logger.info(f"     Source: {source}")

        # Process through SYPHON first
        syphon_result = None
        if self.syphon:
            try:
                # Extract data through SYPHON
                extraction_result = self.syphon.extract_data(
                    source_type="custom",
                    source_data=data
                )
                syphon_result = {
                    "extracted": True,
                    "data_points": len(extraction_result.data_points) if extraction_result else 0,
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"  ✅ SYPHON extraction complete")
            except Exception as e:
                self.logger.debug(f"  SYPHON extraction error: {e}")
                syphon_result = {"extracted": False, "error": str(e)}

        # Create two realities (like RAID 0 mirrors)
        control_reality_data = {
            "source": source,
            "data": data,
            "syphon_result": syphon_result,
            "reality_type": "control",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "processed_by": "SYPHON",
                "reality_id": "control_reality"
            }
        }

        experiment_reality_data = {
            "source": source,
            "data": data,
            "syphon_result": syphon_result,
            "reality_type": "experiment",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "processed_by": "SYPHON",
                "reality_id": "experiment_reality",
                "experimental": True
            }
        }

        # Register realities
        if self.reality_sync:
            control_state = self.reality_sync.register_reality(
                "control_reality",
                control_reality_data,
                RealityType.CONTROL
            )

            experiment_state = self.reality_sync.register_reality(
                "experiment_reality",
                experiment_reality_data,
                RealityType.EXPERIMENT
            )

            # Compare realities
            diffs = self.reality_sync.compare_realities()

            # Determine which is in sync
            control_reality = self.reality_sync.determine_control_reality()

            # Deep Thought analysis
            deep_thought_analysis = None
            if self.deep_thought:
                reality_context = {
                    "realities": {
                        "control": control_state.to_dict(),
                        "experiment": experiment_state.to_dict()
                    },
                    "sync_diffs": [d.to_dict() for d in diffs],
                    "control_reality": control_reality
                }
                deep_thought_analysis = self.deep_thought.analyze_realities(reality_context)

            return {
                "processed": True,
                "source": source,
                "control_reality": control_state.to_dict(),
                "experiment_reality": experiment_state.to_dict(),
                "sync_diffs": [d.to_dict() for d in diffs],
                "control_determined": control_reality,
                "deep_thought_analysis": deep_thought_analysis.to_dict() if deep_thought_analysis else None,
                "syphon_result": syphon_result,
                "timestamp": datetime.now().isoformat()
            }

        return {
            "processed": False,
            "error": "Reality sync not available",
            "syphon_result": syphon_result
        }

    def sync_realities(self) -> Dict[str, Any]:
        """Sync the two realities using RAID-like logic"""
        if not self.reality_sync:
            return {"success": False, "error": "Reality sync not available"}

        self.logger.info("  🔄 Syncing realities...")
        result = self.reality_sync.sync_realities()

        return result

    def get_status(self) -> Dict[str, Any]:
        """Get processor status"""
        return {
            "syphon_available": self.syphon is not None,
            "reality_sync_available": self.reality_sync is not None,
            "deep_thought_available": self.deep_thought is not None,
            "reality_sync_status": self.reality_sync.get_status() if self.reality_sync else None,
            "deep_thought_status": self.deep_thought.get_status() if self.deep_thought else None
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SYPHON Reality Processor")
    parser.add_argument("--process", type=str, help="Process data (JSON file or 'session_summary')")
    parser.add_argument("--sync", action="store_true", help="Sync realities")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    processor = SYPHONRealityProcessor()

    if args.process:
        if args.process == "session_summary":
            # Load session summary
            summary_file = processor.project_root / "docs" / "system" / "SESSION_SUMMARY_20251227.md"
            if summary_file.exists():
                data = {
                    "type": "session_summary",
                    "content": summary_file.read_text(encoding='utf-8'),
                    "source": "session_summary_20251227"
                }
            else:
                data = {"type": "session_summary", "content": "Summary not found", "source": "session_summary_20251227"}
        else:
            # Load JSON file
            data = json.loads(Path(args.process).read_text())

        result = processor.process_through_realities(data, source=args.process)

        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🌐 SYPHON Reality Processing Result")
            print(f"   Processed: {result.get('processed', False)}")
            if result.get('control_determined'):
                print(f"   Control Reality: {result['control_determined']}")
            if result.get('sync_diffs'):
                print(f"   Sync Diffs: {len(result['sync_diffs'])}")
            if result.get('deep_thought_analysis'):
                print(f"   Deep Thought Answer: {result['deep_thought_analysis']['answer'][:100]}...")

    elif args.sync:
        result = processor.sync_realities()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🔄 Sync Result: {result.get('message', 'N/A')}")

    elif args.status:
        status = processor.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🌐 SYPHON Reality Processor Status")
            print(f"   SYPHON: {'✅' if status['syphon_available'] else '❌'}")
            print(f"   Reality Sync: {'✅' if status['reality_sync_available'] else '❌'}")
            print(f"   Deep Thought: {'✅' if status['deep_thought_available'] else '❌'}")

    else:
        parser.print_help()
        print("\n🌐 SYPHON Reality Processor")
        print("   Process data through two simulated worlds")
        print("   Apply RAID 0 mirroring logic to realities")

