#!/usr/bin/env python3
"""
WOPR Core: Workflow/Worktree Identification & Pattern Mapping

CORE @WOPR functionality for:
1. Identifying new or updating existing workflows/worktrees
2. Mapping workflows to #patterns
3. Linking patterns to WOPR workflows
4. Processing workflow mapping for specific or new workflows

Principle: #pattern = @wopr workflows
All workflows/worktrees are identified and mapped to patterns for WOPR processing.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
logger = get_logger("wopr_workflow_pattern_mapper")


try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from workflow_base import WorkflowBase
    WORKFLOW_BASE_AVAILABLE = True
except ImportError:
    WORKFLOW_BASE_AVAILABLE = False
    WorkflowBase = None

try:
    from peak_pattern_system import PeakPatternSystem, PatternType
    PATTERN_SYSTEM_AVAILABLE = True
except ImportError:
    PATTERN_SYSTEM_AVAILABLE = False
    PeakPatternSystem = None
    PatternType = None

try:
    from pattern_workflow_agent_mapper import PatternWorkflowAgentMapper, PatternType as PWAPatternType
    PATTERN_AGENT_MAPPER_AVAILABLE = True
except ImportError:
    PATTERN_AGENT_MAPPER_AVAILABLE = False
    PatternWorkflowAgentMapper = None
    PWAPatternType = None


class WorkflowType(Enum):
    """Workflow type classification"""
    NEW_WORKFLOW = "new_workflow"
    EXISTING_WORKFLOW = "existing_workflow"
    WORKTREE = "worktree"
    PATTERN_WORKFLOW = "pattern_workflow"
    WOPR_WORKFLOW = "wopr_workflow"


class PatternLinkType(Enum):
    """Pattern link type"""
    DIRECT_MATCH = "direct_match"  # Exact pattern match
    SIMILAR_PATTERN = "similar_pattern"  # Similar pattern
    WORKFLOW_PATTERN = "workflow_pattern"  # Workflow-specific pattern
    WOPR_STRATAGEM = "wopr_stratagem"  # WOPR strategic pattern


@dataclass
class WorkflowIdentifier:
    """Identified workflow/worktree"""
    workflow_id: str
    workflow_name: str
    workflow_type: WorkflowType
    file_path: Optional[str] = None
    class_name: Optional[str] = None
    execution_id: Optional[str] = None
    detected_patterns: List[str] = field(default_factory=list)
    pattern_hashtags: List[str] = field(default_factory=list)  # #pattern tags
    wopr_linked: bool = False
    wopr_workflow_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["workflow_type"] = self.workflow_type.value
        return data


@dataclass
class PatternMapping:
    """Mapping between workflow and pattern"""
    mapping_id: str
    workflow_id: str
    pattern_id: str
    pattern_name: str
    link_type: PatternLinkType
    confidence: float = 0.0
    frequency: int = 1
    wopr_stratagem_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["link_type"] = self.link_type.value
        return data


@dataclass
class WorktreeStructure:
    """Worktree structure identification"""
    worktree_id: str
    worktree_name: str
    root_path: str
    branches: List[str] = field(default_factory=list)
    workflows: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    wopr_mapped: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class WOPRWorkflowPatternMapper:
    """
    WOPR Core: Workflow/Worktree Identification & Pattern Mapping

    Identifies workflows/worktrees and maps them to #patterns for WOPR processing.
    """

    def __init__(self, project_root: Optional[Path] = None, wopr_path: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.wopr_path = wopr_path or (self.project_root / "data" / "wopr_plans")
        self.wopr_path.mkdir(parents=True, exist_ok=True)

        # Data directories
        self.data_dir = self.project_root / "data" / "wopr_workflows"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.workflows_file = self.data_dir / "identified_workflows.json"
        self.patterns_file = self.data_dir / "pattern_mappings.json"
        self.worktrees_file = self.data_dir / "identified_worktrees.json"
        self.wopr_workflows_file = self.wopr_path / "WOPR_WORKFLOWS.json"

        # State
        self.identified_workflows: Dict[str, WorkflowIdentifier] = {}
        self.pattern_mappings: Dict[str, PatternMapping] = {}
        self.identified_worktrees: Dict[str, WorktreeStructure] = {}
        self.wopr_workflows: Dict[str, Any] = {}

        self.logger = get_logger("WOPRWorkflowPatternMapper")

        # Initialize pattern system if available
        self.pattern_system = None
        if PATTERN_SYSTEM_AVAILABLE and PeakPatternSystem:
            try:
                self.pattern_system = PeakPatternSystem(self.project_root)
            except Exception as e:
                self.logger.warning(f"Pattern system not available: {e}")

        # Pattern Workflow Agent Mapper (for pattern → workflow → agent mapping with tracking)
        self.pattern_agent_mapper = None
        if PATTERN_AGENT_MAPPER_AVAILABLE and PatternWorkflowAgentMapper:
            try:
                self.pattern_agent_mapper = PatternWorkflowAgentMapper(project_root=self.project_root)
                self.logger.info("✅ Pattern Workflow Agent Mapper initialized")
            except Exception as e:
                self.logger.warning(f"Pattern Agent Mapper not available: {e}")

        self._load_existing_data()

    def _load_existing_data(self):
        """Load existing workflow and pattern data"""
        # Load identified workflows
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.identified_workflows = {
                        wid: WorkflowIdentifier(**{**w_data, 'workflow_type': WorkflowType(w_data['workflow_type'])})
                        for wid, w_data in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"Could not load workflows: {e}")

        # Load pattern mappings
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.pattern_mappings = {
                        mid: PatternMapping(**{**p_data, 'link_type': PatternLinkType(p_data['link_type'])})
                        for mid, p_data in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"Could not load pattern mappings: {e}")

        # Load WOPR workflows
        if self.wopr_workflows_file.exists():
            try:
                with open(self.wopr_workflows_file, 'r', encoding='utf-8') as f:
                    self.wopr_workflows = json.load(f)
            except Exception as e:
                self.logger.warning(f"Could not load WOPR workflows: {e}")

    def identify_workflows(self) -> Dict[str, WorkflowIdentifier]:
        """
        Identify all workflows in the codebase

        Scans for:
        - WorkflowBase subclasses
        - Workflow files
        - Workflow definitions
        - Worktree structures
        """
        self.logger.info("🔍 Identifying workflows and worktrees...")

        # Scan for workflow files
        workflow_files = list(self.project_root.rglob("**/workflow*.py"))
        workflow_files.extend(self.project_root.rglob("**/*workflow*.py"))

        for workflow_file in workflow_files:
            if '__pycache__' in str(workflow_file):
                continue

            try:
                # Read file and analyze
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for WorkflowBase subclasses
                class_matches = re.findall(r'class\s+(\w+.*?)\s*\(.*?WorkflowBase', content)

                for class_match in class_matches:
                    class_name = class_match.strip()
                    workflow_name = class_name.replace('Workflow', '').replace('_', ' ').title()

                    # Extract #pattern hashtags
                    pattern_hashtags = re.findall(r'#pattern\w*|#\w+pattern', content, re.IGNORECASE)

                    # Generate workflow ID
                    workflow_id = hashlib.md5(f"{workflow_file}_{class_name}".encode()).hexdigest()[:16]

                    # Determine workflow type
                    if workflow_id in self.identified_workflows:
                        workflow_type = WorkflowType.EXISTING_WORKFLOW
                    else:
                        workflow_type = WorkflowType.NEW_WORKFLOW

                    # Check if it's a pattern workflow
                    if pattern_hashtags or '#pattern' in content.lower():
                        workflow_type = WorkflowType.PATTERN_WORKFLOW

                    workflow = WorkflowIdentifier(
                        workflow_id=workflow_id,
                        workflow_name=workflow_name,
                        workflow_type=workflow_type,
                        file_path=str(workflow_file.relative_to(self.project_root)),
                        class_name=class_name,
                        pattern_hashtags=pattern_hashtags,
                        metadata={
                            "file": str(workflow_file),
                            "detected_at": datetime.now().isoformat()
                        }
                    )

                    self.identified_workflows[workflow_id] = workflow

            except Exception as e:
                self.logger.debug(f"Could not analyze {workflow_file}: {e}")

        # Scan for worktrees (Git worktrees)
        self._identify_worktrees()

        self._save_workflows()

        self.logger.info(f"✅ Identified {len(self.identified_workflows)} workflows")

        return self.identified_workflows

    def _identify_worktrees(self):
        """Identify Git worktrees"""
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'worktree', 'list'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split()
                        if len(parts) >= 2:
                            worktree_path = parts[0]
                            branch = parts[1] if len(parts) > 1 else "main"

                            worktree_id = hashlib.md5(worktree_path.encode()).hexdigest()[:16]

                            worktree = WorktreeStructure(
                                worktree_id=worktree_id,
                                worktree_name=Path(worktree_path).name,
                                root_path=worktree_path,
                                branches=[branch],
                                metadata={
                                    "detected_at": datetime.now().isoformat(),
                                    "branch": branch
                                }
                            )

                            self.identified_worktrees[worktree_id] = worktree
        except Exception as e:
            self.logger.debug(f"Could not identify worktrees: {e}")

    def map_workflows_to_patterns(self) -> Dict[str, PatternMapping]:
        """
        Map identified workflows to #patterns

        Principle: #pattern = @wopr workflows
        All workflows are mapped to patterns for WOPR processing.
        """
        self.logger.info("🗺️ Mapping workflows to patterns...")

        for workflow_id, workflow in self.identified_workflows.items():
            # Extract patterns from workflow
            patterns = self._extract_patterns_from_workflow(workflow)

            # Map each pattern
            for pattern_text in patterns:
                pattern_id = hashlib.md5(pattern_text.encode()).hexdigest()[:16]

                # Check if pattern exists in pattern system
                pattern_match = None
                if self.pattern_system:
                    pattern_match = self._find_pattern_in_system(pattern_text)

                # Determine link type
                if pattern_match:
                    link_type = PatternLinkType.DIRECT_MATCH
                    pattern_name = pattern_match.get("name", pattern_text)
                    confidence = 0.9
                elif workflow.pattern_hashtags:
                    link_type = PatternLinkType.WORKFLOW_PATTERN
                    pattern_name = pattern_text
                    confidence = 0.7
                else:
                    link_type = PatternLinkType.SIMILAR_PATTERN
                    pattern_name = pattern_text
                    confidence = 0.5

                # Create mapping
                mapping_id = f"{workflow_id}_{pattern_id}"

                if mapping_id in self.pattern_mappings:
                    # Update existing mapping
                    mapping = self.pattern_mappings[mapping_id]
                    mapping.frequency += 1
                    mapping.confidence = max(mapping.confidence, confidence)
                else:
                    # Create new mapping
                    mapping = PatternMapping(
                        mapping_id=mapping_id,
                        workflow_id=workflow_id,
                        pattern_id=pattern_id,
                        pattern_name=pattern_name,
                        link_type=link_type,
                        confidence=confidence,
                        frequency=1,
                        metadata={
                            "pattern_text": pattern_text,
                            "workflow_name": workflow.workflow_name
                        }
                    )
                    self.pattern_mappings[mapping_id] = mapping

                # Link to WOPR if pattern is frequent
                if mapping.frequency >= 2:
                    self._link_to_wopr(workflow, mapping)

                # Create pattern → workflow → agent mapping with full tracking
                if self.pattern_agent_mapper:
                    try:
                        # Determine pattern type
                        pattern_type = PWAPatternType.NEW
                        if mapping_id in self.pattern_mappings:
                            pattern_type = PWAPatternType.UPDATED

                        # Create key-values for pattern
                        key_values = [
                            ("pattern_name", pattern_name),
                            ("workflow_id", workflow_id),
                            ("workflow_name", workflow.workflow_name),
                            ("confidence", confidence),
                            ("link_type", link_type.value)
                        ]

                        # Map pattern to workflow
                        self.pattern_agent_mapper.map_pattern_to_workflow(
                            pattern_id=pattern_id,
                            workflow_id=workflow_id,
                            workflow_name=workflow.workflow_name,
                            confidence=confidence
                        )

                        # Create agent for workflow (all agents in same chat session)
                        agent = self.pattern_agent_mapper.create_agent_for_workflow(
                            workflow_id=workflow_id,
                            workflow_name=workflow.workflow_name,
                            agent_name=f"Agent-{workflow.workflow_name}"
                        )

                        self.logger.info(f"🤖 Created agent {agent.agent_id} for workflow {workflow_id}")
                    except Exception as e:
                        self.logger.warning(f"Error creating pattern→workflow→agent mapping: {e}")

        self._save_pattern_mappings()

        self.logger.info(f"✅ Mapped {len(self.pattern_mappings)} workflow-pattern links")

        return self.pattern_mappings

    def _extract_patterns_from_workflow(self, workflow: WorkflowIdentifier) -> List[str]:
        """Extract patterns from a workflow"""
        patterns = []

        # Add pattern hashtags
        patterns.extend(workflow.pattern_hashtags)

        # Read workflow file if available
        if workflow.file_path:
            try:
                workflow_file = self.project_root / workflow.file_path
                if workflow_file.exists():
                    with open(workflow_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract #pattern tags
                    pattern_tags = re.findall(r'#pattern\w*|#\w+pattern', content, re.IGNORECASE)
                    patterns.extend(pattern_tags)

                    # Extract workflow patterns (method names, step patterns)
                    step_patterns = re.findall(r'def\s+(\w+.*?step.*?)\(|step.*?(\w+.*?pattern)', content, re.IGNORECASE)
                    for match in step_patterns:
                        patterns.append(match[0] or match[1])
            except Exception as e:
                self.logger.debug(f"Could not extract patterns from {workflow.file_path}: {e}")

        return list(set(patterns))  # Remove duplicates

    def _find_pattern_in_system(self, pattern_text: str) -> Optional[Dict[str, Any]]:
        """Find pattern in pattern system"""
        if not self.pattern_system:
            return None

        try:
            # Search for pattern
            patterns = self.pattern_system.find_patterns(query=pattern_text)
            if patterns:
                return {
                    "name": patterns[0].name,
                    "pattern_id": patterns[0].pattern_id,
                    "type": patterns[0].pattern_type.value if hasattr(patterns[0].pattern_type, 'value') else str(patterns[0].pattern_type)
                }
        except Exception as e:
            self.logger.debug(f"Could not search pattern system: {e}")

        return None

    def _link_to_wopr(self, workflow: WorkflowIdentifier, mapping: PatternMapping):
        """
        Link workflow/pattern to WOPR workflows

        Principle: #pattern = @wopr workflows
        """
        if workflow.wopr_linked:
            return

        self.logger.info(f"🔗 Linking {workflow.workflow_name} to WOPR...")

        # Create WOPR workflow entry
        wopr_workflow_id = f"wopr_{workflow.workflow_id}"

        wopr_workflow = {
            "wopr_workflow_id": wopr_workflow_id,
            "workflow_id": workflow.workflow_id,
            "workflow_name": workflow.workflow_name,
            "pattern_mappings": [mapping.mapping_id],
            "pattern_hashtags": workflow.pattern_hashtags,
            "linked_at": datetime.now().isoformat(),
            "status": "active",
            "metadata": {
                "workflow_type": workflow.workflow_type.value,
                "pattern_count": len(workflow.pattern_hashtags)
            }
        }

        self.wopr_workflows[wopr_workflow_id] = wopr_workflow

        # Update workflow
        workflow.wopr_linked = True
        workflow.wopr_workflow_id = wopr_workflow_id

        # Create WOPR stratagem if pattern is frequent
        if mapping.frequency >= 2:
            stratagem_id = self._create_wopr_stratagem(workflow, mapping)
            mapping.wopr_stratagem_id = stratagem_id

        self._save_wopr_workflows()
        self._save_workflows()

    def _create_wopr_stratagem(self, workflow: WorkflowIdentifier, mapping: PatternMapping) -> str:
        try:
            """Create WOPR stratagem for frequent pattern"""
            stratagem_id = f"stratagem_{mapping.pattern_id}"

            stratagem = {
                "stratagem_id": stratagem_id,
                "pattern_id": mapping.pattern_id,
                "pattern_name": mapping.pattern_name,
                "workflow_id": workflow.workflow_id,
                "frequency": mapping.frequency,
                "confidence": mapping.confidence,
                "created_at": datetime.now().isoformat(),
                "tactics": [
                    f"Apply pattern {mapping.pattern_name} to workflow {workflow.workflow_name}",
                    f"Monitor pattern frequency (current: {mapping.frequency})",
                    f"Automate if frequency >= 3"
                ],
                "checkpoints": [
                    f"Pattern applied successfully",
                    f"Workflow execution improved",
                    f"Pattern frequency reduced"
                ]
            }

            # Save stratagem
            stratagem_file = self.wopr_path / "stratagems" / f"{stratagem_id}.json"
            stratagem_file.parent.mkdir(parents=True, exist_ok=True)

            with open(stratagem_file, 'w', encoding='utf-8') as f:
                json.dump(stratagem, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Created WOPR stratagem: {stratagem_id}")

            return stratagem_id

        except Exception as e:
            self.logger.error(f"Error in _create_wopr_stratagem: {e}", exc_info=True)
            raise
    def process_workflow_mapping(self, workflow_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process workflow mapping for specific workflow or all workflows

        This is the core processing function that:
        1. Identifies workflows
        2. Maps to patterns
        3. Links to WOPR
        4. Creates stratagems
        """
        self.logger.info("🔄 Processing workflow mapping...")

        # Step 1: Identify workflows
        if workflow_id:
            # Process specific workflow
            if workflow_id in self.identified_workflows:
                workflow = self.identified_workflows[workflow_id]
            else:
                # Try to identify it
                self.identify_workflows()
                if workflow_id not in self.identified_workflows:
                    return {"error": f"Workflow {workflow_id} not found"}
                workflow = self.identified_workflows[workflow_id]
        else:
            # Process all workflows
            self.identify_workflows()

        # Step 2: Map to patterns
        self.map_workflows_to_patterns()

        # Step 3: Link to WOPR
        for workflow in self.identified_workflows.values():
            if not workflow.wopr_linked:
                mappings = [m for m in self.pattern_mappings.values() if m.workflow_id == workflow.workflow_id]
                if mappings:
                    # Link if has pattern mappings
                    self._link_to_wopr(workflow, mappings[0])

        # Step 4: Generate processing result
        result = {
            "processed_at": datetime.now().isoformat(),
            "workflows_identified": len(self.identified_workflows),
            "pattern_mappings": len(self.pattern_mappings),
            "wopr_linked": len([w for w in self.identified_workflows.values() if w.wopr_linked]),
            "worktrees_identified": len(self.identified_worktrees),
            "wopr_workflows": len(self.wopr_workflows),
            "summary": {
                "new_workflows": len([w for w in self.identified_workflows.values() if w.workflow_type == WorkflowType.NEW_WORKFLOW]),
                "existing_workflows": len([w for w in self.identified_workflows.values() if w.workflow_type == WorkflowType.EXISTING_WORKFLOW]),
                "pattern_workflows": len([w for w in self.identified_workflows.values() if w.workflow_type == WorkflowType.PATTERN_WORKFLOW]),
                "wopr_workflows": len(self.wopr_workflows)
            }
        }

        self.logger.info(f"✅ Processing complete: {result['workflows_identified']} workflows, {result['pattern_mappings']} mappings")

        return result

    def get_workflow_patterns(self, workflow_id: str) -> List[PatternMapping]:
        """Get all patterns for a specific workflow"""
        return [m for m in self.pattern_mappings.values() if m.workflow_id == workflow_id]

    def get_pattern_workflows(self, pattern_id: str) -> List[WorkflowIdentifier]:
        """Get all workflows for a specific pattern"""
        workflow_ids = {m.workflow_id for m in self.pattern_mappings.values() if m.pattern_id == pattern_id}
        return [w for w_id, w in self.identified_workflows.items() if w_id in workflow_ids]

    def _save_workflows(self):
        try:
            """Save identified workflows"""
            workflows_data = {
                wid: workflow.to_dict()
                for wid, workflow in self.identified_workflows.items()
            }

            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_workflows: {e}", exc_info=True)
            raise
    def _save_pattern_mappings(self):
        try:
            """Save pattern mappings"""
            mappings_data = {
                mid: mapping.to_dict()
                for mid, mapping in self.pattern_mappings.items()
            }

            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(mappings_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_pattern_mappings: {e}", exc_info=True)
            raise
    def _save_wopr_workflows(self):
        try:
            """Save WOPR workflows"""
            with open(self.wopr_workflows_file, 'w', encoding='utf-8') as f:
                json.dump(self.wopr_workflows, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_wopr_workflows: {e}", exc_info=True)
            raise
    def generate_wopr_workflow_report(self) -> str:
        """Generate WOPR workflow mapping report"""
        report = []
        report.append("# WOPR Workflow/Pattern Mapping Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        report.append("## Summary")
        report.append(f"- **Workflows Identified**: {len(self.identified_workflows)}")
        report.append(f"- **Pattern Mappings**: {len(self.pattern_mappings)}")
        report.append(f"- **WOPR Linked**: {len([w for w in self.identified_workflows.values() if w.wopr_linked])}")
        report.append(f"- **Worktrees Identified**: {len(self.identified_worktrees)}")
        report.append("")

        report.append("## Workflows by Type")
        for wf_type in WorkflowType:
            count = len([w for w in self.identified_workflows.values() if w.workflow_type == wf_type])
            if count > 0:
                report.append(f"- **{wf_type.value}**: {count}")
        report.append("")

        report.append("## Pattern Mappings")
        for mapping in list(self.pattern_mappings.values())[:20]:  # First 20
            workflow = self.identified_workflows.get(mapping.workflow_id)
            workflow_name = workflow.workflow_name if workflow else "Unknown"
            report.append(f"- **{mapping.pattern_name}** → {workflow_name} (frequency: {mapping.frequency}, confidence: {mapping.confidence:.2f})")
        if len(self.pattern_mappings) > 20:
            report.append(f"- ... and {len(self.pattern_mappings) - 20} more")
        report.append("")

        report.append("## WOPR Workflows")
        for wopr_id, wopr_wf in list(self.wopr_workflows.items())[:10]:
            report.append(f"- **{wopr_wf['workflow_name']}** ({wopr_id})")
            report.append(f"  - Patterns: {len(wopr_wf.get('pattern_mappings', []))}")
            report.append(f"  - Hashtags: {', '.join(wopr_wf.get('pattern_hashtags', []))}")
        if len(self.wopr_workflows) > 10:
            report.append(f"- ... and {len(self.wopr_workflows) - 10} more")
        report.append("")

        return "\n".join(report)


def main():
    try:
        """Main execution"""
        mapper = WOPRWorkflowPatternMapper()

        print("🎯 WOPR Core: Workflow/Pattern Mapping")
        print("=" * 80)
        print("Principle: #pattern = @wopr workflows")
        print("")

        # Process workflow mapping
        result = mapper.process_workflow_mapping()

        print("📊 Processing Results:")
        print(f"   Workflows Identified: {result['workflows_identified']}")
        print(f"   Pattern Mappings: {result['pattern_mappings']}")
        print(f"   WOPR Linked: {result['wopr_linked']}")
        print(f"   Worktrees: {result['worktrees_identified']}")
        print("")

        # Generate report
        report = mapper.generate_wopr_workflow_report()
        report_file = mapper.data_dir / "WOPR_WORKFLOW_MAPPING_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✅ Report saved to: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()