"""
JARVIS Roamwise Portal Word Cloud Generator
Generates word cloud from current topics, short@tags, AI/Bio tech, and work areas.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #WORDCLOUD #ROAMWISE
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import Counter
from datetime import datetime, timedelta

try:
    from wordcloud import WordCloud
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image
    WORDCLOUD_AVAILABLE = True
except ImportError:
    WORDCLOUD_AVAILABLE = False
    print("⚠️  wordcloud, matplotlib, numpy, or PIL not available. Install with: pip install wordcloud matplotlib numpy pillow")

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISRoamwiseWordCloud:
    """
    Generates word cloud for Roamwise Portal.

    Analyzes:
    - Short@tags usage
    - AI/Bio tech topics
    - Current work areas
    - Documentation topics
    - Code patterns
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize word cloud generator.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.shortag_registry = self.project_root / "config" / "shortag_registry.json"
        self.docs_dir = self.project_root / "docs"
        self.scripts_dir = self.project_root / "scripts" / "python"

        # Word frequencies
        self.word_frequencies: Dict[str, int] = {}

    def load_short_tags(self) -> Dict[str, int]:
        """
        Load short@tags from registry.

        Returns:
            Dictionary of tag frequencies
        """
        frequencies = {}

        if self.shortag_registry.exists():
            try:
                with open(self.shortag_registry, 'r', encoding='utf-8') as f:
                    registry = json.load(f)

                    # Count tags
                    if 'tags' in registry:
                        for tag_name, tag_data in registry['tags'].items():
                            # Tag name itself
                            frequencies[tag_name] = frequencies.get(tag_name, 0) + 10

                            # Category
                            if 'category' in tag_data:
                                cat = tag_data['category']
                                frequencies[cat] = frequencies.get(cat, 0) + 5

                            # Description keywords
                            if 'description' in tag_data:
                                desc = tag_data['description']
                                words = self._extract_keywords(desc)
                                for word in words:
                                    frequencies[word] = frequencies.get(word, 0) + 3

                            # Intent keywords
                            if 'intent' in tag_data:
                                intent = tag_data['intent']
                                words = self._extract_keywords(intent)
                                for word in words:
                                    frequencies[word] = frequencies.get(word, 0) + 2
            except Exception as e:
                logger.error(f"Failed to load short tags: {e}", exc_info=True)

        return frequencies

    def analyze_documentation(self) -> Dict[str, int]:
        """
        Analyze documentation for topics.

        Returns:
            Dictionary of topic frequencies
        """
        frequencies = {}

        if not self.docs_dir.exists():
            return frequencies

        # Keywords to look for
        tech_keywords = [
            'AI', 'artificial intelligence', 'machine learning', 'LLM', 'local-first',
            'MariaDB', 'database', 'NAS', 'JARVIS', 'LUMINA', 'SYPHON',
            'HK-47', 'MARVIN', 'ULTRON', 'KAIJU', 'Holocron', 'One Ring',
            'biotech', 'bio tech', 'genomics', 'healthcare', 'medical',
            'voice', 'hands-free', 'automation', 'workflow', 'integration',
            'container', 'Docker', 'N8N', 'MCP', 'API', 'REST',
            'security', 'encryption', 'vault', 'credentials',
            'TODO', 'task', 'project', 'system', 'architecture'
        ]

        for doc_file in self.docs_dir.rglob("*.md"):
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                    # Extract @tags (shift+2) - mentions
                    at_tags = re.findall(r'@[A-Z_]+|@[a-z]+', content)
                    for tag in at_tags:
                        frequencies[tag] = frequencies.get(tag, 0) + 5  # Higher weight for @tags

                    # Extract #tags (shift+3) - hashtags
                    hash_tags = re.findall(r'#[A-Z]+|#[a-z]+', content)
                    for tag in hash_tags:
                        frequencies[tag] = frequencies.get(tag, 0) + 5  # Higher weight for #tags

                    # Extract combined patterns like @DB[#DATABASE]
                    combined_tags = re.findall(r'@[A-Z]+\[#[A-Z]+\]', content)
                    for tag in combined_tags:
                        frequencies[tag] = frequencies.get(tag, 0) + 8  # Even higher for combined
                        # Also count components
                        at_part = re.search(r'@[A-Z]+', tag)
                        hash_part = re.search(r'#[A-Z]+', tag)
                        if at_part:
                            frequencies[at_part.group()] = frequencies.get(at_part.group(), 0) + 2
                        if hash_part:
                            frequencies[hash_part.group()] = frequencies.get(hash_part.group(), 0) + 2

                    # Check for keywords
                    content_lower = content.lower()
                    for keyword in tech_keywords:
                        keyword_lower = keyword.lower()
                        count = content_lower.count(keyword_lower)
                        if count > 0:
                            frequencies[keyword] = frequencies.get(keyword, 0) + count

                    # Extract title words
                    title_match = re.search(r'^#+\s+(.+)$', content, re.MULTILINE)
                    if title_match:
                        title = title_match.group(1)
                        words = self._extract_keywords(title)
                        for word in words:
                            frequencies[word] = frequencies.get(word, 0) + 1
            except Exception as e:
                logger.debug(f"Could not read {doc_file}: {e}")

        return frequencies

    def analyze_recent_work(self) -> Dict[str, int]:
        """
        Analyze recent work from scripts and data.

        Returns:
            Dictionary of work topic frequencies
        """
        frequencies = {}

        # Recent script topics
        if self.scripts_dir.exists():
            for script_file in self.scripts_dir.glob("*.py"):
                # File name keywords
                name_parts = script_file.stem.split('_')
                for part in name_parts:
                    if len(part) > 3:  # Skip short parts
                        frequencies[part] = frequencies.get(part, 0) + 1

                # Read file content
                try:
                    with open(script_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                        # Extract @tags (shift+2) - mentions in code
                        at_tags = re.findall(r'@[A-Z_]+|@[a-z]+', content)
                        for tag in at_tags:
                            frequencies[tag] = frequencies.get(tag, 0) + 3

                        # Extract #tags (shift+3) - hashtags in code
                        hash_tags = re.findall(r'#[A-Z]+|#[a-z]+', content)
                        for tag in hash_tags:
                            frequencies[tag] = frequencies.get(tag, 0) + 3

                        # Extract docstring
                        docstring_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
                        if docstring_match:
                            docstring = docstring_match.group(1)

                            # Extract tags from docstring
                            doc_at_tags = re.findall(r'@[A-Z_]+|@[a-z]+', docstring)
                            for tag in doc_at_tags:
                                frequencies[tag] = frequencies.get(tag, 0) + 2

                            doc_hash_tags = re.findall(r'#[A-Z]+|#[a-z]+', docstring)
                            for tag in doc_hash_tags:
                                frequencies[tag] = frequencies.get(tag, 0) + 2

                            words = self._extract_keywords(docstring)
                            for word in words:
                                frequencies[word] = frequencies.get(word, 0) + 1
                except Exception as e:
                    logger.debug(f"Could not read {script_file}: {e}")

        return frequencies

    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Input text

        Returns:
            List of keywords
        """
        # Remove special characters, keep alphanumeric and spaces
        text = re.sub(r'[^\w\s-]', ' ', text)

        # Split into words
        words = text.lower().split()

        # Filter: length > 2, not common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'from', 'as', 'if', 'it', 'its', 'system', 'systems'}

        keywords = [w for w in words if len(w) > 2 and w not in stop_words]

        return keywords

    def generate_word_frequencies(self) -> Dict[str, int]:
        """
        Generate complete word frequency dictionary.

        Returns:
            Dictionary of word frequencies
        """
        frequencies = Counter()

        # Load short@tags
        tag_freq = self.load_short_tags()
        frequencies.update(tag_freq)

        # Analyze documentation
        doc_freq = self.analyze_documentation()
        frequencies.update(doc_freq)

        # Analyze recent work
        work_freq = self.analyze_recent_work()
        frequencies.update(work_freq)

        # Add current session topics (from this conversation)
        session_topics = {
            'JARVIS': 50,
            'LUMINA': 40,
            'MariaDB': 35,
            'NAS': 35,
            'TODO': 30,
            'One Ring': 25,
            'Holocron': 25,
            'short@tags': 20,
            'HELPDESK': 15,
            'HOLOGRAM': 15,
            '@REC': 15,  # @tag (shift+2)
            '#RECOMMENDATIONS': 12,  # #tag (shift+3)
            'recommendations': 12,
            'conversational': 10,
            'auto-collapse': 10,
            'Grammarly': 8,
            'Chat Interface': 8,
            'siloed databases': 8,
            'living document': 7,
            'word cloud': 5,
            'Roamwise': 5,
            '@DB': 10,  # @tag (shift+2)
            '#DATABASE': 10,  # #tag (shift+3)
            '@DB[#DATABASE]': 15  # Combined pattern
        }
        frequencies.update(session_topics)

        # Boost short typing patterns (@ and #)
        # Find all @tags and #tags and boost them
        for word in list(frequencies.keys()):
            if word.startswith('@'):
                frequencies[word] = int(frequencies.get(word, 0) * 1.5)  # Boost @tags (shift+2)
            elif word.startswith('#'):
                frequencies[word] = int(frequencies.get(word, 0) * 1.5)  # Boost #tags (shift+3)

        self.word_frequencies = dict(frequencies)
        return self.word_frequencies

    def generate_wordcloud(self, output_path: Optional[Path] = None,
                          width: int = 1200, height: int = 800) -> Optional[Path]:
        """
        Generate word cloud image.

        Args:
            output_path: Output file path
            width: Image width
            height: Image height

        Returns:
            Path to generated image
        """
        if not WORDCLOUD_AVAILABLE:
            logger.error("WordCloud libraries not available")
            return None

        if not self.word_frequencies:
            self.generate_word_frequencies()

        if not self.word_frequencies:
            logger.warning("No word frequencies to generate cloud")
            return None

        # Prepare text for word cloud
        # Convert frequencies to text (weighted)
        text_parts = []
        for word, freq in self.word_frequencies.items():
            # Ensure freq is integer
            freq_int = int(freq)
            # Repeat word based on frequency
            text_parts.extend([word] * min(freq_int, 50))  # Cap at 50 repetitions

        text = ' '.join(text_parts)

        # Create word cloud
        wordcloud = WordCloud(
            width=width,
            height=height,
            background_color='white',
            colormap='viridis',
            max_words=200,
            relative_scaling=0.5,
            min_font_size=10,
            collocations=False
        ).generate(text)

        # Save image
        if output_path is None:
            output_path = self.project_root / "data" / "roamwise" / "wordcloud.png"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate and save
        plt.figure(figsize=(width/100, height/100), facecolor='white')
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.tight_layout(pad=0)
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()

        logger.info(f"Word cloud saved to: {output_path}")
        return output_path

    def generate_text_summary(self) -> str:
        """
        Generate text summary of word cloud.

        Returns:
            Formatted text summary
        """
        if not self.word_frequencies:
            self.generate_word_frequencies()

        # Sort by frequency
        sorted_words = sorted(self.word_frequencies.items(), key=lambda x: x[1], reverse=True)

        lines = []
        lines.append("📊 **Roamwise Portal Word Cloud - Current Topics**")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Total Unique Topics:** {len(sorted_words)}")
        lines.append("")

        # Top 30 topics
        lines.append("### 🔝 Top 30 Topics")
        for i, (word, freq) in enumerate(sorted_words[:30], 1):
            bar_length = int(freq / max([f for _, f in sorted_words[:30]]) * 20)
            bar = '█' * bar_length
            lines.append(f"{i:2d}. {word:30s} {bar} ({freq})")

        lines.append("")

        # Categories
        lines.append("### 📁 Categories")

        # Short@tags
        tag_words = [w for w, _ in sorted_words if w.startswith('@') or w.startswith('#')]
        if tag_words:
            lines.append(f"**Short@Tags:** {len(tag_words)}")
            lines.append(f"  Top: {', '.join(tag_words[:10])}")

        # AI/Tech
        ai_words = [w for w, _ in sorted_words if any(kw in w.lower() for kw in ['ai', 'intelligence', 'machine', 'learning', 'llm', 'model'])]
        if ai_words:
            lines.append(f"**AI/Tech:** {len(ai_words)}")
            lines.append(f"  Top: {', '.join(ai_words[:10])}")

        # Database
        db_words = [w for w, _ in sorted_words if any(kw in w.lower() for kw in ['database', 'mariadb', 'sql', 'db', 'data'])]
        if db_words:
            lines.append(f"**Database:** {len(db_words)}")
            lines.append(f"  Top: {', '.join(db_words[:10])}")

        # Systems
        system_words = [w for w, _ in sorted_words if any(kw in w.lower() for kw in ['jarvis', 'lumina', 'system', 'nas', 'holocron'])]
        if system_words:
            lines.append(f"**Systems:** {len(system_words)}")
            lines.append(f"  Top: {', '.join(system_words[:10])}")

        return "\n".join(lines)


def main():
    try:
        """CLI interface for word cloud generator."""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Roamwise Word Cloud Generator")
        parser.add_argument('--generate', action='store_true', help='Generate word cloud image')
        parser.add_argument('--summary', action='store_true', help='Show text summary')
        parser.add_argument('--output', type=str, help='Output file path')
        parser.add_argument('--width', type=int, default=1200, help='Image width')
        parser.add_argument('--height', type=int, default=800, help='Image height')

        args = parser.parse_args()

        generator = JARVISRoamwiseWordCloud()

        if args.summary or not args.generate:
            summary = generator.generate_text_summary()
            print(summary)

        if args.generate:
            output_path = Path(args.output) if args.output else None
            result = generator.generate_wordcloud(output_path, args.width, args.height)
            if result:
                print(f"\n✅ Word cloud saved to: {result}")
            else:
                print("\n❌ Failed to generate word cloud (libraries not available)")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()