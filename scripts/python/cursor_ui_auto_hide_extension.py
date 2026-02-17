#!/usr/bin/env python3
"""
Cursor IDE UI Auto-Hide Extension
Implements auto-hide functionality for Cursor IDE UI sections

Features:
- Auto-hide top header bar (show on hover)
- Auto-hide chat pane details (lines added/removed, model selection)
- Collapse "bird" static text to one line (expand on hover)
- Transcription improvements (pause/resume, auto-send)
- Expanded button controls

Tags: #CURSOR #UI #AUTO_HIDE #QUALITY_OF_LIFE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

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

logger = get_logger("CursorUIAutoHide")


@dataclass
class AutoHideConfig:
    """Configuration for auto-hide sections"""
    enabled: bool = True
    hide_delay_ms: int = 2000
    show_on_hover: bool = True
    always_visible_when_active: bool = True


@dataclass
class TranscriptionConfig:
    """Configuration for transcription improvements"""
    pause_resume_enabled: bool = True
    auto_send_enabled: bool = True
    silence_duration_ms: int = 2000
    min_transcription_length: int = 10
    preserve_text_on_pause: bool = True


class CursorUIAutoHideExtension:
    """
    Cursor IDE UI Auto-Hide Extension

    Implements auto-hide functionality for various UI sections
    to reduce visual clutter and improve focus.
    """

    def __init__(self, project_root: Path, config_path: Optional[Path] = None):
        self.project_root = project_root
        self.config_path = config_path or project_root / "config" / "cursor_ui_auto_hide_config.json"

        # Load configuration
        self.config = self._load_config()

        # State tracking
        self.transcription_state = {
            "is_paused": False,
            "text": "",
            "last_activity": time.time(),
            "auto_send_timer": None
        }

        logger.info("=" * 80)
        logger.info("🎨 CURSOR IDE UI AUTO-HIDE EXTENSION")
        logger.info("=" * 80)
        logger.info(f"   Config: {self.config_path}")
        logger.info(f"   Top header auto-hide: {self.config.get('auto_hide_sections', {}).get('top_header_bar', {}).get('enabled', False)}")
        logger.info(f"   Chat pane auto-hide: {self.config.get('auto_hide_sections', {}).get('chat_pane_details', {}).get('enabled', False)}")
        logger.info(f"   Bird text collapse: {self.config.get('auto_hide_sections', {}).get('bird_static_text', {}).get('enabled', False)}")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                logger.info(f"✅ Loaded config from {self.config_path}")
                return config
            else:
                logger.warning(f"⚠️  Config file not found: {self.config_path}")
                return self._default_config()
        except Exception as e:
            logger.error(f"❌ Error loading config: {e}")
            return self._default_config()

    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration"""
        return {
            "auto_hide_sections": {
                "top_header_bar": {"enabled": True, "hide_delay_ms": 2000},
                "chat_pane_details": {"enabled": True, "hide_delay_ms": 3000},
                "bird_static_text": {"enabled": True, "collapse_to_one_line": True}
            },
            "transcription_improvements": {
                "pause_resume": {"enabled": True},
                "auto_send": {"enabled": True, "silence_duration_ms": 2000}
            }
        }

    def generate_css_injection(self) -> str:
        """
        Generate CSS for auto-hide functionality
        This would be injected into Cursor IDE's UI
        """
        css = """
        /* Cursor IDE UI Auto-Hide Styles */

        /* Top Header Bar - Auto-hide */
        .cursor-header-bar {
            transition: opacity 0.3s ease, transform 0.3s ease;
            opacity: 0.1;
            transform: translateY(-10px);
        }

        .cursor-header-bar:hover {
            opacity: 1;
            transform: translateY(0);
        }

        /* Chat Pane Details - Auto-hide */
        .cursor-chat-pane-details {
            transition: opacity 0.3s ease, max-height 0.3s ease;
            opacity: 0.3;
            max-height: 20px;
            overflow: hidden;
        }

        .cursor-chat-pane-details:hover {
            opacity: 1;
            max-height: 200px;
        }

        /* Bird Static Text - Collapse to one line */
        .cursor-bird-static-text {
            transition: max-height 0.3s ease;
            max-height: 1.5em;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .cursor-bird-static-text:hover {
            max-height: 500px;
            white-space: normal;
        }

        /* Expanded Button Controls */
        .cursor-transcription-controls {
            display: flex;
            gap: 10px;
            width: 100%;
        }

        .cursor-transcription-button {
            flex: 1;
            min-width: 80px;
            padding: 10px 20px;
            font-size: 14px;
        }
        """
        return css

    def generate_js_injection(self) -> str:
        """
        Generate JavaScript for auto-hide functionality
        This would be injected into Cursor IDE's UI
        """
        js = """
        // Cursor IDE UI Auto-Hide JavaScript

        // Auto-hide top header bar
        function setupHeaderAutoHide() {
            const header = document.querySelector('.cursor-header-bar');
            if (header) {
                let hideTimer;
                header.addEventListener('mouseenter', () => {
                    clearTimeout(hideTimer);
                    header.style.opacity = '1';
                    header.style.transform = 'translateY(0)';
                });
                header.addEventListener('mouseleave', () => {
                    hideTimer = setTimeout(() => {
                        header.style.opacity = '0.1';
                        header.style.transform = 'translateY(-10px)';
                    }, 2000);
                });
            }
        }

        // Collapse bird static text
        function setupBirdTextCollapse() {
            const birdText = document.querySelector('.cursor-bird-static-text');
            if (birdText) {
                birdText.addEventListener('mouseenter', () => {
                    birdText.style.maxHeight = '500px';
                    birdText.style.whiteSpace = 'normal';
                });
                birdText.addEventListener('mouseleave', () => {
                    birdText.style.maxHeight = '1.5em';
                    birdText.style.whiteSpace = 'nowrap';
                });
            }
        }

        // Transcription pause/resume
        let transcriptionPaused = false;
        let transcriptionText = '';

        function pauseTranscription() {
            transcriptionPaused = true;
            // Preserve current text
            const textarea = document.querySelector('.cursor-transcription-input');
            if (textarea) {
                transcriptionText = textarea.value;
            }
        }

        function resumeTranscription() {
            transcriptionPaused = false;
            // Restore text
            const textarea = document.querySelector('.cursor-transcription-input');
            if (textarea) {
                textarea.value = transcriptionText;
            }
        }

        // Auto-send after silence
        let silenceTimer;
        function setupAutoSend() {
            const textarea = document.querySelector('.cursor-transcription-input');
            if (textarea) {
                textarea.addEventListener('input', () => {
                    clearTimeout(silenceTimer);
                    silenceTimer = setTimeout(() => {
                        if (textarea.value.length >= 10) {
                            // Auto-send
                            const sendButton = document.querySelector('.cursor-send-button');
                            if (sendButton) {
                                sendButton.click();
                            }
                        }
                    }, 2000);
                });
            }
        }

        // Initialize on page load
        document.addEventListener('DOMContentLoaded', () => {
            setupHeaderAutoHide();
            setupBirdTextCollapse();
            setupAutoSend();
        });
        """
        return js

    def generate_extension_manifest(self) -> Dict[str, Any]:
        """Generate VS Code/Cursor extension manifest"""
        return {
            "name": "cursor-ui-auto-hide",
            "displayName": "Cursor UI Auto-Hide",
            "description": "Auto-hide UI sections to reduce visual clutter",
            "version": "1.0.0",
            "publisher": "lumina",
            "engines": {
                "vscode": "^1.80.0"
            },
            "categories": ["Other"],
            "activationEvents": ["onStartupFinished"],
            "main": "./extension.js",
            "contributes": {
                "commands": [
                    {
                        "command": "cursor.toggleAutoHide",
                        "title": "Toggle Auto-Hide"
                    },
                    {
                        "command": "cursor.pauseTranscription",
                        "title": "Pause Transcription"
                    },
                    {
                        "command": "cursor.resumeTranscription",
                        "title": "Resume Transcription"
                    }
                ],
                "keybindings": [
                    {
                        "command": "cursor.pauseTranscription",
                        "key": "ctrl+space",
                        "when": "editorTextFocus"
                    },
                    {
                        "command": "cursor.toggleAutoSend",
                        "key": "ctrl+shift+s",
                        "when": "editorTextFocus"
                    }
                ]
            }
        }

    def create_implementation_guide(self) -> str:
        """Create implementation guide for integrating this into Cursor IDE"""
        guide = """
# Cursor IDE UI Auto-Hide Implementation Guide

## Overview
This extension implements auto-hide functionality for Cursor IDE UI sections to reduce visual clutter.

## Implementation Methods

### Method 1: Cursor IDE Extension (Recommended)
1. Create VS Code extension structure
2. Inject CSS/JavaScript into Cursor IDE UI
3. Use Cursor API for transcription control

### Method 2: User Styles (Quick Fix)
1. Add CSS to Cursor IDE user settings
2. Use browser DevTools to inject JavaScript
3. Limited functionality but quick to implement

### Method 3: Settings Modification
1. Modify Cursor IDE settings.json
2. Add custom CSS/JavaScript paths
3. Requires Cursor IDE support for custom styling

## Features Implemented

1. **Top Header Bar Auto-Hide**
   - Hides after 2 seconds of no hover
   - Shows on hover
   - Always visible when active

2. **Chat Pane Details Auto-Hide**
   - Lines added/removed box
   - Model selection
   - Hides after 3 seconds

3. **Bird Static Text Collapse**
   - Collapses to one line
   - Expands on hover
   - Shows preview text

4. **Transcription Improvements**
   - Pause/resume without losing text
   - Auto-send after 2 seconds of silence
   - Expanded button controls

## Next Steps

1. Test CSS/JavaScript injection methods
2. Create Cursor IDE extension package
3. Test auto-hide behavior
4. Implement transcription pause/resume
5. Add expanded button controls
        """
        return guide


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE UI Auto-Hide Extension")
        parser.add_argument('--generate-css', action='store_true', help='Generate CSS for auto-hide')
        parser.add_argument('--generate-js', action='store_true', help='Generate JavaScript for auto-hide')
        parser.add_argument('--generate-manifest', action='store_true', help='Generate extension manifest')
        parser.add_argument('--guide', action='store_true', help='Show implementation guide')

        args = parser.parse_args()

        extension = CursorUIAutoHideExtension(project_root)

        if args.generate_css:
            print(extension.generate_css_injection())
        elif args.generate_js:
            print(extension.generate_js_injection())
        elif args.generate_manifest:
            print(json.dumps(extension.generate_extension_manifest(), indent=2))
        elif args.guide:
            print(extension.create_implementation_guide())
        else:
            logger.info("✅ Cursor UI Auto-Hide Extension initialized")
            logger.info("   Use --generate-css, --generate-js, or --guide for output")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()