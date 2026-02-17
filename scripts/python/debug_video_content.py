#!/usr/bin/env python3
"""
Debug Video Content - Check what video data we actually have
"""

import json
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("debug_video_content")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def check_video_content():
    try:
        """Check SYPHON data for video content"""
        syphon_file = Path('data/syphon/extracted_data.json')

        if not syphon_file.exists():
            print("❌ SYPHON file not found")
            return

        with open(syphon_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"📊 Total SYPHON entries: {len(data)}")

        video_entries = []
        for entry in data:
            content = entry.get('content', '').lower()
            data_id = entry.get('data_id', '')

            # Check for video-related keywords
            video_keywords = ['elon', 'musk', 'video', 'argument', 'psychosis', 'llm', 'macrohard', 'navier-stokes', 'post-scarcity', 'abundance']
            is_video = any(keyword in content for keyword in video_keywords)

            if is_video:
                video_entries.append(entry)

        print(f"🎥 Video-related entries found: {len(video_entries)}")

        for i, entry in enumerate(video_entries, 1):
            data_id = entry.get('data_id', 'unknown')
            content = entry.get('content', '')
            metadata = entry.get('metadata', {})

            print(f"\n{i}. 📹 {data_id}")
            print(f"   Content length: {len(content)} characters")
            print(f"   Content preview: {content[:500]}{'...' if len(content) > 500 else ''}")

            # Check for extracted intelligence
            actionable = metadata.get('actionable_items', [])
            tasks = metadata.get('tasks', [])
            intelligence = metadata.get('intelligence', [])

            print(f"   💡 Actionable items: {len(actionable)}")
            print(f"   📋 Tasks: {len(tasks)}")
            print(f"   🧠 Intelligence points: {len(intelligence)}")

            if actionable:
                print("   Actionable items:")
                for item in actionable[:3]:  # Show first 3
                    print(f"     • {item.get('description', 'Unknown')[:100]}...")

            if intelligence:
                print("   Intelligence:")
                for intel in intelligence[:3]:  # Show first 3
                    print(f"     • {intel.get('insight', 'Unknown')[:100]}...")

    except Exception as e:
        logger.error(f"Error in check_video_content: {e}", exc_info=True)
        raise
def check_r5_for_videos():
    try:
        """Check R5 matrix for video content"""
        r5_file = Path('data/r5_living_matrix/LIVING_CONTEXT_MATRIX_PROMPT.md')

        if not r5_file.exists():
            print("❌ R5 matrix file not found")
            return

        with open(r5_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for video-related content
        video_lines = []
        for line in content.split('\n'):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in ['elon', 'musk', 'video', 'psychosis', 'llm', 'macrohard', 'post-scarcity']):
                video_lines.append(line.strip())

        print(f"\n🧠 R5 Matrix video references: {len(video_lines)}")
        for line in video_lines[:5]:  # Show first 5
            print(f"   • {line}")

    except Exception as e:
        logger.error(f"Error in check_r5_for_videos: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    print("🔍 DEBUGGING VIDEO CONTENT INGESTION")
    print("=" * 50)

    check_video_content()
    check_r5_for_videos()

    print("\n" + "=" * 50)
    print("🎯 DEBUG COMPLETE")
