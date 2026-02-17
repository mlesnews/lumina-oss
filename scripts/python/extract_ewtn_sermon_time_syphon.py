#!/usr/bin/env python3
"""
Extract EWTN Sermon on TIME using SYPHON
Processes recent televised EWTN sermon on TIME topic from Comcast/Xfinity/YouTubeTV

@SYPHON @EWTN @YOUTUBE @SOURCES
"""

import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from r5_living_context_matrix import R5LivingContextMatrix
    from master_todo_tracker import MasterTodoTracker, TaskStatus

    SYPHON_AVAILABLE = True
except ImportError as e:
    try:
        # Try alternative import paths
        from scripts.python.syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
        from scripts.python.syphon.models import DataSourceType
        from scripts.python.r5_living_context_matrix import R5LivingContextMatrix
        from scripts.python.master_todo_tracker import MasterTodoTracker, TaskStatus
        SYPHON_AVAILABLE = True
    except ImportError as e2:
        print(f"⚠️  Import error: {e2}")
        SYPHON_AVAILABLE = False


def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from URL"""
    patterns = [
        r'(?:youtube\.com\/(?:watch\?v=|shorts\/|live\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def process_youtube_url(url: str, syphon: SYPHONSystem, r5: R5LivingContextMatrix, 
                        todo_tracker: Optional[MasterTodoTracker] = None) -> Dict[str, Any]:
    """Process a YouTube URL through SYPHON and ingest to R5"""
    print(f"\n{'='*80}")
    print(f"📹 Processing EWTN Sermon: {url}")
    print(f"{'='*80}\n")

    video_id = extract_video_id(url)
    if not video_id:
        print(f"❌ Could not extract video ID from URL: {url}")
        return {"success": False, "error": "Invalid YouTube URL"}

    # Extract with SYPHON
    print("🔍 SYPHON: Extracting intelligence...")
    metadata = {
        "title": "EWTN Sermon on TIME",
        "source": "EWTN",
        "topic": "TIME",
        "source_id": video_id,
        "url": url,
        "provider": "Comcast/Xfinity/YouTubeTV",
        "extraction_date": datetime.now().isoformat()
    }

    result = syphon.extract(DataSourceType.SOCIAL, url, metadata)

    if not result.success:
        print(f"❌ SYPHON extraction failed: {result.error}")
        return {"success": False, "error": result.error}

    if not result.data:
        print(f"❌ SYPHON returned no data")
        return {"success": False, "error": "No data extracted"}

    syphon_data = result.data
    print(f"✅ SYPHON extraction complete!")
    print(f"   - Actionable Items: {len(syphon_data.actionable_items)}")
    print(f"   - Tasks: {len(syphon_data.tasks)}")
    print(f"   - Decisions: {len(syphon_data.decisions)}")
    print(f"   - Intelligence Points: {len(syphon_data.intelligence)}")

    # Ingest to R5
    print("\n📊 Ingesting to R5 Living Context Matrix...")
    session_id = r5.ingest_session({
        "session_id": f"ewtn_sermon_time_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_type": "ewtn_sermon_extraction",
        "timestamp": datetime.now().isoformat(),
        "content": f"EWTN Sermon on TIME\n\nURL: {url}\nVideo ID: {video_id}\n\n{syphon_data.content}",
        "metadata": {
            **syphon_data.metadata,
            "actionable_items": syphon_data.actionable_items,
            "tasks": syphon_data.tasks,
            "decisions": syphon_data.decisions,
            "intelligence": syphon_data.intelligence,
            "source": "EWTN",
            "topic": "TIME",
            "provider": "Comcast/Xfinity/YouTubeTV"
        }
    })
    print(f"✅ Ingested to R5: {session_id}")

    # Update TODO status
    if todo_tracker:
        print("\n📋 Updating TODO status...")
        todos = todo_tracker.get_todos()
        for todo in todos:
            if "EWTN" in todo.title and "TIME" in todo.title:
                todo_tracker.update_status(todo.id, TaskStatus.IN_PROGRESS)
                print(f"✅ Updated TODO: {todo.title} -> IN_PROGRESS")
                break

    # Print summary
    print(f"\n{'='*80}")
    print("📊 EXTRACTION SUMMARY")
    print(f"{'='*80}")
    print(f"Video ID: {video_id}")
    print(f"URL: {url}")
    print(f"R5 Session: {session_id}")
    print(f"Actionable Items: {len(syphon_data.actionable_items)}")
    print(f"Tasks Extracted: {len(syphon_data.tasks)}")
    print(f"Decisions: {len(syphon_data.decisions)}")
    print(f"Intelligence Points: {len(syphon_data.intelligence)}")

    if syphon_data.actionable_items:
        print(f"\n💡 Key Actionable Items:")
        for i, item in enumerate(syphon_data.actionable_items[:5], 1):
            print(f"   {i}. {item}")

    if syphon_data.intelligence:
        print(f"\n🧠 Key Intelligence:")
        for i, intel in enumerate(syphon_data.intelligence[:5], 1):
            print(f"   {i}. {intel}")

    return {
        "success": True,
        "video_id": video_id,
        "session_id": session_id,
        "actionable_items": len(syphon_data.actionable_items),
        "tasks": len(syphon_data.tasks),
        "decisions": len(syphon_data.decisions),
        "intelligence": len(syphon_data.intelligence)
    }


def main():
    """Main execution"""
    if not SYPHON_AVAILABLE:
        print("❌ SYPHON system not available")
        return 1

    print("🔍 EWTN Sermon on TIME - SYPHON Extraction")
    print("=" * 80)

    # Initialize systems
    print("\n🔧 Initializing systems...")
    syphon = SYPHONSystem(SYPHONConfig(project_root=project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(project_root)
    todo_tracker = MasterTodoTracker(project_root=project_root)
    print("✅ Systems initialized")

    # Check for URL argument or prompt
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("\n📝 Please provide a YouTube URL for the EWTN sermon on TIME")
        print("   Usage: python extract_ewtn_sermon_time_syphon.py <youtube_url>")
        print("\n   Or search for EWTN sermons on TIME:")
        print("   - EWTN YouTube Channel: https://www.youtube.com/@EWTN")
        print("   - Search: 'EWTN sermon time' on YouTube")
        print("\n   Example URLs:")
        print("   - https://www.youtube.com/watch?v=VIDEO_ID")
        print("   - https://youtu.be/VIDEO_ID")
        print("   - https://www.youtube.com/live/VIDEO_ID")

        # Try to find recent EWTN content (placeholder - would need YouTube API)
        print("\n⚠️  Note: To automatically find the sermon, YouTube Data API v3 integration is needed")
        print("   For now, please provide the URL directly")
        return 1

    # Process the URL
    result = process_youtube_url(url, syphon, r5, todo_tracker)

    if result.get("success"):
        print(f"\n✅ Extraction complete!")
        return 0
    else:
        print(f"\n❌ Extraction failed: {result.get('error', 'Unknown error')}")
        return 1


if __name__ == "__main__":


    sys.exit(main())