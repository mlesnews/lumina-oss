#!/usr/bin/env python3
"""
Short-Tagging System - Standard-Modularization Portable Programming Logic

AKA "SHORT-TAGGING" with all applicable inceptional conceptions of 
"@TAG[# SHORTTAGGING-CONTEXTUAL-LANGUAGE] AI CHAT SHORTHAND LANGUAGE/INFERENCE-LAYER"

Tags: #SHORTTAGGING #AICHATUI #METATAGGING #SHORTHAND #INFERENCE @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ShortTaggingSystem")


class TagType(Enum):
    """Tag type enumeration"""
    MENTION = "mention"
    HASHTAG = "hashtag"


class TagCategory(Enum):
    """Tag category enumeration"""
    SYSTEM = "system"
    TOOL = "tool"
    CONCEPT = "concept"
    PRINCIPLE = "principle"
    PROCESS = "process"
    QUALITY = "quality"
    POWER_WORD = "power_word"
    INSIGHT = "insight"


@dataclass
class TagDefinition:
    """Tag definition with all properties"""
    type: str
    category: str
    description: str
    context_weight: float
    ai_weight: float
    human_weight: float
    precedence: Optional[int] = None
    alias_of: Optional[str] = None
    pipe_to: Optional[str] = None
    usage: Optional[str] = None
    examples: Optional[List[str]] = None
    module: Optional[str] = None
    class_name: Optional[str] = None
    related: Optional[List[str]] = None
    integration: Optional[Dict] = None
    force_multipliers: Optional[List[str]] = None
    workflow: Optional[Dict] = None
    principle: Optional[str] = None
    inceptional_conceptions: Optional[List[str]] = None

    def __post_init__(self):
        """Validate tag definition"""
        if not 0.0 <= self.context_weight <= 1.0:
            raise ValueError(f"context_weight must be 0.0-1.0, got {self.context_weight}")
        if not 0.0 <= self.ai_weight <= 1.0:
            raise ValueError(f"ai_weight must be 0.0-1.0, got {self.ai_weight}")
        if not 0.0 <= self.human_weight <= 1.0:
            raise ValueError(f"human_weight must be 0.0-1.0, got {self.human_weight}")


@dataclass
class TagContext:
    """Context extracted from tags"""
    systems: List[str] = field(default_factory=list)
    concepts: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    total_context_weight: float = 0.0
    total_ai_weight: float = 0.0
    total_human_weight: float = 0.0
    tag_definitions: Dict[str, TagDefinition] = field(default_factory=dict)
    relationships: Dict[str, List[str]] = field(default_factory=dict)


class ShortTaggingSystem:
    """
    Short-Tagging System - Standard-Modularization Portable Programming Logic

    Provides:
    - Tag registry management
    - Discovery engine
    - Extrapolation engine
    - Context building
    - Pattern recognition
    """

    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize short-tagging system.

        Args:
            registry_path: Path to shortag_registry.json (default: config/shortag_registry.json)
        """
        if registry_path is None:
            registry_path = project_root / "config" / "shortag_registry.json"

        self.registry_path = Path(registry_path)
        self.tags: Dict[str, TagDefinition] = {}
        self.metadata: Dict = {}
        self.load()

    def load(self) -> None:
        """Load registry from JSON file"""
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract metadata
            self.metadata = data.get("_metadata", {})

            # Load tags
            for tag_name, tag_data in data.items():
                if tag_name != "_metadata":
                    try:
                        # Create a copy to avoid modifying the original dict during iteration
                        tag_data_copy = tag_data.copy()

                        # Convert "class" to "class_name" for compatibility
                        # This handles the mismatch between JSON registry ("class") and dataclass field ("class_name")
                        if "class" in tag_data_copy and "class_name" not in tag_data_copy:
                            tag_data_copy["class_name"] = tag_data_copy.pop("class")

                        # Get valid field names from TagDefinition
                        valid_fields = {f.name for f in TagDefinition.__dataclass_fields__.values()}

                        # Filter to only valid fields (removes extra fields like api_server, data_directory, output)
                        filtered_data = {k: v for k, v in tag_data_copy.items() if k in valid_fields}

                        self.tags[tag_name] = TagDefinition(**filtered_data)
                    except Exception as e:
                        logger.warning(f"Failed to load tag {tag_name}: {e}")
                        logger.debug(f"Tag data that failed: {tag_data}", exc_info=True)

            logger.info(f"Loaded {len(self.tags)} tags from {self.registry_path}")

        except FileNotFoundError:
            logger.error(f"Registry file not found: {self.registry_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in registry file: {e}")
            raise

    def get_tag(self, tag_name: str) -> Optional[TagDefinition]:
        """
        Get tag definition.

        Args:
            tag_name: Tag name (e.g., "@jarvis", "#peak")

        Returns:
            TagDefinition or None if not found
        """
        return self.tags.get(tag_name)

    def discover_related(self, tag_name: str) -> List[str]:
        """
        Discover related tags.

        Args:
            tag_name: Tag to find related tags for

        Returns:
            List of related tag names
        """
        tag = self.get_tag(tag_name)
        if not tag:
            return []

        related = []

        # Find tags with same category
        for name, defn in self.tags.items():
            if defn.category == tag.category and name != tag_name:
                related.append(name)

        # Find aliases
        if tag.alias_of:
            related.append(tag.alias_of)

        # Find tags that alias this one
        for name, defn in self.tags.items():
            if defn.alias_of == tag_name:
                related.append(name)

        # Find piped tags
        if tag.pipe_to:
            related.append(tag.pipe_to)

        # Find tags that pipe to this one
        for name, defn in self.tags.items():
            if defn.pipe_to == tag_name:
                related.append(name)

        # Find explicitly related tags
        if tag.related:
            related.extend(tag.related)

        return list(set(related))  # Remove duplicates

    def extrapolate_context(self, tag_names: List[str]) -> TagContext:
        """
        Extrapolate context from tags.

        Args:
            tag_names: List of tag names

        Returns:
            TagContext with discovered context
        """
        context = TagContext()

        for tag_name in tag_names:
            tag = self.get_tag(tag_name)
            if not tag:
                continue

            # Categorize by type
            if tag.type == "mention":
                if tag.category == "system":
                    context.systems.append(tag_name)
                elif tag.category == "tool":
                    context.tools.append(tag_name)
            elif tag.type == "hashtag":
                context.concepts.append(tag_name)

            # Accumulate weights
            context.total_context_weight += tag.context_weight
            context.total_ai_weight += tag.ai_weight
            context.total_human_weight += tag.human_weight

            # Store definition
            context.tag_definitions[tag_name] = tag

            # Discover relationships
            related = self.discover_related(tag_name)
            if related:
                context.relationships[tag_name] = related

        return context

    def extract_tags(self, text: str) -> List[str]:
        """
        Extract tags from text.

        Args:
            text: Text to extract tags from

        Returns:
            List of tag names found
        """
        import re

        # Pattern for @mentions and #hashtags
        pattern = r'(@\w+|#\w+)'
        matches = re.findall(pattern, text)

        # Normalize and deduplicate
        tags = list(set(matches))

        return tags

    def build_semantic_context(self, tag_names: List[str]) -> Dict:
        """
        Build semantic context from tags.

        Args:
            tag_names: List of tag names

        Returns:
            Dictionary with semantic context
        """
        context = self.extrapolate_context(tag_names)

        semantic_context = {
            "systems": context.systems,
            "concepts": context.concepts,
            "tools": context.tools,
            "context_weight": context.total_context_weight,
            "ai_weight": context.total_ai_weight,
            "human_weight": context.total_human_weight,
            "relationships": context.relationships,
            "inferred_actions": [],
            "inferred_integrations": []
        }

        # Infer actions based on tags
        for tag_name in tag_names:
            tag = self.get_tag(tag_name)
            if tag:
                if tag.type == "mention" and tag.category == "system":
                    semantic_context["inferred_actions"].append(f"Use {tag_name} for orchestration")
                if tag.module and tag.class_name:
                    semantic_context["inferred_integrations"].append({
                        "tag": tag_name,
                        "module": tag.module,
                        "class": tag.class_name
                    })

        return semantic_context

    def resolve_alias(self, tag_name: str) -> str:
        """
        Resolve tag alias to primary tag.

        Args:
            tag_name: Tag name (may be alias)

        Returns:
            Primary tag name
        """
        tag = self.get_tag(tag_name)
        if tag and tag.alias_of:
            return tag.alias_of
        return tag_name

    def resolve_pipe(self, tag_name: str) -> Optional[str]:
        """
        Resolve tag pipe target.

        Args:
            tag_name: Tag name

        Returns:
            Pipe target tag name or None
        """
        tag = self.get_tag(tag_name)
        if tag and tag.pipe_to:
            return tag.pipe_to
        return None

    def get_precedence(self, tag_name: str) -> int:
        """
        Get tag precedence.

        Args:
            tag_name: Tag name

        Returns:
            Precedence (1-3, lower is higher precedence)
        """
        tag = self.get_tag(tag_name)
        if tag and tag.precedence:
            return tag.precedence
        return 3  # Default to lowest precedence


