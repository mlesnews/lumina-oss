"""
PUBLIC: NAS Migration Status Checker
Location: scripts/python/nas_migration_status.py
License: MIT

Checks status of NAS migration and related request IDs.
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class NASMigrationStatus:
    """Check NAS migration status."""

    def __init__(self, project_root: Path):
        """
        Initialize status checker.

        Args:
            project_root: Path to project root
        """
        self.project_root = project_root
        self.data_path = project_root / "data"
        self.config_path = project_root / "config"

    def get_migration_plan_status(self) -> Dict[str, Any]:
        """
        Get status from migration plan.

        Returns:
            Migration plan status
        """
        plan_file = self.data_path / "system" / "nas_migration_plan.json"

        if not plan_file.exists():
            return {
                "available": False,
                "error": "Migration plan not found"
            }

        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan = json.load(f)

            return {
                "available": True,
                "timestamp": plan.get("timestamp"),
                "network_drives_status": plan.get("network_drives", {}).get("status", "UNKNOWN"),
                "migration_candidates": plan.get("migration_candidates", {}),
                "steps": plan.get("steps", []),
                "total_size_gb": plan.get("estimated_space_freed_gb", 0),
                "raw_data": plan
            }
        except Exception as e:
            logger.error(f"Failed to read migration plan: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def check_nas_accessibility(self) -> Dict[str, Any]:
        """
        Check if NAS is actually accessible.

        Returns:
            NAS accessibility status
        """
        import os
        nas_path = r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups"

        try:
            accessible = os.path.exists(nas_path)
            return {
                "accessible": accessible,
                "path": nas_path,
                "method": "os.path.exists"
            }
        except Exception as e:
            return {
                "accessible": False,
                "path": nas_path,
                "error": str(e)
            }

    def check_azure_vault_credentials(self) -> Dict[str, Any]:
        """
        Check if Azure Vault credentials are available via TRIAD.

        Returns:
            Azure Vault credential status
        """
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration

            integration = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
            credentials = integration.get_nas_credentials()

            return {
                "available": credentials is not None,
                "has_username": credentials.get("username") is not None if credentials else False,
                "has_password": credentials.get("password") is not None if credentials else False,
                "source": "Azure Key Vault via TRIAD"
            }
        except ImportError:
            return {
                "available": False,
                "error": "nas_azure_vault_integration module not available"
            }
        except Exception as e:
            return {
                "available": False,
                "error": str(e)
            }

    def get_doit_execution_status(self) -> Dict[str, Any]:
        """
        Get status from DOIT execution document.

        Returns:
            DOIT execution status
        """
        doit_file = self.project_root / "DOIT_NAS_MIGRATION_EXECUTED.md"

        if not doit_file.exists():
            return {
                "available": False,
                "error": "DOIT execution document not found"
            }

        try:
            content = doit_file.read_text(encoding="utf-8")

            # Extract key information
            status = {
                "available": True,
                "executed": "EXECUTED" in content and "Dry Run" in content,
                "dry_run": "Dry Run" in content,
                "blocking_issue": None,
                "files_to_migrate": None,
                "size_to_migrate": None,
                "target_path": None,
                "source_path": None
            }

            # Extract details
            if "24,226 files" in content:
                status["files_to_migrate"] = 24226
            if "3.73 GB" in content:
                status["size_to_migrate"] = "3.73 GB"
            if "\\<NAS_PRIMARY_IP>" in content:
                status["target_path"] = "\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\my_projects\\.lumina"
            if "C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina" in content:
                status["source_path"] = "C:\\Users\\mlesn\\Dropbox\\my_projects\\.lumina"

            # Check actual NAS accessibility (not just what document says)
            nas_status = self.check_nas_accessibility()
            if nas_status.get("accessible"):
                status["blocking_issue"] = None  # NAS is accessible!
            elif "NAS authentication required" in content:
                status["blocking_issue"] = "NAS authentication required (but may be accessible via Azure Vault)"

            return status
        except Exception as e:
            logger.error(f"Failed to read DOIT execution: {e}", exc_info=True)
            return {
                "available": False,
                "error": str(e)
            }

    def search_request_ids(self, request_ids: List[str]) -> Dict[str, Any]:
        """
        Search for request IDs in diagnostics.

        Args:
            request_ids: List of request IDs to search for

        Returns:
            Request ID search results
        """
        diagnostics_path = self.data_path / "diagnostics"

        if not diagnostics_path.exists():
            return {
                "available": False,
                "error": "Diagnostics directory not found"
            }

        results = {
            "available": True,
            "request_ids": {},
            "files_found": []
        }

        for request_id in request_ids:
            request_id_results = {
                "found": False,
                "files": []
            }

            # Search for files containing this request ID
            pattern = f"*{request_id}*"
            matching_files = list(diagnostics_path.glob(pattern))

            if matching_files:
                request_id_results["found"] = True
                for file in matching_files:
                    request_id_results["files"].append({
                        "path": str(file),
                        "name": file.name,
                        "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
                    })

                    # Try to read file content
                    try:
                        with open(file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            request_id_results["file_data"] = data
                    except Exception:
                        pass

            results["request_ids"][request_id] = request_id_results
            if request_id_results["found"]:
                results["files_found"].extend(request_id_results["files"])

        return results

    def get_comprehensive_status(
        self,
        request_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get comprehensive NAS migration status.

        Args:
            request_ids: Optional list of request IDs to check

        Returns:
            Comprehensive status
        """
        status = {
            "generated_at": datetime.now().isoformat(),
            "project": "LUMINA",
            "migration_plan": {},
            "doit_execution": {},
            "request_ids": {}
        }

        # Get migration plan status
        logger.info("Checking migration plan status...")
        status["migration_plan"] = self.get_migration_plan_status()

        # Get DOIT execution status
        logger.info("Checking DOIT execution status...")
        status["doit_execution"] = self.get_doit_execution_status()

        # Check actual NAS accessibility
        logger.info("Checking NAS accessibility...")
        status["nas_accessibility"] = self.check_nas_accessibility()

        # Check Azure Vault credentials via TRIAD
        logger.info("Checking Azure Vault credentials via TRIAD...")
        status["azure_vault_credentials"] = self.check_azure_vault_credentials()

        # Search for request IDs if provided
        if request_ids:
            logger.info(f"Searching for request IDs: {request_ids}")
            status["request_ids"] = self.search_request_ids(request_ids)

        return status

    def print_status(self, status: Dict[str, Any]):
        """Print formatted status."""
        print("\n" + "=" * 80)
        print("NAS MIGRATION STATUS - LUMINA")
        print("=" * 80)
        print(f"Generated: {status['generated_at']}")
        print()

        # Migration Plan
        print("-" * 80)
        print("1. MIGRATION PLAN STATUS")
        print("-" * 80)
        plan = status.get("migration_plan", {})
        if plan.get("available", False):
            print(f"   Status: ✅ Available")
            print(f"   Timestamp: {plan.get('timestamp', 'Unknown')}")
            print(f"   Network Drives: {plan.get('network_drives_status', 'UNKNOWN')}")
            print(f"   Total Size: {plan.get('total_size_gb', 0):.2f} GB")

            steps = plan.get("steps", [])
            if steps:
                print(f"   Steps:")
                for step in steps:
                    step_num = step.get("step", 0)
                    action = step.get("action", "Unknown")
                    step_status = step.get("status", "UNKNOWN")
                    status_icon = "✅" if step_status == "COMPLETED" else "⏳" if step_status == "IN_PROGRESS" else "⏸️"
                    print(f"     {status_icon} Step {step_num}: {action} - {step_status}")
        else:
            print(f"   Status: ❌ Not available")
            print(f"   Error: {plan.get('error', 'Unknown error')}")
        print()

        # NAS Accessibility
        print("-" * 80)
        print("2. NAS ACCESSIBILITY")
        print("-" * 80)
        nas_access = status.get("nas_accessibility", {})
        if nas_access.get("accessible", False):
            print(f"   Status: ✅ NAS IS ACCESSIBLE")
            print(f"   Path: {nas_access.get('path', 'Unknown')}")
            print(f"   Note: NAS is not blocked - ready for migration!")
        else:
            print(f"   Status: ❌ NAS not accessible")
            if nas_access.get("error"):
                print(f"   Error: {nas_access.get('error')}")
        print()

        # Azure Vault Credentials
        print("-" * 80)
        print("3. AZURE VAULT CREDENTIALS (TRIAD)")
        print("-" * 80)
        vault_creds = status.get("azure_vault_credentials", {})
        if vault_creds.get("available", False):
            print(f"   Status: ✅ Credentials Available via TRIAD")
            print(f"   Source: {vault_creds.get('source', 'Azure Key Vault')}")
            print(f"   Username: {'✅' if vault_creds.get('has_username') else '❌'}")
            print(f"   Password: {'✅' if vault_creds.get('has_password') else '❌'}")
        else:
            print(f"   Status: ⚠️  Credentials check failed")
            if vault_creds.get("error"):
                print(f"   Error: {vault_creds.get('error')}")
        print()

        # DOIT Execution
        print("-" * 80)
        print("4. DOIT EXECUTION STATUS")
        print("-" * 80)
        doit = status.get("doit_execution", {})
        if doit.get("available", False):
            print(f"   Status: ✅ Available")
            if doit.get("executed", False):
                if doit.get("dry_run", False):
                    print(f"   Execution: ✅ EXECUTED (Dry Run)")
                else:
                    print(f"   Execution: ✅ EXECUTED")
            else:
                print(f"   Execution: ⏸️  Not executed")

            if doit.get("files_to_migrate"):
                print(f"   Files to Migrate: {doit.get('files_to_migrate'):,}")
            if doit.get("size_to_migrate"):
                print(f"   Size to Migrate: {doit.get('size_to_migrate')}")
            if doit.get("target_path"):
                print(f"   Target: {doit.get('target_path')}")
            if doit.get("blocking_issue"):
                print(f"   ⚠️  Note: {doit.get('blocking_issue')}")
        else:
            print(f"   Status: ❌ Not available")
            print(f"   Error: {doit.get('error', 'Unknown error')}")
        print()

        # Request IDs
        if status.get("request_ids", {}).get("available", False):
            print("-" * 80)
            print("5. REQUEST ID STATUS")
            print("-" * 80)
            req_ids = status.get("request_ids", {})
            for req_id, data in req_ids.get("request_ids", {}).items():
                print(f"\n   Request ID: {req_id}")
                if data.get("found", False):
                    print(f"   Status: ✅ Found")
                    files = data.get("files", [])
                    print(f"   Files Found: {len(files)}")
                    for file_info in files:
                        print(f"     - {file_info.get('name', 'Unknown')}")
                        print(f"       Modified: {file_info.get('modified', 'Unknown')}")
                else:
                    print(f"   Status: ❌ Not found in diagnostics")
            print()

        print("=" * 80)
        print()

        # Summary
        print("SUMMARY")
        print("-" * 80)
        plan_status = plan.get("network_drives_status", "UNKNOWN") if plan.get("available") else "N/A"
        doit_status = "EXECUTED (Dry Run)" if doit.get("dry_run") else "EXECUTED" if doit.get("executed") else "NOT EXECUTED"
        nas_accessible = "✅ ACCESSIBLE" if nas_access.get("accessible") else "❌ NOT ACCESSIBLE"
        vault_available = "✅ AVAILABLE" if vault_creds.get("available") else "❌ NOT AVAILABLE"

        print(f"Migration Plan: {plan_status}")
        print(f"NAS Accessibility: {nas_accessible}")
        print(f"Azure Vault Credentials: {vault_available} (via TRIAD)")
        print(f"DOIT Execution: {doit_status}")
        if nas_access.get("accessible") and vault_creds.get("available"):
            print(f"✅ READY TO MIGRATE: NAS accessible and credentials available!")
        elif not nas_access.get("accessible"):
            print(f"⚠️  NAS not accessible - check network connection")
        elif not vault_creds.get("available"):
            print(f"⚠️  Credentials not available - check Azure Vault/TRIAD")
        print()


def main():
    try:
        """Main function to check NAS migration status."""
        import sys

        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        # Get request IDs from command line or use defaults
        request_ids = []
        if len(sys.argv) > 1:
            request_ids = sys.argv[1:]
        else:
            # Default request IDs from user query
            request_ids = [
                "40f54051-33f7-474c-851d-ad85cbb29218",
                "1847f13b-6d51-4ffd-949f-9ba946974e94"
            ]

        print("🔍 Checking NAS Migration Status...")
        print()

        status_checker = NASMigrationStatus(project_root)
        status = status_checker.get_comprehensive_status(request_ids=request_ids)

        status_checker.print_status(status)

        # Save status
        output_path = project_root / "data" / "time_tracking" / f"nas_migration_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

        print(f"💾 Status saved to: {output_path}")
        print()

        return status


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()