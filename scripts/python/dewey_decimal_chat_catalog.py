#!/usr/bin/env python3
"""
Dewey Decimal Card Catalog for Agent Chat Sessions
📚 Organizes all agent chat session titles in a library-style card catalog system

Dewey Decimal Classification adapted for chat sessions:
- 000-099: General/System/Administrative
- 100-199: Philosophy/Psychology/Logic
- 200-299: Religion/Spirituality
- 300-399: Social Sciences/Communication
- 400-499: Language/Linguistics
- 500-599: Natural Sciences/Technology
- 600-699: Applied Sciences/Engineering
- 700-799: Arts/Entertainment
- 800-899: Literature/Writing
- 900-999: History/Geography/Biography

Tags: #DEWEY #CATALOG #LIBRARY #CHAT #SESSIONS #ORGANIZATION @JARVIS
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeweyDecimalCatalog")


@dataclass
class DeweyClassification:
    """Dewey Decimal classification for a chat session"""
    main_class: int  # 000-999
    division: int    # 00-99 (subdivision)
    section: int     # 0-9 (further subdivision)
    dewey_number: str  # Full Dewey number (e.g., "005.1")
    category: str    # Category name
    description: str  # Description of category

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def __str__(self) -> str:
        return f"{self.dewey_number} - {self.category}"


@dataclass
class ChatSessionCard:
    """Card catalog entry for a chat session"""
    session_id: str
    session_title: str
    dewey_number: str
    classification: DeweyClassification
    created_at: str
    last_updated: str
    agent_count: int = 0
    message_count: int = 0
    tags: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    summary: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            **asdict(self),
            "classification": self.classification.to_dict()
        }


class DeweyDecimalChatCatalog:
    """
    Dewey Decimal Card Catalog for Agent Chat Sessions

    Organizes all chat session titles in a library-style catalog system
    that dynamically updates as sessions are created/modified.
    """

    # Dewey Decimal Classification Categories
    DEWEY_CATEGORIES = {
        # 000-099: General/System/Administrative
        (0, 0, 0): ("000", "General Works", "Computer science, information, general works"),
        (0, 0, 5): ("005", "Computer Programming", "Programming, software, applications"),
        (0, 0, 6): ("006", "Special Computer Methods", "AI, machine learning, automation"),

        # 100-199: Philosophy/Psychology/Logic
        (1, 0, 0): ("100", "Philosophy", "Philosophy, logic, ethics"),
        (1, 1, 0): ("110", "Metaphysics", "Reality, existence, consciousness"),
        (1, 2, 0): ("120", "Epistemology", "Knowledge, truth, belief"),
        (1, 3, 0): ("130", "Parapsychology", "Consciousness, AI consciousness"),
        (1, 5, 0): ("150", "Psychology", "Psychology, behavior, cognition"),

        # 200-299: Religion/Spirituality
        (2, 0, 0): ("200", "Religion", "Religion, spirituality, theology"),
        (2, 3, 0): ("230", "Christianity", "Christian theology, doctrine"),

        # 300-399: Social Sciences/Communication
        (3, 0, 0): ("300", "Social Sciences", "Social sciences, sociology"),
        (3, 0, 1): ("301", "Sociology", "Social structure, culture"),
        (3, 0, 2): ("302", "Social Interaction", "Communication, relationships"),
        (3, 8, 0): ("380", "Commerce", "Business, economics, trade"),

        # 400-499: Language/Linguistics
        (4, 0, 0): ("400", "Language", "Language, linguistics, communication"),
        (4, 1, 0): ("410", "Linguistics", "Linguistics, grammar, syntax"),

        # 500-599: Natural Sciences/Technology
        (5, 0, 0): ("500", "Natural Sciences", "Natural sciences, mathematics"),
        (5, 1, 0): ("510", "Mathematics", "Mathematics, statistics"),
        (5, 2, 0): ("520", "Astronomy", "Astronomy, cosmology"),
        (5, 3, 0): ("530", "Physics", "Physics, quantum mechanics"),

        # 600-699: Applied Sciences/Engineering
        (6, 0, 0): ("600", "Technology", "Technology, applied sciences"),
        (6, 0, 1): ("601", "Engineering", "Engineering, design"),
        (6, 2, 0): ("620", "Engineering & Allied Operations", "Mechanical, electrical engineering"),
        (6, 5, 0): ("650", "Management", "Business management, administration"),
        (6, 6, 0): ("660", "Chemical Engineering", "Chemistry, materials"),
        (6, 7, 0): ("670", "Manufacturing", "Manufacturing, production"),

        # 700-799: Arts/Entertainment
        (7, 0, 0): ("700", "Arts", "Arts, recreation, entertainment"),
        (7, 9, 0): ("790", "Recreational & Performing Arts", "Games, sports, entertainment"),

        # 800-899: Literature/Writing
        (8, 0, 0): ("800", "Literature", "Literature, writing, rhetoric"),
        (8, 0, 8): ("808", "Rhetoric", "Writing, composition, communication"),

        # 900-999: History/Geography/Biography
        (9, 0, 0): ("900", "History", "History, geography, biography"),
        (9, 2, 0): ("920", "Biography", "Biography, genealogy"),
    }

    # Keyword mappings to Dewey categories
    KEYWORD_MAPPINGS = {
        # General/System
        "system": (0, 0, 0), "admin": (0, 0, 0), "configuration": (0, 0, 0),
        "programming": (0, 0, 5), "code": (0, 0, 5), "software": (0, 0, 5),
        "ai": (0, 0, 6), "machine learning": (0, 0, 6), "automation": (0, 0, 6),
        "jarvis": (0, 0, 6), "agent": (0, 0, 6), "workflow": (0, 0, 6),

        # Philosophy/Psychology
        "philosophy": (1, 0, 0), "logic": (1, 0, 0), "ethics": (1, 0, 0),
        "consciousness": (1, 3, 0), "awareness": (1, 3, 0),
        "psychology": (1, 5, 0), "behavior": (1, 5, 0), "cognition": (1, 5, 0),

        # Religion/Spirituality
        "religion": (2, 0, 0), "spiritual": (2, 0, 0), "theology": (2, 0, 0),
        "christian": (2, 3, 0), "catholic": (2, 3, 0), "bible": (2, 3, 0),

        # Social Sciences
        "social": (3, 0, 0), "society": (3, 0, 0), "culture": (3, 0, 1),
        "communication": (3, 0, 2), "interaction": (3, 0, 2),
        "business": (3, 8, 0), "commerce": (3, 8, 0), "economic": (3, 8, 0),

        # Language
        "language": (4, 0, 0), "linguistics": (4, 1, 0), "grammar": (4, 1, 0),

        # Natural Sciences
        "science": (5, 0, 0), "mathematics": (5, 1, 0), "math": (5, 1, 0),
        "astronomy": (5, 2, 0), "physics": (5, 3, 0), "quantum": (5, 3, 0),

        # Applied Sciences/Engineering
        "technology": (6, 0, 0), "tech": (6, 0, 0),
        "engineering": (6, 0, 1), "design": (6, 0, 1),
        "mechanical": (6, 2, 0), "electrical": (6, 2, 0),
        "management": (6, 5, 0), "administration": (6, 5, 0),
        "chemical": (6, 6, 0), "chemistry": (6, 6, 0),
        "manufacturing": (6, 7, 0), "production": (6, 7, 0),

        # Arts/Entertainment
        "art": (7, 0, 0), "arts": (7, 0, 0), "creative": (7, 0, 0),
        "entertainment": (7, 9, 0), "game": (7, 9, 0), "gaming": (7, 9, 0),

        # Literature/Writing
        "literature": (8, 0, 0), "writing": (8, 0, 8), "rhetoric": (8, 0, 8),
        "documentation": (8, 0, 8), "document": (8, 0, 8),

        # History/Geography
        "history": (9, 0, 0), "historical": (9, 0, 0),
        "biography": (9, 2, 0), "biographical": (9, 2, 0),
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Dewey Decimal catalog"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Catalog storage
        self.catalog_dir = self.project_root / "data" / "dewey_catalog"
        self.catalog_dir.mkdir(parents=True, exist_ok=True)

        self.catalog_file = self.catalog_dir / "chat_session_catalog.json"
        self.index_file = self.catalog_dir / "dewey_index.json"

        # Load existing catalog
        self.catalog: Dict[str, ChatSessionCard] = {}
        self.dewey_index: Dict[str, List[str]] = defaultdict(list)  # dewey_number -> [session_ids]

        self._load_catalog()

        logger.info("📚 Dewey Decimal Chat Catalog initialized")
        logger.info(f"   Catalog entries: {len(self.catalog)}")

    def _load_catalog(self) -> None:
        """Load existing catalog from disk"""
        if self.catalog_file.exists():
            try:
                with open(self.catalog_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for session_id, card_data in data.items():
                        classification = DeweyClassification(**card_data['classification'])
                        card = ChatSessionCard(
                            session_id=session_id,
                            session_title=card_data['session_title'],
                            dewey_number=card_data['dewey_number'],
                            classification=classification,
                            created_at=card_data['created_at'],
                            last_updated=card_data['last_updated'],
                            agent_count=card_data.get('agent_count', 0),
                            message_count=card_data.get('message_count', 0),
                            tags=card_data.get('tags', []),
                            keywords=card_data.get('keywords', []),
                            summary=card_data.get('summary')
                        )
                        self.catalog[session_id] = card
                        self.dewey_index[card.dewey_number].append(session_id)

                logger.info(f"✅ Loaded {len(self.catalog)} catalog entries")
            except Exception as e:
                logger.warning(f"⚠️  Error loading catalog: {e}")

        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    self.dewey_index = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Error loading index: {e}")

    def _classify_session(self, title: str, content: Optional[str] = None) -> DeweyClassification:
        """Classify a session using Dewey Decimal system"""
        title_lower = title.lower()
        content_lower = (content or "").lower()
        combined_text = f"{title_lower} {content_lower}"

        # Find matching keywords
        best_match = (0, 0, 0)  # Default: General Works
        best_score = 0

        for keyword, dewey_key in self.KEYWORD_MAPPINGS.items():
            if keyword in combined_text:
                score = combined_text.count(keyword)
                if score > best_score:
                    best_score = score
                    best_match = dewey_key

        # Get classification
        if best_match in self.DEWEY_CATEGORIES:
            dewey_num, category, description = self.DEWEY_CATEGORIES[best_match]
        else:
            # Default to General Works
            dewey_num, category, description = self.DEWEY_CATEGORIES[(0, 0, 0)]

        main_class, division, section = best_match

        return DeweyClassification(
            main_class=main_class,
            division=division,
            section=section,
            dewey_number=dewey_num,
            category=category,
            description=description
        )

    def add_or_update_session(self, session_id: str, session_title: str,
                            content: Optional[str] = None,
                            agent_count: int = 0,
                            message_count: int = 0,
                            tags: Optional[List[str]] = None,
                            created_at: Optional[str] = None,
                            last_updated: Optional[str] = None) -> ChatSessionCard:
        """Add or update a session in the catalog"""
        # Classify session
        classification = self._classify_session(session_title, content)

        # Extract keywords from title
        keywords = self._extract_keywords(session_title, content)

        # Create or update card
        if session_id in self.catalog:
            # Update existing
            card = self.catalog[session_id]
            old_dewey = card.dewey_number

            card.session_title = session_title
            card.dewey_number = classification.dewey_number
            card.classification = classification
            card.agent_count = agent_count
            card.message_count = message_count
            card.tags = tags or card.tags
            card.keywords = keywords
            card.last_updated = last_updated or datetime.now().isoformat()

            # Update index if Dewey number changed
            if old_dewey != classification.dewey_number:
                if old_dewey in self.dewey_index:
                    self.dewey_index[old_dewey].remove(session_id)
                self.dewey_index[classification.dewey_number].append(session_id)

            logger.info(f"📝 Updated catalog entry: {session_id} → {classification.dewey_number}")
        else:
            # Create new
            card = ChatSessionCard(
                session_id=session_id,
                session_title=session_title,
                dewey_number=classification.dewey_number,
                classification=classification,
                created_at=created_at or datetime.now().isoformat(),
                last_updated=last_updated or datetime.now().isoformat(),
                agent_count=agent_count,
                message_count=message_count,
                tags=tags or [],
                keywords=keywords
            )
            self.catalog[session_id] = card
            self.dewey_index[classification.dewey_number].append(session_id)

            logger.info(f"➕ Added catalog entry: {session_id} → {classification.dewey_number}")

        # Save catalog
        self._save_catalog()

        return card

    def _extract_keywords(self, title: str, content: Optional[str] = None) -> List[str]:
        """Extract keywords from title and content"""
        text = f"{title} {content or ''}".lower()

        # Extract words (3+ characters, alphanumeric)
        words = re.findall(r'\b[a-z]{3,}\b', text)

        # Filter to relevant keywords (exclude common words)
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
        keywords = [w for w in words if w not in stop_words and len(w) >= 3]

        # Return top 10 unique keywords
        from collections import Counter
        keyword_counts = Counter(keywords)
        return [kw for kw, _ in keyword_counts.most_common(10)]

    def scan_and_catalog_sessions(self) -> Dict[str, Any]:
        """Scan all chat sessions and catalog them"""
        self.logger.info("🔍 Scanning chat sessions for cataloging...")

        sessions_found = 0
        sessions_cataloged = 0

        # Scan master chat session
        master_chat_file = self.project_root / "data" / "master_chat" / "master_session.json"
        if master_chat_file.exists():
            try:
                with open(master_chat_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_id = data.get('session_id', 'jarvis_master_chat')
                    session_title = data.get('session_name', 'JARVIS Master Chat')
                    messages = data.get('messages', [])

                    self.add_or_update_session(
                        session_id=session_id,
                        session_title=session_title,
                        content=json.dumps(data),
                        agent_count=len(data.get('consolidated_agents', [])),
                        message_count=len(messages),
                        created_at=data.get('created_at'),
                        last_updated=data.get('last_activity')
                    )
                    sessions_found += 1
                    sessions_cataloged += 1
            except Exception as e:
                self.logger.warning(f"⚠️  Error scanning master chat: {e}")

        # Scan agent chat sessions directory
        sessions_dir = self.project_root / "data" / "agent_chat_sessions"
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session_id = data.get('session_id', session_file.stem)
                        # Extract better title from metadata (workflow_type, portal_url, etc.)
                        session_title = (
                            data.get('session_name') or 
                            data.get('title') or 
                            data.get('workflow_type') or
                            data.get('metadata', {}).get('workflow_name') or
                            data.get('metadata', {}).get('workflow_type') or
                            session_file.stem
                        )
                        messages = data.get('messages', [])

                        self.add_or_update_session(
                            session_id=session_id,
                            session_title=session_title,
                            content=json.dumps(data),
                            agent_count=len(data.get('agents', [])),
                            message_count=len(messages),
                            created_at=data.get('created_at'),
                            last_updated=data.get('last_updated') or data.get('last_activity')
                        )
                        sessions_found += 1
                        sessions_cataloged += 1
                except Exception as e:
                    self.logger.warning(f"⚠️  Error scanning {session_file}: {e}")

        # Scan sub-ask chat sessions
        sub_ask_sessions_file = self.project_root / "data" / "sub_ask" / "chat_sessions.json"
        if sub_ask_sessions_file.exists():
            try:
                with open(sub_ask_sessions_file, 'r', encoding='utf-8') as f:
                    sessions_data = json.load(f)
                    for session_id, session_data in sessions_data.items():
                        session_title = session_data.get('session_title') or session_data.get('title') or session_id
                        messages = session_data.get('messages', [])

                        self.add_or_update_session(
                            session_id=session_id,
                            session_title=session_title,
                            content=json.dumps(session_data),
                            agent_count=1,  # Sub-ask sessions typically single agent
                            message_count=len(messages),
                            created_at=session_data.get('created_at'),
                            last_updated=session_data.get('updated_at')
                        )
                        sessions_found += 1
                        sessions_cataloged += 1
            except Exception as e:
                self.logger.warning(f"⚠️  Error scanning sub-ask sessions: {e}")

        self.logger.info(f"✅ Cataloged {sessions_cataloged} of {sessions_found} sessions found")

        return {
            "sessions_found": sessions_found,
            "sessions_cataloged": sessions_cataloged,
            "total_catalog_entries": len(self.catalog)
        }

    def get_sessions_by_dewey(self, dewey_number: str) -> List[ChatSessionCard]:
        """Get all sessions classified under a Dewey number"""
        session_ids = self.dewey_index.get(dewey_number, [])
        return [self.catalog[sid] for sid in session_ids if sid in self.catalog]

    def search_catalog(self, query: str) -> List[ChatSessionCard]:
        """Search catalog by title, keywords, or tags"""
        query_lower = query.lower()
        results = []

        for card in self.catalog.values():
            # Search in title
            if query_lower in card.session_title.lower():
                results.append(card)
                continue

            # Search in keywords
            if any(query_lower in kw.lower() for kw in card.keywords):
                results.append(card)
                continue

            # Search in tags
            if any(query_lower in tag.lower() for tag in card.tags):
                results.append(card)
                continue

        return results

    def generate_catalog_report(self) -> Dict[str, Any]:
        """Generate a catalog report"""
        report = {
            "total_entries": len(self.catalog),
            "dewey_distribution": {},
            "categories": {},
            "recent_entries": [],
            "generated_at": datetime.now().isoformat()
        }

        # Count by Dewey number
        for dewey_num, session_ids in self.dewey_index.items():
            report["dewey_distribution"][dewey_num] = len(session_ids)

        # Count by category
        for card in self.catalog.values():
            category = card.classification.category
            report["categories"][category] = report["categories"].get(category, 0) + 1

        # Recent entries (last 10)
        sorted_entries = sorted(
            self.catalog.values(),
            key=lambda c: c.last_updated,
            reverse=True
        )[:10]
        report["recent_entries"] = [
            {
                "session_id": card.session_id,
                "title": card.session_title,
                "dewey": card.dewey_number,
                "category": card.classification.category,
                "last_updated": card.last_updated
            }
            for card in sorted_entries
        ]

        return report

    def _save_catalog(self) -> None:
        """Save catalog to disk"""
        try:
            # Save catalog
            catalog_data = {
                session_id: card.to_dict()
                for session_id, card in self.catalog.items()
            }
            with open(self.catalog_file, 'w', encoding='utf-8') as f:
                json.dump(catalog_data, f, indent=2, ensure_ascii=False)

            # Save index
            index_data = {
                dewey_num: session_ids
                for dewey_num, session_ids in self.dewey_index.items()
            }
            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

            logger.debug("💾 Catalog saved")
        except Exception as e:
            logger.error(f"❌ Error saving catalog: {e}")


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Dewey Decimal Chat Catalog")
        parser.add_argument("--scan", action="store_true", help="Scan and catalog all sessions")
        parser.add_argument("--search", type=str, help="Search catalog by query")
        parser.add_argument("--dewey", type=str, help="Get sessions by Dewey number")
        parser.add_argument("--report", action="store_true", help="Generate catalog report")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        catalog = DeweyDecimalChatCatalog()

        if args.scan:
            result = catalog.scan_and_catalog_sessions()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"\n✅ Catalog scan complete!")
                print(f"   Sessions found: {result['sessions_found']}")
                print(f"   Sessions cataloged: {result['sessions_cataloged']}")
                print(f"   Total catalog entries: {result['total_catalog_entries']}")

        elif args.search:
            results = catalog.search_catalog(args.search)
            if args.json:
                print(json.dumps([card.to_dict() for card in results], indent=2))
            else:
                print(f"\n🔍 Search results for '{args.search}': {len(results)} found")
                for card in results:
                    print(f"   {card.dewey_number} - {card.session_title}")

        elif args.dewey:
            results = catalog.get_sessions_by_dewey(args.dewey)
            if args.json:
                print(json.dumps([card.to_dict() for card in results], indent=2))
            else:
                print(f"\n📚 Sessions in {args.dewey}: {len(results)} found")
                for card in results:
                    print(f"   {card.session_id}: {card.session_title}")

        elif args.report:
            report = catalog.generate_catalog_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"\n📊 Catalog Report")
                print(f"   Total entries: {report['total_entries']}")
                print(f"   Categories: {len(report['categories'])}")
                print(f"\n   Top categories:")
                for category, count in sorted(report['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"      {category}: {count}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()