def main():
    """CLI interface for short-tagging system"""
    import argparse

    parser = argparse.ArgumentParser(description="Short-Tagging System")
    parser.add_argument("--registry", type=Path, help="Path to registry file")
    parser.add_argument("--discover", type=str, help="Discover related tags")
    parser.add_argument("--extrapolate", nargs="+", help="Extrapolate context from tags")
    parser.add_argument("--extract", type=str, help="Extract tags from text")
    parser.add_argument("--list", action="store_true", help="List all tags")

    args = parser.parse_args()

    system = ShortTaggingSystem(args.registry)

    if args.discover:
        related = system.discover_related(args.discover)
        print(f"Related tags for {args.discover}:")
        for tag in related:
            print(f"  - {tag}")

    elif args.extrapolate:
        context = system.extrapolate_context(args.extrapolate)
        print(f"Context from {args.extrapolate}:")
        print(f"  Systems: {context.systems}")
        print(f"  Concepts: {context.concepts}")
        print(f"  Tools: {context.tools}")
        print(f"  Total Context Weight: {context.total_context_weight}")
        print(f"  Total AI Weight: {context.total_ai_weight}")

    elif args.extract:
        tags = system.extract_tags(args.extract)
        print(f"Tags found in '{args.extract}':")
        for tag in tags:
            print(f"  - {tag}")

    elif args.list:
        print(f"Available tags ({len(system.tags)}):")
        for tag_name in sorted(system.tags.keys()):
            tag = system.tags[tag_name]
            print(f"  {tag_name}: {tag.description}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()