#!/usr/bin/env python3
"""
Cursor Intent Preview Extension - Kilo Code Style Integration

Provides intent reformatting preview in Cursor IDE before sending messages.
Integrates with Cursor's extension system to show AI SPEAK format.

Tags: #CURSOR_EXTENSION #INTENT_PREVIEW #KILO_CODE #AI_SPEAK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from ai_intent_reformatter import AIIntentReformatter, IntentReformat
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    AIIntentReformatter = None

logger = get_logger("CursorIntentPreview")


class CursorIntentPreview:
    """
    Cursor Intent Preview - Shows reformatted intent before sending

    Works as a pre-send hook that:
    1. Captures user input
    2. Reformats into AI SPEAK
    3. Shows preview for review
    4. Sends confirmed version
    """

    def __init__(self):
        """Initialize intent preview"""
        if AIIntentReformatter:
            self.formatter = AIIntentReformatter()
        else:
            self.formatter = None
            logger.warning("⚠️  Intent reformatter not available")

        self.preview_data_dir = project_root / "data" / "intent_previews"
        self.preview_data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Cursor Intent Preview initialized")

    def preview_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Preview reformatted intent

        Returns preview data for display in Cursor.
        """
        if not self.formatter:
            return {
                "original": user_input,
                "reformatted": user_input,
                "available": False
            }

        reformat = self.formatter.reformat_intent(user_input)

        preview_data = {
            "original": reformat.original,
            "reformatted": reformat.reformatted,
            "action_word": reformat.action_word,
            "context": reformat.context,
            "intent": reformat.intent,
            "confidence": reformat.confidence,
            "suggestions": reformat.suggestions,
            "available": True,
            "metadata": reformat.metadata
        }

        # Save preview for history
        self._save_preview(preview_data)

        return preview_data

    def _save_preview(self, preview_data: Dict[str, Any]):
        """Save preview to history"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"preview_{timestamp}.json"
            filepath = self.preview_data_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(preview_data, f, indent=2)

            logger.debug(f"💾 Preview saved: {filepath}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save preview: {e}")

    def format_preview_html(self, preview_data: Dict[str, Any]) -> str:
        """Format preview as HTML for Cursor display"""
        if not preview_data.get("available"):
            return f"""
            <div class="intent-preview">
                <p><strong>Original:</strong> {preview_data['original']}</p>
                <p><em>Intent reformatting not available</em></p>
            </div>
            """

        html = f"""
        <div class="intent-preview">
            <div class="preview-section">
                <h3>📝 Original Intent</h3>
                <p class="original-text">{preview_data['original']}</p>
            </div>

            <div class="preview-section">
                <h3>✨ AI SPEAK (Reformatted)</h3>
                <p class="reformatted-text">{preview_data['reformatted']}</p>
            </div>

            <div class="preview-metadata">
        """

        if preview_data.get("action_word"):
            html += f'<span class="badge">Action: {preview_data["action_word"]}</span>'

        if preview_data.get("context"):
            html += f'<span class="badge">Context: {preview_data["context"][:50]}...</span>'

        if preview_data.get("intent"):
            html += f'<span class="badge">Intent: {preview_data["intent"][:50]}...</span>'

        confidence = preview_data.get("confidence", 0)
        html += f'<span class="badge confidence-{int(confidence * 10)}">Confidence: {confidence:.0%}</span>'

        html += """
            </div>
        """

        if preview_data.get("suggestions"):
            html += """
            <div class="suggestions">
                <h4>💡 Suggestions</h4>
                <ul>
            """
            for suggestion in preview_data["suggestions"]:
                html += f"<li>{suggestion}</li>"
            html += """
                </ul>
            </div>
            """

        html += """
            <div class="actions">
                <button class="btn-send-reformatted">Send Reformatted</button>
                <button class="btn-send-original">Send Original</button>
                <button class="btn-edit">Edit</button>
            </div>
        </div>
        """

        return html

    def format_preview_markdown(self, preview_data: Dict[str, Any]) -> str:
        """Format preview as Markdown"""
        if not preview_data.get("available"):
            return f"**Original:** {preview_data['original']}\n\n*Intent reformatting not available*"

        md = []
        md.append("## 🎯 Intent Preview - Review Before Sending\n")
        md.append(f"**📝 Original:**\n{preview_data['original']}\n")
        md.append(f"**✨ AI SPEAK (Reformatted):**\n{preview_data['reformatted']}\n")

        if preview_data.get("action_word"):
            md.append(f"- **Action:** {preview_data['action_word']}")
        if preview_data.get("context"):
            md.append(f"- **Context:** {preview_data['context']}")
        if preview_data.get("intent"):
            md.append(f"- **Intent:** {preview_data['intent']}")

        confidence = preview_data.get("confidence", 0)
        md.append(f"- **Confidence:** {confidence:.0%}\n")

        if preview_data.get("suggestions"):
            md.append("**💡 Suggestions:**")
            for suggestion in preview_data["suggestions"]:
                md.append(f"- {suggestion}")
            md.append("")

        return "\n".join(md)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor Intent Preview")
        parser.add_argument("input", help="User input to preview")
        parser.add_argument("--format", choices=["json", "html", "markdown"], default="json",
                           help="Output format")
        args = parser.parse_args()

        preview = CursorIntentPreview()
        preview_data = preview.preview_intent(args.input)

        if args.format == "json":
            print(json.dumps(preview_data, indent=2))
        elif args.format == "html":
            print(preview.format_preview_html(preview_data))
        elif args.format == "markdown":
            print(preview.format_preview_markdown(preview_data))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())