#!/usr/bin/env python3
"""
JARVIS SYPHON-Enhanced Troubleshooting System

Re-engineered troubleshooting module with SYPHON intelligence extraction.
Integrates proactive troubleshooting logic: pattern recognition, building blocks,
simulation, @FF automation, and SYPHON intelligence extraction.

@SYPHON #TROUBLESHOOTING #PATTERNS #PEAK #FF #INTELLIGENCE
"""

from __future__ import annotations

import sys
import json
import time
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSyphonEnhancedTroubleshooting")

# Import SYPHON system
try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.troubleshooting_extractor import TroubleshootingExtractor
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    SubscriptionTier = None
    TroubleshootingExtractor = None
    logger.warning("⚠️  SYPHON system not available")

# Import proactive troubleshooter logic
try:
    from jarvis_proactive_ide_troubleshooter import (
        JARVISProactiveIDETroubleshooter,
        ErrorPattern,
        ErrorSeverity,
        ErrorCategory,
        IDEError
    )
    PROACTIVE_TROUBLESHOOTER_AVAILABLE = True
except ImportError:
    PROACTIVE_TROUBLESHOOTER_AVAILABLE = False
    JARVISProactiveIDETroubleshooter = None
    ErrorPattern = None
    ErrorSeverity = None
    ErrorCategory = None
    IDEError = None
    logger.warning("⚠️  Proactive troubleshooter not available")

# Import universal troubleshooting
try:
    from universal_workflow_troubleshooting import (
        UniversalWorkflowTroubleshooting,
        TroubleshootingMode,
        EvaluationLevel,
        WorkflowEvaluation
    )
    UNIVERSAL_TROUBLESHOOTING_AVAILABLE = True
except ImportError:
    UNIVERSAL_TROUBLESHOOTING_AVAILABLE = False
    UniversalWorkflowTroubleshooting = None
    TroubleshootingMode = None
    EvaluationLevel = None
    WorkflowEvaluation = None
    logger.warning("⚠️  Universal troubleshooting not available")


