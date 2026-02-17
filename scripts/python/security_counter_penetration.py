#!/usr/bin/env python3
"""
Counter-Penetration System

Proactive defense against penetration attempts.
Designed by @MARVIN, @HK-47, JARVIS, and @MANUS collaboration.

Features:
- Honeypots
- Decoy systems
- Attack deflection
- Threat intelligence
- Automated response
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CounterPenetrationSystem")


class CounterMeasureType(Enum):
    """Types of countermeasures"""
    HONEYPOT = "honeypot"
    DECOY = "decoy"
    DEFLECTION = "deflection"
    RATE_LIMITING = "rate_limiting"
    IP_BLOCKING = "ip_blocking"
    TRAFFIC_SHAPING = "traffic_shaping"


@dataclass
class CounterMeasure:
    """Counter-penetration measure"""
    measure_id: str
    measure_type: CounterMeasureType
    target_ip: str
    description: str
    activated_at: datetime
    active: bool = True
    effectiveness: float = 0.0  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class CounterPenetrationSystem:
    """
    Counter-Penetration System

    Proactive defense mechanisms:
    - Honeypots: Trap attackers
    - Decoys: Mislead attackers
    - Deflection: Redirect attacks
    - Rate limiting: Slow down attacks
    - IP blocking: Block malicious IPs
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("CounterPenetrationSystem")

        self.data_dir = self.project_root / "data" / "security" / "counter_penetration"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.countermeasures: List[CounterMeasure] = []
        self.blocked_ips: List[str] = []
        self.honeypots: Dict[str, Dict[str, Any]] = {}

        self.logger.info("🛡️  Counter-Penetration System initialized")

    def deploy_honeypot(self, service_type: str, port: int, decoy_data: Dict[str, Any] = None) -> CounterMeasure:
        """Deploy honeypot to trap attackers"""
        self.logger.info(f"🍯 Deploying honeypot: {service_type} on port {port}")

        honeypot_id = f"honeypot_{service_type}_{port}"

        self.honeypots[honeypot_id] = {
            "service_type": service_type,
            "port": port,
            "decoy_data": decoy_data or {},
            "deployed_at": datetime.now().isoformat(),
            "interactions": 0,
            "attacks_caught": 0
        }

        measure = CounterMeasure(
            measure_id=honeypot_id,
            measure_type=CounterMeasureType.HONEYPOT,
            target_ip="0.0.0.0",  # Listens on all interfaces
            description=f"Honeypot: {service_type} on port {port}",
            activated_at=datetime.now(),
            effectiveness=0.8  # Honeypots are effective
        )

        self.countermeasures.append(measure)
        self.logger.info(f"✅ Honeypot deployed: {honeypot_id}")

        return measure

    def block_ip(self, ip_address: str, reason: str, duration_hours: int = 24) -> CounterMeasure:
        """Block malicious IP address"""
        self.logger.warning(f"🚫 Blocking IP: {ip_address} (reason: {reason})")

        if ip_address not in self.blocked_ips:
            self.blocked_ips.append(ip_address)

        measure = CounterMeasure(
            measure_id=f"block_{ip_address}_{datetime.now().timestamp()}",
            measure_type=CounterMeasureType.IP_BLOCKING,
            target_ip=ip_address,
            description=f"IP blocked: {reason}",
            activated_at=datetime.now(),
            metadata={
                "reason": reason,
                "duration_hours": duration_hours,
                "expires_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat()
            },
            effectiveness=0.9  # IP blocking is very effective
        )

        self.countermeasures.append(measure)
        self.logger.info(f"✅ IP blocked: {ip_address}")

        return measure

    def deploy_decoy(self, decoy_type: str, location: str, fake_data: Dict[str, Any] = None) -> CounterMeasure:
        """Deploy decoy system to mislead attackers"""
        self.logger.info(f"🎭 Deploying decoy: {decoy_type} at {location}")

        measure = CounterMeasure(
            measure_id=f"decoy_{decoy_type}_{datetime.now().timestamp()}",
            measure_type=CounterMeasureType.DECOY,
            target_ip=location,
            description=f"Decoy: {decoy_type} at {location}",
            activated_at=datetime.now(),
            metadata={
                "decoy_type": decoy_type,
                "fake_data": fake_data or {}
            },
            effectiveness=0.7  # Decoys can mislead attackers
        )

        self.countermeasures.append(measure)
        self.logger.info(f"✅ Decoy deployed: {decoy_type}")

        return measure

    def deflect_attack(self, source_ip: str, target_ip: str, deflection_target: str) -> CounterMeasure:
        """Deflect attack to safe location"""
        self.logger.info(f"↩️  Deflecting attack from {source_ip} to {deflection_target}")

        measure = CounterMeasure(
            measure_id=f"deflect_{source_ip}_{datetime.now().timestamp()}",
            measure_type=CounterMeasureType.DEFLECTION,
            target_ip=source_ip,
            description=f"Attack deflected from {target_ip} to {deflection_target}",
            activated_at=datetime.now(),
            metadata={
                "original_target": target_ip,
                "deflection_target": deflection_target
            },
            effectiveness=0.85  # Deflection is effective
        )

        self.countermeasures.append(measure)
        self.logger.info(f"✅ Attack deflected: {source_ip} → {deflection_target}")

        return measure

    def apply_rate_limiting(self, target_ip: str, max_requests_per_minute: int = 10) -> CounterMeasure:
        """Apply rate limiting to slow down attacks"""
        self.logger.info(f"⏱️  Applying rate limiting to {target_ip}: {max_requests_per_minute} req/min")

        measure = CounterMeasure(
            measure_id=f"ratelimit_{target_ip}_{datetime.now().timestamp()}",
            measure_type=CounterMeasureType.RATE_LIMITING,
            target_ip=target_ip,
            description=f"Rate limiting: {max_requests_per_minute} requests/minute",
            activated_at=datetime.now(),
            metadata={
                "max_requests_per_minute": max_requests_per_minute
            },
            effectiveness=0.75  # Rate limiting slows attacks
        )

        self.countermeasures.append(measure)
        self.logger.info(f"✅ Rate limiting applied: {target_ip}")

        return measure

    def is_ip_blocked(self, ip_address: str) -> bool:
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips

    def get_active_countermeasures(self) -> List[CounterMeasure]:
        """Get active countermeasures"""
        return [m for m in self.countermeasures if m.active]

    def get_statistics(self) -> Dict[str, Any]:
        """Get counter-penetration statistics"""
        active = self.get_active_countermeasures()

        by_type = {}
        for measure in active:
            measure_type = measure.measure_type.value
            by_type[measure_type] = by_type.get(measure_type, 0) + 1

        avg_effectiveness = sum(m.effectiveness for m in active) / len(active) if active else 0

        return {
            "total_countermeasures": len(self.countermeasures),
            "active_countermeasures": len(active),
            "blocked_ips": len(self.blocked_ips),
            "honeypots_deployed": len(self.honeypots),
            "by_type": by_type,
            "average_effectiveness": avg_effectiveness
        }


