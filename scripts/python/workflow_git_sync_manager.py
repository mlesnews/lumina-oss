#!/usr/bin/env python3
"""
Workflow-to-Git Sync Manager

Syncs workflows as git worktrees/branches/PRs for version-controlled workflow management.
Treats workflows as first-class git entities for better organization and collaboration.

Features:
- Workflow-to-branch mapping
- Automatic worktree creation for workflows
- PR generation for workflow sets
- Pattern extraction via @SYPHON
- @WOPR integration for pattern recognition
- Refactor/repurpose opportunity detection

Tags: #WORKFLOW #GIT #WORKTREE #BRANCH #PR #SYPHON #WOPR #PATTERNS @JARVIS @TEAM
"""

import sys
import json
import subprocess
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowGitSyncManager")

# SYPHON Integration
try:
    from syphon_workflow_patterns import SYPHONWorkflowPatternExtractor
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONWorkflowPatternExtractor = None

# WOPR Integration
try:
    from wopr_monitoring import WOPRMonitoring
    WOPR_AVAILABLE = True
except ImportError:
    WOPR_AVAILABLE = False
    WOPRMonitoring = None

# PR/Ticket Coordinator
try:
    from jarvis_pr_ticket_coordinator import PRTicketCoordinator
    PR_COORDINATOR_AVAILABLE = True
except ImportError:
    PR_COORDINATOR_AVAILABLE = False
    PRTicketCoordinator = None


class WorkflowType(Enum):
    """Types of workflows"""
    CURSOR_SESSION = "cursor_session"
    GITLENS_ALERT = "gitlens_alert"
    SYPHON_EXTRACTION = "syphon_extraction"
    WOPR_PATTERN = "wopr_pattern"
    REFACTOR_OPPORTUNITY = "refactor_opportunity"
    COGNITIVE_LOAD = "cognitive_load"
    CURSOR_DOCS = "cursor_docs"
    COMPOSITE = "composite"  # Multiple workflows combined