@dataclass
class SyphonTroubleshootingResult:
    """Result of SYPHON-enhanced troubleshooting"""
    troubleshooting_id: str
    timestamp: datetime

    # Original troubleshooting data
    original_error: Dict[str, Any]
    original_evaluation: Optional[Dict[str, Any]] = None

    # Pattern recognition (#patterns)
    patterns_detected: List[Dict[str, Any]] = field(default_factory=list)
    intent_extracted: Optional[str] = None
    building_blocks: List[str] = field(default_factory=list)

    # Simulation results
    simulated_fix: Optional[Dict[str, Any]] = None
    simulation_success_rate: float = 0.0

    # Applied fix
    fix_applied: Optional[Dict[str, Any]] = None
    fix_success: bool = False

    # @FF shortcuts
    ff_shortcuts_used: List[Dict[str, Any]] = field(default_factory=list)

    # SYPHON intelligence
    syphon_data: Optional[Dict[str, Any]] = None
    actionable_intelligence: List[str] = field(default_factory=list)
    proven_patterns: List[Dict[str, Any]] = field(default_factory=list)

    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class JARVISSyphonEnhancedTroubleshooting:
    """
    JARVIS SYPHON-Enhanced Troubleshooting System

    Combines:
    - Proactive troubleshooting (pattern recognition, building blocks, simulation)
    - Universal workflow troubleshooting (roast/repair, decision-making)
    - SYPHON intelligence extraction
    - @FF keyboard shortcuts automation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON-enhanced troubleshooting"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISSyphonEnhancedTroubleshooting")

        # Initialize SYPHON system
        self.syphon = None
        self.troubleshooting_extractor = None
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True
                )
                self.syphon = SYPHONSystem(config)
                self.troubleshooting_extractor = TroubleshootingExtractor(config)
                self.syphon.register_extractor(DataSourceType.CODE, self.troubleshooting_extractor)
                self.logger.info("✅ SYPHON system initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON initialization failed: {e}")

        # Initialize proactive troubleshooter
        self.proactive_troubleshooter = None
        if PROACTIVE_TROUBLESHOOTER_AVAILABLE:
            try:
                self.proactive_troubleshooter = JARVISProactiveIDETroubleshooter(self.project_root)
                self.logger.info("✅ Proactive troubleshooter initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Proactive troubleshooter initialization failed: {e}")

        # Initialize universal troubleshooting
        self.universal_troubleshooting = None
        if UNIVERSAL_TROUBLESHOOTING_AVAILABLE:
            try:
                self.universal_troubleshooting = UniversalWorkflowTroubleshooting(self.project_root)
                self.logger.info("✅ Universal troubleshooting initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Universal troubleshooting initialization failed: {e}")

        # Data directory
        self.data_dir = self.project_root / "data" / "syphon_troubleshooting"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ JARVIS SYPHON-Enhanced Troubleshooting initialized")

    def troubleshoot_with_syphon(
        self,
        error_data: Dict[str, Any],
        mode: Optional[str] = None,
        level: Optional[str] = None,
        extract_intelligence: bool = True
    ) -> SyphonTroubleshootingResult:
        """
        Troubleshoot with SYPHON intelligence extraction

        Args:
            error_data: Error/troubleshooting data
            mode: Troubleshooting mode (pre/post/continuous/on_error)
            level: Evaluation level (basic/standard/deep/jedi_council)
            extract_intelligence: If True, extract SYPHON intelligence

        Returns:
            SyphonTroubleshootingResult with all intelligence
        """
        troubleshooting_id = error_data.get("error_id") or f"troubleshoot_{int(time.time())}"

        result = SyphonTroubleshootingResult(
            troubleshooting_id=troubleshooting_id,
            timestamp=datetime.now(),
            original_error=error_data
        )

        self.logger.info(f"🔍 Troubleshooting with SYPHON: {troubleshooting_id}")

        # 1. Pattern recognition (#patterns)
        if self.proactive_troubleshooter:
            try:
                patterns = self._detect_patterns(error_data)
                result.patterns_detected = patterns
                result.intent_extracted = self._extract_intent(error_data, patterns)
                result.building_blocks = self._extract_building_blocks(error_data, patterns)
                self.logger.info(f"✅ Detected {len(patterns)} patterns")
            except Exception as e:
                self.logger.error(f"❌ Pattern detection failed: {e}")

        # 2. Simulation
        if self.proactive_troubleshooter:
            try:
                simulation = self._simulate_fix(error_data, result.patterns_detected)
                result.simulated_fix = simulation
                result.simulation_success_rate = simulation.get("success_rate", 0.0)
                self.logger.info(f"✅ Simulation complete: {result.simulation_success_rate:.0%} success rate")
            except Exception as e:
                self.logger.error(f"❌ Simulation failed: {e}")

        # 3. Universal troubleshooting evaluation
        if self.universal_troubleshooting:
            try:
                workflow_data = {
                    "workflow_id": troubleshooting_id,
                    "workflow_name": error_data.get("error_type", "Troubleshooting"),
                    "error_data": error_data
                }

                eval_mode = TroubleshootingMode.ON_ERROR if mode is None else TroubleshootingMode[mode.upper()]
                eval_level = EvaluationLevel.STANDARD if level is None else EvaluationLevel[level.upper()]

                evaluation = self.universal_troubleshooting.evaluate_workflow(
                    workflow_data,
                    mode=eval_mode,
                    level=eval_level
                )

                result.original_evaluation = evaluation.to_dict()
                self.logger.info(f"✅ Universal evaluation complete: {evaluation.should_proceed}")
            except Exception as e:
                self.logger.error(f"❌ Universal evaluation failed: {e}")

        # 4. Apply fix (if simulation successful)
        if result.simulation_success_rate > 0.75:
            try:
                fix = self._apply_fix(error_data, result.simulated_fix)
                result.fix_applied = fix
                result.fix_success = fix.get("success", False)
                result.ff_shortcuts_used = fix.get("ff_shortcuts", [])
                self.logger.info(f"✅ Fix applied: {result.fix_success}")
            except Exception as e:
                self.logger.error(f"❌ Fix application failed: {e}")

        # 5. SYPHON intelligence extraction
        if extract_intelligence and self.troubleshooting_extractor:
            try:
                syphon_result = self.troubleshooting_extractor.extract(
                    content=result.to_dict(),
                    metadata={
                        "troubleshooting_id": troubleshooting_id,
                        "source": "jarvis_syphon_enhanced_troubleshooting"
                    }
                )

                if syphon_result.success and syphon_result.data:
                    result.syphon_data = syphon_result.data.to_dict()
                    result.actionable_intelligence = syphon_result.data.actionable_items
                    result.proven_patterns = self._extract_proven_patterns(syphon_result.data)
                    self.logger.info(f"✅ SYPHON intelligence extracted: {len(result.actionable_intelligence)} items")
            except Exception as e:
                self.logger.error(f"❌ SYPHON extraction failed: {e}")

        # Save result
        self._save_result(result)

        return result

    def _detect_patterns(self, error_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect error patterns (#patterns)"""
        if not self.proactive_troubleshooter:
            return []

        try:
            # Use proactive troubleshooter to detect errors
            errors = self.proactive_troubleshooter.detect_errors()

            patterns = []
            for error in errors:
                if error.pattern:
                    patterns.append({
                        "pattern_id": error.pattern,
                        "pattern_name": error.pattern,
                        "intent": error.intent,
                        "building_blocks": error.building_blocks,
                        "severity": error.severity.value if hasattr(error.severity, 'value') else str(error.severity),
                        "category": error.category.value if hasattr(error.category, 'value') else str(error.category)
                    })

            return patterns
        except Exception as e:
            self.logger.error(f"Pattern detection error: {e}")
            return []

    def _extract_intent(self, error_data: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Optional[str]:
        """Extract intent from patterns"""
        if not patterns:
            return None

        # Use first pattern's intent
        return patterns[0].get("intent")

    def _extract_building_blocks(self, error_data: Dict[str, Any], patterns: List[Dict[str, Any]]) -> List[str]:
        """Extract building blocks"""
        building_blocks = []

        for pattern in patterns:
            blocks = pattern.get("building_blocks", [])
            if isinstance(blocks, list):
                building_blocks.extend(blocks)

        return list(set(building_blocks))  # Remove duplicates

    def _simulate_fix(self, error_data: Dict[str, Any], patterns: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Simulate fix before applying"""
        if not self.proactive_troubleshooter or not patterns:
            return {"success": False, "success_rate": 0.0}

        try:
            # Create IDEError from error_data
            error = IDEError(
                error_id=error_data.get("error_id", ""),
                file_path=error_data.get("file_path", ""),
                line=error_data.get("line", 0),
                column=error_data.get("column", 0),
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.UNKNOWN,
                message=error_data.get("message", ""),
                pattern=patterns[0].get("pattern_id") if patterns else None
            )

            # Simulate fix
            simulation = self.proactive_troubleshooter.simulate_fix(error)

            return simulation
        except Exception as e:
            self.logger.error(f"Simulation error: {e}")
            return {"success": False, "success_rate": 0.0}

    def _apply_fix(self, error_data: Dict[str, Any], simulated_fix: Dict[str, Any]) -> Dict[str, Any]:
        """Apply fix using @FF shortcuts"""
        if not self.proactive_troubleshooter:
            return {"success": False}

        try:
            # Create IDEError
            error = IDEError(
                error_id=error_data.get("error_id", ""),
                file_path=error_data.get("file_path", ""),
                line=error_data.get("line", 0),
                column=error_data.get("column", 0),
                severity=ErrorSeverity.ERROR,
                category=ErrorCategory.UNKNOWN,
                message=error_data.get("message", "")
            )

            # Apply fix
            fix_result = self.proactive_troubleshooter.apply_fix(error, auto_apply=True)

            return {
                "success": fix_result.get("success", False),
                "ff_shortcuts": fix_result.get("ff_shortcuts", []),
                "fix_details": fix_result
            }
        except Exception as e:
            self.logger.error(f"Fix application error: {e}")
            return {"success": False, "error": str(e)}

    def _extract_proven_patterns(self, syphon_data: Any) -> List[Dict[str, Any]]:
        """Extract proven patterns from SYPHON data"""
        proven_patterns = []

        if not syphon_data:
            return proven_patterns

        # Extract from metadata
        metadata = syphon_data.metadata if hasattr(syphon_data, 'metadata') else {}
        patterns = metadata.get("patterns", [])

        for pattern in patterns:
            if pattern.get("proven") or pattern.get("success_rate", 0) > 0.75:
                proven_patterns.append(pattern)

        return proven_patterns

    def _save_result(self, result: SyphonTroubleshootingResult):
        """Save troubleshooting result"""
        try:
            result_file = self.data_dir / f"result_{result.troubleshooting_id}.json"
            with open(result_file, 'w') as f:
                json.dump(result.to_dict(), f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error saving result: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS SYPHON-Enhanced Troubleshooting")
        parser.add_argument("--error-file", type=Path, help="Error data JSON file")
        parser.add_argument("--error-json", type=str, help="Error data as JSON string")
        parser.add_argument("--mode", choices=["pre", "post", "continuous", "on_error"], default="on_error")
        parser.add_argument("--level", choices=["basic", "standard", "deep", "jedi_council"], default="standard")

        args = parser.parse_args()

        # Load error data
        error_data = {}
        if args.error_file:
            with open(args.error_file) as f:
                error_data = json.load(f)
        elif args.error_json:
            error_data = json.loads(args.error_json)
        else:
            # Default test error
            error_data = {
                "error_id": "test_001",
                "error_type": "syntax_error",
                "message": "Syntax error in file",
                "file_path": "test.py",
                "line": 10,
                "column": 5
            }

        # Initialize troubleshooter
        troubleshooter = JARVISSyphonEnhancedTroubleshooting()

        # Troubleshoot
        result = troubleshooter.troubleshoot_with_syphon(
            error_data,
            mode=args.mode,
            level=args.level
        )

        # Print result
        print("\n" + "="*80)
        print("JARVIS SYPHON-ENHANCED TROUBLESHOOTING RESULT")
        print("="*80)
        print(f"Troubleshooting ID: {result.troubleshooting_id}")
        print(f"Patterns Detected: {len(result.patterns_detected)}")
        print(f"Intent: {result.intent_extracted}")
        print(f"Building Blocks: {len(result.building_blocks)}")
        print(f"Simulation Success Rate: {result.simulation_success_rate:.0%}")
        print(f"Fix Applied: {result.fix_success}")
        print(f"@FF Shortcuts Used: {len(result.ff_shortcuts_used)}")
        print(f"Actionable Intelligence: {len(result.actionable_intelligence)}")
        print(f"Proven Patterns: {len(result.proven_patterns)}")
        print("="*80)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    exit(main())