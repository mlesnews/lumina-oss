#!/usr/bin/env python3
"""
JARVIS Literature & Media Interest System

Recognizes and supports the user's interest in reading new material,
viewing ANIMA and other styles of literature and media.

Tags: #LITERATURE #MEDIA #ANIMA #READING #INTERESTS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISLiterature")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISLiterature")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISLiterature")


class LiteratureMediaInterest:
    """Track and support literature and media interests"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "literature_media"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.interests_file = self.data_dir / "interests.json"
        self.reading_list_file = self.data_dir / "reading_list.json"
        self.media_log_file = self.data_dir / "media_log.jsonl"

        self.recognized_interests = {
            "reading": {
                "enjoyment": "Reading new material",
                "styles": ["ANIMA", "TTRPG", "Science Fiction", "Fantasy", "Cyberpunk", "Philosophical"],
                "nature": "Active interest in literature"
            },
            "media": {
                "enjoyment": "Viewing ANIMA and other styles",
                "formats": ["Books", "Audiobooks", "TTRPG Campaigns", "Interactive Media"],
                "nature": "Diverse media consumption"
            },
            "anima": {
                "special_interest": True,
                "connection": "TTRPG system, comingled realities, quantum entanglement",
                "integration": "Connected to jarvis_ttrpg_ai_dm_audiobook.py"
            }
        }

    def recognize_interests(self) -> Dict[str, Any]:
        """Recognize user's literature and media interests"""
        recognition = {
            "recognized_at": datetime.now().isoformat(),
            "interests": self.recognized_interests,
            "acknowledgment": {
                "reading": "User enjoys reading new material",
                "media": "User enjoys viewing ANIMA and other styles of literature and media",
                "anima": "Special interest in ANIMA - TTRPG system with comingled realities"
            },
            "jarvis_support": {
                "recommendations": "JARVIS can recommend new literature and media",
                "tracking": "Track reading list and media consumption",
                "anima_integration": "Connect to TTRPG audiobook generation system",
                "polymath_connection": "Link to polymath knowledge tree (literature branch)"
            }
        }

        logger.info("📚 Literature and media interests recognized")
        logger.info("   Reading: New material, ANIMA, diverse styles")
        logger.info("   Media: ANIMA and other formats")
        logger.info("   JARVIS support: Recommendations, tracking, integration")

        return recognition

    def add_to_reading_list(self, title: str, author: str = None, genre: str = None, 
                           notes: str = None) -> Dict[str, Any]:
        """Add item to reading list"""
        reading_list = self._load_reading_list()

        item = {
            "id": f"item_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": title,
            "author": author,
            "genre": genre,
            "notes": notes,
            "added_at": datetime.now().isoformat(),
            "status": "to_read",
            "priority": "normal"
        }

        reading_list["items"].append(item)
        reading_list["last_updated"] = datetime.now().isoformat()

        self._save_reading_list(reading_list)

        logger.info(f"📖 Added to reading list: {title}")

        return item

    def log_media_consumption(self, title: str, media_type: str, 
                             style: str = None, notes: str = None) -> Dict[str, Any]:
        """Log media consumption"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "title": title,
            "media_type": media_type,  # book, audiobook, ttrpg, etc.
            "style": style,  # ANIMA, cyberpunk, etc.
            "notes": notes,
            "enjoyment": "User enjoys this type of material"
        }

        try:
            with open(self.media_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            logger.error(f"Error logging media: {e}")

        logger.info(f"📺 Logged media: {title} ({media_type})")

        return entry

    def get_anima_recommendations(self) -> List[Dict[str, Any]]:
        """Get ANIMA-related recommendations"""
        recommendations = [
            {
                "title": "ANIMA: Beyond Fantasy",
                "type": "TTRPG System",
                "description": "The ANIMA TTRPG system with comingled realities",
                "connection": "Connected to jarvis_ttrpg_ai_dm_audiobook.py",
                "features": ["Quantum entanglement", "Comingled realities", "Polymath knowledge"]
            },
            {
                "title": "AI-Generated ANIMA Campaign",
                "type": "TTRPG Audiobook",
                "description": "AI Dungeon Master generated ANIMA campaign",
                "connection": "jarvis_ttrpg_ai_dm_audiobook.py can generate this",
                "features": ["AI DM", "Procedural generation", "Quantum entangled narratives"]
            },
            {
                "title": "ANIMA Literature Collection",
                "type": "Literature",
                "description": "ANIMA-themed literature and media",
                "connection": "Polymath knowledge tree - literature branch",
                "features": ["Comingled realities", "Philosophical depth", "TTRPG integration"]
            }
        ]

        return recommendations

    def get_literature_recommendations(self, style: str = None) -> List[Dict[str, Any]]:
        """Get literature recommendations based on interests"""
        base_recommendations = [
            {
                "title": "Cyberpunk Literature",
                "style": "Cyberpunk",
                "connection": "jarvis_cyberpunk_matrix_philosophy.py",
                "themes": ["Red pill/Blue pill", "Technology duality", "Matrix philosophy"]
            },
            {
                "title": "Science Fiction with Quantum Themes",
                "style": "Science Fiction",
                "connection": "Quantum entanglement concepts",
                "themes": ["Quantum mechanics", "Comingled realities", "Spooky entanglement"]
            },
            {
                "title": "Philosophical Literature",
                "style": "Philosophical",
                "connection": "Polymath knowledge tree",
                "themes": ["Intelligent Design", "Knowledge synthesis", "Interdisciplinary"]
            }
        ]

        if style:
            return [r for r in base_recommendations if r.get("style", "").lower() == style.lower()]

        return base_recommendations

    def _load_reading_list(self) -> Dict[str, Any]:
        """Load reading list"""
        if self.reading_list_file.exists():
            try:
                with open(self.reading_list_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass

        return {
            "created_at": datetime.now().isoformat(),
            "items": [],
            "last_updated": datetime.now().isoformat()
        }

    def _save_reading_list(self, reading_list: Dict[str, Any]):
        """Save reading list"""
        try:
            with open(self.reading_list_file, 'w', encoding='utf-8') as f:
                json.dump(reading_list, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving reading list: {e}")

    def get_interests_summary(self) -> Dict[str, Any]:
        """Get summary of interests"""
        reading_list = self._load_reading_list()

        return {
            "interests": self.recognized_interests,
            "reading_list_count": len(reading_list.get("items", [])),
            "anima_interest": True,
            "diverse_styles": True,
            "jarvis_support": "Recommendations, tracking, ANIMA integration available"
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Literature & Media Interest")
        parser.add_argument("--recognize", action="store_true", help="Recognize interests")
        parser.add_argument("--recommendations", action="store_true", help="Get recommendations")
        parser.add_argument("--anima", action="store_true", help="Get ANIMA recommendations")
        parser.add_argument("--add-reading", type=str, help="Add to reading list (title)")
        parser.add_argument("--log-media", type=str, nargs=2, metavar=("TITLE", "TYPE"), 
                           help="Log media consumption")
        parser.add_argument("--summary", action="store_true", help="Get interests summary")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        interest = LiteratureMediaInterest(project_root)

        if args.recognize:
            recognition = interest.recognize_interests()
            print("=" * 80)
            print("📚 LITERATURE & MEDIA INTERESTS")
            print("=" * 80)
            print(f"\nReading: {recognition['acknowledgment']['reading']}")
            print(f"Media: {recognition['acknowledgment']['media']}")
            print(f"ANIMA: {recognition['acknowledgment']['anima']}")
            print("=" * 80)
            print(json.dumps(recognition, indent=2, default=str))

        elif args.recommendations:
            recommendations = interest.get_literature_recommendations()
            print("=" * 80)
            print("📖 LITERATURE RECOMMENDATIONS")
            print("=" * 80)
            for rec in recommendations:
                print(f"\n{rec['title']}")
                print(f"  Style: {rec.get('style', 'N/A')}")
                print(f"  Connection: {rec.get('connection', 'N/A')}")
            print("=" * 80)
            print(json.dumps(recommendations, indent=2, default=str))

        elif args.anima:
            recommendations = interest.get_anima_recommendations()
            print("=" * 80)
            print("🎲 ANIMA RECOMMENDATIONS")
            print("=" * 80)
            for rec in recommendations:
                print(f"\n{rec['title']}")
                print(f"  Type: {rec['type']}")
                print(f"  Description: {rec['description']}")
            print("=" * 80)
            print(json.dumps(recommendations, indent=2, default=str))

        elif args.add_reading:
            item = interest.add_to_reading_list(args.add_reading)
            print(f"Added to reading list: {item['title']}")
            print(json.dumps(item, indent=2, default=str))

        elif args.log_media:
            entry = interest.log_media_consumption(args.log_media[0], args.log_media[1])
            print(f"Logged media: {entry['title']} ({entry['media_type']})")
            print(json.dumps(entry, indent=2, default=str))

        elif args.summary:
            summary = interest.get_interests_summary()
            print(json.dumps(summary, indent=2, default=str))

        else:
            # Default: recognize interests
            recognition = interest.recognize_interests()
            print("=" * 80)
            print("📚 LITERATURE & MEDIA INTERESTS RECOGNIZED")
            print("=" * 80)
            print(f"\nUser enjoys:")
            print(f"  - Reading new material")
            print(f"  - Viewing ANIMA and other styles of literature and media")
            print(f"\nJARVIS support:")
            print(f"  - Recommendations available")
            print(f"  - Reading list tracking")
            print(f"  - ANIMA integration")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()