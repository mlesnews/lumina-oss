#!/usr/bin/env python3
"""
Migrate Lightweight Containers to NAS DSM Container Manager

Identifies and migrates MCP and lightweight Docker containers from:
- kaiju_no_8 (<NAS_IP>) 
- Millennium Falc (<NAS_IP>)
To:
- NAS DS2118+ (<NAS_PRIMARY_IP>) via DSM Container Manager

Tags: #MIGRATION #NAS #DSM #CONTAINERS #MCP @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

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

logger = get_logger("ContainerMigration")

# IP Addresses
KAIJU_NO_8 = "<NAS_IP>"  # Desktop with Iron Legion k8 cluster
MILLENNIUM_FALC = "<NAS_IP>"  # Laptop with ULTRON cluster
NAS_DS2118PLUS = "<NAS_PRIMARY_IP>"  # NAS with DSM Container Manager

# Containers to migrate
CONTAINERS_TO_MIGRATE = {
    "mcp_servers": {
        "source": "containerization/services/mcp-servers/docker-compose.yml",
        "target": "containerization/services/nas-mcp-servers/docker-compose.yml",
        "containers": [
            "manus-mcp-server",  # MANUS MCP Server
            "elevenlabs-mcp-server",  # ElevenLabs MCP Server
        ],
        "description": "MCP servers currently on local machines, should be on NAS for shared access"
    },
    "lightweight_services": {
        "source": "containerization/services",
        "target": "containerization/services/nas-mcp-servers/docker-compose.yml",
        "containers": [
            # These should already be in nas-mcp-servers, but verify
            "n8n",  # Workflow automation
            "postgres-mcp-server",  # Database operations
            "sqlite-mcp-server",  # SQLite operations
            "filesystem-mcp-server",  # File operations
            "git-mcp-server",  # Git operations
            "github-mcp-server",  # GitHub operations
        ],
        "description": "Lightweight services that should be centralized on NAS"
    }
}


class ContainerMigrationPlanner:
    """Plan and execute container migration to NAS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.migration_plan = {
            "timestamp": datetime.now().isoformat(),
            "source_hosts": {
                "kaiju_no_8": KAIJU_NO_8,
                "millennium_falc": MILLENNIUM_FALC
            },
            "target_host": {
                "nas": NAS_DS2118PLUS,
                "container_manager": "DSM Container Manager"
            },
            "migrations": []
        }

    def identify_containers(self) -> Dict[str, Any]:
        try:
            """Identify containers that need migration"""
            logger.info("🔍 Identifying containers to migrate...")

            identified = {
                "mcp_containers": [],
                "lightweight_containers": [],
                "already_on_nas": []
            }

            # Check mcp-servers docker-compose.yml
            mcp_compose = self.project_root / "containerization" / "services" / "mcp-servers" / "docker-compose.yml"
            if mcp_compose.exists():
                logger.info(f"   Found: {mcp_compose}")
                identified["mcp_containers"].append({
                    "file": str(mcp_compose.relative_to(self.project_root)),
                    "containers": ["manus-mcp-server", "elevenlabs-mcp-server"],
                    "status": "needs_migration"
                })

            # Check nas-mcp-servers (already configured for NAS)
            nas_mcp_compose = self.project_root / "containerization" / "services" / "nas-mcp-servers" / "docker-compose.yml"
            if nas_mcp_compose.exists():
                logger.info(f"   Found: {nas_mcp_compose}")
                identified["already_on_nas"].append({
                    "file": str(nas_mcp_compose.relative_to(self.project_root)),
                    "status": "configured_for_nas",
                    "note": "Contains 20+ MCP servers already configured for NAS"
                })

            # Check manus-mcp-server standalone
            manus_compose = self.project_root / "containerization" / "services" / "manus-mcp-server" / "docker-compose.yml"
            if manus_compose.exists():
                logger.info(f"   Found: {manus_compose}")
                identified["mcp_containers"].append({
                    "file": str(manus_compose.relative_to(self.project_root)),
                    "containers": ["manus-mcp-server", "manus-god-cycle", "manus-monitor"],
                    "status": "needs_migration"
                })

            return identified

        except Exception as e:
            self.logger.error(f"Error in identify_containers: {e}", exc_info=True)
            raise
    def create_migration_plan(self, identified: Dict[str, Any]) -> Dict[str, Any]:
        """Create detailed migration plan"""
        logger.info("📋 Creating migration plan...")

        plan = {
            "phase_1_mcp_servers": {
                "description": "Migrate MCP servers from local machines to NAS",
                "steps": [
                    {
                        "step": 1,
                        "action": "Stop MCP containers on kaiju_no_8 and Millennium Falc",
                        "containers": ["manus-mcp-server", "elevenlabs-mcp-server"],
                        "hosts": [KAIJU_NO_8, MILLENNIUM_FALC]
                    },
                    {
                        "step": 2,
                        "action": "Verify nas-mcp-servers/docker-compose.yml includes all MCP servers",
                        "file": "containerization/services/nas-mcp-servers/docker-compose.yml",
                        "note": "Already contains 20+ MCP servers configured for NAS"
                    },
                    {
                        "step": 3,
                        "action": "Deploy to NAS via DSM Container Manager",
                        "method": "docker-compose up -d on NAS",
                        "target": NAS_DS2118PLUS
                    },
                    {
                        "step": 4,
                        "action": "Update MCP client configurations to point to NAS",
                        "files": [
                            ".cursor/mcp.json",
                            "config/mcp_servers.json"
                        ]
                    },
                    {
                        "step": 5,
                        "action": "Test MCP server connectivity from both clusters",
                        "verify": "Both Ultron and Iron Legion can access NAS MCP servers"
                    }
                ]
            },
            "phase_2_lightweight_containers": {
                "description": "Identify and migrate lightweight Docker containers",
                "steps": [
                    {
                        "step": 1,
                        "action": "Scan for docker-compose.yml files on local machines",
                        "note": "Check for lightweight services that don't need GPU"
                    },
                    {
                        "step": 2,
                        "action": "Categorize containers by resource requirements",
                        "categories": {
                            "lightweight": "CPU-only, <1GB RAM, suitable for NAS",
                            "gpu_required": "Needs GPU, keep on local machines",
                            "high_memory": ">4GB RAM, evaluate case-by-case"
                        }
                    },
                    {
                        "step": 3,
                        "action": "Create NAS docker-compose.yml for lightweight containers",
                        "target": "containerization/services/nas-lightweight-services/docker-compose.yml"
                    },
                    {
                        "step": 4,
                        "action": "Migrate containers to NAS",
                        "method": "docker-compose up -d on NAS"
                    }
                ]
            },
            "phase_3_verification": {
                "description": "Verify migration and update configurations",
                "steps": [
                    {
                        "step": 1,
                        "action": "Verify all containers running on NAS",
                        "check": f"docker ps on {NAS_DS2118PLUS}"
                    },
                    {
                        "step": 2,
                        "action": "Test connectivity from Ultron cluster",
                        "source": MILLENNIUM_FALC,
                        "target": NAS_DS2118PLUS
                    },
                    {
                        "step": 3,
                        "action": "Test connectivity from Iron Legion cluster",
                        "source": KAIJU_NO_8,
                        "target": NAS_DS2118PLUS
                    },
                    {
                        "step": 4,
                        "action": "Update environment.json and cluster configs",
                        "files": [
                            ".cursor/environment.json",
                            "scripts/python/ultron_iron_legion_virtual_cluster.py"
                        ]
                    }
                ]
            }
        }

        self.migration_plan["migrations"] = plan
        return plan

    def generate_migration_script(self, plan: Dict[str, Any]) -> str:
        """Generate PowerShell script for migration"""
        script = f"""# Container Migration to NAS - Generated {datetime.now().isoformat()}
# Target: NAS DS2118+ (<NAS_PRIMARY_IP>) via DSM Container Manager

# Phase 1: Stop MCP containers on local machines
Write-Host "Phase 1: Stopping MCP containers on local machines..."

# Stop on kaiju_no_8
Write-Host "Stopping containers on kaiju_no_8 ({KAIJU_NO_8})..."
ssh user@{KAIJU_NO_8} "cd /path/to/lumina && docker-compose -f containerization/services/mcp-servers/docker-compose.yml down"
ssh user@{KAIJU_NO_8} "cd /path/to/lumina && docker-compose -f containerization/services/manus-mcp-server/docker-compose.yml down"

# Stop on Millennium Falc
Write-Host "Stopping containers on Millennium Falc ({MILLENNIUM_FALC})..."
ssh user@{MILLENNIUM_FALC} "cd /path/to/lumina && docker-compose -f containerization/services/mcp-servers/docker-compose.yml down"

# Phase 2: Deploy to NAS
Write-Host "Phase 2: Deploying to NAS ({NAS_DS2118PLUS})..."

# Deploy nas-mcp-servers (already configured)
ssh user@{NAS_DS2118PLUS} "cd /volume1/docker/lumina && docker-compose -f containerization/services/nas-mcp-servers/docker-compose.yml up -d"

# Phase 3: Verify
Write-Host "Phase 3: Verifying deployment..."
ssh user@{NAS_DS2118PLUS} "docker ps --format 'table {{.Names}}\\t{{.Status}}' | grep -E 'mcp|n8n'"

Write-Host "Migration complete! Verify connectivity from both clusters."
"""
        return script

    def save_migration_plan(self, plan: Dict[str, Any]):
        try:
            """Save migration plan to file"""
            output_file = self.project_root / "data" / "migration_plans" / f"container_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w') as f:
                json.dump(self.migration_plan, f, indent=2)

            logger.info(f"✅ Migration plan saved to: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in save_migration_plan: {e}", exc_info=True)
            raise
    def execute(self):
        try:
            """Execute migration planning"""
            logger.info("🚀 Starting container migration planning...")
            logger.info("=" * 80)

            # Step 1: Identify containers
            identified = self.identify_containers()

            # Step 2: Create migration plan
            plan = self.create_migration_plan(identified)

            # Step 3: Generate migration script
            script = self.generate_migration_script(plan)
            script_file = self.project_root / "scripts" / "powershell" / "Migrate-ContainersToNAS.ps1"
            script_file.parent.mkdir(parents=True, exist_ok=True)
            with open(script_file, 'w') as f:
                f.write(script)
            logger.info(f"✅ Migration script saved to: {script_file}")

            # Step 4: Save plan
            plan_file = self.save_migration_plan(plan)

            # Summary
            logger.info("=" * 80)
            logger.info("📊 MIGRATION PLAN SUMMARY")
            logger.info("=" * 80)
            logger.info(f"Source Hosts:")
            logger.info(f"  - kaiju_no_8: {KAIJU_NO_8}")
            logger.info(f"  - Millennium Falc: {MILLENNIUM_FALC}")
            logger.info(f"Target Host:")
            logger.info(f"  - NAS DS2118+: {NAS_DS2118PLUS}")
            logger.info(f"Containers Identified:")
            logger.info(f"  - MCP Containers: {len(identified['mcp_containers'])}")
            logger.info(f"  - Already on NAS: {len(identified['already_on_nas'])}")
            logger.info(f"Migration Script: {script_file}")
            logger.info(f"Migration Plan: {plan_file}")
            logger.info("=" * 80)

            return {
                "identified": identified,
                "plan": plan,
                "script_file": script_file,
                "plan_file": plan_file
            }


        except Exception as e:
            self.logger.error(f"Error in execute: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        planner = ContainerMigrationPlanner(project_root)
        results = planner.execute()
        return results


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()