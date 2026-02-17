#!/usr/bin/env python3
"""
Check Video Insights - Analyze what we learned from ingested videos
"""

import json
import os
from pathlib import Path
from datetime import datetime, timedelta
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def check_syphon_video_data():
    """Check SYPHON extracted data for video content"""
    syphon_file = Path('data/syphon/extracted_data.json')

    if not syphon_file.exists():
        print("❌ SYPHON data file not found")
        return []

    try:
        with open(syphon_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        print(f"📊 SYPHON Data: {len(data)} entries")

        # Look for video-related entries from today
        today = datetime.now().date()
        video_entries = []

        for entry in data:
            content = entry.get('content', '').lower()
            metadata = entry.get('metadata', {})

            # Check if it's video-related content
            is_video_content = any(keyword in content for keyword in [
                'elon musk', 'video', 'youtube', 'argument', 'psychosis', 'llm',
                'macrohard', 'ai-first', 'alternative to microsoft', 'navier-stokes',
                'post-scarcity', 'universal high income', 'abundance'
            ])

            # Check if it's recent (today or yesterday)
            entry_date = None
            if 'extracted_at' in entry:
                try:
                    extracted_at = entry['extracted_at']
                    if isinstance(extracted_at, str):
                        entry_date = datetime.fromisoformat(extracted_at.replace('Z', '+00:00')).date()
                    else:
                        entry_date = datetime.fromtimestamp(extracted_at).date()
                except:
                    pass

            is_recent = entry_date and (today - entry_date).days <= 1

            if is_video_content or is_recent:
                video_entries.append(entry)

        print(f"🎥 Video/recent entries: {len(video_entries)}")

        # Extract insights from video entries
        insights = []
        for entry in video_entries:
            content = entry.get('content', '')

            # Extract actionable items, tasks, intelligence
            actionable = entry.get('metadata', {}).get('actionable_items', [])
            tasks = entry.get('metadata', {}).get('tasks', [])
            intelligence = entry.get('metadata', {}).get('intelligence', [])

            insights.append({
                'data_id': entry.get('data_id', 'unknown'),
                'content_preview': content[:300] + '...' if len(content) > 300 else content,
                'actionable_items': actionable,
                'tasks': tasks,
                'intelligence': intelligence,
                'source': entry.get('source_type', 'unknown')
            })

        return insights

    except Exception as e:
        print(f"❌ Error reading SYPHON data: {e}")
        return []

def check_r5_video_sessions():
    """Check R5 matrix for video-related sessions"""
    r5_file = Path('data/r5_living_matrix/LIVING_CONTEXT_MATRIX_PROMPT.md')

    if not r5_file.exists():
        print("❌ R5 matrix file not found")
        return []

    try:
        with open(r5_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Look for video-related content
        video_keywords = ['elon', 'musk', 'video', 'psychosis', 'llm', 'macrohard', 'post-scarcity']
        video_lines = []

        for line in content.split('\n'):
            if any(keyword.lower() in line.lower() for keyword in video_keywords):
                video_lines.append(line.strip())

        return video_lines[:10]  # Return first 10 matches

    except Exception as e:
        print(f"❌ Error reading R5 matrix: {e}")
        return []

def extract_key_insights():
    """Extract key insights from video content"""
    print("\n🔍 EXTRACTING KEY INSIGHTS FROM INGESTED VIDEOS")
    print("=" * 60)

    # Get SYPHON video data
    syphon_insights = check_syphon_video_data()

    # Get R5 video sessions
    r5_insights = check_r5_video_sessions()

    # Analyze and categorize insights
    print(f"\n📊 ANALYSIS RESULTS")
    print(f"SYPHON Video Entries: {len(syphon_insights)}")
    print(f"R5 Video References: {len(r5_insights)}")

    # Categorize insights
    insights_by_category = {
        'economic_philosophy': [],
        'ai_safety': [],
        'technical_innovation': [],
        'human_nature': [],
        'system_design': []
    }

    # Process SYPHON insights
    for insight in syphon_insights:
        content = insight['content_preview'].lower()

        if any(term in content for term in ['universal high income', 'post-scarcity', 'abundance', 'money', 'economy']):
            insights_by_category['economic_philosophy'].append(insight)

        if any(term in content for term in ['psychosis', 'llm', 'ai safety', 'overconfidence']):
            insights_by_category['ai_safety'].append(insight)

        if any(term in content for term in ['macrohard', 'ai-first', 'microsoft alternative']):
            insights_by_category['technical_innovation'].append(insight)

        if any(term in content for term in ['human nature', 'competition', 'status', 'drive']):
            insights_by_category['human_nature'].append(insight)

        if any(term in content for term in ['system', 'architecture', 'design', 'orchestration']):
            insights_by_category['system_design'].append(insight)

    # Display categorized insights
    for category, insights in insights_by_category.items():
        if insights:
            print(f"\n🎯 {category.upper().replace('_', ' ')} ({len(insights)} insights)")
            print("-" * 50)

            for i, insight in enumerate(insights[:3], 1):  # Show top 3 per category
                print(f"{i}. {insight['content_preview'][:150]}...")

                if insight['actionable_items']:
                    print(f"   💡 Actionable: {len(insight['actionable_items'])} items")

                if insight['intelligence']:
                    print(f"   🧠 Intelligence: {len(insight['intelligence'])} points")

    # Show R5 insights
    if r5_insights:
        print(f"\n🧠 R5 MATRIX VIDEO INSIGHTS")
        print("-" * 50)
        for line in r5_insights:
            print(f"• {line}")

def generate_spark_applications():
    """Generate @SPARK-worthy applications for @LUMINA"""
    print("\n" * 2)
    print("⚡ @SPARK-WORTHY APPLICATIONS FOR @LUMINA")
    print("=" * 60)

    spark_applications = [
        {
            'title': 'Post-Scarcity Economic Modeling',
            'description': 'Implement universal basic compute as foundation for abundance economics',
            'lumina_application': 'R5 matrix could model post-scarcity resource allocation',
            'spark_potential': 'HIGH - Revolutionary economic paradigm shift'
        },
        {
            'title': 'Anti-LLM Psychosis Safeguards',
            'description': 'Confidence capping and adversarial verification prevent AI over-reliance',
            'lumina_application': '@MARVIN verification with confidence limits and peer review requirements',
            'spark_potential': 'CRITICAL - Prevents catastrophic AI-induced decision failures'
        },
        {
            'title': 'Human Nature Integration',
            'description': 'Competition persists in abundance - status replaces survival drives',
            'lumina_application': 'JARVIS gamification and achievement systems for sustained engagement',
            'spark_potential': 'HIGH - Addresses fundamental human motivation psychology'
        },
        {
            'title': 'AI-First Architecture',
            'description': 'Macrohard vision: AI as core engineering team, not just augmentation',
            'lumina_application': '@PEAK optimization where AI drives architecture decisions',
            'spark_potential': 'REVOLUTIONARY - Complete paradigm shift in AI-human collaboration'
        },
        {
            'title': 'Property Rights Evolution',
            'description': 'Location and authenticity become scarce in teleportation era',
            'lumina_application': 'Digital scarcity models for virtual assets and AI-generated content',
            'spark_potential': 'HIGH - New economic models for digital property'
        }
    ]

    for i, app in enumerate(spark_applications, 1):
        print(f"\n{i}. 🚀 {app['title']}")
        print(f"   📝 {app['description']}")
        print(f"   🤖 Lumina Application: {app['lumina_application']}")
        print(f"   ⚡ Spark Potential: {app['spark_potential']}")

def main():
    """Main analysis"""
    print("🎥 VIDEO INSIGHTS ANALYSIS")
    print("What we learned from today's video ingestion")
    print("=" * 60)

    extract_key_insights()
    generate_spark_applications()

    print("\n" * 2)
    print("🎉 ANALYSIS COMPLETE")
    print("Videos processed and insights extracted for @LUMINA optimization")

if __name__ == "__main__":


    main()