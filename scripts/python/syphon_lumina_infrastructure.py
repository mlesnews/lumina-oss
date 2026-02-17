#!/usr/bin/env python3
"""
SYPHON Lumina Infrastructure Extraction

Extracts actionable intelligence from Lumina infrastructure:
- System architecture
- Configuration files
- Integration points
- Infrastructure components
- Security configurations
- Network topology
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
except ImportError:
    # Fallback to simple system
    from syphon_system import SYPHONSystem

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonLuminaInfrastructure")


class LuminaInfrastructureExtractor:
    """Extract infrastructure intelligence from Lumina"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon" / "lumina_infrastructure"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logger = get_logger("LuminaInfrastructureExtractor")

        # Initialize SYPHON
        try:
            config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE,
                enable_self_healing=True,
                enable_banking=False
            )
            self.syphon = SYPHONSystem(config)
        except Exception as e:
            self.logger.warning(f"SYPHON initialization failed: {e}, using fallback")
            self.syphon = SYPHONSystem(self.project_root)

    def extract_infrastructure(self) -> Dict[str, Any]:
        try:
            """Extract complete Lumina infrastructure intelligence"""
            self.logger.info("=" * 70)
            self.logger.info("SYPHON: Extracting Lumina Infrastructure Intelligence")
            self.logger.info("=" * 70)

            infrastructure = {
                "timestamp": datetime.now().isoformat(),
                "extraction_id": f"lumina_infrastructure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "systems": {},
                "configurations": {},
                "integrations": {},
                "infrastructure_components": {},
                "security_configurations": {},
                "network_topology": {},
                "actionable_intelligence": []
            }

            # Extract system architecture
            infrastructure["systems"] = self._extract_systems()

            # Extract configurations
            infrastructure["configurations"] = self._extract_configurations()

            # Extract integrations
            infrastructure["integrations"] = self._extract_integrations()

            # Extract infrastructure components
            infrastructure["infrastructure_components"] = self._extract_infrastructure_components()

            # Extract security configurations
            infrastructure["security_configurations"] = self._extract_security_configurations()

            # Extract network topology
            infrastructure["network_topology"] = self._extract_network_topology()

            # Generate actionable intelligence
            infrastructure["actionable_intelligence"] = self._generate_actionable_intelligence(infrastructure)

            # Save extraction
            output_file = self.data_dir / f"infrastructure_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(infrastructure, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"Infrastructure extraction saved to: {output_file}")

            return infrastructure

        except Exception as e:
            self.logger.error(f"Error in extract_infrastructure: {e}", exc_info=True)
            raise
    def _extract_systems(self) -> Dict[str, Any]:
        """Extract system architecture"""
        systems = {}

        # R5 System
        r5_config = self.project_root / "config" / "r5" / "r5_config.json"
        if r5_config.exists():
            try:
                with open(r5_config, 'r') as f:
                    systems["r5"] = json.load(f)
            except Exception as e:
                self.logger.debug(f"Error reading R5 config: {e}")

        # Helpdesk System
        helpdesk_config = self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"
        if helpdesk_config.exists():
            try:
                with open(helpdesk_config, 'r') as f:
                    systems["helpdesk"] = json.load(f)
            except Exception as e:
                self.logger.debug(f"Error reading helpdesk config: {e}")

        # JARVIS Integration
        jarvis_config = self.project_root / "config" / "lumina_extensions_integration.json"
        if jarvis_config.exists():
            try:
                with open(jarvis_config, 'r') as f:
                    systems["jarvis"] = json.load(f)
            except Exception as e:
                self.logger.debug(f"Error reading JARVIS config: {e}")

        # SYPHON System
        systems["syphon"] = {
            "module": "scripts/python/syphon",
            "enabled": True,
            "version": "1.0.0"
        }

        return systems

    def _extract_configurations(self) -> Dict[str, Any]:
        """Extract configuration files"""
        configs = {}
        config_dir = self.project_root / "config"

        if config_dir.exists():
            for config_file in config_dir.rglob("*.json"):
                try:
                    with open(config_file, 'r') as f:
                        configs[str(config_file.relative_to(self.project_root))] = json.load(f)
                except Exception as e:
                    self.logger.debug(f"Error reading {config_file}: {e}")

        return configs

    def _extract_integrations(self) -> Dict[str, Any]:
        try:
            """Extract integration points"""
            integrations = {
                "n8n": {"enabled": False, "webhooks": []},
                "r5_api": {"endpoint": "http://localhost:8000/r5", "enabled": True},
                "helpdesk": {"coordinator": "C-3PO", "enabled": True},
                "jarvis": {"enabled": True},
                "syphon": {"enabled": True}
            }

            # Check for n8n integration
            n8n_integration = self.project_root / "scripts" / "python" / "n8n_syphon_integration.py"
            if n8n_integration.exists():
                integrations["n8n"]["enabled"] = True

            return integrations

        except Exception as e:
            self.logger.error(f"Error in _extract_integrations: {e}", exc_info=True)
            raise
    def _extract_infrastructure_components(self) -> Dict[str, Any]:
        try:
            """Extract infrastructure components"""
            components = {
                "monitoring": [],
                "orchestration": [],
                "data_management": [],
                "security": [],
                "automation": []
            }

            # Check for monitoring scripts
            scripts_dir = self.project_root / "scripts" / "python"
            if scripts_dir.exists():
                monitoring_patterns = ["monitor", "health", "status"]
                orchestration_patterns = ["orchestrator", "control", "manage"]
                data_patterns = ["data", "lifecycle", "backup"]
                security_patterns = ["security", "scan", "audit"]
                automation_patterns = ["automate", "workflow", "task"]

                for script_file in scripts_dir.glob("*.py"):
                    script_name = script_file.name.lower()

                    if any(p in script_name for p in monitoring_patterns):
                        components["monitoring"].append(str(script_file.relative_to(self.project_root)))
                    if any(p in script_name for p in orchestration_patterns):
                        components["orchestration"].append(str(script_file.relative_to(self.project_root)))
                    if any(p in script_name for p in data_patterns):
                        components["data_management"].append(str(script_file.relative_to(self.project_root)))
                    if any(p in script_name for p in security_patterns):
                        components["security"].append(str(script_file.relative_to(self.project_root)))
                    if any(p in script_name for p in automation_patterns):
                        components["automation"].append(str(script_file.relative_to(self.project_root)))

            return components

        except Exception as e:
            self.logger.error(f"Error in _extract_infrastructure_components: {e}", exc_info=True)
            raise
    def _extract_security_configurations(self) -> Dict[str, Any]:
        try:
            """Extract security configurations"""
            security = {
                "encryption": {"enabled": False, "method": None},
                "authentication": {"enabled": False, "method": None},
                "authorization": {"enabled": False, "method": None},
                "audit_logging": {"enabled": True, "location": "data/logs"}
            }

            # Check for security scripts
            security_scripts = self.project_root / "scripts" / "python"
            if security_scripts.exists():
                for script in security_scripts.glob("*security*.py"):
                    security["encryption"]["enabled"] = True
                    security["encryption"]["method"] = "custom"

            return security

        except Exception as e:
            self.logger.error(f"Error in _extract_security_configurations: {e}", exc_info=True)
            raise
    def _extract_network_topology(self) -> Dict[str, Any]:
        """Extract network topology"""
        topology = {
            "local_services": {
                "r5_api": {"port": 8000, "protocol": "http"},
                "helpdesk": {"type": "file_based", "location": "data/helpdesk"}
            },
            "external_services": {
                "n8n": {"enabled": False},
                "nas": {"host": "<NAS_PRIMARY_IP>", "enabled": True}
            },
            "network_isolation": {"enabled": False}
        }

        return topology

    def _generate_actionable_intelligence(self, infrastructure: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate actionable intelligence from infrastructure"""
        intelligence = []

        # Check for encryption needs
        if not infrastructure["security_configurations"]["encryption"]["enabled"]:
            intelligence.append({
                "priority": "high",
                "category": "security",
                "action": "Implement infrastructure encryption",
                "recommendation": "Apply ICP (Internet Computer Protocol) encryption to all infrastructure components",
                "impact": "Enhanced security and data protection"
            })

        # Check for integration opportunities
        if not infrastructure["integrations"]["n8n"]["enabled"]:
            intelligence.append({
                "priority": "medium",
                "category": "integration",
                "action": "Enable n8n integration",
                "recommendation": "Connect SYPHON to n8n for workflow automation",
                "impact": "Automated intelligence extraction workflows"
            })

        # Check for monitoring gaps
        if len(infrastructure["infrastructure_components"]["monitoring"]) == 0:
            intelligence.append({
                "priority": "medium",
                "category": "monitoring",
                "action": "Implement comprehensive monitoring",
                "recommendation": "Add monitoring for all infrastructure components",
                "impact": "Better observability and issue detection"
            })

        return intelligence


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON Lumina Infrastructure Extraction")
        parser.add_argument(
            "--project-root",
            type=str,
            default=str(project_root),
            help="Project root directory"
        )
        parser.add_argument(
            "--output",
            type=str,
            help="Output file path (optional)"
        )

        args = parser.parse_args()

        extractor = LuminaInfrastructureExtractor(Path(args.project_root))
        infrastructure = extractor.extract_infrastructure()

        logger.info("")
        logger.info("=" * 70)
        logger.info("EXTRACTION COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Systems extracted: {len(infrastructure['systems'])}")
        logger.info(f"Configurations extracted: {len(infrastructure['configurations'])}")
        logger.info(f"Infrastructure components: {sum(len(v) for v in infrastructure['infrastructure_components'].values())}")
        logger.info(f"Actionable intelligence items: {len(infrastructure['actionable_intelligence'])}")
        logger.info("=" * 70)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())