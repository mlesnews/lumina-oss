#!/usr/bin/env python3
"""
Docker Model Mapper - Show Actual @AI @LLM #Models

Maps Docker containers to their actual AI/LLM models.
Shows the real models instead of dockerized aliases.

Tags: #DOCKER #AI #LLM #MODEL-MAPPING #OLLAMA
"""

import sys
import json
import subprocess
import requests
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

logger = get_logger("DockerModelMapper")


class DockerModelMapper:
    """
    Docker Model Mapper

    Maps Docker containers to their actual AI/LLM models.
    Shows real models instead of dockerized aliases.
    """

    def __init__(self, project_root: Path):
        """Initialize Docker Model Mapper"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.mapping_path = self.data_path / "docker_model_mapping"
        self.mapping_path.mkdir(parents=True, exist_ok=True)

        # Mapping file
        self.mapping_file = self.mapping_path / "container_model_mapping.json"

        self.logger.info("🔍 Docker Model Mapper initialized")
        self.logger.info("   Purpose: Show actual @AI @LLM #models")
        self.logger.info("   Instead of: Dockerized aliases")

    def get_docker_containers(self) -> List[Dict[str, Any]]:
        """Get list of Docker containers"""
        self.logger.info("🐳 Getting Docker containers...")

        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode != 0:
                self.logger.warning(f"⚠️  Docker command failed: {result.stderr}")
                return []

            containers = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    try:
                        container = json.loads(line)
                        containers.append(container)
                    except json.JSONDecodeError:
                        continue

            self.logger.info(f"   Found {len(containers)} running containers")
            return containers
        except FileNotFoundError:
            self.logger.warning("⚠️  Docker not found in PATH")
            return []
        except Exception as e:
            self.logger.error(f"❌ Error getting containers: {e}")
            return []

    def get_ollama_models(self, endpoint: str) -> List[Dict[str, Any]]:
        """
        Get actual models from Ollama endpoint

        Args:
            endpoint: Ollama API endpoint (e.g., http://localhost:11434)

        Returns:
            List of actual models
        """
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                return models
            else:
                return []
        except Exception as e:
            self.logger.debug(f"   Could not connect to {endpoint}: {e}")
            return []

    def map_container_to_models(self, container: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map a Docker container to its actual models

        Args:
            container: Docker container info

        Returns:
            Mapping with actual models
        """
        container_name = container.get("Names", "")
        image = container.get("Image", "")
        ports = container.get("Ports", "")

        mapping = {
            "container_name": container_name,
            "docker_image": image,
            "ports": ports,
            "actual_models": [],
            "model_endpoints": [],
            "is_ollama": False,
            "is_llm_container": False
        }

        # Check if it's an Ollama container
        if "ollama" in image.lower():
            mapping["is_ollama"] = True
            mapping["is_llm_container"] = True

            # Extract port from container
            port = None
            if ports:
                # Parse ports (format: "0.0.0.0:11434->11434/tcp")
                try:
                    port_part = ports.split("->")[0].split(":")[-1]
                    port = int(port_part)
                except:
                    # Try to find default Ollama port
                    port = 11434

            # Try to get actual models
            endpoints_to_try = []
            if port:
                endpoints_to_try.append(f"http://localhost:{port}")
            endpoints_to_try.append("http://localhost:11434")

            for endpoint in endpoints_to_try:
                models = self.get_ollama_models(endpoint)
                if models:
                    mapping["actual_models"] = models
                    mapping["model_endpoints"] = [endpoint]
                    mapping["endpoint"] = endpoint
                    break

        # Check for other LLM containers
        elif any(keyword in image.lower() for keyword in ["llm", "model", "ai", "gpt", "claude", "anthropic"]):
            mapping["is_llm_container"] = True
            mapping["note"] = "LLM container detected, but model extraction not yet implemented"

        return mapping

    def map_all_containers_to_models(self) -> Dict[str, Any]:
        """
        Map all Docker containers to their actual models

        Returns:
            Complete mapping of containers to actual models
        """
        self.logger.info("🔍 Mapping Docker containers to actual models...")

        containers = self.get_docker_containers()

        mapping = {
            "timestamp": datetime.now().isoformat(),
            "total_containers": len(containers),
            "llm_containers": 0,
            "ollama_containers": 0,
            "containers_with_models": 0,
            "mappings": []
        }

        for container in containers:
            container_mapping = self.map_container_to_models(container)
            mapping["mappings"].append(container_mapping)

            if container_mapping.get("is_llm_container"):
                mapping["llm_containers"] += 1
            if container_mapping.get("is_ollama"):
                mapping["ollama_containers"] += 1
            if container_mapping.get("actual_models"):
                mapping["containers_with_models"] += 1

        # Save mapping
        try:
            with open(self.mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving mapping: {e}")

        self.logger.info(f"✅ Mapping complete: {mapping['containers_with_models']} containers with models identified")

        return mapping

    def get_model_report(self) -> str:
        """Get formatted report showing actual models"""
        mapping = self.map_all_containers_to_models()

        markdown = []
        markdown.append("# 🔍 Docker Container to Actual Model Mapping")
        markdown.append("**Show Actual @AI @LLM #Models Instead of Dockerized Aliases**")
        markdown.append("")
        markdown.append(f"**Generated:** {mapping['timestamp']}")
        markdown.append("")

        markdown.append("## 📊 Summary")
        markdown.append("")
        markdown.append(f"- **Total Containers:** {mapping['total_containers']}")
        markdown.append(f"- **LLM Containers:** {mapping['llm_containers']}")
        markdown.append(f"- **Ollama Containers:** {mapping['ollama_containers']}")
        markdown.append(f"- **Containers with Models:** {mapping['containers_with_models']}")
        markdown.append("")

        # Show mappings
        markdown.append("## 🐳 Container to Model Mappings")
        markdown.append("")

        for container_map in mapping["mappings"]:
            if container_map.get("is_llm_container"):
                markdown.append(f"### {container_map['container_name']}")
                markdown.append("")
                markdown.append(f"**Docker Image:** `{container_map['docker_image']}`")
                markdown.append(f"**Ports:** {container_map['ports']}")
                markdown.append("")

                if container_map.get("is_ollama"):
                    markdown.append("**Type:** Ollama Container")
                    markdown.append("")

                    if container_map.get("actual_models"):
                        markdown.append("**Actual Models:**")
                        markdown.append("")
                        for model in container_map["actual_models"]:
                            model_name = model.get("name", "Unknown")
                            model_size = model.get("size", 0)
                            model_size_gb = model_size / (1024**3) if model_size else 0
                            markdown.append(f"- **{model_name}**")
                            markdown.append(f"  - Size: {model_size_gb:.2f} GB" if model_size_gb > 0 else "  - Size: Unknown")
                            markdown.append(f"  - Endpoint: {container_map.get('endpoint', 'N/A')}")
                            markdown.append("")
                    else:
                        markdown.append("**Actual Models:** ❌ Could not retrieve models")
                        markdown.append(f"**Note:** Container is running but models not accessible")
                        markdown.append("")
                else:
                    markdown.append("**Type:** LLM Container (non-Ollama)")
                    markdown.append(f"**Note:** {container_map.get('note', 'Model extraction not yet implemented')}")
                    markdown.append("")

        # Containers without models
        containers_without_models = [c for c in mapping["mappings"] if not c.get("is_llm_container")]
        if containers_without_models:
            markdown.append("## 🐳 Other Containers (Non-LLM)")
            markdown.append("")
            for container_map in containers_without_models[:10]:  # Limit to first 10
                markdown.append(f"- **{container_map['container_name']}** - `{container_map['docker_image']}`")
            if len(containers_without_models) > 10:
                markdown.append(f"- ... and {len(containers_without_models) - 10} more")
            markdown.append("")

        markdown.append("---")
        markdown.append("")
        markdown.append("**Status:** ✅ **MAPPING COMPLETE**")
        markdown.append(f"**Containers with Models:** {mapping['containers_with_models']}")

        return "\n".join(markdown)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Docker Model Mapper - Show Actual Models")
        parser.add_argument("--map", action="store_true", help="Map containers to models")
        parser.add_argument("--report", action="store_true", help="Display model report")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        mapper = DockerModelMapper(project_root)

        if args.map:
            mapping = mapper.map_all_containers_to_models()
            if args.json:
                print(json.dumps(mapping, indent=2, default=str))
            else:
                print("✅ Container to Model Mapping: COMPLETE")
                print(f"   LLM Containers: {mapping['llm_containers']}")
                print(f"   Containers with Models: {mapping['containers_with_models']}")

        elif args.report:
            report = mapper.get_model_report()
            print(report)

        else:
            report = mapper.get_model_report()
            print(report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()