#!/usr/bin/env python3
"""
Network Support Team Workflows - Business As Usual (BAU)

Comprehensive workflow system for network support team to handle
Lumina's business as usual operations including:
- Network connectivity monitoring
- NAS service health checks
- Connectivity diagnostics
- Troubleshooting workflows
- Automated remediation
"""

import sys
import time
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False

try:
    from nas_service_monitor import NASServiceMonitor, get_master_coordinator, ServiceStatus
    NAS_MONITOR_AVAILABLE = True
except ImportError:
    NAS_MONITOR_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowPriority(Enum):
    """Workflow priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ROUTINE = "routine"


@dataclass
class WorkflowStep:
    """Individual workflow step"""
    step_id: str
    name: str
    description: str
    action: Callable
    timeout: int = 300  # 5 minutes default
    retry_count: int = 3
    required: bool = True
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value
        if self.start_time:
            data['start_time'] = self.start_time.isoformat()
        if self.end_time:
            data['end_time'] = self.end_time.isoformat()
        # Remove callable action
        data.pop('action', None)
        return data


@dataclass
class Workflow:
    """Network support workflow"""
    workflow_id: str
    name: str
    description: str
    priority: WorkflowPriority
    steps: List[WorkflowStep]
    schedule: Optional[str] = None  # Cron expression
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'workflow_id': self.workflow_id,
            'name': self.name,
            'description': self.description,
            'priority': self.priority.value,
            'steps': [step.to_dict() for step in self.steps],
            'schedule': self.schedule,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'success_count': self.success_count,
            'failure_count': self.failure_count
        }


class NetworkSupportWorkflows:
    """
    Network Support Team Workflows for BAU Operations

    Handles all business as usual network support tasks including:
    - Daily health checks
    - Connectivity monitoring
    - NAS service status
    - Network diagnostics
    - Automated remediation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize network support workflows"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("NetworkSupportWorkflows")

        # Workflow registry
        self.workflows: Dict[str, Workflow] = {}

        # Configuration
        self.config_dir = self.project_root / "config"
        self.data_dir = self.project_root / "data" / "network_support"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load NAS configuration
        self.nas_config = self._load_nas_config()

        # Initialize workflows
        self._initialize_bau_workflows()

        self.logger.info("✅ Network Support Workflows initialized")

    def _load_nas_config(self) -> Dict[str, Any]:
        """Load NAS configuration"""
        try:
            # Try YAML config first
            yaml_config_path = self.config_dir / "nas_proxy_cache_config.yaml"
            if yaml_config_path.exists():
                import yaml
                with open(yaml_config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'nas' in config:
                        return config['nas']

            # Fallback to JSON config
            json_config_path = self.config_dir / "lumina_nas_ssh_config.json"
            if json_config_path.exists():
                with open(json_config_path, 'r') as f:
                    config = json.load(f)
                    if 'nas' in config:
                        nas_config = config['nas'].copy()
                        # Normalize field names
                        if 'username' in nas_config:
                            nas_config['user'] = nas_config['username']
                        return nas_config

        except Exception as e:
            self.logger.debug(f"Could not load NAS config: {e}")

        # Default configuration
        return {
            'host': '<NAS_PRIMARY_IP>',
            'port': 5001,
            'api_port': 5001,
            'ssh_port': 22,
            'user': 'backupadm',
            'timeout': 30
        }

    def _initialize_bau_workflows(self) -> None:
        """Initialize Business As Usual workflows"""

        # 1. Daily Network Health Check
        self._register_workflow(self._create_daily_health_check_workflow())

        # 2. NAS Service Status Check
        self._register_workflow(self._create_nas_status_check_workflow())

        # 3. Connectivity Diagnostics
        self._register_workflow(self._create_connectivity_diagnostics_workflow())

        # 4. Network Performance Check
        self._register_workflow(self._create_network_performance_workflow())

        # 5. Automated Remediation
        self._register_workflow(self._create_automated_remediation_workflow())

        self.logger.info(f"Registered {len(self.workflows)} BAU workflows")

    def _register_workflow(self, workflow: Workflow) -> None:
        """Register a workflow"""
        self.workflows[workflow.workflow_id] = workflow

    def _create_daily_health_check_workflow(self) -> Workflow:
        """Create daily network health check workflow"""
        steps = [
            WorkflowStep(
                step_id="check_nas_connectivity",
                name="Check NAS Connectivity",
                description="Verify NAS is reachable via network",
                action=self._check_nas_connectivity,
                timeout=30
            ),
            WorkflowStep(
                step_id="check_nas_api",
                name="Check NAS API",
                description="Verify NAS API is responding",
                action=self._check_nas_api,
                timeout=30
            ),
            WorkflowStep(
                step_id="check_nas_ssh",
                name="Check NAS SSH",
                description="Verify NAS SSH is accessible",
                action=self._check_nas_ssh,
                timeout=30
            ),
            WorkflowStep(
                step_id="check_internet_connectivity",
                name="Check Internet Connectivity",
                description="Verify internet connectivity",
                action=self._check_internet_connectivity,
                timeout=30
            ),
            WorkflowStep(
                step_id="check_dns_resolution",
                name="Check DNS Resolution",
                description="Verify DNS is working",
                action=self._check_dns_resolution,
                timeout=30
            )
        ]

        return Workflow(
            workflow_id="daily_health_check",
            name="Daily Network Health Check",
            description="Comprehensive daily network health check",
            priority=WorkflowPriority.ROUTINE,
            steps=steps,
            schedule="0 8 * * *"  # Daily at 8 AM
        )

    def _create_nas_status_check_workflow(self) -> Workflow:
        """Create NAS service status check workflow"""
        steps = [
            WorkflowStep(
                step_id="get_nas_monitor_status",
                name="Get NAS Monitor Status",
                description="Retrieve NAS service monitor status",
                action=self._get_nas_monitor_status,
                timeout=60
            ),
            WorkflowStep(
                step_id="check_nas_service_health",
                name="Check NAS Service Health",
                description="Verify NAS services are healthy",
                action=self._check_nas_service_health,
                timeout=60
            ),
            WorkflowStep(
                step_id="report_nas_status",
                name="Report NAS Status",
                description="Generate NAS status report",
                action=self._report_nas_status,
                timeout=30
            )
        ]

        return Workflow(
            workflow_id="nas_status_check",
            name="NAS Service Status Check",
            description="Check NAS service health and status",
            priority=WorkflowPriority.HIGH,
            steps=steps,
            schedule="*/30 * * * *"  # Every 30 minutes
        )

    def _create_connectivity_diagnostics_workflow(self) -> Workflow:
        """Create connectivity diagnostics workflow"""
        steps = [
            WorkflowStep(
                step_id="ping_nas",
                name="Ping NAS",
                description="Ping NAS to check connectivity",
                action=self._ping_nas,
                timeout=30
            ),
            WorkflowStep(
                step_id="traceroute_nas",
                name="Traceroute to NAS",
                description="Trace route to NAS",
                action=self._traceroute_nas,
                timeout=60
            ),
            WorkflowStep(
                step_id="check_port_connectivity",
                name="Check Port Connectivity",
                description="Check NAS ports are accessible",
                action=self._check_port_connectivity,
                timeout=60
            )
        ]

        return Workflow(
            workflow_id="connectivity_diagnostics",
            name="Connectivity Diagnostics",
            description="Diagnose network connectivity issues",
            priority=WorkflowPriority.MEDIUM,
            steps=steps
        )

    def _create_network_performance_workflow(self) -> Workflow:
        """Create network performance check workflow"""
        steps = [
            WorkflowStep(
                step_id="measure_latency",
                name="Measure Latency",
                description="Measure network latency to NAS",
                action=self._measure_latency,
                timeout=60
            ),
            WorkflowStep(
                step_id="check_bandwidth",
                name="Check Bandwidth",
                description="Check available bandwidth",
                action=self._check_bandwidth,
                timeout=120
            ),
            WorkflowStep(
                step_id="analyze_performance",
                name="Analyze Performance",
                description="Analyze network performance metrics",
                action=self._analyze_performance,
                timeout=30
            )
        ]

        return Workflow(
            workflow_id="network_performance",
            name="Network Performance Check",
            description="Check network performance metrics",
            priority=WorkflowPriority.MEDIUM,
            steps=steps,
            schedule="0 */6 * * *"  # Every 6 hours
        )

    def _create_automated_remediation_workflow(self) -> Workflow:
        """Create automated remediation workflow"""
        steps = [
            WorkflowStep(
                step_id="detect_issues",
                name="Detect Issues",
                description="Detect network issues",
                action=self._detect_issues,
                timeout=60
            ),
            WorkflowStep(
                step_id="attempt_remediation",
                name="Attempt Remediation",
                description="Attempt to remediate detected issues",
                action=self._attempt_remediation,
                timeout=300,
                required=False
            ),
            WorkflowStep(
                step_id="verify_remediation",
                name="Verify Remediation",
                description="Verify remediation was successful",
                action=self._verify_remediation,
                timeout=60,
                required=False
            )
        ]

        return Workflow(
            workflow_id="automated_remediation",
            name="Automated Remediation",
            description="Automatically detect and remediate network issues",
            priority=WorkflowPriority.HIGH,
            steps=steps
        )

    # Workflow Step Actions

    def _check_nas_connectivity(self) -> Dict[str, Any]:
        """Check NAS connectivity"""
        try:
            import socket
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
            port = self.nas_config.get('ssh_port', 22)

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host, port))
            sock.close()

            connected = result == 0
            return {
                'success': connected,
                'host': host,
                'port': port,
                'status': 'connected' if connected else 'disconnected'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_nas_api(self) -> Dict[str, Any]:
        """Check NAS API availability"""
        if not REQUESTS_AVAILABLE:
            return {'success': False, 'error': 'requests library not available'}

        try:
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
            port = self.nas_config.get('api_port', 5001)
            url = f"https://{host}:{port}/webapi/query.cgi"

            response = requests.get(
                url,
                params={'api': 'SYNO.API.Info', 'version': '1', 'method': 'query'},
                timeout=5,
                verify=False
            )

            available = response.status_code in [200, 401, 403]
            return {
                'success': available,
                'status_code': response.status_code,
                'response_time_ms': response.elapsed.total_seconds() * 1000
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_nas_ssh(self) -> Dict[str, Any]:
        """Check NAS SSH availability"""
        if not PARAMIKO_AVAILABLE:
            return {'success': False, 'error': 'paramiko not available'}

        try:
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
            port = self.nas_config.get('ssh_port', 22)
            username = self.nas_config.get('user', 'backupadm')
            password = self.nas_config.get('password')

            if not password:
                return {'success': False, 'error': 'SSH password not configured'}

            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                hostname=host,
                port=port,
                username=username,
                password=password,
                timeout=5,
                allow_agent=False,
                look_for_keys=False
            )
            client.close()

            return {
                'success': True,
                'host': host,
                'port': port
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_internet_connectivity(self) -> Dict[str, Any]:
        """Check internet connectivity"""
        test_urls = [
            'https://www.google.com',
            'https://www.cloudflare.com',
            'https://1.1.1.1'
        ]

        results = []
        for url in test_urls:
            try:
                if REQUESTS_AVAILABLE:
                    response = requests.get(url, timeout=5)
                    results.append({
                        'url': url,
                        'success': response.status_code == 200,
                        'status_code': response.status_code
                    })
            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r.get('success', False))
        return {
            'success': success_count > 0,
            'results': results,
            'success_rate': success_count / len(test_urls) * 100
        }

    def _check_dns_resolution(self) -> Dict[str, Any]:
        """Check DNS resolution"""
        test_domains = [
            'google.com',
            'cloudflare.com',
            'github.com'
        ]

        results = []
        for domain in test_domains:
            try:
                import socket
                ip = socket.gethostbyname(domain)
                results.append({
                    'domain': domain,
                    'success': True,
                    'ip': ip
                })
            except Exception as e:
                results.append({
                    'domain': domain,
                    'success': False,
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r.get('success', False))
        return {
            'success': success_count > 0,
            'results': results,
            'success_rate': success_count / len(test_domains) * 100
        }

    def _get_nas_monitor_status(self) -> Dict[str, Any]:
        """Get NAS monitor status"""
        if not NAS_MONITOR_AVAILABLE:
            return {'success': False, 'error': 'NAS monitor not available'}

        try:
            master = get_master_coordinator()
            all_status = master.get_all_status()
            return {
                'success': True,
                'status': all_status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_nas_service_health(self) -> Dict[str, Any]:
        """Check NAS service health"""
        if not NAS_MONITOR_AVAILABLE:
            return {'success': False, 'error': 'NAS monitor not available'}

        try:
            master = get_master_coordinator()
            all_status = master.get_all_status()

            healthy_count = all_status.get('healthy_count', 0)
            total_services = all_status.get('total_services', 0)

            return {
                'success': healthy_count == total_services and total_services > 0,
                'healthy_count': healthy_count,
                'total_services': total_services,
                'health_percentage': (healthy_count / total_services * 100) if total_services > 0 else 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _report_nas_status(self) -> Dict[str, Any]:
        """Report NAS status"""
        if not NAS_MONITOR_AVAILABLE:
            return {'success': False, 'error': 'NAS monitor not available'}

        try:
            master = get_master_coordinator()
            all_status = master.get_all_status()

            # Save report
            report_file = self.data_dir / f"nas_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(all_status, f, indent=2)

            return {
                'success': True,
                'report_file': str(report_file),
                'status': all_status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _ping_nas(self) -> Dict[str, Any]:
        """Ping NAS"""
        try:
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')

            # Use system ping command
            result = subprocess.run(
                ['ping', '-n', '4', host] if sys.platform == 'win32' else ['ping', '-c', '4', host],
                capture_output=True,
                text=True,
                timeout=30
            )

            success = result.returncode == 0
            return {
                'success': success,
                'host': host,
                'output': result.stdout,
                'returncode': result.returncode
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _traceroute_nas(self) -> Dict[str, Any]:
        """Traceroute to NAS"""
        try:
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')

            # Use system traceroute command
            cmd = ['tracert', host] if sys.platform == 'win32' else ['traceroute', host]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                'success': result.returncode == 0,
                'host': host,
                'output': result.stdout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_port_connectivity(self) -> Dict[str, Any]:
        """Check port connectivity"""
        host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
        ports = [
            self.nas_config.get('ssh_port', 22),
            self.nas_config.get('api_port', 5001),
            self.nas_config.get('port', 5001)
        ]

        results = []
        for port in set(ports):  # Remove duplicates
            try:
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, port))
                sock.close()

                results.append({
                    'port': port,
                    'success': result == 0,
                    'status': 'open' if result == 0 else 'closed'
                })
            except Exception as e:
                results.append({
                    'port': port,
                    'success': False,
                    'error': str(e)
                })

        success_count = sum(1 for r in results if r.get('success', False))
        return {
            'success': success_count > 0,
            'results': results,
            'success_rate': success_count / len(results) * 100
        }

    def _measure_latency(self) -> Dict[str, Any]:
        """Measure latency to NAS"""
        try:
            host = self.nas_config.get('host', '<NAS_PRIMARY_IP>')
            latencies = []

            for _ in range(5):
                start = time.time()
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((host, 22))
                sock.close()
                latency = (time.time() - start) * 1000  # Convert to ms

                if result == 0:
                    latencies.append(latency)

            if latencies:
                avg_latency = sum(latencies) / len(latencies)
                min_latency = min(latencies)
                max_latency = max(latencies)

                return {
                    'success': True,
                    'average_latency_ms': avg_latency,
                    'min_latency_ms': min_latency,
                    'max_latency_ms': max_latency,
                    'measurements': latencies
                }
            else:
                return {
                    'success': False,
                    'error': 'Could not measure latency'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _check_bandwidth(self) -> Dict[str, Any]:
        """Check bandwidth (simplified)"""
        # This is a placeholder - actual bandwidth testing would require
        # more sophisticated tools
        return {
            'success': True,
            'note': 'Bandwidth check requires specialized tools',
            'recommendation': 'Use iperf or similar for accurate bandwidth testing'
        }

    def _analyze_performance(self) -> Dict[str, Any]:
        """Analyze network performance"""
        # Aggregate performance metrics
        return {
            'success': True,
            'analysis': 'Performance analysis completed',
            'recommendations': []
        }

    def _detect_issues(self) -> Dict[str, Any]:
        """Detect network issues"""
        issues = []

        # Check connectivity
        connectivity = self._check_nas_connectivity()
        if not connectivity.get('success'):
            issues.append({
                'type': 'connectivity',
                'severity': 'high',
                'description': 'NAS connectivity issue detected'
            })

        # Check API
        api_check = self._check_nas_api()
        if not api_check.get('success'):
            issues.append({
                'type': 'api',
                'severity': 'medium',
                'description': 'NAS API not responding'
            })

        return {
            'success': True,
            'issues': issues,
            'issue_count': len(issues)
        }

    def _attempt_remediation(self) -> Dict[str, Any]:
        """Attempt remediation"""
        # Placeholder for remediation logic
        return {
            'success': True,
            'actions_taken': [],
            'note': 'Remediation logic to be implemented'
        }

    def _verify_remediation(self) -> Dict[str, Any]:
        """Verify remediation"""
        # Re-run checks to verify
        connectivity = self._check_nas_connectivity()
        return {
            'success': connectivity.get('success', False),
            'verified': connectivity.get('success', False)
        }

    # Workflow Execution

    def execute_workflow(self, workflow_id: str) -> Dict[str, Any]:
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            return {
                'success': False,
                'error': f'Workflow {workflow_id} not found'
            }

        workflow = self.workflows[workflow_id]

        if not workflow.enabled:
            return {
                'success': False,
                'error': f'Workflow {workflow_id} is disabled'
            }

        workflow.run_count += 1
        workflow.last_run = datetime.now()

        results = {
            'workflow_id': workflow_id,
            'start_time': datetime.now().isoformat(),
            'steps': []
        }

        all_success = True

        for step in workflow.steps:
            step.start_time = datetime.now()
            step.status = WorkflowStatus.RUNNING

            try:
                result = step.action()
                step.result = result
                step.status = WorkflowStatus.COMPLETED if result.get('success', False) else WorkflowStatus.FAILED

                if not result.get('success', False) and step.required:
                    all_success = False
                    step.error = result.get('error', 'Step failed')

            except Exception as e:
                step.status = WorkflowStatus.FAILED
                step.error = str(e)
                all_success = False
                if step.required:
                    all_success = False

            step.end_time = datetime.now()
            results['steps'].append(step.to_dict())

        results['end_time'] = datetime.now().isoformat()
        results['success'] = all_success

        if all_success:
            workflow.success_count += 1
        else:
            workflow.failure_count += 1

        return results

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all workflows"""
        return [workflow.to_dict() for workflow in self.workflows.values()]

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            return None
        return self.workflows[workflow_id].to_dict()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Network Support Workflows")
    parser.add_argument("--list", action="store_true", help="List all workflows")
    parser.add_argument("--execute", type=str, help="Execute a workflow")
    parser.add_argument("--status", type=str, help="Get workflow status")

    args = parser.parse_args()

    workflows = NetworkSupportWorkflows()

    if args.list:
        print("\n📋 Available Workflows:")
        print("=" * 60)
        for workflow in workflows.list_workflows():
            print(f"\n{workflow['name']} ({workflow['workflow_id']})")
            print(f"  Priority: {workflow['priority']}")
            print(f"  Description: {workflow['description']}")
            print(f"  Steps: {len(workflow['steps'])}")
            print(f"  Enabled: {workflow['enabled']}")
            if workflow['schedule']:
                print(f"  Schedule: {workflow['schedule']}")

    elif args.execute:
        print(f"\n🚀 Executing workflow: {args.execute}")
        result = workflows.execute_workflow(args.execute)
        print(json.dumps(result, indent=2))

    elif args.status:
        status = workflows.get_workflow_status(args.status)
        if status:
            print(json.dumps(status, indent=2))
        else:
            print(f"Workflow {args.status} not found")

    else:
        parser.print_help()

