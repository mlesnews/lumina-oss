#!/usr/bin/env python3
"""
Check Active AI Model/Provider
Shows which AI model is currently being used in Cursor IDE
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

print("=" * 60)
print("Active AI Model/Provider Check")
print("=" * 60)
print("")

# Check Cursor settings
cursor_settings_paths = [
    Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json",
    Path.home() / ".cursor" / "settings.json",
    Path.home() / "Library" / "Application Support" / "Cursor" / "User" / "settings.json",
]

print("Checking Cursor IDE settings...")
for settings_path in cursor_settings_paths:
    if settings_path.exists():
        try:
            with open(settings_path, 'r') as f:
                settings = json.load(f)

            print(f"Found settings at: {settings_path}")
            print("")

            # Look for AI-related settings
            ai_settings = {}
            for key, value in settings.items():
                if any(term in key.lower() for term in ['model', 'provider', 'ai', 'anthropic', 'openai', 'claude', 'gpt']):
                    ai_settings[key] = value

            if ai_settings:
                print("AI-Related Settings:")
                for key, value in ai_settings.items():
                    print(f"  {key}: {value}")
            else:
                print("No AI-related settings found in this file")

            print("")
            break
        except Exception as e:
            print(f"Error reading {settings_path}: {e}")
            print("")

# Check environment variables
print("Checking environment variables...")
env_vars = [
    'CURSOR_MODEL',
    'ANTHROPIC_API_KEY',
    'OPENAI_API_KEY',
    'ACTIVE_MODEL',
    'AI_PROVIDER'
]

found_vars = {}
for var in env_vars:
    value = os.environ.get(var)
    if value:
        # Don't print full API keys, just indicate they exist
        if 'KEY' in var:
            found_vars[var] = "***SET***"
        else:
            found_vars[var] = value

if found_vars:
    print("Found environment variables:")
    for var, value in found_vars.items():
        print(f"  {var}: {value}")
else:
    print("No relevant environment variables found")
print("")

# Check for model tracking files
log_dir = project_root / "logs"
if log_dir.exists():
    print("Checking recent log files for model information...")
    log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)

    for log_file in log_files[:5]:  # Check last 5 log files
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if any(term in content.lower() for term in ['model', 'claude', 'gpt', 'anthropic', 'openai']):
                    print(f"  {log_file.name} - may contain model info")
        except:
            pass

print("")
print("=" * 60)
print("RECOMMENDATION")
print("=" * 60)
print("")
print("For this AutoHotkey debugging problem, I recommend:")
print("")
print("BEST: Claude Sonnet 4.5 or Opus (Anthropic)")
print("  - Excellent at systematic debugging")
print("  - Great at understanding complex system interactions")
print("  - Strong pattern recognition")
print("  - Good at analyzing logs and traces")
print("")
print("ALTERNATIVE: GPT-4 Turbo (OpenAI)")
print("  - Strong code analysis")
print("  - Good debugging capabilities")
print("  - Fast response times")
print("")
print("WHY:")
print("  - This problem requires understanding:")
print("    * System state changes (layout, focus)")
print("    * Timing dependencies")
print("    * Multiple interaction methods")
print("    * Log analysis and pattern matching")
print("  - Claude excels at these types of problems")
print("")
print("=" * 60)
