#!/usr/bin/env python3
"""
@Peak Pattern System

Maximum @Peak pattern extraction, management, and application system.
Designed for full force (@ff) utilization of nutrient-dense, small-footprint solutions.

Features:
- Pattern extraction from code and chat sessions
- Pattern registry and storage
- Pattern application engine
- Pattern validation and quality control
- Integration with R5 Living Context Matrix
- Integration with Kilo Code for automatic pattern usage

Author: <COMPANY_NAME> LLC
Date: 2024-12-19
"""

import json
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
from enum import Enum

import sys
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

    def get_logger(name: str):
        return logging.getLogger(name)

logger = get_logger("PeakPatterns")


class PatternType(Enum):
    """Types of @Peak patterns"""
    CODE_STRUCTURE = "code_structure"
    ERROR_HANDLING = "error_handling"
    TYPE_SAFETY = "type_safety"
    LOGGING = "logging"
    CONFIGURATION = "configuration"
    API_DESIGN = "api_design"
    DATA_PROCESSING = "data_processing"
    TESTING = "testing"
    PERFORMANCE = "performance"
    SECURITY = "security"
    UTILITY = "utility"
    PATTERN = "pattern"  # Meta-pattern for pattern definitions


class PatternQuality(Enum):
    """Quality rating for patterns"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


@dataclass
class PeakPattern:
    """@Peak pattern definition"""
    pattern_id: str
    name: str
    pattern_type: PatternType
    description: str
    code_example: str
    usage_context: List[str]
    dependencies: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    frequency: int = 1
    quality: PatternQuality = PatternQuality.GOOD
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)
    applied_count: int = 0
    success_rate: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["pattern_type"] = self.pattern_type.value
        data["quality"] = self.quality.value
        data["created"] = self.created.isoformat()
        data["updated"] = self.updated.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PeakPattern":
        """Create from dictionary"""
        data["pattern_type"] = PatternType(data["pattern_type"])
        data["quality"] = PatternQuality(data["quality"])
        data["created"] = datetime.fromisoformat(data["created"])
        data["updated"] = datetime.fromisoformat(data["updated"])
        return cls(**data)


class PeakPatternSystem:
    """
    @Peak Pattern System

    Maximum utilization system for @Peak patterns.
    Extracts, stores, validates, and applies nutrient-dense solutions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @Peak Pattern System"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.patterns_dir = self.project_root / "data" / "peak_patterns"
        self.registry_path = self.patterns_dir / "peak_pattern_registry.json"
        self.patterns_storage = self.patterns_dir / "patterns"

        # Ensure directories exist
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        self.patterns_storage.mkdir(exist_ok=True)

        # Load registry
        self.registry = self._load_registry()
        self.patterns: Dict[str, PeakPattern] = {}
        self._load_all_patterns()

        logger.info(f"@Peak Pattern System initialized: {len(self.patterns)} patterns loaded")

    def _load_registry(self) -> Dict[str, Any]:
        """Load pattern registry"""
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load registry: {e}")

        # Create default registry
        return {
            "version": "1.0.0",
            "name": "@Peak Pattern Registry",
            "description": "Registry of all @Peak patterns",
            "last_updated": datetime.now().isoformat(),
            "total_patterns": 0,
            "patterns": {},
            "categories": {
                cat.value: {"description": "", "patterns": []}
                for cat in PatternType
            },
            "metadata": {
                "extraction_enabled": True,
                "auto_apply": True,
                "priority": "maximum",
                "force_multiplier": True
            }
        }

    def _save_registry(self) -> None:
        try:
            """Save pattern registry"""
            self.registry["last_updated"] = datetime.now().isoformat()
            self.registry["total_patterns"] = len(self.patterns)

            with open(self.registry_path, "w", encoding="utf-8") as f:
                json.dump(self.registry, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_registry: {e}", exc_info=True)
            raise
    def _load_all_patterns(self) -> None:
        """Load all patterns from storage"""
        pattern_files = list(self.patterns_storage.glob("*.json"))

        for pattern_file in pattern_files:
            try:
                with open(pattern_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pattern = PeakPattern.from_dict(data)
                    self.patterns[pattern.pattern_id] = pattern
            except Exception as e:
                logger.warning(f"Failed to load pattern {pattern_file}: {e}")

    def extract_patterns_from_code(self, code: str, context: Optional[Dict[str, Any]] = None) -> List[PeakPattern]:
        """
        Extract @Peak patterns from code

        Args:
            code: Source code to analyze
            context: Optional context information

        Returns:
            List of extracted patterns
        """
        patterns = []

        # Look for @Peak annotations
        peak_regex = r"@[Pp]eak\s*[:=]?\s*(.+)"
        matches = re.finditer(peak_regex, code, re.MULTILINE)

        for match in matches:
            pattern_desc = match.group(1).strip()

            # Extract pattern details
            pattern_id = f"peak_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(patterns)}"
            pattern_name = self._extract_pattern_name(pattern_desc)
            pattern_type = self._classify_pattern(code, match.start())

            # Extract code example (surrounding context)
            code_example = self._extract_code_example(code, match.start(), match.end())

            pattern = PeakPattern(
                pattern_id=pattern_id,
                name=pattern_name,
                pattern_type=pattern_type,
                description=pattern_desc,
                code_example=code_example,
                usage_context=[context.get("file_path", "unknown")] if context else [],
                tags=self._extract_tags(code, pattern_desc),
                metadata={"extracted_from": "code", "context": context or {}}
            )

            patterns.append(pattern)

        return patterns

    def extract_patterns_from_chat(self, messages: List[Dict[str, Any]]) -> List[PeakPattern]:
        """
        Extract @Peak patterns from chat session messages

        Args:
            messages: List of chat messages

        Returns:
            List of extracted patterns
        """
        patterns = []

        for message in messages:
            content = message.get("content", "")
            if "@Peak" in content or "@peak" in content or "@PEAK" in content:
                # Extract pattern descriptions
                peak_regex = r"@[Pp]eak\s*[:=]?\s*(.+?)(?=\n|$|@)"
                matches = re.finditer(peak_regex, content, re.MULTILINE | re.DOTALL)

                for match in matches:
                    pattern_desc = match.group(1).strip()

                    pattern_id = f"peak_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(patterns)}"
                    pattern_name = self._extract_pattern_name(pattern_desc)
                    pattern_type = self._classify_pattern_from_text(pattern_desc)

                    pattern = PeakPattern(
                        pattern_id=pattern_id,
                        name=pattern_name,
                        pattern_type=pattern_type,
                        description=pattern_desc,
                        code_example="",
                        usage_context=[message.get("role", "unknown")],
                        tags=self._extract_tags_from_text(pattern_desc),
                        metadata={"extracted_from": "chat", "message_id": message.get("id", "unknown")}
                    )

                    patterns.append(pattern)

        return patterns

    def register_pattern(self, pattern: PeakPattern, merge_existing: bool = True, trigger_research: bool = True) -> bool:
        """
        Register a new pattern or update existing

        Args:
            pattern: Pattern to register
            merge_existing: If True, merge with existing pattern if ID matches
            trigger_research: If True, trigger Watcher Uatu research

        Returns:
            True if registered successfully
        """
        if pattern.pattern_id in self.patterns:
            if merge_existing:
                # Merge with existing
                existing = self.patterns[pattern.pattern_id]
                existing.frequency += pattern.frequency
                existing.updated = datetime.now()
                if pattern.code_example and not existing.code_example:
                    existing.code_example = pattern.code_example
                pattern = existing
            else:
                logger.warning(f"Pattern {pattern.pattern_id} already exists, skipping")
                return False

        # Save pattern file
        pattern_file = self.patterns_storage / f"{pattern.pattern_id}.json"
        with open(pattern_file, "w", encoding="utf-8") as f:
            json.dump(pattern.to_dict(), f, indent=2, ensure_ascii=False)

        # Update registry
        self.patterns[pattern.pattern_id] = pattern
        self.registry["patterns"][pattern.pattern_id] = {
            "name": pattern.name,
            "type": pattern.pattern_type.value,
            "category": pattern.pattern_type.value,
            "frequency": pattern.frequency,
            "quality": pattern.quality.value
        }

        # Update category
        category = self.registry["categories"].get(pattern.pattern_type.value, {})
        if "patterns" not in category:
            category["patterns"] = []
        if pattern.pattern_id not in category["patterns"]:
            category["patterns"].append(pattern.pattern_id)

        self._save_registry()
        logger.info(f"Registered pattern: {pattern.pattern_id} - {pattern.name}")

        # Trigger Watcher Uatu research if enabled
        if trigger_research:
            try:
                from watcher_uatu_research import WatcherUatu, ResearchDepth
                watcher = WatcherUatu(self.project_root)
                report = watcher.research_pattern(pattern.pattern_id, ResearchDepth.MAXIMUM)
                logger.info(f"Watcher Uatu research complete: {len(report.sparks)} sparks generated")
            except Exception as e:
                logger.warning(f"Failed to trigger Watcher Uatu research: {e}")

        return True

    def find_patterns(self,
                      pattern_type: Optional[PatternType] = None,
                      tags: Optional[List[str]] = None,
                      query: Optional[str] = None) -> List[PeakPattern]:
        """
        Find patterns matching criteria

        Args:
            pattern_type: Filter by pattern type
            tags: Filter by tags
            query: Text search query

        Returns:
            List of matching patterns
        """
        matches = list(self.patterns.values())

        if pattern_type:
            matches = [p for p in matches if p.pattern_type == pattern_type]

        if tags:
            matches = [p for p in matches if any(tag in p.tags for tag in tags)]

        if query:
            query_lower = query.lower()
            matches = [p for p in matches if
                      query_lower in p.name.lower() or
                      query_lower in p.description.lower() or
                      query_lower in p.code_example.lower()]

        # Sort by frequency and quality
        matches.sort(key=lambda p: (p.frequency, p.quality.value), reverse=True)

        return matches

    def apply_pattern(self, pattern_id: str, context: Dict[str, Any]) -> Optional[str]:
        try:
            """
            Apply a pattern to generate code

            Args:
                pattern_id: ID of pattern to apply
                context: Context for pattern application

            Returns:
                Generated code or None if pattern not found
            """
            if pattern_id not in self.patterns:
                logger.warning(f"Pattern {pattern_id} not found")
                return None

            pattern = self.patterns[pattern_id]

            # Increment application count
            pattern.applied_count += 1
            pattern.updated = datetime.now()

            # Save updated pattern
            pattern_file = self.patterns_storage / f"{pattern.pattern_id}.json"
            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(pattern.to_dict(), f, indent=2, ensure_ascii=False)

            # Return pattern code example (in real implementation, would generate code)
            return pattern.code_example

        except Exception as e:
            self.logger.error(f"Error in apply_pattern: {e}", exc_info=True)
            raise
    def get_pattern_suggestions(self, code_context: str, file_path: Optional[str] = None) -> List[PeakPattern]:
        """
        Get pattern suggestions for given code context

        Args:
            code_context: Current code context
            file_path: Path to file being edited

        Returns:
            List of suggested patterns
        """
        # Analyze context to find relevant patterns
        suggestions = []

        # Check for common patterns based on context
        if "error" in code_context.lower() or "except" in code_context.lower():
            suggestions.extend(self.find_patterns(pattern_type=PatternType.ERROR_HANDLING))

        if "log" in code_context.lower() or "logger" in code_context.lower():
            suggestions.extend(self.find_patterns(pattern_type=PatternType.LOGGING))

        if "config" in code_context.lower() or "settings" in code_context.lower():
            suggestions.extend(self.find_patterns(pattern_type=PatternType.CONFIGURATION))

        if "def " in code_context or "class " in code_context:
            suggestions.extend(self.find_patterns(pattern_type=PatternType.CODE_STRUCTURE))

        # Return top suggestions
        suggestions = list(set(suggestions))  # Remove duplicates
        suggestions.sort(key=lambda p: (p.frequency, p.quality.value), reverse=True)

        return suggestions[:5]  # Top 5

    def _extract_pattern_name(self, description: str) -> str:
        """Extract pattern name from description"""
        # Try to extract name from description
        lines = description.split("\n")
        first_line = lines[0].strip()
        if len(first_line) < 50:
            return first_line
        return f"Pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    def _classify_pattern(self, code: str, position: int) -> PatternType:
        """Classify pattern type based on code context"""
        # Analyze surrounding code
        context_start = max(0, position - 200)
        context_end = min(len(code), position + 200)
        context = code[context_start:context_end].lower()

        if "error" in context or "except" in context or "raise" in context:
            return PatternType.ERROR_HANDLING
        elif "log" in context or "logger" in context:
            return PatternType.LOGGING
        elif "config" in context or "settings" in context:
            return PatternType.CONFIGURATION
        elif "type" in context or "typing" in context or "Optional" in context:
            return PatternType.TYPE_SAFETY
        elif "test" in context or "assert" in context:
            return PatternType.TESTING
        elif "api" in context or "endpoint" in context:
            return PatternType.API_DESIGN
        elif "security" in context or "auth" in context:
            return PatternType.SECURITY
        elif "performance" in context or "optimize" in context:
            return PatternType.PERFORMANCE
        else:
            return PatternType.UTILITY

    def _classify_pattern_from_text(self, text: str) -> PatternType:
        """Classify pattern type from text description"""
        text_lower = text.lower()

        if any(word in text_lower for word in ["error", "exception", "handle"]):
            return PatternType.ERROR_HANDLING
        elif any(word in text_lower for word in ["log", "logger", "logging"]):
            return PatternType.LOGGING
        elif any(word in text_lower for word in ["config", "settings", "configuration"]):
            return PatternType.CONFIGURATION
        elif any(word in text_lower for word in ["type", "typing", "validation"]):
            return PatternType.TYPE_SAFETY
        elif any(word in text_lower for word in ["test", "testing", "assert"]):
            return PatternType.TESTING
        elif any(word in text_lower for word in ["api", "endpoint", "request"]):
            return PatternType.API_DESIGN
        elif any(word in text_lower for word in ["security", "auth", "permission"]):
            return PatternType.SECURITY
        elif any(word in text_lower for word in ["performance", "optimize", "speed"]):
            return PatternType.PERFORMANCE
        else:
            return PatternType.UTILITY

    def _extract_code_example(self, code: str, start: int, end: int) -> str:
        """Extract code example around pattern annotation"""
        # Extract surrounding code (50 lines before and after)
        lines = code.split("\n")
        start_line = max(0, code[:start].count("\n") - 10)
        end_line = min(len(lines), code[:end].count("\n") + 10)

        return "\n".join(lines[start_line:end_line])

    def _extract_tags(self, code: str, description: str) -> List[str]:
        """Extract tags from code and description"""
        tags = []

        # Extract from description
        words = re.findall(r'\b\w+\b', description.lower())
        common_tags = ["pattern", "peak", "reusable", "nutrient", "dense", "small", "footprint"]
        tags.extend([w for w in words if w in common_tags or len(w) > 4])

        # Extract from code context
        code_lower = code.lower()
        if "async" in code_lower:
            tags.append("async")
        if "class" in code_lower:
            tags.append("class")
        if "function" in code_lower or "def " in code_lower:
            tags.append("function")

        return list(set(tags))[:10]  # Limit to 10 tags

    def _extract_tags_from_text(self, text: str) -> List[str]:
        """Extract tags from text description"""
        words = re.findall(r'\b\w+\b', text.lower())
        return list(set(words))[:10]


def main() -> int:
    """Main entry point for testing"""
    system = PeakPatternSystem()

    # Example: Extract patterns from code
    sample_code = '''
    @Peak: Error handling with logging
    def process_data(data: List[str]) -> Optional[Dict[str, Any]]:
        try:
            logger.info("Processing data")
            result = {}
            for item in data:
                result[item] = process_item(item)
            return result
        except Exception as e:
            logger.error(f"Error processing data: {e}")
            return None
    '''

    patterns = system.extract_patterns_from_code(sample_code, {"file_path": "example.py"})

    for pattern in patterns:
        system.register_pattern(pattern)
        print(f"Registered: {pattern.pattern_id} - {pattern.name}")

    # Find patterns
    error_patterns = system.find_patterns(pattern_type=PatternType.ERROR_HANDLING)
    print(f"\nFound {len(error_patterns)} error handling patterns")

    return 0


if __name__ == "__main__":
    import sys



    sys.exit(main())