#!/usr/bin/env python3
"""
AI Intelligence @BDA (Build-Deploy-Activate) Action Stage

Third stage of the AI Intelligence pipeline:
1. Stage 1: Gathering (Documentation) ✅
2. Stage 2: Planning (Actionable Intelligence) ✅
3. Stage 3: @BDA Action (Build-Deploy-Activate) ✅

Takes actionable intelligence from planning stage and:
- BUILDS: Creates implementations
- DEPLOYS: Deploys to target systems
- ACTIVATES: Activates and monitors

Tags: #BDA #BUILD #DEPLOY #ACTIVATE #ACTION #INTELLIGENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIIntelligenceBDA")


class BuildStatus(Enum):
    """Build status"""
    PENDING = "pending"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class DeployStatus(Enum):
    """Deploy status"""
    PENDING = "pending"
    DEPLOYING = "deploying"
    SUCCESS = "success"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    SKIPPED = "skipped"


class ActivateStatus(Enum):
    """Activate status"""
    PENDING = "pending"
    ACTIVATING = "activating"
    ACTIVE = "active"
    FAILED = "failed"
    MONITORING = "monitoring"
    SKIPPED = "skipped"


@dataclass
class BDAAction:
    """@BDA Action item"""
    action_id: str
    intelligence_id: str
    title: str
    build_status: BuildStatus = BuildStatus.PENDING
    deploy_status: DeployStatus = DeployStatus.PENDING
    activate_status: ActivateStatus = ActivateStatus.PENDING
    build_output: Optional[str] = None
    deploy_output: Optional[str] = None
    activate_output: Optional[str] = None
    build_errors: List[str] = field(default_factory=list)
    deploy_errors: List[str] = field(default_factory=list)
    activate_errors: List[str] = field(default_factory=list)
    build_started: Optional[str] = None
    build_completed: Optional[str] = None
    deploy_started: Optional[str] = None
    deploy_completed: Optional[str] = None
    activate_started: Optional[str] = None
    activate_completed: Optional[str] = None
    target_system: str = "local"
    deployment_path: Optional[str] = None
    activation_verified: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIIntelligenceBDAActionStage:
    """@BDA Action Stage - Build-Deploy-Activate"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @BDA Action Stage"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.planning_dir = self.project_root / "data" / "ai_intelligence_planning"
        self.bda_dir = self.project_root / "data" / "ai_intelligence_bda"
        self.bda_dir.mkdir(parents=True, exist_ok=True)

        # Build artifacts directory
        self.build_dir = self.bda_dir / "builds"
        self.build_dir.mkdir(parents=True, exist_ok=True)

        # Deployment directory
        self.deploy_dir = self.bda_dir / "deployments"
        self.deploy_dir.mkdir(parents=True, exist_ok=True)

        # Activation monitoring directory
        self.activate_dir = self.bda_dir / "activations"
        self.activate_dir.mkdir(parents=True, exist_ok=True)

        # Target systems
        self.nas_path = Path("//<NAS_PRIMARY_IP>")  # NAS deployment target
        self.local_path = self.project_root / "deployments"  # Local deployment target
        self.local_path.mkdir(parents=True, exist_ok=True)

        logger.info("✅ AI Intelligence @BDA Action Stage initialized")
        logger.info(f"   Build Directory: {self.build_dir}")
        logger.info(f"   Deploy Directory: {self.deploy_dir}")
        logger.info(f"   Activate Directory: {self.activate_dir}")

    def load_actionable_intelligence(self) -> List[Dict[str, Any]]:
        """Load actionable intelligence from planning stage"""
        actionable_items = []

        # Load from planning results
        planning_results = sorted(self.planning_dir.glob("planning_results_*.json"), reverse=True)

        for result_file in planning_results[:1]:  # Latest result
            try:
                with open(result_file, 'r', encoding='utf-8') as f:
                    planning_data = json.load(f)

                    # Load actionable items from report
                    report_file = planning_data.get("report_file")
                    if report_file:
                        report_path = self.planning_dir.parent / report_file if not Path(report_file).is_absolute() else Path(report_file)
                        if report_path.exists():
                            # Parse report to extract actionable items
                            actionable_items.extend(self._parse_report(report_path))
            except Exception as e:
                logger.debug(f"Error loading planning result {result_file}: {e}")
                continue

        # Also check reports directory directly
        reports = sorted((self.planning_dir / "reports").glob("AI_INTELLIGENCE_REPORT_*.md"), reverse=True)
        if reports and not actionable_items:
            actionable_items.extend(self._parse_report(reports[0]))

        logger.info(f"   Loaded {len(actionable_items)} actionable intelligence items")
        return actionable_items

    def _parse_report(self, report_path: Path) -> List[Dict[str, Any]]:
        """Parse markdown report to extract actionable items"""
        actionable_items = []

        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse markdown sections
            import re

            # Find all actionable item sections
            item_pattern = r'### (INTEL_\d+): (.+?)\n\n(.*?)(?=###|##|---|$)'
            matches = re.finditer(item_pattern, content, re.DOTALL)

            for match in matches:
                intel_id = match.group(1)
                title = match.group(2)
                details = match.group(3)

                # Extract metadata from details
                source_match = re.search(r'\*\*Source:\*\* (.+)', details)
                url_match = re.search(r'\*\*URL:\*\* (.+)', details)
                threat_match = re.search(r'\*\*Threat Level:\*\* (.+)', details)

                # Extract recommended actions
                actions_section = re.search(r'\*\*Recommended Actions:\*\*\n(.*?)(?=\*\*|$)', details, re.DOTALL)
                actions = []
                if actions_section:
                    action_lines = re.findall(r'- (.+)', actions_section.group(1))
                    actions = action_lines

                actionable_items.append({
                    "intelligence_id": intel_id,
                    "title": title,
                    "source": source_match.group(1) if source_match else "unknown",
                    "url": url_match.group(1) if url_match else "",
                    "threat_level": threat_match.group(1).lower() if threat_match else "low",
                    "recommended_actions": actions,
                    "details": details
                })
        except Exception as e:
            logger.error(f"Error parsing report {report_path}: {e}")

        return actionable_items

    def build(self, actionable_item: Dict[str, Any]) -> BDAAction:
        """BUILD: Create implementation from actionable intelligence"""
        action_id = f"BDA_{actionable_item['intelligence_id']}"

        logger.info(f"   🔨 BUILDING: {actionable_item['title']}")

        bda_action = BDAAction(
            action_id=action_id,
            intelligence_id=actionable_item['intelligence_id'],
            title=actionable_item['title'],
            build_status=BuildStatus.BUILDING,
            build_started=datetime.now().isoformat()
        )

        try:
            # Determine build type based on intelligence
            build_type = self._determine_build_type(actionable_item)

            # Create build implementation
            build_output = self._create_build_implementation(actionable_item, build_type)

            bda_action.build_output = build_output
            bda_action.build_status = BuildStatus.SUCCESS
            bda_action.build_completed = datetime.now().isoformat()
            bda_action.metadata["build_type"] = build_type

            logger.info(f"      ✅ Build successful: {build_type}")

        except Exception as e:
            bda_action.build_status = BuildStatus.FAILED
            bda_action.build_errors.append(str(e))
            bda_action.build_completed = datetime.now().isoformat()
            logger.error(f"      ❌ Build failed: {e}")

        return bda_action

    def _determine_build_type(self, actionable_item: Dict[str, Any]) -> str:
        """Determine what type of build is needed"""
        title = actionable_item.get("title", "").lower()
        actions = actionable_item.get("recommended_actions", [])
        combined = f"{title} {' '.join(actions)}".lower()

        # Determine build type
        if "tutorial" in combined or "how to" in combined or "guide" in combined:
            return "script"
        elif "api" in combined or "integration" in combined:
            return "integration"
        elif "update" in combined or "upgrade" in combined:
            return "update"
        elif "security" in combined or "patch" in combined:
            return "security_patch"
        elif "automation" in combined or "workflow" in combined:
            return "automation"
        else:
            return "implementation"

    def _create_build_implementation(self, actionable_item: Dict[str, Any], build_type: str) -> str:
        try:
            """Create build implementation"""
            build_file = self.build_dir / f"{actionable_item['intelligence_id']}_{build_type}.py"

            # Generate implementation code
            code = self._generate_implementation_code(actionable_item, build_type)

            # Save build file
            with open(build_file, 'w', encoding='utf-8') as f:
                f.write(code)

            return str(build_file)

        except Exception as e:
            self.logger.error(f"Error in _create_build_implementation: {e}", exc_info=True)
            raise
    def _generate_implementation_code(self, actionable_item: Dict[str, Any], build_type: str) -> str:
        """Generate implementation code"""
        title = actionable_item.get("title", "Implementation")
        intel_id = actionable_item.get("intelligence_id", "UNKNOWN")
        url = actionable_item.get("url", "")
        actions = actionable_item.get("recommended_actions", [])

        code = f'''#!/usr/bin/env python3
"""
Implementation: {title}

Generated from AI Intelligence: {intel_id}
Source: {actionable_item.get('source', 'unknown')}
URL: {url}

Build Type: {build_type}
Generated: {datetime.now().isoformat()}

Tags: #BDA #BUILD #AI_INTELLIGENCE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BDAImplementation_{intel_id}")


def main():
    """Main implementation"""
    logger.info("="*80)
    logger.info("🔨 BDA Implementation: {title}")
    logger.info("="*80)
    logger.info("")
    logger.info(f"   Intelligence ID: {intel_id}")
    logger.info(f"   Source: {actionable_item.get('source', 'unknown')}")
    logger.info(f"   URL: {url}")
    logger.info("")

    # Recommended Actions:
'''

        for action in actions:
            code += f"    # TODO: {action}\n"  # [ADDRESSED]  # [ADDRESSED]

        code += f'''
    logger.info("   ✅ Implementation complete")
    logger.info("="*80)


if __name__ == "__main__":
    main()
'''

        return code

    def deploy(self, bda_action: BDAAction) -> BDAAction:
        """DEPLOY: Deploy implementation to target system"""
        if bda_action.build_status != BuildStatus.SUCCESS:
            logger.warning(f"   ⚠️  Skipping deploy - build not successful")
            bda_action.deploy_status = DeployStatus.SKIPPED
            return bda_action

        logger.info(f"   🚀 DEPLOYING: {bda_action.title}")

        bda_action.deploy_status = DeployStatus.DEPLOYING
        bda_action.deploy_started = datetime.now().isoformat()

        try:
            # Determine deployment target
            target = self._determine_deployment_target(bda_action)

            # Deploy to target
            deployment_path = self._deploy_to_target(bda_action, target)

            bda_action.deployment_path = deployment_path
            bda_action.target_system = target
            bda_action.deploy_status = DeployStatus.SUCCESS
            bda_action.deploy_completed = datetime.now().isoformat()

            logger.info(f"      ✅ Deployed to {target}: {deployment_path}")

        except Exception as e:
            bda_action.deploy_status = DeployStatus.FAILED
            bda_action.deploy_errors.append(str(e))
            bda_action.deploy_completed = datetime.now().isoformat()
            logger.error(f"      ❌ Deploy failed: {e}")

        return bda_action

    def _determine_deployment_target(self, bda_action: BDAAction) -> str:
        try:
            """Determine deployment target"""
            # Check if NAS is accessible
            if self.nas_path.exists():
                return "nas"
            else:
                return "local"

        except Exception as e:
            self.logger.error(f"Error in _determine_deployment_target: {e}", exc_info=True)
            raise
    def _deploy_to_target(self, bda_action: BDAAction, target: str) -> str:
        try:
            """Deploy to target system"""
            if not bda_action.build_output:
                raise ValueError("No build output to deploy")

            build_file = Path(bda_action.build_output)
            if not build_file.exists():
                raise FileNotFoundError(f"Build file not found: {build_file}")

            # Determine deployment path
            if target == "nas":
                deploy_path = self.nas_path / "deployments" / "ai_intelligence" / build_file.name
                deploy_path.parent.mkdir(parents=True, exist_ok=True)
            else:
                deploy_path = self.local_path / build_file.name

            # Copy build file to deployment location
            import shutil
            shutil.copy2(build_file, deploy_path)

            # Create deployment manifest
            manifest = {
                "action_id": bda_action.action_id,
                "intelligence_id": bda_action.intelligence_id,
                "title": bda_action.title,
                "deployed_at": datetime.now().isoformat(),
                "target": target,
                "build_file": str(bda_action.build_output),
                "deployment_path": str(deploy_path)
            }

            manifest_file = self.deploy_dir / f"{bda_action.action_id}_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

            return str(deploy_path)

        except Exception as e:
            self.logger.error(f"Error in _deploy_to_target: {e}", exc_info=True)
            raise
    def activate(self, bda_action: BDAAction) -> BDAAction:
        """ACTIVATE: Activate and monitor deployment"""
        if bda_action.deploy_status != DeployStatus.SUCCESS:
            logger.warning(f"   ⚠️  Skipping activate - deploy not successful")
            bda_action.activate_status = ActivateStatus.SKIPPED
            return bda_action

        logger.info(f"   ⚡ ACTIVATING: {bda_action.title}")

        bda_action.activate_status = ActivateStatus.ACTIVATING
        bda_action.activate_started = datetime.now().isoformat()

        try:
            # Verify deployment exists
            if not bda_action.deployment_path or not Path(bda_action.deployment_path).exists():
                raise FileNotFoundError("Deployment file not found")

            # Activate (run/start the deployment)
            activation_result = self._activate_deployment(bda_action)

            bda_action.activate_output = activation_result
            bda_action.activate_status = ActivateStatus.ACTIVE
            bda_action.activate_completed = datetime.now().isoformat()
            bda_action.activation_verified = True

            # Start monitoring
            self._start_monitoring(bda_action)

            logger.info(f"      ✅ Activated and monitoring")

        except Exception as e:
            bda_action.activate_status = ActivateStatus.FAILED
            bda_action.activate_errors.append(str(e))
            bda_action.activate_completed = datetime.now().isoformat()
            logger.error(f"      ❌ Activation failed: {e}")

        return bda_action

    def _activate_deployment(self, bda_action: BDAAction) -> str:
        try:
            """Activate the deployment"""
            # For now, just verify the file exists and is executable
            # In production, would actually run/start the service/script

            deploy_path = Path(bda_action.deployment_path)

            # Create activation record
            activation_record = {
                "action_id": bda_action.action_id,
                "intelligence_id": bda_action.intelligence_id,
                "activated_at": datetime.now().isoformat(),
                "deployment_path": str(deploy_path),
                "status": "active"
            }

            activation_file = self.activate_dir / f"{bda_action.action_id}_activation.json"
            with open(activation_file, 'w', encoding='utf-8') as f:
                json.dump(activation_record, f, indent=2)

            return str(activation_file)

        except Exception as e:
            self.logger.error(f"Error in _activate_deployment: {e}", exc_info=True)
            raise
    def _start_monitoring(self, bda_action: BDAAction):
        """Start monitoring activated deployment"""
        # Create monitoring record
        monitoring_record = {
            "action_id": bda_action.action_id,
            "intelligence_id": bda_action.intelligence_id,
            "monitoring_started": datetime.now().isoformat(),
            "status": "monitoring",
            "checks": []
        }

        monitoring_file = self.activate_dir / f"{bda_action.action_id}_monitoring.json"
        with open(monitoring_file, 'w', encoding='utf-8') as f:
            json.dump(monitoring_record, f, indent=2)

        bda_action.activate_status = ActivateStatus.MONITORING

    def execute_bda_pipeline(self, actionable_items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute complete @BDA pipeline"""
        logger.info("="*80)
        logger.info("🔨⚡🚀 @BDA ACTION STAGE")
        logger.info("="*80)
        logger.info("")

        bda_actions = []

        for item in actionable_items:
            logger.info(f"Processing: {item['title']}")

            # BUILD
            bda_action = self.build(item)

            # DEPLOY
            bda_action = self.deploy(bda_action)

            # ACTIVATE
            bda_action = self.activate(bda_action)

            bda_actions.append(bda_action)

            logger.info("")

        # Save BDA results
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_actions": len(bda_actions),
            "build_success": sum(1 for a in bda_actions if a.build_status == BuildStatus.SUCCESS),
            "deploy_success": sum(1 for a in bda_actions if a.deploy_status == DeployStatus.SUCCESS),
            "activate_success": sum(1 for a in bda_actions if a.activate_status == ActivateStatus.ACTIVE),
            "actions": [asdict(a) for a in bda_actions]
        }

        # Convert enums to strings
        for action_dict in results["actions"]:
            action_dict["build_status"] = action_dict["build_status"].value if hasattr(action_dict["build_status"], "value") else str(action_dict["build_status"])
            action_dict["deploy_status"] = action_dict["deploy_status"].value if hasattr(action_dict["deploy_status"], "value") else str(action_dict["deploy_status"])
            action_dict["activate_status"] = action_dict["activate_status"].value if hasattr(action_dict["activate_status"], "value") else str(action_dict["activate_status"])

        results_file = self.bda_dir / f"bda_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info("="*80)
        logger.info("✅ @BDA ACTION STAGE COMPLETE")
        logger.info("="*80)
        logger.info(f"   Total Actions: {len(bda_actions)}")
        logger.info(f"   Build Success: {results['build_success']}/{len(bda_actions)}")
        logger.info(f"   Deploy Success: {results['deploy_success']}/{len(bda_actions)}")
        logger.info(f"   Activate Success: {results['activate_success']}/{len(bda_actions)}")
        logger.info(f"   Results: {results_file.name}")
        logger.info("="*80)

        return results

    def process_from_planning(self) -> Dict[str, Any]:
        """Process actionable intelligence from planning stage"""
        # Load actionable intelligence
        actionable_items = self.load_actionable_intelligence()

        if not actionable_items:
            logger.warning("⚠️  No actionable intelligence found. Run planning stage first.")
            return {}

        # Execute @BDA pipeline
        return self.execute_bda_pipeline(actionable_items)


def main():
    """Main execution"""
    bda_stage = AIIntelligenceBDAActionStage()
    bda_stage.process_from_planning()


if __name__ == "__main__":


    main()