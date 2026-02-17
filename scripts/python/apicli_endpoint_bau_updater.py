#!/usr/bin/env python3
"""
APICLI Endpoint @BAU Updater

Updates all APICLI endpoints as part of @bau (Business As Usual) workflows.
Runs @v3 verification first, then reruns @v3 health and welfare checks on all
interconnected endpoints, their datapoints and painpoints.

Tags: #APICLI #BAU #V3 #HEALTH_CHECK #WELFARE #ENDPOINTS #DATAPOINTS #PAINPOINTS @JARVIS @LUMINA
"""

import asyncio
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import httpx

from lumina_core.paths import get_script_dir, setup_paths

script_dir = get_script_dir()
project_root_global = script_dir.parent.parent

setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)

    def get_logger(name: str):
        """Fallback logger"""
        return logging.getLogger(name)

logger = get_logger("APICLIEndpointBAUUpdater")


class EndpointStatus(Enum):
    """Endpoint status enumeration"""
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    DOWN = "down"
    UNKNOWN = "unknown"


class DatapointStatus(Enum):
    """Datapoint status enumeration"""
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


@dataclass
class Endpoint:
    """API endpoint definition"""
    name: str
    url: str
    method: str = "GET"
    health_endpoint: Optional[str] = None
    datapoints: List[str] = field(default_factory=list)
    painpoints: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    bau_workflow: bool = True
    v3_verified: bool = False
    last_health_check: Optional[str] = None
    status: str = EndpointStatus.UNKNOWN.value


@dataclass
class Datapoint:
    """Datapoint definition"""
    name: str
    endpoint: str
    path: str
    expected_type: str
    validation_rule: Optional[Dict[str, Any]] = None
    status: str = DatapointStatus.UNKNOWN.value
    last_check: Optional[str] = None
    value: Any = None
    error: Optional[str] = None


@dataclass
class Painpoint:
    """Painpoint definition"""
    name: str
    endpoint: str
    description: str
    severity: str = "medium"  # low, medium, high, critical
    status: str = "active"  # active, resolved, monitoring
    last_occurrence: Optional[str] = None
    occurrences: int = 0


