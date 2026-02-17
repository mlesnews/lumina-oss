#!/usr/bin/env python3
"""
Deploy Azure Infrastructure - @bau Execution

Creates Azure Key Vault, Service Bus, and Managed Identity infrastructure.
Executed with @DOIT authority - immediate execution.

Tags: #BAU #AZURE #KEY_VAULT #SERVICE_BUS #@DOIT @JARVIS @LUMINA
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DeployAzureInfrastructureBau")


class AzureInfrastructureDeployer:
    """
    Deploy Azure Infrastructure - Key Vault, Service Bus, Managed Identity

    Executed with @DOIT authority - full power of @manus/@magneto
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.resource_group = "jarvis-lumina-rg"
        self.location = "eastus"
        self.key_vault_name = "jarvis-lumina-kv"
        self.service_bus_namespace = "jarvis-lumina-bus"  # Changed from -sb (reserved suffix)
        self.managed_identity_name = "jarvis-lumina-identity"

        # Find Azure CLI
        self.az_cmd = self._find_azure_cli()

        logger.info("✅ Azure Infrastructure Deployer initialized")
        logger.info(f"   Resource Group: {self.resource_group}")
        logger.info(f"   Location: {self.location}")

    def _find_azure_cli(self) -> Optional[str]:
        """Find Azure CLI executable"""
        az_paths = [
            "az",
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
        ]

        for path in az_paths:
            try:
                result = subprocess.run(
                    [path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    shell=True
                )
                if result.returncode == 0:
                    logger.info(f"   ✅ Azure CLI found: {path}")
                    return path
            except:
                continue

        logger.warning("   ⚠️  Azure CLI not found")
        return None

    def ensure_logged_in(self) -> bool:
        """Ensure Azure CLI is logged in"""
        if not self.az_cmd:
            return False

        try:
            result = subprocess.run(
                [self.az_cmd, "account", "show"],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                account_info = json.loads(result.stdout)
                logger.info(f"   ✅ Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
                return True
            else:
                logger.warning("   ⚠️  Not logged in - attempting login...")
                subprocess.run([self.az_cmd, "login"], timeout=300, shell=True)
                return True
        except Exception as e:
            logger.error(f"   ❌ Login check failed: {e}")
            return False

    def create_resource_group(self) -> bool:
        """Create resource group if it doesn't exist"""
        if not self.az_cmd:
            return False

        try:
            result = subprocess.run(
                [self.az_cmd, "group", "show", "--name", self.resource_group],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"   ✅ Resource group exists: {self.resource_group}")
                return True
            else:
                logger.info(f"   📦 Creating resource group: {self.resource_group}...")
                subprocess.run(
                    [self.az_cmd, "group", "create", "--name", self.resource_group, "--location", self.location],
                    check=True,
                    timeout=30,
                    shell=True
                )
                logger.info(f"   ✅ Resource group created")
                return True
        except Exception as e:
            logger.error(f"   ❌ Resource group creation failed: {e}")
            return False

    def create_key_vault(self) -> bool:
        """Create Azure Key Vault"""
        if not self.az_cmd:
            return False

        try:
            # Check if Key Vault exists
            result = subprocess.run(
                [self.az_cmd, "keyvault", "show", "--name", self.key_vault_name],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"   ✅ Key Vault exists: {self.key_vault_name}")
                return True

            # Create Key Vault
            logger.info(f"   🔐 Creating Key Vault: {self.key_vault_name}...")
            subprocess.run(
                [
                    self.az_cmd, "keyvault", "create",
                    "--name", self.key_vault_name,
                    "--resource-group", self.resource_group,
                    "--location", self.location,
                    "--enabled-for-deployment", "true",
                    "--enabled-for-template-deployment", "true",
                    "--enabled-for-disk-encryption", "true"
                ],
                check=True,
                timeout=60,
                shell=True
            )
            logger.info(f"   ✅ Key Vault created")
            return True
        except Exception as e:
            logger.error(f"   ❌ Key Vault creation failed: {e}")
            return False

    def create_service_bus(self) -> bool:
        """Create Azure Service Bus namespace"""
        if not self.az_cmd:
            return False

        try:
            # Check if Service Bus exists
            result = subprocess.run(
                [self.az_cmd, "servicebus", "namespace", "show", "--name", self.service_bus_namespace, "--resource-group", self.resource_group],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"   ✅ Service Bus namespace exists: {self.service_bus_namespace}")
                return True

            # Create Service Bus namespace
            logger.info(f"   🚌 Creating Service Bus namespace: {self.service_bus_namespace}...")
            subprocess.run(
                [
                    self.az_cmd, "servicebus", "namespace", "create",
                    "--name", self.service_bus_namespace,
                    "--resource-group", self.resource_group,
                    "--location", self.location,
                    "--sku", "Standard"
                ],
                check=True,
                timeout=60,
                shell=True
            )
            logger.info(f"   ✅ Service Bus namespace created")
            return True
        except Exception as e:
            logger.error(f"   ❌ Service Bus creation failed: {e}")
            return False

    def create_managed_identity(self) -> bool:
        """Create Managed Identity"""
        if not self.az_cmd:
            return False

        try:
            # Check if Managed Identity exists
            result = subprocess.run(
                [self.az_cmd, "identity", "show", "--name", self.managed_identity_name, "--resource-group", self.resource_group],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode == 0:
                logger.info(f"   ✅ Managed Identity exists: {self.managed_identity_name}")
                return True

            # Create Managed Identity
            logger.info(f"   🔑 Creating Managed Identity: {self.managed_identity_name}...")
            subprocess.run(
                [
                    self.az_cmd, "identity", "create",
                    "--name", self.managed_identity_name,
                    "--resource-group", self.resource_group,
                    "--location", self.location
                ],
                check=True,
                timeout=30,
                shell=True
            )
            logger.info(f"   ✅ Managed Identity created")
            return True
        except Exception as e:
            logger.error(f"   ❌ Managed Identity creation failed: {e}")
            return False

    def configure_managed_identity_access(self) -> bool:
        """Configure Managed Identity access to Key Vault and Service Bus"""
        if not self.az_cmd:
            return False

        try:
            # Get Managed Identity principal ID
            result = subprocess.run(
                [self.az_cmd, "identity", "show", "--name", self.managed_identity_name, "--resource-group", self.resource_group],
                capture_output=True,
                text=True,
                timeout=10,
                shell=True
            )
            if result.returncode != 0:
                logger.error("   ❌ Managed Identity not found")
                return False

            identity_info = json.loads(result.stdout)
            principal_id = identity_info.get("principalId")

            if not principal_id:
                logger.error("   ❌ Could not get principal ID")
                return False

            # Grant Key Vault access using RBAC (Key Vault uses RBAC authorization)
            logger.info(f"   🔐 Granting Key Vault access to Managed Identity (RBAC)...")
            try:
                # Get subscription ID from identity info
                subscription_id = identity_info.get("subscriptionId", "")
                if subscription_id:
                    subprocess.run(
                        [
                            self.az_cmd, "role", "assignment", "create",
                            "--assignee", principal_id,
                            "--role", "Key Vault Secrets Officer",
                            "--scope", f"/subscriptions/{subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.KeyVault/vaults/{self.key_vault_name}"
                        ],
                        check=True,
                        timeout=30,
                        shell=True
                    )
                    logger.info(f"   ✅ Key Vault RBAC access granted")
                else:
                    logger.warning(f"   ⚠️  Could not get subscription ID for RBAC")
            except Exception as e:
                logger.warning(f"   ⚠️  Key Vault RBAC access grant failed: {e}")

            # Grant Service Bus access
            logger.info(f"   🚌 Granting Service Bus access to Managed Identity...")
            try:
                subscription_id = identity_info.get("subscriptionId", "")
                if subscription_id:
                    # First check if Service Bus namespace exists
                    sb_check = subprocess.run(
                        [self.az_cmd, "servicebus", "namespace", "show", "--name", self.service_bus_namespace, "--resource-group", self.resource_group],
                        capture_output=True,
                        text=True,
                        timeout=10,
                        shell=True
                    )
                    if sb_check.returncode == 0:
                        subprocess.run(
                            [
                                self.az_cmd, "role", "assignment", "create",
                                "--assignee", principal_id,
                                "--role", "Azure Service Bus Data Owner",
                                "--scope", f"/subscriptions/{subscription_id}/resourceGroups/{self.resource_group}/providers/Microsoft.ServiceBus/namespaces/{self.service_bus_namespace}"
                            ],
                            check=True,
                            timeout=30,
                            shell=True
                        )
                        logger.info(f"   ✅ Service Bus access granted")
                    else:
                        logger.warning(f"   ⚠️  Service Bus namespace not found - skipping access grant")
                else:
                    logger.warning(f"   ⚠️  Could not get subscription ID for Service Bus access")
            except Exception as e:
                logger.warning(f"   ⚠️  Service Bus access grant failed: {e}")

            return True
        except Exception as e:
            logger.error(f"   ❌ Managed Identity access configuration failed: {e}")
            return False

    def deploy_all(self) -> Dict[str, Any]:
        """Deploy all Azure infrastructure"""
        logger.info("=" * 80)
        logger.info("🚀 @DOIT: DEPLOYING AZURE INFRASTRUCTURE")
        logger.info("=" * 80)
        logger.info("Full power of @manus/@magneto - Ultimate authority")
        logger.info("=" * 80)

        results = {
            "timestamp": datetime.now().isoformat(),
            "resource_group": self.resource_group,
            "location": self.location,
            "steps": {},
            "status": "deploying"
        }

        # Step 1: Ensure logged in
        logger.info("\n1️⃣  Ensuring Azure login...")
        if not self.ensure_logged_in():
            results["status"] = "failed"
            results["error"] = "Azure login failed"
            return results
        results["steps"]["login"] = "success"

        # Step 2: Create resource group
        logger.info("\n2️⃣  Creating resource group...")
        if not self.create_resource_group():
            results["status"] = "failed"
            results["error"] = "Resource group creation failed"
            return results
        results["steps"]["resource_group"] = "success"

        # Step 3: Create Key Vault
        logger.info("\n3️⃣  Creating Azure Key Vault...")
        if not self.create_key_vault():
            results["status"] = "partial"
            results["error"] = "Key Vault creation failed"
        else:
            results["steps"]["key_vault"] = "success"

        # Step 4: Create Service Bus
        logger.info("\n4️⃣  Creating Azure Service Bus...")
        if not self.create_service_bus():
            results["status"] = "partial"
            if "error" not in results:
                results["error"] = "Service Bus creation failed"
        else:
            results["steps"]["service_bus"] = "success"

        # Step 5: Create Managed Identity
        logger.info("\n5️⃣  Creating Managed Identity...")
        if not self.create_managed_identity():
            results["status"] = "partial"
            if "error" not in results:
                results["error"] = "Managed Identity creation failed"
        else:
            results["steps"]["managed_identity"] = "success"

        # Step 6: Configure access
        logger.info("\n6️⃣  Configuring Managed Identity access...")
        if not self.configure_managed_identity_access():
            results["status"] = "partial"
            if "error" not in results:
                results["error"] = "Access configuration failed"
        else:
            results["steps"]["access_config"] = "success"

        if results["status"] == "deploying":
            results["status"] = "completed"

        logger.info("\n" + "=" * 80)
        logger.info("✅ AZURE INFRASTRUCTURE DEPLOYMENT COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Status: {results['status']}")
        logger.info(f"Steps completed: {len([k for k, v in results['steps'].items() if v == 'success'])}")
        logger.info("=" * 80)

        return results


def main():
    try:
        """Main entry point"""
        import argparse
        from datetime import datetime

        parser = argparse.ArgumentParser(
            description="Deploy Azure Infrastructure - @DOIT authority"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output results as JSON"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        deployer = AzureInfrastructureDeployer(project_root)
        results = deployer.deploy_all()

        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            print(f"\n🚀 @DOIT: AZURE INFRASTRUCTURE DEPLOYMENT")
            print("=" * 80)
            print(f"Status: {results['status']}")
            print(f"Resource Group: {results['resource_group']}")
            print(f"Location: {results['location']}")
            print(f"\nSteps:")
            for step, status in results['steps'].items():
                print(f"  {step}: {status}")
            if 'error' in results:
                print(f"\n⚠️  Error: {results['error']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()