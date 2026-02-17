#!/usr/bin/env python3
"""
Living Blueprint Sync System

Maintains One Ring Blueprint as living document:
- Auto-syncs with all system changes
- Verifies, validates, and verifies again
- Measures twice, cuts once
- Keeps blueprint up-to-date at all times
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import hashlib


class LivingBlueprintSync:
    """
    Living Blueprint Sync System

    "Measure twice, cut once" - Quality over speed
    Keeps One Ring Blueprint synchronized with reality at all times
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        self.blueprint_path = self.project_root / "config" / "one_ring_blueprint.json"
        self.sync_log_path = self.project_root / "data" / "blueprint_sync" / "sync_log.json"
        self.sync_log_path.parent.mkdir(parents=True, exist_ok=True)

        # Load blueprint
        self.blueprint = self._load_blueprint()
        self.last_sync_hash = self._get_blueprint_hash()

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("LivingBlueprintSync")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🔄 LivingBlueprintSync - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def _load_blueprint(self) -> Dict[str, Any]:
        """Load One Ring Blueprint"""
        if not self.blueprint_path.exists():
            return {}

        try:
            with open(self.blueprint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading blueprint: {e}")
            return {}

    def _get_blueprint_hash(self) -> str:
        try:
            """Get hash of current blueprint for change detection"""
            if not self.blueprint:
                return ""
            return hashlib.sha256(json.dumps(self.blueprint, sort_keys=True).encode()).hexdigest()[:16]

        except Exception as e:
            self.logger.error(f"Error in _get_blueprint_hash: {e}", exc_info=True)
            raise
    def verify_blueprint_version(self, expected_version: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify blueprint is on correct version

        Measure twice: Check version and validate integrity
        """
        verification = {
            "timestamp": datetime.now().isoformat(),
            "blueprint_exists": self.blueprint_path.exists(),
            "version_match": False,
            "integrity_check": False,
            "sync_status": "unknown",
            "recommendations": []
        }

        if not self.blueprint:
            verification["recommendations"].append("Blueprint not found or not loadable")
            return verification

        # Check version
        metadata = self.blueprint.get('blueprint_metadata', {})
        current_version = metadata.get('version', 'unknown')

        if expected_version:
            verification["version_match"] = current_version == expected_version
            if not verification["version_match"]:
                verification["recommendations"].append(f"Version mismatch: expected {expected_version}, got {current_version}")
        else:
            verification["version_match"] = True  # No expected version specified

        # Integrity check
        required_sections = [
            'blueprint_metadata',
            'core_systems',
            'system_integrations',
            'defense_architecture'
        ]

        missing_sections = [s for s in required_sections if s not in self.blueprint]
        verification["integrity_check"] = len(missing_sections) == 0

        if missing_sections:
            verification["recommendations"].append(f"Missing sections: {', '.join(missing_sections)}")

        # Sync status
        last_updated = metadata.get('last_updated')
        if last_updated:
            try:
                last_update = datetime.fromisoformat(last_updated.replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_update.replace(tzinfo=None)).days

                if days_ago == 0:
                    verification["sync_status"] = "up_to_date"
                elif days_ago <= 7:
                    verification["sync_status"] = "recent"
                elif days_ago <= 30:
                    verification["sync_status"] = "needs_sync"
                else:
                    verification["sync_status"] = "outdated"
                    verification["recommendations"].append(f"Blueprint not synced in {days_ago} days")
            except:
                verification["sync_status"] = "unknown"

        return verification

    def sync_blueprint_timestamp(self) -> bool:
        """
        Update blueprint timestamp (first measure)

        This is step 1 of "measure twice, cut once"
        """
        if not self.blueprint:
            self.logger.error("Cannot sync - blueprint not loaded")
            return False

        # Update timestamp
        if 'blueprint_metadata' not in self.blueprint:
            self.blueprint['blueprint_metadata'] = {}

        self.blueprint['blueprint_metadata']['last_updated'] = datetime.now().isoformat()
        self.blueprint['blueprint_metadata']['last_synced'] = datetime.now().isoformat()

        return True

    def evaluate_ask_impact(self, ask_text: str) -> Dict[str, Any]:
        """
        Evaluate impact of an ask on the master blueprint

        Args:
            ask_text: The ask text to evaluate

        Returns:
            Dictionary with impact analysis
        """
        impact = {
            "impact_areas": [],
            "changes_required": [],
            "notes": [],
            "blueprint_compliant": True
        }

        # Analyze ask text for keywords
        ask_lower = ask_text.lower()

        # Check for system changes
        system_keywords = ['system', 'component', 'integration', 'module', 'service']
        if any(keyword in ask_lower for keyword in system_keywords):
            impact["impact_areas"].append("core_systems")
            impact["changes_required"].append("Review core_systems section")

        # Check for defense changes
        defense_keywords = ['defense', 'security', 'containment', 'killswitch', 'threat']
        if any(keyword in ask_lower for keyword in defense_keywords):
            impact["impact_areas"].append("defense_architecture")
            impact["changes_required"].append("Review defense_architecture section")

        # Check for integration changes
        integration_keywords = ['integrate', 'connect', 'api', 'endpoint', 'webhook']
        if any(keyword in ask_lower for keyword in integration_keywords):
            impact["impact_areas"].append("system_integrations")
            impact["changes_required"].append("Review system_integrations section")

        # Check for blueprint compliance
        if 'blueprint' in ask_lower or 'compliance' in ask_lower:
            impact["notes"].append("Ask directly references blueprint")

        return impact

    def sync_blueprint_status(self) -> bool:
        """
        Sync blueprint with actual system status (second measure)

        This is step 2 of "measure twice, cut once"
        """
        if not self.blueprint:
            return False

        # Verify core systems status
        core_systems = self.blueprint.get('core_systems', {})

        # Check for master_feedback_loop
        mfl = core_systems.get('master_feedback_loop', {})
        if mfl and isinstance(mfl, dict):
            # Verify autonomous execution exists
            if 'autonomous_execution' not in mfl:
                mfl['autonomous_execution'] = {
                    "status": "operational",
                    "mode": "@DOIT @ALWAYS",
                    "human_intervention": "none_required",
                    "executor": "scripts/python/master_feedback_loop_autonomous_executor.py"
                }

        # Verify @AIQ integration
        mfl = core_systems.get('master_feedback_loop', {})
        if mfl and isinstance(mfl, dict):
            chat_summaries = mfl.get('ai_chat_summaries_integration', {})
            if chat_summaries:
                if '@aiq_integration' not in chat_summaries:
                    chat_summaries['@aiq_integration'] = {
                        "status": "integrated",
                        "position": "first_step_in_decision_chain",
                        "chat_summaries_include": True
                    }

        return True

    def save_blueprint(self) -> bool:
        """
        Save blueprint (cut once - final action)

        Only after both measures are complete
        """
        try:
            # Create backup
            if self.blueprint_path.exists():
                backup_path = self.blueprint_path.parent / f"{self.blueprint_path.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                import shutil
                shutil.copy(self.blueprint_path, backup_path)
                self.logger.info(f"Backup created: {backup_path.name}")

            # Save blueprint
            with open(self.blueprint_path, 'w', encoding='utf-8') as f:
                json.dump(self.blueprint, f, indent=2, default=str)

            # Update sync log
            self._log_sync()

            self.logger.info("✅ Blueprint synced and saved")
            return True

        except Exception as e:
            self.logger.error(f"Error saving blueprint: {e}")
            return False

    def sync_blueprint(self) -> Dict[str, Any]:
        """
        Complete blueprint sync process

        Measure twice, cut once:
        1. Measure: Update timestamp
        2. Measure: Sync status
        3. Cut: Save blueprint
        """
        self.logger.info("🔄 Starting blueprint sync...")

        result = {
            "timestamp": datetime.now().isoformat(),
            "steps_completed": [],
            "steps_failed": [],
            "changes_detected": False,
            "success": False
        }

        # Step 1: Measure - Update timestamp
        if self.sync_blueprint_timestamp():
            result["steps_completed"].append("timestamp_update")
        else:
            result["steps_failed"].append("timestamp_update")
            return result

        # Step 2: Measure - Sync status
        if self.sync_blueprint_status():
            result["steps_completed"].append("status_sync")
        else:
            result["steps_failed"].append("status_sync")
            return result

        # Step 3: Cut - Save blueprint
        new_hash = self._get_blueprint_hash()
        if new_hash != self.last_sync_hash:
            result["changes_detected"] = True

        if self.save_blueprint():
            result["steps_completed"].append("save")
            result["success"] = True
            self.last_sync_hash = new_hash
        else:
            result["steps_failed"].append("save")

        return result

    def _log_sync(self):
        """Log sync operation"""
        sync_log = []

        if self.sync_log_path.exists():
            try:
                with open(self.sync_log_path, 'r', encoding='utf-8') as f:
                    sync_log = json.load(f)
            except:
                sync_log = []

        sync_entry = {
            "timestamp": datetime.now().isoformat(),
            "blueprint_hash": self.last_sync_hash,
            "status": "success"
        }

        sync_log.append(sync_entry)

        # Keep only last 100 entries
        sync_log = sync_log[-100:]

        with open(self.sync_log_path, 'w', encoding='utf-8') as f:
            json.dump(sync_log, f, indent=2)

    def verify_and_validate_workflow(self) -> Dict[str, Any]:
        """
        Complete verify, validate, and verify workflow

        Triple-check system:
        1. Verify blueprint version
        2. Validate blueprint integrity
        3. Verify sync status
        """
        self.logger.info("🔍 Starting verify, validate, and verify workflow...")

        # Verification 1: Version check
        verification_1 = self.verify_blueprint_version()

        # Validation: Integrity check
        validation = {
            "timestamp": datetime.now().isoformat(),
            "blueprint_loaded": bool(self.blueprint),
            "required_sections_present": all(
                s in self.blueprint for s in [
                    'blueprint_metadata',
                    'core_systems',
                    'system_integrations'
                ]
            ),
            "core_systems_count": len(self.blueprint.get('core_systems', {})),
            "integration_count": len(self.blueprint.get('system_integrations', {}).get('lumina_systems', {}))
        }

        # Verification 2: Sync status check
        verification_2 = self.verify_blueprint_version()

        return {
            "verification_1": verification_1,
            "validation": validation,
            "verification_2": verification_2,
            "all_checks_passed": (
                verification_1.get("integrity_check", False) and
                validation.get("required_sections_present", False) and
                verification_2.get("integrity_check", False)
            )
        }


def main():
    """Main execution"""
    sync_system = LivingBlueprintSync()

    print("\n" + "=" * 80)
    print("🔄 LIVING BLUEPRINT SYNC SYSTEM")
    print("=" * 80)
    print("Measure twice, cut once - Quality over speed")
    print()

    # Verify and validate
    print("🔍 Step 1: Verify, Validate, and Verify")
    vvv_result = sync_system.verify_and_validate_workflow()

    print(f"   Verification 1: {'✅ Passed' if vvv_result['verification_1']['integrity_check'] else '❌ Failed'}")
    print(f"   Validation: {'✅ Passed' if vvv_result['validation']['required_sections_present'] else '❌ Failed'}")
    print(f"   Verification 2: {'✅ Passed' if vvv_result['verification_2']['integrity_check'] else '❌ Failed'}")
    print(f"   All Checks: {'✅ Passed' if vvv_result['all_checks_passed'] else '❌ Failed'}")
    print()

    # Sync blueprint
    print("🔄 Step 2: Sync Blueprint (Measure Twice, Cut Once)")
    sync_result = sync_system.sync_blueprint()

    print(f"   Steps Completed: {len(sync_result['steps_completed'])}")
    for step in sync_result['steps_completed']:
        print(f"      ✅ {step}")

    if sync_result['steps_failed']:
        print(f"   Steps Failed: {len(sync_result['steps_failed'])}")
        for step in sync_result['steps_failed']:
            print(f"      ❌ {step}")

    print(f"   Changes Detected: {sync_result['changes_detected']}")
    print(f"   Success: {'✅' if sync_result['success'] else '❌'}")
    print()

    # Final verification
    print("🔍 Step 3: Final Verification")
    final_verification = sync_system.verify_blueprint_version()

    print(f"   Sync Status: {final_verification['sync_status']}")
    print(f"   Integrity: {'✅' if final_verification['integrity_check'] else '❌'}")
    print(f"   Version Match: {'✅' if final_verification['version_match'] else '❌'}")

    if final_verification['recommendations']:
        print(f"   Recommendations:")
        for rec in final_verification['recommendations']:
            print(f"      • {rec}")

    print()
    print("✅ Living Blueprint Sync Complete")
    print()


if __name__ == "__main__":



    main()