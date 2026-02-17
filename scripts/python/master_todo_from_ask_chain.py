#!/usr/bin/env python3
"""
Master To-Do List from @ASK Chain - Full Circle Integration

Links all @asks from inception (zero ask) to Master To-Do List.
Master To-Do List is based on Master Blueprint logic.
Tracks completion status, identifies incomplete/partial items.
Uses triage to generate current priority to-do list.

Tags: #ASK #MASTER_TODO #TRIAGE #BLUEPRINT #FULL_CIRCLE @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("MasterTodoFromAskChain")


class CompletionStatus(Enum):
    """Completion status for asks/todos"""
    COMPLETED = "completed"
    IN_PROGRESS = "in_progress"
    PARTIAL = "partial"
    PENDING = "pending"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class MasterTodoFromAskChain:
    """
    Master To-Do List from @ASK Chain - Full Circle Integration

    Links all @asks from inception to Master To-Do List.
    Based on Master Blueprint logic.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Master To-Do from Ask Chain system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.intelligence_dir = self.data_dir / "intelligence"
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.master_todo_file = self.project_root / "MASTER_TODO.md"

        # Load all asks
        self.all_asks: List[Dict[str, Any]] = []
        self.master_todo_items: List[Dict[str, Any]] = []
        self.blueprint_data: Dict[str, Any] = {}

        logger.info("=" * 80)
        logger.info("🔄 MASTER TODO FROM @ASK CHAIN - FULL CIRCLE INTEGRATION")
        logger.info("=" * 80)

    def load_all_asks(self) -> List[Dict[str, Any]]:
        """Load all @asks from inception"""
        logger.info("📋 Loading all @asks from inception...")

        # Load from LUMINA_ALL_ASKS_ORDERED.json
        ordered_asks_file = self.intelligence_dir / "LUMINA_ALL_ASKS_ORDERED.json"
        if ordered_asks_file.exists():
            try:
                with open(ordered_asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    asks = data.get("asks", []) if isinstance(data, dict) else data
                    self.all_asks = asks
                    logger.info(f"   ✅ Loaded {len(asks)} @asks from ordered file")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading ordered asks: {e}")

        # Also try trace system
        if not self.all_asks:
            try:
                from trace_ask_stack_to_inception import AskStackTracer
                tracer = AskStackTracer(self.project_root)
                asks = tracer.load_all_ask_sources()
                self.all_asks = asks
                logger.info(f"   ✅ Loaded {len(asks)} @asks from trace system")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading from trace: {e}")

        logger.info(f"📊 Total @asks loaded: {len(self.all_asks)}")
        return self.all_asks

    def load_blueprint(self) -> Dict[str, Any]:
        """Load Master Blueprint"""
        logger.info("📐 Loading Master Blueprint...")

        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    self.blueprint_data = json.load(f)
                    logger.info("   ✅ Master Blueprint loaded")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading blueprint: {e}")
                self.blueprint_data = {}
        else:
            logger.warning("   ⚠️  Blueprint file not found")
            self.blueprint_data = {}

        return self.blueprint_data

    def load_master_todo(self) -> List[Dict[str, Any]]:
        """Load existing Master To-Do List"""
        logger.info("📋 Loading Master To-Do List...")

        if self.master_todo_file.exists():
            try:
                with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Parse markdown to-do items
                    items = self._parse_master_todo_markdown(content)
                    self.master_todo_items = items
                    logger.info(f"   ✅ Loaded {len(items)} items from Master To-Do")
            except Exception as e:
                logger.warning(f"   ⚠️  Error loading master todo: {e}")
                self.master_todo_items = []
        else:
            logger.warning("   ⚠️  Master To-Do file not found")
            self.master_todo_items = []

        return self.master_todo_items

    def _parse_master_todo_markdown(self, content: str) -> List[Dict[str, Any]]:
        """Parse Master To-Do markdown into structured items"""
        items = []
        lines = content.split('\n')

        current_section = None
        current_category = None

        for line in lines:
            # Section headers
            if line.startswith('##'):
                current_section = line.replace('#', '').strip()
            # Category headers
            elif line.startswith('###'):
                current_category = line.replace('#', '').strip()
            # To-do items
            elif line.strip().startswith('- [x]') or line.strip().startswith('- [ ]'):
                status = 'completed' if '[x]' in line else 'pending'
                text = line.replace('- [x]', '').replace('- [ ]', '').strip()

                # Extract priority markers
                priority = 'normal'
                if '🔴' in text or 'CRITICAL' in text.upper():
                    priority = 'critical'
                elif '🟡' in text or 'HIGH' in text.upper():
                    priority = 'high'
                elif '🟢' in text or 'LOW' in text.upper():
                    priority = 'low'

                items.append({
                    'text': text,
                    'status': status,
                    'priority': priority,
                    'section': current_section,
                    'category': current_category,
                    'source': 'master_todo'
                })

        return items

    def link_asks_to_todo(self) -> List[Dict[str, Any]]:
        """Link all @asks to Master To-Do List items"""
        logger.info("🔗 Linking @asks to Master To-Do List...")

        # Load all data
        asks = self.load_all_asks()
        todo_items = self.load_master_todo()
        blueprint = self.load_blueprint()

        # Create linked items
        linked_items = []

        # Start with asks (inception to now)
        for i, ask in enumerate(asks, 1):
            ask_text = ask.get('ask_text', ask.get('text', ''))

            # Try to match with existing todo items
            matched_todo = None
            for todo in todo_items:
                if ask_text.lower() in todo['text'].lower() or todo['text'].lower() in ask_text.lower():
                    matched_todo = todo
                    break

            # Determine completion status
            status = self._determine_ask_status(ask, matched_todo)

            linked_items.append({
                'index': i,
                'ask_id': ask.get('ask_text', '')[:50],
                'ask_text': ask_text,
                'timestamp': ask.get('timestamp', ''),
                'source': ask.get('source', 'unknown'),
                'category': ask.get('category', 'general'),
                'priority': ask.get('priority', 'normal'),
                'status': status,
                'todo_match': matched_todo['text'] if matched_todo else None,
                'blueprint_aligned': self._check_blueprint_alignment(ask, blueprint)
            })

        logger.info(f"   ✅ Linked {len(linked_items)} @asks to Master To-Do")
        return linked_items

    def _determine_ask_status(self, ask: Dict[str, Any], matched_todo: Optional[Dict[str, Any]]) -> str:
        """Determine completion status of an ask"""
        if matched_todo:
            return matched_todo.get('status', 'pending')

        # Check for completion indicators in ask text
        ask_text = str(ask.get('ask_text', ask.get('text', ''))).lower()

        if any(word in ask_text for word in ['complete', 'done', 'finished', 'implemented']):
            return 'completed'
        elif any(word in ask_text for word in ['in progress', 'working on', 'partial']):
            return 'in_progress'
        elif any(word in ask_text for word in ['blocked', 'waiting', 'pending']):
            return 'blocked'
        else:
            return 'pending'

    def _check_blueprint_alignment(self, ask: Dict[str, Any], blueprint: Dict[str, Any]) -> bool:
        """Check if ask aligns with Master Blueprint"""
        if not blueprint:
            return True  # Assume aligned if no blueprint

        ask_text = str(ask.get('ask_text', ask.get('text', ''))).lower()
        ask_category = ask.get('category', 'general')

        # Check against blueprint core systems
        core_systems = blueprint.get('core_systems', {})
        for system_name, system_data in core_systems.items():
            if system_name.lower() in ask_text or ask_category in system_name.lower():
                return True

        return True  # Default to aligned

    def generate_completion_standings(self, linked_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate completion standings report"""
        logger.info("📊 Generating completion standings...")

        total = len(linked_items)
        completed = sum(1 for item in linked_items if item['status'] == 'completed')
        in_progress = sum(1 for item in linked_items if item['status'] == 'in_progress')
        partial = sum(1 for item in linked_items if item['status'] == 'partial')
        pending = sum(1 for item in linked_items if item['status'] == 'pending')
        blocked = sum(1 for item in linked_items if item['status'] == 'blocked')

        completion_rate = (completed / total * 100) if total > 0 else 0

        standings = {
            'total': total,
            'completed': completed,
            'in_progress': in_progress,
            'partial': partial,
            'pending': pending,
            'blocked': blocked,
            'completion_rate': completion_rate,
            'by_category': defaultdict(int),
            'by_priority': defaultdict(int),
            'by_status': {
                'completed': completed,
                'in_progress': in_progress,
                'partial': partial,
                'pending': pending,
                'blocked': blocked
            }
        }

        # Breakdown by category
        for item in linked_items:
            standings['by_category'][item['category']] += 1
            standings['by_priority'][item['priority']] += 1

        logger.info(f"   ✅ Completion Rate: {completion_rate:.1f}% ({completed}/{total})")
        return standings

    def identify_incomplete_items(self, linked_items: List[Dict[str, Any]], limit: int = 15) -> List[Dict[str, Any]]:
        """Identify incomplete/partial items (next N that never got completed)"""
        logger.info(f"🔍 Identifying next {limit} incomplete/partial items...")

        incomplete = [
            item for item in linked_items
            if item['status'] in ['pending', 'partial', 'in_progress', 'blocked']
        ]

        # Sort by priority and timestamp
        incomplete.sort(key=lambda x: (
            {'critical': 0, 'high': 1, 'medium': 2, 'normal': 3, 'low': 4}.get(x['priority'], 3),
            x.get('timestamp', '')
        ))

        next_items = incomplete[:limit]
        logger.info(f"   ✅ Found {len(next_items)} next incomplete items")

        return next_items

    def triage_priority_list(self, linked_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate triaged priority list (current priority to-do list)"""
        logger.info("🎯 Generating triaged priority list...")

        # Filter incomplete items
        incomplete = [
            item for item in linked_items
            if item['status'] in ['pending', 'partial', 'in_progress', 'blocked']
        ]

        # Triage by priority, blueprint alignment, and dependencies
        triaged = sorted(incomplete, key=lambda x: (
            {'critical': 0, 'high': 1, 'medium': 2, 'normal': 3, 'low': 4}.get(x['priority'], 3),
            0 if x.get('blueprint_aligned', True) else 1,
            x.get('index', 999999)
        ))

        logger.info(f"   ✅ Triaged {len(triaged)} priority items")
        return triaged

    def generate_master_todo_report(self) -> Dict[str, Any]:
        """Generate complete Master To-Do report from @ask chain"""
        logger.info("=" * 80)
        logger.info("📋 GENERATING MASTER TODO REPORT FROM @ASK CHAIN")
        logger.info("=" * 80)

        # Link asks to todo
        linked_items = self.link_asks_to_todo()

        # Generate standings
        standings = self.generate_completion_standings(linked_items)

        # Identify incomplete items
        incomplete_items = self.identify_incomplete_items(linked_items, limit=15)

        # Generate triaged priority list
        triaged_list = self.triage_priority_list(linked_items)

        report = {
            'generated_at': datetime.now().isoformat(),
            'total_asks': len(linked_items),
            'standings': standings,
            'incomplete_items': incomplete_items,
            'triaged_priority_list': triaged_list[:50],  # Top 50 priority items
            'linked_items': linked_items
        }

        logger.info("=" * 80)
        logger.info("✅ MASTER TODO REPORT GENERATED")
        logger.info(f"   Total @asks: {standings['total']}")
        logger.info(f"   Completed: {standings['completed']} ({standings['completion_rate']:.1f}%)")
        logger.info(f"   Next Incomplete: {len(incomplete_items)}")
        logger.info(f"   Triaged Priority: {len(triaged_list)}")
        logger.info("=" * 80)

        return report

    def save_report(self, report: Dict[str, Any]) -> Path:
        try:
            """Save Master To-Do report"""
            report_dir = self.data_dir / "master_todo_reports"
            report_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = report_dir / f"master_todo_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Report saved: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def print_standings_summary(self, report: Dict[str, Any]):
        """Print standings summary"""
        standings = report['standings']

        print("\n" + "=" * 80)
        print("📊 COMPLETION STANDINGS")
        print("=" * 80)
        print(f"Total @asks: {standings['total']}")
        print(f"✅ Completed: {standings['completed']} ({standings['completion_rate']:.1f}%)")
        print(f"🔄 In Progress: {standings['in_progress']}")
        print(f"⚠️  Partial: {standings['partial']}")
        print(f"⏳ Pending: {standings['pending']}")
        print(f"🚫 Blocked: {standings['blocked']}")
        print("=" * 80)

        print("\n📋 NEXT 15 INCOMPLETE ITEMS:")
        print("-" * 80)
        for i, item in enumerate(report['incomplete_items'][:15], 1):
            status_icon = {
                'in_progress': '🔄',
                'partial': '⚠️',
                'pending': '⏳',
                'blocked': '🚫'
            }.get(item['status'], '❓')

            print(f"{i:2d}. {status_icon} [{item['priority'].upper()}] {item['ask_text'][:70]}...")

        print("\n🎯 TOP 10 TRIAGED PRIORITY ITEMS:")
        print("-" * 80)
        for i, item in enumerate(report['triaged_priority_list'][:10], 1):
            print(f"{i:2d}. [{item['priority'].upper()}] {item['ask_text'][:70]}...")

        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Master To-Do List from @ASK Chain - Full Circle Integration")
    parser.add_argument('--generate', action='store_true', help='Generate Master To-Do report')
    parser.add_argument('--save', action='store_true', help='Save report to file')
    parser.add_argument('--standings', action='store_true', help='Show completion standings')

    args = parser.parse_args()

    system = MasterTodoFromAskChain()

    if args.generate or not any([args.generate, args.standings]):
        # Default: generate report
        report = system.generate_master_todo_report()

        if args.save:
            system.save_report(report)

        if args.standings or not args.save:
            system.print_standings_summary(report)


if __name__ == "__main__":


    main()