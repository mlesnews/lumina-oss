#!/usr/bin/env python3
"""
Configure Iron Legion to Use M Drive for Models

Sets up Iron Legion cluster to use M drive (NAS) for all model storage,
mirroring the ULTRON configuration. Creates proper directory structure
with each cluster as a subdirectory.

Tags: #IRON_LEGION #M_DRIVE #MODEL_STORAGE #CLUSTER @LUMINA
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConfigureIronLegionMDrive")


class IronLegionMDriveConfigurator:
    """Configure Iron Legion to use M drive for models"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_file = self.config_dir / "iron_legion_cluster_config.json"

        # Load current config
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {}

    def setup_m_drive_structure(self) -> Dict[str, Any]:
        """Set up M drive directory structure for Iron Legion"""

        logger.info("=" * 80)
        logger.info("📁 SETTING UP M DRIVE STRUCTURE FOR IRON LEGION")
        logger.info("=" * 80)

        # M drive paths
        base_paths = [
            "M:\\Ollama\\models",
            "M:\\Ollama\\models\\iron_legion",
        ]

        # Mark-specific directories
        mark_dirs = [
            "mark_i",
            "mark_ii",
            "mark_iii",
            "mark_iv",
            "mark_v",
            "mark_vi",
            "mark_vii"
        ]

        results = {
            "created": [],
            "failed": [],
            "existing": []
        }

        # Check if M drive is accessible
        if not os.path.exists("M:\\"):
            logger.error("❌ M drive not accessible!")
            logger.error("   Please map M drive first:")
            logger.error("   net use M: \\\\DS2118PLUS\\AI-Models /persistent:yes")
            return results

        logger.info("✅ M drive is accessible")

        # Create base directories
        for base_path in base_paths:
            try:
                os.makedirs(base_path, exist_ok=True)
                if os.path.exists(base_path):
                    results["created"].append(base_path)
                    logger.info(f"✅ Created: {base_path}")
                else:
                    results["existing"].append(base_path)
                    logger.info(f"ℹ️  Already exists: {base_path}")
            except Exception as e:
                results["failed"].append(base_path)
                logger.error(f"❌ Failed to create {base_path}: {e}")

        # Create Mark-specific directories
        iron_legion_base = "M:\\Ollama\\models\\iron_legion"
        for mark_dir in mark_dirs:
            mark_path = os.path.join(iron_legion_base, mark_dir)
            try:
                os.makedirs(mark_path, exist_ok=True)
                if os.path.exists(mark_path):
                    results["created"].append(mark_path)
                    logger.info(f"  ✅ Created: {mark_path}")
            except Exception as e:
                results["failed"].append(mark_path)
                logger.error(f"  ❌ Failed to create {mark_path}: {e}")

        return results

    def update_iron_legion_config(self) -> bool:
        """Update Iron Legion config to use M drive"""

        logger.info("\n" + "=" * 80)
        logger.info("⚙️  UPDATING IRON LEGION CONFIGURATION")
        logger.info("=" * 80)

        # Update cluster info with M drive configuration
        if "cluster_info" not in self.config:
            self.config["cluster_info"] = {}

        self.config["cluster_info"]["model_storage"] = {
            "primary": "M:\\Ollama\\models\\iron_legion",
            "description": "All Iron Legion models stored on M drive (NAS)",
            "ollama_models_path": "M:\\Ollama\\models",
            "cluster_subdir": "iron_legion",
            "mirrors_ultron": True,
            "directory_structure": {
                "base": "M:\\Ollama\\models",
                "iron_legion": "M:\\Ollama\\models\\iron_legion",
                "mark_i": "M:\\Ollama\\models\\iron_legion\\mark_i",
                "mark_ii": "M:\\Ollama\\models\\iron_legion\\mark_ii",
                "mark_iii": "M:\\Ollama\\models\\iron_legion\\mark_iii",
                "mark_iv": "M:\\Ollama\\models\\iron_legion\\mark_iv",
                "mark_v": "M:\\Ollama\\models\\iron_legion\\mark_v",
                "mark_vi": "M:\\Ollama\\models\\iron_legion\\mark_vi",
                "mark_vii": "M:\\Ollama\\models\\iron_legion\\mark_vii"
            }
        }

        # Update each Mark to reference M drive
        if "standalone_access" in self.config and "models" in self.config["standalone_access"]:
            for mark_id, mark_info in self.config["standalone_access"]["models"].items():
                mark_info["model_storage"] = f"M:\\Ollama\\models\\iron_legion\\{mark_id}"
                mark_info["uses_m_drive"] = True

        # Save updated config
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)

            logger.info(f"✅ Configuration updated: {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")
            return False

    def configure_ollama_environment(self) -> bool:
        """Configure Ollama environment variable for Iron Legion"""

        logger.info("\n" + "=" * 80)
        logger.info("🔧 CONFIGURING OLLAMA ENVIRONMENT")
        logger.info("=" * 80)

        # Set OLLAMA_MODELS to M drive
        ollama_models_path = "M:\\Ollama\\models"

        try:
            # Set system environment variable
            import winreg

            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_ALL_ACCESS
            )

            winreg.SetValueEx(key, "OLLAMA_MODELS", 0, winreg.REG_EXPAND_SZ, ollama_models_path)
            winreg.CloseKey(key)

            logger.info(f"✅ Set OLLAMA_MODELS={ollama_models_path} (system)")

            # Also set for current session
            os.environ["OLLAMA_MODELS"] = ollama_models_path
            logger.info(f"✅ Set OLLAMA_MODELS for current session")

            return True
        except Exception as e:
            logger.warning(f"⚠️  Could not set system environment variable: {e}")
            logger.info("   Setting for current session only...")
            os.environ["OLLAMA_MODELS"] = ollama_models_path
            return True

    def run_complete_setup(self) -> Dict[str, Any]:
        """Run complete Iron Legion M drive setup"""

        logger.info("=" * 80)
        logger.info("🚀 IRON LEGION M DRIVE SETUP")
        logger.info("=" * 80)
        logger.info("Configuring Iron Legion to use M drive for models (mirroring ULTRON)")
        logger.info("")

        # Step 1: Set up directory structure
        dir_results = self.setup_m_drive_structure()

        # Step 2: Update configuration
        config_success = self.update_iron_legion_config()

        # Step 3: Configure environment
        env_success = self.configure_ollama_environment()

        # Summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 SETUP SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Directories created: {len(dir_results['created'])}")
        logger.info(f"⚠️  Directories failed: {len(dir_results['failed'])}")
        logger.info(f"✅ Configuration updated: {config_success}")
        logger.info(f"✅ Environment configured: {env_success}")

        if len(dir_results['failed']) == 0 and config_success and env_success:
            logger.info("\n🎉 Iron Legion M drive setup complete!")
            logger.info("   All models will be stored on M drive")
            logger.info("   Directory structure: M:\\Ollama\\models\\iron_legion\\")
        else:
            logger.warning("\n⚠️  Setup completed with some issues")
            if dir_results['failed']:
                logger.warning(f"   Failed directories: {dir_results['failed']}")

        return {
            "directory_setup": dir_results,
            "config_updated": config_success,
            "environment_configured": env_success,
            "m_drive_path": "M:\\Ollama\\models\\iron_legion"
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Configure Iron Legion to use M drive")
        parser.add_argument("--setup", action="store_true", help="Run complete setup")
        parser.add_argument("--create-dirs", action="store_true", help="Create directory structure only")
        parser.add_argument("--update-config", action="store_true", help="Update configuration only")

        args = parser.parse_args()

        configurator = IronLegionMDriveConfigurator()

        if args.setup or not any([args.create_dirs, args.update_config]):
            result = configurator.run_complete_setup()

            # Save results
            results_file = configurator.project_root / "data" / "iron_legion_m_drive_setup.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"\n📄 Results saved: {results_file}")

        elif args.create_dirs:
            result = configurator.setup_m_drive_structure()
            print(json.dumps(result, indent=2))

        elif args.update_config:
            success = configurator.update_iron_legion_config()
            print(f"Configuration updated: {success}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()