#!/usr/bin/env python3
"""
System State Verification Script
Verifies actual system state vs expected state

Tag: @triage #verification #oversight #introspection
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests library not available. Install with: pip install requests")

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SystemStateVerifier")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ContainerStatus:
    """Container status information"""
    name: str
    status: str
    health: Optional[str] = None
    ports: Optional[str] = None
    image: Optional[str] = None


@dataclass
class ServiceHealth:
    """Service health information"""
    endpoint: str
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None
    healthy: bool = False


@dataclass
class LLMModel:
    """LLM model information"""
    name: str
    endpoint: str
    available: bool = False
    source: str = "unknown"  # config, discovered, etc.


@dataclass
class SystemState:
    """Complete system state"""
    timestamp: datetime
    containers: List[ContainerStatus] = field(default_factory=list)
    services: List[ServiceHealth] = field(default_factory=list)
    llms: List[LLMModel] = field(default_factory=list)
    discrepancies: List[str] = field(default_factory=list)


class SystemStateVerifier:
    """Verify actual system state vs expected state"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            # Try to find project root
            script_dir = Path(__file__).parent
            project_root = script_dir.parent.parent

        self.project_root = Path(project_root)
        self.state = SystemState(timestamp=datetime.now())

    def verify_docker_containers(self) -> List[ContainerStatus]:
        """Verify Docker containers"""
        logger.info("Verifying Docker containers...")

        containers = []

        try:
            # Run docker ps
            result = subprocess.run(
                ["docker", "ps", "-a", "--format", "json"],
                capture_output=True,
                text=True,
                check=True
            )

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    container = ContainerStatus(
                        name=data.get("Names", "unknown"),
                        status=data.get("Status", "unknown"),
                        health=data.get("Health", None),
                        ports=data.get("Ports", None),
                        image=data.get("Image", None)
                    )
                    containers.append(container)
                except json.JSONDecodeError:
                    continue

            self.state.containers = containers
            logger.info(f"Found {len(containers)} containers")

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to query Docker: {e}")
            self.state.discrepancies.append(f"Docker query failed: {e}")
        except FileNotFoundError:
            logger.error("Docker not found in PATH")
            self.state.discrepancies.append("Docker not found in PATH")

        return containers

    def verify_service_health(self) -> List[ServiceHealth]:
        """Verify service health"""
        logger.info("Verifying service health...")

        if not REQUESTS_AVAILABLE:
            logger.warning("requests library not available, skipping service health checks")
            return []

        services = []
        endpoints = [
            "http://localhost:3000/health",  # Load balancer
            "http://localhost:3001/api/tags",  # Primary Ollama
            "http://localhost:3002/api/tags",  # Secondary Ollama
            "http://localhost:3003/api/tags",  # Tertiary Ollama
            "http://localhost:8000/r5/health",  # R5 API
        ]

        for endpoint in endpoints:
            health = ServiceHealth(endpoint=endpoint)
            try:
                import time
                start = time.time()
                response = requests.get(endpoint, timeout=5)
                health.response_time = time.time() - start
                health.status_code = response.status_code
                health.healthy = response.status_code == 200
            except requests.exceptions.RequestException as e:
                health.error = str(e)
                health.healthy = False

            services.append(health)
            logger.info(f"{endpoint}: {'✓' if health.healthy else '✗'}")

        self.state.services = services
        return services

    def discover_llms(self) -> List[LLMModel]:
        """Discover all LLMs"""
        logger.info("Discovering LLMs...")

        llms = []

        # From config files
        config_llms = self._discover_llms_from_configs()
        llms.extend(config_llms)

        # From running services
        discovered_llms = self._discover_llms_from_services()
        llms.extend(discovered_llms)

        # Deduplicate
        seen = set()
        unique_llms = []
        for llm in llms:
            key = (llm.name, llm.endpoint)
            if key not in seen:
                seen.add(key)
                unique_llms.append(llm)

        self.state.llms = unique_llms
        logger.info(f"Discovered {len(unique_llms)} unique LLMs")

        return unique_llms

    def _discover_llms_from_configs(self) -> List[LLMModel]:
        """Discover LLMs from configuration files"""
        llms = []

        # Check iron_legion_cluster.json
        cluster_config = self.project_root / "<COMPANY>-financial-services_llc-env" / "llm_cluster" / "configs" / "iron_legion_cluster.json"
        if cluster_config.exists():
            try:
                with open(cluster_config, 'r') as f:
                    config = json.load(f)
                    endpoints = config.get("endpoints", {})
                    for endpoint_name, endpoint_config in endpoints.items():
                        models = endpoint_config.get("models", [])
                        url = endpoint_config.get("url", "")
                        for model_name in models:
                            llms.append(LLMModel(
                                name=model_name,
                                endpoint=url,
                                source="llama3.2:3b_cluster.json"
                            ))
            except Exception as e:
                logger.error(f"Failed to parse cluster config: {e}")

        # Check server_config.json
        server_config = self.project_root / "<COMPANY>-financial-services_llc-env" / "llm_cluster" / "configs" / "server_config.json"
        if server_config.exists():
            try:
                with open(server_config, 'r') as f:
                    config = json.load(f)
                    models = config.get("models", {})
                    for model_name in models.keys():
                        llms.append(LLMModel(
                            name=model_name,
                            endpoint="http://localhost:3000",
                            source="server_config.json"
                        ))
                    # Check fallback models
                    fallback = config.get("fallback", {})
                    fallback_models = fallback.get("models", [])
                    for model_name in fallback_models:
                        llms.append(LLMModel(
                            name=model_name,
                            endpoint="http://localhost:3001",
                            source="server_config.json (fallback)"
                        ))
            except Exception as e:
                logger.error(f"Failed to parse server config: {e}")

        # Check kilo_code config
        kilo_config = self.project_root / "config" / "kilo_code_optimized_config.json"
        if kilo_config.exists():
            try:
                with open(kilo_config, 'r') as f:
                    config = json.load(f)
                    models = config.get("llm_config", {}).get("models", {})
                    for model_type, model_name in models.items():
                        llms.append(LLMModel(
                            name=model_name,
                            endpoint="http://localhost:11437",
                            source="kilo_code_optimized_config.json"
                        ))
            except Exception as e:
                logger.error(f"Failed to parse kilo code config: {e}")

        return llms

    def _discover_llms_from_services(self) -> List[LLMModel]:
        """Discover LLMs from running services"""
        llms = []

        if not REQUESTS_AVAILABLE:
            return llms

        endpoints = [
            ("http://localhost:3000", "loadbalancer"),
            ("http://localhost:3001", "primary"),
            ("http://localhost:3002", "secondary"),
            ("http://localhost:3003", "tertiary"),
        ]

        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    for model in models:
                        model_name = model.get("name", "unknown")
                        llms.append(LLMModel(
                            name=model_name,
                            endpoint=endpoint,
                            available=True,
                            source=f"discovered from {name}"
                        ))
            except Exception as e:
                logger.debug(f"Failed to query {endpoint}: {e}")

        return llms

    def compare_expected_vs_actual(self) -> List[str]:
        """Compare expected vs actual state"""
        discrepancies = []

        # Expected containers
        expected_containers = [
            "lumina-ollama-primary",
            "lumina-ollama-secondary",
            "lumina-ollama-tertiary",
            "lumina-llm-loadbalancer"
        ]

        actual_container_names = [c.name for c in self.state.containers]

        for expected in expected_containers:
            if expected not in actual_container_names:
                discrepancies.append(f"Missing container: {expected}")

        # Check container health
        for container in self.state.containers:
            if container.name in expected_containers:
                if container.health and "unhealthy" in container.health.lower():
                    discrepancies.append(f"Unhealthy container: {container.name}")

        # Check service health
        for service in self.state.services:
            if not service.healthy:
                discrepancies.append(f"Unhealthy service: {service.endpoint}")

        self.state.discrepancies = discrepancies
        return discrepancies

    def generate_report(self) -> Dict[str, Any]:
        """Generate verification report"""
        report = {
            "timestamp": self.state.timestamp.isoformat(),
            "containers": [asdict(c) for c in self.state.containers],
            "services": [asdict(s) for s in self.state.services],
            "llms": [asdict(l) for l in self.state.llms],
            "discrepancies": self.state.discrepancies,
            "summary": {
                "total_containers": len(self.state.containers),
                "healthy_containers": len([c for c in self.state.containers if c.health and "healthy" in c.health.lower()]),
                "unhealthy_containers": len([c for c in self.state.containers if c.health and "unhealthy" in c.health.lower()]),
                "total_services": len(self.state.services),
                "healthy_services": len([s for s in self.state.services if s.healthy]),
                "unhealthy_services": len([s for s in self.state.services if not s.healthy]),
                "total_llms": len(self.state.llms),
                "available_llms": len([l for l in self.state.llms if l.available]),
                "total_discrepancies": len(self.state.discrepancies)
            }
        }

        return report

    def verify_all(self) -> Dict[str, Any]:
        """Run all verification checks"""
        logger.info("Starting system state verification...")

        # Verify containers
        self.verify_docker_containers()

        # Verify services
        self.verify_service_health()

        # Discover LLMs
        self.discover_llms()

        # Compare expected vs actual
        self.compare_expected_vs_actual()

        # Generate report
        report = self.generate_report()

        return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Verify system state")
        parser.add_argument("--output", "-o", help="Output file for report", default=None)
        parser.add_argument("--project-root", help="Project root directory", default=None)

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        verifier = SystemStateVerifier(project_root)
        report = verifier.verify_all()

        # Print summary
        print("\n" + "="*60)
        print("SYSTEM STATE VERIFICATION REPORT")
        print("="*60)
        print(f"\nTimestamp: {report['timestamp']}")
        print(f"\nContainers: {report['summary']['total_containers']} total")
        print(f"  Healthy: {report['summary']['healthy_containers']}")
        print(f"  Unhealthy: {report['summary']['unhealthy_containers']}")
        print(f"\nServices: {report['summary']['total_services']} total")
        print(f"  Healthy: {report['summary']['healthy_services']}")
        print(f"  Unhealthy: {report['summary']['unhealthy_services']}")
        print(f"\nLLMs: {report['summary']['total_llms']} total")
        print(f"  Available: {report['summary']['available_llms']}")
        print(f"\nDiscrepancies: {report['summary']['total_discrepancies']}")

        if report['discrepancies']:
            print("\nDiscrepancies:")
            for disc in report['discrepancies']:
                print(f"  - {disc}")

        # Print LLMs
        if report['llms']:
            print("\nDiscovered LLMs:")
            for llm in report['llms']:
                status = "✓" if llm['available'] else "✗"
                print(f"  {status} {llm['name']} @ {llm['endpoint']} (from {llm['source']})")

        # Save report
        if args.output:
            output_path = Path(args.output)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_path}")
        else:
            # Save to default location
            output_path = Path(__file__).parent.parent / "data" / "system_state_report.json"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nReport saved to: {output_path}")

        return 0 if report['summary']['total_discrepancies'] == 0 else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())