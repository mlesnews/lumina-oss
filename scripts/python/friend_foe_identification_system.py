#!/usr/bin/env python3
"""
Friend or Foe Identification System
Friendly/Green vs Enemy/Red Classification

IFF (Identify Friend or Foe) system for security classification.
Green = Friendly (safe, trusted, authorized)
Red = Enemy (threat, malicious, unauthorized)

Tags: #FRIEND-FOE #IFF #SECURITY #CLASSIFICATION #GREEN #RED
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FriendFoeIFF")


class FriendFoeStatus(Enum):
    """Friend or Foe Status"""
    FRIENDLY = "FRIENDLY"  # Green - Safe, trusted, authorized
    FOE = "FOE"  # Red - Threat, malicious, unauthorized
    UNKNOWN = "UNKNOWN"  # Yellow - Unidentified, needs analysis
    NEUTRAL = "NEUTRAL"  # Gray - Neither friend nor foe


class FriendFoeIdentificationSystem:
    """
    Friend or Foe Identification System

    IFF (Identify Friend or Foe) classification:
    - Green (FRIENDLY): Safe, trusted, authorized
    - Red (FOE): Threat, malicious, unauthorized
    - Yellow (UNKNOWN): Unidentified, needs analysis
    - Gray (NEUTRAL): Neither friend nor foe

    #INCEPTION: Classification at the level of a mote, a spec of dust.
    Friend or Foe reduced to the most fundamental scale.
    Are we there yet? Yes. We are at the mote level.
    """

    def __init__(self, project_root: Path):
        """Initialize Friend/Foe Identification System"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.iff_path = self.data_path / "friend_foe_iff"
        self.iff_path.mkdir(parents=True, exist_ok=True)

        # Classification files
        self.friendly_list_file = self.iff_path / "friendly_list.json"
        self.foe_list_file = self.iff_path / "foe_list.json"
        self.classification_file = self.iff_path / "classifications.json"

        # Load classifications
        self.friendly_list = self._load_friendly_list()
        self.foe_list = self._load_foe_list()
        self.classifications = self._load_classifications()

        self.logger.info("🟢🔴 Friend or Foe Identification System initialized")
        self.logger.info("   Green (FRIENDLY): Safe, trusted, authorized")
        self.logger.info("   Red (FOE): Threat, malicious, unauthorized")
        self.logger.info("   IFF System: Active")
        self.logger.info("   #INCEPTION: Classification at mote/spec-of-dust level")
        self.logger.info("   Scale: Reduced to fundamental particle level")

    def _load_friendly_list(self) -> List[Dict[str, Any]]:
        """Load friendly (green) list"""
        if self.friendly_list_file.exists():
            try:
                with open(self.friendly_list_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading friendly list: {e}")

        # Default friendly entities
        return [
            {
                "entity": "JARVIS",
                "type": "virtual_assistant",
                "status": "FRIENDLY",
                "color": "green",
                "reason": "Trusted system, authorized operations",
                "classification_date": datetime.now().isoformat()
            },
            {
                "entity": "MARVIN",
                "type": "virtual_assistant",
                "status": "FRIENDLY",
                "color": "green",
                "reason": "Validation system, reality checks",
                "classification_date": datetime.now().isoformat()
            },
            {
                "entity": "@SECTEAM",
                "type": "security_team",
                "status": "FRIENDLY",
                "color": "green",
                "reason": "Authorized security operations",
                "classification_date": datetime.now().isoformat()
            },
            {
                "entity": "@SYPHON",
                "type": "intelligence_system",
                "status": "FRIENDLY",
                "color": "green",
                "reason": "Authorized intelligence extraction",
                "classification_date": datetime.now().isoformat()
            }
        ]

    def _load_foe_list(self) -> List[Dict[str, Any]]:
        """Load foe (red) list"""
        if self.foe_list_file.exists():
            try:
                with open(self.foe_list_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading foe list: {e}")

        # Default foe patterns (threats)
        return [
            {
                "entity": "hardcoded_secrets",
                "type": "security_violation",
                "status": "FOE",
                "color": "red",
                "reason": "Critical security threat",
                "classification_date": datetime.now().isoformat()
            },
            {
                "entity": "sql_injection",
                "type": "security_violation",
                "status": "FOE",
                "color": "red",
                "reason": "Critical security threat",
                "classification_date": datetime.now().isoformat()
            },
            {
                "entity": "command_injection",
                "type": "security_violation",
                "status": "FOE",
                "color": "red",
                "reason": "Critical security threat",
                "classification_date": datetime.now().isoformat()
            }
        ]

    def _load_classifications(self) -> Dict[str, Any]:
        """Load classification rules"""
        if self.classification_file.exists():
            try:
                with open(self.classification_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading classifications: {e}")

        return {
            "rules": {
                "friendly_indicators": [
                    "authorized",
                    "trusted",
                    "validated",
                    "safe",
                    "approved"
                ],
                "foe_indicators": [
                    "malicious",
                    "unauthorized",
                    "threat",
                    "vulnerability",
                    "exploit"
                ]
            },
            "last_updated": datetime.now().isoformat()
        }

    def _save_friendly_list(self):
        """Save friendly list"""
        try:
            with open(self.friendly_list_file, 'w', encoding='utf-8') as f:
                json.dump(self.friendly_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving friendly list: {e}")

    def _save_foe_list(self):
        """Save foe list"""
        try:
            with open(self.foe_list_file, 'w', encoding='utf-8') as f:
                json.dump(self.foe_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving foe list: {e}")

    def identify_friend_or_foe(self, entity: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Identify if entity is friend or foe

        Args:
            entity: Entity to identify (name, process, file, etc.)
            context: Additional context for identification

        Returns:
            Classification result with status, color, and reason
        """
        self.logger.info(f"🔍 Identifying Friend or Foe: {entity}")

        # Check friendly list
        for friendly in self.friendly_list:
            if friendly["entity"].lower() == entity.lower():
                result = {
                    "entity": entity,
                    "status": FriendFoeStatus.FRIENDLY.value,
                    "color": "green",
                    "classification": "FRIENDLY",
                    "reason": friendly.get("reason", "On friendly list"),
                    "confidence": "high",
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"   🟢 FRIENDLY (Green): {entity}")
                return result

        # Check foe list
        for foe in self.foe_list:
            if foe["entity"].lower() in entity.lower() or entity.lower() in foe["entity"].lower():
                result = {
                    "entity": entity,
                    "status": FriendFoeStatus.FOE.value,
                    "color": "red",
                    "classification": "FOE",
                    "reason": foe.get("reason", "On foe list"),
                    "confidence": "high",
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"   🔴 FOE (Red): {entity}")
                return result

        # Analyze context if provided
        if context:
            friendly_indicators = self.classifications["rules"]["friendly_indicators"]
            foe_indicators = self.classifications["rules"]["foe_indicators"]

            context_str = str(context).lower()

            friendly_count = sum(1 for indicator in friendly_indicators if indicator in context_str)
            foe_count = sum(1 for indicator in foe_indicators if indicator in context_str)

            if friendly_count > foe_count:
                result = {
                    "entity": entity,
                    "status": FriendFoeStatus.FRIENDLY.value,
                    "color": "green",
                    "classification": "FRIENDLY",
                    "reason": f"Friendly indicators detected ({friendly_count})",
                    "confidence": "medium",
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"   🟢 FRIENDLY (Green): {entity} - Context analysis")
                return result
            elif foe_count > friendly_count:
                result = {
                    "entity": entity,
                    "status": FriendFoeStatus.FOE.value,
                    "color": "red",
                    "classification": "FOE",
                    "reason": f"Foe indicators detected ({foe_count})",
                    "confidence": "medium",
                    "timestamp": datetime.now().isoformat()
                }
                self.logger.info(f"   🔴 FOE (Red): {entity} - Context analysis")
                return result

        # Unknown
        result = {
            "entity": entity,
            "status": FriendFoeStatus.UNKNOWN.value,
            "color": "yellow",
            "classification": "UNKNOWN",
            "reason": "Not in friendly or foe list, insufficient context",
            "confidence": "low",
            "timestamp": datetime.now().isoformat()
        }
        self.logger.info(f"   🟡 UNKNOWN (Yellow): {entity}")
        return result

    def add_friendly(self, entity: str, entity_type: str, reason: str) -> Dict[str, Any]:
        """Add entity to friendly (green) list"""
        friendly = {
            "entity": entity,
            "type": entity_type,
            "status": "FRIENDLY",
            "color": "green",
            "reason": reason,
            "classification_date": datetime.now().isoformat()
        }
        self.friendly_list.append(friendly)
        self._save_friendly_list()
        self.logger.info(f"✅ Added to friendly list: {entity}")
        return friendly

    def add_foe(self, entity: str, entity_type: str, reason: str) -> Dict[str, Any]:
        """Add entity to foe (red) list"""
        foe = {
            "entity": entity,
            "type": entity_type,
            "status": "FOE",
            "color": "red",
            "reason": reason,
            "classification_date": datetime.now().isoformat()
        }
        self.foe_list.append(foe)
        self._save_foe_list()
        self.logger.info(f"✅ Added to foe list: {entity}")
        return foe

    def get_classification_summary(self) -> str:
        """Get formatted classification summary"""
        markdown = []
        markdown.append("## 🟢🔴 Friend or Foe Identification System")
        markdown.append("")
        markdown.append("**IFF System:** Active")
        markdown.append("")

        markdown.append("### 🟢 Friendly (Green)")
        markdown.append("")
        markdown.append(f"**Count:** {len(self.friendly_list)}")
        markdown.append("")
        for friendly in self.friendly_list[:10]:  # First 10
            markdown.append(f"✅ **{friendly['entity']}** ({friendly['type']})")
            markdown.append(f"   - Reason: {friendly.get('reason', 'N/A')}")
            markdown.append("")

        markdown.append("### 🔴 Foe (Red)")
        markdown.append("")
        markdown.append(f"**Count:** {len(self.foe_list)}")
        markdown.append("")
        for foe in self.foe_list[:10]:  # First 10
            markdown.append(f"❌ **{foe['entity']}** ({foe['type']})")
            markdown.append(f"   - Reason: {foe.get('reason', 'N/A')}")
            markdown.append("")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Friend or Foe Identification System")
        parser.add_argument("--identify", type=str, help="Identify entity as friend or foe")
        parser.add_argument("--add-friendly", type=str, help="Add entity to friendly list")
        parser.add_argument("--add-foe", type=str, help="Add entity to foe list")
        parser.add_argument("--type", type=str, help="Entity type (for add operations)")
        parser.add_argument("--reason", type=str, help="Reason (for add operations)")
        parser.add_argument("--summary", action="store_true", help="Display classification summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        iff = FriendFoeIdentificationSystem(project_root)

        if args.identify:
            result = iff.identify_friend_or_foe(args.identify)
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                status_icon = "🟢" if result["status"] == "FRIENDLY" else "🔴" if result["status"] == "FOE" else "🟡"
                print(f"{status_icon} {result['entity']}: {result['status']} ({result['color']})")
                print(f"   Reason: {result['reason']}")
                print(f"   Confidence: {result['confidence']}")

        elif args.add_friendly:
            if not args.reason:
                args.reason = "Manually added to friendly list"
            if not args.type:
                args.type = "unknown"
            friendly = iff.add_friendly(args.add_friendly, args.type, args.reason)
            if args.json:
                print(json.dumps(friendly, indent=2, default=str))
            else:
                print(f"✅ Added to friendly list: {args.add_friendly}")

        elif args.add_foe:
            if not args.reason:
                args.reason = "Manually added to foe list"
            if not args.type:
                args.type = "unknown"
            foe = iff.add_foe(args.add_foe, args.type, args.reason)
            if args.json:
                print(json.dumps(foe, indent=2, default=str))
            else:
                print(f"✅ Added to foe list: {args.add_foe}")

        elif args.summary:
            summary = iff.get_classification_summary()
            print(summary)

        else:
            summary = iff.get_classification_summary()
            print(summary)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()