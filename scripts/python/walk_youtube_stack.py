#!/usr/bin/env python3
"""
Walk Down YouTube Stack - Extract Insights for LUMINA

This script processes syphoned YouTube watch history and extracts deep insights
for LUMINA intelligence, patterns, and knowledge integration.

"Walk down the stack" means systematically analyzing each video in chronological
order to identify patterns, themes, and actionable insights.
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("WalkYouTubeStack")

# Add scripts/python to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


class YouTubeStackWalker:
    """
    Walk down the stack of watched videos and extract insights for LUMINA
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.syphon_dir = self.project_root / "data" / "syphon" / "youtube_history"
        self.output_dir = self.project_root / "data" / "intelligence" / "youtube_insights"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.videos = []
        self.insights = []
        self.patterns = defaultdict(list)
        self.themes = Counter()

    def load_latest_syphon_data(self) -> Optional[Dict[str, Any]]:
        """Load the most recent syphon data"""
        if not self.syphon_dir.exists():
            logger.error(f"Syphon directory not found: {self.syphon_dir}")
            return None

        # Find latest watch history JSON file
        history_files = list(self.syphon_dir.glob("watch_history_*.json"))
        if not history_files:
            logger.error("No watch history files found. Please run syphon_youtube_watch_history_30_days.py first.")
            return None

        latest_file = max(history_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"📂 Loading latest syphon data: {latest_file.name}")

        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if isinstance(data, list):
                self.videos = data
            elif isinstance(data, dict) and "videos" in data:
                self.videos = data["videos"]
            else:
                self.videos = []

            logger.info(f"   ✅ Loaded {len(self.videos)} videos")
            return {"videos": self.videos, "source_file": str(latest_file)}

        except Exception as e:
            logger.error(f"Error loading syphon data: {e}")
            return None

    def extract_themes(self) -> Dict[str, Any]:
        """Extract themes and topics from video titles and channels"""
        logger.info("🎨 Extracting themes and topics...")

        # LUMINA-relevant themes
        lumina_themes = {
            "ai_progress": ["gpt", "claude", "anthropic", "openai", "agi", "superintelligence", 
                           "ai breakthrough", "llm", "neural", "deepmind", "ai revolution"],
            "ai_communication": ["ai communication", "prompt engineering", "ai interaction", 
                                "human ai", "ai conversation", "chatgpt", "claude"],
            "ai_experts": ["wes roth", "dylan curious", "andrej karpathy", "geoffrey hinton", 
                          "sam altman", "demis hassabis"],
            "technology_trends": ["nvidia", "gpu", "silicon", "hardware", "quantum", "robotics"],
            "coding_ai": ["coding", "programming", "software", "development", "code generation"],
            "philosophy_ai": ["ai consciousness", "ai ethics", "ai safety", "alignment", 
                             "ai risk", "existential risk"],
            "productivity": ["productivity", "automation", "workflow", "efficiency", "tools"],
            "lumina_concepts": ["autonomous", "agent", "orchestration", "ai agent", "multi-agent"]
        }

        theme_matches = defaultdict(list)

        for video in self.videos:
            title_lower = video.get("title", "").lower()
            channel_lower = video.get("channel", "").lower()
            text = f"{title_lower} {channel_lower}"

            for theme, keywords in lumina_themes.items():
                if any(keyword in text for keyword in keywords):
                    theme_matches[theme].append({
                        "title": video.get("title"),
                        "channel": video.get("channel"),
                        "url": video.get("url"),
                        "video_id": video.get("video_id")
                    })
                    self.themes[theme] += 1

        logger.info(f"   ✅ Identified {len(theme_matches)} themes")
        return dict(theme_matches)

    def extract_temporal_patterns(self) -> Dict[str, Any]:
        """Extract temporal patterns (watch times, batching, etc.)"""
        logger.info("⏰ Extracting temporal patterns...")

        patterns = {
            "watch_times": [],
            "daily_watch_counts": defaultdict(int),
            "channel_batching": defaultdict(list),
            "topic_clusters": []
        }

        for video in self.videos:
            watch_time = video.get("watch_time", "")
            channel = video.get("channel", "Unknown")

            # Parse watch time if available
            try:
                if watch_time:
                    watch_dt = datetime.fromisoformat(watch_time.replace("Z", "+00:00"))
                    patterns["watch_times"].append(watch_dt)
                    day_key = watch_dt.strftime("%Y-%m-%d")
                    patterns["daily_watch_counts"][day_key] += 1
            except:
                pass

            patterns["channel_batching"][channel].append(video)

        # Identify channel batching (multiple videos from same channel in sequence)
        batched_channels = {}
        for channel, videos in patterns["channel_batching"].items():
            if len(videos) >= 3:
                batched_channels[channel] = len(videos)

        patterns["batched_channels"] = dict(batched_channels)
        patterns["total_days"] = len(patterns["daily_watch_counts"])

        logger.info(f"   ✅ Extracted temporal patterns across {patterns['total_days']} days")
        return patterns

    def extract_lumina_insights(self, themes: Dict[str, Any], patterns: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract specific insights relevant to LUMINA"""
        logger.info("💡 Extracting LUMINA insights...")

        insights = []

        # AI Progress Insights
        ai_progress_videos = themes.get("ai_progress", [])
        if ai_progress_videos:
            insights.append({
                "category": "ai_progress_tracking",
                "title": f"Tracking AI Progress: {len(ai_progress_videos)} videos",
                "description": f"User is actively tracking AI progress through {len(ai_progress_videos)} videos",
                "key_videos": ai_progress_videos[:5],
                "relevance": "high",
                "action": "Monitor for new AI breakthroughs that could impact LUMINA development"
            })

        # Expert Following Insights
        expert_videos = themes.get("ai_experts", [])
        if expert_videos:
            insights.append({
                "category": "expert_knowledge_absorption",
                "title": f"Following AI Experts: {len(expert_videos)} videos",
                "description": f"User follows key AI experts (Wes Roth, Dylan Curious, etc.)",
                "key_videos": expert_videos[:5],
                "relevance": "high",
                "action": "Extract expert insights and integrate into LUMINA knowledge base"
            })

        # Communication Patterns
        comm_videos = themes.get("ai_communication", [])
        if comm_videos:
            insights.append({
                "category": "communication_interest",
                "title": f"AI Communication Focus: {len(comm_videos)} videos",
                "description": "User shows strong interest in AI communication and interaction",
                "key_videos": comm_videos[:5],
                "relevance": "critical",
                "action": "Directly relevant to LUMINA's core mission - extract communication insights"
            })

        # Batching Patterns
        batched = patterns.get("batched_channels", {})
        if batched:
            top_batched = sorted(batched.items(), key=lambda x: x[1], reverse=True)[:3]
            insights.append({
                "category": "deep_dive_pattern",
                "title": f"Deep Dive Pattern: {len(batched)} channels batched",
                "description": f"User watches multiple videos from: {', '.join([c for c, _ in top_batched])}",
                "details": dict(top_batched),
                "relevance": "medium",
                "action": "These channels represent deep interest areas - prioritize for content extraction"
            })

        # Topic Clusters
        if len(self.themes) > 0:
            top_themes = self.themes.most_common(5)
            insights.append({
                "category": "interest_priorities",
                "title": "Top Interest Themes",
                "description": "Primary themes in user's watch history",
                "themes": dict(top_themes),
                "relevance": "high",
                "action": "Align LUMINA development priorities with user interests"
            })

        logger.info(f"   ✅ Generated {len(insights)} insights")
        return insights

    def generate_recommendations(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Generate actionable recommendations for LUMINA"""
        recommendations = []

        # High-priority recommendations
        high_priority_insights = [i for i in insights if i.get("relevance") == "critical" or i.get("relevance") == "high"]

        if high_priority_insights:
            recommendations.append("🔴 HIGH PRIORITY: Extract insights from high-relevance videos")
            for insight in high_priority_insights[:3]:
                action = insight.get("action", "")
                if action:
                    recommendations.append(f"   • {action}")

        # Communication-specific
        comm_insights = [i for i in insights if "communication" in i.get("category", "")]
        if comm_insights:
            recommendations.append("💬 COMMUNICATION FOCUS: Deep dive into AI communication videos")
            recommendations.append("   • Extract prompt engineering techniques")
            recommendations.append("   • Identify interaction patterns")
            recommendations.append("   • Integrate communication insights into LUMINA")

        # Expert content
        expert_insights = [i for i in insights if "expert" in i.get("category", "")]
        if expert_insights:
            recommendations.append("🎓 EXPERT CONTENT: Process expert videos for knowledge extraction")
            recommendations.append("   • Create summaries of key expert insights")
            recommendations.append("   • Identify actionable techniques")
            recommendations.append("   • Feed into LUMINA knowledge base")

        return recommendations

    def save_insights(self, themes: Dict[str, Any], patterns: Dict[str, Any],
                         insights: List[Dict[str, Any]], recommendations: List[str]):
        """Save extracted insights to files"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save comprehensive insights
            insights_data = {
                "timestamp": datetime.now().isoformat(),
                "source": "youtube_watch_history_stack_walk",
                "total_videos_analyzed": len(self.videos),
                "themes": themes,
                "patterns": {
                    "temporal": patterns,
                    "theme_counts": dict(self.themes)
                },
                "insights": insights,
                "recommendations": recommendations,
                "summary": {
                    "total_themes": len(themes),
                    "total_insights": len(insights),
                    "total_recommendations": len(recommendations),
                    "high_priority_count": len([i for i in insights if i.get("relevance") in ["critical", "high"]])
                }
            }

            insights_file = self.output_dir / f"youtube_stack_insights_{timestamp}.json"
            with open(insights_file, 'w', encoding='utf-8') as f:
                json.dump(insights_data, f, indent=2)
            logger.info(f"   💾 Insights saved: {insights_file.name}")

            # Save markdown report
            report_file = self.output_dir / f"youtube_stack_report_{timestamp}.md"
            self._generate_markdown_report(report_file, insights_data)
            logger.info(f"   📄 Report saved: {report_file.name}")

            return insights_file, report_file

        except Exception as e:
            self.logger.error(f"Error in save_insights: {e}", exc_info=True)
            raise
    def _generate_markdown_report(self, report_file: Path, insights_data: Dict[str, Any]):
        try:
            """Generate human-readable markdown report"""
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("# YouTube Stack Walk - LUMINA Insights Report\n\n")
                f.write(f"**Generated**: {insights_data['timestamp']}\n\n")
                f.write(f"**Videos Analyzed**: {insights_data['total_videos_analyzed']}\n\n")

                f.write("## Summary\n\n")
                summary = insights_data['summary']
                f.write(f"- **Themes Identified**: {summary['total_themes']}\n")
                f.write(f"- **Insights Generated**: {summary['total_insights']}\n")
                f.write(f"- **High Priority Insights**: {summary['high_priority_count']}\n")
                f.write(f"- **Recommendations**: {summary['total_recommendations']}\n\n")

                f.write("## Top Themes\n\n")
                theme_counts = insights_data['patterns']['theme_counts']
                for theme, count in sorted(theme_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
                    f.write(f"- **{theme.replace('_', ' ').title()}**: {count} videos\n")
                f.write("\n")

                f.write("## Key Insights\n\n")
                for insight in insights_data['insights']:
                    f.write(f"### {insight.get('title', 'Untitled')}\n\n")
                    f.write(f"**Category**: {insight.get('category', 'Unknown')}\n\n")
                    f.write(f"**Relevance**: {insight.get('relevance', 'Unknown')}\n\n")
                    f.write(f"{insight.get('description', '')}\n\n")
                    f.write(f"**Action**: {insight.get('action', '')}\n\n")

                    if 'key_videos' in insight:
                        f.write("**Key Videos**:\n")
                        for video in insight['key_videos'][:3]:
                            f.write(f"- [{video.get('title', 'Unknown')}]({video.get('url', '#')})\n")
                        f.write("\n")

                f.write("## Recommendations\n\n")
                for rec in insights_data['recommendations']:
                    f.write(f"{rec}\n\n")

        except Exception as e:
            self.logger.error(f"Error in _generate_markdown_report: {e}", exc_info=True)
            raise
    def print_summary(self, themes: Dict[str, Any], insights: List[Dict[str, Any]], 
                     recommendations: List[str]):
        """Print summary to console"""
        print()
        print("="*70)
        print("📚 YOUTUBE STACK WALK - LUMINA INSIGHTS")
        print("="*70)
        print()
        print(f"📹 Videos Analyzed: {len(self.videos)}")
        print(f"🎨 Themes Identified: {len(themes)}")
        print(f"💡 Insights Generated: {len(insights)}")
        print(f"⭐ High Priority Insights: {len([i for i in insights if i.get('relevance') in ['critical', 'high']])}")
        print()

        print("🏆 TOP THEMES:")
        print("-"*50)
        for theme, count in self.themes.most_common(10):
            bar = "█" * min(count, 30)
            print(f"   {count:3d} {bar} {theme.replace('_', ' ').title()}")
        print()

        print("💡 KEY INSIGHTS:")
        print("-"*50)
        for insight in insights[:5]:
            relevance_icon = "🔴" if insight.get("relevance") == "critical" else "🟡" if insight.get("relevance") == "high" else "🟢"
            print(f"   {relevance_icon} {insight.get('title', 'Untitled')}")
            print(f"      {insight.get('description', '')[:60]}...")
        print()

        if recommendations:
            print("🎯 RECOMMENDATIONS:")
            print("-"*50)
            for rec in recommendations[:10]:
                print(f"   {rec}")
        print()

    def walk_stack(self) -> Optional[Dict[str, Any]]:
        """Walk down the stack and extract all insights"""
        print("="*70)
        print("🚶 WALKING DOWN YOUTUBE STACK")
        print("="*70)
        print()

        # Load data
        data = self.load_latest_syphon_data()
        if not data:
            return None

        # Extract themes
        themes = self.extract_themes()

        # Extract patterns
        patterns = self.extract_temporal_patterns()

        # Extract insights
        insights = self.extract_lumina_insights(themes, patterns)

        # Generate recommendations
        recommendations = self.generate_recommendations(insights)

        # Save results
        insights_file, report_file = self.save_insights(themes, patterns, insights, recommendations)

        # Print summary
        self.print_summary(themes, insights, recommendations)

        print(f"✅ Stack walk complete!")
        print(f"   📊 Insights: {insights_file.name}")
        print(f"   📄 Report: {report_file.name}")
        print()

        return {
            "themes": themes,
            "patterns": patterns,
            "insights": insights,
            "recommendations": recommendations,
            "files": {
                "insights": str(insights_file),
                "report": str(report_file)
            }
        }


def main():
    """CLI interface"""
    walker = YouTubeStackWalker()
    result = walker.walk_stack()

    if result:
        return 0
    else:
        return 1


if __name__ == "__main__":



    sys.exit(main())