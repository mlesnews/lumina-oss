#!/usr/bin/env python3
"""
JARVIS: Restack and Process All @ASKS

Restacks and processes all @ASKS from project beginning until today,
in proper order of precedence to form a sequential lucid storytelling
from beginning to end.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import sys

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

class ASKRestacker:
    """
    Restack and process all @ASKS in chronological order
    Create sequential lucid storytelling
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize ASK restacker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.resumed_sessions_dir = self.data_dir / "resumed_sessions"
        self.intelligence_dir = self.data_dir / "intelligence"
        self.holocron_dir = self.data_dir / "holocron"

        self.all_asks: List[Dict[str, Any]] = []
        self.ask_timeline: List[Dict[str, Any]] = []

    def discover_all_asks(self, use_cache: bool = True, show_each: bool = True) -> List[Dict[str, Any]]:
        """
        Discover all @ASKS from project beginning until today

        Sources:
        - Chat session files
        - Resume session files
        - Intelligence reports
        - TODO files
        - Documentation files
        - Code comments with @ASK

        Args:
            use_cache: If True, load from cache if available and recent
            show_each: If True, display each ask as it's discovered
        """
        print("="*80)
        print("🔍 JARVIS: Discovering All @ASKS")
        print("="*80)

        # Check cache first
        cache_file = self.project_root / "data" / "ask_cache" / "discovered_asks.json"
        cache_file.parent.mkdir(parents=True, exist_ok=True)

        if use_cache and cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    cache_time = datetime.fromisoformat(cache_data.get("cached_at", "2000-01-01"))
                    cache_age = (datetime.now() - cache_time).total_seconds()

                    # Use cache if less than 1 hour old
                    if cache_age < 3600:
                        cached_asks = cache_data.get("asks", [])
                        print(f"\n💾 Loaded {len(cached_asks)} asks from cache (age: {int(cache_age/60)}m)")
                        if show_each:
                            print("\n📋 CACHED ASKS:")
                            for idx, ask in enumerate(cached_asks, 1):
                                ask_text = ask.get("text", ask.get("ask_text", "Unknown"))[:80]
                                source = ask.get("source", "Unknown")
                                print(f"   [{idx}] {ask_text}... (from {source})")
                        self.all_asks = cached_asks
                        return cached_asks
                    else:
                        print(f"\n⏰ Cache expired (age: {int(cache_age/60)}m), rediscovering...")
            except Exception as e:
                print(f"   ⚠️  Cache load error: {e}, rediscovering...")

        # Discover fresh
        all_asks = []
        ask_count = 0

        # 1. Search resumed sessions
        print("\n📂 Searching resumed sessions...")
        if self.resumed_sessions_dir.exists():
            for session_file in self.resumed_sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                        asks = self._extract_asks_from_session(session_data, session_file)
                        for ask in asks:
                            ask_count += 1
                            all_asks.append(ask)
                            if show_each:
                                ask_text = ask.get("text", ask.get("ask_text", "Unknown"))[:80]
                                print(f"   [{ask_count}] ✨ {ask_text}... (from {session_file.name})")
                        if asks and not show_each:
                            print(f"   ✅ {session_file.name}: {len(asks)} asks found")
                except Exception as e:
                    print(f"   ⚠️  {session_file.name}: Error - {e}")

        # 2. Search intelligence files
        print("\n📊 Searching intelligence files...")
        if self.intelligence_dir.exists():
            for intel_file in self.intelligence_dir.glob("*.md"):
                asks = self._extract_asks_from_markdown(intel_file)
                for ask in asks:
                    ask_count += 1
                    all_asks.append(ask)
                    if show_each:
                        ask_text = ask.get("text", ask.get("ask_text", "Unknown"))[:80]
                        print(f"   [{ask_count}] ✨ {ask_text}... (from {intel_file.name})")
                if asks and not show_each:
                    print(f"   ✅ {intel_file.name}: {len(asks)} asks found")

        # 3. Search documentation files
        print("\n📚 Searching documentation files...")
        doc_files = [
            self.project_root / "MASTER_TODO.md",
            self.project_root / "TRIAGED_EXECUTION_PATH_FORWARD.md",
            self.project_root / "ANTHROPIC_LEARNINGS_APPLIED.md"
        ]
        for doc_file in doc_files:
            if doc_file.exists():
                asks = self._extract_asks_from_markdown(doc_file)
                for ask in asks:
                    ask_count += 1
                    all_asks.append(ask)
                    if show_each:
                        ask_text = ask.get("text", ask.get("ask_text", "Unknown"))[:80]
                        print(f"   [{ask_count}] ✨ {ask_text}... (from {doc_file.name})")
                if asks and not show_each:
                    print(f"   ✅ {doc_file.name}: {len(asks)} asks found")

        # 4. Search code files for @ASK comments
        print("\n💻 Searching code files for @ASK comments...")
        code_asks = self._extract_asks_from_code()
        for ask in code_asks:
            ask_count += 1
            all_asks.append(ask)
            if show_each:
                ask_text = ask.get("text", ask.get("ask_text", "Unknown"))[:80]
                source = ask.get("source", "code")
                print(f"   [{ask_count}] ✨ {ask_text}... (from {source})")
        if code_asks and not show_each:
            print(f"   ✅ Code files: {len(code_asks)} asks found")

        print(f"\n📊 Total @ASKS discovered: {len(all_asks)}")

        # Save to cache
        try:
            cache_data = {
                "cached_at": datetime.now().isoformat(),
                "asks": all_asks,
                "count": len(all_asks)
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            print(f"💾 Cached {len(all_asks)} asks for future use")
        except Exception as e:
            print(f"   ⚠️  Cache save error: {e}")

        self.all_asks = all_asks
        return all_asks

    def _extract_asks_from_session(self, session_data: Dict[str, Any], session_file: Path) -> List[Dict[str, Any]]:
        """Extract @ASKS from session data"""
        asks = []

        # Try different session data structures
        messages = []
        if isinstance(session_data, dict):
            if "messages" in session_data:
                messages = session_data["messages"]
            elif "conversation" in session_data:
                messages = session_data["conversation"]
            elif "chat" in session_data:
                messages = session_data["chat"]
            elif isinstance(session_data, list):
                messages = session_data

        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get("content", "") or msg.get("text", "") or msg.get("message", "")
                role = msg.get("role", "") or msg.get("type", "")

                if content and role in ["user", "human", "assistant"]:
                    ask_matches = self._find_ask_patterns(content)
                    for match in ask_matches:
                        asks.append({
                            "ask_text": match["text"],
                            "timestamp": msg.get("timestamp") or msg.get("time") or self._extract_timestamp_from_filename(session_file),
                            "source": "session",
                            "source_file": str(session_file.relative_to(self.project_root)),
                            "context": content[:200] if len(content) > 200 else content,
                            "priority": match.get("priority", "normal"),
                            "category": match.get("category", "general")
                        })

        return asks

    def _extract_asks_from_markdown(self, file_path: Path) -> List[Dict[str, Any]]:
        """Extract @ASKS from markdown files"""
        asks = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find @ASK patterns
            ask_matches = self._find_ask_patterns(content)
            for match in ask_matches:
                asks.append({
                    "ask_text": match["text"],
                    "timestamp": self._extract_timestamp_from_file(file_path),
                    "source": "documentation",
                    "source_file": str(file_path.relative_to(self.project_root)),
                    "context": self._extract_context(content, match["text"]),
                    "priority": match.get("priority", "normal"),
                    "category": match.get("category", "general")
                })
        except Exception as e:
            pass

        return asks

    def _extract_asks_from_code(self) -> List[Dict[str, Any]]:
        """Extract @ASK comments from code files"""
        asks = []

        code_dirs = [
            self.project_root / "scripts" / "python",
            self.project_root / "scripts"
        ]

        for code_dir in code_dirs:
            if not code_dir.exists():
                continue

            for code_file in code_dir.rglob("*.py"):
                try:
                    with open(code_file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    for i, line in enumerate(lines):
                        if "@ASK" in line.upper() or "@ask" in line:
                            ask_text = line.replace("#", "").replace("@ASK", "").replace("@ask", "").strip()
                            if ask_text:
                                asks.append({
                                    "ask_text": ask_text,
                                    "timestamp": self._extract_timestamp_from_file(code_file),
                                    "source": "code",
                                    "source_file": str(code_file.relative_to(self.project_root)),
                                    "line_number": i + 1,
                                    "context": "".join(lines[max(0, i-2):i+3]),
                                    "priority": "normal",
                                    "category": "code_comment"
                                })
                except Exception:
                    pass

        return asks

    def _find_ask_patterns(self, text: str) -> List[Dict[str, Any]]:
        """Find @ASK patterns in text"""
        asks = []

        # Pattern 1: Direct @ASK mentions
        pattern1 = r'@ASK[:\s]+(.+?)(?:\n|$)'
        matches1 = re.finditer(pattern1, text, re.IGNORECASE | re.MULTILINE)
        for match in matches1:
            asks.append({
                "text": match.group(1).strip(),
                "priority": self._detect_priority(match.group(1)),
                "category": self._detect_category(match.group(1))
            })

        # Pattern 2: User request patterns
        pattern2 = r'(?:please|can you|could you|i want|i need|let\'?s|we need|we want)[\s:]+(.+?)(?:\n|\.|$)'
        matches2 = re.finditer(pattern2, text, re.IGNORECASE | re.MULTILINE)
        for match in matches2:
            ask_text = match.group(1).strip()
            if len(ask_text) > 10:  # Filter out very short matches
                asks.append({
                    "text": ask_text,
                    "priority": self._detect_priority(ask_text),
                    "category": self._detect_category(ask_text)
                })

        # Pattern 3: Question patterns
        pattern3 = r'(\w+(?:\s+\w+){3,}\?)'
        matches3 = re.finditer(pattern3, text, re.IGNORECASE)
        for match in matches3:
            ask_text = match.group(1).strip()
            if any(keyword in ask_text.lower() for keyword in ["how", "what", "why", "when", "where", "can", "should", "will"]):
                asks.append({
                    "text": ask_text,
                    "priority": "normal",
                    "category": "question"
                })

        return asks

    def _detect_priority(self, text: str) -> str:
        """Detect priority from ask text"""
        text_lower = text.lower()
        if any(keyword in text_lower for keyword in ["urgent", "critical", "asap", "immediately", "now", "fix", "broken"]):
            return "high"
        elif any(keyword in text_lower for keyword in ["important", "priority", "soon"]):
            return "medium"
        else:
            return "normal"

    def _detect_category(self, text: str) -> str:
        """Detect category from ask text"""
        text_lower = text.lower()

        categories = {
            "system": ["system", "workflow", "orchestration", "architecture"],
            "intelligence": ["intelligence", "syphon", "extract", "analyze", "gather"],
            "ai": ["ai", "agent", "llm", "model", "anthropic", "claude", "gpt"],
            "development": ["develop", "create", "build", "implement", "code"],
            "analysis": ["analyze", "compare", "study", "review", "examine"],
            "fix": ["fix", "repair", "debug", "error", "bug", "issue"],
            "enhancement": ["enhance", "improve", "optimize", "upgrade"],
            "documentation": ["document", "write", "create doc", "readme"],
            "integration": ["integrate", "connect", "link", "sync"],
            "testing": ["test", "validate", "verify", "check"]
        }

        for category, keywords in categories.items():
            if any(keyword in text_lower for keyword in keywords):
                return category

        return "general"

    def _extract_timestamp_from_filename(self, file_path: Path) -> str:
        """Extract timestamp from filename"""
        # Pattern: filename_YYYYMMDD_HHMMSS.json
        pattern = r'(\d{8}_\d{6})'
        match = re.search(pattern, file_path.name)
        if match:
            return match.group(1)
        return datetime.now().isoformat()

    def _extract_timestamp_from_file(self, file_path: Path) -> str:
        """Extract timestamp from file metadata or content"""
        # Try filename first
        timestamp = self._extract_timestamp_from_filename(file_path)
        if timestamp and timestamp != datetime.now().isoformat():
            return timestamp

        # Try file modification time
        try:
            mtime = file_path.stat().st_mtime
            return datetime.fromtimestamp(mtime).isoformat()
        except:
            return datetime.now().isoformat()

    def _extract_context(self, content: str, ask_text: str) -> str:
        """Extract context around ask text"""
        idx = content.find(ask_text)
        if idx == -1:
            return content[:200] if len(content) > 200 else content

        start = max(0, idx - 100)
        end = min(len(content), idx + len(ask_text) + 100)
        return content[start:end]

    def restack_asks(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Restack asks: order by precedence and prepare for timeline

        Alias for order_asks_by_precedence for unified system compatibility
        """
        return self.order_asks_by_precedence(asks)

    def order_asks_by_precedence(self, asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Order asks by precedence:
        1. Timestamp (chronological)
        2. Priority (high > medium > normal)
        3. Category dependencies
        4. Source reliability
        """
        print("\n📋 Ordering @ASKS by precedence...")

        # Sort by timestamp
        sorted_asks = sorted(asks, key=lambda x: x.get("timestamp", ""))

        # Group by priority
        priority_order = {"high": 0, "medium": 1, "normal": 2}
        sorted_asks = sorted(sorted_asks, key=lambda x: priority_order.get(x.get("priority", "normal"), 2))

        # Apply category dependencies
        category_order = {
            "system": 0,
            "architecture": 1,
            "development": 2,
            "integration": 3,
            "intelligence": 4,
            "analysis": 5,
            "enhancement": 6,
            "fix": 7,
            "testing": 8,
            "documentation": 9,
            "general": 10
        }

        sorted_asks = sorted(sorted_asks, key=lambda x: category_order.get(x.get("category", "general"), 10))

        # Re-sort by timestamp within same priority/category
        sorted_asks = sorted(sorted_asks, key=lambda x: x.get("timestamp", ""))

        print(f"   ✅ Ordered {len(sorted_asks)} asks")

        return sorted_asks

    def create_timeline(self, restacked_asks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Create timeline from restacked asks

        Returns a timeline structure with chronological ordering and metadata
        """
        timeline = []

        for i, ask in enumerate(restacked_asks, 1):
            timeline_entry = {
                "index": i,
                "timestamp": ask.get("timestamp", ""),
                "text": ask.get("ask_text", ask.get("text", "")),
                "priority": ask.get("priority", "normal"),
                "category": ask.get("category", "general"),
                "source": ask.get("source", "unknown"),
                "context": ask.get("context", "")[:200] if ask.get("context") else "",
                "metadata": {
                    "file": ask.get("file", ""),
                    "line": ask.get("line", 0),
                    "extracted_at": datetime.now().isoformat()
                }
            }
            timeline.append(timeline_entry)

        return timeline

    def create_sequential_storytelling(self, ordered_asks: List[Dict[str, Any]]) -> str:
        """
        Create sequential lucid storytelling from beginning to end
        """
        print("\n📖 Creating sequential lucid storytelling...")

        story = []
        story.append("# 📖 LUMINA PROJECT: Sequential Storytelling from Beginning to End")
        story.append("")
        story.append("**Generated by:** JARVIS ASK Restacker")
        story.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        story.append(f"**Total @ASKS Processed:** {len(ordered_asks)}")
        story.append("")
        story.append("---")
        story.append("")
        story.append("## 🎬 The Story Begins")
        story.append("")

        # Group asks by time periods
        time_periods = self._group_by_time_periods(ordered_asks)

        chapter_num = 1
        for period, period_asks in time_periods.items():
            story.append(f"## 📅 Chapter {chapter_num}: {period}")
            story.append("")

            for i, ask in enumerate(period_asks, 1):
                ask_num = f"{chapter_num}.{i}"
                story.append(f"### {ask_num} {ask.get('category', 'General').title()} Request")
                story.append("")
                story.append(f"**@ASK:** {ask.get('ask_text', 'N/A')}")
                story.append("")
                story.append(f"**Priority:** {ask.get('priority', 'normal').upper()}")
                story.append(f"**Category:** {ask.get('category', 'general')}")
                story.append(f"**Source:** {ask.get('source', 'unknown')}")
                story.append(f"**Timestamp:** {ask.get('timestamp', 'unknown')}")
                story.append("")

                if ask.get('context'):
                    story.append("**Context:**")
                    story.append("```")
                    story.append(ask['context'][:300] + "..." if len(ask['context']) > 300 else ask['context'])
                    story.append("```")
                    story.append("")

                story.append("---")
                story.append("")

            chapter_num += 1

        story.append("## 🏁 The Story Continues")
        story.append("")
        story.append("This is a living document. The story of Lumina continues to evolve.")
        story.append("")
        story.append(f"**Last Updated:** {datetime.now().isoformat()}")

        return "\n".join(story)

    def _group_by_time_periods(self, asks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group asks by time periods"""
        periods = defaultdict(list)

        for ask in asks:
            timestamp = ask.get("timestamp", "")
            period = self._determine_time_period(timestamp)
            periods[period].append(ask)

        # Sort periods chronologically
        period_order = {
            "Project Beginning (Early Development)": 0,
            "Foundation Phase": 1,
            "Integration Phase": 2,
            "Enhancement Phase": 3,
            "Intelligence Phase": 4,
            "Current Phase": 5
        }

        sorted_periods = sorted(periods.items(), key=lambda x: period_order.get(x[0], 99))

        return dict(sorted_periods)

    def _determine_time_period(self, timestamp: str) -> str:
        """Determine time period from timestamp"""
        try:
            if isinstance(timestamp, str):
                # Try to parse ISO format
                if "T" in timestamp:
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                else:
                    # Try filename format
                    try:
                        dt = datetime.strptime(timestamp[:14], "%Y%m%d%H%M%S")
                    except:
                        return "Current Phase"
            else:
                return "Current Phase"

            # Determine period based on date
            now = datetime.now()
            days_ago = (now - dt.replace(tzinfo=None)).days

            if days_ago > 180:
                return "Project Beginning (Early Development)"
            elif days_ago > 120:
                return "Foundation Phase"
            elif days_ago > 60:
                return "Integration Phase"
            elif days_ago > 30:
                return "Enhancement Phase"
            elif days_ago > 7:
                return "Intelligence Phase"
            else:
                return "Current Phase"
        except:
            return "Current Phase"

    def process_and_save(self):
        try:
            """Main processing function"""
            print("="*80)
            print("🤖 JARVIS: Restacking All @ASKS")
            print("="*80)

            # Discover all asks
            all_asks = self.discover_all_asks()

            if not all_asks:
                print("\n⚠️  No @ASKS found. Checking alternative sources...")
                # Try to extract from summary documents
                all_asks = self._extract_from_summaries()

            # Order by precedence
            ordered_asks = self.order_asks_by_precedence(all_asks)

            # Create storytelling
            storytelling = self.create_sequential_storytelling(ordered_asks)

            # Save results
            output_dir = self.intelligence_dir
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save storytelling
            story_file = output_dir / "LUMINA_SEQUENTIAL_STORYTELLING.md"
            with open(story_file, 'w', encoding='utf-8') as f:
                f.write(storytelling)
            print(f"\n💾 Saved storytelling: {story_file.name}")

            # Save ordered asks JSON
            json_file = output_dir / "LUMINA_ALL_ASKS_ORDERED.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "total_asks": len(ordered_asks),
                        "generated_at": datetime.now().isoformat(),
                        "generated_by": "JARVIS ASK Restacker"
                    },
                    "asks": ordered_asks
                }, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved ordered asks: {json_file.name}")

            # Create summary
            summary = self._create_summary(ordered_asks)
            summary_file = output_dir / "LUMINA_ASKS_SUMMARY.md"
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(summary)
            print(f"💾 Saved summary: {summary_file.name}")

            print("\n" + "="*80)
            print("✅ JARVIS RESTACKING COMPLETE")
            print("="*80)
            print(f"\n📊 Total @ASKS Processed: {len(ordered_asks)}")
            print(f"📖 Storytelling: {story_file.name}")
            print(f"📋 Ordered Data: {json_file.name}")
            print(f"📊 Summary: {summary_file.name}")
            print("\n" + "="*80)

            # Handle large files (Chunking & Indexing)
            try:
                from holocron_large_file_handler import HolocronLargeFileHandler
                handler = HolocronLargeFileHandler(self.project_root)
                print("🧩 JARVIS: Indexing and chunking large files...")
                handler.process_large_files()
                print("✅ Large file handling complete")
            except Exception as e:
                print(f"⚠️  Large file handling skipped: {e}")

            return {
                "total_asks": len(ordered_asks),
                "story_file": str(story_file),
                "json_file": str(json_file),
                "summary_file": str(summary_file)
            }

        except Exception as e:
            self.logger.error(f"Error in process_and_save: {e}", exc_info=True)
            raise
    def _extract_from_summaries(self) -> List[Dict[str, Any]]:
        try:
            """Extract asks from summary documents"""
            asks = []

            # Extract from known summary files
            summary_files = [
                self.project_root / "MASTER_TODO.md",
                self.project_root / "ANTHROPIC_LEARNINGS_APPLIED.md"
            ]

            for summary_file in summary_files:
                if summary_file.exists():
                    asks.extend(self._extract_asks_from_markdown(summary_file))

            return asks

        except Exception as e:
            self.logger.error(f"Error in _extract_from_summaries: {e}", exc_info=True)
            raise
    def _create_summary(self, ordered_asks: List[Dict[str, Any]]) -> str:
        """Create summary of all asks"""
        summary = []
        summary.append("# 📊 LUMINA PROJECT: @ASKS Summary")
        summary.append("")
        summary.append(f"**Total @ASKS:** {len(ordered_asks)}")
        summary.append(f"**Generated:** {datetime.now().isoformat()}")
        summary.append("")
        summary.append("---")
        summary.append("")

        # Statistics
        by_priority = defaultdict(int)
        by_category = defaultdict(int)
        by_source = defaultdict(int)

        for ask in ordered_asks:
            by_priority[ask.get("priority", "normal")] += 1
            by_category[ask.get("category", "general")] += 1
            by_source[ask.get("source", "unknown")] += 1

        summary.append("## 📈 Statistics")
        summary.append("")
        summary.append("### By Priority:")
        for priority, count in sorted(by_priority.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"- **{priority.upper()}:** {count}")
        summary.append("")

        summary.append("### By Category:")
        for category, count in sorted(by_category.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"- **{category}:** {count}")
        summary.append("")

        summary.append("### By Source:")
        for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"- **{source}:** {count}")
        summary.append("")

        summary.append("---")
        summary.append("")
        summary.append("## 📋 All @ASKS (Chronological)")
        summary.append("")

        for i, ask in enumerate(ordered_asks, 1):
            summary.append(f"{i}. **{ask.get('category', 'General')}** - {ask.get('ask_text', 'N/A')[:100]}...")
            summary.append(f"   - Priority: {ask.get('priority', 'normal')}")
            summary.append(f"   - Source: {ask.get('source', 'unknown')}")
            summary.append(f"   - Timestamp: {ask.get('timestamp', 'unknown')}")
            summary.append("")

        return "\n".join(summary)

def main():
    """Main execution"""
    restacker = ASKRestacker()
    results = restacker.process_and_save()

    print(f"\n✅ Complete! Processed {results['total_asks']} @ASKS")
    print(f"📖 Storytelling: {results['story_file']}")
    print(f"📋 Data: {results['json_file']}")

if __name__ == "__main__":



    main()