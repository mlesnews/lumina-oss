#!/usr/bin/env python3
"""
JARVIS: Final Sequential Storytelling

Creates the final, lucid sequential storytelling from all @ASKS,
filtering out noise and focusing on the actual evolution of Lumina.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging
logger = logging.getLogger("jarvis_final_storytelling")


def create_final_storytelling(project_root: Path):
    try:
        """
        Create final sequential storytelling
        """
        print("="*80)
        print("📖 JARVIS: Creating Final Sequential Storytelling")
        print("="*80)

        intelligence_dir = project_root / "data" / "intelligence"
        ask_database = project_root / "data" / "ask_database" / "asks.json"
        ordered_asks_file = intelligence_dir / "LUMINA_ALL_ASKS_ORDERED.json"

        # Load structured asks from database
        structured_asks = []
        if ask_database.exists():
            with open(ask_database, 'r', encoding='utf-8') as f:
                ask_db = json.load(f)
                for ask_id, ask_data in ask_db.items():
                    structured_asks.append({
                        "ask_id": ask_id,
                        "ask_text": ask_data.get("ask_text", ""),
                        "timestamp": ask_data.get("submitted_at", ""),
                        "status": ask_data.get("status", ""),
                        "priority": ask_data.get("priority", "normal"),
                        "source": "ask_database",
                        "category": "structured"
                    })
            print(f"\n✅ Loaded {len(structured_asks)} structured asks from database")

        # Load ordered asks and filter out code comment noise
        session_asks = []
        if ordered_asks_file.exists():
            with open(ordered_asks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_asks = data.get("asks", [])

                # Filter: Only keep session and documentation asks, skip code comments
                for ask in all_asks:
                    source = ask.get("source", "")
                    category = ask.get("category", "")
                    ask_text = ask.get("ask_text", "")

                    # Skip code comments (too noisy)
                    if source == "code" and category == "code_comment":
                        continue

                    # Skip very short or repetitive asks
                    if len(ask_text) < 20:
                        continue

                    # Keep session and documentation asks
                    if source in ["session", "documentation"]:
                        session_asks.append(ask)

            print(f"✅ Filtered to {len(session_asks)} meaningful session/documentation asks")

        # Combine and deduplicate
        all_meaningful_asks = structured_asks + session_asks

        # Sort by timestamp
        all_meaningful_asks.sort(key=lambda x: x.get("timestamp", ""))

        print(f"\n📊 Total meaningful @ASKS: {len(all_meaningful_asks)}")

        # Create final storytelling
        final_story = create_lucid_narrative(all_meaningful_asks)

        # Save
        final_file = intelligence_dir / "LUMINA_FINAL_SEQUENTIAL_STORYTELLING.md"
        with open(final_file, 'w', encoding='utf-8') as f:
            f.write(final_story)

        print(f"\n✅ Final storytelling saved: {final_file.name}")
        print("\n" + "="*80)
        print("✅ FINAL STORYTELLING COMPLETE")
        print("="*80)

        return final_file

    except Exception as e:
        logger.error(f"Error in create_final_storytelling: {e}", exc_info=True)
        raise
def create_lucid_narrative(asks: List[Dict[str, Any]]) -> str:
    """Create lucid narrative from asks"""

    story = []
    story.append("# 📖 LUMINA: The Complete Story")
    story.append("")
    story.append("**A Sequential Narrative of Every @ASK from Project Beginning to Today**")
    story.append("")
    story.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    story.append(f"**Total @ASKS:** {len(asks)}")
    story.append("")
    story.append("---")
    story.append("")
    story.append("## 🎬 Prologue: The Vision")
    story.append("")
    story.append("Lumina began as a vision - an AI system that could understand, learn, and evolve. This is the story of that evolution, told through every @ASK, every question, every request that shaped its journey from concept to enterprise-grade platform.")
    story.append("")
    story.append("---")
    story.append("")

    # Group by evolution phases
    phases = group_by_evolution_phases(asks)

    chapter_num = 1
    for phase_name, phase_asks in phases.items():
        story.append(f"## 📚 Chapter {chapter_num}: {phase_name}")
        story.append("")
        story.append(f"*{len(phase_asks)} @ASKS in this phase*")
        story.append("")

        # Create narrative for phase
        phase_narrative = create_phase_narrative(phase_name, phase_asks)
        story.append(phase_narrative)
        story.append("")
        story.append("---")
        story.append("")

        chapter_num += 1

    story.append("## 🏁 Epilogue: The Journey Continues")
    story.append("")
    story.append("Lumina's story is not complete. Each new @ASK adds another layer, another capability, another step toward the ultimate vision. The journey continues.")
    story.append("")
    story.append(f"**Total @ASKS Processed:** {len(asks)}")
    story.append(f"**Last Updated:** {datetime.now().isoformat()}")
    story.append("")
    story.append("---")
    story.append("")
    story.append("*This is a living document. The story continues with each new @ASK.*")

    return "\n".join(story)

def group_by_evolution_phases(asks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group asks by evolution phases"""
    phases = defaultdict(list)

    for ask in asks:
        ask_text = ask.get("ask_text", "").lower()
        timestamp = ask.get("timestamp", "")

        # Determine phase based on content and timing
        phase = determine_evolution_phase(ask_text, timestamp)
        phases[phase].append(ask)

    # Sort phases chronologically
    phase_order = {
        "Foundation: The Beginning": 1,
        "Core Systems: Building the Base": 2,
        "Intelligence: SYPHON & Data Gathering": 3,
        "AI Capabilities: Agents & Models": 4,
        "Quality: Verification & Confidence": 5,
        "Integration: Connecting Everything": 6,
        "Enhancement: Optimization & Growth": 7,
        "Analysis: Learning & Understanding": 8,
        "Current: The Present": 9
    }

    sorted_phases = sorted(phases.items(), key=lambda x: (
        phase_order.get(x[0], 99),
        min((ask.get("timestamp", "") for ask in x[1]), default="")
    ))

    return dict(sorted_phases)

