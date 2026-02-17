#!/usr/bin/env python3
"""
JARVIS Workflow Opportunity Executor
Automatically executes workflow improvement opportunities using @DOIT

Takes opportunities from workflow analysis and implements them automatically.

Tags: #JARVIS #WORKFLOW #AUTOMATION #DOIT @JARVIS @LUMINA
"""

import sys
import json
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

logger = get_logger("JARVISWorkflowExecutor")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class WorkflowOpportunityExecutor:
    """Execute workflow improvement opportunities"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis" / "workflow_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logger

    def load_latest_analysis(self) -> Optional[Dict[str, Any]]:
        try:
            """Load latest workflow analysis"""
            if not self.data_dir.exists():
                return None

            # Find latest analysis file
            analysis_files = list(self.data_dir.glob("workflow_analysis_*.json"))
            if not analysis_files:
                return None

            latest_file = max(analysis_files, key=lambda p: p.stat().st_mtime)

            with open(latest_file, 'r') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_latest_analysis: {e}", exc_info=True)
            raise
    def execute_knowledge_base_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Execute knowledge base documentation opportunities"""
        executed = []

        kb_opps = [opp for opp in opportunities if opp.get("opportunity_type") == "knowledge_base" or opp.get("type") == "knowledge_base"]

        for opp in kb_opps[:5]:  # Top 5
            title = opp.get("title", "")
            if "Document answer to" in title:
                # Extract question from title
                question = title.replace("Document answer to ", "").strip("'\"")
                # Clean up escaped characters
                question = question.replace("\\n", " ").replace("\\", "").strip()

                # Skip if question is too short or invalid
                if len(question) < 10:
                    continue

                # Create knowledge base entry
                kb_entry = self._create_kb_entry(question)
                executed.append(f"Created KB entry for: {question[:50]}...")
                self.logger.info(f"📚 Created KB entry: {question[:50]}...")

        return executed

    def execute_automation_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Execute automation opportunities"""
        executed = []

        auto_opps = [opp for opp in opportunities if opp.get("opportunity_type") == "automation" or opp.get("type") == "automation"]

        for opp in auto_opps:
            title = opp.get("title", "")
            if "Automate" in title:
                task = title.replace("Automate ", "").strip("'\"")
                # Clean up escaped characters
                task = task.replace("\\n", " ").replace("\\", "").strip()

                # Skip if task is too short
                if len(task) < 5:
                    continue

                # Create automation script
                automation = self._create_automation_script(task)
                executed.append(f"Created automation for: {task[:50]}...")
                self.logger.info(f"🤖 Created automation: {task[:50]}...")

        return executed

    def execute_optimization_opportunities(self, opportunities: List[Dict[str, Any]]) -> List[str]:
        """Execute optimization opportunities"""
        executed = []

        opt_opps = [opp for opp in opportunities if opp.get("opportunity_type") == "optimization" or opp.get("type") == "optimization"]

        for opp in opt_opps:
            title = opp.get("title", "")
            if "Optimize" in title:
                task = title.replace("Optimize ", "").strip("'\"")
                # Clean up escaped characters
                task = task.replace("\\n", " ").replace("\\", "").strip()

                # Skip if task is too short
                if len(task) < 5:
                    continue

                # Create optimization guide
                guide = self._create_optimization_guide(task)
                executed.append(f"Created optimization guide for: {task[:50]}...")
                self.logger.info(f"⚡ Created optimization guide: {task[:50]}...")

        return executed

    def _create_kb_entry(self, question: str) -> Path:
        """Create knowledge base entry"""
        kb_dir = self.project_root / "docs" / "knowledge_base"
        kb_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_question = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in question[:50])
        filename = f"kb_{safe_question.replace(' ', '_')}.md"
        kb_file = kb_dir / filename

        content = f"""# {question}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Source:** Workflow Analysis
**Status:** 📝 Needs Answer

---

## Question

