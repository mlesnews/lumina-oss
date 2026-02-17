#!/usr/bin/env python3
"""
JARVIS @ASK Stack Triage & Docuseries Organization
Dewey-Decimal Catalog Notation for YouTube Docuseries Anime Cartoon

Addresses all @ASK stacks since project inception via triage.
Establishes @SMART order of precedence for chapters (holocrons).
Creates YouTube docuseries structure with Dewey-Decimal notation in video titles.

Episodes: 30-45 minutes, real storytelling, less filler.
Exception: Cartoon Network inspired "Poppa-Palpatine & Aluminum Falcon" commercial episodes.
Ads for favorite YouTube content creators.

Tags: #JARVIS #@ASK #TRIAGE #DEWEY #DECIMAL #HOLOCRON #YOUTUBE #DOCUSERIES #ANIME #CARTOON @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
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

logger = get_logger("JARVISAskStackTriageDocuseries")


class TriagePriority(Enum):
    """Triage priority levels"""
    CRITICAL = "critical"  # Must address immediately
    HIGH = "high"  # Address soon
    MEDIUM = "medium"  # Normal priority
    LOW = "low"  # Can wait
    ARCHIVE = "archive"  # Historical reference only


class EpisodeType(Enum):
    """Episode types"""
    STORY = "story"  # Real storytelling episode (30-45 min)
    COMMERCIAL = "commercial"  # Poppa-Palpatine & Aluminum Falcon commercial
    FILLER = "filler"  # Filler episode (minimal, unless special)
    AD = "ad"  # Ad for favorite YouTube content creators


@dataclass
class TriageResult:
    """Triage result for an @ASK"""
    ask_id: str
    ask_text: str
    priority: TriagePriority
    category: str
    dewey_classification: str
    holocron_chapter: str
    episode_number: Optional[int] = None
    episode_type: EpisodeType = EpisodeType.STORY
    reasoning: str = ""
    dependencies: List[str] = field(default_factory=list)
    estimated_duration: int = 30  # minutes


@dataclass
class DocuseriesEpisode:
    """YouTube docuseries episode"""
    episode_number: int
    dewey_title: str  # Dewey-Decimal notation in title
    title: str
    episode_type: EpisodeType
    duration_minutes: int
    holocron_chapter: str
    asks_addressed: List[str] = field(default_factory=list)
    story_arc: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)
    is_commercial: bool = False
    featured_creators: List[str] = field(default_factory=list)  # For ad episodes


class JARVISAskStackTriageDocuseries:
    """
    JARVIS @ASK Stack Triage & Docuseries Organization

    Addresses all @ASK stacks via triage and organizes into YouTube docuseries
    with Dewey-Decimal catalog notation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize triage and docuseries system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ask_triage_docuseries"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load all @ASK stacks
        self.all_asks = self._load_all_asks()

        # Triage results
        self.triage_results: List[TriageResult] = []

        # Docuseries episodes
        self.episodes: List[DocuseriesEpisode] = []

        # Dewey-Decimal mapping
        self.dewey_mapping = self._initialize_dewey_mapping()

        # Holocron chapter mapping
        self.holocron_chapters = self._load_holocron_chapters()

        logger.info("✅ JARVIS @ASK Stack Triage & Docuseries System initialized")
        logger.info(f"   Total @ASKS loaded: {len(self.all_asks)}")

    def _load_all_asks(self) -> List[Dict[str, Any]]:
        """Load all @ASK stacks since project inception"""
        asks_file = self.project_root / "data" / "holocron" / "archives" / "000_Information_Systems" / "LUMINA_ALL_ASKS_ORDERED.json"

        if asks_file.exists():
            try:
                with open(asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get("asks", [])
            except Exception as e:
                logger.warning(f"⚠️  Failed to load @ASK stacks: {e}")

        return []

    def _initialize_dewey_mapping(self) -> Dict[str, str]:
        """Initialize Dewey-Decimal classification mapping"""
        return {
            "command_control": "Ω-000",
            "knowledge_management": "Σ-001",
            "education": "Δ-002",
            "synchronization": "Δ-003",
            "analytics": "Σ-004",
            "architecture": "Δ-005",
            "operations": "β-006",
            "information_systems": "000",
            "philosophy_psychology": "100",
            "religion_spirituality": "200",
            "social_sciences": "300",
            "language": "400",
            "science_mathematics": "500",
            "technology": "600",
            "arts_recreation": "700",
            "literature": "800",
            "history_geography": "900"
        }

    def _load_holocron_chapters(self) -> Dict[str, Any]:
        """Load holocron chapter structure"""
        holocron_index = self.project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"

        if holocron_index.exists():
            try:
                with open(holocron_index, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Failed to load holocron index: {e}")

        return {}

    def triage_all_asks(self) -> List[TriageResult]:
        """Triage all @ASK stacks"""
        logger.info("="*80)
        logger.info("🔍 TRIAGING ALL @ASK STACKS")
        logger.info(f"   Total @ASKS: {len(self.all_asks)}")
        logger.info("="*80)

        triage_results = []

        for ask in self.all_asks:
            result = self._triage_single_ask(ask)
            triage_results.append(result)

        self.triage_results = triage_results

        # Save triage results
        self._save_triage_results()

        logger.info(f"✅ Triage complete: {len(triage_results)} @ASKS processed")
        logger.info(f"   Critical: {sum(1 for r in triage_results if r.priority == TriagePriority.CRITICAL)}")
        logger.info(f"   High: {sum(1 for r in triage_results if r.priority == TriagePriority.HIGH)}")
        logger.info(f"   Medium: {sum(1 for r in triage_results if r.priority == TriagePriority.MEDIUM)}")
        logger.info(f"   Low: {sum(1 for r in triage_results if r.priority == TriagePriority.LOW)}")
        logger.info(f"   Archive: {sum(1 for r in triage_results if r.priority == TriagePriority.ARCHIVE)}")

        return triage_results

    def _triage_single_ask(self, ask: Dict[str, Any]) -> TriageResult:
        """Triage a single @ASK"""
        ask_id = ask.get("ask_text", "")[:50]  # Use first 50 chars as ID
        ask_text = ask.get("ask_text", "")
        category = ask.get("category", "general")
        priority = ask.get("priority", "normal")

        # Determine triage priority
        triage_priority = self._determine_triage_priority(ask_text, category, priority)

        # Determine Dewey classification
        dewey_classification = self._determine_dewey_classification(ask_text, category)

        # Determine holocron chapter
        holocron_chapter = self._determine_holocron_chapter(ask_text, category, dewey_classification)

        # Determine episode type
        episode_type = self._determine_episode_type(ask_text, category)

        return TriageResult(
            ask_id=ask_id,
            ask_text=ask_text,
            priority=triage_priority,
            category=category,
            dewey_classification=dewey_classification,
            holocron_chapter=holocron_chapter,
            episode_type=episode_type,
            reasoning=f"Triage based on category '{category}', priority '{priority}'"
        )

    def _determine_triage_priority(self, ask_text: str, category: str, priority: str) -> TriagePriority:
        """Determine triage priority"""
        text_lower = ask_text.lower()

        # Critical keywords
        if any(kw in text_lower for kw in ["critical", "urgent", "must", "immediate", "break", "error", "fail"]):
            return TriagePriority.CRITICAL

        # High priority keywords
        if any(kw in text_lower for kw in ["important", "priority", "soon", "fix", "resolve"]):
            return TriagePriority.HIGH

        # Archive keywords
        if any(kw in text_lower for kw in ["archive", "historical", "old", "legacy", "deprecated"]):
            return TriagePriority.ARCHIVE

        # Priority mapping
        priority_map = {
            "critical": TriagePriority.CRITICAL,
            "high": TriagePriority.HIGH,
            "normal": TriagePriority.MEDIUM,
            "low": TriagePriority.LOW
        }

        return priority_map.get(priority.lower(), TriagePriority.MEDIUM)

    def _determine_dewey_classification(self, ask_text: str, category: str) -> str:
        """Determine Dewey-Decimal classification"""
        text_lower = ask_text.lower()

        # Map based on keywords and category
        if "jarvis" in text_lower or "command" in text_lower or "control" in text_lower:
            return "Ω-000"
        elif "knowledge" in text_lower or "library" in text_lower or "catalog" in text_lower:
            return "Σ-001"
        elif "education" in text_lower or "learning" in text_lower or "holocron" in text_lower:
            return "Δ-002"
        elif "sync" in text_lower or "coordinate" in text_lower:
            return "Δ-003"
        elif "analytics" in text_lower or "monitor" in text_lower or "stats" in text_lower:
            return "Σ-004"
        elif "architecture" in text_lower or "design" in text_lower or "system" in text_lower:
            return "Δ-005"
        elif "operation" in text_lower or "task" in text_lower or "mission" in text_lower:
            return "β-006"
        elif "information" in text_lower or "data" in text_lower:
            return "000"
        elif "ai" in text_lower or "intelligence" in text_lower:
            return "600"
        elif "story" in text_lower or "narrative" in text_lower or "video" in text_lower:
            return "900"
        else:
            return "000"  # Default: Information Systems

    def _determine_holocron_chapter(self, ask_text: str, category: str, dewey: str) -> str:
        """Determine holocron chapter"""
        # Map Dewey to holocron chapter
        dewey_to_chapter = {
            "Ω-000": "Command & Control",
            "Σ-001": "Knowledge Management",
            "Δ-002": "Education & Learning",
            "Δ-003": "Synchronization",
            "Σ-004": "Analytics & Monitoring",
            "Δ-005": "Architecture & Design",
            "β-006": "Operations & Management",
            "000": "Information Systems",
            "600": "Technology & AI",
            "900": "History & Storytelling"
        }

        return dewey_to_chapter.get(dewey, "General")

    def _determine_episode_type(self, ask_text: str, category: str) -> EpisodeType:
        """Determine episode type"""
        text_lower = ask_text.lower()

        # Commercial keywords
        if any(kw in text_lower for kw in ["commercial", "ad", "sponsor", "poppa-palpatine", "aluminum falcon"]):
            return EpisodeType.COMMERCIAL

        # Ad keywords
        if any(kw in text_lower for kw in ["youtube", "creator", "subscribe", "channel"]):
            return EpisodeType.AD

        # Filler keywords (minimal)
        if any(kw in text_lower for kw in ["filler", "bonus", "extra"]):
            return EpisodeType.FILLER

        # Default: Story episode
        return EpisodeType.STORY

    def create_docuseries_structure(self) -> List[DocuseriesEpisode]:
        """Create YouTube docuseries structure with @SMART order of precedence"""
        logger.info("="*80)
        logger.info("📺 CREATING YOUTUBE DOCUSERIES STRUCTURE")
        logger.info("   Dewey-Decimal Notation in Titles")
        logger.info("   @SMART Order of Precedence")
        logger.info("="*80)

        # Group asks by holocron chapter and priority
        grouped_asks = self._group_asks_by_chapter()

        # Create episodes with @SMART order
        episodes = []
        episode_number = 1

        # @SMART Order of Precedence:
        # 1. Critical asks (must address first)
        # 2. High priority asks
        # 3. Medium priority asks (grouped by chapter)
        # 4. Low priority asks
        # 5. Commercial/Ad episodes (strategically placed)

        # Process by priority
        for priority in [TriagePriority.CRITICAL, TriagePriority.HIGH, TriagePriority.MEDIUM, TriagePriority.LOW]:
            priority_asks = [r for r in self.triage_results if r.priority == priority]

            # Group by chapter for better storytelling
            chapter_groups = {}
            for result in priority_asks:
                chapter = result.holocron_chapter
                if chapter not in chapter_groups:
                    chapter_groups[chapter] = []
                chapter_groups[chapter].append(result)

            # Create episodes for each chapter
            for chapter, asks in sorted(chapter_groups.items()):
                # Create story episodes (30-45 min)
                episode = self._create_story_episode(
                    episode_number=episode_number,
                    chapter=chapter,
                    asks=asks,
                    dewey=asks[0].dewey_classification if asks else "000"
                )
                episodes.append(episode)
                episode_number += 1

        # Add commercial episodes (Poppa-Palpatine & Aluminum Falcon)
        commercial_episodes = self._create_commercial_episodes(episode_number)
        episodes.extend(commercial_episodes)
        episode_number += len(commercial_episodes)

        # Add ad episodes for favorite YouTube creators
        ad_episodes = self._create_ad_episodes(episode_number)
        episodes.extend(ad_episodes)

        self.episodes = episodes

        # Save docuseries structure
        self._save_docuseries_structure()

        logger.info(f"✅ Docuseries structure created: {len(episodes)} episodes")
        logger.info(f"   Story Episodes: {sum(1 for e in episodes if e.episode_type == EpisodeType.STORY)}")
        logger.info(f"   Commercial Episodes: {sum(1 for e in episodes if e.episode_type == EpisodeType.COMMERCIAL)}")
        logger.info(f"   Ad Episodes: {sum(1 for e in episodes if e.episode_type == EpisodeType.AD)}")

        return episodes

    def _group_asks_by_chapter(self) -> Dict[str, List[TriageResult]]:
        """Group asks by holocron chapter"""
        grouped = {}
        for result in self.triage_results:
            chapter = result.holocron_chapter
            if chapter not in grouped:
                grouped[chapter] = []
            grouped[chapter].append(result)
        return grouped

    def _create_story_episode(self, episode_number: int, chapter: str, asks: List[TriageResult], dewey: str) -> DocuseriesEpisode:
        """Create a story episode"""
        # Create Dewey-Decimal title notation
        dewey_title = f"[{dewey}]"

        # Episode title with Dewey notation
        title = f"{dewey_title} Chapter {episode_number}: {chapter}"

        # Determine duration (30-45 min, based on number of asks)
        num_asks = len(asks)
        duration = min(45, max(30, num_asks * 2))  # 2 min per ask, capped at 45 min

        return DocuseriesEpisode(
            episode_number=episode_number,
            dewey_title=dewey_title,
            title=title,
            episode_type=EpisodeType.STORY,
            duration_minutes=duration,
            holocron_chapter=chapter,
            asks_addressed=[ask.ask_id for ask in asks],
            story_arc=f"Addressing {len(asks)} @ASKS in {chapter}",
            description=f"Real storytelling episode addressing {len(asks)} @ASKS from {chapter}. Dewey-Decimal classification: {dewey}",
            tags=["#storytelling", "#holocron", f"#{chapter.lower().replace(' ', '_')}", f"#{dewey}"]
        )

    def _create_commercial_episodes(self, start_episode: int) -> List[DocuseriesEpisode]:
        """Create Poppa-Palpatine & Aluminum Falcon commercial episodes"""
        commercials = []

        # Create 3-5 commercial episodes (strategically placed)
        for i in range(3):
            episode = DocuseriesEpisode(
                episode_number=start_episode + i,
                dewey_title="[COM-001]",
                title=f"[COM-001] Poppa-Palpatine & Aluminum Falcon - Commercial {i+1}",
                episode_type=EpisodeType.COMMERCIAL,
                duration_minutes=5,  # Short commercials
                holocron_chapter="Commercial Break",
                story_arc="Cartoon Network inspired commercial",
                description="Cartoon Network inspired Poppa-Palpatine & Aluminum Falcon commercial episode",
                tags=["#commercial", "#poppa-palpatine", "#aluminum-falcon", "#cartoon-network"],
                is_commercial=True
            )
            commercials.append(episode)

        return commercials

    def _create_ad_episodes(self, start_episode: int) -> List[DocuseriesEpisode]:
        """Create ad episodes for favorite YouTube content creators"""
        # This would be populated with actual favorite creators
        # For now, create template structure
        ad_episodes = []

        # Example: Create ad episodes (can be customized)
        favorite_creators = [
            "Creator 1",
            "Creator 2",
            "Creator 3"
        ]

        for i, creator in enumerate(favorite_creators):
            episode = DocuseriesEpisode(
                episode_number=start_episode + i,
                dewey_title="[AD-001]",
                title=f"[AD-001] Supporting {creator}",
                episode_type=EpisodeType.AD,
                duration_minutes=2,  # Short ads
                holocron_chapter="Community Support",
                story_arc=f"Ad for favorite YouTube creator: {creator}",
                description=f"Supporting our favorite YouTube content creator: {creator}",
                tags=["#ad", "#youtube", "#creator", "#support"],
                featured_creators=[creator]
            )
            ad_episodes.append(episode)

        return ad_episodes

    def _save_triage_results(self):
        """Save triage results"""
        try:
            triage_file = self.data_dir / "triage_results.json"
            with open(triage_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_asks": len(self.triage_results),
                    "triage_results": [
                        {
                            "ask_id": r.ask_id,
                            "ask_text": r.ask_text,
                            "priority": r.priority.value,
                            "category": r.category,
                            "dewey_classification": r.dewey_classification,
                            "holocron_chapter": r.holocron_chapter,
                            "episode_type": r.episode_type.value,
                            "reasoning": r.reasoning
                        }
                        for r in self.triage_results
                    ]
                }, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save triage results: {e}")

    def _save_docuseries_structure(self):
        """Save docuseries structure"""
        try:
            docuseries_file = self.data_dir / "docuseries_structure.json"
            with open(docuseries_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_episodes": len(self.episodes),
                    "episodes": [
                        {
                            "episode_number": e.episode_number,
                            "dewey_title": e.dewey_title,
                            "title": e.title,
                            "episode_type": e.episode_type.value,
                            "duration_minutes": e.duration_minutes,
                            "holocron_chapter": e.holocron_chapter,
                            "asks_addressed": e.asks_addressed,
                            "story_arc": e.story_arc,
                            "description": e.description,
                            "tags": e.tags,
                            "is_commercial": e.is_commercial,
                            "featured_creators": e.featured_creators
                        }
                        for e in self.episodes
                    ]
                }, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to save docuseries structure: {e}")

    def generate_video_titles(self) -> List[str]:
        """Generate video titles with Dewey-Decimal notation"""
        titles = []
        for episode in sorted(self.episodes, key=lambda e: e.episode_number):
            # Format: [DEWEY] Episode #: Title
            title = f"{episode.dewey_title} Episode {episode.episode_number}: {episode.title.replace(episode.dewey_title, '').strip()}"
            titles.append(title)
        return titles

    def get_smart_order_report(self) -> Dict[str, Any]:
        """Get @SMART order of precedence report"""
        return {
            "total_asks": len(self.all_asks),
            "triage_summary": {
                "critical": sum(1 for r in self.triage_results if r.priority == TriagePriority.CRITICAL),
                "high": sum(1 for r in self.triage_results if r.priority == TriagePriority.HIGH),
                "medium": sum(1 for r in self.triage_results if r.priority == TriagePriority.MEDIUM),
                "low": sum(1 for r in self.triage_results if r.priority == TriagePriority.LOW),
                "archive": sum(1 for r in self.triage_results if r.priority == TriagePriority.ARCHIVE)
            },
            "docuseries_summary": {
                "total_episodes": len(self.episodes),
                "story_episodes": sum(1 for e in self.episodes if e.episode_type == EpisodeType.STORY),
                "commercial_episodes": sum(1 for e in self.episodes if e.episode_type == EpisodeType.COMMERCIAL),
                "ad_episodes": sum(1 for e in self.episodes if e.episode_type == EpisodeType.AD),
                "total_duration_hours": sum(e.duration_minutes for e in self.episodes) / 60
            },
            "smart_order": [
                "1. Critical Priority @ASKS (Immediate)",
                "2. High Priority @ASKS (Soon)",
                "3. Medium Priority @ASKS (Normal)",
                "4. Low Priority @ASKS (Can Wait)",
                "5. Commercial Episodes (Strategic Placement)",
                "6. Ad Episodes (Community Support)"
            ]
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @ASK Stack Triage & Docuseries Organization")
    parser.add_argument("--triage", action="store_true", help="Triage all @ASK stacks")
    parser.add_argument("--docuseries", action="store_true", help="Create docuseries structure")
    parser.add_argument("--titles", action="store_true", help="Generate video titles")
    parser.add_argument("--report", action="store_true", help="Show @SMART order report")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("📺 JARVIS @ASK Stack Triage & Docuseries Organization")
    print("   Dewey-Decimal Catalog Notation for YouTube Docuseries")
    print("="*80 + "\n")

    system = JARVISAskStackTriageDocuseries()

    if args.triage:
        system.triage_all_asks()

    if args.docuseries:
        system.create_docuseries_structure()

    if args.titles:
        titles = system.generate_video_titles()
        print("📺 VIDEO TITLES (with Dewey-Decimal Notation)")
        print("="*80)
        for title in titles:
            print(f"   {title}")
        print("="*80 + "\n")

    if args.report:
        report = system.get_smart_order_report()
        print("📊 @SMART ORDER OF PRECEDENCE REPORT")
        print("="*80)
        print(json.dumps(report, indent=2, default=str))
        print("="*80 + "\n")

    if not any([args.triage, args.docuseries, args.titles, args.report]):
        print("Use --triage to triage all @ASK stacks")
        print("Use --docuseries to create docuseries structure")
        print("Use --titles to generate video titles")
        print("Use --report to show @SMART order report")
        print("="*80 + "\n")
