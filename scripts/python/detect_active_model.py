#!/usr/bin/env python3
"""
Detect Active AI Model in Cursor IDE
Attempts to determine which AI model is currently active
"""

import json
import os
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

def detect_active_model():
    """Try to detect the active AI model"""
    model_info = {
        "provider": "Unknown",
        "model": "Unknown",
        "source": "Unknown"
    }

    # Method 1: Check Cursor settings
    cursor_settings_paths = [
        Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
        Path.home() / ".cursor" / "settings.json",
    ]

    for settings_path in cursor_settings_paths:
        if settings_path.exists():
            try:
                with open(settings_path, 'r') as f:
                    settings = json.load(f)

                # Look for model settings
                if "cursor.ai.model" in settings:
                    model_info["model"] = settings["cursor.ai.model"]
                    model_info["source"] = "settings.json"
                    if "claude" in model_info["model"].lower():
                        model_info["provider"] = "Anthropic"
                    elif "gpt" in model_info["model"].lower():
                        model_info["provider"] = "OpenAI"
                    break
            except:
                pass

    # Method 2: Check environment
    if model_info["provider"] == "Unknown":
        if os.environ.get("ANTHROPIC_API_KEY"):
            model_info["provider"] = "Anthropic"
            model_info["model"] = "Claude (detected from API key)"
            model_info["source"] = "environment"
        elif os.environ.get("OPENAI_API_KEY"):
            model_info["provider"] = "OpenAI"
            model_info["model"] = "GPT (detected from API key)"
            model_info["source"] = "environment"

    # Method 3: Default assumption (Cursor typically uses Claude)
    if model_info["provider"] == "Unknown":
        model_info["provider"] = "Anthropic"
        model_info["model"] = "Claude (default assumption)"
        model_info["source"] = "default"

    return model_info

def format_model_display(model_info):
    """Format model info for display in chat title"""
    model_name = model_info["model"]

    # Simplify model names
    if "claude" in model_name.lower():
        if "sonnet" in model_name.lower() or "4.5" in model_name:
            return "[Claude Sonnet 4.5]"
        elif "opus" in model_name.lower():
            return "[Claude Opus]"
        elif "haiku" in model_name.lower():
            return "[Claude Haiku]"
        else:
            return "[Claude]"
    elif "gpt" in model_name.lower():
        if "4" in model_name and "turbo" in model_name.lower():
            return "[GPT-4 Turbo]"
        elif "4" in model_name:
            return "[GPT-4]"
        elif "3.5" in model_name:
            return "[GPT-3.5]"
        else:
            return "[GPT]"
    else:
        return f"[{model_info['provider']}]"

if __name__ == "__main__":
    model_info = detect_active_model()
    display = format_model_display(model_info)

    print(json.dumps({
        "provider": model_info["provider"],
        "model": model_info["model"],
        "display": display,
        "source": model_info["source"]
    }))
