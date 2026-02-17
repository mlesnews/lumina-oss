#!/usr/bin/env python3
"""
Deploy NAS API Integration with All AI Agents Across All Environments

Deploys the NAS API integration, homelab AI ecosystem configuration, and cache settings
to all environments: dev, staging, production, and portable variants.

Environments:
- .lumina (base/development)
- <COMPANY>-financial-services_llc-env (production)
- <COMPANY>-financial-services_llc-env_portable (portable)
- <COMPANY_ID>-env (alternative)
"""

import sys
import shutil
import json
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
base_env_root = project_root  # .lumina

# Environment definitions
ENVIRONMENTS = {
    "dev": {
        "path": project_root,
        "name": ".lumina (Development)",
        "config_path": project_root / "config"
    },
    "prod": {
        "path": project_root.parent / "<COMPANY>-financial-services_llc-env",
        "name": "<COMPANY>-financial-services_llc-env (Production)",
        "config_path": project_root.parent / "<COMPANY>-financial-services_llc-env" / "config"
    },
    "portable": {
        "path": project_root.parent / "<COMPANY>-financial-services_llc-env_portable",
        "name": "<COMPANY>-financial-services_llc-env_portable (Portable)",
        "config_path": project_root.parent / "<COMPANY>-financial-services_llc-env_portable" / "config"
    },
    "alt": {
        "path": project_root.parent / "<COMPANY_ID>-env",
        "name": "<COMPANY_ID>-env (Alternative)",
        "config_path": project_root.parent / "<COMPANY_ID>-env" / "config"
    }
}

# Files to deploy
FILES_TO_DEPLOY = {
    "config/homelab_ai_ecosystem.json": {
        "description": "Homelab AI Ecosystem Registry",
        "required": True
    },
    "config/nas_proxy_cache_config.yaml": {
        "description": "NAS Proxy-Cache Configuration",
        "required": True
    },
    "config/lumina_nas_ssh_config.json": {
        "description": "NAS SSH Configuration (with Azure Key Vault)",
        "required": False,  # May exist with environment-specific values
        "merge": True  # Merge if exists
    }
}

# Scripts to deploy (to scripts/python/)
SCRIPTS_TO_DEPLOY = {
    "scripts/python/nas_physics_cache.py": {
        "description": "NAS Physics Cache with Azure Key Vault",
        "required": True
    },
    "scripts/python/convert_jarvis_tasks_to_nas_cron.py": {
        "description": "JARVIS Cron Converter with Proxy-Cache",
        "required": True
    },
    "scripts/python/nas_azure_vault_integration.py": {
        "description": "NAS Azure Vault Integration",
        "required": False  # May already exist
    }
}

