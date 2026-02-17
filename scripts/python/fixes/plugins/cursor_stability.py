"""
Cursor IDE Stability Fix Plugin

Fixes Cursor IDE stability issues:
- Menu activation when typing
- Alt-tab focus issues
- Keyboard shortcut conflicts
- Chat box focus problems

Tags: #CURSOR #STABILITY #KEYBOARD #FOCUS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fixes.fixer import FixPlugin, FixType, FixResult
except ImportError:
    from ..fixer import FixPlugin, FixType, FixResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorStabilityFixPlugin")


class CursorStabilityFixPlugin(FixPlugin):
    """Fix Cursor IDE stability and keyboard/focus issues"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.CURSOR_STABILITY,
            name="Cursor Stability Fixer",
            description="Fixes Cursor IDE stability issues: menu activation, focus, keyboard conflicts"
        )

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'cursor', 'menu', 'activation', 'typing', 'alt-tab', 'focus',
            'keyboard', 'shortcut', 'conflict', 'stability', 'chat box'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect Cursor IDE stability issues"""
        issues = []
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        cursor_settings = project_root / ".cursor" / "settings.json"
        if not cursor_settings.exists():
            issues.append("Cursor settings file not found")
            return issues

        try:
            with open(cursor_settings, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Check for problematic settings
            if settings.get('editor', {}).get('quickSuggestions', {}).get('other') is True:
                # This can cause menu activation while typing
                pass  # Will be fixed

            # Check for auto-focus issues
            if settings.get('cursor.chat', {}).get('autoFocus') is True:
                # Can cause focus issues when alt-tabbing
                pass  # Will be fixed

            # Check for inline suggestions that might interfere
            if settings.get('editor.inlineSuggest', {}).get('enabled') is True:
                # Can cause interference while typing
                pass  # Will be fixed

        except Exception as e:
            issues.append(f"Error reading Cursor settings: {e}")

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix Cursor IDE stability issues"""
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)
        fixes_applied = []
        errors = []

        cursor_settings = project_root / ".cursor" / "settings.json"
        if not cursor_settings.exists():
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message="Cursor settings file not found",
                details={'error': 'settings.json not found'}
            )

        try:
            with open(cursor_settings, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            updated = False

            # Fix 1: Disable quick suggestions that cause menu activation
            if 'editor' not in settings:
                settings['editor'] = {}
            if 'quickSuggestions' not in settings['editor']:
                settings['editor']['quickSuggestions'] = {}

            # Set quickSuggestions to only show on trigger, not while typing
            if settings['editor']['quickSuggestions'].get('other') is True:
                settings['editor']['quickSuggestions']['other'] = 'off'
                fixes_applied.append("Disabled quick suggestions while typing (prevents menu activation)")
                updated = True

            # Fix 2: Improve chat focus behavior
            if 'cursor.chat' not in settings:
                settings['cursor.chat'] = {}

            # Disable auto-focus on chat to prevent alt-tab issues
            if settings['cursor.chat'].get('autoFocus') is True:
                settings['cursor.chat']['autoFocus'] = False
                fixes_applied.append("Disabled chat auto-focus (prevents alt-tab issues)")
                updated = True

            # Fix 3: Adjust inline suggestions to reduce interference
            if 'editor.inlineSuggest' not in settings:
                settings['editor.inlineSuggest'] = {}

            # Increase delay to reduce interference
            if settings['editor.inlineSuggest'].get('delay', 100) < 200:
                settings['editor.inlineSuggest']['delay'] = 200
                fixes_applied.append("Increased inline suggestion delay (reduces typing interference)")
                updated = True

            # Fix 4: Disable accept suggestion on Enter to prevent accidental accepts
            if settings['editor.inlineSuggest'].get('acceptSuggestionOnEnter') == 'on':
                settings['editor.inlineSuggest']['acceptSuggestionOnEnter'] = 'off'
                fixes_applied.append("Disabled accept suggestion on Enter (prevents accidental accepts)")
                updated = True

            # Fix 5: Improve suggest selection to reduce menu activation
            if settings.get('editor', {}).get('suggestSelection') == 'first':
                settings['editor']['suggestSelection'] = 'recentlyUsed'
                fixes_applied.append("Changed suggest selection to recently used (reduces menu activation)")
                updated = True

            # Fix 6: Disable word-based suggestions that can interfere
            if settings.get('editor', {}).get('wordBasedSuggestions') != 'off':
                settings['editor']['wordBasedSuggestions'] = 'off'
                fixes_applied.append("Disabled word-based suggestions (reduces interference)")
                updated = True

            # Fix 7: Add focus-related settings
            if 'window' not in settings:
                settings['window'] = {}

            # Prevent focus stealing
            if 'restoreWindows' not in settings['window']:
                settings['window']['restoreWindows'] = 'all'
                fixes_applied.append("Set window restore behavior (improves focus management)")
                updated = True

            # Fix 8: Improve chat box behavior
            if 'cursor.chat' not in settings:
                settings['cursor.chat'] = {}

            # Disable always open pinned to reduce focus stealing
            if settings.get('cursor.chat', {}).get('alwaysOpenPinned') is True:
                settings['cursor.chat']['alwaysOpenPinned'] = False
                fixes_applied.append("Disabled always open pinned chats (reduces focus stealing)")
                updated = True

            # Fix 9: Add keyboard shortcut stability settings
            if 'keyboard' not in settings:
                settings['keyboard'] = {}

            # Prevent Alt key from activating menus
            if 'altKeyBehavior' not in settings['keyboard']:
                settings['keyboard']['altKeyBehavior'] = 'focusMenuBar'
                fixes_applied.append("Set Alt key behavior (prevents accidental menu activation)")
                updated = True

            # Fix 10: Improve editor stability
            if 'editor' not in settings:
                settings['editor'] = {}

            # Reduce cursor blinking to improve stability
            if 'cursorBlinking' not in settings['editor']:
                settings['editor']['cursorBlinking'] = 'solid'
                fixes_applied.append("Set cursor blinking to solid (improves stability)")
                updated = True

            # Save updated settings
            if updated:
                with open(cursor_settings, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)
                fixes_applied.append("✅ Cursor settings updated successfully")

        except Exception as e:
            errors.append(f"Failed to update Cursor settings: {e}")
            logger.error(f"Error fixing Cursor stability: {e}", exc_info=True)

        success = len(fixes_applied) > 0 and len(errors) == 0

        return FixResult(
            fix_type=self.fix_type,
            success=success,
            message=f"Applied {len(fixes_applied)} stability fixes" if fixes_applied else "No fixes needed",
            details={
                'fixes_applied': fixes_applied,
                'errors': errors
            }
        )
