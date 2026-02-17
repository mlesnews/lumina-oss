#!/usr/bin/env python3
"""
JARVIS @PEAK Agent Management System

JARVIS controls/manages all agents/subagents both locally and using appropriate frameworks.
Uses @PEAK tool selection: "Measure twice, cut once, the first time, every time!"

Frameworks:
- Docker: Container management and orchestration
- ElevenLabs: Text-to-Speech for voice agents
- MANUS: RDP/automation for remote operations
- MCP Servers: Model Context Protocol integrations
- Local: Direct Python process management

Tags: #JARVIS #AGENTS #SUBAGENTS #PEAK #DOCKER #ELEVENLABS #MANUS #MCP @JARVIS @TEAM
"""

import sys
import json
import time
import subprocess
import psutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPeakAgentManagement")

# @PEAK Pattern System
try:
    from peak_pattern_system import PeakPatternSystem
    PEAK_PATTERNS_AVAILABLE = True
except ImportError:
    PEAK_PATTERNS_AVAILABLE = False
    PeakPatternSystem = None

# Framework integrations
try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    JARVISElevenLabsTTS = None

try:
    from manus_unified_control import MANUSUnifiedControl
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    MANUSUnifiedControl = None

try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_SUPERAGENT_AVAILABLE = True
except ImportError:
    JARVIS_SUPERAGENT_AVAILABLE = False
    JARVISFullTimeSuperAgent = None


class AgentType(Enum):
    """Agent deployment types"""
    LOCAL = "local"  # Local Python process
    DOCKER = "docker"  # Docker container
    ELEVENLABS = "elevenlabs"  # ElevenLabs TTS service
    MANUS = "manus"  # MANUS RDP/automation
    MCP = "mcp"  # MCP Server
    HYBRID = "hybrid"  # Multiple frameworks


class AgentStatus(Enum):
    """Agent status"""
    INACTIVE = "inactive"
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    STOPPING = "stopping"
    ERROR = "error"


@dataclass
class AgentDefinition:
    """Agent definition with @PEAK tool selection"""
    agent_id: str
    agent_name: str
    agent_type: AgentType
    framework: str  # "docker", "elevenlabs", "manus", "local", "mcp"
    command: Optional[str] = None  # Command to execute
    docker_image: Optional[str] = None  # Docker image (if docker)
    docker_compose_file: Optional[str] = None  # Docker compose file
    mcp_server: Optional[str] = None  # MCP server name (if mcp)
    dependencies: List[str] = field(default_factory=list)  # Other agents this depends on
    resource_requirements: Dict[str, Any] = field(default_factory=dict)  # CPU, memory, etc.
    peak_tool_selection: Dict[str, Any] = field(default_factory=dict)  # @PEAK tool selection rationale
    created: datetime = field(default_factory=datetime.now)
    updated: datetime = field(default_factory=datetime.now)


@dataclass
class AgentInstance:
    """Running agent instance"""
    agent_id: str
    agent_name: str
    agent_type: AgentType
    framework: str
    status: AgentStatus
    process_id: Optional[int] = None  # Process ID (if local)
    container_id: Optional[str] = None  # Container ID (if docker)
    started_at: Optional[datetime] = None
    resource_usage: Dict[str, float] = field(default_factory=dict)  # CPU, memory usage
    last_health_check: Optional[datetime] = None
    error_message: Optional[str] = None


