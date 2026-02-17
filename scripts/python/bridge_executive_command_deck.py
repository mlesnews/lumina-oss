#!/usr/bin/env python3
"""
Bridge Executive Command Deck - Naval/Maritime (Terrestrial & Space) Tactical Warfare

Inspired by naval and maritime command structures with tactical warfare application:
- Bridge command center
- Executive decision-making
- Tactical operations
- Terrestrial and space operations
- Real-time situation awareness
- Tactical displays
- Command hierarchy

Integrates with:
- JARVIS Command & Control Center
- JARVIS Governance System
- All LUMINA systems
- Intelligence systems
- Communication systems

Tags: #BRIDGE #COMMAND_DECK #NAVAL #MARITIME #TACTICAL #WARFARE #TERRESTRIAL #SPACE @JARVIS @LUMINA @PEAK @DTN
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
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

logger = get_logger("BridgeCommandDeck")


class OperationalDomain(Enum):
    """Operational domains"""
    TERRESTRIAL = "terrestrial"  # Earth-based operations
    MARITIME = "maritime"  # Ocean/sea operations
    AEROSPACE = "aerospace"  # Air/space operations
    SPACE = "space"  # Space operations
    DEEP_SPACE = "deep_space"  # Deep space operations


class TacticalStatus(Enum):
    """Tactical status levels"""
    GREEN = "green"  # All clear, normal operations
    YELLOW = "yellow"  # Caution, heightened awareness
    ORANGE = "orange"  # Alert, potential threat
    RED = "red"  # Critical, immediate action required
    BLACK = "black"  # Emergency, maximum alert


class BridgeStation(Enum):
    """Bridge stations (officer positions)"""
    CAPTAIN = "captain"  # Executive command
    TACTICAL_OFFICER = "tactical_officer"  # Tactical operations
    NAVIGATION_OFFICER = "navigation_officer"  # Navigation and routing
    COMMUNICATIONS_OFFICER = "communications_officer"  # Communications
    ENGINEERING_OFFICER = "engineering_officer"  # Systems and resources
    INTELLIGENCE_OFFICER = "intelligence_officer"  # Intelligence and analysis
    WEAPONS_OFFICER = "weapons_officer"  # Operations and execution
    SCIENCE_OFFICER = "science_officer"  # Analysis and research


@dataclass
class TacticalSituation:
    """Tactical situation assessment"""
    situation_id: str
    domain: str  # OperationalDomain value
    status: str  # TacticalStatus value
    threat_level: int = 0  # 0-10
    description: str = ""
    assets_available: List[str] = field(default_factory=list)
    threats_identified: List[str] = field(default_factory=list)
    tactical_options: List[Dict[str, Any]] = field(default_factory=list)
    recommended_action: Optional[str] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeOrder:
    """Bridge order (command)"""
    order_id: str
    station: str  # BridgeStation value
    order_type: str  # tactical, navigation, communication, engineering, etc.
    command: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10
    status: str = "pending"  # pending, executing, completed, failed
    executed_by: Optional[str] = None
    execution_result: Optional[Dict[str, Any]] = None
    timestamp: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BridgeStatus:
    """Bridge status display"""
    bridge_id: str
    domain: str  # OperationalDomain value
    tactical_status: str  # TacticalStatus value
    stations_manned: Dict[str, bool] = field(default_factory=dict)
    active_operations: List[str] = field(default_factory=list)
    alerts: List[str] = field(default_factory=list)
    systems_status: Dict[str, str] = field(default_factory=dict)
    timestamp: str = ""


class BridgeExecutiveCommandDeck:
    """
    Bridge Executive Command Deck

    Naval/Maritime inspired command center:
    - Executive command structure
    - Tactical warfare application
    - Terrestrial and space operations
    - Real-time situation awareness
    - Tactical decision-making
    - Command hierarchy
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Bridge Executive Command Deck"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "bridge_command_deck"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.orders_file = self.data_dir / "orders.json"
        self.situations_file = self.data_dir / "situations.json"
        self.status_file = self.data_dir / "bridge_status.json"

        # Bridge state
        self.current_domain = OperationalDomain.TERRESTRIAL
        self.tactical_status = TacticalStatus.GREEN
        self.active_orders: Dict[str, BridgeOrder] = {}
        self.tactical_situations: Dict[str, TacticalSituation] = {}
        self.bridge_status: Optional[BridgeStatus] = None

        # Station assignments
        self.stations: Dict[str, str] = {}  # station -> officer/system

        # Load state
        self._load_state()

        # Initialize bridge
        self._initialize_bridge()

        # Integrate with systems
        self._integrate_systems()

        logger.info("✅ Bridge Executive Command Deck initialized")
        logger.info(f"   Domain: {self.current_domain.value}")
        logger.info(f"   Tactical Status: {self.tactical_status.value}")
        logger.info("   Stations: Manned and ready")

    def _load_state(self):
        """Load bridge state"""
        # Load orders
        if self.orders_file.exists():
            try:
                with open(self.orders_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.active_orders = {
                        k: BridgeOrder(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load orders: {e}")

        # Load situations
        if self.situations_file.exists():
            try:
                with open(self.situations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.tactical_situations = {
                        k: TacticalSituation(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"Could not load situations: {e}")

        # Load bridge status
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.bridge_status = BridgeStatus(**data)
            except Exception as e:
                logger.debug(f"Could not load bridge status: {e}")

    def _save_state(self):
        """Save bridge state"""
        # Save orders
        try:
            with open(self.orders_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.active_orders.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving orders: {e}")

        # Save situations
        try:
            with open(self.situations_file, 'w', encoding='utf-8') as f:
                json.dump({k: asdict(v) for k, v in self.tactical_situations.items()}, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving situations: {e}")

        # Save bridge status
        if self.bridge_status:
            try:
                with open(self.status_file, 'w', encoding='utf-8') as f:
                    json.dump(asdict(self.bridge_status), f, indent=2, default=str)
            except Exception as e:
                logger.error(f"Error saving bridge status: {e}")

    def _initialize_bridge(self):
        """Initialize bridge stations"""
        # Assign stations to systems
        self.stations = {
            BridgeStation.CAPTAIN.value: "JARVIS_Executive",
            BridgeStation.TACTICAL_OFFICER.value: "JARVIS_Tactical",
            BridgeStation.NAVIGATION_OFFICER.value: "JARVIS_Navigation",
            BridgeStation.COMMUNICATIONS_OFFICER.value: "JARVIS_Communications",
            BridgeStation.ENGINEERING_OFFICER.value: "JARVIS_Engineering",
            BridgeStation.INTELLIGENCE_OFFICER.value: "JARVIS_Intelligence",
            BridgeStation.WEAPONS_OFFICER.value: "JARVIS_Operations",
            BridgeStation.SCIENCE_OFFICER.value: "JARVIS_Analysis"
        }

        # Initialize bridge status
        if not self.bridge_status:
            self.bridge_status = BridgeStatus(
                bridge_id="bridge_primary",
                domain=self.current_domain.value,
                tactical_status=self.tactical_status.value,
                stations_manned={station: True for station in self.stations.keys()},
                systems_status={}
            )

    def _integrate_systems(self):
        """Integrate with LUMINA systems"""
        # Command & Control integration
        try:
            from jarvis_command_control_center import JARVISCommandControlCenter
            self.command_control = JARVISCommandControlCenter(project_root=self.project_root)
            logger.info("   ✅ Command & Control integrated")
        except Exception as e:
            logger.warning(f"Command & Control not available: {e}")
            self.command_control = None

        # Governance integration
        try:
            from jarvis_governance_system import JARVISGovernanceSystem
            self.governance = JARVISGovernanceSystem(project_root=self.project_root)
            logger.info("   ✅ Governance integrated")
        except Exception as e:
            logger.warning(f"Governance not available: {e}")
            self.governance = None

        # Communication integration
        try:
            from lumina_n8n_nas_communication_integration import LUMINAN8NNASCommunicationIntegration
            self.communications = LUMINAN8NNASCommunicationIntegration(project_root=self.project_root)
            logger.info("   ✅ Communications integrated")
        except Exception as e:
            logger.warning(f"Communications not available: {e}")
            self.communications = None

        # Intelligence integration
        try:
            from lumina_intelligence_collection import LUMINAIntelligenceCollection
            self.intelligence = LUMINAIntelligenceCollection(project_root=self.project_root)
            logger.info("   ✅ Intelligence integrated")
        except Exception as e:
            logger.warning(f"Intelligence not available: {e}")
            self.intelligence = None

    def assess_tactical_situation(
        self,
        domain: OperationalDomain,
        description: str,
        threats: Optional[List[str]] = None,
        assets: Optional[List[str]] = None
    ) -> TacticalSituation:
        """
        Assess tactical situation

        Naval/maritime tactical assessment:
        - Threat identification
        - Asset availability
        - Tactical options
        - Recommended action
        """
        situation_id = f"situation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Assess threat level
        threat_level = len(threats or []) * 2  # Simple calculation
        if threat_level > 10:
            threat_level = 10

        # Determine tactical status
        if threat_level >= 8:
            status = TacticalStatus.BLACK
        elif threat_level >= 6:
            status = TacticalStatus.RED
        elif threat_level >= 4:
            status = TacticalStatus.ORANGE
        elif threat_level >= 2:
            status = TacticalStatus.YELLOW
        else:
            status = TacticalStatus.GREEN

        # Generate tactical options
        tactical_options = self._generate_tactical_options(domain, threat_level, assets or [])

        # Determine recommended action
        recommended_action = self._determine_recommended_action(tactical_options, threat_level)

        situation = TacticalSituation(
            situation_id=situation_id,
            domain=domain.value,
            status=status.value,
            threat_level=threat_level,
            description=description,
            assets_available=assets or [],
            threats_identified=threats or [],
            tactical_options=tactical_options,
            recommended_action=recommended_action,
            timestamp=datetime.now().isoformat()
        )

        self.tactical_situations[situation_id] = situation
        self.tactical_status = status
        self.bridge_status.tactical_status = status.value
        self._save_state()

        logger.warning(f"   🚨 Tactical Situation: {status.value.upper()} - Threat Level {threat_level}/10")

        return situation

    def _generate_tactical_options(
        self,
        domain: OperationalDomain,
        threat_level: int,
        assets: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate tactical options based on situation"""
        options = []

        # Defensive options
        if threat_level >= 4:
            options.append({
                "type": "defensive",
                "name": "Defensive Posture",
                "description": "Assume defensive position, secure assets",
                "risk": "low",
                "effectiveness": "high" if threat_level < 7 else "medium"
            })

        # Offensive options
        if threat_level >= 6 and len(assets) > 0:
            options.append({
                "type": "offensive",
                "name": "Active Response",
                "description": "Engage threats with available assets",
                "risk": "medium",
                "effectiveness": "high"
            })

        # Evasive options
        if threat_level >= 5:
            options.append({
                "type": "evasive",
                "name": "Evasive Maneuvers",
                "description": "Avoid engagement, reposition",
                "risk": "low",
                "effectiveness": "medium"
            })

        # Diplomatic options
        if threat_level < 6:
            options.append({
                "type": "diplomatic",
                "name": "Diplomatic Approach",
                "description": "Attempt resolution through communication",
                "risk": "low",
                "effectiveness": "variable"
            })

        return options

    def _determine_recommended_action(
        self,
        tactical_options: List[Dict[str, Any]],
        threat_level: int
    ) -> str:
        """Determine recommended tactical action"""
        if not tactical_options:
            return "Maintain current course"

        # High threat - defensive or offensive
        if threat_level >= 7:
            for option in tactical_options:
                if option["type"] in ["defensive", "offensive"]:
                    return option["name"]

        # Medium threat - defensive or evasive
        elif threat_level >= 4:
            for option in tactical_options:
                if option["type"] in ["defensive", "evasive"]:
                    return option["name"]

        # Low threat - diplomatic or maintain
        else:
            for option in tactical_options:
                if option["type"] == "diplomatic":
                    return option["name"]

        return "Maintain current course"

    def issue_bridge_order(
        self,
        station: BridgeStation,
        order_type: str,
        command: str,
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 5
    ) -> BridgeOrder:
        """
        Issue bridge order (command)

        Naval/maritime command structure:
        - Orders issued from bridge stations
        - Executed by appropriate systems
        - Tracked and monitored
        """
        order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        order = BridgeOrder(
            order_id=order_id,
            station=station.value,
            order_type=order_type,
            command=command,
            parameters=parameters or {},
            priority=priority,
            status="pending",
            timestamp=datetime.now().isoformat()
        )

        self.active_orders[order_id] = order

        # Execute order based on station
        self._execute_bridge_order(order)

        self._save_state()

        logger.info(f"   📢 Bridge Order: {station.value} - {command}")

        return order

    def _execute_bridge_order(self, order: BridgeOrder):
        """Execute bridge order through appropriate system"""
        station = order.station
        command = order.command
        params = order.parameters

        try:
            if station == BridgeStation.CAPTAIN.value:
                # Executive command - route to governance or command control
                if self.governance:
                    # Propose governance decision
                    from jarvis_governance_system import GovernanceBranch, DecisionType, GovernanceScale
                    decision = self.governance.propose_decision(
                        branch=GovernanceBranch.EXECUTIVE,
                        decision_type=DecisionType.STRATEGIC,
                        title=command,
                        description=params.get("description", command),
                        scale=GovernanceScale.GLOBAL,
                        proposer="Bridge_Captain"
                    )
                    order.execution_result = {"decision_id": decision.decision_id}
                    order.status = "executed"

            elif station == BridgeStation.TACTICAL_OFFICER.value:
                # Tactical operations
                if self.command_control:
                    # Create tactical operation
                    operation = self.command_control.create_operation(
                        name=command,
                        scale=params.get("scale", "global"),
                        priority=order.priority
                    )
                    order.execution_result = {"operation_id": operation.operation_id}
                    order.status = "executed"

            elif station == BridgeStation.COMMUNICATIONS_OFFICER.value:
                # Communications
                if self.communications:
                    from lumina_n8n_nas_communication_integration import (
                        CommunicationType, CommunicationDirection, CommunicationChannel
                    )
                    comm_type = CommunicationType[params.get("type", "EMAIL").upper()]
                    direction = CommunicationDirection[params.get("direction", "OUTBOUND").upper()]
                    channel = CommunicationChannel[params.get("channel", "EMAIL").upper()]

                    message = self.communications.route_communication(
                        comm_type=comm_type,
                        direction=direction,
                        channel=channel,
                        source=params.get("source", "bridge"),
                        destination=params.get("destination", ""),
                        content=params.get("content", {})
                    )
                    order.execution_result = {"message_id": message.message_id}
                    order.status = "executed" if message.routed_through_n8n else "failed"

            elif station == BridgeStation.INTELLIGENCE_OFFICER.value:
                # Intelligence operations
                if self.intelligence:
                    if command == "collect_hourly":
                        collection = self.intelligence.collect_hourly_intelligence()
                        order.execution_result = {"collection_id": collection.aggregation_id}
                        order.status = "executed"
                    elif command == "aggregate_daily":
                        aggregation = self.intelligence.aggregate_daily_intelligence()
                        order.execution_result = {"aggregation_id": aggregation.aggregation_id}
                        order.status = "executed"

            else:
                # Other stations - generic execution
                order.execution_result = {"status": "executed", "note": "Order processed"}
                order.status = "executed"

        except Exception as e:
            logger.error(f"Error executing bridge order: {e}")
            order.execution_result = {"error": str(e)}
            order.status = "failed"

        order.executed_by = self.stations.get(station, "Unknown")

    def set_operational_domain(self, domain: OperationalDomain):
        """Set operational domain (terrestrial, maritime, space, etc.)"""
        self.current_domain = domain
        if self.bridge_status:
            self.bridge_status.domain = domain.value
        self._save_state()
        logger.info(f"   🌍 Operational Domain: {domain.value}")

    def get_bridge_status_display(self) -> Dict[str, Any]:
        """Get comprehensive bridge status display"""
        return {
            "bridge_id": self.bridge_status.bridge_id if self.bridge_status else "bridge_primary",
            "domain": self.current_domain.value,
            "tactical_status": self.tactical_status.value,
            "stations": {
                station: {
                    "manned": self.bridge_status.stations_manned.get(station, False) if self.bridge_status else False,
                    "officer": self.stations.get(station, "Unassigned")
                }
                for station in [s.value for s in BridgeStation]
            },
            "active_orders": len(self.active_orders),
            "pending_orders": sum(1 for o in self.active_orders.values() if o.status == "pending"),
            "tactical_situations": len(self.tactical_situations),
            "active_threats": sum(1 for s in self.tactical_situations.values() 
                                if s.status in [TacticalStatus.RED.value, TacticalStatus.BLACK.value]),
            "integrations": {
                "command_control": self.command_control is not None,
                "governance": self.governance is not None,
                "communications": self.communications is not None,
                "intelligence": self.intelligence is not None
            },
            "timestamp": datetime.now().isoformat()
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Bridge Executive Command Deck")
        parser.add_argument("--status", action="store_true", help="Show bridge status")
        parser.add_argument("--assess", type=str, nargs=3, metavar=("DOMAIN", "DESC", "THREATS"), help="Assess tactical situation")
        parser.add_argument("--order", type=str, nargs=4, metavar=("STATION", "TYPE", "COMMAND", "PARAMS"), help="Issue bridge order")
        parser.add_argument("--domain", type=str, help="Set operational domain")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        bridge = BridgeExecutiveCommandDeck()

        if args.status:
            status = bridge.get_bridge_status_display()
            if args.json:
                print(json.dumps(status, indent=2, default=str))
            else:
                print("Bridge Executive Command Deck Status:")
                print(f"  Domain: {status['domain']}")
                print(f"  Tactical Status: {status['tactical_status']}")
                print(f"  Active Orders: {status['active_orders']}")
                print(f"  Active Threats: {status['active_threats']}")

        elif args.assess:
            domain_str, desc, threats_str = args.assess
            domain = OperationalDomain[domain_str.upper()]
            threats = threats_str.split(",") if threats_str else []
            situation = bridge.assess_tactical_situation(domain, desc, threats=threats)
            if args.json:
                print(json.dumps(asdict(situation), indent=2, default=str))
            else:
                print(f"✅ Tactical Situation Assessed: {situation.situation_id}")
                print(f"   Status: {situation.status}")
                print(f"   Threat Level: {situation.threat_level}/10")

        elif args.order:
            station_str, order_type, command, params_str = args.order
            station = BridgeStation[station_str.upper()]
            params = json.loads(params_str) if params_str.startswith("{") else {}
            order = bridge.issue_bridge_order(station, order_type, command, params)
            if args.json:
                print(json.dumps(asdict(order), indent=2, default=str))
            else:
                print(f"✅ Bridge Order Issued: {order.order_id}")

        elif args.domain:
            domain = OperationalDomain[args.domain.upper()]
            bridge.set_operational_domain(domain)
            print(f"✅ Domain set: {domain.value}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()