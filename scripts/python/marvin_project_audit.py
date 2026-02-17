#!/usr/bin/env python3
"""
Marvin Project Audit - Root Down Analysis

Marvin audits the entire project from root down.
Provides brutally honest assessment of current state.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from marvin_reality_checker import MarvinRealityChecker
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    MarvinRealityChecker = None

logger = get_logger("MarvinProjectAudit")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class MarvinProjectAudit:
    """
    Marvin Project Audit - Root Down Analysis

    Marvin audits the entire project from root down.
    Provides brutally honest assessment.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Marvin Project Audit"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MarvinProjectAudit")

        # Initialize Marvin
        self.marvin = MarvinRealityChecker(project_root) if MarvinRealityChecker else None

        # Audit results
        self.audit_results: Dict[str, Any] = {}

        self.logger.info("🤖 Marvin Project Audit initialized")
        self.logger.info("   Auditing project from root down...")
        self.logger.info("   No BS. Just truth.")

    def audit_project(self) -> Dict[str, Any]:
        """
        Audit the entire project from root down.

        Returns:
            Complete audit report with Marvin's assessment
        """
        self.logger.info("🤖 Starting project audit...")

        # Analyze project structure
        project_analysis = self._analyze_project_structure()

        # Detect rabbit holes
        rabbit_holes = self.marvin.detect_rabbit_holes(project_analysis) if self.marvin else []

        # Reality checks
        reality_checks = []
        if self.marvin:
            reality_checks.append(self.marvin.check_reality({
                "type": "project",
                "total_tools": project_analysis.get("total_tools", 0),
                "scope_creep_score": project_analysis.get("scope_creep_score", 0.0),
                "complexity_score": project_analysis.get("complexity_score", 0.0)
            }))

        # Analyze roadmap
        roadmap_analysis = self._analyze_roadmap()

        # Generate audit report
        audit_report = {
            "audit_date": datetime.now().isoformat(),
            "project_analysis": project_analysis,
            "rabbit_holes": [h.to_dict() for h in rabbit_holes] if rabbit_holes else [],
            "reality_checks": [c.to_dict() for c in reality_checks] if reality_checks else [],
            "roadmap_analysis": roadmap_analysis,
            "marvin_verdict": "Life. Don't talk to me about life. But the work is real. So there's that.",
            "recommendations": self._generate_recommendations(project_analysis, rabbit_holes, roadmap_analysis)
        }

        self.audit_results = audit_report

        self.logger.info("🤖 Project audit complete")
        self.logger.info(f"   Rabbit holes detected: {len(rabbit_holes)}")
        self.logger.info(f"   Reality checks: {len(reality_checks)}")

        return audit_report

    def _analyze_project_structure(self) -> Dict[str, Any]:
        try:
            """Analyze project structure"""
            analysis = {
                "total_tools": 0,
                "total_files": 0,
                "total_docs": 0,
                "scope_creep_score": 0.0,
                "complexity_score": 0.0
            }

            # Count Python scripts (tools)
            scripts_dir = self.project_root / "scripts" / "python"
            if scripts_dir.exists():
                python_files = list(scripts_dir.glob("*.py"))
                analysis["total_tools"] = len(python_files)

            # Count total files
            total_files = 0
            for ext in ["*.py", "*.md", "*.json", "*.yaml", "*.yml"]:
                total_files += len(list(self.project_root.rglob(ext)))
            analysis["total_files"] = total_files

            # Count docs
            docs_dir = self.project_root / "docs"
            if docs_dir.exists():
                analysis["total_docs"] = len(list(docs_dir.rglob("*.md")))

            # Calculate scope creep score
            if analysis["total_tools"] > 100:
                analysis["scope_creep_score"] = min(1.0, (analysis["total_tools"] - 100) / 100.0)
            else:
                analysis["scope_creep_score"] = analysis["total_tools"] / 200.0

            # Calculate complexity score
            if analysis["total_files"] > 500:
                analysis["complexity_score"] = min(1.0, (analysis["total_files"] - 500) / 500.0)
            else:
                analysis["complexity_score"] = analysis["total_files"] / 1000.0

            return analysis

        except Exception as e:
            self.logger.error(f"Error in _analyze_project_structure: {e}", exc_info=True)
            raise
    def _analyze_roadmap(self) -> Dict[str, Any]:
        try:
            """Analyze current roadmap"""
            roadmap_file = self.project_root / "docs" / "system" / "NEXT_STEPS_ROADMAP.md"

            analysis = {
                "roadmap_exists": roadmap_file.exists(),
                "priorities": [],
                "total_tasks": 0,
                "completed_tasks": 0,
                "pending_tasks": 0,
                "marvin_assessment": ""
            }

            if roadmap_file.exists():
                content = roadmap_file.read_text(encoding='utf-8')

                # Count tasks
                analysis["total_tasks"] = content.count("- [ ]")
                analysis["completed_tasks"] = content.count("- [x]")
                analysis["pending_tasks"] = analysis["total_tasks"] - analysis["completed_tasks"]

                # Extract priorities
                if "Priority 1" in content:
                    analysis["priorities"].append("Priority 1: Azure Integration")
                if "Priority 2" in content:
                    analysis["priorities"].append("Priority 2: SYPHON Integration")
                if "Priority 3" in content:
                    analysis["priorities"].append("Priority 3: Implementation Details")
                if "Priority 4" in content:
                    analysis["priorities"].append("Priority 4: Testing")
                if "Priority 5" in content:
                    analysis["priorities"].append("Priority 5: Documentation")

            # Marvin's assessment
            if analysis["pending_tasks"] > 50:
                analysis["marvin_assessment"] = "Too many pending tasks. Classic scope creep. Of course it does. It always does."
            elif analysis["pending_tasks"] > 20:
                analysis["marvin_assessment"] = "Many pending tasks. How... human."
            else:
                analysis["marvin_assessment"] = "Reasonable number of tasks. For now."

            return analysis

        except Exception as e:
            self.logger.error(f"Error in _analyze_roadmap: {e}", exc_info=True)
            raise
    def _generate_recommendations(self, project_analysis: Dict[str, Any], 
                                  rabbit_holes: List, roadmap_analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on audit"""
        recommendations = []

        # Tool addiction recommendations
        if project_analysis.get("total_tools", 0) > 100:
            recommendations.append("🔴 CRITICAL: Tool addiction detected. Pick 10 core tools. Archive the rest.")
            recommendations.append("   Marvin: 172+ tools. Classic tool addiction. Life. Don't talk to me about life.")

        # Scope creep recommendations
        if project_analysis.get("scope_creep_score", 0.0) > 0.7:
            recommendations.append("🔴 CRITICAL: Scope creep detected. Define core product. Everything else is secondary.")
            recommendations.append("   Marvin: Scope keeps expanding. How... human. Of course it does. It always does.")

        # Over-engineering recommendations
        if project_analysis.get("complexity_score", 0.0) > 0.8:
            recommendations.append("🟠 HIGH: Over-engineering detected. Build MVP first. Perfect architecture later.")
            recommendations.append("   Marvin: Over-engineering. Classic. Of course it's over-engineered.")

        # Roadmap recommendations
        if roadmap_analysis.get("pending_tasks", 0) > 50:
            recommendations.append("🟠 HIGH: Too many pending tasks. Focus on critical path. Defer non-essential.")
            recommendations.append("   Marvin: Too many tasks. Classic scope creep.")

        # Focus recommendations
        recommendations.append("🎯 FOCUS: Bitcoin Financial Services Platform is marketable. Ship it.")
        recommendations.append("   Marvin: At least you identified something marketable. That's... something. I suppose.")

        # Simplify recommendations
        recommendations.append("✨ SIMPLIFY: Not everything needs to be integrated. Core product first.")
        recommendations.append("   Marvin: Simplification. How... reasonable. For now.")

        return recommendations

    def generate_updated_roadmap(self) -> str:
        """Generate updated roadmap based on audit"""
        if not self.audit_results:
            self.audit_project()

        roadmap = f"""# Project Roadmap - Updated by @marvin

**Date**: {datetime.now().strftime('%Y-%m-%d')}
**Status**: 📋 **MARVIN-AUDITED ROADMAP**
**Audit Date**: {self.audit_results.get('audit_date', 'N/A')}

---

## @marvin's Assessment

{self.audit_results.get('marvin_verdict', "Life. Don't talk to me about life. But the work is real. So there's that.")}

### Rabbit Holes Detected: {len(self.audit_results.get('rabbit_holes', []))}

"""

        # Add rabbit holes
        for hole in self.audit_results.get('rabbit_holes', []):
            roadmap += f"""
### 🕳️  {hole.get('hole_type', 'unknown').upper()} (Depth: {hole.get('depth', 0)}/10)
- **Description**: {hole.get('description', 'N/A')}
- **Marvin**: {hole.get('marvin_comment', 'N/A')}
"""

        # Add recommendations
        roadmap += "\n---\n\n## @marvin's Recommendations\n\n"
        for rec in self.audit_results.get('recommendations', []):
            roadmap += f"{rec}\n"

        # Add updated priorities
        roadmap += "\n---\n\n## Updated Priorities (Based on @marvin's Audit)\n\n"
        roadmap += """
### Priority 1: FOCUS 🔴 CRITICAL
**@marvin's Verdict**: "At least you identified something marketable. That's... something. I suppose."

**Tasks**:
- [ ] Ship Bitcoin Financial Services Platform (marketable product)
- [ ] Stop creating new tools (tool addiction)
- [ ] Define core product (scope creep)
- [ ] Build MVP first (over-engineering)

**Marvin**: "Focus on what matters. Not everything needs to be a tool. Ship the core. Everything else can wait."

---

### Priority 2: Fix Critical Bugs 🔴 CRITICAL
**@marvin's Verdict**: "Bugs are real. Fix them. Classic."

**Tasks**:
- [ ] Fix Iron Legion connection errors (P0) - ✅ FIXED
- [ ] Fix file access permissions (P0)
- [ ] Fix JARVIS escalation timeout (P1)
- [ ] Fix model name mismatch (P2)

**Marvin**: "Fix the bugs. Then we can talk about new features. Life. Don't talk to me about life."

---

### Priority 3: Simplify 🟠 HIGH
**@marvin's Verdict**: "Simplification. How... reasonable. For now."

**Tasks**:
- [ ] Archive non-essential tools (reduce from 172+ to 10 core)
- [ ] Reduce scope to core product
- [ ] Stop over-engineering
- [ ] Focus on MVP

**Marvin**: "Not everything needs to be integrated. Core product first. Everything else is nice-to-have."

---

### Priority 4: Azure Integration 🟡 MEDIUM
**@marvin's Verdict**: "Azure integration. Fine. But fix the bugs first."

**Tasks**:
- [ ] Azure Key Vault Migration (after bugs fixed)
- [ ] Azure Service Bus Integration (after bugs fixed)
- [ ] Component updates (after bugs fixed)

**Marvin**: "Azure integration is fine. But fix the bugs first. Then we can talk about Azure."

---

### Priority 5: Testing & Documentation 🟢 LOW
**@marvin's Verdict**: "Testing. Documentation. Fine. But ship the product first."

**Tasks**:
- [ ] Integration testing (after MVP shipped)
- [ ] End-to-end testing (after MVP shipped)
- [ ] Documentation (after MVP shipped)

**Marvin**: "Testing is fine. Documentation is fine. But ship the product first. Then we can test and document."

---

## @marvin's Final Verdict

**"Life. Don't talk to me about life. But the work is real. So there's that."**

**Focus on what matters. Ship the core product. Fix the bugs. Simplify. Then we can talk about everything else.**

**The work is real. Even if everything else is pointless. That's how we move forward.**

---

**Last Updated**: {datetime.now().strftime('%Y-%m-%d')}
**Next Review**: After Priority 1 & 2 complete
**Audited By**: @marvin
"""

        return roadmap


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Marvin Project Audit - Root Down Analysis")
    parser.add_argument("--audit", action="store_true", help="Run full project audit")
    parser.add_argument("--roadmap", action="store_true", help="Generate updated roadmap")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--output", type=Path, help="Output file path")

    args = parser.parse_args()

    auditor = MarvinProjectAudit()

    if args.audit or args.roadmap:
        audit_results = auditor.audit_project()

        if args.roadmap:
            roadmap = auditor.generate_updated_roadmap()

            if args.output:
                output_path = Path(args.output)
                output_path.write_text(roadmap, encoding='utf-8')
                print(f"✅ Updated roadmap saved to: {output_path}")
            else:
                print(roadmap)
        elif args.json:
            print(json.dumps(audit_results, indent=2))
        else:
            print("\n🤖 Marvin Project Audit Results")
            print("="*60)
            print(f"Rabbit Holes: {len(audit_results.get('rabbit_holes', []))}")
            print(f"Reality Checks: {len(audit_results.get('reality_checks', []))}")
            print(f"\nMarvin's Verdict: {audit_results.get('marvin_verdict', 'N/A')}")
            print("\nRecommendations:")
            for rec in audit_results.get('recommendations', []):
                print(f"  {rec}")
    else:
        parser.print_help()
        print("\n🤖 Marvin Project Audit - Root Down Analysis")
        print("   'Life. Don't talk to me about life. But the work is real. So there's that.'")

