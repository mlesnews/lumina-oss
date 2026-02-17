#!/usr/bin/env python3
"""
Holocron Compound Logging System

TCC&DDS: The Card Catalog & Dewey-Decimal System
Compound log-style for history preservation and documentation (@HOLOCRONS)

Forms chapters for:
- Book/Audiobook/Comicbook (Digital) format
- Video/Television/Movie format

@SLMM: Sound-Light-Music-Magic ("SLI-M")
@LAFF: Individual Multimedia Studios

Tags: #holocrons #card_catalog #dewey_decimal #compound_logging #tcc #dds #slmm #laff
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("HolocronCompoundLogging")


class MediaFormat(Enum):
    """Media formats"""
    BOOK = "book"
    AUDIOBOOK = "audiobook"
    COMICBOOK = "comicbook"
    VIDEO = "video"
    TELEVISION = "television"
    MOVIE = "movie"


class SLMMElement(Enum):
    """Sound-Light-Music-Magic elements"""
    SOUND = "sound"  # Audio elements
    LIGHT = "light"  # Visual/lighting
    MUSIC = "music"  # Musical score
    MAGIC = "magic"  # Special effects/magic


@dataclass
class DeweyDecimalClassification:
    """Dewey-Decimal classification"""
    dewey_number: str
    category: str
    description: str
    subcategories: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CardCatalogCard:
    """Card catalog card (TCC)"""
    catalog_number: str
    title: str
    author: str
    dewey_decimal: str
    subject_headings: List[str] = field(default_factory=list)
    description: str = ""
    holocron_reference: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['created_at'] = self.created_at.isoformat()
        return result


@dataclass
class HolocronEntry:
    """Holocron entry (history preservation)"""
    holocron_id: str
    title: str
    content: str
    dewey_classification: str
    card_catalog_number: str
    chapter_number: int
    media_formats: List[MediaFormat] = field(default_factory=list)
    slmm_elements: Dict[str, Any] = field(default_factory=dict)
    laff_studio: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['media_formats'] = [f.value for f in self.media_formats]
        result['created_at'] = self.created_at.isoformat()
        return result


class HolocronCompoundLoggingSystem:
    """
    Holocron Compound Logging System

    TCC&DDS: The Card Catalog & Dewey-Decimal System
    Compound log-style for history preservation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize holocron compound logging"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "holocrons"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Holocrons
        self.holocrons: Dict[str, HolocronEntry] = {}

        # Card catalog
        self.card_catalog: Dict[str, CardCatalogCard] = {}

        # Dewey-Decimal classifications
        self.dewey_classifications: Dict[str, DeweyDecimalClassification] = {}

        # Initialize standard Dewey classifications
        self._initialize_dewey_classifications()

        # Load saved holocrons
        self._load_holocrons()

        logger.info("=" * 80)
        logger.info("📚 HOLOCRON COMPOUND LOGGING SYSTEM")
        logger.info("=" * 80)
        logger.info("   TCC&DDS: The Card Catalog & Dewey-Decimal System")
        logger.info("   History preservation and documentation (@HOLOCRONS)")
        logger.info("   Chapters for Book/Audiobook/Comicbook/Video/TV/Movie")
        logger.info("=" * 80)
        logger.info("")

    def _initialize_dewey_classifications(self):
        """Initialize standard Dewey-Decimal classifications"""
        classifications = [
            DeweyDecimalClassification("000", "Computer Science, Information & General Works", "General works"),
            DeweyDecimalClassification("100", "Philosophy & Psychology", "Philosophy"),
            DeweyDecimalClassification("200", "Religion", "Religious works"),
            DeweyDecimalClassification("300", "Social Sciences", "Social sciences"),
            DeweyDecimalClassification("400", "Language", "Languages"),
            DeweyDecimalClassification("500", "Natural Sciences & Mathematics", "Sciences"),
            DeweyDecimalClassification("600", "Technology", "Applied sciences"),
            DeweyDecimalClassification("700", "Arts & Recreation", "Arts"),
            DeweyDecimalClassification("800", "Literature", "Literature"),
            DeweyDecimalClassification("900", "History & Geography", "History"),
            # Custom LUMINA classifications
            DeweyDecimalClassification("Ω-000", "Command & Control", "JARVIS systems"),
            DeweyDecimalClassification("Σ-001", "Knowledge Management", "Knowledge systems"),
            DeweyDecimalClassification("Δ-002", "Education & Learning", "Educational systems"),
            DeweyDecimalClassification("Σ-004", "Analytics & Monitoring", "Analytics systems"),
        ]

        for classification in classifications:
            self.dewey_classifications[classification.dewey_number] = classification

        logger.info(f"✅ Initialized {len(self.dewey_classifications)} Dewey-Decimal classifications")

    def create_holocron_entry(
        self,
        title: str,
        content: str,
        dewey_classification: str,
        chapter_number: int,
        media_formats: Optional[List[MediaFormat]] = None,
        slmm_elements: Optional[Dict[str, Any]] = None,
        laff_studio: Optional[str] = None,
        acs_prefix: Optional[str] = None
    ) -> HolocronEntry:
        """
        Create holocron entry with compound logging

        Format: [PREFIX-@CCDDS[#CARDCATALOG-DEWEYDECIMAL-ID+NUM#, TITLE]
        Where:
        - PREFIX = @ACS or other prefix
        - @CCDDS = Card Catalog & Dewey-Decimal System
        - #CARDCATALOG-DEWEYDECIMAL-ID+NUM# = CC-{DEWEY}-{CHAPTER:04d}
        - Comma separator before TITLE
        """
        holocron_id = f"holocron_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Base Card Catalog Number: CC-{DEWEY}-{CHAPTER:04d}
        card_catalog_dewey_id = f"CC-{dewey_classification}-{chapter_number:04d}"

        # Format with @CCDDS prefix and comma separator
        # Format: [PREFIX-@CCDDS[#CARDCATALOG-DEWEYDECIMAL-ID+NUM#, TITLE]
        prefix = acs_prefix or "@ACS"
        card_catalog_number = f"{prefix}-@CCDDS[#{card_catalog_dewey_id}#, {title}]"

        entry = HolocronEntry(
            holocron_id=holocron_id,
            title=title,
            content=content,
            dewey_classification=dewey_classification,
            card_catalog_number=card_catalog_number,  # Full formatted number with comma separator
            chapter_number=chapter_number,
            media_formats=media_formats or [MediaFormat.BOOK],
            slmm_elements=slmm_elements or {},
            laff_studio=laff_studio
        )

        self.holocrons[holocron_id] = entry

        # Create card catalog entry
        self._create_card_catalog_entry(entry)

        logger.info(f"📚 Created holocron entry: {title}")
        logger.info(f"   Dewey: {dewey_classification}")
        logger.info(f"   Card Catalog: {card_catalog_number}")
        logger.info(f"   Chapter: {chapter_number}")

        return entry

    def _create_card_catalog_entry(self, entry: HolocronEntry):
        """Create card catalog entry for holocron"""
        # Extract subject headings from content
        subject_headings = self._extract_subject_headings(entry.content)

        # Extract base catalog number from formatted string for indexing
        # Format: [PREFIX-@CCDDS[#CC-DEWEY-CHAPTER#, TITLE]
        # Extract: CC-DEWEY-CHAPTER from the formatted string
        import re
        base_catalog_match = re.search(r'#(CC-[^#]+)#', entry.card_catalog_number)
        base_catalog_number = base_catalog_match.group(1) if base_catalog_match else entry.card_catalog_number

        card = CardCatalogCard(
            catalog_number=entry.card_catalog_number,  # Full formatted: [PREFIX-@CCDDS[#CC-DEWEY-CHAPTER#, TITLE]
            title=entry.title,
            author="LUMINA System",
            dewey_decimal=entry.dewey_classification,
            subject_headings=subject_headings,
            description=entry.content[:200] + "..." if len(entry.content) > 200 else entry.content,
            holocron_reference=entry.holocron_id
        )

        # Store by full formatted catalog number
        self.card_catalog[entry.card_catalog_number] = card
        # Also store by base catalog number for lookup
        self.card_catalog[base_catalog_number] = card

        logger.info(f"📇 Created card catalog entry: {entry.card_catalog_number}")

    def _extract_subject_headings(self, content: str) -> List[str]:
        """Extract subject headings from content"""
        # Simple extraction - look for key terms
        keywords = []
        words = content.lower().split()

        # Common subject terms
        subject_terms = [
            "system", "command", "control", "monitoring", "escalation",
            "delegation", "workflow", "memory", "ask", "agent", "jarvis",
            "fishbowl", "stargate", "galactic", "waypoint", "energy", "tier"
        ]

        for term in subject_terms:
            if term in words:
                keywords.append(term.title())

        return keywords[:5]  # Limit to 5

    def generate_chapter_for_format(
        self,
        holocron_id: str,
        format_type: MediaFormat
    ) -> Dict[str, Any]:
        """Generate chapter content for specific media format"""
        if holocron_id not in self.holocrons:
            return {}

        entry = self.holocrons[holocron_id]

        base = {
            "holocron_id": holocron_id,
            "title": entry.title,
            "chapter_number": entry.chapter_number,
            "dewey": entry.dewey_classification,
            "card_catalog": entry.card_catalog_number,
            "format": format_type.value
        }

        if format_type == MediaFormat.BOOK:
            return {
                **base,
                "type": "digital_book",
                "pages": len(entry.content.split()) // 250,
                "word_count": len(entry.content.split()),
                "chapters": [entry.title]
            }

        elif format_type == MediaFormat.AUDIOBOOK:
            duration = len(entry.content.split()) // 150  # ~150 words per minute
            return {
                **base,
                "type": "audiobook",
                "duration_minutes": duration,
                "narration": "AI-generated",
                "slmm": entry.slmm_elements,
                "sound_elements": entry.slmm_elements.get("sound", {})
            }

        elif format_type == MediaFormat.COMICBOOK:
            return {
                **base,
                "type": "digital_comic",
                "panels": len(entry.content.split()) // 50,
                "art_style": "digital_illustration",
                "slmm": {
                    "light": entry.slmm_elements.get("light", {}),
                    "magic": entry.slmm_elements.get("magic", {})
                }
            }

        elif format_type == MediaFormat.VIDEO:
            duration = len(entry.content.split()) // 150
            return {
                **base,
                "type": "video",
                "duration_minutes": duration,
                "resolution": "4K",
                "slmm": entry.slmm_elements,
                "laff_studio": entry.laff_studio
            }

        elif format_type == MediaFormat.TELEVISION:
            return {
                **base,
                "type": "television_episode",
                "episode_number": entry.chapter_number,
                "duration_minutes": 30,
                "season": 1,
                "slmm": entry.slmm_elements,
                "laff_studio": entry.laff_studio
            }

        elif format_type == MediaFormat.MOVIE:
            return {
                **base,
                "type": "movie",
                "duration_minutes": 120,
                "rating": "PG-13",
                "slmm": entry.slmm_elements,
                "laff_studio": entry.laff_studio
            }

        return base

    def get_compound_log_report(self) -> Dict[str, Any]:
        """Get compound log report (TCC&DDS)"""
        return {
            "report_date": datetime.now().isoformat(),
            "card_catalog": {
                "total_entries": len(self.card_catalog),
                "entries": [c.to_dict() for c in self.card_catalog.values()]
            },
            "dewey_decimal": {
                "total_classifications": len(self.dewey_classifications),
                "classifications": [d.to_dict() for d in self.dewey_classifications.values()],
                "used_classifications": list(set(h.dewey_classification for h in self.holocrons.values()))
            },
            "holocrons": {
                "total": len(self.holocrons),
                "chapters": [h.to_dict() for h in self.holocrons.values()]
            },
            "media_formats": {
                "total_formats": len(MediaFormat),
                "formats": [f.value for f in MediaFormat]
            },
            "compound_logging_style": "TCC&DDS (The Card Catalog & Dewey-Decimal System)",
            "description": "Modern human library systems for history preservation and documentation"
        }

    def _load_holocrons(self):
        """Load holocrons from file"""
        holocron_file = self.data_dir / "holocrons_compound_log.json"

        if not holocron_file.exists():
            return

        try:
            with open(holocron_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load holocrons
            for hid, entry_data in data.get('holocrons', {}).items():
                entry = HolocronEntry(
                    holocron_id=entry_data['holocron_id'],
                    title=entry_data['title'],
                    content=entry_data['content'],
                    dewey_classification=entry_data['dewey_classification'],
                    card_catalog_number=entry_data['card_catalog_number'],
                    chapter_number=entry_data['chapter_number'],
                    media_formats=[MediaFormat(f) for f in entry_data.get('media_formats', [])],
                    slmm_elements=entry_data.get('slmm_elements', {}),
                    laff_studio=entry_data.get('laff_studio'),
                    created_at=datetime.fromisoformat(entry_data['created_at'])
                )
                self.holocrons[hid] = entry

            # Load card catalog
            for cnum, card_data in data.get('card_catalog', {}).items():
                card = CardCatalogCard(
                    catalog_number=card_data['catalog_number'],
                    title=card_data['title'],
                    author=card_data['author'],
                    dewey_decimal=card_data['dewey_decimal'],
                    subject_headings=card_data.get('subject_headings', []),
                    description=card_data.get('description', ''),
                    holocron_reference=card_data.get('holocron_reference'),
                    created_at=datetime.fromisoformat(card_data['created_at'])
                )
                self.card_catalog[cnum] = card

            logger.info(f"📂 Loaded {len(self.holocrons)} holocrons and {len(self.card_catalog)} card catalog entries")
        except Exception as e:
            logger.debug(f"Could not load holocrons: {e}")

    def save_holocrons(self):
        try:
            """Save holocrons to file"""
            holocron_file = self.data_dir / "holocrons_compound_log.json"

            data = {
                "holocrons": {hid: h.to_dict() for hid, h in self.holocrons.items()},
                "card_catalog": {cnum: c.to_dict() for cnum, c in self.card_catalog.items()},
                "dewey_classifications": {dnum: d.to_dict() for dnum, d in self.dewey_classifications.items()},
                "saved_at": datetime.now().isoformat()
            }

            with open(holocron_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"💾 Holocrons saved: {holocron_file}")


        except Exception as e:
            self.logger.error(f"Error in save_holocrons: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Holocron Compound Logging System")
        parser.add_argument('--create', nargs=7, metavar=('TITLE', 'CONTENT', 'DEWEY', 'CHAPTER', 'FORMATS', 'LAFF', 'PREFIX'),
                           help='Create holocron entry (PREFIX optional, defaults to @ACS)')
        parser.add_argument('--generate', nargs=2, metavar=('HOLOCRON_ID', 'FORMAT'),
                           help='Generate chapter for format')
        parser.add_argument('--report', action='store_true', help='Show compound log report')
        parser.add_argument('--save', action='store_true', help='Save holocrons')

        args = parser.parse_args()

        system = HolocronCompoundLoggingSystem()

        if args.create:
            create_args = args.create
            title, content, dewey, chapter_str, formats_str, laff = create_args[:6]
            acs_prefix = create_args[6] if len(create_args) > 6 and create_args[6] != "none" else None

            chapter_num = int(chapter_str)
            formats = [MediaFormat(f) for f in formats_str.split(',')]
            slmm = {"sound": {}, "light": {}, "music": {}, "magic": {}}

            entry = system.create_holocron_entry(
                title=title,
                content=content,
                dewey_classification=dewey,
                chapter_number=chapter_num,
                media_formats=formats,
                slmm_elements=slmm,
                laff_studio=laff if laff != "none" else None,
                acs_prefix=acs_prefix
            )
            print(f"\n✅ Created holocron: {entry.holocron_id}")
            if args.save:
                system.save_holocrons()

        elif args.generate:
            holocron_id, format_str = args.generate
            format_type = MediaFormat(format_str.lower())
            chapter = system.generate_chapter_for_format(holocron_id, format_type)
            if chapter:
                print("\n" + "=" * 80)
                print(f"🎬 GENERATED CHAPTER: {format_type.value.upper()}")
                print("=" * 80)
                print(json.dumps(chapter, indent=2, default=str))
                print("=" * 80)
                print("")
            if args.save:
                system.save_holocrons()

        elif args.report:
            report = system.get_compound_log_report()
            print("\n" + "=" * 80)
            print("📚 COMPOUND LOG REPORT (TCC&DDS)")
            print("=" * 80)
            print(f"Card Catalog Entries: {report['card_catalog']['total_entries']}")
            print(f"Holocron Chapters: {report['holocrons']['total']}")
            print(f"Dewey Classifications: {report['dewey_decimal']['total_classifications']}")
            print(f"Used Classifications: {len(report['dewey_decimal']['used_classifications'])}")
            print("")
            print("Media Formats Available:")
            for fmt in report['media_formats']['formats']:
                print(f"   - {fmt}")
            print("")
            print("=" * 80)
            print("")
            if args.save:
                system.save_holocrons()

        else:
            print("\n" + "=" * 80)
            print("📚 HOLOCRON COMPOUND LOGGING SYSTEM")
            print("=" * 80)
            print("   TCC&DDS: The Card Catalog & Dewey-Decimal System")
            print("")
            print("Use --create to create holocron entry")
            print("Use --generate to generate chapter for format")
            print("Use --report to show compound log report")
            print("=" * 80)
            print("")

        if args.save:
            system.save_holocrons()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()