#!/usr/bin/env python3
"""
@V3 Verification: Cloud Storage Migration to NAS LOCAL-CLOUD-STORAGE
Verifies all cloud storage providers have been migrated correctly

Tags: #V3 #VERIFICATION #CLOUD_STORAGE #NAS_MIGRATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from v3_verification import V3Verification, VerificationResult, V3VerificationConfig
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    # Fallback V3 classes
    class VerificationResult:
        def __init__(self, step_name, passed, message, details=None):
            self.step_name = step_name
            self.passed = passed
            self.message = message
            self.details = details or {}

    class V3Verification:
        def __init__(self, config=None):
            self.verification_results = []

        def verify_data_integrity(self, data, data_type="generic"):
            return VerificationResult("data_integrity", True, "Verified")

logger = get_logger("V3CloudStorageVerification")


class V3CloudStorageVerification:
    """@V3: Verify cloud storage migration to NAS LOCAL-CLOUD-STORAGE"""

    def __init__(self):
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_base = f"\\\\{self.nas_ip}"
        self.local_cloud_storage = Path(f"{self.nas_base}\\backups\\LOCAL-CLOUD-STORAGE")

        self.cloud_providers = [
            {
                "name": "Dropbox",
                "source": Path("C:\\Users\\mlesn\\Dropbox"),
                "target": self.local_cloud_storage / "Dropbox",
                "expected_size_gb": 4605.35
            },
            {
                "name": "OneDrive",
                "source": Path("C:\\Users\\mlesn\\OneDrive"),
                "target": self.local_cloud_storage / "OneDrive",
                "expected_size_gb": 67.97
            }
        ]

        self.v3_verifier = V3Verification()

    def get_directory_size(self, path: Path) -> float:
        """Get directory size in GB"""
        if not path.exists():
            return 0.0

        import os
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for filename in filenames:
                    filepath = Path(dirpath) / filename
                    try:
                        total_size += filepath.stat().st_size
                    except (OSError, PermissionError):
                        pass
        except (OSError, PermissionError):
            pass

        return total_size / (1024**3)

    def verify_provider_migration(self, provider: Dict) -> VerificationResult:
        try:
            """Verify a single cloud storage provider migration"""
            name = provider["name"]
            source = provider["source"]
            target = provider["target"]
            expected_size = provider.get("expected_size_gb", 0)

            logger.info(f"🔍 Verifying {name} migration...")
            logger.info(f"   Source: {source}")
            logger.info(f"   Target: {target}")

            details = {
                "provider": name,
                "source_path": str(source),
                "target_path": str(target)
            }

            issues = []

            # Check if target exists
            if not target.exists():
                issues.append(f"Target directory does not exist: {target}")
                details["target_exists"] = False
            else:
                details["target_exists"] = True

            # Check source size
            source_size = self.get_directory_size(source)
            details["source_size_gb"] = source_size

            # Check target size
            target_size = self.get_directory_size(target)
            details["target_size_gb"] = target_size

            # Verify sizes match (allow 5% difference)
            if source_size > 0 and target_size > 0:
                ratio = target_size / source_size if source_size > 0 else 0
                details["size_ratio"] = ratio

                if ratio < 0.95:
                    issues.append(f"Target size too small: {target_size:.2f} GB vs {source_size:.2f} GB (ratio: {ratio:.2%})")
                elif ratio > 1.05:
                    issues.append(f"Target size too large: {target_size:.2f} GB vs {source_size:.2f} GB (ratio: {ratio:.2%})")
                else:
                    details["size_match"] = True
            elif source_size > 0 and target_size == 0:
                issues.append(f"Target is empty but source has {source_size:.2f} GB")
            elif source_size == 0 and target_size > 0:
                details["source_migrated"] = True
                logger.info(f"   ✅ Source appears to be migrated (empty)")

            # Check if source should be cleaned up
            if source_size > expected_size * 0.1:  # More than 10% of expected size remaining
                details["source_cleanup_needed"] = True
                issues.append(f"Source still has {source_size:.2f} GB (should be cleaned up)")
            else:
                details["source_cleanup_complete"] = True

            passed = len(issues) == 0
            message = f"{name} migration verified" if passed else f"{name} migration issues: {', '.join(issues)}"

            result = VerificationResult(
                step_name=f"verify_{name.lower()}_migration",
                passed=passed,
                message=message,
                details=details
            )

            self.v3_verifier.verification_results.append(result)
            return result

        except Exception as e:
            self.logger.error(f"Error in verify_provider_migration: {e}", exc_info=True)
            raise
    def verify_nas_structure(self) -> VerificationResult:
        try:
            """Verify NAS LOCAL-CLOUD-STORAGE structure exists"""
            logger.info("🔍 Verifying NAS LOCAL-CLOUD-STORAGE structure...")

            details = {
                "nas_base": str(self.nas_base),
                "local_cloud_storage": str(self.local_cloud_storage)
            }

            issues = []

            # Check if NAS base is accessible
            if not Path(self.nas_base).exists():
                issues.append(f"NAS base not accessible: {self.nas_base}")
                details["nas_accessible"] = False
            else:
                details["nas_accessible"] = True

            # Check if LOCAL-CLOUD-STORAGE exists
            if not self.local_cloud_storage.exists():
                issues.append(f"LOCAL-CLOUD-STORAGE not found: {self.local_cloud_storage}")
                details["local_cloud_storage_exists"] = False
            else:
                details["local_cloud_storage_exists"] = True

                # Check provider directories
                for provider in self.cloud_providers:
                    provider_target = provider["target"]
                    if provider_target.exists():
                        details[f"{provider['name'].lower()}_target_exists"] = True
                    else:
                        details[f"{provider['name'].lower()}_target_exists"] = False
                        issues.append(f"{provider['name']} target directory not found: {provider_target}")

            passed = len(issues) == 0
            message = "NAS structure verified" if passed else f"NAS structure issues: {', '.join(issues)}"

            result = VerificationResult(
                step_name="verify_nas_structure",
                passed=passed,
                message=message,
                details=details
            )

            self.v3_verifier.verification_results.append(result)
            return result

        except Exception as e:
            self.logger.error(f"Error in verify_nas_structure: {e}", exc_info=True)
            raise
    def run_full_verification(self) -> Dict:
        """@V3: Run full verification suite"""
        logger.info("=" * 80)
        logger.info("@V3: CLOUD STORAGE MIGRATION VERIFICATION")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "verifications": [],
            "summary": {}
        }

        # Step 1: Verify NAS structure
        logger.info("📋 Step 1: Verifying NAS structure...")
        nas_result = self.verify_nas_structure()
        results["verifications"].append({
            "step": nas_result.step_name,
            "passed": nas_result.passed,
            "message": nas_result.message,
            "details": nas_result.details
        })
        logger.info(f"   {'✅' if nas_result.passed else '❌'} {nas_result.message}")
        logger.info("")

        # Step 2: Verify each provider migration
        for provider in self.cloud_providers:
            logger.info(f"📋 Step 2: Verifying {provider['name']} migration...")
            provider_result = self.verify_provider_migration(provider)
            results["verifications"].append({
                "step": provider_result.step_name,
                "passed": provider_result.passed,
                "message": provider_result.message,
                "details": provider_result.details
            })
            logger.info(f"   {'✅' if provider_result.passed else '❌'} {provider_result.message}")
            logger.info("")

        # Summary
        total_verifications = len(results["verifications"])
        passed = sum(1 for v in results["verifications"] if v["passed"])
        failed = total_verifications - passed

        results["summary"] = {
            "total_verifications": total_verifications,
            "passed": passed,
            "failed": failed,
            "all_passed": failed == 0
        }

        logger.info("=" * 80)
        logger.info("📊 @V3 VERIFICATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total verifications: {total_verifications}")
        logger.info(f"Passed: {passed}")
        logger.info(f"Failed: {failed}")
        logger.info(f"Status: {'✅ ALL PASSED' if results['summary']['all_passed'] else '❌ SOME FAILED'}")
        logger.info("=" * 80)

        return results


def main():
    """Main entry point"""
    verifier = V3CloudStorageVerification()
    results = verifier.run_full_verification()

    print("\n" + "=" * 80)
    print("@V3: CLOUD STORAGE MIGRATION VERIFICATION COMPLETE")
    print("=" * 80)
    print(f"Status: {'✅ ALL PASSED' if results['summary']['all_passed'] else '❌ SOME FAILED'}")
    print(f"Passed: {results['summary']['passed']}/{results['summary']['total_verifications']}")
    print()


if __name__ == "__main__":


    main()