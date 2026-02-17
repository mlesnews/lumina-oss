#!/usr/bin/env python3
"""
Analyze Today's Intelligence Gathering - External Source Scans & Sweeps

Generates comprehensive report on:
- What we've learned today
- How long scans took
- Intelligence value assessment (mission-critical vs informational)
- Temperature/intensity scoring
- Recommendations for next scan timing and intensity

Tags: #INTELLIGENCE #ANALYSIS #SYPHON #EXTERNAL_SOURCES @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

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

logger = get_logger("AnalyzeTodaysIntelligence")


class IntelligenceValue(Enum):
    """Intelligence value classification"""
    MISSION_CRITICAL = "mission_critical"  # Actionable, high-impact, time-sensitive
    HIGH_VALUE = "high_value"  # Important but not immediately critical
    INFORMATIONAL = "informational"  # Useful context but not actionable
    LOW_VALUE = "low_value"  # Minimal value, noise


class IntelligenceTemperature(Enum):
    """Intelligence temperature/intensity"""
    CRITICAL = "critical"  # 🔥🔥🔥 Immediate action required
    HOT = "hot"  # 🔥🔥 High priority, time-sensitive
    WARM = "warm"  # 🔥 Moderate priority
    COOL = "cool"  # Normal priority
    COLD = "cold"  # Low priority, background info


@dataclass
class IntelligenceAssessment:
    """Assessment of intelligence value and temperature"""
    value: IntelligenceValue
    temperature: IntelligenceTemperature
    score: float  # 0-100
    reasoning: str
    actionable: bool
    time_sensitive: bool
    impact_level: str  # "high", "medium", "low"


class IntelligenceAnalyzer:
    """Analyze intelligence for value and temperature"""

    # Keywords that indicate mission-critical intelligence
    MISSION_CRITICAL_KEYWORDS = [
        "security", "breach", "vulnerability", "exploit", "attack", "threat",
        "critical", "urgent", "emergency", "outage", "failure", "down",
        "deadline", "due", "required", "must", "immediate", "now",
        "opportunity", "deal", "contract", "revenue", "profit", "loss",
        "compliance", "legal", "lawsuit", "regulation", "audit"
    ]

    # Keywords that indicate high-value intelligence
    HIGH_VALUE_KEYWORDS = [
        "update", "new", "release", "announcement", "feature", "improvement",
        "partnership", "collaboration", "acquisition", "merger",
        "research", "study", "finding", "discovery", "breakthrough",
        "trend", "market", "industry", "competitor", "analysis"
    ]

    def assess_intelligence(self, intelligence_data: Dict[str, Any]) -> IntelligenceAssessment:
        """
        Assess intelligence value and temperature

        Args:
            intelligence_data: Intelligence data dict with title, content, summary, etc.

        Returns:
            IntelligenceAssessment
        """
        content = (intelligence_data.get("content", "") or "").lower()
        title = (intelligence_data.get("title", "") or "").lower()
        summary = (intelligence_data.get("summary", "") or "").lower()

        combined_text = f"{title} {summary} {content}"

        # Count keyword matches
        mission_critical_matches = sum(1 for kw in self.MISSION_CRITICAL_KEYWORDS if kw in combined_text)
        high_value_matches = sum(1 for kw in self.HIGH_VALUE_KEYWORDS if kw in combined_text)

        # Calculate score (0-100)
        score = 0.0

        # Mission-critical indicators
        if mission_critical_matches > 0:
            score += min(mission_critical_matches * 15, 60)  # Up to 60 points

        # High-value indicators
        if high_value_matches > 0:
            score += min(high_value_matches * 5, 30)  # Up to 30 points

        # Recency bonus (if timestamp available)
        if "timestamp" in intelligence_data:
            try:
                intel_time = datetime.fromisoformat(intelligence_data["timestamp"])
                age_hours = (datetime.now() - intel_time).total_seconds() / 3600
                if age_hours < 1:
                    score += 10  # Very recent
                elif age_hours < 24:
                    score += 5  # Today
            except:
                pass

        # Source quality bonus
        source = intelligence_data.get("source", "").lower()
        if any(x in source for x in ["official", "primary", "direct", "verified"]):
            score += 5

        score = min(score, 100.0)

        # Determine value classification
        if score >= 70:
            value = IntelligenceValue.MISSION_CRITICAL
            temperature = IntelligenceTemperature.CRITICAL if score >= 85 else IntelligenceTemperature.HOT
            actionable = True
            time_sensitive = True
            impact_level = "high"
        elif score >= 40:
            value = IntelligenceValue.HIGH_VALUE
            temperature = IntelligenceTemperature.WARM
            actionable = True
            time_sensitive = score >= 50
            impact_level = "medium"
        elif score >= 20:
            value = IntelligenceValue.INFORMATIONAL
            temperature = IntelligenceTemperature.COOL
            actionable = False
            time_sensitive = False
            impact_level = "low"
        else:
            value = IntelligenceValue.LOW_VALUE
            temperature = IntelligenceTemperature.COLD
            actionable = False
            time_sensitive = False
            impact_level = "low"

        # Generate reasoning
        reasoning_parts = []
        if mission_critical_matches > 0:
            reasoning_parts.append(f"{mission_critical_matches} mission-critical indicators")
        if high_value_matches > 0:
            reasoning_parts.append(f"{high_value_matches} high-value indicators")
        if score >= 70:
            reasoning_parts.append("High actionable value")
        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Low signal strength"

        return IntelligenceAssessment(
            value=value,
            temperature=temperature,
            score=score,
            reasoning=reasoning,
            actionable=actionable,
            time_sensitive=time_sensitive,
            impact_level=impact_level
        )


def analyze_todays_scans() -> Dict[str, Any]:
    """Analyze today's scan results"""
    data_dir = project_root / "data" / "syphon_source_sweeps_scans"
    scan_history_file = data_dir / "scan_history.json"

    today = datetime.now().date()
    today_scans = []

    if scan_history_file.exists():
        with open(scan_history_file, 'r') as f:
            all_scans = json.load(f)

            for scan in all_scans:
                try:
                    scan_time = datetime.fromisoformat(scan["timestamp"])
                    if scan_time.date() == today:
                        today_scans.append(scan)
                except:
                    pass

    # Filter external sources
    external_scans = [
        s for s in today_scans
        if s.get("source_id", "").startswith("external_")
    ]

    # Calculate statistics
    total_duration = sum(s.get("duration_seconds", 0) for s in external_scans)
    total_items = sum(s.get("items_found", 0) for s in external_scans)
    total_intelligence = sum(s.get("intelligence_extracted", 0) for s in external_scans)
    total_duplicates = sum(s.get("metadata", {}).get("duplicates_skipped", 0) for s in external_scans)
    total_updates = sum(s.get("metadata", {}).get("updates_found", 0) for s in external_scans)

    # Group by source
    by_source = {}
    for scan in external_scans:
        source_id = scan.get("source_id", "unknown")
        if source_id not in by_source:
            by_source[source_id] = {
                "source_name": scan.get("source_name", source_id),
                "scans": [],
                "total_items": 0,
                "total_intelligence": 0,
                "total_duration": 0.0
            }
        by_source[source_id]["scans"].append(scan)
        by_source[source_id]["total_items"] += scan.get("items_found", 0)
        by_source[source_id]["total_intelligence"] += scan.get("intelligence_extracted", 0)
        by_source[source_id]["total_duration"] += scan.get("duration_seconds", 0)

    return {
        "date": today.isoformat(),
        "total_scans": len(external_scans),
        "total_duration_seconds": total_duration,
        "total_duration_formatted": f"{total_duration:.2f}s ({total_duration/60:.2f} minutes)",
        "total_items_found": total_items,
        "total_intelligence_extracted": total_intelligence,
        "total_duplicates_skipped": total_duplicates,
        "total_updates_found": total_updates,
        "scans_by_source": by_source,
        "raw_scans": external_scans
    }


