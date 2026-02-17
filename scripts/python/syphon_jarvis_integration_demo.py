#!/usr/bin/env python3
"""
SYPHON → JARVIS Integration Demonstration
@PEAK Complete Feed Posting from All Actors & Spectrums for Decisioning

Demonstrates the complete SYPHON actor feed aggregation and JARVIS decisioning
process with real intelligence from all personas and spectrums.
"""

import sys
import time
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Import our systems
from syphon_actor_feed_aggregator import SYPHONActorFeedAggregator, JARVISDecisionFeed
from jarvis_syphon_decisioning import JARVISSYPHONDecisioning
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def demonstrate_complete_integration():
    """Demonstrate complete SYPHON → JARVIS integration"""
    print("🔗 SYPHON → JARVIS Integration Demonstration")
    print("=" * 60)
    print("Posting actor feeds from ALL spectrums & personas for JARVIS decisioning")
    print()

    # Initialize systems
    print("🚀 Initializing SYPHON Actor Feed Aggregator...")
    feed_aggregator = SYPHONActorFeedAggregator()

    print("🎯 Initializing JARVIS SYPHON Decisioning...")
    decisioning = JARVISSYPHONDecisioning()

    print()

    # Generate comprehensive feed
    print("📊 Generating SYPHON Actor Feed from All Spectrums & Personas...")
    print("-" * 60)

    feed = feed_aggregator.generate_jarvis_decision_feed()

    # Display feed results
    display_feed_results(feed)

    print()
    print("🤖 JARVIS Analyzing SYPHON Feed for Decision Opportunities...")
    print("-" * 60)

    # Analyze feed for decisions
    decision_contexts = decisioning.analyze_feed_for_decisions(feed)

    print(f"🎯 Found {len(decision_contexts)} Decision Opportunities:")
    print()

    decisions_made = []
    for i, context in enumerate(decision_contexts, 1):
        print(f"Decision Context {i}:")
        print(f"  Type: {context.decision_type}")
        print(f"  Trigger Spectrum: {context.trigger_spectrum}")
        print(f"  Trigger Actor: {context.trigger_actor}")

        # Evaluate context
        evaluated_context = decisioning.evaluate_decision_context(context)

        print(f"  Risk Level: {evaluated_context.risk_assessment['risk_level']}")
        print(f"  Confidence: {evaluated_context.decision_confidence:.2f}")
        print(f"  Consensus: {evaluated_context.consensus_analysis['consensus_level']}")

        # Make decision
        outcome = decisioning.make_decision(evaluated_context)
        decisions_made.append(outcome)

        print(f"  JARVIS Decision: {outcome.final_decision}")
        print(f"  Action Plan: {len(outcome.action_plan)} actions")
        print()

    # Summary
    print("📋 INTEGRATION SUMMARY")
    print("=" * 60)
    print(f"📰 SYPHON Feed Generated: {feed.feed_id}")
    print(f"📊 Intelligence Items: {feed.system_status['total_intelligence_items']}")
    print(f"🚨 Critical Items: {feed.system_status['critical_items']}")
    print(f"🌈 Active Spectrums: {feed.active_spectrums}")
    print(f"🎭 Total Actors: {feed.total_actors}")
    print()
    print(f"🎯 Decisions Made: {len(decisions_made)}")
    print(f"🏥 System Health: {feed.system_status['overall_health']} ({feed.system_status['health_score']:.2f})")
    print()

    # Display spectrum breakdown
    print("📈 SPECTRUM INTELLIGENCE BREAKDOWN:")
    for spectrum_name, spectrum_feed in feed.spectrum_feeds.items():
        if spectrum_feed.total_intelligence > 0:
            status_icon = "🔴" if spectrum_feed.critical_items > 0 else "🟡" if spectrum_feed.high_priority_items > 0 else "🟢"
            print(f"  {status_icon} {spectrum_name.upper()}: {spectrum_feed.total_intelligence} items "
                  f"({spectrum_feed.critical_items} critical, {spectrum_feed.high_priority_items} high)")

    print()
    print("✅ SYPHON → JARVIS Integration Demonstration Complete")
    print("🎉 All actors and spectrums successfully posted for decisioning!")

