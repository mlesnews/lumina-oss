#!/usr/bin/env python3
"""
Ingest YouTube videos to R5 using enhanced SYPHON SocialExtractor
Enhancement of existing R5/SYPHON integration patterns
"""

import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from r5_living_context_matrix import R5LivingContextMatrix

    syphon = SYPHONSystem(SYPHONConfig(project_root=project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(project_root)

    videos = [
        ("https://youtube.com/shorts/yjKzsBzE2og?si=NrqrNHuLL-eAAyE-", "Why copying data to central locations kills agentic AI", "yjKzsBzE2og"),
        ("https://youtu.be/Udc19q1o6Mg?si=2fG0NfB8hKi7ktFx", None, "Udc19q1o6Mg"),
        ("https://youtu.be/uVZMc-i5EEs?si=e7RSJEzmevxUIkcN", None, "uVZMc-i5EEs"),
        ("https://www.youtube.com/live/YF6qfe90BcU?si=ssLiRu9yD084AAHV", "YouTube Live Stream", "YF6qfe90BcU"),
        ("https://youtu.be/MeEZpjGrpm0?si=QTqb21tdt7Ybobe2", "I Created the AI Assistant We All Dreamed Of (Iron Man Jarvis) - Ada Assistant", "MeEZpjGrpm0")
    ]

    for url, title, video_id in videos:
        print(f"\n📹 Processing: {url}")
        result = syphon.extract(DataSourceType.SOCIAL, url, {"title": title or "", "source_id": video_id, "url": url})

        if result.success and result.data:
            sd = result.data
            session_id = r5.ingest_session({
                "session_id": f"youtube_{video_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "session_type": "youtube_ingestion",
                "timestamp": datetime.now().isoformat(),
                "content": f"Title: {sd.metadata.get('title', title or 'Unknown')}\nURL: {url}\n\n{sd.content}",
                "metadata": {**sd.metadata, "actionable_items": sd.actionable_items, "tasks": sd.tasks, "intelligence": sd.intelligence}
            })
            print(f"  ✅ Ingested to R5: {session_id}")
        else:
            print(f"  ❌ Failed: {result.error}")

    print("\n✅ Complete!")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

