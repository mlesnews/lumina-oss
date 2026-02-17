#!/usr/bin/env python3
"""
JARVIS Docker Ubuntu Migration

Migrates Docker containers from Ubuntu to Kali Linux.
LUMINA uses ONLY Kali Linux.

Tags: #MIGRATION #DOCKER #KALI-LINUX
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDockerUbuntu")


class JARVISDockerUbuntuMigration:
    """
    JARVIS Docker Ubuntu Migration

    Migrates Docker containers from Ubuntu to Kali Linux.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.ubuntu_containers: List[Dict[str, Any]] = []

        self.logger.info("✅ JARVIS Docker Ubuntu Migration initialized")

    def find_ubuntu_containers(self) -> List[Dict[str, Any]]:
        """Find all Docker containers using Ubuntu images"""
        self.logger.info("🔍 Searching for Ubuntu Docker containers...")

        try:
            # Find containers using Ubuntu images
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "ancestor=ubuntu:22.04", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            containers = []

            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    if not line.strip():
                        continue

                    parts = line.split('|')
                    if len(parts) >= 2:
                        containers.append({
                            "name": parts[0],
                            "image": parts[1],
                            "status": parts[2] if len(parts) > 2 else "Unknown"
                        })

            # Also check for other Ubuntu versions
            for ubuntu_version in ["ubuntu:20.04", "ubuntu:18.04", "ubuntu:latest"]:
                result = subprocess.run(
                    ["docker", "ps", "-a", "--filter", f"ancestor={ubuntu_version}", "--format", "{{.Names}}|{{.Image}}|{{.Status}}"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0 and result.stdout.strip():
                    for line in result.stdout.strip().split('\n'):
                        if not line.strip():
                            continue

                        parts = line.split('|')
                        if len(parts) >= 2:
                            container_name = parts[0]
                            # Avoid duplicates
                            if not any(c["name"] == container_name for c in containers):
                                containers.append({
                                    "name": container_name,
                                    "image": parts[1],
                                    "status": parts[2] if len(parts) > 2 else "Unknown"
                                })

            self.ubuntu_containers = containers

            self.logger.info(f"   Found {len(containers)} Ubuntu container(s)")
            for container in containers:
                self.logger.info(f"   - {container['name']} ({container['image']}) - {container['status']}")

            return containers

        except FileNotFoundError:
            self.logger.warning("⚠️  Docker not found")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error finding Ubuntu containers: {e}", exc_info=True)
            return []

    def inspect_container(self, container_name: str) -> Dict[str, Any]:
        """Inspect container configuration"""
        self.logger.info(f"🔍 Inspecting container: {container_name}...")

        try:
            result = subprocess.run(
                ["docker", "inspect", container_name],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                if data:
                    return data[0]

            return {}

        except Exception as e:
            self.logger.error(f"❌ Error inspecting container: {e}", exc_info=True)
            return {}

    def create_kali_dockerfile(self, container_name: str, container_config: Dict[str, Any]) -> Optional[Path]:
        """Create Kali Linux Dockerfile"""
        self.logger.info(f"📝 Creating Kali Linux Dockerfile for {container_name}...")

        dockerfile_dir = self.project_root / "containerization" / "services" / container_name
        dockerfile_dir.mkdir(parents=True, exist_ok=True)

        dockerfile_path = dockerfile_dir / "Dockerfile.kali"

        try:
            # Extract configuration from container
            config = container_config.get("Config", {})
            env_vars = config.get("Env", [])
            cmd = config.get("Cmd", [])
            working_dir = config.get("WorkingDir", "/workspace")
            volumes = config.get("Volumes", {})

            # Build Dockerfile
            dockerfile_content = f"""# {container_name} - Kali Linux
# Replaces Ubuntu with Kali Linux for LUMINA compliance
# LUMINA uses ONLY Kali Linux

FROM kalilinux/kali-rolling:latest

# Labels
LABEL maintainer="lumina-ai"
LABEL description="{container_name} - Kali Linux (replaces Ubuntu)"
LABEL version="1.0.0"

# Environment variables
ENV DEBIAN_FRONTEND=noninteractive \\
    PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
"""

            # Add environment variables
            for env_var in env_vars:
                if env_var:
                    dockerfile_content += f'ENV {env_var}\n'

            # Install basic tools
            dockerfile_content += """
# Update and install essential tools
RUN apt-get update && apt-get install -y --no-install-recommends \\
    curl \\
    wget \\
    git \\
    vim \\
    nano \\
    net-tools \\
    iputils-ping \\
    openssh-client \\
    procps \\
    htop \\
    build-essential \\
    python3 \\
    python3-pip \\
    && rm -rf /var/lib/apt/lists/* \\
    && apt-get clean

"""

            # Set working directory
            if working_dir:
                dockerfile_content += f"WORKDIR {working_dir}\n\n"

            # Create volume directories
            if volumes:
                dockerfile_content += "# Create volume directories\n"
                for volume in volumes.keys():
                    dockerfile_content += f"RUN mkdir -p {volume}\n"
                dockerfile_content += "\n"

            # Add volumes
            if volumes:
                volume_list = ", ".join([f'"{v}"' for v in volumes.keys()])
                dockerfile_content += f"VOLUME [{volume_list}]\n\n"

            # Add command
            if cmd:
                cmd_str = json.dumps(cmd)
                dockerfile_content += f"CMD {cmd_str}\n"
            else:
                dockerfile_content += 'CMD ["sleep", "infinity"]\n'

            # Write Dockerfile
            dockerfile_path.write_text(dockerfile_content)

            self.logger.info(f"   ✅ Created Dockerfile: {dockerfile_path}")
            return dockerfile_path

        except Exception as e:
            self.logger.error(f"❌ Error creating Dockerfile: {e}", exc_info=True)
            return None

    def build_kali_image(self, container_name: str, dockerfile_path: Path) -> bool:
        """Build Kali Linux image"""
        self.logger.info(f"🔨 Building Kali Linux image for {container_name}...")

        try:
            image_name = f"{container_name}:kali"

            result = subprocess.run(
                ["docker", "build", "-f", str(dockerfile_path), "-t", image_name, str(dockerfile_path.parent)],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes timeout
            )

            if result.returncode == 0:
                self.logger.info(f"   ✅ Successfully built {image_name}")
                return True
            else:
                self.logger.error(f"   ❌ Build failed: {result.stderr}")
                return False

        except Exception as e:
            self.logger.error(f"❌ Error building image: {e}", exc_info=True)
            return False

    def migrate_container(self, container_name: str) -> Dict[str, Any]:
        try:
            """Migrate container from Ubuntu to Kali Linux"""
            self.logger.info(f"🔄 Migrating container: {container_name}...")

            migration = {
                "container_name": container_name,
                "timestamp": datetime.now().isoformat(),
                "inspect": None,
                "dockerfile": None,
                "build": None,
                "stop": None,
                "remove": None,
                "success": False
            }

            # Step 1: Inspect container
            container_config = self.inspect_container(container_name)
            migration["inspect"] = {"success": bool(container_config)}

            if not container_config:
                self.logger.error(f"   ❌ Failed to inspect container")
                return migration

            # Step 2: Create Kali Dockerfile
            dockerfile_path = self.create_kali_dockerfile(container_name, container_config)
            migration["dockerfile"] = {"success": dockerfile_path is not None, "path": str(dockerfile_path) if dockerfile_path else None}

            if not dockerfile_path:
                self.logger.error(f"   ❌ Failed to create Dockerfile")
                return migration

            # Step 3: Build Kali image
            build_success = self.build_kali_image(container_name, dockerfile_path)
            migration["build"] = {"success": build_success}

            if not build_success:
                self.logger.error(f"   ❌ Failed to build Kali image")
                return migration

            # Step 4: Stop Ubuntu container
            self.logger.info(f"   🛑 Stopping Ubuntu container...")
            stop_result = subprocess.run(
                ["docker", "stop", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            migration["stop"] = {"success": stop_result.returncode == 0}

            # Step 5: Remove Ubuntu container
            self.logger.info(f"   🗑️  Removing Ubuntu container...")
            remove_result = subprocess.run(
                ["docker", "rm", container_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            migration["remove"] = {"success": remove_result.returncode == 0}

            if migration["stop"]["success"] and migration["remove"]["success"]:
                migration["success"] = True
                self.logger.info(f"   ✅ Successfully migrated {container_name}")
            else:
                self.logger.warning(f"   ⚠️  Migration incomplete for {container_name}")

            return migration

        except Exception as e:
            self.logger.error(f"Error in migrate_container: {e}", exc_info=True)
            raise
    def full_migration(self) -> Dict[str, Any]:
        """Perform full Docker Ubuntu migration"""
        self.logger.info("🚀 Starting full Docker Ubuntu migration...")

        # Find Ubuntu containers
        containers = self.find_ubuntu_containers()

        if not containers:
            self.logger.info("   ✅ No Ubuntu containers found")
            return {
                "success": True,
                "message": "No Ubuntu containers to migrate",
                "containers": []
            }

        self.logger.info(f"   Found {len(containers)} Ubuntu container(s) to migrate")

        # Migrate each container
        migrations = []
        for container in containers:
            migration = self.migrate_container(container["name"])
            migrations.append(migration)

        # Summary
        successful = sum(1 for m in migrations if m.get("success"))
        failed = len(migrations) - successful

        result = {
            "success": failed == 0,
            "timestamp": datetime.now().isoformat(),
            "total_ubuntu": len(containers),
            "migrated": successful,
            "failed": failed,
            "migrations": migrations
        }

        self.logger.info(f"   ✅ Migration complete: {successful} successful, {failed} failed")

        return result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Docker Ubuntu Migration")
        parser.add_argument("--find", action="store_true", help="Find Ubuntu containers")
        parser.add_argument("--migrate", action="store_true", help="Migrate all Ubuntu containers")
        parser.add_argument("--migrate-container", type=str, help="Migrate specific container")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        migration = JARVISDockerUbuntuMigration(project_root)

        if args.find:
            containers = migration.find_ubuntu_containers()
            print(json.dumps(containers, indent=2))

        elif args.migrate:
            result = migration.full_migration()
            print(json.dumps(result, indent=2, default=str))

        elif args.migrate_container:
            result = migration.migrate_container(args.migrate_container)
            print(json.dumps(result, indent=2, default=str))

        else:
            print("Usage:")
            print("  --find              : Find Ubuntu containers")
            print("  --migrate            : Migrate all Ubuntu containers")
            print("  --migrate-container  : Migrate specific container")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()