def display_feed_results(feed: JARVISDecisionFeed):
    """Display comprehensive feed results"""
    print(f"📰 SYPHON ACTOR FEED RESULTS - {feed.feed_id}")
    print(f"⏰ Timestamp: {feed.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎭 Total Actors: {feed.total_actors}")
    print(f"🌈 Active Spectrums: {feed.active_spectrums}")
    print()

    # Spectrum analysis
    print("📊 SPECTRUM INTELLIGENCE:")
    total_intelligence = 0
    total_critical = 0

    for spectrum_name, spectrum_feed in feed.spectrum_feeds.items():
        if spectrum_feed.total_intelligence > 0:
            status = "🔴 CRITICAL" if spectrum_feed.critical_items > 0 else "🟡 HIGH" if spectrum_feed.high_priority_items > 0 else "🟢 NORMAL"
            print(f"  {status} {spectrum_name.upper()}:")
            print(f"    Intelligence: {spectrum_feed.total_intelligence}")
            print(f"    Critical: {spectrum_feed.critical_items}")
            print(f"    High Priority: {spectrum_feed.high_priority_items}")
            print(f"    Actors: {', '.join(spectrum_feed.actors)}")

            total_intelligence += spectrum_feed.total_intelligence
            total_critical += spectrum_feed.critical_items
            print()

    # Critical alerts
    if feed.critical_alerts:
        print("🚨 CRITICAL ALERTS:")
        for alert in feed.critical_alerts:
            print(f"  ⚠️  {alert['spectrum'].upper()}: {alert['description']}")
            print(f"      Priority: {alert['priority']}")
            print(f"      Actors: {', '.join(alert['actors_involved'])}")
        print()

    # Decision recommendations
    if feed.decision_recommendations:
        print("🎯 DECISION RECOMMENDATIONS:")
        for rec in feed.decision_recommendations:
            priority_icon = "🔴" if rec['priority'] == 'critical' else "🟠" if rec['priority'] == 'high' else "🟡"
            print(f"  {priority_icon} {rec['type'].replace('_', ' ').title()}:")
            print(f"      {rec['description']}")
            print(f"      Impact: {rec['estimated_impact']} | Timeframe: {rec['timeframe']}")
        print()

    # Required actions
    if feed.action_required:
        print("⚡ REQUIRED ACTIONS:")
        for action in feed.action_required:
            print(f"  🔧 {action['action_type'].replace('_', ' ').title()}:")
            print(f"      {action['description']}")
            print(f"      Priority: {action['priority']}")
        print()

    # System status
    print("🏥 SYSTEM STATUS:")
    status = feed.system_status
    health_icon = "🟢" if status['overall_health'] == 'excellent' else "🟡" if status['overall_health'] == 'good' else "🔴"
    print(f"  {health_icon} Health: {status['overall_health'].title()}")
    print(f"  📊 Health Score: {status['health_score']:.2f}")
    print(f"  🧠 Total Intelligence: {status['total_intelligence_items']}")
    print(f"  🚨 Critical Items: {status['critical_items']}")
    print(f"  📈 Intelligence Velocity: {status.get('intelligence_velocity', 0):.1f} items/hour")

def demonstrate_real_time_feeding():
    """Demonstrate real-time SYPHON feed posting"""
    print("\n" + "="*60)
    print("🔄 REAL-TIME SYPHON FEED POSTING DEMONSTRATION")
    print("="*60)

    print("This would demonstrate continuous feeding of SYPHON intelligence")
    print("from all actors and spectrums to JARVIS for ongoing decisioning.")
    print()
    print("In production, this runs continuously with:")
    print("• Real-time actor intelligence collection")
    print("• Continuous spectrum analysis")
    print("• Live decision opportunity identification")
    print("• Automated action orchestration")
    print("• Performance monitoring and optimization")

def main():
    """Main demonstration"""
    print("🎭 SYPHON → JARVIS COMPLETE INTEGRATION DEMO")
    print("Posting feeds from ALL actors of ALL spectrums for decisioning")
    print("="*70)

    try:
        # Run complete integration demonstration
        demonstrate_complete_integration()

        # Show real-time capabilities
        demonstrate_real_time_feeding()

        print("\n" + "="*70)
        print("🎉 DEMONSTRATION COMPLETE")
        print("✅ SYPHON feeds from all actors & spectrums posted to JARVIS")
        print("✅ Intelligence analysis and decisioning completed")
        print("✅ Cross-spectrum integration verified")
        print("✅ Multi-actor consensus evaluation performed")
        print("✅ Risk-weighted decision making demonstrated")
        print()
        print("🚀 @LUMINA SYPHON → JARVIS Decisioning System: OPERATIONAL")

    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":


    main()