def recommend_next_scan(analysis: Dict[str, Any], sources_config: Dict[str, Any]) -> Dict[str, Any]:
    """Recommend when to run next scan and at what intensity"""
    # Get minimum scan interval from sources
    min_interval = min(
        (s.get("scan_interval_minutes", 240) for s in sources_config.values()),
        default=240
    )

    # If we found intelligence, recommend sooner
    if analysis["total_intelligence_extracted"] > 0:
        recommended_interval = min_interval / 2  # Scan twice as often
        intensity = "DEEP"  # Use deep scan
    elif analysis["total_items_found"] > 0:
        recommended_interval = min_interval * 0.75  # Slightly more frequent
        intensity = "TARGETED"  # Use targeted scan
    else:
        recommended_interval = min_interval  # Normal interval
        intensity = "QUICK"  # Use quick scan

    # Calculate next scan time
    next_scan_time = datetime.now() + timedelta(minutes=recommended_interval)

    return {
        "recommended_interval_minutes": recommended_interval,
        "recommended_interval_formatted": f"{recommended_interval:.0f} minutes ({recommended_interval/60:.1f} hours)",
        "recommended_intensity": intensity,
        "next_scan_time": next_scan_time.isoformat(),
        "next_scan_time_formatted": next_scan_time.strftime("%Y-%m-%d %H:%M:%S"),
        "reasoning": (
            "High intelligence found - scan more frequently" if analysis["total_intelligence_extracted"] > 0
            else "Normal scan interval recommended" if analysis["total_items_found"] == 0
            else "Some items found - slightly increase frequency"
        )
    }


