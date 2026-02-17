#!/usr/bin/env python3
"""
LUMINA AI Intelligence Mapper

Processes YouTube AI intelligence and feeds it into LUMINA system
for visualization in Romewise AI frontend.

Maps out:
- AI trends and direction
- Global AI landscape
- Intelligence clusters
- Trend analysis
- Visual representation

Tags: #LUMINA #AI #INTELLIGENCE #VISUALIZATION #ROMEWISE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAAIIntelligenceMapper")


class LUMINAAIIntelligenceMapper:
    """Map AI intelligence into LUMINA system for visualization"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize mapper"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.ai_intel_dir = self.project_root / "data" / "youtube_ai_doit_intelligence"
        self.lumina_data_dir = self.project_root / "data" / "lumina_ai_intelligence"
        self.lumina_data_dir.mkdir(parents=True, exist_ok=True)

        # Visualization directory
        self.viz_dir = self.project_root / "data" / "va_desktop_viz"
        self.viz_dir.mkdir(parents=True, exist_ok=True)

        # AI trend categories
        self.ai_categories = {
            "language_models": ["GPT", "LLM", "language model", "transformer", "BERT", "T5"],
            "automation": ["automation", "autonomous", "agent", "assistant", "chatbot", "RPA"],
            "computer_vision": ["computer vision", "image recognition", "CV", "object detection"],
            "machine_learning": ["machine learning", "ML", "deep learning", "neural network", "CNN", "RNN"],
            "data_science": ["data science", "data analysis", "big data", "analytics"],
            "ai_ethics": ["AI ethics", "bias", "fairness", "transparency", "responsible AI"],
            "ai_applications": ["AI application", "use case", "implementation", "deployment"],
            "research": ["research", "paper", "study", "academic", "publication"]
        }

        logger.info("✅ LUMINA AI Intelligence Mapper initialized")

    def load_ai_intelligence(self) -> List[Dict[str, Any]]:
        """Load all AI intelligence from scans"""
        all_intelligence = []

        # Load from latest scan
        scan_files = sorted(self.ai_intel_dir.glob("ai_doit_scan_*.json"), reverse=True)

        for scan_file in scan_files[:5]:  # Last 5 scans
            try:
                with open(scan_file, 'r', encoding='utf-8') as f:
                    scan_data = json.load(f)
                    intelligence = scan_data.get("intelligence", {})

                    # Add AI intelligence
                    ai_intel = intelligence.get("ai_intelligence", [])
                    combined_intel = intelligence.get("combined_intelligence", [])

                    for item in ai_intel + combined_intel:
                        if item.get("ai_related"):
                            item["scan_file"] = scan_file.name
                            item["scan_date"] = scan_data.get("scan_metadata", {}).get("started", "")
                            all_intelligence.append(item)
            except Exception as e:
                logger.debug(f"Error loading scan file {scan_file}: {e}")
                continue

        logger.info(f"   Loaded {len(all_intelligence)} AI intelligence items")
        return all_intelligence

    def categorize_intelligence(self, intelligence_list: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize intelligence by AI topic"""
        categorized = defaultdict(list)

        for item in intelligence_list:
            title = item.get("title", "").lower()
            content = item.get("content", "").lower()
            summary = item.get("summary", "").lower()

            combined_text = f"{title} {summary} {content}"

            # Categorize
            categories_found = []
            for category, keywords in self.ai_categories.items():
                if any(keyword.lower() in combined_text for keyword in keywords):
                    categories_found.append(category)
                    categorized[category].append(item)

            # If no category found, add to general
            if not categories_found:
                categorized["general"].append(item)
            else:
                item["categories"] = categories_found

        return dict(categorized)

    def extract_trends(self, intelligence_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract trends and patterns from intelligence"""
        trends = {
            "top_topics": Counter(),
            "top_channels": Counter(),
            "temporal_distribution": defaultdict(int),
            "keyword_frequency": Counter(),
            "trend_direction": {}
        }

        # Extract keywords
        ai_keywords = [
            "GPT", "LLM", "AI", "machine learning", "deep learning",
            "automation", "neural network", "transformer", "language model",
            "computer vision", "NLP", "prompt engineering", "fine-tuning"
        ]

        for item in intelligence_list:
            # Top channels
            channel = item.get("channel", "Unknown")
            trends["top_channels"][channel] += 1

            # Temporal distribution
            timestamp = item.get("timestamp", "")
            if timestamp:
                try:
                    date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    date_key = date.strftime("%Y-%m-%d")
                    trends["temporal_distribution"][date_key] += 1
                except:
                    pass

            # Keyword frequency
            text = f"{item.get('title', '')} {item.get('summary', '')} {item.get('content', '')}".lower()
            for keyword in ai_keywords:
                if keyword.lower() in text:
                    trends["keyword_frequency"][keyword] += text.count(keyword.lower())

        # Top topics
        for item in intelligence_list:
            categories = item.get("categories", ["general"])
            for category in categories:
                trends["top_topics"][category] += 1

        # Trend direction analysis
        if trends["temporal_distribution"]:
            dates = sorted(trends["temporal_distribution"].keys())
            if len(dates) >= 2:
                recent_count = sum(trends["temporal_distribution"][d] for d in dates[-7:])
                older_count = sum(trends["temporal_distribution"][d] for d in dates[:-7]) if len(dates) > 7 else recent_count

                if recent_count > older_count:
                    trends["trend_direction"] = {
                        "direction": "increasing",
                        "change_percent": ((recent_count - older_count) / max(older_count, 1)) * 100,
                        "description": "AI interest is increasing"
                }
                else:
                    trends["trend_direction"] = {
                        "direction": "stable",
                        "change_percent": 0,
                        "description": "AI interest is stable"
                    }

        return trends

    def create_visualization_data(self, intelligence_list: List[Dict[str, Any]], 
                                  categorized: Dict[str, List[Dict[str, Any]]],
                                  trends: Dict[str, Any]) -> Dict[str, Any]:
        """Create visualization data for Romewise AI frontend"""

        # Create nodes for visualization
        nodes = []
        edges = []

        # Category nodes
        for category, items in categorized.items():
            nodes.append({
                "id": f"category_{category}",
                "type": "category",
                "label": category.replace("_", " ").title(),
                "size": len(items),
                "color": self._get_category_color(category),
                "x": 0,  # Will be positioned by frontend
                "y": 0
            })

        # Intelligence nodes
        for idx, item in enumerate(intelligence_list[:100]):  # Limit to 100 for performance
            node_id = f"intelligence_{idx}"
            nodes.append({
                "id": node_id,
                "type": "intelligence",
                "label": item.get("title", "Untitled")[:50],
                "size": 1,
                "color": "#4A90E2",
                "url": item.get("url", ""),
                "summary": item.get("summary", "")[:200],
                "categories": item.get("categories", []),
                "timestamp": item.get("timestamp", ""),
                "x": 0,
                "y": 0
            })

            # Create edges to categories
            for category in item.get("categories", ["general"]):
                edges.append({
                    "source": node_id,
                    "target": f"category_{category}",
                    "type": "belongs_to"
                })

        # Trend nodes
        for keyword, count in trends["keyword_frequency"].most_common(20):
            nodes.append({
                "id": f"trend_{keyword}",
                "type": "trend",
                "label": keyword,
                "size": min(count / 10, 5),  # Scale size
                "color": "#FF6B6B",
                "frequency": count,
                "x": 0,
                "y": 0
            })

        visualization_data = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_intelligence": len(intelligence_list),
                "categories": len(categorized),
                "trends_analyzed": len(trends["keyword_frequency"])
            },
            "nodes": nodes,
            "edges": edges,
            "trends": {
                "top_topics": dict(trends["top_topics"].most_common(10)),
                "top_channels": dict(trends["top_channels"].most_common(10)),
                "keyword_frequency": dict(trends["keyword_frequency"].most_common(20)),
                "temporal_distribution": dict(trends["temporal_distribution"]),
                "trend_direction": trends["trend_direction"]
            },
            "categories": {
                category: {
                    "count": len(items),
                    "items": [{
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "summary": item.get("summary", "")[:200]
                    } for item in items[:10]]  # Top 10 per category
                }
                for category, items in categorized.items()
            },
            "global_ai_direction": self._analyze_global_direction(intelligence_list, trends)
        }

        return visualization_data

    def _get_category_color(self, category: str) -> str:
        """Get color for category"""
        colors = {
            "language_models": "#FF6B6B",
            "automation": "#4ECDC4",
            "computer_vision": "#45B7D1",
            "machine_learning": "#FFA07A",
            "data_science": "#98D8C8",
            "ai_ethics": "#F7DC6F",
            "ai_applications": "#BB8FCE",
            "research": "#85C1E2",
            "general": "#95A5A6"
        }
        return colors.get(category, "#95A5A6")

    def _analyze_global_direction(self, intelligence_list: List[Dict[str, Any]], 
                                  trends: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze global AI direction"""

        direction_analysis = {
            "primary_focus": [],
            "emerging_trends": [],
            "declining_areas": [],
            "overall_direction": "stable",
            "key_insights": []
        }

        # Analyze keyword frequency trends
        keyword_freq = trends.get("keyword_frequency", Counter())
        top_keywords = keyword_freq.most_common(10)

        if top_keywords:
            direction_analysis["primary_focus"] = [kw[0] for kw in top_keywords[:5]]

        # Analyze temporal trends
        temporal = trends.get("temporal_distribution", {})
        if temporal:
            dates = sorted(temporal.keys())
            if len(dates) >= 2:
                recent_keywords = []
                older_keywords = []

                # This is simplified - in production, would track keywords over time
                direction_analysis["overall_direction"] = trends.get("trend_direction", {}).get("direction", "stable")

        # Key insights
        if keyword_freq:
            top_keyword = keyword_freq.most_common(1)[0]
            direction_analysis["key_insights"].append(
                f"Most discussed topic: {top_keyword[0]} ({top_keyword[1]} mentions)"
            )

        if trends.get("top_topics"):
            top_topic = trends["top_topics"].most_common(1)[0]
            direction_analysis["key_insights"].append(
                f"Primary category: {top_topic[0]} ({top_topic[1]} items)"
            )

        direction_analysis["key_insights"].append(
            f"Total AI intelligence items: {len(intelligence_list)}"
        )

        return direction_analysis

    def save_to_lumina(self, visualization_data: Dict[str, Any]) -> Path:
        try:
            """Save visualization data to LUMINA system"""
            # Save to LUMINA data directory
            lumina_file = self.lumina_data_dir / f"ai_intelligence_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(lumina_file, 'w', encoding='utf-8') as f:
                json.dump(visualization_data, f, indent=2, default=str)

            logger.info(f"   Saved to LUMINA: {lumina_file}")

            # Also save to visualization directory for Romewise frontend
            viz_file = self.viz_dir / "romewise_ai_intelligence.json"

            with open(viz_file, 'w', encoding='utf-8') as f:
                json.dump(visualization_data, f, indent=2, default=str)

            logger.info(f"   Saved for Romewise frontend: {viz_file}")

            return viz_file

        except Exception as e:
            self.logger.error(f"Error in save_to_lumina: {e}", exc_info=True)
            raise
    def process_and_map(self) -> Dict[str, Any]:
        """Process AI intelligence and create visualization map"""
        logger.info("="*80)
        logger.info("🗺️  LUMINA AI INTELLIGENCE MAPPING")
        logger.info("="*80)
        logger.info("")

        # Load intelligence
        logger.info("📥 Loading AI intelligence...")
        intelligence_list = self.load_ai_intelligence()

        if not intelligence_list:
            logger.warning("⚠️  No AI intelligence found. Run YouTube AI scan first.")
            return {}

        # Categorize
        logger.info("📂 Categorizing intelligence...")
        categorized = self.categorize_intelligence(intelligence_list)
        logger.info(f"   Categories: {list(categorized.keys())}")

        # Extract trends
        logger.info("📊 Analyzing trends...")
        trends = self.extract_trends(intelligence_list)
        logger.info(f"   Top topics: {list(trends['top_topics'].most_common(5))}")

        # Create visualization
        logger.info("🎨 Creating visualization data...")
        visualization_data = self.create_visualization_data(intelligence_list, categorized, trends)

        # Save to LUMINA
        logger.info("💾 Saving to LUMINA system...")
        viz_file = self.save_to_lumina(visualization_data)

        # Print summary
        logger.info("")
        logger.info("="*80)
        logger.info("✅ MAPPING COMPLETE")
        logger.info("="*80)
        logger.info(f"   Intelligence Items: {len(intelligence_list)}")
        logger.info(f"   Categories: {len(categorized)}")
        logger.info(f"   Visualization Nodes: {len(visualization_data['nodes'])}")
        logger.info(f"   Visualization Edges: {len(visualization_data['edges'])}")
        logger.info(f"   Romewise File: {viz_file}")
        logger.info("="*80)

        # Print global direction
        global_dir = visualization_data.get("global_ai_direction", {})
        logger.info("")
        logger.info("🌍 GLOBAL AI DIRECTION")
        logger.info("="*80)
        logger.info(f"   Overall Direction: {global_dir.get('overall_direction', 'unknown')}")
        logger.info(f"   Primary Focus: {', '.join(global_dir.get('primary_focus', []))}")
        for insight in global_dir.get("key_insights", []):
            logger.info(f"   • {insight}")
        logger.info("="*80)

        return visualization_data


def main():
    """Main execution"""
    mapper = LUMINAAIIntelligenceMapper()
    mapper.process_and_map()


if __name__ == "__main__":


    main()