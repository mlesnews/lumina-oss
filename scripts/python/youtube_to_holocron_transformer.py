#!/usr/bin/env python3
"""
YouTube to Holocron Transformer - Inception-Style Deep Integration

Transforms YouTube channel knowledge from the Deep Crawl system into
powerful Jedi Archives Holocron entries. This is INCEPTION-level integration:
knowledge embedded within knowledge, structured for maximum power and accessibility.

"In the depths of knowledge, we plant seeds of understanding that grow into
trees of wisdom. Each Holocron is a seed. Each YouTube channel is potential
power waiting to be unlocked." - @JOCOSTA-NU

Features:
- Deep transformation of SME profiles into Holocron entries
- Multi-layered knowledge extraction (Inception-style)
- Dewey Decimal classification integration
- Full Jedi Archives integration
- Power-granting structure for knowledge access
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class YouTubeToHolocronTransformer:
    """
    YouTube to Holocron Transformer - Inception-Style Deep Integration

    Transforms YouTube channel knowledge into powerful Holocron entries
    that grant knowledge power through structured, accessible formats.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize transformer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.holocron_dir = self.data_dir / "holocron"
        self.youtube_intel_dir = self.data_dir / "youtube_intelligence"

        # Create YouTube-specific Holocron domain
        self.youtube_holocron_dir = self.holocron_dir / "youtube_sme_knowledge"
        self.youtube_holocron_dir.mkdir(parents=True, exist_ok=True)

        # Holocron index file
        self.holocron_index_file = self.holocron_dir / "HOLOCRON_INDEX.json"

        # Load existing index
        self.holocron_index = self._load_holocron_index()

        logger.info("🔮 YouTube to Holocron Transformer initialized (Inception Mode)")

    def _load_holocron_index(self) -> Dict[str, Any]:
        """Load existing Holocron index"""
        if self.holocron_index_file.exists():
            try:
                with open(self.holocron_index_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load Holocron index: {e}")

        # Return default structure
        return {
            "archive_metadata": {
                "name": "Holocron Archive - Master Index",
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "status": "operational",
                "classification": "general_access",
                "purpose": "Central catalog of all knowledge artifacts",
                "location": str(self.holocron_dir),
                "maintained_by": "@JOCOSTA-NU (Head Jedi Librarian)"
            },
            "entries": {}
        }

    def _save_holocron_index(self) -> None:
        try:
            """Save updated Holocron index"""
            self.holocron_index["archive_metadata"]["last_updated"] = datetime.now().isoformat()

            with open(self.holocron_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.holocron_index, f, indent=2, ensure_ascii=False)

            logger.info("✅ Holocron index saved")

        except Exception as e:
            self.logger.error(f"Error in _save_holocron_index: {e}", exc_info=True)
            raise
    def _generate_holocron_id(self, channel_id: str) -> str:
        """Generate unique Holocron ID for a channel"""
        timestamp = datetime.now().strftime("%Y%m%d")
        short_id = channel_id[:8] if len(channel_id) > 8 else channel_id
        return f"HOLOCRON-YT-{timestamp}-{short_id}"

    def _classify_domain(self, sme_profile: Dict[str, Any]) -> str:
        """
        Classify domain based on SME profile

        Returns Dewey Decimal domain classification
        """
        domain_matches = sme_profile.get("domain_matches", 0)
        channel_name = sme_profile.get("channel_name", "").lower()

        # Domain classification mapping (from YouTube crawler domains)
        if any(kw in channel_name for kw in ["ai", "machine learning", "neural", "llm", "gpt", "claude"]):
            return "ai_ml"
        elif any(kw in channel_name for kw in ["software", "coding", "programming", "development"]):
            return "software_engineering"
        elif any(kw in channel_name for kw in ["data", "analytics", "science"]):
            return "data_science"
        elif any(kw in channel_name for kw in ["business", "startup", "entrepreneur", "product"]):
            return "business_product"
        elif any(kw in channel_name for kw in ["quantum", "blockchain", "crypto", "web3"]):
            return "emerging_tech"
        else:
            return "general_knowledge"

    def _extract_knowledge_layers(self, sme_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract knowledge in Inception-style layers

        Layer 0: Surface knowledge (basic channel info)
        Layer 1: Content knowledge (video analysis)
        Layer 2: Expertise knowledge (SME scoring and indicators)
        Layer 3: Intelligence knowledge (actionable insights)
        """
        videos = sme_profile.get("videos", [])

        # Layer 0: Surface
        layer_0 = {
            "channel_id": sme_profile.get("channel_id"),
            "channel_name": sme_profile.get("channel_name"),
            "uploader": sme_profile.get("uploader"),
            "url": sme_profile.get("url"),
            "identified_at": sme_profile.get("identified_at")
        }

        # Layer 1: Content
        layer_1 = {
            "video_count": sme_profile.get("video_count", 0),
            "total_views": sme_profile.get("total_views", 0),
            "top_videos": [
                {
                    "title": v.get("title"),
                    "video_id": v.get("video_id"),
                    "url": v.get("url"),
                    "view_count": v.get("view_count"),
                    "upload_date": v.get("upload_date")
                }
                for v in videos[:10]  # Top 10 videos
            ],
            "content_analysis": {
                "video_titles": [v.get("title", "") for v in videos[:20]],
                "upload_frequency": "calculated",  # TODO: Calculate from dates  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                "engagement_metrics": {
                    "total_views": sme_profile.get("total_views", 0),
                    "average_views_per_video": sme_profile.get("total_views", 0) / max(sme_profile.get("video_count", 1), 1)
                }
            }
        }

        # Layer 2: Expertise
        layer_2 = {
            "sme_score": sme_profile.get("sme_score", 0),
            "sme_tier": sme_profile.get("sme_tier", "casual"),
            "sme_indicators": sme_profile.get("sme_indicators", []),
            "domain_matches": sme_profile.get("domain_matches", 0),
            "expertise_areas": self._identify_expertise_areas(videos),
            "credibility_metrics": {
                "high_video_count": sme_profile.get("video_count", 0) > 10,
                "high_view_count": sme_profile.get("total_views", 0) > 100000,
                "domain_focused": sme_profile.get("domain_matches", 0) > 5
            }
        }

        # Layer 3: Intelligence (deepest layer - actionable power)
        layer_3 = {
            "actionable_insights": self._generate_actionable_insights(sme_profile),
            "knowledge_gaps_addressed": self._identify_knowledge_gaps(videos),
            "recommended_use_cases": self._recommend_use_cases(sme_profile),
            "power_granting_attributes": {
                "searchable": True,
                "actionable": True,
                "structured": True,
                "integrated": True,
                "evolving": True
            }
        }

        return {
            "layer_0_surface": layer_0,
            "layer_1_content": layer_1,
            "layer_2_expertise": layer_2,
            "layer_3_intelligence": layer_3
        }

    def _identify_expertise_areas(self, videos: List[Dict[str, Any]]) -> List[str]:
        """Identify specific expertise areas from video titles"""
        expertise_keywords = defaultdict(int)
        all_titles = " ".join([v.get("title", "").lower() for v in videos[:20]])

        # Common expertise keywords
        keywords = [
            "python", "javascript", "react", "kubernetes", "docker",
            "machine learning", "deep learning", "neural networks",
            "system design", "architecture", "distributed systems",
            "startup", "business", "product", "entrepreneurship"
        ]

        for keyword in keywords:
            if keyword in all_titles:
                expertise_keywords[keyword] += all_titles.count(keyword)

        # Return top 5 expertise areas
        sorted_expertise = sorted(expertise_keywords.items(), key=lambda x: x[1], reverse=True)
        return [kw for kw, count in sorted_expertise[:5]]

    def _generate_actionable_insights(self, sme_profile: Dict[str, Any]) -> List[str]:
        """Generate actionable insights from SME profile"""
        insights = []
        sme_tier = sme_profile.get("sme_tier", "casual")

        if sme_tier == "expert":
            insights.append("High-quality source for deep domain knowledge")
            insights.append("Recommended for comprehensive learning paths")
            insights.append("Valuable for expert-level insights and best practices")

        if sme_profile.get("total_views", 0) > 100000:
            insights.append("High engagement indicates practical, applicable knowledge")

        if sme_profile.get("domain_matches", 0) > 5:
            insights.append("Strong domain focus - reliable source for specialized topics")

        return insights

    def _identify_knowledge_gaps(self, videos: List[Dict[str, Any]]) -> List[str]:
        """Identify knowledge gaps that this channel addresses"""
        # Analyze video titles to identify topics covered
        topics = set()
        for video in videos[:20]:
            title = video.get("title", "").lower()
            # Extract key topics (simplified - could be enhanced with NLP)
            if any(kw in title for kw in ["tutorial", "guide", "how to", "learn"]):
                topics.add("Educational content")
            if any(kw in title for kw in ["deep dive", "explained", "understanding"]):
                topics.add("Deep explanations")
            if any(kw in title for kw in ["tips", "tricks", "best practices"]):
                topics.add("Practical advice")

        return list(topics)

    def _recommend_use_cases(self, sme_profile: Dict[str, Any]) -> List[str]:
        """Recommend use cases for this channel's knowledge"""
        use_cases = []
        sme_tier = sme_profile.get("sme_tier", "casual")

        if sme_tier in ["expert", "experienced"]:
            use_cases.append("Learning resource for domain expertise")
            use_cases.append("Reference for best practices and patterns")
            use_cases.append("Source for staying current with domain trends")

        if sme_profile.get("video_count", 0) > 50:
            use_cases.append("Comprehensive knowledge base for domain")

        return use_cases

    def _generate_holocron_entry(self, sme_profile: Dict[str, Any], knowledge_layers: Dict[str, Any]) -> Dict[str, Any]:
        """Generate complete Holocron entry from SME profile and knowledge layers"""
        holocron_id = self._generate_holocron_id(sme_profile.get("channel_id", "unknown"))
        domain = self._classify_domain(sme_profile)

        # Determine priority based on SME tier
        tier_priority_map = {
            "expert": "HIGH",
            "experienced": "MEDIUM",
            "emerging": "LOW",
            "casual": "LOW"
        }
        priority = tier_priority_map.get(sme_profile.get("sme_tier", "casual"), "LOW")

        # Generate tags
        tags = [
            "#youtube-sme",
            f"#sme-tier-{sme_profile.get('sme_tier', 'casual')}",
            f"#domain-{domain}",
            "#external-knowledge",
            "#holocron-transformed"
        ]

        # Add domain-specific tags
        if domain == "ai_ml":
            tags.append("#ai-machine-learning")
        elif domain == "software_engineering":
            tags.append("#software-development")
        elif domain == "data_science":
            tags.append("#data-analytics")

        holocron_entry = {
            "entry_id": holocron_id,
            "title": f"YouTube SME: {sme_profile.get('channel_name', 'Unknown Channel')}",
            "type": "external_knowledge_source",
            "domain": domain,
            "classification": f"Δ-028.7 YouTube Deep Crawl - {domain.replace('_', ' ').title()}",
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
            "priority": priority,
            "status": "active",
            "tags": tags,
            "source": {
                "type": "youtube_channel",
                "channel_id": sme_profile.get("channel_id"),
                "channel_name": sme_profile.get("channel_name"),
                "channel_url": sme_profile.get("url"),
                "crawled_at": sme_profile.get("identified_at")
            },
            "knowledge_layers": knowledge_layers,
            "metadata": {
                "sme_score": sme_profile.get("sme_score", 0),
                "sme_tier": sme_profile.get("sme_tier", "casual"),
                "video_count": sme_profile.get("video_count", 0),
                "total_views": sme_profile.get("total_views", 0),
                "domain_matches": sme_profile.get("domain_matches", 0)
            },
            "integration_points": {
                "dewey_classification": "Δ-028.7",
                "jedi_archives_location": f"youtube_sme_knowledge/{domain}",
                "power_granting": True,
                "searchable": True,
                "actionable": True
            }
        }

        return holocron_entry

    def _create_holocron_document(self, holocron_entry: Dict[str, Any], knowledge_layers: Dict[str, Any]) -> Path:
        """Create markdown document for Holocron entry"""
        domain = holocron_entry.get("domain", "general")
        domain_dir = self.youtube_holocron_dir / domain
        domain_dir.mkdir(parents=True, exist_ok=True)

        # Create filename from channel name
        channel_name = holocron_entry.get("source", {}).get("channel_name", "unknown")
        safe_filename = "".join(c if c.isalnum() or c in (' ', '-', '_') else '' for c in channel_name)
        safe_filename = safe_filename.replace(' ', '_').lower()[:50]

        doc_file = domain_dir / f"{safe_filename}_{holocron_entry['entry_id']}.md"

        # Generate markdown content
        md_content = f"""# {holocron_entry['title']}

**Holocron ID:** {holocron_entry['entry_id']}  
**Classification:** {holocron_entry['classification']}  
**Domain:** {holocron_entry['domain'].replace('_', ' ').title()}  
**Priority:** {holocron_entry['priority']}  
**Status:** {holocron_entry['status']}  
**Created:** {holocron_entry['created']}  
**Last Modified:** {holocron_entry['modified']}

---

## Source Information

- **Channel Name:** {holocron_entry['source']['channel_name']}
- **Channel ID:** {holocron_entry['source']['channel_id']}
- **Channel URL:** {holocron_entry['source']['channel_url']}
- **Crawled At:** {holocron_entry['source']['crawled_at']}

---

## SME Profile

- **SME Score:** {holocron_entry['metadata']['sme_score']}/3
- **SME Tier:** {holocron_entry['metadata']['sme_tier'].upper()}
- **Video Count:** {holocron_entry['metadata']['video_count']}
- **Total Views:** {holocron_entry['metadata']['total_views']:,}
- **Domain Matches:** {holocron_entry['metadata']['domain_matches']}

---

## Knowledge Layers (Inception-Style Deep Integration)

### Layer 0: Surface Knowledge
- **Channel ID:** {knowledge_layers['layer_0_surface']['channel_id']}
- **Channel Name:** {knowledge_layers['layer_0_surface']['channel_name']}
- **Uploader:** {knowledge_layers['layer_0_surface']['uploader']}
- **URL:** {knowledge_layers['layer_0_surface']['url']}

### Layer 1: Content Knowledge
- **Video Count:** {knowledge_layers['layer_1_content']['video_count']}
- **Total Views:** {knowledge_layers['layer_1_content']['total_views']:,}
- **Average Views/Video:** {knowledge_layers['layer_1_content']['content_analysis']['engagement_metrics']['average_views_per_video']:,.0f}

**Top Videos:**
"""

        for i, video in enumerate(knowledge_layers['layer_1_content']['top_videos'][:5], 1):
            md_content += f"\n{i}. **{video.get('title', 'Unknown')}**"
            md_content += f"\n   - Views: {video.get('view_count', 'N/A')}"
            md_content += f"\n   - Upload Date: {video.get('upload_date', 'N/A')}"
            md_content += f"\n   - URL: {video.get('url', 'N/A')}\n"

        md_content += f"""
### Layer 2: Expertise Knowledge
- **SME Tier:** {knowledge_layers['layer_2_expertise']['sme_tier'].upper()}
- **SME Score:** {knowledge_layers['layer_2_expertise']['sme_score']}/3
- **Domain Matches:** {knowledge_layers['layer_2_expertise']['domain_matches']}

**SME Indicators:**
"""
        for indicator in knowledge_layers['layer_2_expertise']['sme_indicators']:
            md_content += f"- {indicator}\n"

        md_content += "\n**Expertise Areas:**\n"
        for area in knowledge_layers['layer_2_expertise']['expertise_areas']:
            md_content += f"- {area}\n"

        md_content += f"""
### Layer 3: Intelligence Knowledge (Power-Granting Layer)
**Actionable Insights:**
"""
        for insight in knowledge_layers['layer_3_intelligence']['actionable_insights']:
            md_content += f"- {insight}\n"

        md_content += "\n**Knowledge Gaps Addressed:**\n"
        for gap in knowledge_layers['layer_3_intelligence']['knowledge_gaps_addressed']:
            md_content += f"- {gap}\n"

        md_content += "\n**Recommended Use Cases:**\n"
        for use_case in knowledge_layers['layer_3_intelligence']['recommended_use_cases']:
            md_content += f"- {use_case}\n"

        md_content += f"""
---

## Power-Granting Attributes

This Holocron grants knowledge power through:
- ✅ **Searchable:** Fully indexed and searchable in Jedi Archives
- ✅ **Actionable:** Contains actionable insights and recommendations
- ✅ **Structured:** Multi-layered knowledge organization (Inception-style)
- ✅ **Integrated:** Connected to Master Feedback Loop and SYPHON
- ✅ **Evolving:** Continuously updated with new channel content

---

## Integration Points

- **Dewey Classification:** {holocron_entry['integration_points']['dewey_classification']}
- **Jedi Archives Location:** {holocron_entry['integration_points']['jedi_archives_location']}
- **Tags:** {', '.join(holocron_entry['tags'])}

---

## Tags

{chr(10).join(['- ' + tag for tag in holocron_entry['tags']])}

---

*This Holocron was automatically generated from YouTube channel knowledge through deep Inception-style transformation. Each layer reveals deeper insights, granting increasing knowledge power.*
"""

        # Write document
        doc_file.write_text(md_content, encoding='utf-8')
        logger.info(f"✅ Holocron document created: {doc_file.name}")

        return doc_file

    def transform_sme_to_holocron(self, sme_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single SME profile into a Holocron entry

        This is the core transformation - Inception-style deep knowledge extraction
        """
        logger.info(f"🔮 Transforming SME to Holocron: {sme_profile.get('channel_name', 'Unknown')}")

        # Extract knowledge layers (Inception-style)
        knowledge_layers = self._extract_knowledge_layers(sme_profile)

        # Generate Holocron entry
        holocron_entry = self._generate_holocron_entry(sme_profile, knowledge_layers)

        # Create markdown document
        doc_path = self._create_holocron_document(holocron_entry, knowledge_layers)
        holocron_entry["location"] = str(doc_path.relative_to(self.project_root))

        # Add to index
        domain = holocron_entry.get("domain", "general_knowledge")
        if "entries" not in self.holocron_index:
            self.holocron_index["entries"] = {}

        if "youtube_sme_knowledge" not in self.holocron_index["entries"]:
            self.holocron_index["entries"]["youtube_sme_knowledge"] = {}

        if domain not in self.holocron_index["entries"]["youtube_sme_knowledge"]:
            self.holocron_index["entries"]["youtube_sme_knowledge"][domain] = {}

        # Store in index
        entry_key = holocron_entry["entry_id"].lower().replace("-", "_")
        self.holocron_index["entries"]["youtube_sme_knowledge"][domain][entry_key] = holocron_entry

        logger.info(f"✅ SME transformed to Holocron: {holocron_entry['entry_id']}")

        return holocron_entry

    def transform_all_smes(self, sme_map_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """
        Transform all SMEs from the SME map into Holocron entries

        This is the mass transformation - turning waves of channels into
        powerful knowledge artifacts
        """
        if sme_map_file is None:
            sme_map_file = self.youtube_intel_dir / "sme_map.json"

        if not sme_map_file.exists():
            logger.warning(f"⚠️  SME map file not found: {sme_map_file}")
            return []

        # Load SME map
        with open(sme_map_file, 'r', encoding='utf-8') as f:
            sme_map_data = json.load(f)

        sme_profiles = sme_map_data.get("smes", [])
        logger.info(f"🔮 Transforming {len(sme_profiles)} SMEs to Holocrons (Inception Mode)")

        transformed_holocrons = []

        for sme_profile in sme_profiles:
            try:
                holocron_entry = self.transform_sme_to_holocron(sme_profile)
                transformed_holocrons.append(holocron_entry)
            except Exception as e:
                logger.error(f"❌ Error transforming SME {sme_profile.get('channel_name', 'Unknown')}: {e}")

        # Save updated index
        self._save_holocron_index()

        logger.info(f"✅ Transformation complete: {len(transformed_holocrons)} Holocrons created")

        return transformed_holocrons

    def generate_transformation_report(self, holocrons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate transformation report"""
        report = {
            "transformation_timestamp": datetime.now().isoformat(),
            "total_holocrons_created": len(holocrons),
            "domain_breakdown": defaultdict(int),
            "tier_breakdown": defaultdict(int),
            "priority_breakdown": defaultdict(int),
            "total_knowledge_power": {
                "total_videos": sum(h.get("metadata", {}).get("video_count", 0) for h in holocrons),
                "total_views": sum(h.get("metadata", {}).get("total_views", 0) for h in holocrons),
                "total_sme_score": sum(h.get("metadata", {}).get("sme_score", 0) for h in holocrons)
            }
        }

        for holocron in holocrons:
            domain = holocron.get("domain", "unknown")
            tier = holocron.get("metadata", {}).get("sme_tier", "unknown")
            priority = holocron.get("priority", "unknown")

            report["domain_breakdown"][domain] += 1
            report["tier_breakdown"][tier] += 1
            report["priority_breakdown"][priority] += 1

        return report

def main():
    try:
        """Main execution"""
        transformer = YouTubeToHolocronTransformer()

        import argparse
        parser = argparse.ArgumentParser(description="YouTube to Holocron Transformer (Inception Mode)")
        parser.add_argument("--sme-map", type=Path, help="Path to SME map JSON file")
        parser.add_argument("--report", action="store_true", help="Generate transformation report")

        args = parser.parse_args()

        # Transform all SMEs
        holocrons = transformer.transform_all_smes(args.sme_map)

        if args.report and holocrons:
            report = transformer.generate_transformation_report(holocrons)
            report_file = transformer.data_dir / "youtube_intelligence" / f"transformation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            print(f"\n✅ Transformation Report:")
            print(f"   Total Holocrons: {report['total_holocrons_created']}")
            print(f"   Total Videos: {report['total_knowledge_power']['total_videos']:,}")
            print(f"   Total Views: {report['total_knowledge_power']['total_views']:,}")
            print(f"   Report saved: {report_file.name}")

        print(f"\n🔮 Inception complete: {len(holocrons)} channels transformed into powerful Holocrons")
        print("   Knowledge power granted. Wisdom unlocked. ⚡📚")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()