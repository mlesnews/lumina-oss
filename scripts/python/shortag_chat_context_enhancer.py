#!/usr/bin/env python3
"""
Short@Tag Chat Session Context Enhancer
Advanced metatagging AI agent chat session context enhancer using short@tags as @rules

This system:
1. Extracts short@tags from chat sessions
2. Applies them as @rules for context enhancement
3. Enhances AI agent understanding through weighted context
4. Integrates with Dewey Decimal catalog
5. Updates dynamically as sessions change

Tags: #SHORTAG #CONTEXT #ENHANCEMENT #RULES #CHAT #SESSIONS @JARVIS
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
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

logger = get_logger("ShortagContextEnhancer")

# Import short@tag registry
try:
    from shortag_to_cursorrules_converter import ShortagToCursorRulesConverter
    CONVERTER_AVAILABLE = True
except ImportError:
    CONVERTER_AVAILABLE = False
    ShortagToCursorRulesConverter = None
    logger.warning("⚠️  Short@Tag converter not available")

# Import Dewey catalog
try:
    from dewey_decimal_chat_catalog import DeweyDecimalChatCatalog
    DEWEY_AVAILABLE = True
except ImportError:
    DEWEY_AVAILABLE = False
    DeweyDecimalChatCatalog = None
    logger.warning("⚠️  Dewey catalog not available")


@dataclass
class ContextEnhancement:
    """Context enhancement applied to a chat session"""
    session_id: str
    session_title: str
    shortags_found: List[str] = field(default_factory=list)
    context_weights: Dict[str, float] = field(default_factory=dict)
    ai_weights: Dict[str, float] = field(default_factory=dict)
    human_weights: Dict[str, float] = field(default_factory=dict)
    total_context_weight: float = 0.0
    enhanced_context: str = ""
    rules_applied: List[str] = field(default_factory=list)
    enhanced_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ShortagChatContextEnhancer:
    """
    Short@Tag Chat Session Context Enhancer

    Uses short@tags as @rules to enhance AI agent chat session context.
    This is an advanced metatagging system that improves AI understanding
    through weighted context application.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize context enhancer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Load short@tag registry
        self.shortag_registry_file = self.project_root / "config" / "shortag_registry.json"
        self.shortags: Dict[str, Dict[str, Any]] = {}
        self._load_shortags()

        # Initialize converter
        self.converter = None
        if CONVERTER_AVAILABLE:
            try:
                self.converter = ShortagToCursorRulesConverter(project_root)
                logger.info("✅ Short@Tag converter initialized")
            except Exception as e:
                logger.warning(f"⚠️  Converter initialization failed: {e}")

        # Initialize Dewey catalog
        self.dewey_catalog = None
        if DEWEY_AVAILABLE:
            try:
                self.dewey_catalog = DeweyDecimalChatCatalog(project_root)
                logger.info("✅ Dewey catalog initialized")
            except Exception as e:
                logger.warning(f"⚠️  Dewey catalog initialization failed: {e}")

        # Enhancement storage
        self.enhancements_dir = self.project_root / "data" / "shortag_enhancements"
        self.enhancements_dir.mkdir(parents=True, exist_ok=True)

        # Track enhancements
        self.enhancements: Dict[str, ContextEnhancement] = {}
        self._load_enhancements()

        logger.info("🧠 Short@Tag Chat Context Enhancer initialized")
        logger.info(f"   Loaded {len(self.shortags)} short@tags")
        logger.info(f"   Loaded {len(self.enhancements)} enhancements")

    def _load_shortags(self) -> None:
        """Load short@tag registry"""
        if not self.shortag_registry_file.exists():
            logger.warning(f"⚠️  Shortag registry not found: {self.shortag_registry_file}")
            return

        try:
            with open(self.shortag_registry_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Filter out metadata
                self.shortags = {
                    k: v for k, v in data.items()
                    if not k.startswith("_")
                }
            logger.info(f"✅ Loaded {len(self.shortags)} short@tags")
        except Exception as e:
            logger.error(f"❌ Error loading shortag registry: {e}")

    def extract_shortags_from_text(self, text: str) -> List[Tuple[str, Dict[str, Any]]]:
        """Extract short@tags from text"""
        found_tags = []

        # Pattern for @mentions and #hashtags
        mention_pattern = r'@(\w+)'
        hashtag_pattern = r'#(\w+)'

        # Find all mentions
        for match in re.finditer(mention_pattern, text):
            tag_name = f"@{match.group(1)}"
            if tag_name in self.shortags:
                found_tags.append((tag_name, self.shortags[tag_name]))

        # Find all hashtags
        for match in re.finditer(hashtag_pattern, text):
            tag_name = f"#{match.group(1)}"
            if tag_name in self.shortags:
                found_tags.append((tag_name, self.shortags[tag_name]))

        return found_tags

    def enhance_session_context(self, session_id: str, session_title: str,
                               session_content: str) -> ContextEnhancement:
        """Enhance chat session context using short@tags as @rules"""
        self.logger.info(f"🧠 Enhancing context for session: {session_title}")

        # Extract short@tags
        found_tags = self.extract_shortags_from_text(session_content)
        tag_names = [tag[0] for tag in found_tags]

        # Calculate context weights
        context_weights = {}
        ai_weights = {}
        human_weights = {}
        total_context_weight = 0.0

        for tag_name, tag_data in found_tags:
            context_weight = tag_data.get("context_weight", 0.5)
            ai_weight = tag_data.get("ai_weight", 0.5)
            human_weight = tag_data.get("human_weight", 0.5)

            context_weights[tag_name] = context_weight
            ai_weights[tag_name] = ai_weight
            human_weights[tag_name] = human_weight
            total_context_weight += context_weight

        # Generate enhanced context
        enhanced_context = self._generate_enhanced_context(
            session_title, session_content, found_tags
        )

        # Generate rules applied
        rules_applied = self._generate_rules_applied(found_tags)

        # Create enhancement
        enhancement = ContextEnhancement(
            session_id=session_id,
            session_title=session_title,
            shortags_found=tag_names,
            context_weights=context_weights,
            ai_weights=ai_weights,
            human_weights=human_weights,
            total_context_weight=total_context_weight,
            enhanced_context=enhanced_context,
            rules_applied=rules_applied
        )

        self.enhancements[session_id] = enhancement
        self._save_enhancement(enhancement)

        self.logger.info(f"✅ Enhanced context: {len(tag_names)} tags, weight: {total_context_weight:.2f}")

        return enhancement

    def _generate_enhanced_context(self, title: str, content: str,
                                   found_tags: List[Tuple[str, Dict[str, Any]]]) -> str:
        """Generate enhanced context string"""
        context_parts = []

        context_parts.append(f"# Enhanced Context for: {title}")
        context_parts.append("")
        context_parts.append("## Short@Tags Applied as @Rules")
        context_parts.append("")

        for tag_name, tag_data in found_tags:
            description = tag_data.get("description", "")
            category = tag_data.get("category", "general")
            context_weight = tag_data.get("context_weight", 0.5)
            ai_weight = tag_data.get("ai_weight", 0.5)
            human_weight = tag_data.get("human_weight", 0.5)

            context_parts.append(f"### {tag_name}")
            context_parts.append(f"- **Category**: {category}")
            context_parts.append(f"- **Description**: {description}")
            context_parts.append(f"- **Context Weight**: {context_weight}")
            context_parts.append(f"- **AI Weight**: {ai_weight}")
            context_parts.append(f"- **Human Weight**: {human_weight}")
            context_parts.append("")

            usage = tag_data.get("usage", "")
            if usage:
                context_parts.append(f"**Usage**: {usage}")
                context_parts.append("")

        context_parts.append("## Context Application")
        context_parts.append("")
        context_parts.append("These short@tags function as @rules in Cursor IDE,")
        context_parts.append("enhancing AI agent understanding through weighted context.")
        context_parts.append("")

        return "\n".join(context_parts)

    def _generate_rules_applied(self, found_tags: List[Tuple[str, Dict[str, Any]]]) -> List[str]:
        """Generate list of rules applied"""
        rules = []

        for tag_name, tag_data in found_tags:
            category = tag_data.get("category", "general")
            description = tag_data.get("description", "")

            rule = f"When `{tag_name}` is mentioned: "
            rule += f"Apply {category} context with weight {tag_data.get('context_weight', 0.5)}. "
            rule += f"{description}"

            rules.append(rule)

        return rules

    def enhance_all_sessions(self) -> Dict[str, ContextEnhancement]:
        """Enhance context for all chat sessions"""
        self.logger.info("🔍 Scanning and enhancing all chat sessions...")

        enhanced_count = 0

        # Scan master chat session
        master_chat_file = self.project_root / "data" / "master_chat" / "master_session.json"
        if master_chat_file.exists():
            try:
                with open(master_chat_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session_id = data.get('session_id', 'jarvis_master_chat')
                    session_title = data.get('session_name', 'JARVIS Master Chat')
                    content = json.dumps(data)

                    enhancement = self.enhance_session_context(
                        session_id, session_title, content
                    )
                    enhanced_count += 1
            except Exception as e:
                self.logger.warning(f"⚠️  Error enhancing master chat: {e}")

        # Scan agent chat sessions
        sessions_dir = self.project_root / "data" / "agent_chat_sessions"
        if sessions_dir.exists():
            for session_file in sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session_id = data.get('session_id', session_file.stem)
                        session_title = data.get('session_name') or data.get('title') or session_id
                        content = json.dumps(data)

                        enhancement = self.enhance_session_context(
                            session_id, session_title, content
                        )
                        enhanced_count += 1
                except Exception as e:
                    self.logger.warning(f"⚠️  Error enhancing {session_file}: {e}")

        self.logger.info(f"✅ Enhanced {enhanced_count} sessions")

        return self.enhancements

    def get_enhanced_context_for_session(self, session_id: str) -> Optional[str]:
        """Get enhanced context for a specific session"""
        if session_id in self.enhancements:
            return self.enhancements[session_id].enhanced_context
        return None

    def generate_context_report(self) -> Dict[str, Any]:
        """Generate report of context enhancements"""
        report = {
            "total_sessions_enhanced": len(self.enhancements),
            "total_shortags_used": len(set(
                tag for enh in self.enhancements.values()
                for tag in enh.shortags_found
            )),
            "shortag_frequency": defaultdict(int),
            "average_context_weight": 0.0,
            "top_enhanced_sessions": [],
            "generated_at": datetime.now().isoformat()
        }

        # Count short@tag frequency
        total_weight = 0.0
        for enhancement in self.enhancements.values():
            total_weight += enhancement.total_context_weight
            for tag in enhancement.shortags_found:
                report["shortag_frequency"][tag] += 1

        # Calculate average
        if self.enhancements:
            report["average_context_weight"] = total_weight / len(self.enhancements)

        # Top enhanced sessions
        sorted_sessions = sorted(
            self.enhancements.values(),
            key=lambda e: e.total_context_weight,
            reverse=True
        )[:10]
        report["top_enhanced_sessions"] = [
            {
                "session_id": e.session_id,
                "title": e.session_title,
                "tags_count": len(e.shortags_found),
                "context_weight": e.total_context_weight
            }
            for e in sorted_sessions
        ]

        return report

    def _load_enhancements(self) -> None:
        """Load existing enhancements from disk"""
        for enhancement_file in self.enhancements_dir.glob("*_enhancement.json"):
            try:
                with open(enhancement_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    enhancement = ContextEnhancement(**data)
                    self.enhancements[enhancement.session_id] = enhancement
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading {enhancement_file}: {e}")

    def _save_enhancement(self, enhancement: ContextEnhancement) -> None:
        """Save enhancement to disk"""
        enhancement_file = self.enhancements_dir / f"{enhancement.session_id}_enhancement.json"

        try:
            with open(enhancement_file, 'w', encoding='utf-8') as f:
                json.dump(enhancement.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving enhancement: {e}")

    def update_cursorrules_with_shortags(self) -> bool:
        """Update .cursorrules with short@tag rules"""
        if not self.converter:
            self.logger.warning("⚠️  Converter not available")
            return False

        try:
            success = self.converter.append_to_cursorrules(backup=True)
            if success:
                self.logger.info("✅ Updated .cursorrules with short@tag rules")
            return success
        except Exception as e:
            self.logger.error(f"❌ Error updating .cursorrules: {e}")
            return False


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Short@Tag Chat Context Enhancer")
        parser.add_argument("--enhance-all", action="store_true",
                           help="Enhance context for all sessions")
        parser.add_argument("--session", type=str,
                           help="Enhance specific session ID")
        parser.add_argument("--update-rules", action="store_true",
                           help="Update .cursorrules with short@tag rules")
        parser.add_argument("--report", action="store_true",
                           help="Generate context enhancement report")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        enhancer = ShortagChatContextEnhancer()

        if args.update_rules:
            success = enhancer.update_cursorrules_with_shortags()
            if args.json:
                print(json.dumps({"success": success}, indent=2))
            else:
                print(f"\n{'✅' if success else '❌'} Rules update: {'Success' if success else 'Failed'}")

        elif args.enhance_all:
            enhancements = enhancer.enhance_all_sessions()
            if args.json:
                print(json.dumps({sid: e.to_dict() for sid, e in enhancements.items()}, indent=2))
            else:
                print(f"\n✅ Enhanced {len(enhancements)} sessions")
                for session_id, enhancement in list(enhancements.items())[:10]:
                    print(f"   {session_id}: {len(enhancement.shortags_found)} tags, weight: {enhancement.total_context_weight:.2f}")

        elif args.session:
            # Would need session content - placeholder
            print("Session-specific enhancement requires session content")

        elif args.report:
            report = enhancer.generate_context_report()
            if args.json:
                print(json.dumps(report, indent=2))
            else:
                print(f"\n📊 Context Enhancement Report")
                print(f"   Sessions enhanced: {report['total_sessions_enhanced']}")
                print(f"   Short@tags used: {report['total_shortags_used']}")
                print(f"   Average context weight: {report['average_context_weight']:.2f}")
                print(f"\n   Top short@tags:")
                for tag, count in sorted(report['shortag_frequency'].items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"      {tag}: {count}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()