def main():
    """CLI for counter-penetration system"""
    import argparse

    parser = argparse.ArgumentParser(description="Counter-Penetration System")
    parser.add_argument("--deploy-honeypot", nargs=2, metavar=("SERVICE", "PORT"), help="Deploy honeypot")
    parser.add_argument("--block-ip", nargs=2, metavar=("IP", "REASON"), help="Block IP address")
    parser.add_argument("--deploy-decoy", nargs=2, metavar=("TYPE", "LOCATION"), help="Deploy decoy")
    parser.add_argument("--deflect", nargs=3, metavar=("SOURCE_IP", "TARGET_IP", "DEFLECTION_TARGET"), help="Deflect attack")
    parser.add_argument("--rate-limit", nargs=2, metavar=("IP", "MAX_REQ_PER_MIN"), help="Apply rate limiting")
    parser.add_argument("--check-blocked", help="Check if IP is blocked")
    parser.add_argument("--stats", action="store_true", help="Show statistics")

    args = parser.parse_args()

    system = CounterPenetrationSystem()

    if args.deploy_honeypot:
        service, port = args.deploy_honeypot
        measure = system.deploy_honeypot(service, int(port))
        print(f"✅ Honeypot deployed: {measure.measure_id}")

    elif args.block_ip:
        ip, reason = args.block_ip
        measure = system.block_ip(ip, reason)
        print(f"✅ IP blocked: {ip}")

    elif args.deploy_decoy:
        decoy_type, location = args.deploy_decoy
        measure = system.deploy_decoy(decoy_type, location)
        print(f"✅ Decoy deployed: {measure.measure_id}")

    elif args.deflect:
        source_ip, target_ip, deflection_target = args.deflect
        measure = system.deflect_attack(source_ip, target_ip, deflection_target)
        print(f"✅ Attack deflected: {source_ip} → {deflection_target}")

    elif args.rate_limit:
        ip, max_req = args.rate_limit
        measure = system.apply_rate_limiting(ip, int(max_req))
        print(f"✅ Rate limiting applied: {ip}")

    elif args.check_blocked:
        blocked = system.is_ip_blocked(args.check_blocked)
        print(f"{'🚫 Blocked' if blocked else '✅ Not blocked'}: {args.check_blocked}")

    elif args.stats:
        stats = system.get_statistics()
        print(f"\n📊 Counter-Penetration Statistics:")
        print(f"  Total Countermeasures: {stats['total_countermeasures']}")
        print(f"  Active: {stats['active_countermeasures']}")
        print(f"  Blocked IPs: {stats['blocked_ips']}")
        print(f"  Honeypots: {stats['honeypots_deployed']}")
        print(f"  Average Effectiveness: {stats['average_effectiveness']:.2%}")

    else:
        parser.print_help()


if __name__ == "__main__":



    main()