"""
JARVIS Cursor IDE Footer Manager
Manages Cursor IDE footer/status bar to prevent clutter and overflow.

Solutions:
1. Two footer bars (if supported)
2. Collapsible/expandable sections
3. Priority-based display (show important, hide less important)
4. Rotating/cycling through items
5. Grouping related items
6. Auto-hide when not needed

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #CURSOR #FOOTER #UI
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class FooterItemPriority(str, Enum):
    """Footer item priority levels."""
    CRITICAL = "critical"  # Always show
    HIGH = "high"  # Show when space available
    MEDIUM = "medium"  # Show when space available, hide if crowded
    LOW = "low"  # Hide by default, show on hover/expand
    HIDDEN = "hidden"  # Always hidden


@dataclass
class FooterItem:
    """Footer/status bar item configuration."""
    id: str
    name: str
    priority: FooterItemPriority
    category: str
    visible: bool = True
    position: Optional[int] = None
    group: Optional[str] = None
    tooltip: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class JARVISCursorFooterManager:
    """
    Manages Cursor IDE footer/status bar to prevent clutter.

    Solutions:
    1. Priority-based visibility
    2. Grouping related items
    3. Collapsible sections
    4. Rotating display
    5. Two footer bars (if supported)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize footer manager.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.config_file = self.project_root / "config" / "cursor_footer_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.items: List[FooterItem] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load footer configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [
                        FooterItem(**item) for item in data.get('items', [])
                    ]
            except Exception as e:
                logger.error(f"Failed to load footer config: {e}", exc_info=True)
                self.items = self._default_items()
        else:
            self.items = self._default_items()
            self._save_config()

    def _default_items(self) -> List[FooterItem]:
        """Get default footer items configuration."""
        return [
            # Critical - Always show
            FooterItem(
                id="cursor_model",
                name="Cursor Model",
                priority=FooterItemPriority.CRITICAL,
                category="ai",
                visible=True,
                position=0
            ),
            FooterItem(
                id="branch",
                name="Git Branch",
                priority=FooterItemPriority.CRITICAL,
                category="git",
                visible=True,
                position=1
            ),
            FooterItem(
                id="errors",
                name="Errors",
                priority=FooterItemPriority.CRITICAL,
                category="problems",
                visible=True,
                position=2
            ),
            FooterItem(
                id="warnings",
                name="Warnings",
                priority=FooterItemPriority.CRITICAL,
                category="problems",
                visible=True,
                position=3
            ),

            # High - Show when space available
            FooterItem(
                id="language",
                name="Language",
                priority=FooterItemPriority.HIGH,
                category="editor",
                visible=True,
                position=4
            ),
            FooterItem(
                id="encoding",
                name="Encoding",
                priority=FooterItemPriority.HIGH,
                category="editor",
                visible=True,
                position=5
            ),
            FooterItem(
                id="line_endings",
                name="Line Endings",
                priority=FooterItemPriority.HIGH,
                category="editor",
                visible=True,
                position=6
            ),

            # Medium - Show when space available, hide if crowded
            FooterItem(
                id="cursor_position",
                name="Cursor Position",
                priority=FooterItemPriority.MEDIUM,
                category="editor",
                visible=True,
                position=7
            ),
            FooterItem(
                id="selection",
                name="Selection",
                priority=FooterItemPriority.MEDIUM,
                category="editor",
                visible=True,
                position=8
            ),
            FooterItem(
                id="indent_size",
                name="Indent Size",
                priority=FooterItemPriority.MEDIUM,
                category="editor",
                visible=True,
                position=9
            ),

            # Low - Hide by default, show on hover/expand
            FooterItem(
                id="file_size",
                name="File Size",
                priority=FooterItemPriority.LOW,
                category="editor",
                visible=False,
                position=10
            ),
            FooterItem(
                id="line_count",
                name="Line Count",
                priority=FooterItemPriority.LOW,
                category="editor",
                visible=False,
                position=11
            ),
            FooterItem(
                id="spaces_tabs",
                name="Spaces/Tabs",
                priority=FooterItemPriority.LOW,
                category="editor",
                visible=False,
                position=12
            ),
        ]

    def _save_config(self) -> None:
        """Save footer configuration."""
        try:
            data = {
                'timestamp': __import__('datetime').datetime.now().isoformat(),
                'description': 'Cursor IDE Footer Configuration',
                'items': [item.to_dict() for item in self.items]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save footer config: {e}", exc_info=True)

    def get_visible_items(self, max_items: Optional[int] = None) -> List[FooterItem]:
        """
        Get visible footer items based on priority.

        Args:
            max_items: Maximum number of items to show (None = all visible)

        Returns:
            List of visible footer items
        """
        # Filter by visibility and priority
        visible = [item for item in self.items if item.visible]

        # Sort by priority and position
        priority_order = {
            FooterItemPriority.CRITICAL: 0,
            FooterItemPriority.HIGH: 1,
            FooterItemPriority.MEDIUM: 2,
            FooterItemPriority.LOW: 3,
            FooterItemPriority.HIDDEN: 4
        }

        visible.sort(key=lambda x: (
            priority_order.get(x.priority, 99),
            x.position if x.position is not None else 999
        ))

        # Apply max_items limit if specified
        if max_items:
            # Always include critical items
            critical = [item for item in visible if item.priority == FooterItemPriority.CRITICAL]
            others = [item for item in visible if item.priority != FooterItemPriority.CRITICAL]

            remaining_slots = max_items - len(critical)
            if remaining_slots > 0:
                return critical + others[:remaining_slots]
            else:
                return critical[:max_items]

        return visible

    def get_footer_layout(self, use_two_bars: bool = False) -> Dict[str, Any]:
        """
        Get footer layout configuration.

        Args:
            use_two_bars: Whether to use two footer bars

        Returns:
            Dictionary with layout configuration
        """
        visible = self.get_visible_items()

        if use_two_bars:
            # Split items across two bars
            mid_point = len(visible) // 2
            bar1 = visible[:mid_point]
            bar2 = visible[mid_point:]

            return {
                'layout': 'two_bars',
                'bar1': {
                    'items': [item.to_dict() for item in bar1],
                    'count': len(bar1)
                },
                'bar2': {
                    'items': [item.to_dict() for item in bar2],
                    'count': len(bar2)
                },
                'total': len(visible)
            }
        else:
            # Single bar with priority-based visibility
            # Estimate max items that fit (typically 8-12 items)
            max_fit = 10
            fitted = self.get_visible_items(max_items=max_fit)

            return {
                'layout': 'single_bar_priority',
                'items': [item.to_dict() for item in fitted],
                'visible_count': len(fitted),
                'hidden_count': len(visible) - len(fitted),
                'total': len(visible)
            }

    def suggest_solution(self) -> Dict[str, Any]:
        """
        Suggest best solution for footer management.

        Returns:
            Dictionary with recommendation
        """
        visible = self.get_visible_items()
        total = len(visible)

        # Count by priority
        critical = len([item for item in visible if item.priority == FooterItemPriority.CRITICAL])
        high = len([item for item in visible if item.priority == FooterItemPriority.HIGH])
        medium = len([item for item in visible if item.priority == FooterItemPriority.MEDIUM])
        low = len([item for item in visible if item.priority == FooterItemPriority.LOW])

        # Recommendation logic
        if total <= 8:
            solution = "single_bar"
            reason = "All items fit comfortably in one footer bar"
        elif total <= 16 and critical <= 6:
            solution = "single_bar_priority"
            reason = "Use priority-based visibility - show critical/high, hide medium/low"
        elif total > 16 or critical > 8:
            solution = "two_bars"
            reason = "Too many items - use two footer bars or aggressive priority filtering"
        else:
            solution = "single_bar_priority"
            reason = "Use priority-based visibility with grouping"

        return {
            'solution': solution,
            'reason': reason,
            'stats': {
                'total': total,
                'critical': critical,
                'high': high,
                'medium': medium,
                'low': low
            },
            'recommendation': self._get_recommendation_details(solution)
        }

    def _get_recommendation_details(self, solution: str) -> Dict[str, Any]:
        """Get detailed recommendation for solution."""
        if solution == "two_bars":
            return {
                'action': 'Configure two footer bars',
                'steps': [
                    'Enable secondary status bar in Cursor settings',
                    'Split items: Critical/High on bar 1, Medium/Low on bar 2',
                    'Or: Editor items on bar 1, System items on bar 2'
                ],
                'config': self.get_footer_layout(use_two_bars=True)
            }
        elif solution == "single_bar_priority":
            return {
                'action': 'Use priority-based visibility',
                'steps': [
                    'Show only Critical and High priority items',
                    'Hide Medium and Low priority items',
                    'Add hover/click to expand and show hidden items',
                    'Group related items together'
                ],
                'config': self.get_footer_layout(use_two_bars=False)
            }
        else:
            return {
                'action': 'Current layout is fine',
                'steps': ['No changes needed'],
                'config': self.get_footer_layout(use_two_bars=False)
            }


def main():
    """CLI interface for footer manager."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Cursor Footer Manager")
    parser.add_argument('--suggest', action='store_true', help='Suggest solution')
    parser.add_argument('--layout', action='store_true', help='Show layout')
    parser.add_argument('--two-bars', action='store_true', help='Show two-bar layout')
    parser.add_argument('--priority', action='store_true', help='Show priority-based layout')

    args = parser.parse_args()

    manager = JARVISCursorFooterManager()

    if args.suggest or not any([args.layout, args.two_bars, args.priority]):
        suggestion = manager.suggest_solution()
        print("\n💡 **Footer Management Suggestion**")
        print(f"Solution: {suggestion['solution']}")
        print(f"Reason: {suggestion['reason']}")
        print(f"\nStats:")
        print(f"  Total items: {suggestion['stats']['total']}")
        print(f"  Critical: {suggestion['stats']['critical']}")
        print(f"  High: {suggestion['stats']['high']}")
        print(f"  Medium: {suggestion['stats']['medium']}")
        print(f"  Low: {suggestion['stats']['low']}")
        print(f"\nRecommendation:")
        rec = suggestion['recommendation']
        print(f"  Action: {rec['action']}")
        print(f"  Steps:")
        for step in rec['steps']:
            print(f"    - {step}")

    if args.layout:
        layout = manager.get_footer_layout(use_two_bars=False)
        print(f"\n📊 Single Bar Layout:")
        print(f"  Visible: {layout['visible_count']} items")
        print(f"  Hidden: {layout['hidden_count']} items")
        print(f"  Total: {layout['total']} items")

    if args.two_bars:
        layout = manager.get_footer_layout(use_two_bars=True)
        print(f"\n📊 Two Bar Layout:")
        print(f"  Bar 1: {layout['bar1']['count']} items")
        print(f"  Bar 2: {layout['bar2']['count']} items")
        print(f"  Total: {layout['total']} items")


if __name__ == "__main__":


    main()