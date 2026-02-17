#!/usr/bin/env python3
"""
Content Creation Engine - Books & YouTube Docuseries Generator

Uses SYPHON + Agents + @asks unified system to create:
1. Books from conversation history and project evolution
2. YouTube docuseries from sequential storytelling
3. Educational content from learning patterns
4. Entertainment content from narrative flow

This engine transforms the unified intelligence extraction system into
a powerful content creation pipeline.

Tags: #CONTENT #BOOKS #DOCUSERIES #YOUTUBE #EDUCATION #ENTERTAINMENT @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
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

logger = get_logger("ContentCreationEngine")

# Unified system integration
try:
    from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem
    UNIFIED_SYSTEM_AVAILABLE = True
except ImportError:
    UNIFIED_SYSTEM_AVAILABLE = False
    SYPHONAgentsAsksUnifiedSystem = None

# @asks restacker
try:
    from jarvis_restack_all_asks import ASKRestacker
    ASKS_AVAILABLE = True
except ImportError:
    ASKS_AVAILABLE = False
    ASKRestacker = None

# Holocron integration
try:
    from holocron_docuseries import HolocronDocuseriesManager
    HOLOCRON_AVAILABLE = True
except ImportError:
    HOLOCRON_AVAILABLE = False
    HolocronDocuseriesManager = None


class ContentType(Enum):
    """Types of content that can be generated"""
    BOOK = "book"
    DOCUSERIES = "docuseries"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    TUTORIAL = "tutorial"
    CASE_STUDY = "case_study"
    NARRATIVE = "narrative"


class ContentFormat(Enum):
    """Output formats for content"""
    MARKDOWN = "markdown"
    PDF = "pdf"
    EPUB = "epub"
    VIDEO_SCRIPT = "video_script"
    YOUTUBE_DESCRIPTION = "youtube_description"
    CHAPTER_OUTLINE = "chapter_outline"


@dataclass
class ContentChapter:
    """A chapter in a book or episode in a docuseries"""
    chapter_number: int
    title: str
    content: str
    summary: str
    key_points: List[str] = field(default_factory=list)
    timestamp: str = ""
    source_asks: List[str] = field(default_factory=list)
    intelligence_extracted: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentBook:
    """A complete book generated from project history"""
    title: str
    subtitle: str
    author: str
    chapters: List[ContentChapter] = field(default_factory=list)
    introduction: str = ""
    conclusion: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        data['chapters'] = [ch.to_dict() for ch in self.chapters]
        return data


@dataclass
class DocuseriesEpisode:
    """An episode in a YouTube docuseries"""
    episode_number: int
    title: str
    description: str
    script: str
    duration_minutes: int = 10
    key_moments: List[str] = field(default_factory=list)
    visuals_needed: List[str] = field(default_factory=list)
    source_asks: List[str] = field(default_factory=list)
    intelligence_extracted: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Docuseries:
    """A complete YouTube docuseries"""
    title: str
    description: str
    episodes: List[DocuseriesEpisode] = field(default_factory=list)
    playlist_description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['generated_at'] = self.generated_at.isoformat()
        data['episodes'] = [ep.to_dict() for ep in self.episodes]
        return data


class ContentCreationEngine:
    """
    Content Creation Engine

    Transforms unified intelligence extraction into books and docuseries
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize content creation engine"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.content_dir = self.data_dir / "content_creation"
        self.content_dir.mkdir(parents=True, exist_ok=True)

        # Unified system
        self.unified_system = None
        if UNIFIED_SYSTEM_AVAILABLE:
            try:
                self.unified_system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
                logger.info("✅ Unified system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Unified system not available: {e}")

        # @asks restacker
        self.ask_restacker = None
        if ASKS_AVAILABLE:
            try:
                self.ask_restacker = ASKRestacker(project_root=self.project_root)
                logger.info("✅ @asks restacker initialized")
            except Exception as e:
                logger.warning(f"⚠️  @asks restacker not available: {e}")

        # Holocron integration
        self.holocron = None
        if HOLOCRON_AVAILABLE:
            try:
                self.holocron = HolocronDocuseriesManager(project_root=self.project_root)
                logger.info("✅ Holocron docuseries manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  Holocron not available: {e}")

        logger.info("✅ Content Creation Engine initialized")

    def create_book_from_asks(self, 
                              title: str,
                              subtitle: str = "",
                              author: str = "JARVIS AI",
                              min_chapters: int = 5,
                              max_chapters: int = 20) -> Optional[ContentBook]:
        """
        Create a book from @asks timeline

        Transforms chronological @asks into a structured book with chapters
        """
        if not self.ask_restacker:
            logger.error("@asks restacker not available")
            return None

        try:
            logger.info(f"📚 Creating book: {title}")

            # Discover and restack all @asks
            all_asks = self.ask_restacker.discover_all_asks()
            if not all_asks:
                logger.warning("No @asks found")
                return None

            restacked_asks = self.ask_restacker.restack_asks(all_asks)
            timeline = self.ask_restacker.create_timeline(restacked_asks)

            # Group asks into chapters
            chapters = self._group_asks_into_chapters(timeline, min_chapters, max_chapters)

            # Create book structure
            book = ContentBook(
                title=title,
                subtitle=subtitle or f"From {len(restacked_asks)} Conversations to Complete Story",
                author=author,
                chapters=chapters,
                introduction=self._generate_introduction(title, len(restacked_asks)),
                conclusion=self._generate_conclusion(title, len(chapters)),
                metadata={
                    "total_asks": len(restacked_asks),
                    "total_chapters": len(chapters),
                    "generation_method": "unified_system_asks_timeline"
                }
            )

            logger.info(f"✅ Book created: {len(chapters)} chapters")
            return book

        except Exception as e:
            logger.error(f"Error creating book: {e}", exc_info=True)
            return None

    def create_docuseries_from_asks(self,
                                    title: str,
                                    description: str = "",
                                    episodes_per_season: int = 10,
                                    episode_duration_minutes: int = 10) -> Optional[Docuseries]:
        """
        Create a YouTube docuseries from @asks timeline

        Transforms chronological @asks into episodic video content
        """
        if not self.ask_restacker:
            logger.error("@asks restacker not available")
            return None

        try:
            logger.info(f"🎬 Creating docuseries: {title}")

            # Discover and restack all @asks
            all_asks = self.ask_restacker.discover_all_asks()
            if not all_asks:
                logger.warning("No @asks found")
                return None

            restacked_asks = self.ask_restacker.restack_asks(all_asks)
            timeline = self.ask_restacker.create_timeline(restacked_asks)

            # Group asks into episodes
            episodes = self._group_asks_into_episodes(timeline, episodes_per_season, episode_duration_minutes)

            # Create docuseries structure
            docuseries = Docuseries(
                title=title,
                description=description or f"An epic journey through {len(restacked_asks)} conversations",
                episodes=episodes,
                playlist_description=self._generate_playlist_description(title, len(episodes)),
                tags=self._generate_tags(title, restacked_asks),
                metadata={
                    "total_asks": len(restacked_asks),
                    "total_episodes": len(episodes),
                    "generation_method": "unified_system_asks_timeline"
                }
            )

            logger.info(f"✅ Docuseries created: {len(episodes)} episodes")
            return docuseries

        except Exception as e:
            logger.error(f"Error creating docuseries: {e}", exc_info=True)
            return None

    def _group_asks_into_chapters(self, timeline: List[Dict[str, Any]], 
                                  min_chapters: int, max_chapters: int) -> List[ContentChapter]:
        """Group timeline asks into book chapters"""
        if not timeline:
            return []

        # Calculate optimal chapter count
        total_asks = len(timeline)
        optimal_chapters = min(max_chapters, max(min_chapters, total_asks // 10))

        # Group asks into chapters
        asks_per_chapter = max(1, total_asks // optimal_chapters)
        chapters = []

        for chapter_num in range(1, optimal_chapters + 1):
            start_idx = (chapter_num - 1) * asks_per_chapter
            end_idx = min(start_idx + asks_per_chapter, total_asks)

            if start_idx >= total_asks:
                break

            chapter_asks = timeline[start_idx:end_idx]

            # Extract key information
            chapter_title = self._generate_chapter_title(chapter_asks, chapter_num)
            chapter_content = self._generate_chapter_content(chapter_asks)
            chapter_summary = self._generate_chapter_summary(chapter_asks)
            key_points = [ask.get("text", "")[:100] for ask in chapter_asks[:5]]

            chapter = ContentChapter(
                chapter_number=chapter_num,
                title=chapter_title,
                content=chapter_content,
                summary=chapter_summary,
                key_points=key_points,
                timestamp=chapter_asks[0].get("timestamp", "") if chapter_asks else "",
                source_asks=[ask.get("text", "") for ask in chapter_asks],
                intelligence_extracted=self._extract_intelligence_from_asks(chapter_asks)
            )

            chapters.append(chapter)

        return chapters

    def _group_asks_into_episodes(self, timeline: List[Dict[str, Any]],
                                  episodes_per_season: int,
                                  duration_minutes: int) -> List[DocuseriesEpisode]:
        """Group timeline asks into docuseries episodes"""
        if not timeline:
            return []

        # Calculate asks per episode
        total_asks = len(timeline)
        asks_per_episode = max(1, total_asks // episodes_per_season)

        episodes = []

        for episode_num in range(1, episodes_per_season + 1):
            start_idx = (episode_num - 1) * asks_per_episode
            end_idx = min(start_idx + asks_per_episode, total_asks)

            if start_idx >= total_asks:
                break

            episode_asks = timeline[start_idx:end_idx]

            # Generate episode content
            episode_title = self._generate_episode_title(episode_asks, episode_num)
            episode_description = self._generate_episode_description(episode_asks)
            episode_script = self._generate_episode_script(episode_asks, duration_minutes)
            key_moments = [ask.get("text", "")[:80] for ask in episode_asks[:5]]
            visuals_needed = self._generate_visuals_list(episode_asks)

            episode = DocuseriesEpisode(
                episode_number=episode_num,
                title=episode_title,
                description=episode_description,
                script=episode_script,
                duration_minutes=duration_minutes,
                key_moments=key_moments,
                visuals_needed=visuals_needed,
                source_asks=[ask.get("text", "") for ask in episode_asks],
                intelligence_extracted=self._extract_intelligence_from_asks(episode_asks)
            )

            episodes.append(episode)

        return episodes

    def _generate_chapter_title(self, asks: List[Dict[str, Any]], chapter_num: int) -> str:
        """Generate a chapter title from asks"""
        if not asks:
            return f"Chapter {chapter_num}"

        # Extract category or key theme
        categories = [ask.get("category", "") for ask in asks if ask.get("category")]
        if categories:
            most_common = max(set(categories), key=categories.count)
            return f"Chapter {chapter_num}: {most_common.title()}"

        return f"Chapter {chapter_num}: The Journey Continues"

    def _generate_chapter_content(self, asks: List[Dict[str, Any]]) -> str:
        """Generate chapter content from asks"""
        content_lines = []

        for i, ask in enumerate(asks, 1):
            ask_text = ask.get("text", "")
            priority = ask.get("priority", "normal")
            category = ask.get("category", "general")

            content_lines.append(f"\n## {i}. {ask_text}")
            content_lines.append(f"\n**Priority:** {priority.upper()} | **Category:** {category}")

            if ask.get("context"):
                context = ask.get("context", "")[:300]
                content_lines.append(f"\n**Context:** {context}")

        return "\n".join(content_lines)

    def _generate_chapter_summary(self, asks: List[Dict[str, Any]]) -> str:
        """Generate chapter summary"""
        if not asks:
            return ""

        total_asks = len(asks)
        categories = [ask.get("category", "") for ask in asks if ask.get("category")]
        most_common_category = max(set(categories), key=categories.count) if categories else "general"

        return f"This chapter covers {total_asks} key requests, primarily focused on {most_common_category}."

    def _generate_episode_title(self, asks: List[Dict[str, Any]], episode_num: int) -> str:
        """Generate episode title"""
        if not asks:
            return f"Episode {episode_num}"

        # Use first ask as inspiration
        first_ask = asks[0].get("text", "")[:50]
        return f"Episode {episode_num}: {first_ask}"

    def _generate_episode_description(self, asks: List[Dict[str, Any]]) -> str:
        """Generate YouTube episode description"""
        if not asks:
            return ""

        description_lines = [
            f"In this episode, we explore {len(asks)} key moments in the journey.",
            "",
            "**Key Topics:**"
        ]

        for ask in asks[:5]:
            ask_text = ask.get("text", "")[:100]
            description_lines.append(f"- {ask_text}")

        return "\n".join(description_lines)

    def _generate_episode_script(self, asks: List[Dict[str, Any]], duration_minutes: int) -> str:
        """Generate video script for episode"""
        script_lines = [
            f"# Episode Script ({duration_minutes} minutes)",
            "",
            "## Introduction",
            f"Welcome to this episode where we explore {len(asks)} fascinating moments.",
            "",
            "## Main Content"
        ]

        for i, ask in enumerate(asks, 1):
            ask_text = ask.get("text", "")
            script_lines.append(f"\n### Moment {i}")
            script_lines.append(f"{ask_text}")
            script_lines.append(f"[Visual: {ask.get('category', 'general')} related content]")

        script_lines.append("\n## Conclusion")
        script_lines.append("Join us next time as we continue this incredible journey.")

        return "\n".join(script_lines)

    def _generate_visuals_list(self, asks: List[Dict[str, Any]]) -> List[str]:
        """Generate list of visuals needed for episode"""
        visuals = []
        categories = set([ask.get("category", "general") for ask in asks])

        for category in categories:
            visuals.append(f"{category.title()} related graphics")

        return visuals

    def _generate_introduction(self, title: str, total_asks: int) -> str:
        """Generate book introduction"""
        return f"""
# Introduction

This book was generated from {total_asks} conversations, requests, and moments of discovery.

**{title}** represents a journey through time, ideas, and innovation. Each chapter tells a story
of exploration, problem-solving, and creation.

What you're about to read is not just a collection of requests—it's a narrative of how
intelligence, automation, and human-AI collaboration can create something extraordinary.

Welcome to the story.
"""

    def _generate_conclusion(self, title: str, total_chapters: int) -> str:
        """Generate book conclusion"""
        return f"""
# Conclusion

We've journeyed through {total_chapters} chapters, each representing a step forward in
understanding, building, and creating.

**{title}** is more than a book—it's a testament to the power of conversation, intelligence
extraction, and narrative generation.

The story continues. The journey never ends.

Thank you for reading.
"""

    def _generate_playlist_description(self, title: str, total_episodes: int) -> str:
        """Generate YouTube playlist description"""
        return f"""
{title} - A {total_episodes}-episode docuseries exploring the journey of innovation,
discovery, and creation through conversation and intelligence extraction.

**About This Series:**
This docuseries was generated from real conversations, requests, and moments of discovery,
transformed into engaging narrative content through AI-powered intelligence extraction.

**Episodes:**
{total_episodes} episodes covering the complete journey from beginning to present.

Subscribe for more content!
"""

    def _generate_tags(self, title: str, asks: List[Dict[str, Any]]) -> List[str]:
        """Generate YouTube tags"""
        tags = ["AI", "Technology", "Innovation", "Documentary", "Education"]

        categories = set([ask.get("category", "") for ask in asks if ask.get("category")])
        tags.extend([cat.title() for cat in categories if cat])

        return tags[:20]  # YouTube limit

    def _extract_intelligence_from_asks(self, asks: List[Dict[str, Any]]) -> List[str]:
        """Extract intelligence from asks using unified system"""
        if not self.unified_system or not self.unified_system.syphon:
            return []

        try:
            # Combine ask texts
            ask_text = "\n".join([ask.get("text", "") for ask in asks])

            if not ask_text.strip():
                return []

            # Extract intelligence
            from syphon import DataSourceType
            result = self.unified_system.syphon.extract(
                DataSourceType.IDE,
                ask_text,
                metadata={"source": "content_creation", "asks": len(asks)}
            )

            if result.success and result.data:
                intelligence = []
                if result.data.actionable_items:
                    intelligence.extend(result.data.actionable_items[:5])
                if result.data.intelligence:
                    intelligence.extend(result.data.intelligence[:5])
                return intelligence

        except Exception as e:
            logger.debug(f"Error extracting intelligence: {e}")

        return []

    def save_book(self, book: ContentBook, format: ContentFormat = ContentFormat.MARKDOWN) -> Path:
        """Save book to file"""
        if format == ContentFormat.MARKDOWN:
            return self._save_book_markdown(book)
        else:
            logger.warning(f"Format {format} not yet implemented")
            return self._save_book_markdown(book)

    def _save_book_markdown(self, book: ContentBook) -> Path:
        try:
            """Save book as Markdown"""
            output_file = self.content_dir / f"{book.title.replace(' ', '_')}_book.md"

            content = []
            content.append(f"# {book.title}")
            if book.subtitle:
                content.append(f"## {book.subtitle}")
            content.append(f"\n**Author:** {book.author}")
            content.append(f"**Generated:** {book.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
            content.append("\n---\n")

            content.append(book.introduction)
            content.append("\n---\n")

            for chapter in book.chapters:
                content.append(f"\n# {chapter.title}")
                content.append(f"\n{chapter.summary}\n")
                content.append(chapter.content)
                content.append("\n---\n")

            content.append(book.conclusion)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))

            logger.info(f"✅ Book saved: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in _save_book_markdown: {e}", exc_info=True)
            raise
    def save_docuseries(self, docuseries: Docuseries) -> Path:
        try:
            """Save docuseries to file"""
            output_file = self.content_dir / f"{docuseries.title.replace(' ', '_')}_docuseries.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(docuseries.to_dict(), f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"✅ Docuseries saved: {output_file}")
            return output_file


        except Exception as e:
            self.logger.error(f"Error in save_docuseries: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("📚 Content Creation Engine - Books & YouTube Docuseries Generator")
    print("="*80 + "\n")

    engine = ContentCreationEngine()

    # Create a book
    print("📖 Creating book from @asks...")
    book = engine.create_book_from_asks(
        title="The Lumina Project: A Journey Through Conversation",
        subtitle="From Ideas to Intelligence",
        author="JARVIS AI"
    )

    if book:
        print(f"✅ Book created: {len(book.chapters)} chapters")
        book_file = engine.save_book(book)
        print(f"💾 Saved: {book_file.name}")

    # Create a docuseries
    print("\n🎬 Creating docuseries from @asks...")
    docuseries = engine.create_docuseries_from_asks(
        title="Lumina: The AI-Powered Development Ecosystem",
        description="An epic journey through innovation and discovery",
        episodes_per_season=10,
        episode_duration_minutes=10
    )

    if docuseries:
        print(f"✅ Docuseries created: {len(docuseries.episodes)} episodes")
        docuseries_file = engine.save_docuseries(docuseries)
        print(f"💾 Saved: {docuseries_file.name}")

    print("\n✅ Content Creation Engine Test Complete")
    print("="*80 + "\n")
