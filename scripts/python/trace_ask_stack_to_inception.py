#!/usr/bin/env python3
"""
Trace @ASK Stack All The Way Back to Inception

"THAT'S A FACT, JACK."

Walks the entire ask stack from the most recent back to the very first @ASK
since project inception. Provides complete historical context.

Tags: #ask_stack #trace #history #inception #fact_jack
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("TraceAskStackToInception")


class AskStackTracer:
    """
    Trace @ASK Stack All The Way Back to Inception

    "THAT'S A FACT, JACK."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ask stack tracer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"

        # All ask sources
        self.ask_sources = []
        self.all_asks = []

        logger.info("=" * 80)
        logger.info("🔍 TRACING @ASK STACK TO INCEPTION")
        logger.info("   THAT'S A FACT, JACK.")
        logger.info("=" * 80)
        logger.info("")

    def load_all_ask_sources(self) -> List[Dict[str, Any]]:
        """Load all @ASK sources from all locations"""
        all_asks = []

        # Source 1: LUMINA_ALL_ASKS_ORDERED.json (primary)
        primary_file = self.project_root / "data" / "holocron" / "archives" / "000_Information_Systems" / "LUMINA_ALL_ASKS_ORDERED.json"
        if primary_file.exists():
            try:
                with open(primary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    asks = data.get("asks", []) if isinstance(data, dict) else data
                    all_asks.extend(asks)
                    logger.info(f"✅ Loaded {len(asks)} @ASKS from LUMINA_ALL_ASKS_ORDERED.json")
                    self.ask_sources.append({
                        "source": str(primary_file),
                        "count": len(asks),
                        "type": "primary"
                    })
            except Exception as e:
                logger.warning(f"⚠️  Failed to load primary file: {e}")

        # Source 2: ask_stack_analysis directory
        ask_stack_dir = self.data_dir / "ask_stack_analysis"
        if ask_stack_dir.exists():
            for file in ask_stack_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        asks = data.get("ask_stacks", []) or data.get("asks", []) or (data if isinstance(data, list) else [])
                        if asks:
                            all_asks.extend(asks)
                            logger.info(f"✅ Loaded {len(asks)} @ASKS from {file.name}")
                            self.ask_sources.append({
                                "source": str(file),
                                "count": len(asks),
                                "type": "analysis"
                            })
                except Exception as e:
                    logger.debug(f"Error loading {file}: {e}")

        # Source 3: asks directory
        asks_dir = self.data_dir / "asks"
        if asks_dir.exists():
            for file in asks_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        asks = data.get("asks", []) or (data if isinstance(data, list) else [])
                        if asks:
                            all_asks.extend(asks)
                            logger.info(f"✅ Loaded {len(asks)} @ASKS from {file.name}")
                            self.ask_sources.append({
                                "source": str(file),
                                "count": len(asks),
                                "type": "individual"
                            })
                except Exception as e:
                    logger.debug(f"Error loading {file}: {e}")

        # Source 4: agent chat sessions (may contain @ASKS)
        agent_sessions_dir = self.data_dir / "agent_chat_sessions"
        if agent_sessions_dir.exists():
            for file in agent_sessions_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        # Look for @ASK patterns in messages
                        messages = data.get("messages", []) or data.get("conversation", []) or []
                        for msg in messages:
                            content = msg.get("content", "") or msg.get("text", "") or ""
                            if "@ASK" in content or "ask" in content.lower():
                                all_asks.append({
                                    "ask_text": content[:200],
                                    "source": file.name,
                                    "timestamp": msg.get("timestamp") or data.get("timestamp"),
                                    "category": "agent_session"
                                })
                except Exception:
                    pass

        # Deduplicate by ask_text (first 100 chars)
        seen = set()
        unique_asks = []
        for ask in all_asks:
            ask_text = str(ask.get("ask_text", "") or ask.get("text", "") or ask.get("content", ""))[:100]
            if ask_text and ask_text not in seen:
                seen.add(ask_text)
                unique_asks.append(ask)

        self.all_asks = unique_asks
        logger.info("")
        logger.info(f"📋 Total unique @ASKS: {len(self.all_asks)}")
        logger.info(f"   Sources: {len(self.ask_sources)}")
        logger.info("")

        return self.all_asks

    def trace_to_inception(self) -> Dict[str, Any]:
        """Trace all @ASKS back to inception"""
        logger.info("=" * 80)
        logger.info("🔍 TRACING @ASK STACK ALL THE WAY BACK")
        logger.info("   THAT'S A FACT, JACK.")
        logger.info("=" * 80)
        logger.info("")

        # Load all asks
        asks = self.load_all_ask_sources()

        # Sort by timestamp (newest first, then walk back)
        asks_with_timestamps = []
        for ask in asks:
            timestamp = ask.get("timestamp") or ask.get("created_at") or ask.get("date")
            if isinstance(timestamp, str):
                try:
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    timestamp = None
            asks_with_timestamps.append((timestamp, ask))

        # Sort: newest first (most recent at top)
        asks_with_timestamps.sort(key=lambda x: x[0] if x[0] else datetime.min, reverse=True)

        # Group by time periods
        by_year = defaultdict(list)
        by_month = defaultdict(list)
        by_category = defaultdict(list)

        for timestamp, ask in asks_with_timestamps:
            if timestamp:
                year = timestamp.year
                month_key = f"{timestamp.year}-{timestamp.month:02d}"
                by_year[year].append((timestamp, ask))
                by_month[month_key].append((timestamp, ask))

            category = ask.get("category") or ask.get("type") or "general"
            by_category[category].append(ask)

        # Build trace report
        trace_report = {
            "trace_date": datetime.now().isoformat(),
            "total_asks": len(asks),
            "sources": self.ask_sources,
            "timeline": {
                "by_year": {str(k): len(v) for k, v in sorted(by_year.items(), reverse=True)},
                "by_month": {k: len(v) for k, v in sorted(by_month.items(), reverse=True)},
                "by_category": {k: len(v) for k, v in by_category.items()}
            },
            "chronological_trace": [
                {
                    "index": i + 1,
                    "timestamp": ts.isoformat() if ts else None,
                    "ask_text": str(ask.get("ask_text") or ask.get("text") or ask.get("content", ""))[:200],
                    "category": ask.get("category") or ask.get("type") or "general",
                    "priority": ask.get("priority") or "normal",
                    "source": ask.get("source") or "unknown"
                }
                for i, (ts, ask) in enumerate(asks_with_timestamps)
            ],
            "oldest_ask": {
                "timestamp": asks_with_timestamps[-1][0].isoformat() if asks_with_timestamps and asks_with_timestamps[-1][0] else None,
                "ask_text": str(asks_with_timestamps[-1][1].get("ask_text") or asks_with_timestamps[-1][1].get("text", ""))[:200] if asks_with_timestamps else None,
                "index": len(asks_with_timestamps)
            } if asks_with_timestamps else None,
            "newest_ask": {
                "timestamp": asks_with_timestamps[0][0].isoformat() if asks_with_timestamps and asks_with_timestamps[0][0] else None,
                "ask_text": str(asks_with_timestamps[0][1].get("ask_text") or asks_with_timestamps[0][1].get("text", ""))[:200] if asks_with_timestamps else None,
                "index": 1
            } if asks_with_timestamps else None
        }

        return trace_report

    def print_trace_report(self, report: Dict[str, Any]):
        """Print comprehensive trace report"""
        print("\n" + "=" * 80)
        print("🔍 @ASK STACK TRACE TO INCEPTION")
        print("   THAT'S A FACT, JACK.")
        print("=" * 80)
        print("")

        print(f"📊 TOTAL @ASKS: {report['total_asks']}")
        print(f"   Trace Date: {report['trace_date']}")
        print(f"   Sources: {len(report['sources'])}")
        print("")

        # Timeline
        print("📅 TIMELINE BREAKDOWN")
        print("-" * 80)
        print("\nBy Year (Newest First):")
        for year, count in list(report['timeline']['by_year'].items())[:10]:
            print(f"   {year}: {count} @ASKS")

        print("\nBy Month (Recent):")
        for month, count in list(report['timeline']['by_month'].items())[:12]:
            print(f"   {month}: {count} @ASKS")

        print("\nBy Category:")
        for category, count in sorted(report['timeline']['by_category'].items(), key=lambda x: x[1], reverse=True):
            print(f"   {category}: {count} @ASKS")
        print("")

        # Oldest and Newest
        if report.get('oldest_ask'):
            print("🏛️  OLDEST @ASK (Inception):")
            print("-" * 80)
            oldest = report['oldest_ask']
            print(f"   Index: #{oldest['index']} (First @ASK)")
            print(f"   Timestamp: {oldest['timestamp']}")
            print(f"   Text: {oldest['ask_text']}")
            print("")

        if report.get('newest_ask'):
            print("🆕 NEWEST @ASK (Most Recent):")
            print("-" * 80)
            newest = report['newest_ask']
            print(f"   Index: #{newest['index']} (Latest @ASK)")
            print(f"   Timestamp: {newest['timestamp']}")
            print(f"   Text: {newest['ask_text']}")
            print("")

        # Chronological trace (first 20 and last 20)
        print("📜 CHRONOLOGICAL TRACE (Sample)")
        print("-" * 80)
        print("\nMost Recent (Top 10):")
        for ask in report['chronological_trace'][:10]:
            print(f"   #{ask['index']:4d} [{ask['timestamp'] or 'No date'}] {ask['category']:15s} | {ask['ask_text'][:60]}...")

        if len(report['chronological_trace']) > 20:
            print(f"\n   ... ({len(report['chronological_trace']) - 20} more @ASKS) ...\n")

        print("\nOldest (Bottom 10):")
        for ask in report['chronological_trace'][-10:]:
            print(f"   #{ask['index']:4d} [{ask['timestamp'] or 'No date'}] {ask['category']:15s} | {ask['ask_text'][:60]}...")

        print("")
        print("=" * 80)
        print("✅ TRACE COMPLETE - THAT'S A FACT, JACK.")
        print("=" * 80)
        print("")

    def save_trace_report(self, report: Dict[str, Any]):
        try:
            """Save trace report to file"""
            trace_dir = self.data_dir / "ask_stack_trace"
            trace_dir.mkdir(parents=True, exist_ok=True)

            trace_file = trace_dir / f"ask_stack_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(trace_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"💾 Trace report saved: {trace_file}")
            return trace_file


        except Exception as e:
            self.logger.error(f"Error in save_trace_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Trace @ASK Stack All The Way Back to Inception")
    parser.add_argument('--trace', action='store_true', help='Trace all @ASKS to inception')
    parser.add_argument('--save', action='store_true', help='Save trace report')
    parser.add_argument('--full', action='store_true', help='Show full chronological trace')

    args = parser.parse_args()

    tracer = AskStackTracer()

    if args.trace or not any([args.trace, args.save, args.full]):
        # Default: trace
        report = tracer.trace_to_inception()
        tracer.print_trace_report(report)

        if args.save:
            tracer.save_trace_report(report)

        if args.full:
            print("\n" + "=" * 80)
            print("📜 FULL CHRONOLOGICAL TRACE (ALL @ASKS)")
            print("=" * 80)
            print("")
            for ask in report['chronological_trace']:
                print(f"#{ask['index']:4d} [{ask['timestamp'] or 'No date':19s}] {ask['category']:15s} | {ask['ask_text']}")
            print("")
            print("=" * 80)
            print("✅ FULL TRACE COMPLETE")
            print("=" * 80)
            print("")


if __name__ == "__main__":


    main()