def main():
    try:
        """Main execution"""
        logger.info("="*80)
        logger.info("📊 TODAY'S EXTERNAL SOURCE INTELLIGENCE ANALYSIS")
        logger.info("="*80)
        logger.info("")

        # Analyze today's scans
        analysis = analyze_todays_scans()

        logger.info("📅 DATE: " + analysis["date"])
        logger.info("")

        logger.info("🔍 SCAN SUMMARY")
        logger.info(f"   Total External Scans: {analysis['total_scans']}")
        logger.info(f"   Total Duration: {analysis['total_duration_formatted']}")
        logger.info(f"   Items Found: {analysis['total_items_found']}")
        logger.info(f"   Intelligence Extracted: {analysis['total_intelligence_extracted']}")
        logger.info(f"   Duplicates Skipped: {analysis['total_duplicates_skipped']}")
        logger.info(f"   Updates Found: {analysis['total_updates_found']}")
        logger.info("")

        # Show breakdown by source
        if analysis["scans_by_source"]:
            logger.info("📊 BREAKDOWN BY SOURCE")
            for source_id, source_data in analysis["scans_by_source"].items():
                logger.info(f"   {source_data['source_name']}:")
                logger.info(f"      Scans: {len(source_data['scans'])}")
                logger.info(f"      Items: {source_data['total_items']}")
                logger.info(f"      Intelligence: {source_data['total_intelligence']}")
                logger.info(f"      Duration: {source_data['total_duration']:.2f}s")
            logger.info("")

        # Load sources config for recommendations
        sources_file = project_root / "data" / "syphon_source_sweeps_scans" / "sources.json"
        sources_config = {}
        if sources_file.exists():
            with open(sources_file, 'r') as f:
                sources_config = json.load(f)

        # Get recommendations
        recommendations = recommend_next_scan(analysis, sources_config)

        logger.info("⏰ NEXT SCAN RECOMMENDATIONS")
        logger.info(f"   Recommended Interval: {recommendations['recommended_interval_formatted']}")
        logger.info(f"   Recommended Intensity: {recommendations['recommended_intensity']}")
        logger.info(f"   Next Scan Time: {recommendations['next_scan_time_formatted']}")
        logger.info(f"   Reasoning: {recommendations['reasoning']}")
        logger.info("")

        # Intelligence value assessment
        logger.info("🎯 INTELLIGENCE VALUE ASSESSMENT")
        logger.info("")
        logger.info("   Value Classifications:")
        logger.info("   - MISSION_CRITICAL: Actionable, high-impact, time-sensitive")
        logger.info("   - HIGH_VALUE: Important but not immediately critical")
        logger.info("   - INFORMATIONAL: Useful context but not actionable")
        logger.info("   - LOW_VALUE: Minimal value, noise")
        logger.info("")
        logger.info("   Temperature Levels:")
        logger.info("   - CRITICAL 🔥🔥🔥: Immediate action required")
        logger.info("   - HOT 🔥🔥: High priority, time-sensitive")
        logger.info("   - WARM 🔥: Moderate priority")
        logger.info("   - COOL: Normal priority")
        logger.info("   - COLD: Low priority, background info")
        logger.info("")

        if analysis["total_intelligence_extracted"] == 0:
            logger.info("   ⚠️  No intelligence extracted today - scans may need implementation")
            logger.info("   💡 Recommendation: Focus on implementing actual source scanning logic")
            logger.info("   💡 For 4-6 hour deep searches: Use DEEP scan type with high-value sources")
        else:
            logger.info(f"   ✅ {analysis['total_intelligence_extracted']} intelligence items extracted")
            logger.info("   💡 Use IntelligenceAnalyzer.assess_intelligence() to evaluate each item")

        logger.info("")
        logger.info("="*80)
        logger.info("✅ ANALYSIS COMPLETE")
        logger.info("="*80)

        # Save detailed report
        report_file = project_root / "data" / "syphon_source_sweeps_scans" / f"intelligence_report_{datetime.now().strftime('%Y%m%d')}.json"
        report = {
            "analysis": analysis,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"📄 Detailed report saved to: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()