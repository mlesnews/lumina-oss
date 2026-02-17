#!/usr/bin/env python3
"""
SYPHON Troubleshooting Intelligence Extractor

Extracts actionable intelligence from troubleshooting sessions, errors, and fixes.
Integrates pattern recognition, building blocks, simulation, and @FF automation.

@SYPHON #TROUBLESHOOTING #PATTERNS #PEAK #FF #INTELLIGENCE
"""

from __future__ import annotations

import json
import re
from abc import ABC
from datetime import datetime
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from syphon.models import SyphonData, DataSourceType, ExtractionResult
from syphon.extractors import BaseExtractor

if TYPE_CHECKING:
    from syphon.core import SYPHONConfig


class TroubleshootingExtractor(BaseExtractor):
    """
    Extracts intelligence from troubleshooting sessions.

    Extracts:
    - Error patterns and intent
    - Building blocks breakdown
    - Fix strategies and success rates
    - @FF keyboard shortcuts used
    - Proven patterns for future reference
    """

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from troubleshooting content.

        Args:
            content: Troubleshooting data (error, fix, session, etc.)
            metadata: Additional metadata

        Returns:
            ExtractionResult with extracted intelligence
        """
        try:
            # Handle different content types
            if isinstance(content, dict):
                troubleshooting_data = content
            elif isinstance(content, str):
                troubleshooting_data = {"error_message": content, "raw": content}
            else:
                troubleshooting_data = {"content": str(content)}

            # Merge with metadata
            full_metadata = {
                **metadata,
                **troubleshooting_data
            }

            # Extract intelligence components
            content_text = self._get_content_text(troubleshooting_data)

            # Extract patterns and intent
            patterns = self._extract_patterns(content_text, troubleshooting_data)

            # Extract building blocks
            building_blocks = self._extract_building_blocks(content_text, troubleshooting_data)

            # Extract fix strategies
            fix_strategies = self._extract_fix_strategies(troubleshooting_data)

            # Extract @FF shortcuts
            ff_shortcuts = self._extract_ff_shortcuts(troubleshooting_data)

            # Extract actionable items
            actionable_items = self._extract_actionable_items(content_text)

            # Extract tasks
            tasks = self._extract_tasks(content_text)

            # Extract decisions
            decisions = self._extract_decisions(content_text)

            # Extract intelligence
            intelligence = self._extract_intelligence(content_text, troubleshooting_data)

            # Create syphon data
            syphon_data = SyphonData(
                data_id=f"troubleshooting_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.CODE,  # Troubleshooting is code-related
                source_id=troubleshooting_data.get("error_id") or troubleshooting_data.get("session_id", ""),
                content=content_text,
                metadata={
                    **full_metadata,
                    "patterns": patterns,
                    "building_blocks": building_blocks,
                    "fix_strategies": fix_strategies,
                    "ff_shortcuts": ff_shortcuts
                },
                extracted_at=datetime.now(),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=intelligence
            )

            return ExtractionResult(success=True, data=syphon_data)

        except Exception as e:
            return ExtractionResult(success=False, error=str(e))

    def _get_content_text(self, data: Dict[str, Any]) -> str:
        """Extract text content from troubleshooting data"""
        text_parts = []

        if "error_message" in data:
            text_parts.append(data["error_message"])
        if "fix_description" in data:
            text_parts.append(data["fix_description"])
        if "session_log" in data:
            text_parts.append(data["session_log"])
        if "raw" in data:
            text_parts.append(data["raw"])
        if "content" in data:
            text_parts.append(data["content"])

        return "\n".join(text_parts)

    def _extract_patterns(self, content: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract error patterns and intent (#patterns)"""
        patterns = []

        # Check if pattern is already identified
        if "pattern" in data:
            patterns.append({
                "pattern_id": data.get("pattern_id", ""),
                "pattern_name": data.get("pattern", ""),
                "intent": data.get("intent", ""),
                "confidence": data.get("pattern_confidence", 0.0)
            })

        # Extract patterns from content
        pattern_keywords = [
            "syntax error", "type error", "import error", "undefined",
            "unused", "lint", "format", "config", "dependency"
        ]

        content_lower = content.lower()
        for keyword in pattern_keywords:
            if keyword in content_lower:
                patterns.append({
                    "pattern_type": keyword,
                    "detected": True,
                    "context": self._extract_context(content, keyword)
                })

        return patterns

    def _extract_building_blocks(self, content: str, data: Dict[str, Any]) -> List[str]:
        """Extract building blocks breakdown"""
        building_blocks = []

        # Check if building blocks already identified
        if "building_blocks" in data:
            if isinstance(data["building_blocks"], list):
                building_blocks.extend(data["building_blocks"])

        # Extract from content
        # Look for common building blocks
        block_patterns = [
            r"import\s+(\w+)",
            r"from\s+(\w+)\s+import",
            r"def\s+(\w+)",
            r"class\s+(\w+)",
            r"(\w+)\s*=\s*\w+",
        ]

        for pattern in block_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                block = match.group(1) if match.lastindex else match.group(0)
                if block and block not in building_blocks:
                    building_blocks.append(block)

        return building_blocks[:20]  # Limit to top 20

    def _extract_fix_strategies(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract fix strategies and success rates"""
        strategies = []

        if "fix_strategy" in data:
            strategies.append({
                "strategy": data["fix_strategy"],
                "success_rate": data.get("success_rate", 0.0),
                "proven": data.get("proven", False),
                "simulation": data.get("simulation", {})
            })

        if "simulated_fix" in data:
            sim = data["simulated_fix"]
            strategies.append({
                "strategy": "simulated",
                "success_rate": sim.get("success_rate", 0.0),
                "simulation": sim
            })

        return strategies

    def _extract_ff_shortcuts(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract @FF keyboard shortcuts used"""
        shortcuts = []

        if "ff_shortcuts" in data:
            if isinstance(data["ff_shortcuts"], list):
                shortcuts.extend(data["ff_shortcuts"])

        if "keyboard_shortcuts" in data:
            if isinstance(data["keyboard_shortcuts"], list):
                shortcuts.extend(data["keyboard_shortcuts"])

        # Extract from content
        shortcut_patterns = [
            r"(?:Ctrl|Cmd)\+[A-Z0-9\+\-]+",
            r"F\d+",
            r"Alt\+[A-Z0-9]",
            r"Shift\+[A-Z0-9]"
        ]

        content = self._get_content_text(data)
        for pattern in shortcut_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                shortcut = match.group(0)
                if shortcut not in [s.get("shortcut", "") if isinstance(s, dict) else s for s in shortcuts]:
                    shortcuts.append({"shortcut": shortcut, "detected": True})

        return shortcuts

    def _extract_context(self, content: str, keyword: str, context_lines: int = 3) -> str:
        """Extract context around keyword"""
        lines = content.split('\n')
        keyword_lower = keyword.lower()

        for i, line in enumerate(lines):
            if keyword_lower in line.lower():
                start = max(0, i - context_lines)
                end = min(len(lines), i + context_lines + 1)
                return '\n'.join(lines[start:end])

        return ""

    def _extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items from troubleshooting content"""
        actionable_items = []
        content_lower = content.lower()

        # Action patterns
        action_patterns = [
            r'(?:fix|resolve|correct|repair)\s+(.+)',
            r'(?:apply|execute|run|perform)\s+(.+)',
            r'(?:check|verify|validate)\s+(.+)',
            r'(?:update|modify|change)\s+(.+)',
        ]

        for pattern in action_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                item = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if item and len(item) > 10 and item not in actionable_items:
                    actionable_items.append(item)

        return actionable_items[:10]

    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract tasks from troubleshooting content"""
        tasks = []
        content_lower = content.lower()

        # Task patterns
        task_patterns = [
            (r'(?:todo|task|need to|must|should)\s+(.+)', 'general'),
            (r'(?:fix|resolve)\s+(.+)', 'fix'),
            (r'(?:test|verify)\s+(.+)', 'test'),
        ]

        for pattern, task_type in task_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if task_text and len(task_text) > 10:
                    tasks.append({
                        "text": task_text,
                        "type": task_type,
                        "priority": "high" if "urgent" in task_text or "critical" in task_text else "medium"
                    })

        return tasks[:10]

    def _extract_decisions(self, content: str) -> List[Dict[str, Any]]:
        """Extract decisions from troubleshooting content"""
        decisions = []
        content_lower = content.lower()

        # Decision patterns
        decision_patterns = [
            (r'(?:decided|chose|selected|opted)\s+(.+)', 'selection'),
            (r'(?:should|will|going to)\s+(.+)', 'action'),
        ]

        for pattern, decision_type in decision_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                decision_text = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if decision_text and len(decision_text) > 10:
                    decisions.append({
                        "text": decision_text,
                        "type": decision_type
                    })

        return decisions[:10]

    def _extract_intelligence(self, content: str, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract intelligence/insights from troubleshooting"""
        intelligence = []
        content_lower = content.lower()

        # Intelligence patterns
        intel_patterns = [
            (r'(?:pattern|intent|behavior)\s+(.+)', 'pattern'),
            (r'(?:root cause|underlying issue)\s+(.+)', 'root_cause'),
            (r'(?:insight|discovery|finding)\s+(.+)', 'insight'),
            (r'(?:proven|successful|working)\s+(.+)', 'proven_solution'),
        ]

        for pattern, intel_type in intel_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                intel_text = match.group(1).strip() if match.lastindex else match.group(0).strip()
                if intel_text and len(intel_text) > 10:
                    intelligence.append({
                        "text": intel_text,
                        "type": intel_type
                    })

        # Add proven patterns
        if data.get("proven", False):
            intelligence.append({
                "text": f"Proven pattern: {data.get('pattern', 'Unknown')}",
                "type": "proven_pattern",
                "success_rate": data.get("success_rate", 0.0)
            })

        return intelligence[:10]
