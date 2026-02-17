#!/usr/bin/env python3
"""
Lumina Digest - Modern AI-Inspired Reader's Digest

Unified knowledge repository that condenses and curates knowledge from:
- @holocron - Crystallized knowledge archive
- YouTube Video Empire - Video content library
- Living Documentation - Continuously updated
- R5 Living Context - Aggregated intelligence

Into digestible, curated summaries - just like Reader's Digest condenses articles.

Tags: #LUMINA_DIGEST #READERS_DIGEST #CURATION #SUMMARIZATION @JARVIS @R5 @LUMINA
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime
import json
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaDigest")


class LuminaDigest:
    """
    Lumina Digest - Modern AI-Inspired Reader's Digest

    Condenses and curates knowledge from all sources into digestible formats:
    - Holocron Archive (@holocron) - Crystallized wisdom
    - YouTube Video Empire - Video content
    - Living Documentation - System docs
    - R5 Living Context Matrix - Aggregated intelligence

    Just like Reader's Digest condenses articles, Lumina Digest condenses knowledge.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize Lumina Digest.

        Args:
            project_root: Project root directory
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent

        # Knowledge source paths
        self.holocron_path = self.project_root / "data" / "holocron"
        self.youtube_path = self.project_root / "data" / "youtube"
        self.docs_path = self.project_root / "docs"
        self.digest_index_path = self.project_root / "data" / "lumina_digest_index.json"

        # Initialize indexes
        self.holocron_index = {}
        self.youtube_index = {}
        self.docs_index = {}
        self.unified_index = {}

        logger.info("📚 Initializing Lumina Digest (Reader's Digest)...")
        self._load_indexes()
        logger.info("✅ Lumina Digest initialized")

    def _load_indexes(self) -> None:
        """Load all knowledge indexes"""
        # Load holocron index
        holocron_index_file = self.holocron_path / "HOLOCRON_INDEX.json"
        if holocron_index_file.exists():
            try:
                with open(holocron_index_file, 'r', encoding='utf-8') as f:
                    self.holocron_index = json.load(f)
                logger.info(f"✅ Loaded {len(self.holocron_index.get('entries', {}))} holocron entries")
            except Exception as e:
                logger.warning(f"Could not load holocron index: {e}")

        # Load YouTube index (if exists)
        youtube_index_file = self.youtube_path / "youtube_index.json"
        if youtube_index_file.exists():
            try:
                with open(youtube_index_file, 'r', encoding='utf-8') as f:
                    self.youtube_index = json.load(f)
                logger.info(f"✅ Loaded {len(self.youtube_index.get('videos', {}))} YouTube videos")
            except Exception as e:
                logger.warning(f"Could not load YouTube index: {e}")

        # Load unified digest index (if exists)
        if self.digest_index_path.exists():
            try:
                with open(self.digest_index_path, 'r', encoding='utf-8') as f:
                    self.unified_index = json.load(f)
                logger.info("✅ Loaded unified digest index")
            except Exception as e:
                logger.warning(f"Could not load unified index: {e}")

    def search(
        self,
        query: str,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Search across all knowledge sources.

        Args:
            query: Search query
            source: Optional source filter ('holocron', 'youtube', 'docs')

        Returns:
            Search results from all sources
        """
        results = {
            'query': query,
            'holocron': [],
            'youtube': [],
            'docs': [],
            'total': 0
        }

        # Search holocron
        if not source or source == 'holocron':
            holocron_results = self._search_holocron(query)
            results['holocron'] = holocron_results

        # Search YouTube
        if not source or source == 'youtube':
            youtube_results = self._search_youtube(query)
            results['youtube'] = youtube_results

        # Search docs
        if not source or source == 'docs':
            docs_results = self._search_docs(query)
            results['docs'] = docs_results

        results['total'] = (
            len(results['holocron']) +
            len(results['youtube']) +
            len(results['docs'])
        )

        return results

    def _search_holocron(self, query: str) -> List[Dict[str, Any]]:
        """Search holocron archive"""
        results = []
        query_lower = query.lower()

        entries = self.holocron_index.get('entries', {})
        for category, category_entries in entries.items():
            if isinstance(category_entries, dict):
                for entry_id, entry in category_entries.items():
                    if isinstance(entry, dict):
                        # Simple text search
                        title = entry.get('title', '').lower()
                        tags = ' '.join(entry.get('tags', [])).lower()
                        content = f"{title} {tags}"

                        if query_lower in content:
                            results.append({
                                'id': entry_id,
                                'type': 'holocron',
                                'category': category,
                                'title': entry.get('title'),
                                'location': entry.get('location'),
                                'tags': entry.get('tags', []),
                                'match_score': self._calculate_match_score(query_lower, content)
                            })

        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

    def _search_youtube(self, query: str) -> List[Dict[str, Any]]:
        """Search YouTube content"""
        results = []
        query_lower = query.lower()

        videos = self.youtube_index.get('videos', {})
        for video_id, video in videos.items():
            if isinstance(video, dict):
                title = video.get('title', '').lower()
                description = video.get('description', '').lower()
                content = f"{title} {description}"

                if query_lower in content:
                    results.append({
                        'id': video_id,
                        'type': 'youtube',
                        'title': video.get('title'),
                        'url': video.get('url'),
                        'match_score': self._calculate_match_score(query_lower, content)
                    })

        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

    def _search_docs(self, query: str) -> List[Dict[str, Any]]:
        """Search documentation"""
        results = []
        query_lower = query.lower()

        # Simple file-based search
        if self.docs_path.exists():
            for doc_file in self.docs_path.rglob("*.md"):
                try:
                    content = doc_file.read_text(encoding='utf-8').lower()
                    if query_lower in content:
                        results.append({
                            'id': str(doc_file.relative_to(self.project_root)),
                            'type': 'docs',
                            'title': doc_file.stem,
                            'path': str(doc_file.relative_to(self.project_root)),
                            'match_score': self._calculate_match_score(query_lower, content)
                        })
                except Exception as e:
                    logger.debug(f"Could not read {doc_file}: {e}")

        # Sort by match score
        results.sort(key=lambda x: x['match_score'], reverse=True)
        return results

    def _calculate_match_score(self, query: str, content: str) -> float:
        """Calculate match score (simple frequency)"""
        query_words = query.split()
        matches = sum(1 for word in query_words if word in content)
        return matches / len(query_words) if query_words else 0.0

    def get_holocron(self, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get holocron entry by ID"""
        entries = self.holocron_index.get('entries', {})
        for category, category_entries in entries.items():
            if isinstance(category_entries, dict):
                if entry_id in category_entries:
                    entry = category_entries[entry_id].copy()
                    entry['category'] = category
                    return entry
        return None

    def get_related_content(
        self,
        entry_id: str,
        entry_type: str = 'holocron'
    ) -> Dict[str, Any]:
        """
        Get related content across all sources.

        Args:
            entry_id: Entry ID
            entry_type: Type of entry ('holocron', 'youtube', 'docs')

        Returns:
            Related content from all sources
        """
        related = {
            'holocron': [],
            'youtube': [],
            'docs': []
        }

        # Get entry
        if entry_type == 'holocron':
            entry = self.get_holocron(entry_id)
            if entry:
                # Extract keywords from entry
                keywords = entry.get('tags', []) + [entry.get('title', '')]
                query = ' '.join(keywords)

                # Search related content
                results = self.search(query)
                related['youtube'] = results['youtube'][:5]  # Top 5
                related['docs'] = results['docs'][:5]  # Top 5

        return related

    def get_youtube_video(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get YouTube video by ID"""
        videos = self.youtube_index.get('videos', {})
        return videos.get(video_id)

    def get_transcript(self, video_id: str) -> Optional[str]:
        try:
            """Get transcript for YouTube video"""
            # Placeholder - would load from transcript file
            transcript_path = self.youtube_path / "transcripts" / f"{video_id}.txt"
            if transcript_path.exists():
                return transcript_path.read_text(encoding='utf-8')
            return None

        except Exception as e:
            self.logger.error(f"Error in get_transcript: {e}", exc_info=True)
            raise
    def get_stats(self) -> Dict[str, Any]:
        try:
            """Get statistics about Lumina Digest"""
            return {
                'holocron_entries': len(self.holocron_index.get('entries', {})),
                'youtube_videos': len(self.youtube_index.get('videos', {})),
                'docs_count': len(list(self.docs_path.rglob("*.md"))) if self.docs_path.exists() else 0,
                'total_knowledge_items': (
                    len(self.holocron_index.get('entries', {})) +
                    len(self.youtube_index.get('videos', {})) +
                    (len(list(self.docs_path.rglob("*.md"))) if self.docs_path.exists() else 0)
                )
            }

        except Exception as e:
            self.logger.error(f"Error in get_stats: {e}", exc_info=True)
            raise
    def generate_weekly_digest(self) -> Dict[str, Any]:
        """
        Generate weekly digest - curated summary of week's knowledge.

        Returns:
            Weekly digest with cover story, features, quick tips, trending
        """
        # Get recent content (last 7 days)
        # This is a placeholder - would filter by date
        recent_holocron = list(self.holocron_index.get('entries', {}).values())[:5]
        recent_docs = self._search_docs("")[:5]  # Get recent docs

        digest = {
            'title': 'Lumina Digest - Weekly Edition',
            'date': datetime.now().isoformat(),
            'cover_story': {
                'title': 'Most Important Topic This Week',
                'content': 'Summary of most important knowledge...',
                'source': 'holocron'
            },
            'features': [
                {
                    'title': entry.get('title', 'Untitled'),
                    'summary': f"Summary of {entry.get('title', 'entry')}...",
                    'source': 'holocron',
                    'location': entry.get('location')
                }
                for entry in recent_holocron[:3]
            ],
            'quick_tips': [
                'Tip 1: Memory optimization...',
                'Tip 2: Tool agnosticism...',
                'Tip 3: Stay agile...'
            ],
            'trending': [
                'Memory optimization',
                'Tool agnosticism',
                'AOS architecture'
            ],
            'deep_dives': [
                {
                    'title': doc['title'],
                    'path': doc['path'],
                    'summary': f"Deep dive into {doc['title']}..."
                }
                for doc in recent_docs[:2]
            ]
        }

        return digest

    def generate_topic_digest(self, topic: str) -> Dict[str, Any]:
        """
        Generate topic-specific digest.

        Args:
            topic: Topic to generate digest for

        Returns:
            Topic digest with curated content
        """
        # Search for topic across all sources
        results = self.search(topic)

        digest = {
            'topic': topic,
            'title': f'Lumina Digest - {topic.title()}',
            'date': datetime.now().isoformat(),
            'summary': f"Curated content about {topic}...",
            'holocron_entries': results['holocron'][:5],
            'youtube_videos': results['youtube'][:5],
            'documentation': results['docs'][:5],
            'key_points': [
                f"Key point 1 about {topic}...",
                f"Key point 2 about {topic}...",
                f"Key point 3 about {topic}..."
            ],
            'quick_reference': f"Quick reference for {topic}..."
        }

        return digest

    def generate_quick_reference(self, topic: str) -> str:
        """
        Generate one-page quick reference card.

        Args:
            topic: Topic for quick reference

        Returns:
            One-page summary in markdown format
        """
        results = self.search(topic)

        quick_ref = f"""# {topic.title()} - Quick Reference

## Key Points
- Point 1: Summary from holocron/docs
- Point 2: Summary from holocron/docs
- Point 3: Summary from holocron/docs

## Related Holocron Entries
{chr(10).join(f"- {entry['title']}" for entry in results['holocron'][:3])}

## Related Documentation
{chr(10).join(f"- {doc['title']}" for doc in results['docs'][:3])}

## Action Items
- [ ] Action item 1
- [ ] Action item 2
- [ ] Action item 3

---
*Generated by Lumina Digest - Reader's Digest for AI*
"""

        return quick_ref

    def get_digestible_summary(
        self,
        entry_id: str,
        entry_type: str = 'holocron',
        summary_level: str = 'executive'
    ) -> Dict[str, Any]:
        """
        Get digestible summary of content.

        Args:
            entry_id: Entry ID
            entry_type: Type of entry ('holocron', 'youtube', 'docs')
            summary_level: 'executive', 'detailed', 'quick'

        Returns:
            Digestible summary
        """
        if entry_type == 'holocron':
            entry = self.get_holocron(entry_id)
            if entry:
                return {
                    'id': entry_id,
                    'type': 'holocron',
                    'title': entry.get('title'),
                    'executive_summary': f"Executive summary of {entry.get('title')}...",
                    'detailed_summary': f"Detailed summary of {entry.get('title')}...",
                    'quick_summary': f"Quick summary of {entry.get('title')}...",
                    'key_points': entry.get('tags', []),
                    'location': entry.get('location')
                }

        return {'error': f'Entry {entry_id} not found'}


def main():
    """Example usage"""
    print("=" * 80)
    print("📚 LUMINA DIGEST - READER'S DIGEST FOR AI")
    print("=" * 80)
    print()

    # Initialize
    digest = LuminaDigest()

    # Get stats
    stats = digest.get_stats()
    print("KNOWLEDGE STATISTICS:")
    print("-" * 80)
    print(f"  Holocron Entries: {stats['holocron_entries']}")
    print(f"  YouTube Videos: {stats['youtube_videos']}")
    print(f"  Documentation Files: {stats['docs_count']}")
    print(f"  Total Knowledge Items: {stats['total_knowledge_items']}")
    print()

    # Generate weekly digest
    print("WEEKLY DIGEST:")
    print("-" * 80)
    weekly = digest.generate_weekly_digest()
    print(f"Title: {weekly['title']}")
    print(f"Cover Story: {weekly['cover_story']['title']}")
    print(f"Features: {len(weekly['features'])}")
    print(f"Quick Tips: {len(weekly['quick_tips'])}")
    print()

    # Generate topic digest
    print("TOPIC DIGEST EXAMPLE:")
    print("-" * 80)
    topic = digest.generate_topic_digest("memory optimization")
    print(f"Topic: {topic['topic']}")
    print(f"Holocron Entries: {len(topic['holocron_entries'])}")
    print(f"Documentation: {len(topic['documentation'])}")
    print()

    # Generate quick reference
    print("QUICK REFERENCE EXAMPLE:")
    print("-" * 80)
    quick_ref = digest.generate_quick_reference("memory optimization")
    print(quick_ref[:500] + "...")
    print()

    print("=" * 80)
    print("📚 Lumina Digest - Condensing knowledge into digestible formats")
    print("=" * 80)


if __name__ == "__main__":


    main()