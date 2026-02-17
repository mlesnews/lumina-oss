"""
JARVIS Footer Ticker/Banner System
Airport ticker / LED sign effect for Cursor IDE footer.

Slow scrolling banner that rotates through all footer items,
like an airport ticker or LED sign.

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #CURSOR #FOOTER #TICKER #BANNER
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


@dataclass
class TickerItem:
    """Item in the ticker banner."""
    id: str
    text: str
    priority: int = 0
    color: Optional[str] = None
    icon: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class JARVISFooterTickerBanner:
    """
    Airport ticker / LED sign effect for footer.

    Features:
    - Slow horizontal scrolling
    - Rotates through all items
    - LED sign aesthetic
    - Smooth animation
    - Configurable speed
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize ticker banner system.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

        # File paths
        self.config_file = self.project_root / "config" / "footer_ticker_config.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Ticker settings
        self.scroll_speed = 30  # Pixels per second (slow)
        self.item_spacing = 50  # Pixels between items
        self.loop = True  # Loop continuously
        self.pause_on_hover = True  # Pause when hovering

        # Load items
        self.items: List[TickerItem] = []
        self._load_config()

    def _load_config(self) -> None:
        """Load ticker configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.items = [
                        TickerItem(**item) for item in data.get('items', [])
                    ]
                    self.scroll_speed = data.get('scroll_speed', 30)
                    self.item_spacing = data.get('item_spacing', 50)
            except Exception as e:
                logger.error(f"Failed to load ticker config: {e}", exc_info=True)
                self.items = self._default_items()
        else:
            self.items = self._default_items()
            self._save_config()

    def _default_items(self) -> List[TickerItem]:
        """Get default ticker items."""
        from jarvis_cursor_footer_manager import JARVISCursorFooterManager

        footer_manager = JARVISCursorFooterManager(self.project_root)
        footer_items = footer_manager.get_visible_items()

        ticker_items = []
        for item in footer_items:
            # Format as ticker text
            text = self._format_ticker_text(item)
            ticker_item = TickerItem(
                id=item.id,
                text=text,
                priority=item.position or 0,
                icon=self._get_icon_for_item(item),
                metadata={'footer_item': item.to_dict()}
            )
            ticker_items.append(ticker_item)

        return ticker_items

    def _format_ticker_text(self, footer_item: Any) -> str:
        """Format footer item as ticker text."""
        # Format: "ICON | NAME: VALUE" or "NAME: VALUE"
        icon = self._get_icon_for_item(footer_item)
        name = footer_item.name

        if icon:
            return f"{icon} {name}"
        else:
            return name

    def _get_icon_for_item(self, footer_item: Any) -> Optional[str]:
        """Get icon for footer item."""
        icon_map = {
            'cursor_model': '🤖',
            'branch': '🌿',
            'errors': '❌',
            'warnings': '⚠️',
            'language': '📝',
            'encoding': '🔤',
            'line_endings': '↩️',
            'cursor_position': '📍',
            'selection': '✂️',
            'indent_size': '↹',
            'file_size': '📊',
            'line_count': '📏'
        }
        return icon_map.get(footer_item.id)

    def _save_config(self) -> None:
        """Save ticker configuration."""
        try:
            data = {
                'timestamp': datetime.now().isoformat(),
                'description': 'Footer Ticker Banner Configuration',
                'scroll_speed': self.scroll_speed,
                'item_spacing': self.item_spacing,
                'loop': self.loop,
                'pause_on_hover': self.pause_on_hover,
                'items': [item.to_dict() for item in self.items]
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save ticker config: {e}", exc_info=True)

    def generate_css_animation(self) -> str:
        """
        Generate CSS for ticker animation.

        Returns:
            CSS code for ticker banner
        """
        # Calculate total width needed
        total_width = sum(len(item.text) * 8 + self.item_spacing for item in self.items)

        css = f"""
/* JARVIS Footer Ticker Banner - Airport LED Sign Effect */
.footer-ticker-container {{
    width: 100%;
    height: 22px;
    overflow: hidden;
    position: relative;
    background: var(--vscode-statusBar-background);
    border-top: 1px solid var(--vscode-statusBar-border);
}}

.footer-ticker-track {{
    display: flex;
    white-space: nowrap;
    animation: ticker-scroll {total_width / self.scroll_speed}s linear infinite;
    will-change: transform;
}}

.footer-ticker-track:hover {{
    animation-play-state: {'paused' if self.pause_on_hover else 'running'};
}}

.footer-ticker-item {{
    display: inline-block;
    padding: 0 {self.item_spacing / 2}px;
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: var(--vscode-statusBar-foreground);
    text-shadow: 0 0 2px currentColor;
    letter-spacing: 1px;
}}

/* LED Sign Effect */
.footer-ticker-item::before {{
    content: '●';
    margin-right: 4px;
    color: var(--vscode-statusBar-foreground);
    opacity: 0.6;
    animation: blink 2s infinite;
}}

@keyframes ticker-scroll {{
    0% {{
        transform: translateX(0);
    }}
    100% {{
        transform: translateX(-{total_width}px);
    }}
}}

