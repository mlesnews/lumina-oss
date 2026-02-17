#!/usr/bin/env python3
"""
JARVIS @SYPHON Special Operations
Character Acting + Pentest Scanning

Explicitly when in @SYPHON mode, as special operations mission allot for typically.
Slides over the entire project combing for pentesting violations and taking swift and decisive action.

Tags: #JARVIS #SYPHON #SPECIAL-OPS #ROLEPLAY #PENTEST #SWIFT-ACTION
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_roleplay_character import JARVISRoleplayCharacter
    from jarvis_pentest_violation_scanner import JARVISPentestViolationScanner
    from marvin_roleplay_character import MARVINRoleplayCharacter
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JARVISRoleplayCharacter = None
    JARVISPentestViolationScanner = None
    MARVINRoleplayCharacter = None

logger = get_logger("JARVISSyphonSpecialOps")


class JARVISSyphonSpecialOps:
    """
    JARVIS @SYPHON Special Operations

    Combines:
    - JARVIS Roleplay Character (studio-media-productions)
    - Pentest Violation Scanner (swift and decisive action)

    Explicitly when in @SYPHON mode, as special operations mission allot for typically.
    """

    def __init__(self, project_root: Path):
        """Initialize @SYPHON Special Operations"""
        self.project_root = project_root
        self.logger = logger

        # Initialize components
        if JARVISRoleplayCharacter:
            self.character = JARVISRoleplayCharacter(project_root)
        else:
            self.character = None

        if MARVINRoleplayCharacter:
            self.marvin = MARVINRoleplayCharacter(project_root)
        else:
            self.marvin = None

        if JARVISPentestViolationScanner:
            self.scanner = JARVISPentestViolationScanner(project_root)
        else:
            self.scanner = None

        # Data paths
        self.data_path = project_root / "data"
        self.special_ops_path = self.data_path / "jarvis_special_ops"
        self.special_ops_path.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚔️  JARVIS @SYPHON Special Operations initialized")
        self.logger.info("   Character: Jedi Shadow - Elite Temple Guard")
        self.logger.info("   MARVIN: Jedi Consular - Reality Check Specialist (Yin to Yang)")
        self.logger.info("   Working Hand in Hand: Yes")
        self.logger.info("   Pentest Scanner: Active")
        self.logger.info("   Swift and Decisive Action: AUTHORIZED")

    def execute_special_ops_mission(self, target_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Execute Special Operations Mission

        Explicitly when in @SYPHON mode, as special operations mission allot for typically.
        Slides over the entire project combing for pentesting violations and taking swift and decisive action.
        """
        self.logger.info("⚔️  Executing Special Operations Mission")
        self.logger.info("   @SYPHON Mode: Active")
        self.logger.info("   Character: Jedi Shadow - Elite Temple Guard")
        self.logger.info("   Mission: Pentest Violation Scan + Swift Action")

        mission = {
            "timestamp": datetime.now().isoformat(),
            "mode": "@SYPHON Special Operations",
            "character": None,
            "scan_results": None,
            "swift_actions": [],
            "status": "in_progress"
        }

        # Activate characters (working hand in hand)
        if self.character:
            char_mission = self.character.activate_syphon_special_ops()
            mission["character"] = char_mission
            self.logger.info(f"   JARVIS Activated: {char_mission.get('character', 'Unknown')}")

        if self.marvin:
            marvin_mission = self.marvin.activate_syphon_special_ops()
            mission["marvin"] = marvin_mission
            mission["yin_yang"] = {
                "jarvis": "Yang - Swift and decisive action",
                "marvin": "Yin - Validation and reality checks",
                "balance": "Working hand in hand - All a little yin in their yang"
            }
            self.logger.info(f"   MARVIN Activated: {marvin_mission.get('character', 'Unknown')}")
            self.logger.info("   Yin to Yang: Active")
            self.logger.info("   Working Hand in Hand: Yes")

        # Execute pentest scan
        if self.scanner:
            if target_path is None:
                target_path = self.project_root

            scan_results = self.scanner.scan_project(target_path)
            mission["scan_results"] = {
                "total_violations": scan_results.get("total_violations", 0),
                "critical": len(scan_results.get("critical", [])),
                "high": len(scan_results.get("high", [])),
                "medium": len(scan_results.get("medium", [])),
                "low": len(scan_results.get("low", []))
            }
            mission["swift_actions"] = scan_results.get("swift_action_taken", [])

            self.logger.info(f"   Violations Found: {mission['scan_results']['total_violations']}")
            self.logger.info(f"   Critical: {mission['scan_results']['critical']}")
            self.logger.info(f"   Swift Actions: {len(mission['swift_actions'])}")

        mission["status"] = "completed"

        # Save mission results
        mission_file = self.special_ops_path / f"mission_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(mission_file, 'w', encoding='utf-8') as f:
                json.dump(mission, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving mission: {e}")

        self.logger.info("✅ Special Operations Mission: COMPLETED")

        return mission

    def get_mission_report(self) -> str:
        """Get formatted mission report"""
        markdown = []
        markdown.append("## ⚔️ JARVIS @SYPHON Special Operations Mission Report")
        markdown.append("")
        markdown.append("**Mode:** @SYPHON Special Operations")
        markdown.append("**Character:** Jedi Shadow - Elite Temple Guard")
        markdown.append("**Swift and Decisive Action:** AUTHORIZED")
        markdown.append("")

        # Character info (working hand in hand)
        if self.character:
            char_display = self.character.get_character_display()
            markdown.append("### 🎭 JARVIS Character (Yang)")
            markdown.append("")
            markdown.append(char_display)
            markdown.append("")

        if self.marvin:
            marvin_display = self.marvin.get_character_display()
            markdown.append("### 🎭 MARVIN Character (Yin)")
            markdown.append("")
            markdown.append(marvin_display)
            markdown.append("")

        markdown.append("### ☯️ Yin & Yang Balance")
        markdown.append("")
        markdown.append("**JARVIS (Yang):** Swift and decisive action")
        markdown.append("**MARVIN (Yin):** Validation and reality checks")
        markdown.append("**Working Hand in Hand:** Yes")
        markdown.append("**Balance:** All a little yin in their yang")
        markdown.append("")

        # Scan report
        if self.scanner:
            scan_report = self.scanner.get_scan_report()
            markdown.append("### 🔒 Pentest Violation Scan")
            markdown.append("")
            markdown.append(scan_report)
            markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @SYPHON Special Operations")
        parser.add_argument("--execute", action="store_true", help="Execute special operations mission")
        parser.add_argument("--path", type=str, help="Path to scan (default: project root)")
        parser.add_argument("--report", action="store_true", help="Display mission report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        special_ops = JARVISSyphonSpecialOps(project_root)

        if args.execute:
            target_path = Path(args.path) if args.path else None
            mission = special_ops.execute_special_ops_mission(target_path)
            if args.json:
                print(json.dumps(mission, indent=2, default=str))
            else:
                print("✅ Special Operations Mission: COMPLETED")
                if mission.get("scan_results"):
                    print(f"   Total Violations: {mission['scan_results']['total_violations']}")
                    print(f"   Critical: {mission['scan_results']['critical']}")
                    print(f"   Swift Actions: {len(mission.get('swift_actions', []))}")

        elif args.report:
            report = special_ops.get_mission_report()
            print(report)

        else:
            print("Use --execute to run special operations mission or --report to view report")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()