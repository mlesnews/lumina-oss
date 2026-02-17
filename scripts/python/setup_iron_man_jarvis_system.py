#!/usr/bin/env python3
"""
Setup Iron Man Virtual Assistants & Jarvis System

Complete setup script for:
- Iron Man Virtual Assistants (JARVIS, Ultron, Ultimate Iron Man)
- Iron Legion AI Models (7 models on KAIJU)
- Windows Copilot plugins
- Magic words activation
- Expert routing configuration

Tags: #IRON_MAN #JARVIS #SETUP #IRON_LEGION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("IronManJarvisSetup")


class IronManJarvisSetup:
    """Complete setup for Iron Man Virtual Assistants & Jarvis"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data"
        self.plugins_dir = self.config_dir / "windows_copilot_plugins"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def verify_configs(self) -> Dict[str, bool]:
        try:
            """Verify all configuration files exist"""
            results = {}

            configs = {
                "iron_legion_cluster": self.config_dir / "iron_legion_cluster_config.json",
                "iron_legion_experts": self.config_dir / "iron_legion_experts_config.json",
                "kaiju_iron_legion": self.config_dir / "kaiju_iron_legion_config.json",
                "jarvis_manifest": self.plugins_dir / "jarvis_manifest.json",
                "ultron_manifest": self.plugins_dir / "ultron_manifest.json",
                "ultimate_iron_man_manifest": self.plugins_dir / "ultimate_iron_man_manifest.json",
            }

            for name, path in configs.items():
                results[name] = path.exists()
                if not results[name]:
                    logger.warning(f"⚠️  Missing config: {name} ({path})")
                else:
                    logger.info(f"✅ Found config: {name}")

            return results

        except Exception as e:
            self.logger.error(f"Error in verify_configs: {e}", exc_info=True)
            raise
    def verify_scripts(self) -> Dict[str, bool]:
        try:
            """Verify all assistant scripts exist"""
            results = {}

            scripts = {
                "iron_man_manager": script_dir / "iron_man_assistant_manager.py",
                "jarvis_desktop": script_dir / "jarvis_desktop_assistant.py",
                "ultron_desktop": script_dir / "ultron_desktop_assistant.py",
                "ultimate_iron_man": script_dir / "ultimate_iron_man_desktop_assistant_hq.py",
            }

            for name, path in scripts.items():
                results[name] = path.exists()
                if not results[name]:
                    logger.warning(f"⚠️  Missing script: {name} ({path})")
                else:
                    logger.info(f"✅ Found script: {name}")

            return results

        except Exception as e:
            self.logger.error(f"Error in verify_scripts: {e}", exc_info=True)
            raise
    def setup_magic_words(self) -> bool:
        """Set up magic words activation file"""
        activation_file = self.data_dir / "iron_man_activation_phrase.txt"

        try:
            # Create activation file with magic words
            activation_file.write_text("Jarvis Iron Legion", encoding='utf-8')
            logger.info(f"✅ Magic words activation file created: {activation_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create activation file: {e}")
            return False

    def verify_kaiju_cluster(self) -> Dict[str, Any]:
        """Verify KAIJU Iron Legion cluster is accessible"""
        import requests

        results = {
            "kaiju_reachable": False,
            "ollama_running": False,
            "expert_router": False,
            "models_available": []
        }

        # Check KAIJU reachability
        try:
            response = requests.get("http://<NAS_IP>:11437/api/tags", timeout=5)
            if response.status_code == 200:
                results["kaiju_reachable"] = True
                results["ollama_running"] = True

                # Check available models
                models_data = response.json()
                if "models" in models_data:
                    results["models_available"] = [m.get("name", "") for m in models_data["models"]]
                    logger.info(f"✅ Found {len(results['models_available'])} models on KAIJU")
        except Exception as e:
            logger.warning(f"⚠️  KAIJU not reachable: {e}")

        # Check expert router
        try:
            response = requests.get("http://<NAS_IP>:3000/health", timeout=5)
            if response.status_code == 200:
                results["expert_router"] = True
                logger.info("✅ Expert router is running")
        except Exception as e:
            logger.warning(f"⚠️  Expert router not reachable: {e}")

        return results

    def generate_setup_report(self) -> Dict[str, Any]:
        try:
            """Generate complete setup report"""
            report = {
                "timestamp": str(Path(__file__).stat().st_mtime),
                "configs": self.verify_configs(),
                "scripts": self.verify_scripts(),
                "magic_words_setup": self.setup_magic_words(),
                "kaiju_cluster": self.verify_kaiju_cluster(),
            }

            return report

        except Exception as e:
            self.logger.error(f"Error in generate_setup_report: {e}", exc_info=True)
            raise
    def print_setup_summary(self, report: Dict[str, Any]):
        """Print setup summary"""
        print("=" * 80)
        print("🦾 IRON MAN & JARVIS SETUP SUMMARY")
        print("=" * 80)
        print()

        # Configs
        print("📋 Configuration Files:")
        configs_ok = all(report["configs"].values())
        for name, exists in report["configs"].items():
            icon = "✅" if exists else "❌"
            print(f"   {icon} {name}")
        print()

        # Scripts
        print("📜 Assistant Scripts:")
        scripts_ok = all(report["scripts"].values())
        for name, exists in report["scripts"].items():
            icon = "✅" if exists else "❌"
            print(f"   {icon} {name}")
        print()

        # Magic Words
        print("⚔️  Magic Words Activation:")
        icon = "✅" if report["magic_words_setup"] else "❌"
        print(f"   {icon} Activation file created")
        print()

        # KAIJU Cluster
        print("🤖 KAIJU Iron Legion Cluster:")
        kaiju = report["kaiju_cluster"]
        print(f"   {'✅' if kaiju['kaiju_reachable'] else '❌'} KAIJU reachable")
        print(f"   {'✅' if kaiju['ollama_running'] else '❌'} Ollama running")
        print(f"   {'✅' if kaiju['expert_router'] else '❌'} Expert router")
        if kaiju["models_available"]:
            print(f"   ✅ Found {len(kaiju['models_available'])} models:")
            for model in kaiju["models_available"][:5]:  # Show first 5
                print(f"      - {model}")
        print()

        # Overall status
        overall_ok = configs_ok and scripts_ok and report["magic_words_setup"]
        print("=" * 80)
        if overall_ok:
            print("✅ SETUP COMPLETE - Ready to launch assistants!")
        else:
            print("⚠️  SETUP INCOMPLETE - Some components missing")
        print("=" * 80)
        print()

        print("🚀 Next Steps:")
        print("   1. Verify KAIJU cluster is running (if needed)")
        print("   2. Say 'Jarvis Iron Legion' to activate")
        print("   3. Launch assistants:")
        print("      python scripts/python/jarvis_desktop_assistant.py")
        print("      python scripts/python/ultron_desktop_assistant.py")
        print("      python scripts/python/ultimate_iron_man_desktop_assistant_hq.py")
        print()


def main():
    try:
        """Main setup function"""
        setup = IronManJarvisSetup()
        report = setup.generate_setup_report()
        setup.print_setup_summary(report)

        # Save report
        report_file = setup.data_dir / "iron_man_jarvis_setup_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        logger.info(f"📊 Setup report saved: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()