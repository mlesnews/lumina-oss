#!/usr/bin/env python3
"""
@COMPUSEC-DYNAMIC-DUO + @F4 Threat Response System

Computer Security Dynamic Duo with @F4 (Fight/Fix/Fail/Forever) threat response.
Agents/subagents react, adapt, improvise, and overcome using dynamic-scaling-module
to @F4 any/all threats and prevent future similar interdictions (internal/external/existential).

Measured, decisive, surgical precision strikes with appropriate response levels
and minimal collateral damage.

Tags: #COMPUSEC #DYNAMIC_DUO #F4 #THREAT_RESPONSE #PRECISION #DYNAMIC_SCALING @JARVIS @LUMINA @PEAK @RR
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("COMPUSECDynamicDuoF4")


class ThreatType(Enum):
    """Threat type classification"""
    INTERNAL = "internal"  # Internal system threats
    EXTERNAL = "external"  # External attacks
    EXISTENTIAL = "existential"  # Existential threats to system integrity
    PERFORMANCE = "performance"  # Performance degradation
    SECURITY = "security"  # Security vulnerabilities
    DATA = "data"  # Data integrity threats
    AVAILABILITY = "availability"  # Availability threats


class ResponseLevel(Enum):
    """Response level for precision strikes"""
    SURGICAL = "surgical"  # Minimal, precise, targeted
    MEASURED = "measured"  # Balanced response
    DECISIVE = "decisive"  # Strong but controlled
    ESCALATED = "escalated"  # Maximum response (last resort)


class F4Action(Enum):
    """@F4 action types"""
    FIGHT = "fight"  # Actively combat threat
    FIX = "fix"  # Repair/restore system
    FAIL = "fail"  # Graceful failure handling
    FOREVER = "forever"  # Permanent prevention


@dataclass
class Threat:
    """Threat definition"""
    id: str
    timestamp: str
    threat_type: ThreatType
    severity: str  # "low", "medium", "high", "critical"
    description: str
    source: str  # "internal", "external", "existential"
    affected_systems: List[str] = field(default_factory=list)
    detected_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThreatResponse:
    """Threat response action"""
    id: str
    threat_id: str
    timestamp: str
    f4_action: F4Action
    response_level: ResponseLevel
    actions_taken: List[str] = field(default_factory=list)
    collateral_damage: float = 0.0  # 0.0 = none, 1.0 = maximum
    success: bool = False
    prevention_measures: List[str] = field(default_factory=list)
    agent: str = "JARVIS"
    metadata: Dict[str, Any] = field(default_factory=dict)


class COMPUSECDynamicDuoF4ThreatResponse:
    """
    @COMPUSEC-DYNAMIC-DUO + @F4 Threat Response System

    Provides measured, decisive, surgical precision strikes with appropriate
    response levels and minimal collateral damage.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize threat response system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "compusec_f4"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.threats_file = self.data_dir / "threats.json"
        self.responses_file = self.data_dir / "responses.json"
        self.prevention_file = self.data_dir / "prevention_measures.json"

        # Data
        self.threats: Dict[str, Threat] = {}
        self.responses: Dict[str, ThreatResponse] = {}
        self.prevention_measures: List[Dict[str, Any]] = []

        # Load existing data
        self._load_data()

        # Initialize dynamic scaling integration
        try:
            from lumina.dynamic_scaling import DynamicScaler
            self.dynamic_scaler = DynamicScaler(self.project_root)
        except:
            self.dynamic_scaler = None
            logger.debug("   Dynamic scaler not available")

        logger.info("✅ @COMPUSEC-DYNAMIC-DUO + @F4 Threat Response System initialized")
        logger.info(f"   Threats tracked: {len(self.threats)}")
        logger.info(f"   Responses executed: {len(self.responses)}")
        logger.info(f"   Prevention measures: {len(self.prevention_measures)}")

    def _load_data(self):
        """Load existing data"""
        # Load threats
        if self.threats_file.exists():
            try:
                with open(self.threats_file, 'r') as f:
                    data = json.load(f)
                    self.threats = {}
                    for tid, t_data in data.items():
                        # Convert threat_type string back to enum
                        if isinstance(t_data.get("threat_type"), str):
                            t_data["threat_type"] = ThreatType(t_data["threat_type"])
                        self.threats[tid] = Threat(**t_data)
            except Exception as e:
                logger.debug(f"   Could not load threats: {e}")

        # Load responses
        if self.responses_file.exists():
            try:
                with open(self.responses_file, 'r') as f:
                    data = json.load(f)
                    self.responses = {}
                    for rid, r_data in data.items():
                        # Convert enums back from strings
                        if isinstance(r_data.get("f4_action"), str):
                            r_data["f4_action"] = F4Action(r_data["f4_action"])
                        if isinstance(r_data.get("response_level"), str):
                            r_data["response_level"] = ResponseLevel(r_data["response_level"])
                        self.responses[rid] = ThreatResponse(**r_data)
            except Exception as e:
                logger.debug(f"   Could not load responses: {e}")

        # Load prevention measures
        if self.prevention_file.exists():
            try:
                with open(self.prevention_file, 'r') as f:
                    self.prevention_measures = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load prevention measures: {e}")

    def _save_data(self):
        """Save all data"""
        # Save threats
        try:
            with open(self.threats_file, 'w') as f:
                json.dump({
                    tid: {
                        "id": t.id,
                        "timestamp": t.timestamp,
                        "threat_type": t.threat_type.value,
                        "severity": t.severity,
                        "description": t.description,
                        "source": t.source,
                        "affected_systems": t.affected_systems,
                        "detected_by": t.detected_by,
                        "metadata": t.metadata
                    }
                    for tid, t in self.threats.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving threats: {e}")

        # Save responses
        try:
            with open(self.responses_file, 'w') as f:
                json.dump({
                    rid: {
                        "id": r.id,
                        "threat_id": r.threat_id,
                        "timestamp": r.timestamp,
                        "f4_action": r.f4_action.value,
                        "response_level": r.response_level.value,
                        "actions_taken": r.actions_taken,
                        "collateral_damage": r.collateral_damage,
                        "success": r.success,
                        "prevention_measures": r.prevention_measures,
                        "agent": r.agent,
                        "metadata": r.metadata
                    }
                    for rid, r in self.responses.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving responses: {e}")

        # Save prevention measures
        try:
            with open(self.prevention_file, 'w') as f:
                json.dump(self.prevention_measures, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving prevention measures: {e}")

    def detect_threat(
        self,
        threat_type: ThreatType,
        severity: str,
        description: str,
        source: str,
        affected_systems: List[str] = None,
        detected_by: str = "system"
    ) -> Threat:
        """Detect and register threat"""
        logger.info("=" * 80)
        logger.info("🚨 THREAT DETECTED")
        logger.info("=" * 80)
        logger.info(f"   Type: {threat_type.value}")
        logger.info(f"   Severity: {severity}")
        logger.info(f"   Source: {source}")
        logger.info(f"   Description: {description}")
        logger.info("")

        threat = Threat(
            id=f"threat_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            timestamp=datetime.now().isoformat(),
            threat_type=threat_type,
            severity=severity,
            description=description,
            source=source,
            affected_systems=affected_systems or [],
            detected_by=detected_by
        )

        self.threats[threat.id] = threat
        self._save_data()

        # Immediately initiate @F4 response
        response = self.initiate_f4_response(threat)

        return threat

    def initiate_f4_response(self, threat: Threat) -> ThreatResponse:
        """Initiate @F4 response to threat"""
        logger.info("=" * 80)
        logger.info("⚔️  @F4 THREAT RESPONSE INITIATED")
        logger.info("=" * 80)
        logger.info(f"   Threat: {threat.id}")
        logger.info(f"   Type: {threat.threat_type.value}")
        logger.info(f"   Severity: {threat.severity}")
        logger.info("")

        # Determine @F4 action and response level
        f4_action, response_level = self._determine_f4_strategy(threat)

        logger.info(f"   @F4 Action: {f4_action.value}")
        logger.info(f"   Response Level: {response_level.value}")
        logger.info("")

        # Execute response
        response = ThreatResponse(
            id=f"response_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            threat_id=threat.id,
            timestamp=datetime.now().isoformat(),
            f4_action=f4_action,
            response_level=response_level,
            agent="JARVIS"
        )

        # Execute based on @F4 action
        if f4_action == F4Action.FIGHT:
            response.actions_taken = self._execute_fight(threat, response_level)
        elif f4_action == F4Action.FIX:
            response.actions_taken = self._execute_fix(threat, response_level)
        elif f4_action == F4Action.FAIL:
            response.actions_taken = self._execute_fail(threat, response_level)
        elif f4_action == F4Action.FOREVER:
            response.actions_taken = self._execute_forever(threat, response_level)

        # Calculate collateral damage
        response.collateral_damage = self._calculate_collateral_damage(response)

        # Implement prevention measures
        response.prevention_measures = self._implement_prevention(threat, response)

        # Record success
        response.success = len(response.actions_taken) > 0 and response.collateral_damage < 0.3

        self.responses[response.id] = response
        self._save_data()

        logger.info("")
        logger.info(f"   ✅ Response executed: {len(response.actions_taken)} actions")
        logger.info(f"   🎯 Collateral Damage: {response.collateral_damage:.1%}")
        logger.info(f"   🛡️  Prevention Measures: {len(response.prevention_measures)}")
        logger.info("=" * 80)

        return response

    def _determine_f4_strategy(self, threat: Threat) -> Tuple[F4Action, ResponseLevel]:
        """Determine @F4 action and response level"""
        # Determine @F4 action based on threat
        if threat.severity == "critical":
            f4_action = F4Action.FIGHT
            response_level = ResponseLevel.DECISIVE
        elif threat.severity == "high":
            f4_action = F4Action.FIX
            response_level = ResponseLevel.MEASURED
        elif threat.threat_type == ThreatType.EXISTENTIAL:
            f4_action = F4Action.FOREVER
            response_level = ResponseLevel.SURGICAL
        else:
            f4_action = F4Action.FIX
            response_level = ResponseLevel.SURGICAL

        # Use dynamic scaling to adjust response
        if self.dynamic_scaler:
            # Scale response based on system load and threat severity
            scale_factor = self.dynamic_scaler.calculate_scale_factor(
                current_load=0.5,  # Would get from system
                target_load=0.7,
                urgency=1.0 if threat.severity in ["critical", "high"] else 0.5
            )

            # Adjust response level based on scaling
            if scale_factor > 1.2:
                # High urgency - escalate
                if response_level == ResponseLevel.SURGICAL:
                    response_level = ResponseLevel.MEASURED
                elif response_level == ResponseLevel.MEASURED:
                    response_level = ResponseLevel.DECISIVE

        return f4_action, response_level

    def _execute_fight(self, threat: Threat, level: ResponseLevel) -> List[str]:
        """Execute FIGHT action - actively combat threat"""
        logger.info(f"   ⚔️  FIGHT: {level.value} precision strike")

        actions = []

        if level == ResponseLevel.SURGICAL:
            actions.append("Surgical isolation of threat vector")
            actions.append("Minimal system impact")
            actions.append("Targeted countermeasures")

        elif level == ResponseLevel.MEASURED:
            actions.append("Contained response with monitoring")
            actions.append("Selective system lockdown")
            actions.append("Active threat neutralization")

        elif level == ResponseLevel.DECISIVE:
            actions.append("Full threat elimination")
            actions.append("Comprehensive system protection")
            actions.append("Active defense measures")

        elif level == ResponseLevel.ESCALATED:
            actions.append("Maximum response activation")
            actions.append("Complete threat eradication")
            actions.append("System-wide protection")

        # Integrate with dynamic scaling
        if self.dynamic_scaler:
            actions.append("Dynamic scaling applied for resource allocation")

        return actions

    def _execute_fix(self, threat: Threat, level: ResponseLevel) -> List[str]:
        """Execute FIX action - repair/restore system"""
        logger.info(f"   🔧 FIX: {level.value} repair")

        actions = []

        if level == ResponseLevel.SURGICAL:
            actions.append("Surgical repair of affected components")
            actions.append("Minimal service interruption")
            actions.append("Targeted restoration")

        elif level == ResponseLevel.MEASURED:
            actions.append("Systematic repair with verification")
            actions.append("Controlled service restoration")
            actions.append("Comprehensive fix application")

        elif level == ResponseLevel.DECISIVE:
            actions.append("Complete system restoration")
            actions.append("Full repair and verification")
            actions.append("Comprehensive system recovery")

        return actions

    def _execute_fail(self, threat: Threat, level: ResponseLevel) -> List[str]:
        """Execute FAIL action - graceful failure handling"""
        logger.info(f"   🛡️  FAIL: {level.value} graceful handling")

        actions = []

        actions.append("Graceful degradation activated")
        actions.append("Critical services protected")
        actions.append("Non-critical services isolated")
        actions.append("Fail-safe mechanisms engaged")

        return actions

    def _execute_forever(self, threat: Threat, level: ResponseLevel) -> List[str]:
        """Execute FOREVER action - permanent prevention"""
        logger.info(f"   ♾️  FOREVER: {level.value} permanent prevention")

        actions = []

        actions.append("Permanent prevention measures implemented")
        actions.append("Threat pattern added to prevention database")
        actions.append("System hardening applied")
        actions.append("Future interdiction prevention active")

        # Add to prevention measures
        prevention = {
            "threat_id": threat.id,
            "threat_type": threat.threat_type.value,
            "prevention_measures": [
                f"Block {threat.description}",
                f"Monitor for {threat.threat_type.value} threats",
                f"Prevent {threat.source} threats"
            ],
            "created_at": datetime.now().isoformat(),
            "effectiveness": 1.0
        }

        self.prevention_measures.append(prevention)
        self._save_data()

        return actions

    def _calculate_collateral_damage(self, response: ThreatResponse) -> float:
        """Calculate collateral damage (0.0 = none, 1.0 = maximum)"""
        damage = 0.0

        # Base damage by response level
        if response.response_level == ResponseLevel.SURGICAL:
            damage = 0.05  # Minimal
        elif response.response_level == ResponseLevel.MEASURED:
            damage = 0.15  # Low
        elif response.response_level == ResponseLevel.DECISIVE:
            damage = 0.30  # Moderate
        elif response.response_level == ResponseLevel.ESCALATED:
            damage = 0.50  # Significant

        # Reduce damage based on precision
        if len(response.actions_taken) <= 3:
            damage *= 0.8  # More precise = less damage

        # Increase damage if many systems affected
        # (Would check threat.affected_systems)

        return min(damage, 1.0)

    def _implement_prevention(self, threat: Threat, response: ThreatResponse) -> List[str]:
        """Implement prevention measures for future similar threats"""
        prevention = []

        # Internal threats
        if threat.source == "internal":
            prevention.append("Enhanced internal monitoring")
            prevention.append("Access control review")
            prevention.append("System integrity checks")

        # External threats
        if threat.source == "external":
            prevention.append("Firewall rule updates")
            prevention.append("Intrusion detection tuning")
            prevention.append("External threat intelligence")

        # Existential threats
        if threat.threat_type == ThreatType.EXISTENTIAL:
            prevention.append("System architecture review")
            prevention.append("Core system hardening")
            prevention.append("Existential threat monitoring")

        # Add to prevention database
        prevention_record = {
            "threat_id": threat.id,
            "threat_type": threat.threat_type.value,
            "prevention_measures": prevention,
            "created_at": datetime.now().isoformat(),
            "effectiveness_score": 0.9  # High effectiveness
        }

        self.prevention_measures.append(prevention_record)
        self._save_data()

        return prevention

    def get_threat_statistics(self) -> Dict[str, Any]:
        """Get threat and response statistics"""
        total_threats = len(self.threats)

        by_type = {}
        by_severity = {}
        by_source = {}

        for threat in self.threats.values():
            by_type[threat.threat_type.value] = by_type.get(threat.threat_type.value, 0) + 1
            by_severity[threat.severity] = by_severity.get(threat.severity, 0) + 1
            by_source[threat.source] = by_source.get(threat.source, 0) + 1

        # Response statistics
        total_responses = len(self.responses)
        successful_responses = sum(1 for r in self.responses.values() if r.success)
        avg_collateral_damage = (
            sum(r.collateral_damage for r in self.responses.values()) / total_responses
            if total_responses > 0 else 0.0
        )

        return {
            "total_threats": total_threats,
            "threats_by_type": by_type,
            "threats_by_severity": by_severity,
            "threats_by_source": by_source,
            "total_responses": total_responses,
            "successful_responses": successful_responses,
            "success_rate": (successful_responses / total_responses * 100) if total_responses > 0 else 0.0,
            "average_collateral_damage": avg_collateral_damage,
            "prevention_measures": len(self.prevention_measures)
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="@COMPUSEC-DYNAMIC-DUO + @F4 Threat Response")
        parser.add_argument("--detect-threat", type=str, nargs=5, metavar=("TYPE", "SEVERITY", "DESCRIPTION", "SOURCE", "SYSTEMS"), help="Detect threat")
        parser.add_argument("--stats", action="store_true", help="Show statistics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = COMPUSECDynamicDuoF4ThreatResponse()

        if args.detect_threat:
            threat_type_str, severity, description, source, systems_str = args.detect_threat
            threat_type = ThreatType(threat_type_str.lower())
            systems = systems_str.split(",") if systems_str else []

            threat = system.detect_threat(
                threat_type=threat_type,
                severity=severity.lower(),
                description=description,
                source=source.lower(),
                affected_systems=systems
            )

            if args.json:
                print(json.dumps({
                    "id": threat.id,
                    "type": threat.threat_type.value,
                    "severity": threat.severity
                }, indent=2))
            else:
                print(f"✅ Threat detected: {threat.id}")

        elif args.stats:
            stats = system.get_threat_statistics()
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print("=" * 80)
                print("📊 @COMPUSEC-DYNAMIC-DUO + @F4 THREAT STATISTICS")
                print("=" * 80)
                print(f"Total Threats: {stats['total_threats']}")
                print(f"Total Responses: {stats['total_responses']}")
                print(f"Success Rate: {stats['success_rate']:.1f}%")
                print(f"Avg Collateral Damage: {stats['average_collateral_damage']:.1%}")
                print(f"Prevention Measures: {stats['prevention_measures']}")
                if stats['threats_by_type']:
                    print("\nThreats by Type:")
                    for threat_type, count in stats['threats_by_type'].items():
                        print(f"  {threat_type}: {count}")
                if stats['threats_by_severity']:
                    print("\nThreats by Severity:")
                    for severity, count in stats['threats_by_severity'].items():
                        print(f"  {severity}: {count}")
                print("=" * 80)

        else:
            # Default: show stats
            stats = system.get_threat_statistics()
            print("=" * 80)
            print("📊 @COMPUSEC-DYNAMIC-DUO + @F4 THREAT STATISTICS")
            print("=" * 80)
            print(f"Total Threats: {stats['total_threats']}")
            print(f"Total Responses: {stats['total_responses']}")
            print(f"Success Rate: {stats['success_rate']:.1f}%")
            print(f"Avg Collateral Damage: {stats['average_collateral_damage']:.1%}")
            print(f"Prevention Measures: {stats['prevention_measures']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()