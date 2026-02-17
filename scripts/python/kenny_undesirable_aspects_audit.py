#!/usr/bin/env python3
"""
Kenny Undesirable Aspects Audit

Systematic audit of undesirable visual and behavioral aspects of Kenny.
Creates a comprehensive list and tracks fixes.

Tags: #KENNY #AUDIT #QUALITY #FIXES @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import json

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHONConfig = None
    DataSourceType = None

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@dataclass
class UndesirableAspect:
    """Single undesirable aspect"""
    category: str  # "visual" or "behavioral"
    description: str
    severity: str  # "critical", "high", "medium", "low"
    status: str = "open"  # "open", "in_progress", "fixed", "verified"
    notes: str = ""
    fix_applied: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "description": self.description,
            "severity": self.severity,
            "status": self.status,
            "notes": self.notes,
            "fix_applied": self.fix_applied
        }

class KennyUndesirableAspectsAudit:
    """Audit system for Kenny's undesirable aspects"""

    def __init__(self):
        self.aspects: List[UndesirableAspect] = []
        self.audit_file = project_root / "data" / "kenny_undesirable_aspects_audit.json"
        self._load_audit()
        if not self.aspects:
            self._create_initial_audit()

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")

    def _load_audit(self):
        """Load existing audit"""
        if self.audit_file.exists():
            try:
                with open(self.audit_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.aspects = [
                        UndesirableAspect(**item) for item in data.get('aspects', [])
                    ]
            except Exception as e:
                print(f"Could not load audit: {e}")

    def _save_audit(self):
        """Save audit to file"""
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "aspects": [aspect.to_dict() for aspect in self.aspects]
            }
            with open(self.audit_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving audit: {e}")

    def _create_initial_audit(self):
        """Create initial audit based on known issues"""

        # VISUAL ASPECTS
        self.aspects.append(UndesirableAspect(
            category="visual",
            description="Kenny appears as 'Froot Loop' ring (not filled circle)",
            severity="critical",
            status="open",
            notes="Sprite rendering creates ring appearance instead of filled circle"
        ))

        self.aspects.append(UndesirableAspect(
            category="visual",
            description="Kenny size variance (24px) indicates scaling issues",
            severity="high",
            status="open",
            notes="Size changes between frames suggest rendering inconsistency"
        ))

        # BEHAVIORAL ASPECTS
        self.aspects.append(UndesirableAspect(
            category="behavioral",
            description="Large movement jumps (966px) - 'zipping off' behavior",
            severity="critical",
            status="open",
            notes="Kenny makes huge jumps instead of smooth movement"
        ))

        self.aspects.append(UndesirableAspect(
            category="behavioral",
            description="Kenny stops moving after initial movement (stuck in corner)",
            severity="critical",
            status="open",
            notes="Movement stops after large jump, remains stationary"
        ))

        self.aspects.append(UndesirableAspect(
            category="behavioral",
            description="Average speed too fast (486 px/s) - not balanced",
            severity="high",
            status="open",
            notes="Speed should be ~5-6 px/s for balanced movement, not 486 px/s"
        ))

        self._save_audit()

    def print_audit_report(self):
        """Print audit report"""
        print("\n" + "=" * 80)
        print("📋 KENNY UNDESIRABLE ASPECTS AUDIT")
        print("=" * 80)
        print()

        visual_aspects = [a for a in self.aspects if a.category == "visual"]
        behavioral_aspects = [a for a in self.aspects if a.category == "behavioral"]

        print(f"VISUAL ASPECTS ({len(visual_aspects)}):")
        print("-" * 80)
        for aspect in visual_aspects:
            status_icon = "✅" if aspect.status == "fixed" else "❌" if aspect.status == "open" else "🔄"
            print(f"{status_icon} [{aspect.severity.upper()}] {aspect.description}")
            if aspect.notes:
                print(f"   Notes: {aspect.notes}")
            if aspect.fix_applied:
                print(f"   Fix: {aspect.fix_applied}")
            print()

        print(f"BEHAVIORAL ASPECTS ({len(behavioral_aspects)}):")
        print("-" * 80)
        for aspect in behavioral_aspects:
            status_icon = "✅" if aspect.status == "fixed" else "❌" if aspect.status == "open" else "🔄"
            print(f"{status_icon} [{aspect.severity.upper()}] {aspect.description}")
            if aspect.notes:
                print(f"   Notes: {aspect.notes}")
            if aspect.fix_applied:
                print(f"   Fix: {aspect.fix_applied}")
            print()

        # Summary
        open_count = len([a for a in self.aspects if a.status == "open"])
        fixed_count = len([a for a in self.aspects if a.status == "fixed"])
        total = len(self.aspects)

        print("=" * 80)
        print("SUMMARY:")
        print(f"  Total Aspects: {total}")
        print(f"  Open: {open_count} ❌")
        print(f"  Fixed: {fixed_count} ✅")
        print(f"  Progress: {fixed_count}/{total} ({fixed_count*100//total if total > 0 else 0}%)")
        print("=" * 80)
        print()

if __name__ == "__main__":
    audit = KennyUndesirableAspectsAudit()
    audit.print_audit_report()