class JARVISPeakAgentManagement:
    """
    JARVIS @PEAK Agent Management System

    Centralized management of all agents/subagents using @PEAK tool selection.
    "Measure twice, cut once, the first time, every time!"
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS @PEAK Agent Management"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_agent_management"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.agents_file = self.data_dir / "agents_registry.json"
        self.instances_file = self.data_dir / "agent_instances.json"

        # @PEAK Pattern System
        self.peak_patterns = None
        if PEAK_PATTERNS_AVAILABLE:
            try:
                self.peak_patterns = PeakPatternSystem(project_root=self.project_root)
                logger.info("✅ @PEAK Pattern System initialized")
            except Exception as e:
                logger.warning(f"⚠️  @PEAK Pattern System not available: {e}")

        # Framework integrations
        self.elevenlabs = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs = JARVISElevenLabsTTS(project_root=self.project_root)
                logger.info("✅ ElevenLabs integration initialized")
            except Exception as e:
                logger.debug(f"ElevenLabs not available: {e}")

        self.manus = None
        if MANUS_AVAILABLE:
            try:
                self.manus = MANUSUnifiedControl(project_root=self.project_root)
                logger.info("✅ MANUS integration initialized")
            except Exception as e:
                logger.debug(f"MANUS not available: {e}")

        self.jarvis_superagent = None
        if JARVIS_SUPERAGENT_AVAILABLE:
            try:
                self.jarvis_superagent = JARVISFullTimeSuperAgent(project_root=self.project_root)
                logger.info("✅ JARVIS Superagent initialized")
            except Exception as e:
                logger.debug(f"JARVIS Superagent not available: {e}")

        # Agent registry and instances
        self.agent_definitions: Dict[str, AgentDefinition] = {}
        self.agent_instances: Dict[str, AgentInstance] = {}

        # Load existing agents
        self._load_agents()
        self._load_instances()

        logger.info("✅ JARVIS @PEAK Agent Management System initialized")
        logger.info(f"   Agents registered: {len(self.agent_definitions)}")
        logger.info(f"   Instances running: {len([i for i in self.agent_instances.values() if i.status == AgentStatus.ACTIVE])}")

    def _load_agents(self):
        """Load agent definitions"""
        if self.agents_file.exists():
            try:
                with open(self.agents_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_id, agent_data in data.items():
                        agent_data['agent_type'] = AgentType(agent_data['agent_type'])
                        agent_data['created'] = datetime.fromisoformat(agent_data['created'])
                        agent_data['updated'] = datetime.fromisoformat(agent_data['updated'])
                        self.agent_definitions[agent_id] = AgentDefinition(**agent_data)
                logger.info(f"✅ Loaded {len(self.agent_definitions)} agent definitions")
            except Exception as e:
                logger.warning(f"⚠️  Could not load agents: {e}")

    def _save_agents(self):
        """Save agent definitions"""
        try:
            data = {}
            for agent_id, agent in self.agent_definitions.items():
                agent_dict = {
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "agent_type": agent.agent_type.value,
                    "framework": agent.framework,
                    "command": agent.command,
                    "docker_image": agent.docker_image,
                    "docker_compose_file": agent.docker_compose_file,
                    "mcp_server": agent.mcp_server,
                    "dependencies": agent.dependencies,
                    "resource_requirements": agent.resource_requirements,
                    "peak_tool_selection": agent.peak_tool_selection,
                    "created": agent.created.isoformat(),
                    "updated": agent.updated.isoformat()
                }
                data[agent_id] = agent_dict

            with open(self.agents_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Could not save agents: {e}")

    def _load_instances(self):
        """Load agent instances"""
        if self.instances_file.exists():
            try:
                with open(self.instances_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for agent_id, instance_data in data.items():
                        instance_data['agent_type'] = AgentType(instance_data['agent_type'])
                        instance_data['status'] = AgentStatus(instance_data['status'])
                        if instance_data.get('started_at'):
                            instance_data['started_at'] = datetime.fromisoformat(instance_data['started_at'])
                        if instance_data.get('last_health_check'):
                            instance_data['last_health_check'] = datetime.fromisoformat(instance_data['last_health_check'])
                        self.agent_instances[agent_id] = AgentInstance(**instance_data)
                logger.info(f"✅ Loaded {len(self.agent_instances)} agent instances")
            except Exception as e:
                logger.warning(f"⚠️  Could not load instances: {e}")

    def _save_instances(self):
        """Save agent instances"""
        try:
            data = {}
            for agent_id, instance in self.agent_instances.items():
                instance_dict = {
                    "agent_id": instance.agent_id,
                    "agent_name": instance.agent_name,
                    "agent_type": instance.agent_type.value,
                    "framework": instance.framework,
                    "status": instance.status.value,
                    "process_id": instance.process_id,
                    "container_id": instance.container_id,
                    "started_at": instance.started_at.isoformat() if instance.started_at else None,
                    "resource_usage": instance.resource_usage,
                    "last_health_check": instance.last_health_check.isoformat() if instance.last_health_check else None,
                    "error_message": instance.error_message
                }
                data[agent_id] = instance_dict

            with open(self.instances_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Could not save instances: {e}")

    def select_peak_tool(self, task: str, requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Select best @PEAK tool for the job

        "Measure twice, cut once, the first time, every time!"

        Args:
            task: Task description
            requirements: Task requirements (CPU, memory, isolation, etc.)

        Returns:
            Tool selection with rationale
        """
        selection = {
            "framework": "local",  # Default
            "rationale": "Default local execution",
            "alternatives_considered": [],
            "measurements": {}
        }

        # Measure requirements (first measurement)
        needs_isolation = requirements.get("isolation", False)
        needs_scaling = requirements.get("scaling", False)
        needs_tts = requirements.get("tts", False)
        needs_rdp = requirements.get("rdp", False)
        needs_mcp = requirements.get("mcp", False)
        cpu_required = requirements.get("cpu", 0.0)
        memory_required = requirements.get("memory", 0.0)

        # Measure system resources (second measurement)
        try:
            cpu_available = 100.0 - psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_available = 100.0 - memory.percent
        except:
            cpu_available = 50.0
            memory_available = 50.0

        selection["measurements"] = {
            "cpu_available": cpu_available,
            "memory_available": memory_available,
            "cpu_required": cpu_required,
            "memory_required": memory_required
        }

        # Check for force_local (upper management requirement)
        force_local = requirements.get("force_local", False)
        if force_local:
            selection["framework"] = "local"
            selection["rationale"] = "Upper management requires direct access - Local is @PEAK tool for authority"
            selection["alternatives_considered"] = ["docker", "mcp"]
            return selection

        # Select best tool (cut once)
        if needs_tts and ELEVENLABS_AVAILABLE:
            selection["framework"] = "elevenlabs"
            selection["rationale"] = "Task requires TTS - ElevenLabs is @PEAK tool for voice synthesis"
            selection["alternatives_considered"] = ["local", "docker"]

        elif needs_rdp and MANUS_AVAILABLE:
            selection["framework"] = "manus"
            selection["rationale"] = "Task requires RDP/automation - MANUS is @PEAK tool for remote operations"
            selection["alternatives_considered"] = ["local", "docker"]

        elif needs_mcp:
            selection["framework"] = "mcp"
            selection["rationale"] = "Task requires MCP server integration - MCP is @PEAK tool for model context"
            selection["alternatives_considered"] = ["local", "docker"]

        elif needs_isolation or needs_scaling:
            # Check if Docker is available
            try:
                result = subprocess.run(["docker", "--version"], capture_output=True, timeout=2)
                if result.returncode == 0:
                    selection["framework"] = "docker"
                    selection["rationale"] = "Task requires isolation/scaling - Docker is @PEAK tool for containerization"
                    selection["alternatives_considered"] = ["local"]
            except:
                selection["framework"] = "local"
                selection["rationale"] = "Docker not available, using local execution"

        elif cpu_required > cpu_available or memory_required > memory_available:
            # Resource constraints - consider Docker for isolation
            try:
                result = subprocess.run(["docker", "--version"], capture_output=True, timeout=2)
                if result.returncode == 0:
                    selection["framework"] = "docker"
                    selection["rationale"] = "Resource constraints detected - Docker provides isolation"
                    selection["alternatives_considered"] = ["local"]
            except:
                selection["framework"] = "local"
                selection["rationale"] = "Docker not available, using local execution (may be resource-constrained)"

        else:
            selection["framework"] = "local"
            selection["rationale"] = "Local execution is @PEAK tool for this task (no special requirements)"
            selection["alternatives_considered"] = ["docker"]

        logger.info(f"📏 @PEAK Tool Selection: {selection['framework']} - {selection['rationale']}")

        return selection

    def register_agent(self, agent_id: str, agent_name: str, task: str, 
                      requirements: Dict[str, Any], **kwargs) -> AgentDefinition:
        """
        Register agent with @PEAK tool selection

        "Measure twice, cut once, the first time, every time!"
        """
        # Measure twice: Select best tool
        tool_selection = self.select_peak_tool(task, requirements)

        # Determine agent type
        framework = tool_selection["framework"]
        if framework == "docker":
            agent_type = AgentType.DOCKER
        elif framework == "elevenlabs":
            agent_type = AgentType.ELEVENLABS
        elif framework == "manus":
            agent_type = AgentType.MANUS
        elif framework == "mcp":
            agent_type = AgentType.MCP
        else:
            agent_type = AgentType.LOCAL

        # Create agent definition
        agent = AgentDefinition(
            agent_id=agent_id,
            agent_name=agent_name,
            agent_type=agent_type,
            framework=framework,
            command=kwargs.get("command"),
            docker_image=kwargs.get("docker_image"),
            docker_compose_file=kwargs.get("docker_compose_file"),
            mcp_server=kwargs.get("mcp_server"),
            dependencies=kwargs.get("dependencies", []),
            resource_requirements=requirements,
            peak_tool_selection=tool_selection,
            updated=datetime.now()
        )

        self.agent_definitions[agent_id] = agent
        self._save_agents()

        logger.info(f"✅ Registered agent: {agent_id} ({agent_name})")
        logger.info(f"   Framework: {framework} - {tool_selection['rationale']}")

        return agent

    def start_agent(self, agent_id: str) -> bool:
        """Start agent using appropriate framework"""
        if agent_id not in self.agent_definitions:
            logger.error(f"❌ Agent not found: {agent_id}")
            return False

        agent_def = self.agent_definitions[agent_id]

        # Check dependencies
        for dep_id in agent_def.dependencies:
            if dep_id not in self.agent_instances or \
               self.agent_instances[dep_id].status != AgentStatus.ACTIVE:
                logger.warning(f"⚠️  Dependency not active: {dep_id}")
                # Try to start dependency
                if dep_id in self.agent_definitions:
                    self.start_agent(dep_id)

        # Start based on framework
        try:
            if agent_def.agent_type == AgentType.DOCKER:
                return self._start_docker_agent(agent_def)
            elif agent_def.agent_type == AgentType.ELEVENLABS:
                return self._start_elevenlabs_agent(agent_def)
            elif agent_def.agent_type == AgentType.MANUS:
                return self._start_manus_agent(agent_def)
            elif agent_def.agent_type == AgentType.MCP:
                return self._start_mcp_agent(agent_def)
            else:
                return self._start_local_agent(agent_def)
        except Exception as e:
            logger.error(f"❌ Error starting agent {agent_id}: {e}")
            instance = AgentInstance(
                agent_id=agent_id,
                agent_name=agent_def.agent_name,
                agent_type=agent_def.agent_type,
                framework=agent_def.framework,
                status=AgentStatus.ERROR,
                error_message=str(e)
            )
            self.agent_instances[agent_id] = instance
            self._save_instances()
            return False

    def _start_local_agent(self, agent_def: AgentDefinition) -> bool:
        """Start local Python agent"""
        if not agent_def.command:
            logger.error(f"❌ No command specified for agent: {agent_def.agent_id}")
            return False

        try:
            process = subprocess.Popen(
                agent_def.command.split(),
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            instance = AgentInstance(
                agent_id=agent_def.agent_id,
                agent_name=agent_def.agent_name,
                agent_type=agent_def.agent_type,
                framework=agent_def.framework,
                status=AgentStatus.ACTIVE,
                process_id=process.pid,
                started_at=datetime.now(),
                last_health_check=datetime.now()
            )

            self.agent_instances[agent_def.agent_id] = instance
            self._save_instances()

            logger.info(f"✅ Started local agent: {agent_def.agent_id} (PID: {process.pid})")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting local agent: {e}")
            return False

    def _start_docker_agent(self, agent_def: AgentDefinition) -> bool:
        """Start Docker agent"""
        try:
            if agent_def.docker_compose_file:
                # Use docker-compose
                result = subprocess.run(
                    ["docker-compose", "-f", agent_def.docker_compose_file, "up", "-d"],
                    cwd=str(self.project_root),
                    capture_output=True,
                    timeout=30
                )
            elif agent_def.docker_image:
                # Use docker run
                result = subprocess.run(
                    ["docker", "run", "-d", agent_def.docker_image],
                    capture_output=True,
                    timeout=30
                )
            else:
                logger.error(f"❌ No Docker image/compose file specified: {agent_def.agent_id}")
                return False

            if result.returncode == 0:
                container_id = result.stdout.decode().strip().split('\n')[-1]

                instance = AgentInstance(
                    agent_id=agent_def.agent_id,
                    agent_name=agent_def.agent_name,
                    agent_type=agent_def.agent_type,
                    framework=agent_def.framework,
                    status=AgentStatus.ACTIVE,
                    container_id=container_id,
                    started_at=datetime.now(),
                    last_health_check=datetime.now()
                )

                self.agent_instances[agent_def.agent_id] = instance
                self._save_instances()

                logger.info(f"✅ Started Docker agent: {agent_def.agent_id} (Container: {container_id[:12]})")
                return True
            else:
                logger.error(f"❌ Docker command failed: {result.stderr.decode()}")
                return False
        except Exception as e:
            logger.error(f"❌ Error starting Docker agent: {e}")
            return False

    def _start_elevenlabs_agent(self, agent_def: AgentDefinition) -> bool:
        """Start ElevenLabs TTS agent"""
        if not self.elevenlabs:
            logger.error(f"❌ ElevenLabs not available: {agent_def.agent_id}")
            return False

        try:
            instance = AgentInstance(
                agent_id=agent_def.agent_id,
                agent_name=agent_def.agent_name,
                agent_type=agent_def.agent_type,
                framework=agent_def.framework,
                status=AgentStatus.ACTIVE,
                started_at=datetime.now(),
                last_health_check=datetime.now()
            )

            self.agent_instances[agent_def.agent_id] = instance
            self._save_instances()

            logger.info(f"✅ Started ElevenLabs agent: {agent_def.agent_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting ElevenLabs agent: {e}")
            return False

    def _start_manus_agent(self, agent_def: AgentDefinition) -> bool:
        """Start MANUS agent"""
        if not self.manus:
            logger.error(f"❌ MANUS not available: {agent_def.agent_id}")
            return False

        try:
            instance = AgentInstance(
                agent_id=agent_def.agent_id,
                agent_name=agent_def.agent_name,
                agent_type=agent_def.agent_type,
                framework=agent_def.framework,
                status=AgentStatus.ACTIVE,
                started_at=datetime.now(),
                last_health_check=datetime.now()
            )

            self.agent_instances[agent_def.agent_id] = instance
            self._save_instances()

            logger.info(f"✅ Started MANUS agent: {agent_def.agent_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting MANUS agent: {e}")
            return False

    def _start_mcp_agent(self, agent_def: AgentDefinition) -> bool:
        """Start MCP server agent"""
        if not agent_def.mcp_server:
            logger.error(f"❌ No MCP server specified: {agent_def.agent_id}")
            return False

        try:
            # MCP servers are managed by Cursor IDE, so we just register them
            instance = AgentInstance(
                agent_id=agent_def.agent_id,
                agent_name=agent_def.agent_name,
                agent_type=agent_def.agent_type,
                framework=agent_def.framework,
                status=AgentStatus.ACTIVE,
                started_at=datetime.now(),
                last_health_check=datetime.now()
            )

            self.agent_instances[agent_def.agent_id] = instance
            self._save_instances()

            logger.info(f"✅ Registered MCP agent: {agent_def.agent_id} ({agent_def.mcp_server})")
            return True
        except Exception as e:
            logger.error(f"❌ Error starting MCP agent: {e}")
            return False

    def stop_agent(self, agent_id: str) -> bool:
        """Stop agent"""
        if agent_id not in self.agent_instances:
            logger.warning(f"⚠️  Agent instance not found: {agent_id}")
            return False

        instance = self.agent_instances[agent_id]
        instance.status = AgentStatus.STOPPING

        try:
            if instance.agent_type == AgentType.DOCKER and instance.container_id:
                subprocess.run(["docker", "stop", instance.container_id], timeout=10)
            elif instance.process_id:
                try:
                    process = psutil.Process(instance.process_id)
                    process.terminate()
                    process.wait(timeout=5)
                except psutil.NoSuchProcess:
                    pass

            instance.status = AgentStatus.INACTIVE
            self._save_instances()

            logger.info(f"✅ Stopped agent: {agent_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error stopping agent {agent_id}: {e}")
            instance.status = AgentStatus.ERROR
            instance.error_message = str(e)
            self._save_instances()
            return False

    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all agents"""
        return {
            "timestamp": datetime.now().isoformat(),
            "agents_registered": len(self.agent_definitions),
            "agents_active": len([i for i in self.agent_instances.values() if i.status == AgentStatus.ACTIVE]),
            "agents": {
                agent_id: {
                    "name": agent.agent_name,
                    "type": agent.agent_type.value,
                    "framework": agent.framework,
                    "status": self.agent_instances.get(agent_id, AgentInstance(
                        agent_id=agent_id,
                        agent_name=agent.agent_name,
                        agent_type=agent.agent_type,
                        framework=agent.framework,
                        status=AgentStatus.INACTIVE
                    )).status.value,
                    "peak_tool_selection": agent.peak_tool_selection
                }
                for agent_id, agent in self.agent_definitions.items()
            }
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @PEAK Agent Management")
    parser.add_argument("--status", action="store_true", help="Show agent status")
    parser.add_argument("--register", type=str, help="Register new agent (JSON config)")
    parser.add_argument("--start", type=str, help="Start agent by ID")
    parser.add_argument("--stop", type=str, help="Stop agent by ID")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤖 JARVIS @PEAK Agent Management System")
    print("   'Measure twice, cut once, the first time, every time!'")
    print("="*80 + "\n")

    manager = JARVISPeakAgentManagement()

    if args.status:
        status = manager.get_agent_status()
        print(json.dumps(status, indent=2, default=str))

    elif args.register:
        # Register agent from JSON
        try:
            config = json.loads(args.register)
            agent = manager.register_agent(**config)
            print(f"\n✅ Registered agent: {agent.agent_id}")
            print(f"   Framework: {agent.framework}")
            print(f"   Rationale: {agent.peak_tool_selection['rationale']}")
        except Exception as e:
            print(f"\n❌ Error registering agent: {e}")

    elif args.start:
        success = manager.start_agent(args.start)
        print(f"\n{'✅' if success else '❌'} Agent {args.start} {'started' if success else 'failed to start'}")

    elif args.stop:
        success = manager.stop_agent(args.stop)
        print(f"\n{'✅' if success else '❌'} Agent {args.stop} {'stopped' if success else 'failed to stop'}")

    else:
        # Default: show status
        status = manager.get_agent_status()
        print("📊 AGENT STATUS")
        print("="*80)
        print(f"Agents Registered: {status['agents_registered']}")
        print(f"Agents Active: {status['agents_active']}")
        print()

        if status['agents']:
            print("🤖 AGENTS")
            print("="*80)
            for agent_id, agent_info in status['agents'].items():
                status_icon = "✅" if agent_info['status'] == 'active' else "❌"
                print(f"{status_icon} {agent_id} ({agent_info['name']})")
                print(f"   Framework: {agent_info['framework']} | Status: {agent_info['status']}")
                if agent_info.get('peak_tool_selection'):
                    print(f"   @PEAK: {agent_info['peak_tool_selection'].get('rationale', 'N/A')}")
                print()

        print("💡 Use --help for commands")
        print("="*80 + "\n")
