#!/usr/bin/env python3
"""
L.A.F.F. Broadcast Breakdown & Clarification

Break down and clarify the broadcast statistics to show exactly:
- What was sent where
- How many messages/posts
- Which channels/systems received what

Tags: #LAUGH #FACTORY #BROADCAST #BREAKDOWN #CLARIFICATION @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LAFFBroadcastBreakdown")


class LAFFBroadcastBreakdown:
    """
    L.A.F.F. Broadcast Breakdown & Clarification

    Provides detailed breakdown of what was broadcast where
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize breakdown analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.broadcast_dir = self.data_dir / "lumina_film_factory" / "broadcasts"

        logger.info("✅ L.A.F.F. Broadcast Breakdown initialized")

    def analyze_latest_broadcast(self) -> Dict[str, Any]:
        try:
            """Analyze the latest broadcast and provide detailed breakdown"""
            logger.info("="*80)
            logger.info("📊 L.A.F.F. BROADCAST BREAKDOWN & CLARIFICATION")
            logger.info("="*80)

            # Find latest broadcast file
            broadcast_files = list(self.broadcast_dir.glob("broadcast_*.json"))
            if not broadcast_files:
                return {"error": "No broadcast files found"}

            latest_broadcast = max(broadcast_files, key=lambda p: p.stat().st_mtime)

            with open(latest_broadcast, 'r', encoding='utf-8') as f:
                broadcast_data = json.load(f)

            breakdown = {
                "broadcast_file": latest_broadcast.name,
                "timestamp": broadcast_data.get("timestamp"),
                "detailed_breakdown": {}
            }

            # Breakdown by category
            broadcasts = broadcast_data.get("broadcasts", {})

            # 1. INTERNAL AI COMMUNITY BREAKDOWN
            internal = broadcasts.get("internal_ai_community", {})
            breakdown["detailed_breakdown"]["internal_ai_community"] = {
                "category": "Internal AI Community",
                "description": "Messages sent to internal AI systems and agents",
                "messages_sent": internal.get("messages_sent", 0),
                "channels": internal.get("channels", []),
                "details": {
                    "agent_sessions": {
                        "type": "Agent Session",
                        "description": "Created agent session file for coordination",
                        "location": "data/agent_chat_sessions/",
                        "format": "JSON session file"
                    },
                    "syphon_intelligence_feed": {
                        "type": "Intelligence Feed",
                        "description": "Added to SYPHON intelligence feed for distribution",
                        "location": "SYPHON unified system",
                        "format": "Intelligence feed entry"
                    },
                    "@asks_system": {
                        "type": "Ask Entry",
                        "description": "Created @ask entry in asks system",
                        "location": "data/asks/",
                        "format": "JSON ask file"
                    }
                }
            }

            # 2. SOCIAL MEDIA BREAKDOWN
            social = broadcasts.get("social_media", {})
            breakdown["detailed_breakdown"]["social_media"] = {
                "category": "Social Media",
                "description": "Posts created for social media platforms (ready to post)",
                "posts_created": social.get("posts_created", 0),
                "platforms": social.get("platforms", []),
                "details": {
                    "Twitter/X": {
                        "type": "Social Media Post",
                        "description": "Twitter/X post created (ready to post)",
                        "location": "data/lumina_film_factory/social_media_posts/",
                        "format": "JSON post file",
                        "status": "ready_to_post",
                        "note": "Requires manual posting or API integration"
                    },
                    "YouTube": {
                        "type": "Community Post",
                        "description": "YouTube community post created (ready to post)",
                        "location": "data/lumina_film_factory/social_media_posts/",
                        "format": "JSON post file",
                        "status": "ready_to_post",
                        "note": "Requires manual posting or API integration"
                    }
                }
            }

            # 3. SOURCE CHANNELS BREAKDOWN
            sources = broadcasts.get("source_channels", {})
            breakdown["detailed_breakdown"]["source_channels"] = {
                "category": "All @SOURCE Channels",
                "description": "Messages sent to source research and import systems",
                "messages_sent": sources.get("messages_sent", 0),
                "channels": sources.get("channels", []),
                "details": {
                    "daily_source_sweeps": {
                        "type": "Source Research",
                        "description": "Broadcast to daily source sweeps system",
                        "location": "Source Deep Research Missions system",
                        "format": "System integration"
                    },
                    "syphon_imports": {
                        "type": "SYPHON Import",
                        "description": "Created announcement import file",
                        "location": "data/syphon/imported_sources/",
                        "format": "JSON import file"
                    }
                }
            }

            # 4. NETWORK SYSTEMS BREAKDOWN
            network = broadcasts.get("network_systems", {})
            breakdown["detailed_breakdown"]["network_systems"] = {
                "category": "Network Systems",
                "description": "Messages sent to network-wide systems",
                "messages_sent": network.get("messages_sent", 0),
                "systems": network.get("systems", []),
                "details": {
                    "JARVIS": {
                        "type": "JARVIS System",
                        "description": "Announcement file created in JARVIS system",
                        "location": "data/jarvis/",
                        "format": "JSON announcement file"
                    },
                    "LUMINA": {
                        "type": "LUMINA System",
                        "description": "Announcement file created in LUMINA system",
                        "location": "data/lumina/",
                        "format": "JSON announcement file"
                    }
                }
            }

            # Calculate totals
            breakdown["summary"] = {
                "total_messages_sent": (
                    breakdown["detailed_breakdown"]["internal_ai_community"]["messages_sent"] +
                    breakdown["detailed_breakdown"]["source_channels"]["messages_sent"] +
                    breakdown["detailed_breakdown"]["network_systems"]["messages_sent"]
                ),
                "total_posts_created": breakdown["detailed_breakdown"]["social_media"]["posts_created"],
                "total_channels_covered": (
                    len(breakdown["detailed_breakdown"]["internal_ai_community"]["channels"]) +
                    len(breakdown["detailed_breakdown"]["social_media"]["platforms"]) +
                    len(breakdown["detailed_breakdown"]["source_channels"]["channels"]) +
                    len(breakdown["detailed_breakdown"]["network_systems"]["systems"])
                ),
                "total_systems_notified": len(breakdown["detailed_breakdown"]["network_systems"]["systems"]),
                "breakdown_by_type": {
                    "internal_channels": len(breakdown["detailed_breakdown"]["internal_ai_community"]["channels"]),
                    "social_platforms": len(breakdown["detailed_breakdown"]["social_media"]["platforms"]),
                    "source_channels": len(breakdown["detailed_breakdown"]["source_channels"]["channels"]),
                    "network_systems": len(breakdown["detailed_breakdown"]["network_systems"]["systems"])
                }
            }

            return breakdown


        except Exception as e:
            self.logger.error(f"Error in analyze_latest_broadcast: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("📊 L.A.F.F. BROADCAST BREAKDOWN & CLARIFICATION")
    print("="*80 + "\n")

    analyzer = LAFFBroadcastBreakdown()
    breakdown = analyzer.analyze_latest_broadcast()

    if "error" in breakdown:
        print(f"❌ {breakdown['error']}")
        exit(1)

    print(f"Broadcast File: {breakdown['broadcast_file']}")
    print(f"Timestamp: {breakdown['timestamp']}\n")

    summary = breakdown["summary"]
    print("="*80)
    print("📊 SUMMARY STATISTICS")
    print("="*80)
    print(f"Total Messages Sent: {summary['total_messages_sent']}")
    print(f"Total Posts Created: {summary['total_posts_created']}")
    print(f"Total Channels Covered: {summary['total_channels_covered']}")
    print(f"Total Systems Notified: {summary['total_systems_notified']}\n")

    print("="*80)
    print("📋 DETAILED BREAKDOWN")
    print("="*80 + "\n")

    for category_key, category_data in breakdown["detailed_breakdown"].items():
        category_name = category_data["category"]
        print(f"🎯 {category_name}")
        print(f"   Description: {category_data['description']}")

        if "messages_sent" in category_data:
            print(f"   Messages Sent: {category_data['messages_sent']}")
        if "posts_created" in category_data:
            print(f"   Posts Created: {category_data['posts_created']}")

        items = category_data.get("channels") or category_data.get("platforms") or category_data.get("systems", [])
        print(f"   Items: {len(items)}")

        print(f"\n   Details:")
        for item_key, item_details in category_data.get("details", {}).items():
            print(f"      • {item_key}:")
            print(f"        Type: {item_details['type']}")
            print(f"        Description: {item_details['description']}")
            print(f"        Location: {item_details['location']}")
            print(f"        Format: {item_details['format']}")
            if "status" in item_details:
                print(f"        Status: {item_details['status']}")
            if "note" in item_details:
                print(f"        Note: {item_details['note']}")

        print()

    print("="*80)
    print("📊 BREAKDOWN BY TYPE")
    print("="*80)
    for type_name, count in summary["breakdown_by_type"].items():
        print(f"   {type_name.replace('_', ' ').title()}: {count}")

    print("\n" + "="*80)
    print("✅ BREAKDOWN COMPLETE")
    print("="*80 + "\n")