@dataclass
class V3VerificationResult:
    """@v3 verification result"""
    endpoint: str
    verified: bool
    verification_time: str
    issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class HealthWelfareCheck:
    """Health and welfare check result"""
    endpoint: str
    health_status: str
    welfare_status: str
    check_time: str
    datapoints: List[Dict[str, Any]] = field(default_factory=list)
    painpoints: List[Dict[str, Any]] = field(default_factory=list)
    interconnected_endpoints: List[str] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class APICLIEndpointBAUUpdater:
    """
    APICLI Endpoint @BAU Updater

    Updates all APICLI endpoints as part of @bau workflows with:
    - @v3 verification (first pass)
    - @v3 health and welfare checks (second pass)
    - Datapoint validation
    - Painpoint identification
    - Interconnected endpoint analysis
    """

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize APICLI endpoint updater"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.data_dir = self.project_root / "data" / "apicli_endpoints"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load endpoints configuration
        self.endpoints = self._load_endpoints()
        self.datapoints = self._load_datapoints()
        self.painpoints = self._load_painpoints()

        # V3 verification results
        self.v3_results: List[V3VerificationResult] = []

        # Health and welfare check results
        self.health_welfare_results: List[HealthWelfareCheck] = []

        logger.info("✅ APICLI Endpoint @BAU Updater initialized")
        logger.info("   Project Root: %s", self.project_root)
        logger.info("   Endpoints: %d", len(self.endpoints))
        logger.info("   Datapoints: %d", len(self.datapoints))
        logger.info("   Painpoints: %d", len(self.painpoints))

    def _load_endpoints(self) -> List[Endpoint]:
        """Load endpoints configuration"""
        endpoints_file = self.data_dir / "endpoints.json"

        if endpoints_file.exists():
            try:
                with open(endpoints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Endpoint(**ep) for ep in data.get("endpoints", [])]
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("⚠️  Error loading endpoints: %s", e)

        # Default endpoints
        default_endpoints = [
            Endpoint(
                name="AIOS API Gateway",
                url="http://localhost:3000",
                method="GET",
                health_endpoint="/health",
                datapoints=["status", "aios_url", "service"],
                painpoints=["connection_timeout", "service_unavailable"],
                tags=["@bau", "#api_gateway", "#aios"],
                bau_workflow=True
            ),
            Endpoint(
                name="AIOS Kernel",
                url="http://aios_kernel:8080",
                method="GET",
                health_endpoint="/health",
                datapoints=["status", "kernel_version", "resources"],
                painpoints=["kernel_crash", "resource_exhaustion"],
                tags=["@bau", "#aios", "#kernel"],
                bau_workflow=True
            )
        ]

        # Save default endpoints
        self._save_endpoints(default_endpoints)

        return default_endpoints

    def _save_endpoints(self, endpoints: List[Endpoint]):
        try:
            """Save endpoints configuration"""
            endpoints_file = self.data_dir / "endpoints.json"
            data = {
                "endpoints": [asdict(ep) for ep in endpoints],
                "updated_at": datetime.now().isoformat()
            }
            with open(endpoints_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_endpoints: {e}", exc_info=True)
            raise
    def _load_datapoints(self) -> List[Datapoint]:
        """Load datapoints configuration"""
        datapoints_file = self.data_dir / "datapoints.json"

        if datapoints_file.exists():
            try:
                with open(datapoints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Datapoint(**dp) for dp in data.get("datapoints", [])]
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("⚠️  Error loading datapoints: %s", e)

        # Build datapoints from endpoints
        datapoints = []
        for endpoint in self.endpoints:
            for dp_name in endpoint.datapoints:
                datapoints.append(Datapoint(
                    name=dp_name,
                    endpoint=endpoint.name,
                    path=f"/{dp_name}",
                    expected_type="str" if "status" in dp_name else "any"
                ))

        return datapoints

    def _load_painpoints(self) -> List[Painpoint]:
        """Load painpoints configuration"""
        painpoints_file = self.data_dir / "painpoints.json"

        if painpoints_file.exists():
            try:
                with open(painpoints_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return [Painpoint(**pp) for pp in data.get("painpoints", [])]
            except (OSError, json.JSONDecodeError) as e:
                logger.warning("⚠️  Error loading painpoints: %s", e)

        # Build painpoints from endpoints
        painpoints = []
        for endpoint in self.endpoints:
            for pp_name in endpoint.painpoints:
                painpoints.append(Painpoint(
                    name=pp_name,
                    endpoint=endpoint.name,
                    description=f"{pp_name} for {endpoint.name}",
                    severity=("high" if "crash" in pp_name or "failure" in pp_name
                              else "medium")
                ))

        return painpoints

    async def _v3_verify_endpoint(self, endpoint: Endpoint) -> V3VerificationResult:
        """Run @v3 verification on endpoint"""
        logger.info("🔍 @v3 Verifying endpoint: %s", endpoint.name)

        issues = []
        warnings = []
        recommendations = []
        verified = True

        try:
            # Check endpoint accessibility
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    response = await client.get(endpoint.url, follow_redirects=True)
                    if response.status_code >= 400:
                        verified = False
                        issues.append(f"HTTP {response.status_code} error")
                except httpx.TimeoutException:
                    verified = False
                    issues.append("Connection timeout")
                except httpx.ConnectError:
                    verified = False
                    issues.append("Connection refused")
                except Exception as e:
                    verified = False
                    issues.append(f"Connection error: {str(e)}")

            # Check health endpoint if available
            if endpoint.health_endpoint:
                try:
                    health_url = f"{endpoint.url}{endpoint.health_endpoint}"
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        response = await client.get(health_url)
                        if response.status_code != 200:
                            warnings.append(f"Health endpoint returned {response.status_code}")
                        else:
                            try:
                                health_data = response.json()
                                if ("status" in health_data and
                                    health_data["status"] != "operational"):
                                    warnings.append(f"Health status: {health_data.get('status')}")
                            except (json.JSONDecodeError, AttributeError):
                                pass
                except Exception as e:
                    warnings.append(f"Health check failed: {str(e)}")

            # Check required datapoints
            for datapoint in self.datapoints:
                if datapoint.endpoint == endpoint.name:
                    if not datapoint.value:
                        warnings.append(f"Datapoint {datapoint.name} not available")

            # Check active painpoints
            active_pp = [pp for pp in self.painpoints
                        if pp.endpoint == endpoint.name and pp.status == "active"]
            if active_pp:
                warnings.append(f"{len(active_pp)} active painpoints")
                for pp in active_pp:
                    if pp.severity in ["high", "critical"]:
                        issues.append(f"Critical painpoint: {pp.name}")

            if not issues and not warnings:
                recommendations.append("Endpoint ready for @bau workflows")

        except Exception as e:
            verified = False
            issues.append(f"Verification error: {str(e)}")

        result = V3VerificationResult(
            endpoint=endpoint.name,
            verified=verified and len(issues) == 0,
            verification_time=datetime.now().isoformat(),
            issues=issues,
            warnings=warnings,
            recommendations=recommendations
        )

        # Update endpoint
        endpoint.v3_verified = result.verified
        endpoint.status = (EndpointStatus.OPERATIONAL.value if result.verified
                          else EndpointStatus.DEGRADED.value)

        logger.info("   %s: %s", "✅ Verified" if result.verified else "❌ Failed", endpoint.name)
        return result

    async def _check_datapoint(self, datapoint: Datapoint, endpoint: Endpoint) -> Datapoint:
        """Check datapoint health"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.get(f"{endpoint.url}{datapoint.path}")
                    if response.status_code == 200:
                        data = response.json()
                        datapoint.value = data.get(datapoint.name)
                        datapoint.status = DatapointStatus.HEALTHY.value
                    else:
                        datapoint.status = DatapointStatus.WARNING.value
                except Exception as e:
                    datapoint.status = DatapointStatus.CRITICAL.value
        except Exception as e:
            datapoint.status = DatapointStatus.UNKNOWN.value

        datapoint.last_check = datetime.now().isoformat()
        return datapoint

    def _check_painpoint(self, painpoint: Painpoint, endpoint: Endpoint) -> Painpoint:
        """Check painpoint status"""
        if endpoint.status == EndpointStatus.OPERATIONAL.value:
            if painpoint.status == "active":
                # INFO: Auto-resolve logic pending
                logger.debug("   Painpoint active but endpoint operational")
        elif endpoint.status == EndpointStatus.DOWN.value:
            if painpoint.status != "active":
                painpoint.status = "active"
            painpoint.occurrences += 1
            painpoint.last_occurrence = datetime.now().isoformat()
        return painpoint

    def _find_interconnected_endpoints(self, endpoint: Endpoint) -> List[str]:
        """Find interconnected endpoints"""
        interconnected = []
        for other in self.endpoints:
            if other.name == endpoint.name:
                continue
            shared_dp = set(endpoint.datapoints) & set(other.datapoints)
            if shared_dp or endpoint.url in other.url or other.url in endpoint.url:
                interconnected.append(other.name)
        return interconnected

    async def _health_welfare_check(self, endpoint: Endpoint) -> HealthWelfareCheck:
        """Run health and welfare check on endpoint"""
        logger.info("🏥 Health & Welfare check: %s", endpoint.name)
        datapoint_results = []
        for dp in self.datapoints:
            if dp.endpoint == endpoint.name:
                checked_dp = await self._check_datapoint(dp, endpoint)
                datapoint_results.append({
                    "name": checked_dp.name,
                    "status": checked_dp.status,
                    "value": checked_dp.value
                })

        painpoint_results = []
        for pp in self.painpoints:
            if pp.endpoint == endpoint.name:
                checked_pp = self._check_painpoint(pp, endpoint)
                painpoint_results.append({
                    "name": checked_pp.name,
                    "status": checked_pp.status,
                    "severity": checked_pp.severity,
                    "occurrences": checked_pp.occurrences
                })

        interconnected = self._find_interconnected_endpoints(endpoint)
        critical_dp = [d for d in datapoint_results
                       if d["status"] == DatapointStatus.CRITICAL.value]
        active_pp = [p for p in painpoint_results
                     if p["status"] == "active" and p["severity"] in ["high", "critical"]]

        if critical_dp or active_pp:
            welfare_status = "degraded"
        elif any(d["status"] == DatapointStatus.WARNING.value for d in datapoint_results):
            welfare_status = "warning"
        else:
            welfare_status = "healthy"

        result = HealthWelfareCheck(
            endpoint=endpoint.name,
            health_status=endpoint.status,
            welfare_status=welfare_status,
            check_time=datetime.now().isoformat(),
            datapoints=datapoint_results,
            painpoints=painpoint_results,
            interconnected_endpoints=interconnected
        )
        logger.info("   Health: %s, Welfare: %s", endpoint.status, welfare_status)
        return result

    async def update_all_endpoints_bau(self) -> Dict[str, Any]:
        """Update all APICLI endpoints for @bau workflows"""
        logger.info("🔄 Updating all APICLI endpoints for @bau workflows")
        for endpoint in self.endpoints:
            if endpoint.bau_workflow:
                result = await self._v3_verify_endpoint(endpoint)
                self.v3_results.append(result)

        for endpoint in self.endpoints:
            if endpoint.bau_workflow:
                result = await self._health_welfare_check(endpoint)
                self.health_welfare_results.append(result)
                endpoint.last_health_check = datetime.now().isoformat()

        report = self._generate_report()
        self._save_results()
        logger.info("✅ APICLI Endpoint @BAU Update Complete")
        return report

    def _generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        v3_ver = len([r for r in self.v3_results if r.verified])
        v3_fail = len([r for r in self.v3_results if not r.verified])

        healthy_w = len([r for r in self.health_welfare_results if r.welfare_status == "healthy"])
        degraded_w = len([r for r in self.health_welfare_results if r.welfare_status == "degraded"])

        report = {
            "generated_at": datetime.now().isoformat(),
            "v3_verification": {
                "total_endpoints": len(self.v3_results),
                "verified": v3_ver,
                "failed": v3_fail,
                "results": [asdict(r) for r in self.v3_results]
            },
            "health_welfare_checks": {
                "total_endpoints": len(self.health_welfare_results),
                "healthy": healthy_w,
                "degraded": degraded_w,
                "results": [asdict(r) for r in self.health_welfare_results]
            },
            "datapoints_summary": {
                "total": sum(len(r.datapoints) for r in self.health_welfare_results),
                "healthy": sum(len([d for d in r.datapoints
                                    if d["status"] == DatapointStatus.HEALTHY.value])
                               for r in self.health_welfare_results),
                "critical": sum(len([d for d in r.datapoints
                                     if d["status"] == DatapointStatus.CRITICAL.value])
                                for r in self.health_welfare_results)
            }
        }
        return report

    def _save_results(self):
        try:
            """Save verification and health check results"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            v3_file = self.data_dir / f"v3_verification_{timestamp}.json"
            with open(v3_file, 'w', encoding='utf-8') as f:
                json.dump({"results": [asdict(r) for r in self.v3_results]}, f, indent=2)

            health_file = self.data_dir / f"health_welfare_{timestamp}.json"
            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump({"results": [asdict(r) for r in self.health_welfare_results]}, f, indent=2)
            logger.info("   Results saved: %s, %s", v3_file.name, health_file.name)


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse
    parser = argparse.ArgumentParser(description="APICLI Endpoint @BAU Updater")
    parser.add_argument("--update", action="store_true", help="Update all endpoints")
    args = parser.parse_args()
    updater = APICLIEndpointBAUUpdater()
    if args.update:
        report = asyncio.run(updater.update_all_endpoints_bau())
        print(f"\n📊 Report Generated: {report['generated_at']}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()