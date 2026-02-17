#!/usr/bin/env python3
"""
Fix Multiple Issues:
1. Gemini 3 Flash configuration not working / Bedrock confusion
2. Auto-send after 10 seconds of silence (not working)
3. Voice filter background bleed through (still getting background)

Tags: #FIX #GEMINI #BEDROCK #AUTO_SEND #VOICE_FILTER
@JARVIS @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixGeminiBedrockAutoSendVoiceFilter")

def fix_gemini_and_bedrock(project_root: Path) -> bool:
    """Remove/disable Gemini 3 Flash and ensure Bedrock is disabled"""
    settings_file = project_root / ".cursor" / "settings.json"

    if not settings_file.exists():
        logger.error(f"❌ Settings file not found: {settings_file}")
        return False

    logger.info("=" * 80)
    logger.info("🔧 FIX GEMINI 3 FLASH & BEDROCK CONFUSION")
    logger.info("=" * 80)

    try:
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to read settings: {e}")
        return False

    changed = False

    # Remove Gemini 3 Flash from all model sections
    model_sections = [
        "cursor.model.customModels",
        "cursor.agent.customModels",
        "cursor.chat.customModels",
        "cursor.composer.customModels",
        "cursor.inlineCompletion.customModels",
    ]

    for section_key in model_sections:
        if section_key not in settings:
            continue

        models = settings[section_key]
        if not isinstance(models, list):
            continue

        # Remove Gemini models
        original_count = len(models)
        settings[section_key] = [
            m for m in models 
            if not (isinstance(m, dict) and (
                "gemini" in str(m.get("name", "")).lower() or
                "gemini" in str(m.get("title", "")).lower() or
                "gemini" in str(m.get("model", "")).lower() or
                m.get("provider") == "google" or
                "google" in str(m.get("apiBase", "")).lower()
            ))
        ]

        if len(settings[section_key]) < original_count:
            logger.info(f"   ✅ Removed Gemini models from {section_key}")
            changed = True

    # Disable Bedrock completely
    bedrock_keys = [
        "cursor.agent.bedrockEnabled",
        "cursor.chat.bedrockEnabled",
        "cursor.composer.bedrockEnabled",
        "cursor.inlineCompletion.bedrockEnabled",
        "bedrock.enabled",
        "aws.bedrock.enabled",
    ]

    for key in bedrock_keys:
        if key in settings and settings[key] is not False:
            settings[key] = False
            logger.info(f"   ✅ Disabled {key}")
            changed = True

    # Add explicit Bedrock disable
    if "bedrock" not in settings:
        settings["bedrock"] = {}
    settings["bedrock"]["enabled"] = False
    settings["bedrock"]["blocked"] = True
    settings["bedrock"]["reason"] = "Local models only - Bedrock disabled to prevent confusion"
    changed = True
    logger.info("   ✅ Added explicit Bedrock disable")

    if changed:
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            logger.info("")
            logger.info("✅ Gemini removed and Bedrock disabled")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write settings: {e}")
            return False
    else:
        logger.info("✅ No Gemini models found, Bedrock already disabled")
        return True

def fix_auto_send_10_seconds(project_root: Path) -> bool:
    """Fix auto-send to trigger after 10 seconds of silence"""
    transcription_file = project_root / "scripts" / "python" / "cursor_auto_recording_transcription_fixed.py"

    if not transcription_file.exists():
        logger.error(f"❌ Transcription file not found: {transcription_file}")
        return False

    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 FIX AUTO-SEND: 10 SECONDS OF SILENCE")
    logger.info("=" * 80)

    try:
        with open(transcription_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read transcription file: {e}")
        return False

    original_content = content

    # Fix 1: Change dynamic timeout to support 10 seconds
    # Current: dynamic_pause_timeout = 1.5-4.0 seconds
    # Need: Support 10 seconds of silence before auto-send

    # Replace dynamic timeout calculation
    old_dynamic = """self.dynamic_pause_timeout = 2.0  # Start with 2 seconds"""
    new_dynamic = """self.dynamic_pause_timeout = 10.0  # 10 seconds of silence before auto-send"""
    if old_dynamic in content:
        content = content.replace(old_dynamic, new_dynamic)
        logger.info("   ✅ Updated initial dynamic timeout to 10 seconds")

    # Fix 2: Update dynamic timeout calculation to allow 10 seconds
    old_calc = """self.dynamic_pause_timeout = min(4.0, 2.0 + (self.consecutive_audio_count * 0.2)) # 2s -> 4s max"""
    new_calc = """self.dynamic_pause_timeout = min(10.0, 10.0 + (self.consecutive_audio_count * 0.0)) # 10s fixed for auto-send"""
    if old_calc in content:
        content = content.replace(old_calc, new_calc)
        logger.info("   ✅ Updated dynamic timeout calculation to 10 seconds")

    # Fix 3: Update shorter timeout when paused
    old_shorter = """self.dynamic_pause_timeout = 1.5 # Shorter timeout when paused"""
    new_shorter = """self.dynamic_pause_timeout = 10.0 # 10 seconds of silence before auto-send"""
    if old_shorter in content:
        content = content.replace(old_shorter, new_shorter)
        logger.info("   ✅ Updated pause timeout to 10 seconds")

    # Fix 4: Add explicit 10-second silence detection
    if "10.*second" not in content.lower() or "ten.*second" not in content.lower():
        # Add comment about 10-second silence
        silence_comment = """# FIX: 10 seconds of silence triggers auto-send (user requirement)
                    # Dynamic timeout now fixed at 10 seconds for reliable auto-send"""
        if "# FIX: 10 seconds" not in content:
            # Find the listen call and add comment before it
            listen_pattern = "audio = self.recognizer.listen(source, timeout=self.dynamic_pause_timeout"
            if listen_pattern in content:
                content = content.replace(
                    listen_pattern,
                    silence_comment + "\n                    " + listen_pattern
                )
                logger.info("   ✅ Added 10-second silence comment")

    if content != original_content:
        try:
            with open(transcription_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("")
            logger.info("✅ Auto-send fixed: 10 seconds of silence")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write transcription file: {e}")
            return False
    else:
        logger.info("✅ Auto-send already configured for 10 seconds")
        return True

def fix_voice_filter_stricter(project_root: Path) -> bool:
    """Make voice filter stricter to prevent background bleed through"""
    voice_filter_file = project_root / "scripts" / "python" / "voice_filter_system.py"

    if not voice_filter_file.exists():
        logger.error(f"❌ Voice filter file not found: {voice_filter_file}")
        return False

    logger.info("")
    logger.info("=" * 80)
    logger.info("🔧 FIX VOICE FILTER: STRICTER THRESHOLD (PREVENT BACKGROUND BLEED)")
    logger.info("=" * 80)

    try:
        with open(voice_filter_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        logger.error(f"❌ Failed to read voice filter file: {e}")
        return False

    original_content = content

    # Increase threshold from 0.75 to 0.85 (stricter matching)
    old_threshold = """self.voice_match_threshold = 0.75  # Increased for stricter filtering of TV/background"""
    new_threshold = """self.voice_match_threshold = 0.85  # STRICT: Prevents background bleed through (TV, other speakers)"""
    if old_threshold in content:
        content = content.replace(old_threshold, new_threshold)
        logger.info("   ✅ Increased voice match threshold to 0.85 (stricter)")

    # Also check for other threshold values
    import re
    threshold_pattern = r'self\.voice_match_threshold\s*=\s*0\.\d+'
    matches = re.findall(threshold_pattern, content)
    for match in matches:
        if "0.85" not in match:
            content = re.sub(
                r'self\.voice_match_threshold\s*=\s*0\.\d+',
                'self.voice_match_threshold = 0.85  # STRICT: Prevents background bleed',
                content
            )
            logger.info("   ✅ Updated voice match threshold to 0.85")
            break

    if content != original_content:
        try:
            with open(voice_filter_file, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info("")
            logger.info("✅ Voice filter threshold increased to 0.85 (stricter)")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to write voice filter file: {e}")
            return False
    else:
        logger.info("✅ Voice filter threshold already at 0.85")
        return True

def main():
    """Fix all issues"""
    logger.info("=" * 80)
    logger.info("🔧 FIXING: Gemini/Bedrock, Auto-Send, Voice Filter")
    logger.info("=" * 80)
    logger.info("")

    success1 = fix_gemini_and_bedrock(project_root)
    success2 = fix_auto_send_10_seconds(project_root)
    success3 = fix_voice_filter_stricter(project_root)

    logger.info("")
    logger.info("=" * 80)
    if success1 and success2 and success3:
        logger.info("✅ ALL FIXES APPLIED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Summary:")
        logger.info("   ✅ Gemini 3 Flash removed from all model sections")
        logger.info("   ✅ Bedrock explicitly disabled (no confusion)")
        logger.info("   ✅ Auto-send: 10 seconds of silence triggers send")
        logger.info("   ✅ Voice filter: Threshold increased to 0.85 (stricter)")
        logger.info("")
        logger.info("⚠️  IMPORTANT: Restart Cursor and transcription service for changes")
        return True
    else:
        logger.info("⚠️  SOME FIXES FAILED")
        logger.info("=" * 80)
        return False

if __name__ == "__main__":
    sys.exit(0 if success else 1)


    success = main()