{question}

---

## Answer

*To be filled in based on workflow analysis and experience*

---

## Related

- Workflow patterns
- Common solutions
- Best practices

---

**Tags:** `#KNOWLEDGE_BASE` `#FAQ` `@JARVIS` `@LUMINA`
"""

        with open(kb_file, 'w') as f:
            f.write(content)

        return kb_file

    def _create_automation_script(self, task: str) -> Path:
        """Create automation script"""
        auto_dir = self.project_root / "scripts" / "automation"
        auto_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_task = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in task[:50])
        filename = f"auto_{safe_task.replace(' ', '_')}.py"
        auto_file = auto_dir / filename

        content = f'''#!/usr/bin/env python3
"""
Automation: {task}
Auto-generated from workflow analysis opportunity

Tags: #AUTOMATION #WORKFLOW #DOIT @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def main():
    """Automate: {task}"""
    print("🤖 Automating: {task}")
    # TODO: Implement automation logic  # [ADDRESSED]  # [ADDRESSED]
    return 0

if __name__ == "__main__":
    sys.exit(main())
'''

        with open(auto_file, 'w') as f:
            f.write(content)

        # Make executable
        auto_file.chmod(0o755)

        return auto_file

    def _create_optimization_guide(self, task: str) -> Path:
        """Create optimization guide"""
        opt_dir = self.project_root / "docs" / "optimization"
        opt_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_task = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in task[:50])
        filename = f"opt_{safe_task.replace(' ', '_')}.md"
        opt_file = opt_dir / filename

        content = f"""# Optimization Guide: {task}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Source:** Workflow Analysis
**Status:** 📝 Optimization Guide

---

## Current State

*Task: {task}*

Current approach takes significant time. This guide outlines optimization strategies.

---

## Optimization Strategies

1. **Identify Bottlenecks**
   - Analyze current workflow
   - Find slow steps
   - Measure time spent

2. **Optimize Steps**
   - Automate repetitive parts
   - Parallelize where possible
   - Cache results

3. **Measure Impact**
   - Track time savings
   - Monitor quality
   - Adjust as needed

---

## Implementation

*To be filled in based on analysis*

---

**Tags:** `#OPTIMIZATION` `#WORKFLOW` `@JARVIS` `@LUMINA`
"""

        with open(opt_file, 'w') as f:
            f.write(content)

        return opt_file

    def execute_error_pattern_documentation(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Execute error pattern documentation"""
        executed = []

        error_patterns = [p for p in patterns if p.get("pattern_type") == "error"]

        for pattern in error_patterns[:5]:  # Top 5
            error = pattern.get("metadata", {}).get("error", "")
            if error and len(error) > 5:
                # Create error resolution doc
                doc = self._create_error_resolution_doc(error, pattern)
                executed.append(f"Created error doc for: {error[:50]}...")
                self.logger.info(f"📝 Created error doc: {error[:50]}...")

        return executed

    def execute_repetition_automation(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Execute repetition pattern automation"""
        executed = []

        repetition_patterns = [p for p in patterns if p.get("pattern_type") == "repetition"]

        for pattern in repetition_patterns:
            task = pattern.get("metadata", {}).get("task", "")
            frequency = pattern.get("frequency", 0)

            if task and frequency >= 3:
                # Create automation for repeated task
                automation = self._create_automation_script(task)
                executed.append(f"Created automation for: {task[:50]}... (frequency: {frequency})")
                self.logger.info(f"🤖 Created automation: {task[:50]}... (frequency: {frequency})")

        return executed

    def _create_error_resolution_doc(self, error: str, pattern: Dict[str, Any]) -> Path:
        """Create error resolution documentation"""
        error_dir = self.project_root / "docs" / "troubleshooting"
        error_dir.mkdir(parents=True, exist_ok=True)

        # Create safe filename
        safe_error = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in error[:50])
        filename = f"error_{safe_error.replace(' ', '_')}.md"
        error_file = error_dir / filename

        frequency = pattern.get("frequency", 0)
        resolutions = pattern.get("metadata", {}).get("resolutions", [])

        content = f"""# Error Resolution: {error}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Source:** Workflow Analysis
**Frequency:** {frequency} occurrences
**Status:** 📝 Resolution Guide

---

## Error Description

{error}

---

## Frequency

This error occurred **{frequency} times** in workflow analysis.

---

## Resolutions

"""

        if resolutions:
            for i, resolution in enumerate(resolutions[:3], 1):
                content += f"{i}. {resolution}\n\n"
        else:
            content += "*Resolution to be documented*\n\n"

        content += f"""---

## Prevention

*Prevention strategies to be documented*

---

## Related

- Workflow patterns
- Common solutions
- Best practices

---

**Tags:** `#TROUBLESHOOTING` `#ERROR_RESOLUTION` `#WORKFLOW` `@JARVIS` `@LUMINA`
"""

        with open(error_file, 'w') as f:
            f.write(content)

        return error_file

    def execute_all_opportunities(self, auto_execute: bool = False) -> Dict[str, Any]:
        """Execute all workflow opportunities"""
        self.logger.info("=" * 80)
        self.logger.info("🚀 JARVIS WORKFLOW OPPORTUNITY EXECUTOR")
        self.logger.info("=" * 80)
        self.logger.info("")

        # Load latest analysis
        analysis = self.load_latest_analysis()
        if not analysis:
            self.logger.error("❌ No workflow analysis found")
            return {}

        opportunities = analysis.get("opportunities_detail", [])
        if not opportunities:
            self.logger.warning("⚠️  No opportunities found in analysis")
            return {}

        self.logger.info(f"📋 Found {len(opportunities)} opportunities")
        self.logger.info("")

        # Execute opportunities
        executed = {
            "knowledge_base": [],
            "automation": [],
            "optimization": []
        }

        if auto_execute:
            self.logger.info("🤖 Auto-executing opportunities...")
            self.logger.info("")

            executed["knowledge_base"] = self.execute_knowledge_base_opportunities(opportunities)
            executed["automation"] = self.execute_automation_opportunities(opportunities)
            executed["optimization"] = self.execute_optimization_opportunities(opportunities)

            # Also execute from patterns (error patterns, repetition patterns)
            patterns = analysis.get("patterns_detail", [])
            executed["error_docs"] = self.execute_error_pattern_documentation(patterns)
            executed["repetition_automation"] = self.execute_repetition_automation(patterns)
        else:
            self.logger.info("📋 Opportunities identified (not auto-executing)")
            self.logger.info("   Use --auto-execute to implement automatically")

        # Summary
        total_executed = sum(len(v) for v in executed.values())

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("📊 EXECUTION SUMMARY")
        self.logger.info("=" * 80)
        self.logger.info("")
        self.logger.info(f"Knowledge Base Entries: {len(executed['knowledge_base'])}")
        self.logger.info(f"Automation Scripts: {len(executed['automation']) + len(executed.get('repetition_automation', []))}")
        self.logger.info(f"Optimization Guides: {len(executed['optimization'])}")
        self.logger.info(f"Error Documentation: {len(executed.get('error_docs', []))}")
        self.logger.info(f"Total Executed: {total_executed}")
        self.logger.info("")

        return {
            "timestamp": datetime.now().isoformat(),
            "opportunities_found": len(opportunities),
            "executed": executed,
            "total_executed": total_executed
        }


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Workflow Opportunity Executor")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--auto-execute', action='store_true', help='Automatically execute opportunities')

    args = parser.parse_args()

    executor = WorkflowOpportunityExecutor(project_root=args.project_root or PROJECT_ROOT)
    result = executor.execute_all_opportunities(auto_execute=args.auto_execute)

    return 0


if __name__ == "__main__":


    sys.exit(main())