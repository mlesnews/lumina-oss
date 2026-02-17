#!/usr/bin/env python3
"""
Extract Intelligence from Ada (JARVIS-like AI Assistant) Video
Processes insights and actionable items for Lumina JARVIS enhancement
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

    # Ada/JARVIS Video Content
    ada_content = """
Title: I Created the AI Assistant We All Dreamed Of (Iron Man Jarvis) - Ada Assistant
URL: https://youtu.be/MeEZpjGrpm0?si=QTqb21tdt7Ybobe2

KEY INSIGHTS:

1. GEMINI 2.5 NATIVE AUDIO MODEL
- Simultaneous hear, think, and speak (no latency)
- Enables interruptions during conversations
- Multimodal capabilities (process various input types)
- Identifies objects held by users
- Single model for efficiency

2. SMART HOME CONTROL
- Control physical devices (smart bulbs, etc.)
- Kasa smart bulbs integration via Python
- Hand tracking and gesture control
- Physical world control capabilities

3. WEB BROWSING AGENT
- Gemini Computer Use model for web interaction
- Navigate and interact with webpages
- Add items to cart, browse, search
- True multitasking capabilities

4. ADVANCED CAPABILITIES
- Project management features
- Long-term memory system
- CAD design capabilities (planned)
- Robot arm integration planning
- Mechanical design, electronics, programming integration

5. INTERACTION IMPROVEMENTS
- Interruption support (can interject during conversations)
- Gesture-based control
- Visual object identification
- Simultaneous task execution

TECHNICAL APPROACH:
- Uses Gemini 2.5 Native Audio for natural conversation
- Python-based smart home integration
- Web agent for browser automation
- Project management for complex tasks
- Long-term memory for context retention

COMPARISON TO JARVIS:
- Similar to Iron Man's JARVIS in functionality
- Voice interaction with interruptions
- Physical world control
- Web browsing and task automation
- Project planning and management
- Future CAD design capabilities
"""

    print("🔍 Extracting intelligence from Ada/JARVIS video...")

    # Extract intelligence
    result = syphon.extract(
        DataSourceType.SOCIAL,
        ada_content,
        {
            "title": "I Created the AI Assistant We All Dreamed Of (Iron Man Jarvis)",
            "source_id": "MeEZpjGrpm0",
            "url": "https://youtu.be/MeEZpjGrpm0?si=QTqb21tdt7Ybobe2",
            "source_type": "youtube",
            "focus": "jarvis_enhancement",
            "relevance": "high"
        }
    )

    if result.success and result.data:
        sd = result.data

        # Enhanced ingestion with actionable intelligence
        session_data = {
            "session_id": f"ada_jarvis_intelligence_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "session_type": "jarvis_enhancement_intelligence",
            "timestamp": datetime.now().isoformat(),
            "content": ada_content,
            "metadata": {
                **sd.metadata,
                "actionable_items": sd.actionable_items,
                "tasks": sd.tasks,
                "intelligence": sd.intelligence,
                "decisions": sd.decisions,
                "video_url": "https://youtu.be/MeEZpjGrpm0?si=QTqb21tdt7Ybobe2",
                "video_id": "MeEZpjGrpm0",
                "focus_areas": [
                    "gemini_2.5_integration",
                    "smart_home_control",
                    "web_browsing_agent",
                    "multimodal_interaction",
                    "interruption_support",
                    "gesture_control",
                    "project_management",
                    "long_term_memory",
                    "cad_design_integration"
                ]
            }
        }

        session_id = r5.ingest_session(session_data)
        print(f"✅ Intelligence extracted and ingested to R5: {session_id}")
        print(f"\n📊 Extracted:")
        print(f"   - Actionable Items: {len(sd.actionable_items)}")
        print(f"   - Tasks: {len(sd.tasks)}")
        print(f"   - Intelligence Points: {len(sd.intelligence)}")
        print(f"   - Decisions: {len(sd.decisions)}")
    else:
        print(f"❌ Extraction failed: {result.error}")

    print("\n✅ Complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

