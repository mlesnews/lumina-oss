#!/usr/bin/env python3
"""
JARVIS Knowledge Base Enhancer
Enhances KB entries with actual answers from workflow analysis

Tags: #JARVIS #KNOWLEDGE_BASE #WORKFLOW @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISKBEnhancer")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class KnowledgeBaseEnhancer:
    """Enhance knowledge base entries with actual content"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.kb_dir = project_root / "docs" / "knowledge_base"
        self.kb_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

    def filter_workflow_questions(self, question: str) -> bool:
        """Filter to only workflow/technical questions"""
        # Filter out non-technical questions
        non_workflow_keywords = [
            "catholic", "praying", "pray", "religion", "faith",
            "made for", "sr", "sister", "father", "priest"
        ]

        question_lower = question.lower()
        for keyword in non_workflow_keywords:
            if keyword in question_lower:
                return False

        # Keep technical/workflow questions
        workflow_keywords = [
            "how", "what", "why", "when", "where",
            "error", "fix", "implement", "configure",
            "setup", "install", "deploy", "run",
            "workflow", "process", "system", "tool"
        ]

        for keyword in workflow_keywords:
            if keyword in question_lower:
                return True

        return False

    def enhance_kb_entry(self, kb_file: Path) -> bool:
        """Enhance a single KB entry"""
        if not kb_file.exists():
            return False

        content = kb_file.read_text()

        # Extract question from title
        title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        if not title_match:
            return False

        question = title_match.group(1)

        # Check if already has answer
        if "## Answer" in content and "*To be filled in" not in content:
            self.logger.debug(f"KB entry already has answer: {kb_file.name}")
            return False

        # Try to find answer in summaries
        answer = self._find_answer_in_summaries(question)

        if answer:
            # Update KB entry with answer
            updated_content = self._update_kb_with_answer(content, answer)
            kb_file.write_text(updated_content)
            self.logger.info(f"✅ Enhanced KB entry: {kb_file.name}")
            return True
        else:
            self.logger.debug(f"No answer found for: {question[:50]}...")
            return False

    def _find_answer_in_summaries(self, question: str) -> Optional[str]:
        """Try to find answer in workflow summaries"""
        # Load summaries
        summary_dirs = [
            self.project_root / "data" / "jarvis" / "summaries",
            self.project_root / "data" / "jarvis" / "workflow_analysis"
        ]

        for summary_dir in summary_dirs:
            if not summary_dir.exists():
                continue

            # Search JSON files
            for summary_file in summary_dir.glob("*.json"):
                try:
                    with open(summary_file, 'r') as f:
                        data = json.load(f)

                    # Search in content
                    content = json.dumps(data).lower()
                    question_lower = question.lower()

                    # Simple keyword matching
                    question_words = set(re.findall(r'\w+', question_lower))
                    if len(question_words) > 0:
                        # Check if any significant words match
                        matches = sum(1 for word in question_words if len(word) > 3 and word in content)
                        if matches >= 2:  # At least 2 significant words match
                            # Extract relevant section
                            answer = self._extract_relevant_section(data, question)
                            if answer:
                                return answer

                except Exception as e:
                    self.logger.debug(f"Error reading {summary_file}: {e}")

        return None

    def _extract_relevant_section(self, data: Dict[str, Any], question: str) -> Optional[str]:
        """Extract relevant section from data"""
        # Try to find answer-like content
        content_fields = ["content", "summary", "text", "description", "answer", "solution"]

        for field in content_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str) and len(value) > 50:
                    # Check if it seems like an answer
                    if any(word in value.lower() for word in ["because", "solution", "answer", "fix", "how"]):
                        return value[:500]  # Limit length

        return None

    def _update_kb_with_answer(self, content: str, answer: str) -> str:
        """Update KB content with answer"""
        # Find answer section
        answer_pattern = r'(## Answer\n\n)(.*?)(\n\n---)'

        if re.search(answer_pattern, content, re.DOTALL):
            # Replace existing answer
            replacement = f"\\1{answer}\n\n\\3"
            return re.sub(answer_pattern, replacement, content, flags=re.DOTALL)
        else:
            # Add answer section
            answer_section = f"\n## Answer\n\n{answer}\n\n---"
            # Insert before "## Related"
            if "## Related" in content:
                return content.replace("## Related", answer_section + "\n## Related")
            else:
                return content + answer_section

    def enhance_all_kb_entries(self) -> Dict[str, Any]:
        try:
            """Enhance all KB entries"""
            self.logger.info("=" * 80)
            self.logger.info("📚 JARVIS KNOWLEDGE BASE ENHANCER")
            self.logger.info("=" * 80)
            self.logger.info("")

            kb_files = list(self.kb_dir.glob("kb_*.md"))

            if not kb_files:
                self.logger.warning("⚠️  No KB entries found")
                return {"enhanced": 0, "total": 0}

            self.logger.info(f"📋 Found {len(kb_files)} KB entries")
            self.logger.info("")

            enhanced = 0
            filtered = 0

            for kb_file in kb_files:
                # Check if should filter
                content = kb_file.read_text()
                title_match = re.search(r'^# (.+)$', content, re.MULTILINE)
                if title_match:
                    question = title_match.group(1)
                    if not self.filter_workflow_questions(question):
                        self.logger.debug(f"Filtered out non-workflow question: {question[:50]}...")
                        filtered += 1
                        continue

                if self.enhance_kb_entry(kb_file):
                    enhanced += 1

            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("📊 ENHANCEMENT SUMMARY")
            self.logger.info("=" * 80)
            self.logger.info("")
            self.logger.info(f"Total KB entries: {len(kb_files)}")
            self.logger.info(f"Enhanced: {enhanced}")
            self.logger.info(f"Filtered (non-workflow): {filtered}")
            self.logger.info(f"Remaining: {len(kb_files) - enhanced - filtered}")
            self.logger.info("")

            return {
                "timestamp": datetime.now().isoformat(),
                "total": len(kb_files),
                "enhanced": enhanced,
                "filtered": filtered
            }


        except Exception as e:
            self.logger.error(f"Error in enhance_all_kb_entries: {e}", exc_info=True)
            raise
def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Knowledge Base Enhancer")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--file', type=Path, help='Enhance specific KB file')

    args = parser.parse_args()

    enhancer = KnowledgeBaseEnhancer(project_root=args.project_root or PROJECT_ROOT)

    if args.file:
        result = enhancer.enhance_kb_entry(args.file)
        return 0 if result else 1
    else:
        result = enhancer.enhance_all_kb_entries()
        return 0


if __name__ == "__main__":


    sys.exit(main())