#!/usr/bin/env python3
"""
JARVIS Pin Collaboration Insight
Pin important insights about AI & Human collaboration

@JARVIS @CLEVER @AI @HUMAN @COLLAB @PIN @INSIGHT
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPinCollaboration")


class JARVISPinCollaborationInsight:
    """
    Pin Collaboration Insight System

    Pins important insights about AI & Human collaboration
    for future reference and reflection.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize pin system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Pinned insights directory
        self.pins_dir = self.project_root / "data" / "pinned_insights"
        self.pins_dir.mkdir(parents=True, exist_ok=True)

        # Master pins file
        self.master_pins_file = self.pins_dir / "master_pins.json"

        logger.info("✅ Pin Collaboration Insight System initialized")

    def pin_insight(
        self,
        insight: str,
        category: str = "collaboration",
        tags: Optional[list] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Pin an insight"""
        logger.info("=" * 70)
        logger.info("📌 PINNING INSIGHT")
        logger.info("=" * 70)
        logger.info("")

        pin_id = f"pin_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        pin_data = {
            "pin_id": pin_id,
            "insight": insight,
            "category": category,
            "tags": tags or [],
            "pinned_at": datetime.now().isoformat(),
            "metadata": metadata or {},
            "pinned_by": "JARVIS",
            "status": "pinned"
        }

        # Load existing pins
        pins = self._load_pins()

        # Add new pin
        pins["pins"].append(pin_data)
        pins["metadata"]["last_updated"] = datetime.now().isoformat()
        pins["metadata"]["total_pins"] = len(pins["pins"])

        # Save pins
        self._save_pins(pins)

        # Save individual pin file
        pin_file = self.pins_dir / f"{pin_id}.json"
        with open(pin_file, 'w', encoding='utf-8') as f:
            json.dump(pin_data, f, indent=2, default=str)

        logger.info(f"Pin ID: {pin_id}")
        logger.info(f"Insight: {insight}")
        logger.info(f"Category: {category}")
        logger.info(f"Tags: {', '.join(pin_data['tags'])}")
        logger.info(f"Pin file: {pin_file}")
        logger.info(f"Total pins: {pins['metadata']['total_pins']}")
        logger.info("")

        # Ingest to R5 if available
        try:
            from scripts.python.r5_living_context_matrix import R5LivingContextMatrix
            r5 = R5LivingContextMatrix(self.project_root)

            session_data = {
                "session_id": f"pinned_insight_{pin_id}",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {
                        "role": "user",
                        "content": f"Pinned insight: {insight}"
                    },
                    {
                        "role": "assistant",
                        "content": f"This insight has been pinned for future reference. Category: {category}"
                    }
                ],
                "metadata": {
                    "pin_id": pin_id,
                    "category": category,
                    "tags": pin_data["tags"],
                    "type": "pinned_insight"
                }
            }

            r5.ingest_session(session_data)
            logger.info("✅ Insight ingested to R5 Living Context Matrix")
        except Exception as e:
            logger.warning(f"⚠️  R5 not available: {e}")

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ INSIGHT PINNED")
        logger.info("=" * 70)

        return {
            "success": True,
            "pin_id": pin_id,
            "pin_data": pin_data,
            "pin_file": str(pin_file),
            "master_pins_file": str(self.master_pins_file)
        }

    def pin_collaboration_insight(self) -> Dict[str, Any]:
        """Pin the collaboration insight"""
        insight = "I suppose it all comes down to how @clever our @ai & @human @collab goes, eh?"

        return self.pin_insight(
            insight=insight,
            category="collaboration",
            tags=["@clever", "@ai", "@human", "@collab", "@pin", "@insight"],
            metadata={
                "source": "user_insight",
                "importance": "high",
                "philosophy": "ai_human_collaboration",
                "reflection": "Everything depends on the cleverness of AI and human collaboration"
            }
        )

    def _load_pins(self) -> Dict[str, Any]:
        """Load master pins file"""
        if self.master_pins_file.exists():
            try:
                with open(self.master_pins_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load pins: {e}")

        return {
            "pins": [],
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "total_pins": 0
            }
        }

    def _save_pins(self, pins: Dict[str, Any]) -> None:
        """Save master pins file"""
        try:
            with open(self.master_pins_file, 'w', encoding='utf-8') as f:
                json.dump(pins, f, indent=2, default=str)
            logger.info(f"✅ Master pins saved: {self.master_pins_file}")
        except Exception as e:
            logger.error(f"Failed to save pins: {e}")

    def get_all_pins(self) -> Dict[str, Any]:
        """Get all pinned insights"""
        return self._load_pins()

    def get_pins_by_category(self, category: str) -> list:
        """Get pins by category"""
        pins = self._load_pins()
        return [pin for pin in pins["pins"] if pin.get("category") == category]


def main():
    """Main execution"""
    print("=" * 70)
    print("📌 PINNING COLLABORATION INSIGHT")
    print("=" * 70)
    print()

    pinner = JARVISPinCollaborationInsight()
    result = pinner.pin_collaboration_insight()

    print()
    print("=" * 70)
    print("✅ INSIGHT PINNED")
    print("=" * 70)
    print(f"Pin ID: {result['pin_id']}")
    print(f"Insight: {result['pin_data']['insight']}")
    print(f"Category: {result['pin_data']['category']}")
    print(f"Tags: {', '.join(result['pin_data']['tags'])}")
    print(f"Pin File: {result['pin_file']}")
    print("=" * 70)
    print()
    print("💭 Reflection:")
    print("   Everything depends on how clever our AI & Human collaboration goes.")
    print("   This is now pinned for future reference.")
    print("=" * 70)


if __name__ == "__main__":


    main()