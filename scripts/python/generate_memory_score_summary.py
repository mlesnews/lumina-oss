#!/usr/bin/env python3
"""
🔄 **Lumina Memory Score Summary Generator**

Generates comprehensive memory score summaries and comparative analysis.
Shows persistent scoring trends, improvement tracking, and intent fulfillment metrics.
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Local imports
script_dir = Path(__file__).parent.parent
project_root = script_dir.parent
if str(project_root) not in os.sys.path:
    os.sys.path.insert(0, str(project_root))

from persistent_memory_scorer import get_memory_scorer, get_memory_score_report
import logging
logger = logging.getLogger("generate_memory_score_summary")


def generate_comprehensive_memory_summary() -> str:
    """Generate comprehensive memory score summary with comparisons"""

    scorer = get_memory_scorer()

    # Get current score and recent report
    current_score = scorer.get_current_memory_score()
    report = get_memory_score_report(days_back=30)

    # Create comprehensive summary
    summary_lines = []

    # Header
    summary_lines.append("🔄 **LUMINA PERSISTENT MEMORY SCORE SUMMARY**")
    summary_lines.append("=" * 60)
    summary_lines.append(f"📅 **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    summary_lines.append("")

    # Current Score Section
    summary_lines.append("🎯 **CURRENT MEMORY SCORE**")
    summary_lines.append("-" * 30)

    if current_score is not None:
        summary_lines.append(".1f")
        summary_lines.append("")

        # Score interpretation
        if current_score >= 90:
            interpretation = "🏆 EXCELLENT - Outstanding memory and intent fulfillment"
        elif current_score >= 80:
            interpretation = "🎖️ VERY GOOD - Strong performance with minor gaps"
        elif current_score >= 70:
            interpretation = "👍 GOOD - Solid performance with room for improvement"
        elif current_score >= 60:
            interpretation = "⚠️ FAIR - Adequate performance needing attention"
        elif current_score >= 40:
            interpretation = "❌ POOR - Significant gaps requiring improvement"
        else:
            interpretation = "💔 CRITICAL - Major issues with memory and fulfillment"

        summary_lines.append(f"**Interpretation:** {interpretation}")
    else:
        summary_lines.append("❌ **No current score available**")
        summary_lines.append("   (First run - establishing baseline)")

    summary_lines.append("")

    # Detailed Report Section
    summary_lines.append("📊 **DETAILED PERFORMANCE ANALYSIS**")
    summary_lines.append("-" * 40)

    if report['total_scores'] > 0:
        trends = report['trends']

        summary_lines.append(f"📈 **Total Evaluations:** {report['total_scores']}")
        summary_lines.append(f"📊 **Average Score:** {report.get('average_score', 0):.1f}/100")
        summary_lines.append(f"📊 **Trend Direction:** {trends.trend_direction.upper()}")
        summary_lines.append(f"📈 **Improvement Rate:** {trends.get('improvement_rate', 0):.1f}%")
        summary_lines.append(f"🎯 **Consistency Rating:** {trends.consistency_rating.upper()}")
        summary_lines.append("")

        # Component Analysis
        summary_lines.append("🔍 **SCORE COMPONENTS BREAKDOWN**")
        summary_lines.append("-" * 35)

        components = [
            ("Intent Understanding", "How well user intent is grasped"),
            ("Context Retention", "How well previous context is maintained"),
            ("Completion Quality", "Quality of task execution and deliverables"),
            ("User Satisfaction", "Estimated user satisfaction level"),
            ("Innovation Level", "Level of creative and novel solutions"),
            ("Error Prevention", "Effectiveness of error avoidance and handling")
        ]

        weights = {
            "Intent Understanding": "25%",
            "Context Retention": "20%",
            "Completion Quality": "25%",
            "User Satisfaction": "15%",
            "Innovation Level": "10%",
            "Error Prevention": "5%"
        }

        for component, description in components:
            summary_lines.append(f"• **{component}** ({weights[component]})")
            summary_lines.append(f"  └─ {description}")

        summary_lines.append("")

        # Distribution Analysis
        summary_lines.append("📋 **QUALITY DISTRIBUTIONS**")
        summary_lines.append("-" * 30)

        distributions = report['distributions']

        # Context Quality
        summary_lines.append("**Context Quality:**")
        context_dist = distributions['context_quality']
        for quality, count in context_dist.items():
            if count > 0:
                summary_lines.append(f"  • {quality.capitalize()}: {count}")

        summary_lines.append("")

        # Fulfillment Level
        summary_lines.append("**Fulfillment Level:**")
        fulfillment_dist = distributions['fulfillment_level']
        for level, count in fulfillment_dist.items():
            if count > 0:
                summary_lines.append(f"  • {level.capitalize()}: {count}")

        summary_lines.append("")

        # Trend Analysis
        summary_lines.append("📈 **IMPROVEMENT TRENDS**")
        summary_lines.append("-" * 25)

        improvement_trends = distributions['improvement_trends']
        total_trends = sum(improvement_trends.values())

        if total_trends > 0:
            for trend, count in improvement_trends.items():
                percentage = (count / total_trends) * 100
                summary_lines.append(f"  • {trend.capitalize()}: {count} ({percentage:.1f}%)")
        summary_lines.append("")

        # Recent Scores
        if 'recent_scores' in report and report['recent_scores']:
            summary_lines.append("📅 **RECENT SCORES (Last 10)**")
            summary_lines.append("-" * 30)

            recent_scores = report['recent_scores'][:10]
            for i, score in enumerate(recent_scores, 1):
                summary_lines.append(f"  {i:2d}. Score: {score:.1f}/100")

    else:
        summary_lines.append("📝 **No historical data available**")
        summary_lines.append("   (This appears to be the baseline evaluation)")

    summary_lines.append("")

    # Comparative Analysis Section
    summary_lines.append("🔄 **COMPARATIVE ANALYSIS**")
    summary_lines.append("-" * 30)

    # Previous vs Current Analysis
    if report['total_scores'] > 1:
        recent_scores = report['recent_scores'][:5] if 'recent_scores' in report else []
        if len(recent_scores) >= 2:
            latest = recent_scores[0]
            previous = recent_scores[1]
            change = latest - previous

            summary_lines.append("**Score Change Analysis:**")
            summary_lines.append(f"  📈 Change: {change:+.1f} points")
            if change > 0:
                summary_lines.append("  🎉 **IMPROVEMENT DETECTED**")
            elif change < 0:
                summary_lines.append("  ⚠️ **DECLINE DETECTED**")
            else:
                summary_lines.append("  ➡️ **STABLE PERFORMANCE**")
    else:
        summary_lines.append("**Baseline Establishment:**")
        summary_lines.append("  📊 First evaluation - establishing performance baseline")
        summary_lines.append("  🔄 Future evaluations will show improvement trends")

    summary_lines.append("")

    # Performance Insights
    summary_lines.append("💡 **PERFORMANCE INSIGHTS**")
    summary_lines.append("-" * 28)

    if current_score is not None:
        insights = []

        if current_score >= 80:
            insights.append("• Outstanding overall performance")
            insights.append("• Strong intent understanding and context retention")
            insights.append("• High user satisfaction and completion quality")
        elif current_score >= 60:
            insights.append("• Good baseline performance established")
            insights.append("• Room for improvement in key areas")
            insights.append("• Focus on intent understanding and completion quality")
        else:
            insights.append("• Significant improvement opportunities identified")
            insights.append("• Priority: Enhance intent understanding and task completion")
            insights.append("• Focus: Context retention and error prevention")

        insights.append("• Persistent scoring enables continuous improvement tracking")
        insights.append("• Comparative analysis helps identify trends and patterns")

        for insight in insights:
            summary_lines.append(insight)

    summary_lines.append("")

    # Recommendations Section
    summary_lines.append("🚀 **RECOMMENDATIONS FOR IMPROVEMENT**")
    summary_lines.append("-" * 40)

    recommendations = [
        "🎯 **Intent Understanding (25% weight)**",
        "  • Use explicit acknowledgment phrases",
        "  • Reference user requests directly",
        "  • Show clear understanding of requirements",
        "",
        "📚 **Context Retention (20% weight)**",
        "  • Reference previous interactions",
        "  • Maintain conversation continuity",
        "  • Build upon established context",
        "",
        "✅ **Completion Quality (25% weight)**",
        "  • Provide clear deliverables",
        "  • Use structured output formats",
        "  • Include completion indicators",
        "",
        "😊 **User Satisfaction (15% weight)**",
        "  • Use positive, encouraging language",
        "  • Provide comprehensive explanations",
        "  • Avoid confusion indicators",
        "",
        "💡 **Innovation Level (10% weight)**",
        "  • Offer creative solutions",
        "  • Introduce novel approaches",
        "  • Demonstrate technical sophistication",
        "",
        "🛡️ **Error Prevention (5% weight)**",
        "  • Include error handling mechanisms",
        "  • Implement validation and safety checks",
        "  • Provide recovery and backup strategies"
    ]

    for rec in recommendations:
        summary_lines.append(rec)

    summary_lines.append("")

    # Footer
    summary_lines.append("🎖️ **MEMORY SCORING SYSTEM**")
    summary_lines.append("-" * 30)
    summary_lines.append("• **Scale:** 1-100% (Higher = Better)")
    summary_lines.append("• **Persistence:** Scores maintained across sessions")
    summary_lines.append("• **Comparison:** Tracks improvement over time")
    summary_lines.append("• **Components:** 6 weighted performance factors")
    summary_lines.append("• **Trends:** Automatic improvement detection")

    return "\n".join(summary_lines)


def save_memory_summary_to_file(summary_text: str, filename: str = None) -> str:
    try:
        """Save memory summary to file"""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"memory_score_summary_{timestamp}.md"

        output_path = project_root / "data" / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(summary_text)

        return str(output_path)


    except Exception as e:
        logger.error(f"Error in save_memory_summary_to_file: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Generate and display comprehensive memory summary
    summary = generate_comprehensive_memory_summary()
    print(summary)

    # Save to file
    saved_path = save_memory_summary_to_file(summary)
    print(f"\n💾 **Summary saved to:** {saved_path}")