# Documentation to deploy
DOCS_TO_DEPLOY = {
    "docs/system/NAS_API_FULL_INTEGRATION.md": {
        "description": "NAS API Full Integration Documentation",
        "required": False
    },
    "docs/system/PROXY_CACHE_INTEGRATION.md": {
        "description": "Proxy Cache Integration Documentation",
        "required": False
    }
}



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class EnvironmentDeployer:
    """Deploy NAS API integration to all environments"""

    def __init__(self):
        self.results = {
            "deployed": [],
            "skipped": [],
            "failed": [],
            "created_dirs": []
        }

    def check_environment(self, env_key: str, env_config: Dict[str, Any]) -> bool:
        try:
            """Check if environment exists and is accessible"""
            env_path = env_config["path"]
            config_path = env_config["config_path"]

            if not env_path.exists():
                print(f"⚠️  Environment not found: {env_path}")
                return False

            if not config_path.exists():
                print(f"⚠️  Config directory not found: {config_path}")
                print(f"   Creating config directory...")
                config_path.mkdir(parents=True, exist_ok=True)
                self.results["created_dirs"].append(str(config_path))

            return True

        except Exception as e:
            self.logger.error(f"Error in check_environment: {e}", exc_info=True)
            raise
    def deploy_file(self, env_key: str, env_config: Dict[str, Any], 
                   relative_path: str, file_config: Dict[str, Any]) -> bool:
        """Deploy a file to an environment"""
        source_file = base_env_root / relative_path
        target_file = env_config["path"] / relative_path

        if not source_file.exists():
            if file_config.get("required", False):
                print(f"❌ Required source file not found: {source_file}")
                return False
            else:
                print(f"⚠️  Optional source file not found: {source_file}")
                return True  # Skip optional files

        # Skip if source and target are the same file (dev environment)
        try:
            if source_file.resolve() == target_file.resolve():
                print(f"  ⏭️  Skipped (already in place): {relative_path}")
                return True
        except Exception:
            pass  # Continue if resolve fails

        try:
            # Create target directory if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)

            # Handle merge for JSON files
            if file_config.get("merge", False) and target_file.exists():
                if relative_path.endswith(".json"):
                    self._merge_json(source_file, target_file)
                elif relative_path.endswith((".yaml", ".yml")):
                    self._merge_yaml(source_file, target_file)
                else:
                    # For other files, copy if source is newer
                    if source_file.stat().st_mtime > target_file.stat().st_mtime:
                        shutil.copy2(source_file, target_file)
            else:
                # Direct copy
                shutil.copy2(source_file, target_file)

            print(f"  ✅ Deployed: {relative_path}")
            return True

        except Exception as e:
            print(f"  ❌ Failed to deploy {relative_path}: {e}")
            return False

    def _merge_json(self, source: Path, target: Path):
        """Merge JSON files, preserving target-specific values"""
        try:
            with open(source, 'r', encoding='utf-8') as f:
                source_data = json.load(f)
            with open(target, 'r', encoding='utf-8') as f:
                target_data = json.load(f)

            # Merge: source provides defaults, target overrides
            merged = {**source_data, **target_data}

            # Deep merge for nested dicts
            for key, value in source_data.items():
                if isinstance(value, dict) and key in target_data and isinstance(target_data[key], dict):
                    merged[key] = {**value, **target_data[key]}

            with open(target, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)

        except Exception as e:
            print(f"    ⚠️  Merge failed, copying instead: {e}")
            shutil.copy2(source, target)

    def _merge_yaml(self, source: Path, target: Path):
        """Merge YAML files, preserving target-specific values"""
        try:
            import yaml
            with open(source, 'r', encoding='utf-8') as f:
                source_data = yaml.safe_load(f) or {}
            with open(target, 'r', encoding='utf-8') as f:
                target_data = yaml.safe_load(f) or {}

            # Merge: source provides defaults, target overrides
            merged = {**source_data, **target_data}

            # Deep merge for nested dicts
            for key, value in source_data.items():
                if isinstance(value, dict) and key in target_data and isinstance(target_data[key], dict):
                    merged[key] = {**value, **target_data[key]}

            with open(target, 'w', encoding='utf-8') as f:
                yaml.dump(merged, f, default_flow_style=False, sort_keys=False)

        except Exception as e:
            print(f"    ⚠️  Merge failed, copying instead: {e}")
            shutil.copy2(source, target)

    def deploy_to_environment(self, env_key: str, env_config: Dict[str, Any]):
        """Deploy all files to an environment"""
        print(f"\n{'='*60}")
        print(f"📦 Deploying to: {env_config['name']}")
        print(f"   Path: {env_config['path']}")
        print(f"{'='*60}")

        if not self.check_environment(env_key, env_config):
            self.results["skipped"].append(env_key)
            return

        deployed_count = 0
        failed_count = 0

        # Deploy config files
        print("\n📁 Deploying configuration files...")
        for relative_path, file_config in FILES_TO_DEPLOY.items():
            if self.deploy_file(env_key, env_config, relative_path, file_config):
                deployed_count += 1
            else:
                failed_count += 1

        # Deploy scripts
        print("\n📜 Deploying scripts...")
        for relative_path, file_config in SCRIPTS_TO_DEPLOY.items():
            if self.deploy_file(env_key, env_config, relative_path, file_config):
                deployed_count += 1
            else:
                failed_count += 1

        # Deploy documentation
        print("\n📚 Deploying documentation...")
        for relative_path, file_config in DOCS_TO_DEPLOY.items():
            if self.deploy_file(env_key, env_config, relative_path, file_config):
                deployed_count += 1

        if failed_count == 0:
            self.results["deployed"].append(env_key)
            print(f"\n✅ Successfully deployed to {env_config['name']}")
        else:
            self.results["failed"].append((env_key, failed_count))
            print(f"\n⚠️  Deployed to {env_config['name']} with {failed_count} failures")

    def deploy_all(self):
        """Deploy to all environments"""
        print("🚀 NAS API Integration - Multi-Environment Deployment")
        print("=" * 60)
        print(f"Base Environment: {base_env_root}")
        print(f"Environments to deploy: {len(ENVIRONMENTS)}")
        print()

        for env_key, env_config in ENVIRONMENTS.items():
            self.deploy_to_environment(env_key, env_config)

        self.print_summary()

    def print_summary(self):
        """Print deployment summary"""
        print(f"\n{'='*60}")
        print("📊 Deployment Summary")
        print(f"{'='*60}")
        print(f"✅ Successfully deployed: {len(self.results['deployed'])}")
        for env in self.results['deployed']:
            print(f"   - {ENVIRONMENTS[env]['name']}")

        if self.results['skipped']:
            print(f"\n⚠️  Skipped: {len(self.results['skipped'])}")
            for env in self.results['skipped']:
                print(f"   - {ENVIRONMENTS[env]['name']}")

        if self.results['failed']:
            print(f"\n❌ Failed: {len(self.results['failed'])}")
            for env, count in self.results['failed']:
                print(f"   - {ENVIRONMENTS[env]['name']} ({count} failures)")

        if self.results['created_dirs']:
            print(f"\n📁 Created directories: {len(self.results['created_dirs'])}")
            for dir_path in self.results['created_dirs']:
                print(f"   - {dir_path}")

        print()


def main():
    """Main entry point"""
    deployer = EnvironmentDeployer()
    deployer.deploy_all()
    return 0 if not deployer.results['failed'] else 1


if __name__ == "__main__":



    sys.exit(main())