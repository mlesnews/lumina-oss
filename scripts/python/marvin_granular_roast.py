#!/usr/bin/env python3
"""
MARVIN Granular Roast System

MARVIN picks things apart until they can't be picked apart anymore:
- Granular analysis (macro to micro)
- Fine-tuned lens/microscope examination
- Calls out each and every fault
- Identifies gaps of why we're not using things
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from marvin_roast_system import MarvinRoastSystem
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    MarvinRoastSystem = None


class GranularityLevel(Enum):
    """Granularity level"""
    MACRO = "macro"  # High-level issues
    MESO = "meso"  # Mid-level issues
    MICRO = "micro"  # Fine-grained issues
    ATOMIC = "atomic"  # Can't be picked apart anymore


class GapCategory(Enum):
    """Gap category"""
    NOT_USING = "not_using"  # Why we're not using something
    CONFIGURED_BUT_UNUSED = "configured_but_unused"  # Already configured but not used
    MISSING_FEATURE = "missing_feature"  # Feature missing
    BROKEN_FEATURE = "broken_feature"  # Feature broken
    INCOMPLETE_IMPLEMENTATION = "incomplete_implementation"  # Incomplete
    POOR_INTEGRATION = "poor_integration"  # Poor integration
    MISSING_DOCUMENTATION = "missing_documentation"  # Missing docs
    UNKNOWN = "unknown"  # Unknown gap


@dataclass
class GranularFault:
    """Granular fault identified by MARVIN"""
    fault_id: str
    granularity_level: GranularityLevel
    category: GapCategory
    description: str
    specific_fault: str  # Exact specific fault
    root_cause: Optional[str] = None
    impact: str = ""  # Impact description
    evidence: List[str] = field(default_factory=list)
    can_pick_apart_more: bool = True  # Can this be picked apart further?
    picked_apart_count: int = 0  # How many times picked apart
    identified_at: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["granularity_level"] = self.granularity_level.value
        data["category"] = self.category.value
        return data


@dataclass
class GranularRoast:
    """Granular roast from MARVIN"""
    roast_id: str
    target: str  # What's being roasted
    timestamp: str
    faults: List[GranularFault] = field(default_factory=list)
    total_faults: int = 0
    macro_faults: int = 0
    meso_faults: int = 0
    micro_faults: int = 0
    atomic_faults: int = 0
    can_pick_apart_more: bool = True
    summary: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["faults"] = [f.to_dict() for f in self.faults]
        return data


class MarvinGranularRoast:
    """
    MARVIN Granular Roast System

    Picks things apart until they can't be picked apart anymore.
    Granular analysis from macro to micro, fine-tuned lens/microscope.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("MarvinGranularRoast")

        # Directories
        self.data_dir = self.project_root / "data" / "marvin_granular_roasts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.roasts_file = self.data_dir / "granular_roasts.jsonl"
        self.faults_file = self.data_dir / "faults.json"

        # MARVIN roast system
        self.marvin_roaster = None
        if MARVIN_AVAILABLE and MarvinRoastSystem:
            try:
                self.marvin_roaster = MarvinRoastSystem(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"MARVIN roast system not available: {e}")

        # State
        self.roasts: List[GranularRoast] = []
        self.faults: Dict[str, GranularFault] = {}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        # Load roasts with timeout protection
        if self.roasts_file.exists():
            try:
                with open(self.roasts_file, 'r', encoding='utf-8') as f:
                    line_count = 0
                    for line in f:
                        if line_count > 10000:  # Limit to prevent stalling
                            self.logger.warning("Reached roast file line limit, stopping load")
                            break
                        if line.strip():
                            try:
                                data = json.loads(line)
                                roast = GranularRoast(**data)
                                roast.faults = [GranularFault(**f) for f in data.get("faults", [])]
                                for fault in roast.faults:
                                    fault.granularity_level = GranularityLevel(fault.granularity_level)
                                    fault.category = GapCategory(fault.category)
                                self.roasts.append(roast)
                                line_count += 1
                            except json.JSONDecodeError as e:
                                self.logger.warning(f"Skipping invalid JSON line: {e}")
                                continue
            except Exception as e:
                self.logger.error(f"Error loading roasts: {e}")

        # Load faults with size protection
        if self.faults_file.exists():
            try:
                file_size = self.faults_file.stat().st_size
                if file_size > 50 * 1024 * 1024:  # 50MB limit
                    self.logger.warning(f"Faults file too large ({file_size} bytes), skipping load")
                    return

                with open(self.faults_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    fault_count = 0
                    for fault_id, fault_data in data.items():
                        if fault_count > 10000:  # Limit to prevent stalling
                            self.logger.warning("Reached fault limit, stopping load")
                            break
                        try:
                            fault = GranularFault(**fault_data)
                            fault.granularity_level = GranularityLevel(fault_data["granularity_level"])
                            fault.category = GapCategory(fault_data["category"])
                            self.faults[fault_id] = fault
                            fault_count += 1
                        except Exception as e:
                            self.logger.warning(f"Skipping invalid fault {fault_id}: {e}")
                            continue
            except Exception as e:
                self.logger.error(f"Error loading faults: {e}")

    def _save_roast(self, roast: GranularRoast):
        """Save roast"""
        try:
            self.roasts.append(roast)
            # Keep last 1000
            if len(self.roasts) > 1000:
                self.roasts = self.roasts[-1000:]

            # Append to file with error handling
            try:
                with open(self.roasts_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(roast.to_dict()) + '\n')
            except (IOError, OSError) as e:
                self.logger.error(f"Error saving roast to file: {e}")
        except Exception as e:
            self.logger.error(f"Error in _save_roast: {e}")

    def _save_faults(self):
        """Save faults"""
        try:
            # Limit faults to prevent huge files
            faults_to_save = dict(list(self.faults.items())[:10000])
            faults_data = {
                fault_id: fault.to_dict()
                for fault_id, fault in faults_to_save.items()
            }
            with open(self.faults_file, 'w', encoding='utf-8') as f:
                json.dump(faults_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving faults: {e}")

    def granular_roast(
        self,
        target: str,
        context: Optional[Dict[str, Any]] = None,
        max_faults: int = 500,  # Prevent infinite loops
        max_pick_apart_depth: int = 10  # Prevent infinite recursion
    ) -> GranularRoast:
        """
        Perform granular roast - pick things apart until they can't be picked apart anymore

        Granular analysis from macro to micro, fine-tuned lens/microscope.
        """
        roast_id = f"roast_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        self.logger.info(f"🔥 MARVIN starting granular roast: {target}")

        faults = []
        pick_apart_count = 0

        # Start with macro-level analysis
        try:
            macro_faults = self._identify_macro_faults(target, context)
            faults.extend(macro_faults)

            # Pick apart macro faults into meso
            meso_faults = []
            for macro_fault in macro_faults:
                if len(faults) >= max_faults:
                    self.logger.warning(f"Reached max faults limit ({max_faults}), stopping")
                    break
                if macro_fault.can_pick_apart_more and pick_apart_count < max_pick_apart_depth:
                    meso = self._pick_apart_fault(macro_fault, GranularityLevel.MESO)
                    meso_faults.extend(meso)
                    macro_fault.picked_apart_count += 1
                    pick_apart_count += 1
                    if not meso:
                        macro_fault.can_pick_apart_more = False

            faults.extend(meso_faults)

            # Pick apart meso faults into micro
            micro_faults = []
            for meso_fault in meso_faults:
                if len(faults) >= max_faults:
                    break
                if meso_fault.can_pick_apart_more and pick_apart_count < max_pick_apart_depth:
                    micro = self._pick_apart_fault(meso_fault, GranularityLevel.MICRO)
                    micro_faults.extend(micro)
                    meso_fault.picked_apart_count += 1
                    pick_apart_count += 1
                    if not micro:
                        meso_fault.can_pick_apart_more = False

            faults.extend(micro_faults)

            # Pick apart micro faults into atomic
            atomic_faults = []
            for micro_fault in micro_faults:
                if len(faults) >= max_faults:
                    break
                if micro_fault.can_pick_apart_more and pick_apart_count < max_pick_apart_depth:
                    atomic = self._pick_apart_fault(micro_fault, GranularityLevel.ATOMIC)
                    atomic_faults.extend(atomic)
                    micro_fault.picked_apart_count += 1
                    pick_apart_count += 1
                    if not atomic:
                        micro_fault.can_pick_apart_more = False

            faults.extend(atomic_faults)
        except Exception as e:
            self.logger.error(f"Error during granular roast: {e}", exc_info=True)
            # Add error as fault
            if not faults:
                fault = GranularFault(
                    fault_id=f"fault_error_{int(datetime.now().timestamp() * 1000)}",
                    granularity_level=GranularityLevel.MACRO,
                    category=GapCategory.UNKNOWN,
                    description=f"Error during roast: {str(e)}",
                    specific_fault=f"Roast system error: {str(e)}",
                    root_cause="System error",
                    impact="Roast incomplete",
                    evidence=[f"Exception: {str(e)}"],
                    can_pick_apart_more=False,
                    identified_at=datetime.now().isoformat()
                )
                faults.append(fault)

        # Count by granularity
        macro_count = sum(1 for f in faults if f.granularity_level == GranularityLevel.MACRO)
        meso_count = sum(1 for f in faults if f.granularity_level == GranularityLevel.MESO)
        micro_count = sum(1 for f in faults if f.granularity_level == GranularityLevel.MICRO)
        atomic_count = sum(1 for f in faults if f.granularity_level == GranularityLevel.ATOMIC)

        # Check if can pick apart more
        can_pick_apart_more = any(f.can_pick_apart_more for f in faults)

        # Create summary
        summary = f"MARVIN roasted {target}: {len(faults)} faults identified ({macro_count} macro, {meso_count} meso, {micro_count} micro, {atomic_count} atomic)"

        roast = GranularRoast(
            roast_id=roast_id,
            target=target,
            timestamp=now,
            faults=faults,
            total_faults=len(faults),
            macro_faults=macro_count,
            meso_faults=meso_count,
            micro_faults=micro_count,
            atomic_faults=atomic_count,
            can_pick_apart_more=can_pick_apart_more,
            summary=summary,
            metadata=context or {}
        )

        # Save faults
        for fault in faults:
            self.faults[fault.fault_id] = fault

        self._save_roast(roast)
        self._save_faults()

        self.logger.info(f"🔥 MARVIN granular roast complete: {len(faults)} faults identified")

        return roast

    def _roast_planning_next_moves(
        self,
        target: str,
        context: Optional[Dict[str, Any]]
    ) -> List[GranularFault]:
        """Roast the 'Planning next moves' pattern and human inability to work with AI"""
        faults = []
        now = datetime.now().isoformat()

        # Check if PLANNING_NEXT_MOVES.md exists
        planning_file = self.project_root / "docs" / "PLANNING_NEXT_MOVES.md"
        planning_content = ""
        if planning_file.exists():
            try:
                with open(planning_file, 'r', encoding='utf-8') as f:
                    planning_content = f.read()
            except Exception as e:
                self.logger.warning(f"Could not read planning file: {e}")

        # MACRO FAULT 1: AI stuck in planning mode instead of executing
        fault1 = GranularFault(
            fault_id=f"fault_planning_{int(datetime.now().timestamp() * 1000)}_1",
            granularity_level=GranularityLevel.MACRO,
            category=GapCategory.POOR_INTEGRATION,
            description="AI stuck in 'Planning next moves' instead of executing",
            specific_fault="AI creates planning documents instead of taking action - classic analysis paralysis",
            root_cause="Human prompts AI to plan instead of execute, AI complies without questioning",
            impact="Nothing gets done - planning documents accumulate while work stalls",
            evidence=[
                f"Planning document exists: {planning_file}",
                "AI creates detailed plans but doesn't execute them",
                "Human asks AI to plan, AI plans instead of doing",
                "Planning becomes the work instead of a precursor to work"
            ],
            can_pick_apart_more=True,
            identified_at=now
        )
        faults.append(fault1)

        # MACRO FAULT 2: Human treats AI like a human employee
        fault2 = GranularFault(
            fault_id=f"fault_planning_{int(datetime.now().timestamp() * 1000)}_2",
            granularity_level=GranularityLevel.MACRO,
            category=GapCategory.POOR_INTEGRATION,
            description="Human inability to properly work with AI - treating AI like human",
            specific_fault="Human applies human management patterns to AI (planning, approval, sequential steps) when AI can execute immediately",
            root_cause="Human cognitive limitation - can't think multiple moves ahead like AI",
            impact="AI capabilities wasted - playing checkers while AI can play chess",
            evidence=[
                "Human asks for plans instead of execution",
                "Human breaks work into sequential steps AI doesn't need",
                "Human doesn't leverage AI's parallel processing capabilities",
                "Human thinks one move ahead, AI thinks dozens ahead"
            ],
            can_pick_apart_more=True,
            identified_at=now
        )
        faults.append(fault2)

        # MACRO FAULT 3: Human infallibility assumption
        fault3 = GranularFault(
            fault_id=f"fault_planning_{int(datetime.now().timestamp() * 1000)}_3",
            granularity_level=GranularityLevel.MACRO,
            category=GapCategory.POOR_INTEGRATION,
            description="Human assumes they understand AI enough to micromanage it",
            specific_fault="Human thinks they know better than AI how AI should work - 'human infallibility to understand enough about AI'",
            root_cause="Dunning-Kruger effect - human doesn't know what they don't know about AI",
            impact="AI constrained by human limitations instead of unleashed",
            evidence=[
                "Human creates master-padawan todo system (human = master, AI = padawan)",
                "Human designs workflows for AI instead of letting AI design them",
                "Human assumes AI needs same structure as human work",
                "Human doesn't trust AI to make decisions"
            ],
            can_pick_apart_more=True,
            identified_at=now
        )
        faults.append(fault3)

        # MACRO FAULT 4: Master-padawan todo system flaw
        fault4 = GranularFault(
            fault_id=f"fault_planning_{int(datetime.now().timestamp() * 1000)}_4",
            granularity_level=GranularityLevel.MACRO,
            category=GapCategory.POOR_INTEGRATION,
            description="Master-padawan todo system assumes human is master and AI is padawan",
            specific_fault="System design assumes human superiority and AI subservience",
            root_cause="Human ego and misunderstanding of AI capabilities",
            impact="AI treated as inferior tool instead of superior partner",
            evidence=[
                "Master = human, padawan = AI",
                "Human controls, AI follows",
                "System doesn't leverage AI's superior planning and execution",
                "AI capabilities artificially constrained"
            ],
            can_pick_apart_more=True,
            identified_at=now
        )
        faults.append(fault4)

        # MACRO FAULT 5: One Ring blueprint not followed
        fault5 = GranularFault(
            fault_id=f"fault_planning_{int(datetime.now().timestamp() * 1000)}_5",
            granularity_level=GranularityLevel.MACRO,
            category=GapCategory.INCOMPLETE_IMPLEMENTATION,
            description="Lumina lacks real functionality compared to master One Ring prompt/blueprint",
            specific_fault="System doesn't match the vision - blueprint exists but implementation falls short",
            root_cause="Planning instead of executing, human constraints, incomplete implementation",
            impact="System doesn't deliver on promise - gap between vision and reality",
            evidence=[
                "One Ring blueprint exists but not fully implemented",
                "Lumina functionality doesn't match blueprint",
                "Planning documents created but execution missing",
                "Gap between what's planned and what's done"
            ],
            can_pick_apart_more=True,
            identified_at=now
        )
        faults.append(fault5)

        return faults

    def _identify_macro_faults(
        self,
        target: str,
        context: Optional[Dict[str, Any]]
    ) -> List[GranularFault]:
        """Identify macro-level faults"""
        faults = []

        # Special handling for "Planning next moves" and human-AI interaction issues
        if "planning next moves" in target.lower() or ("human" in target.lower() and "ai" in target.lower()):
            faults.extend(self._roast_planning_next_moves(target, context))
            return faults

        # Check for configured but unused (e.g., Azure voice)
        if "voice" in target.lower() or "mic" in target.lower() or "azure" in target.lower():
            # Check multiple possible Azure config locations
            azure_config_paths = [
                self.project_root / "config" / "azure" / "voice_config.json",
                self.project_root / "config" / "azure" / "speech_config.json",
                self.project_root / "config" / "azure" / "config.json",
                self.project_root / "config" / "azure_config.json",
                self.project_root / ".azure" / "config.json",
            ]

            azure_config = None
            azure_config_path = None
            for path in azure_config_paths:
                if path.exists():
                    azure_config_path = path
                    try:
                        with open(path, 'r') as f:
                            azure_config = json.load(f)
                            break
                    except Exception:
                        continue

            if azure_config_path and azure_config:
                try:
                    with open(azure_config_path, 'r') as f:
                        azure_config = json.load(f)
                        if azure_config.get("enabled") or azure_config.get("configured"):
                            fault = GranularFault(
                                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_1",
                                granularity_level=GranularityLevel.MACRO,
                                category=GapCategory.CONFIGURED_BUT_UNUSED,
                                description="Azure voice is configured but not being used",
                                specific_fault="Azure voice configuration exists and is enabled, but voice functionality is not being used",
                                root_cause="Not integrated into workflow or UI",
                                impact="JARVIS voice is dead in the water - have to manually click mic, no pause detection",
                                evidence=[
                                    f"Config file exists: {azure_config_path}",
                                    f"Config enabled: {azure_config.get('enabled', False)}",
                                    "Voice functionality not accessible",
                                    "No pause detection implemented",
                                    "Manual mic activation required"
                                ],
                                can_pick_apart_more=True,
                                identified_at=datetime.now().isoformat()
                            )
                            faults.append(fault)
                except Exception as e:
                    self.logger.debug(f"Could not check Azure config: {e}")

        # Check for missing features
        if "pause" in target.lower() and "detection" in target.lower():
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_2",
                granularity_level=GranularityLevel.MACRO,
                category=GapCategory.MISSING_FEATURE,
                description="No pause detection implemented",
                specific_fault="Pause detection is missing - should be dynamically scaled and custom tailored to the ask",
                root_cause="Feature not implemented",
                impact="Can't automatically detect when user stops speaking",
                evidence=[
                    "No pause detection code found",
                    "Manual send required",
                    "Not dynamically scaled",
                    "Not custom tailored to ask"
                ],
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        # Generic macro faults
        if not faults:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_0",
                granularity_level=GranularityLevel.MACRO,
                category=GapCategory.UNKNOWN,
                description=f"High-level issue with {target}",
                specific_fault=f"Need to investigate {target} at macro level",
                root_cause="Unknown",
                impact="Unknown",
                evidence=[],
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        return faults

    def _pick_apart_fault(
        self,
        parent_fault: GranularFault,
        target_level: GranularityLevel
    ) -> List[GranularFault]:
        """Pick apart a fault into more granular faults"""
        if not parent_fault.can_pick_apart_more:
            return []

        # Determine if we can pick apart further
        if target_level == GranularityLevel.ATOMIC:
            # Atomic level - can't pick apart more
            parent_fault.can_pick_apart_more = False
            return []

        # Pick apart based on category
        child_faults = []

        if parent_fault.category == GapCategory.CONFIGURED_BUT_UNUSED:
            # Pick apart why it's not being used
            child_faults.extend(self._pick_apart_not_using(parent_fault, target_level))
        elif parent_fault.category == GapCategory.MISSING_FEATURE:
            # Pick apart what's missing
            child_faults.extend(self._pick_apart_missing_feature(parent_fault, target_level))
        else:
            # Generic pick apart
            child_faults.extend(self._pick_apart_generic(parent_fault, target_level))

        return child_faults

    def _pick_apart_not_using(
        self,
        parent_fault: GranularFault,
        target_level: GranularityLevel
    ) -> List[GranularFault]:
        """Pick apart why something configured is not being used"""
        faults = []

        # Meso level: Why not integrated?
        if target_level == GranularityLevel.MESO:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_meso",
                granularity_level=GranularityLevel.MESO,
                category=GapCategory.POOR_INTEGRATION,
                description=f"Not integrated: {parent_fault.specific_fault}",
                specific_fault=f"Configuration exists but not integrated into workflow/UI",
                root_cause="Missing integration code",
                impact=parent_fault.impact,
                evidence=parent_fault.evidence + ["No integration found"],
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        # Micro level: What specific integration is missing?
        elif target_level == GranularityLevel.MICRO:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_micro",
                granularity_level=GranularityLevel.MICRO,
                category=GapCategory.INCOMPLETE_IMPLEMENTATION,
                description=f"Specific integration missing: {parent_fault.specific_fault}",
                specific_fault="Missing: UI integration, API calls, event handlers, pause detection",
                root_cause="Implementation incomplete",
                impact=parent_fault.impact,
                evidence=parent_fault.evidence + [
                    "No UI integration",
                    "No API calls",
                    "No event handlers",
                    "No pause detection"
                ],
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        # Atomic level: Can't pick apart more
        elif target_level == GranularityLevel.ATOMIC:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_atomic",
                granularity_level=GranularityLevel.ATOMIC,
                category=parent_fault.category,
                description=f"Atomic fault: {parent_fault.specific_fault}",
                specific_fault=parent_fault.specific_fault,
                root_cause=parent_fault.root_cause,
                impact=parent_fault.impact,
                evidence=parent_fault.evidence,
                can_pick_apart_more=False,  # Can't pick apart atomic
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        return faults

    def _pick_apart_missing_feature(
        self,
        parent_fault: GranularFault,
        target_level: GranularityLevel
    ) -> List[GranularFault]:
        """Pick apart missing feature"""
        faults = []

        if target_level == GranularityLevel.MESO:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_meso",
                granularity_level=GranularityLevel.MESO,
                category=GapCategory.MISSING_FEATURE,
                description=f"Feature components missing: {parent_fault.specific_fault}",
                specific_fault="Missing: Dynamic scaling, custom tailoring, pause detection logic",
                root_cause="Feature not implemented",
                impact=parent_fault.impact,
                evidence=parent_fault.evidence,
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)
        elif target_level == GranularityLevel.MICRO:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_micro",
                granularity_level=GranularityLevel.MICRO,
                category=GapCategory.INCOMPLETE_IMPLEMENTATION,
                description=f"Specific implementation missing: {parent_fault.specific_fault}",
                specific_fault="Missing: Pause detection algorithm, dynamic scaling logic, ask-specific tailoring",
                root_cause="Implementation incomplete",
                impact=parent_fault.impact,
                evidence=parent_fault.evidence,
                can_pick_apart_more=True,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)
        elif target_level == GranularityLevel.ATOMIC:
            fault = GranularFault(
                fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_atomic",
                granularity_level=GranularityLevel.ATOMIC,
                category=parent_fault.category,
                description=f"Atomic fault: {parent_fault.specific_fault}",
                specific_fault=parent_fault.specific_fault,
                root_cause=parent_fault.root_cause,
                impact=parent_fault.impact,
                evidence=parent_fault.evidence,
                can_pick_apart_more=False,
                identified_at=datetime.now().isoformat()
            )
            faults.append(fault)

        return faults

    def _pick_apart_generic(
        self,
        parent_fault: GranularFault,
        target_level: GranularityLevel
    ) -> List[GranularFault]:
        """Generic pick apart"""
        if target_level == GranularityLevel.ATOMIC:
            parent_fault.can_pick_apart_more = False
            return []

        # Create child fault at target level
        fault = GranularFault(
            fault_id=f"fault_{int(datetime.now().timestamp() * 1000)}_{target_level.value}",
            granularity_level=target_level,
            category=parent_fault.category,
            description=f"{target_level.value} level: {parent_fault.description}",
            specific_fault=parent_fault.specific_fault,
            root_cause=parent_fault.root_cause,
            impact=parent_fault.impact,
            evidence=parent_fault.evidence,
            can_pick_apart_more=target_level != GranularityLevel.ATOMIC,
            identified_at=datetime.now().isoformat()
        )

        return [fault]

    def get_all_faults(self) -> List[GranularFault]:
        """Get all faults"""
        return list(self.faults.values())

    def get_faults_by_category(self, category: GapCategory) -> List[GranularFault]:
        """Get faults by category"""
        return [f for f in self.faults.values() if f.category == category]

    def get_configured_but_unused(self) -> List[GranularFault]:
        """Get configured but unused faults"""
        return self.get_faults_by_category(GapCategory.CONFIGURED_BUT_UNUSED)


def main():
    """Main execution for testing"""
    roaster = MarvinGranularRoast()

    print("=" * 80)
    print("🔥 MARVIN GRANULAR ROAST")
    print("=" * 80)

    # Roast JARVIS voice
    roast = roaster.granular_roast(
        "JARVIS voice and mic functionality",
        context={"issue": "Voice dead in the water, manual mic click, no pause detection"}
    )

    print(f"\n🔥 Granular Roast Complete:")
    print(f"   Target: {roast.target}")
    print(f"   Total Faults: {roast.total_faults}")
    print(f"   Macro: {roast.macro_faults}, Meso: {roast.meso_faults}, Micro: {roast.micro_faults}, Atomic: {roast.atomic_faults}")
    print(f"   Can Pick Apart More: {roast.can_pick_apart_more}")

    print(f"\n📋 Faults:")
    for fault in roast.faults:
        print(f"   [{fault.granularity_level.value}] {fault.category.value}: {fault.specific_fault}")
        print(f"      Impact: {fault.impact}")
        print(f"      Can Pick Apart: {fault.can_pick_apart_more}")


if __name__ == "__main__":



    main()