@keyframes blink {{
    0%, 100% {{ opacity: 0.6; }}
    50% {{ opacity: 1; }}
}}

/* Smooth scrolling */
.footer-ticker-track {{
    transition: transform 0.1s ease-out;
}}
"""
        return css.strip()

    def generate_html_structure(self) -> str:
        """
        Generate HTML structure for ticker.

        Returns:
            HTML code for ticker banner
        """
        items_html = '\n'.join([
            f'        <span class="footer-ticker-item" data-id="{item.id}">{item.text}</span>'
            for item in self.items
        ])

        html = f"""
<div class="footer-ticker-container">
    <div class="footer-ticker-track">
{items_html}
        <!-- Duplicate for seamless loop -->
{items_html}
    </div>
</div>
"""
        return html.strip()

    def generate_extension_code(self) -> str:
        try:
            """
            Generate VS Code extension code for ticker.

            Returns:
                TypeScript code for extension
            """
            items_json = json.dumps([item.to_dict() for item in self.items], indent=2)

            code = f"""
        except Exception as e:
            self.logger.error(f"Error in generate_extension_code: {e}", exc_info=True)
            raise
// JARVIS Footer Ticker Banner Extension
import * as vscode from 'vscode';

const TICKER_ITEMS = {items_json};

const SCROLL_SPEED = {self.scroll_speed}; // pixels per second
const ITEM_SPACING = {self.item_spacing}; // pixels

export function activate(context: vscode.ExtensionContext) {{
    // Create ticker status bar item
    const tickerItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Left,
        1000
    );

    let currentIndex = 0;
    let scrollPosition = 0;

    // Update ticker display
    function updateTicker() {{
        const items = TICKER_ITEMS.map(item => 
            `${{item.icon || ''}} ${{item.text}}`
        ).join('  •  ');

        // Simulate scrolling by rotating through items
        const visibleItems = TICKER_ITEMS.slice(currentIndex, currentIndex + 5);
        const displayText = visibleItems.map(item => 
            `${{item.icon || ''}} ${{item.text}}`
        ).join('  •  ');

        tickerItem.text = `$(sync~spin) ${{displayText}}`;
        tickerItem.tooltip = `All items: ${{items}}`;
        tickerItem.show();

        // Rotate to next item
        currentIndex = (currentIndex + 1) % TICKER_ITEMS.length;
    }}

    // Update every 3 seconds (slow scroll)
    const interval = setInterval(updateTicker, 3000);
    updateTicker();

    context.subscriptions.push(tickerItem);
    context.subscriptions.push({{ dispose: () => clearInterval(interval) }});
}}

export function deactivate() {{
    // Cleanup
}}
"""
        except Exception as e:
            logger.error(f"Error generating VS Code extension: {e}")
            raise
        return code.strip()

    def get_ticker_config(self) -> Dict[str, Any]:
        """
        Get ticker configuration.

        Returns:
            Dictionary with ticker config
        """
        return {
            'scroll_speed': self.scroll_speed,
            'item_spacing': self.item_spacing,
            'loop': self.loop,
            'pause_on_hover': self.pause_on_hover,
            'total_items': len(self.items),
            'estimated_duration': sum(len(item.text) * 8 + self.item_spacing for item in self.items) / self.scroll_speed,
            'items': [item.to_dict() for item in self.items]
        }


def main():
    """CLI interface for ticker banner."""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Footer Ticker Banner")
    parser.add_argument('--css', action='store_true', help='Generate CSS')
    parser.add_argument('--html', action='store_true', help='Generate HTML')
    parser.add_argument('--extension', action='store_true', help='Generate extension code')
    parser.add_argument('--config', action='store_true', help='Show config')
    parser.add_argument('--speed', type=int, help='Set scroll speed (pixels/second)')

    args = parser.parse_args()

    ticker = JARVISFooterTickerBanner()

    if args.speed:
        ticker.scroll_speed = args.speed
        ticker._save_config()
        print(f"✅ Scroll speed set to {args.speed} pixels/second")

    if args.config or not any([args.css, args.html, args.extension]):
        config = ticker.get_ticker_config()
        print("\n📊 **Ticker Banner Configuration**")
        print(f"Scroll Speed: {config['scroll_speed']} pixels/second")
        print(f"Item Spacing: {config['item_spacing']} pixels")
        print(f"Loop: {config['loop']}")
        print(f"Pause on Hover: {config['pause_on_hover']}")
        print(f"Total Items: {config['total_items']}")
        print(f"Estimated Duration: {config['estimated_duration']:.1f} seconds per cycle")
        print(f"\nItems ({len(config['items'])}):")
        for item in config['items']:
            print(f"  - {item.get('icon', '')} {item['text']}")

    if args.css:
        print("\n" + "="*60)
        print("CSS CODE:")
        print("="*60)
        print(ticker.generate_css_animation())

    if args.html:
        print("\n" + "="*60)
        print("HTML CODE:")
        print("="*60)
        print(ticker.generate_html_structure())

    if args.extension:
        print("\n" + "="*60)
        print("EXTENSION CODE (TypeScript):")
        print("="*60)
        print(ticker.generate_extension_code())


if __name__ == "__main__":


    main()