@dataclass
class WorkflowDefinition:
    """Definition of a workflow"""
    workflow_id: str
    workflow_name: str
    workflow_type: WorkflowType
    description: str
    files: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    refactor_opportunities: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GitWorkflowMapping:
    """Mapping between workflow and git branch/worktree/PR"""
    workflow_id: str
    branch_name: str
    worktree_path: Optional[Path] = None
    pr_number: Optional[str] = None
    pr_url: Optional[str] = None
    status: str = "active"  # active, merged, closed
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowGitSyncManager:
    """
    Workflow-to-Git Sync Manager

    Manages workflows as git worktrees/branches/PRs for version-controlled workflow management.
    """

    def __init__(self, project_root: Optional[Path] = None, git_repo_path: Optional[Path] = None):
        """Initialize Workflow-to-Git Sync Manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.git_repo_path = Path(git_repo_path) if git_repo_path else self.project_root

        # Data directories
        self.data_dir = self.project_root / "data" / "workflow_git_sync"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Worktree base directory
        self.worktrees_dir = self.project_root / "worktrees"
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

        # Storage files
        self.workflows_file = self.data_dir / "workflows.json"
        self.mappings_file = self.data_dir / "git_mappings.json"

        # SYPHON Pattern Extractor
        self.syphon_extractor = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon_extractor = SYPHONWorkflowPatternExtractor(project_root=project_root)
                logger.info("✅ SYPHON Pattern Extractor initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # WOPR Monitoring
        self.wopr_monitoring = None
        if WOPR_AVAILABLE:
            try:
                holocron_path = self.project_root / "data" / "holocron"
                self.wopr_monitoring = WOPRMonitoring(
                    wopr_path=self.project_root / "data" / "wopr",
                    holocron_path=holocron_path
                )
                logger.info("✅ WOPR Monitoring initialized")
            except Exception as e:
                logger.warning(f"⚠️  WOPR not available: {e}")

        # PR/Ticket Coordinator
        self.pr_coordinator = None
        if PR_COORDINATOR_AVAILABLE:
            try:
                self.pr_coordinator = PRTicketCoordinator(project_root=project_root)
                logger.info("✅ PR/Ticket Coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  PR/Ticket Coordinator not available: {e}")

        # Load existing data
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.git_mappings: Dict[str, GitWorkflowMapping] = {}
        self._load_data()

        logger.info("✅ Workflow-to-Git Sync Manager initialized")

    def _load_data(self):
        """Load workflows and git mappings"""
        # Load workflows
        if self.workflows_file.exists():
            try:
                with open(self.workflows_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for wf_id, wf_data in data.get("workflows", {}).items():
                        wf_data["workflow_type"] = WorkflowType(wf_data["workflow_type"])
                        wf_data["created_at"] = datetime.fromisoformat(wf_data["created_at"])
                        wf_data["updated_at"] = datetime.fromisoformat(wf_data["updated_at"])
                        self.workflows[wf_id] = WorkflowDefinition(**wf_data)
                logger.info(f"✅ Loaded {len(self.workflows)} workflows")
            except Exception as e:
                logger.warning(f"⚠️  Error loading workflows: {e}")

        # Load git mappings
        if self.mappings_file.exists():
            try:
                with open(self.mappings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for wf_id, mapping_data in data.get("mappings", {}).items():
                        if mapping_data.get("worktree_path"):
                            mapping_data["worktree_path"] = Path(mapping_data["worktree_path"])
                        mapping_data["created_at"] = datetime.fromisoformat(mapping_data["created_at"])
                        self.git_mappings[wf_id] = GitWorkflowMapping(**mapping_data)
                logger.info(f"✅ Loaded {len(self.git_mappings)} git mappings")
            except Exception as e:
                logger.warning(f"⚠️  Error loading git mappings: {e}")

    def _save_data(self):
        """Save workflows and git mappings"""
        # Save workflows
        try:
            workflows_data = {
                "timestamp": datetime.now().isoformat(),
                "workflows": {}
            }
            for wf_id, workflow in self.workflows.items():
                wf_dict = {
                    "workflow_id": workflow.workflow_id,
                    "workflow_name": workflow.workflow_name,
                    "workflow_type": workflow.workflow_type.value,
                    "description": workflow.description,
                    "files": workflow.files,
                    "dependencies": workflow.dependencies,
                    "patterns": workflow.patterns,
                    "refactor_opportunities": workflow.refactor_opportunities,
                    "created_at": workflow.created_at.isoformat(),
                    "updated_at": workflow.updated_at.isoformat(),
                    "metadata": workflow.metadata
                }
                workflows_data["workflows"][wf_id] = wf_dict

            with open(self.workflows_file, 'w', encoding='utf-8') as f:
                json.dump(workflows_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving workflows: {e}")

        # Save git mappings
        try:
            mappings_data = {
                "timestamp": datetime.now().isoformat(),
                "mappings": {}
            }
            for wf_id, mapping in self.git_mappings.items():
                mapping_dict = {
                    "workflow_id": mapping.workflow_id,
                    "branch_name": mapping.branch_name,
                    "worktree_path": str(mapping.worktree_path) if mapping.worktree_path else None,
                    "pr_number": mapping.pr_number,
                    "pr_url": mapping.pr_url,
                    "status": mapping.status,
                    "created_at": mapping.created_at.isoformat(),
                    "metadata": mapping.metadata
                }
                mappings_data["mappings"][wf_id] = mapping_dict

            with open(self.mappings_file, 'w', encoding='utf-8') as f:
                json.dump(mappings_data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving git mappings: {e}")

    def _sanitize_branch_name(self, name: str) -> str:
        """Sanitize branch name for git"""
        # Replace spaces and special chars with hyphens
        name = re.sub(r'[^a-zA-Z0-9_-]', '-', name)
        # Remove consecutive hyphens
        name = re.sub(r'-+', '-', name)
        # Remove leading/trailing hyphens
        name = name.strip('-')
        # Limit length
        if len(name) > 100:
            name = name[:100]
        return name.lower()

    def discover_workflows(self, search_paths: Optional[List[Path]] = None) -> List[WorkflowDefinition]:
        """Discover workflows from codebase using @SYPHON pattern extraction"""
        logger.info("🔍 Discovering workflows via @SYPHON pattern extraction...")

        if search_paths is None:
            search_paths = [
                self.project_root / "scripts" / "python",
                self.project_root / "data" / "workflows",
            ]

        discovered_workflows = []

        # Use SYPHON to extract patterns
        if self.syphon_extractor:
            try:
                # Extract patterns from files in search paths
                patterns = []
                for search_path in search_paths:
                    if not search_path.exists():
                        continue
                    for py_file in search_path.rglob("*.py"):
                        if "workflow" in py_file.name.lower():
                            with open(py_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                            extracted_patterns = self.syphon_extractor.extract_patterns_from_workflow(
                                workflow_content=content,
                                workflow_name=py_file.stem,
                                workflow_source=str(py_file)
                            )
                            for pattern in extracted_patterns:
                                patterns.append({
                                    "id": pattern.pattern_id,
                                    "name": pattern.name,
                                    "type": pattern.workflow_type,
                                    "description": pattern.description,
                                    "files": [str(py_file.relative_to(self.project_root))],
                                    "patterns": [pattern.name],
                                    "refactor_opportunities": []
                                })

                for pattern in patterns:
                    workflow = WorkflowDefinition(
                        workflow_id=f"wf_{hashlib.md5(pattern.get('name', '').encode()).hexdigest()[:8]}",
                        workflow_name=pattern.get('name', 'Unknown Workflow'),
                        workflow_type=WorkflowType(pattern.get('type', 'composite')),
                        description=pattern.get('description', ''),
                        files=pattern.get('files', []),
                        patterns=pattern.get('patterns', []),
                        refactor_opportunities=pattern.get('refactor_opportunities', []),
                        metadata={
                            "discovered_via": "syphon",
                            "pattern_id": pattern.get('id'),
                            "confidence": pattern.get('confidence', 0.5)
                        }
                    )
                    discovered_workflows.append(workflow)
                    self.workflows[workflow.workflow_id] = workflow

                logger.info(f"✅ Discovered {len(discovered_workflows)} workflows via @SYPHON")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON extraction failed: {e}")

        # Also scan for workflow files directly
        for search_path in search_paths:
            if not search_path.exists():
                continue

            for py_file in search_path.rglob("*.py"):
                if "workflow" in py_file.name.lower() or "pattern" in py_file.name.lower():
                    # Extract workflow info from file
                    workflow = self._extract_workflow_from_file(py_file)
                    if workflow:
                        discovered_workflows.append(workflow)
                        self.workflows[workflow.workflow_id] = workflow

        self._save_data()
        return discovered_workflows

    def _extract_workflow_from_file(self, file_path: Path) -> Optional[WorkflowDefinition]:
        """Extract workflow definition from Python file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract workflow name from class/function names
            workflow_name = file_path.stem.replace('_', ' ').title()

            # Extract patterns and refactor opportunities via @SYPHON
            patterns = []
            refactor_opportunities = []

            if self.syphon_extractor:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    extracted_patterns = self.syphon_extractor.extract_patterns_from_workflow(
                        workflow_content=content,
                        workflow_name=file_path.stem,
                        workflow_source=str(file_path)
                    )
                    patterns = [p.name for p in extracted_patterns]
                    refactor_opportunities = []  # Would be extracted from pattern analysis
                except Exception:
                    pass

            workflow = WorkflowDefinition(
                workflow_id=f"wf_{hashlib.md5(str(file_path).encode()).hexdigest()[:8]}",
                workflow_name=workflow_name,
                workflow_type=WorkflowType.COMPOSITE,
                description=f"Workflow extracted from {file_path.name}",
                files=[str(file_path.relative_to(self.project_root))],
                patterns=patterns,
                refactor_opportunities=refactor_opportunities,
                metadata={
                    "source_file": str(file_path),
                    "extracted_at": datetime.now().isoformat()
                }
            )

            return workflow
        except Exception as e:
            logger.warning(f"⚠️  Error extracting workflow from {file_path}: {e}")
            return None

    def create_workflow_branch(self, workflow_id: str, base_branch: str = "main") -> Tuple[bool, str]:
        """Create git branch for workflow"""
        if workflow_id not in self.workflows:
            return False, f"Workflow {workflow_id} not found"

        workflow = self.workflows[workflow_id]
        branch_name = self._sanitize_branch_name(f"workflow/{workflow.workflow_name}")

        try:
            # Check if branch already exists
            result = subprocess.run(
                ["git", "branch", "--list", branch_name],
                cwd=self.git_repo_path,
                capture_output=True,
                text=True
            )

            if result.stdout.strip():
                logger.info(f"   Branch {branch_name} already exists")
                return True, branch_name

            # Create branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name, base_branch],
                cwd=self.git_repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Created branch: {branch_name}")

                # Create mapping
                mapping = GitWorkflowMapping(
                    workflow_id=workflow_id,
                    branch_name=branch_name,
                    status="active"
                )
                self.git_mappings[workflow_id] = mapping
                self._save_data()

                return True, branch_name
            else:
                return False, f"Error creating branch: {result.stderr}"

        except Exception as e:
            return False, f"Exception creating branch: {str(e)}"

    def create_worktree(self, workflow_id: str) -> Tuple[bool, Path]:
        """Create git worktree for workflow"""
        if workflow_id not in self.workflows:
            return False, None

        workflow = self.workflows[workflow_id]

        # Get or create branch
        if workflow_id not in self.git_mappings:
            success, branch_name = self.create_workflow_branch(workflow_id)
            if not success:
                return False, None
        else:
            branch_name = self.git_mappings[workflow_id].branch_name

        worktree_name = self._sanitize_branch_name(workflow.workflow_name)
        worktree_path = self.worktrees_dir / worktree_name

        try:
            # Check if worktree already exists
            if worktree_path.exists():
                logger.info(f"   Worktree {worktree_path} already exists")
                return True, worktree_path

            # Create worktree
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch_name],
                cwd=self.git_repo_path,
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info(f"✅ Created worktree: {worktree_path}")

                # Update mapping
                if workflow_id in self.git_mappings:
                    self.git_mappings[workflow_id].worktree_path = worktree_path
                    self._save_data()

                return True, worktree_path
            else:
                return False, None

        except Exception as e:
            logger.error(f"❌ Error creating worktree: {e}")
            return False, None

    def create_workflow_pr(self, workflow_id: str, title: Optional[str] = None, description: Optional[str] = None) -> Tuple[bool, Optional[str]]:
        """Create PR for workflow"""
        if workflow_id not in self.workflows:
            return False, None

        workflow = self.workflows[workflow_id]

        # Ensure branch exists
        if workflow_id not in self.git_mappings:
            success, branch_name = self.create_workflow_branch(workflow_id)
            if not success:
                return False, None
        else:
            branch_name = self.git_mappings[workflow_id].branch_name

        # Use PR coordinator if available
        if self.pr_coordinator:
            try:
                pr_title = title or f"Workflow: {workflow.workflow_name}"
                pr_description = description or self._generate_pr_description(workflow)

                # Create PR via coordinator
                pr_result = self.pr_coordinator.create_pr_and_ticket(
                    title=pr_title,
                    description=pr_description,
                    change_type="feature",
                    severity="minor"
                )

                if pr_result.get("success"):
                    pr_number = pr_result.get("pr_id")
                    self.git_mappings[workflow_id].pr_number = pr_number
                    self._save_data()
                    logger.info(f"✅ Created PR: {pr_number}")
                    return True, pr_number

            except Exception as e:
                logger.warning(f"⚠️  Error creating PR via coordinator: {e}")

        # Fallback: manual PR creation instructions
        logger.info(f"📋 Manual PR creation needed for branch: {branch_name}")
        return False, None

    def _generate_pr_description(self, workflow: WorkflowDefinition) -> str:
        """Generate PR description from workflow"""
        description = f"""# Workflow: {workflow.workflow_name}

## Description
{workflow.description}

## Workflow Type
{workflow.workflow_type.value}

## Files
{chr(10).join(f'- {f}' for f in workflow.files)}

## Patterns Detected
{chr(10).join(f'- {p}' for p in workflow.patterns) if workflow.patterns else 'None detected'}

## Refactor Opportunities
{chr(10).join(f'- {r}' for r in workflow.refactor_opportunities) if workflow.refactor_opportunities else 'None detected'}

## Dependencies
{chr(10).join(f'- {d}' for d in workflow.dependencies) if workflow.dependencies else 'None'}

---
*Generated by Workflow-to-Git Sync Manager*
"""
        return description

    def sync_workflow_set(self, workflow_ids: List[str], create_pr: bool = True) -> Dict[str, Any]:
        """Sync a set of workflows as a combined branch/PR"""
        logger.info(f"🔄 Syncing workflow set: {len(workflow_ids)} workflows")

        results = {
            "workflows": [],
            "branch_created": False,
            "worktree_created": False,
            "pr_created": False,
            "errors": []
        }

        # Create composite workflow
        composite_name = f"workflow-set-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        composite_id = f"composite_{hashlib.md5(composite_name.encode()).hexdigest()[:8]}"

        composite_workflow = WorkflowDefinition(
            workflow_id=composite_id,
            workflow_name=composite_name,
            workflow_type=WorkflowType.COMPOSITE,
            description=f"Composite workflow set containing {len(workflow_ids)} workflows",
            dependencies=workflow_ids,
            metadata={
                "composite": True,
                "component_workflows": workflow_ids
            }
        )

        self.workflows[composite_id] = composite_workflow

        # Create branch for composite
        success, branch_name = self.create_workflow_branch(composite_id)
        if success:
            results["branch_created"] = True
            results["branch_name"] = branch_name

        # Create worktree
        success, worktree_path = self.create_worktree(composite_id)
        if success:
            results["worktree_created"] = True
            results["worktree_path"] = str(worktree_path)

        # Create PR if requested
        if create_pr:
            success, pr_number = self.create_workflow_pr(composite_id)
            if success:
                results["pr_created"] = True
                results["pr_number"] = pr_number

        results["composite_workflow_id"] = composite_id
        return results

    def find_refactor_opportunities(self, workflow_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Find refactor/repurpose opportunities using @SYPHON and @WOPR"""
        logger.info("🔍 Finding refactor/repurpose opportunities...")

        opportunities = []

        # Use SYPHON to extract patterns
        if self.syphon_extractor:
            try:
                if workflow_id and workflow_id in self.workflows:
                    workflow = self.workflows[workflow_id]
                    for file_path in workflow.files:
                        file_path_obj = self.project_root / file_path
                        if file_path_obj.exists():
                            with open(file_path_obj, 'r', encoding='utf-8') as f:
                                content = f.read()
                            extracted_patterns = self.syphon_extractor.extract_patterns_from_workflow(
                                workflow_content=content,
                                workflow_name=file_path_obj.stem,
                                workflow_source=str(file_path_obj)
                            )
                            # Analyze patterns for refactor opportunities
                            for pattern in extracted_patterns:
                                if len(pattern.steps) > 10:  # Complex pattern = refactor opportunity
                                    opportunities.append({
                                        "source": "syphon",
                                        "workflow_id": workflow_id,
                                        "file": file_path,
                                        "opportunity": f"Complex pattern '{pattern.name}' could be refactored into smaller components",
                                        "confidence": 0.7
                                    })
                else:
                    # Scan all workflows
                    for wf_id, workflow in self.workflows.items():
                        for file_path in workflow.files:
                            file_path_obj = self.project_root / file_path
                            if file_path_obj.exists():
                                with open(file_path_obj, 'r', encoding='utf-8') as f:
                                    content = f.read()
                                extracted_patterns = self.syphon_extractor.extract_patterns_from_workflow(
                                    workflow_content=content,
                                    workflow_name=file_path_obj.stem,
                                    workflow_source=str(file_path_obj)
                                )
                                for pattern in extracted_patterns:
                                    if len(pattern.steps) > 10:
                                        opportunities.append({
                                            "source": "syphon",
                                            "workflow_id": wf_id,
                                            "file": file_path,
                                            "opportunity": f"Complex pattern '{pattern.name}' could be refactored",
                                            "confidence": 0.7
                                        })
            except Exception as e:
                logger.warning(f"⚠️  SYPHON extraction error: {e}")

        # Use WOPR for pattern recognition
        if self.wopr_monitoring:
            try:
                # WOPR can identify patterns across workflows
                wopr_patterns = self._wopr_analyze_patterns()
                for pattern in wopr_patterns:
                    opportunities.append({
                        "source": "wopr",
                        "pattern": pattern,
                        "type": "pattern_recognition"
                    })
            except Exception as e:
                logger.warning(f"⚠️  WOPR analysis error: {e}")

        logger.info(f"✅ Found {len(opportunities)} refactor opportunities")
        return opportunities

    def _wopr_analyze_patterns(self) -> List[Dict[str, Any]]:
        """Use WOPR to analyze patterns across workflows"""
        patterns = []

        # Analyze workflow patterns
        workflow_names = [wf.workflow_name for wf in self.workflows.values()]
        workflow_types = [wf.workflow_type.value for wf in self.workflows.values()]

        # Find common patterns
        from collections import Counter
        type_counts = Counter(workflow_types)

        for wf_type, count in type_counts.items():
            if count > 1:
                patterns.append({
                    "pattern": f"Multiple {wf_type} workflows ({count})",
                    "suggestion": f"Consider consolidating {wf_type} workflows",
                    "workflows": [wf.workflow_id for wf in self.workflows.values() if wf.workflow_type.value == wf_type]
                })

        return patterns


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Workflow-to-Git Sync Manager")
    parser.add_argument("--discover", action="store_true", help="Discover workflows")
    parser.add_argument("--sync", type=str, nargs="+", help="Sync workflow(s) to git")
    parser.add_argument("--create-pr", action="store_true", help="Create PR for synced workflows")
    parser.add_argument("--refactor", type=str, nargs="?", const="all", help="Find refactor opportunities")
    parser.add_argument("--list", action="store_true", help="List all workflows")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🔄 Workflow-to-Git Sync Manager")
    print("="*80 + "\n")

    manager = WorkflowGitSyncManager()

    if args.discover:
        workflows = manager.discover_workflows()
        print(f"\n✅ Discovered {len(workflows)} workflows\n")
        for wf in workflows:
            print(f"   - {wf.workflow_name} ({wf.workflow_type.value})")
        print()

    elif args.sync:
        workflow_ids = args.sync
        result = manager.sync_workflow_set(workflow_ids, create_pr=args.create_pr)
        print(f"\n📊 SYNC RESULT:")
        print(f"   Branch: {'✅' if result.get('branch_created') else '❌'}")
        print(f"   Worktree: {'✅' if result.get('worktree_created') else '❌'}")
        print(f"   PR: {'✅' if result.get('pr_created') else '❌'}")
        if result.get('pr_number'):
            print(f"   PR Number: {result['pr_number']}")
        print()

    elif args.refactor:
        if args.refactor == "all":
            opportunities = manager.find_refactor_opportunities()
        else:
            opportunities = manager.find_refactor_opportunities(args.refactor)

        print(f"\n🔍 REFACTOR OPPORTUNITIES: {len(opportunities)}\n")
        for opp in opportunities[:10]:  # Show first 10
            print(f"   [{opp.get('source', 'unknown').upper()}] {opp.get('opportunity', opp.get('pattern', 'N/A'))}")
        print()

    elif args.list:
        print(f"\n📋 WORKFLOWS: {len(manager.workflows)}\n")
        for wf_id, wf in manager.workflows.items():
            print(f"   {wf.workflow_name} ({wf.workflow_type.value})")
            if wf_id in manager.git_mappings:
                mapping = manager.git_mappings[wf_id]
                print(f"      Branch: {mapping.branch_name}")
                if mapping.pr_number:
                    print(f"      PR: {mapping.pr_number}")
        print()

    else:
        print("Use --help for usage information\n")