def determine_evolution_phase(ask_text: str, timestamp: str) -> str:
    """Determine evolution phase from ask text"""

    # Foundation
    if any(keyword in ask_text for keyword in ["beginning", "start", "foundation", "base", "initial", "first", "setup", "establish"]):
        return "Foundation: The Beginning"

    # Core Systems
    if any(keyword in ask_text for keyword in ["workflow", "orchestration", "base", "core system", "architecture", "system"]):
        return "Core Systems: Building the Base"

    # Intelligence
    if any(keyword in ask_text for keyword in ["syphon", "extract", "intelligence", "gather", "collect", "data", "email", "sms"]):
        return "Intelligence: SYPHON & Data Gathering"

    # AI Capabilities
    if any(keyword in ask_text for keyword in ["ai", "agent", "llm", "anthropic", "claude", "gpt", "model", "marvin", "jarvis"]):
        return "AI Capabilities: Agents & Models"

    # Quality
    if any(keyword in ask_text for keyword in ["fix", "bug", "error", "test", "verify", "quality", "shrink", "confidence", "hallucination", "roast"]):
        return "Quality: Verification & Confidence"

    # Integration
    if any(keyword in ask_text for keyword in ["integrate", "connect", "sync", "link", "bridge", "compatibility"]):
        return "Integration: Connecting Everything"

    # Enhancement
    if any(keyword in ask_text for keyword in ["enhance", "improve", "optimize", "upgrade", "better", "enhancement"]):
        return "Enhancement: Optimization & Growth"

    # Analysis
    if any(keyword in ask_text for keyword in ["analyze", "compare", "study", "review", "examine", "learn", "understand"]):
        return "Analysis: Learning & Understanding"

    # Default to current
    return "Current: The Present"

def create_phase_narrative(phase_name: str, phase_asks: List[Dict[str, Any]]) -> str:
    """Create narrative for a phase"""
    narrative = []

    # Sort chronologically
    sorted_asks = sorted(phase_asks, key=lambda x: x.get("timestamp", ""))

    narrative.append(f"### The {phase_name} Journey")
    narrative.append("")
    narrative.append(f"This phase represents {len(sorted_asks)} @ASKS that shaped Lumina's evolution in this area.")
    narrative.append("")

    # Show key asks (limit to most important)
    key_asks = sorted_asks[:20] if len(sorted_asks) > 20 else sorted_asks

    for i, ask in enumerate(key_asks, 1):
        ask_text = ask.get("ask_text", "N/A")
        priority = ask.get("priority", "normal")
        source = ask.get("source", "unknown")
        timestamp = ask.get("timestamp", "unknown")

        narrative.append(f"#### {i}. {ask_text[:200]}")
        narrative.append("")
        narrative.append(f"**Priority:** {priority.upper()} | **Source:** {source} | **When:** {timestamp[:10] if len(timestamp) > 10 else timestamp}")
        narrative.append("")

        if len(sorted_asks) > 20 and i == 20:
            narrative.append(f"*... and {len(sorted_asks) - 20} more @ASKS in this phase*")
            narrative.append("")
            break

    return "\n".join(narrative)

if __name__ == "__main__":
    project_root = Path(__file__).parent.parent.parent
    create_final_storytelling(project_root)

