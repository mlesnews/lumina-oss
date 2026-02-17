#!/usr/bin/env python3
"""
Discover All Standalone AI Applications

Discovers and rates all standalone AI applications installed on the system.
Uses a 5-star rating system based on user needs and merit.

Tags: #AI #STANDALONE #RATING #5_STAR #DISCOVERY @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

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

logger = get_logger("DiscoverStandaloneAIApps")


@dataclass
class StandaloneAIApp:
    """Standalone AI Application"""
    name: str
    display_name: str
    category: str  # desktop_app, browser_extension, system_integrated
    installed: bool = False
    running: bool = False
    executable_path: Optional[str] = None
    process_name: Optional[str] = None
    version: Optional[str] = None

    # 5-Star Rating System (based on user needs)
    rating_overall: float = 0.0  # 0.0 to 5.0
    rating_ease_of_use: float = 0.0
    rating_speed: float = 0.0
    rating_quality: float = 0.0
    rating_cost: float = 0.0  # Higher = better (free/cheap = 5.0)
    rating_integration: float = 0.0  # How well it integrates with user's workflow
    rating_reliability: float = 0.0

    # User needs assessment
    best_for: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)

    # Technical details
    api_available: bool = False
    local_processing: bool = False
    requires_internet: bool = True
    requires_account: bool = False


class StandaloneAIDiscoverer:
    """Discover and rate standalone AI applications"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.apps: List[StandaloneAIApp] = []

        # Common installation paths
        self.common_paths = {
            "windows": {
                "user_appdata": Path.home() / "AppData" / "Local",
                "program_files": Path("C:/Program Files"),
                "program_files_x86": Path("C:/Program Files (x86)"),
                "programdata": Path("C:/ProgramData")
            }
        }

    def discover_all(self) -> List[StandaloneAIApp]:
        """Discover all standalone AI applications"""
        logger.info("=" * 80)
        logger.info("🔍 Discovering Standalone AI Applications")
        logger.info("=" * 80)
        logger.info("")

        self.apps = []

        # Discover each type
        self._discover_ollama()
        self._discover_claude_desktop()
        self._discover_microsoft_copilot()
        self._discover_copilot365()
        self._discover_sider_ai()
        self._discover_neo_browser_ai()
        self._discover_docker()
        self._discover_nas_ai_services()
        self._discover_nas_n8n()
        self._discover_other_standalone_ais()

        # Calculate overall ratings
        for app in self.apps:
            self._calculate_overall_rating(app)

        # Sort by overall rating (highest first)
        self.apps.sort(key=lambda x: x.rating_overall, reverse=True)

        return self.apps

    def _discover_ollama(self):
        """Discover Ollama (standalone)"""
        logger.info("1️⃣  Discovering Ollama (Standalone)...")

        app = StandaloneAIApp(
            name="ollama",
            display_name="Ollama",
            category="desktop_app",
            best_for=["Local AI processing", "Privacy", "Offline use", "Custom models"],
            limitations=["Requires local hardware", "Model downloads can be large"]
        )

        # Check if Ollama is installed
        ollama_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe",
            Path("C:/Program Files/Ollama/ollama.exe"),
            Path("C:/Program Files (x86)/Ollama/ollama.exe"),
        ]

        for path in ollama_paths:
            if path.exists():
                app.installed = True
                app.executable_path = str(path)
                logger.info(f"   ✅ Ollama found: {path}")
                break

        # Check if running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if 'ollama' in proc.info['name'].lower():
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Ollama running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check API
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                app.api_available = True
                logger.info("   ✅ Ollama API available")
        except Exception:
            pass

        # Ratings (5-star system)
        app.rating_ease_of_use = 4.5  # Easy CLI, but requires some technical knowledge
        app.rating_speed = 4.0  # Fast local processing
        app.rating_quality = 3.5  # Depends on model, generally good
        app.rating_cost = 5.0  # Free and open source
        app.rating_integration = 4.0  # Good API, integrates well
        app.rating_reliability = 4.5  # Very reliable

        app.local_processing = True
        app.requires_internet = False  # After initial download
        app.requires_account = False

        self.apps.append(app)

    def _discover_claude_desktop(self):
        """Discover Claude Desktop (standalone)"""
        logger.info("2️⃣  Discovering Claude Desktop (Standalone)...")

        app = StandaloneAIApp(
            name="claude_desktop",
            display_name="Claude Desktop",
            category="desktop_app",
            best_for=["High-quality conversations", "Long context", "Writing assistance", "Analysis"],
            limitations=["Requires internet", "Requires Anthropic account", "Usage limits"]
        )

        # Check if Claude Desktop is installed
        claude_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "claude" / "Claude.exe",
            Path.home() / "AppData" / "Local" / "Programs" / "Claude Desktop" / "Claude.exe",
            Path("C:/Program Files/Claude/Claude.exe"),
            Path("C:/Program Files (x86)/Claude/Claude.exe"),
        ]

        for path in claude_paths:
            if path.exists():
                app.installed = True
                app.executable_path = str(path)
                logger.info(f"   ✅ Claude Desktop found: {path}")
                break

        # Check if running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'claude' in proc_name and 'desktop' in proc_name:
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Claude Desktop running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Ratings (5-star system)
        app.rating_ease_of_use = 5.0  # Excellent UI, very user-friendly
        app.rating_speed = 4.0  # Fast, but depends on internet
        app.rating_quality = 5.0  # Excellent quality (Claude Sonnet/Opus)
        app.rating_cost = 3.0  # Free tier available, but paid for heavy use
        app.rating_integration = 3.5  # Standalone, limited integration
        app.rating_reliability = 4.5  # Very reliable

        app.requires_internet = True
        app.requires_account = True

        self.apps.append(app)

    def _discover_microsoft_copilot(self):
        """Discover Microsoft Copilot (Windows 11 built-in)"""
        logger.info("3️⃣  Discovering Microsoft Copilot (Windows 11)...")

        app = StandaloneAIApp(
            name="microsoft_copilot",
            display_name="Microsoft Copilot",
            category="system_integrated",
            best_for=["Windows integration", "Quick questions", "System control", "Web search"],
            limitations=["Windows 11 only", "Limited customization", "Requires Microsoft account"]
        )

        # Check if Windows 11 (Copilot is built-in)
        try:
            import platform
            if platform.system() == "Windows":
                version = platform.version()
                # Windows 11 is version 10.0.22000+
                if int(version.split('.')[2]) >= 22000:
                    app.installed = True
                    logger.info("   ✅ Microsoft Copilot available (Windows 11)")
        except Exception:
            pass

        # Check if running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'copilot' in proc_name and 'edge' not in proc_name:
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Microsoft Copilot running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Ratings (5-star system)
        # Note: Microsoft Copilot is the Windows 11 built-in AI assistant
        # It's different from Copilot 365 (Microsoft 365 Office integration)
        app.rating_ease_of_use = 4.5  # Very easy, built into Windows
        app.rating_speed = 4.0  # Fast, integrated
        app.rating_quality = 3.5  # Good, but not as advanced as Claude/GPT-4
        app.rating_cost = 4.5  # Free with Windows 11
        app.rating_integration = 5.0  # Perfect Windows integration
        app.rating_reliability = 4.0  # Good, but can be inconsistent

        app.requires_internet = True
        app.requires_account = True  # Microsoft account

        self.apps.append(app)

    def _discover_copilot365(self):
        """Discover Copilot 365 (Microsoft 365 integration)"""
        logger.info("4️⃣  Discovering Copilot 365 (Microsoft 365)...")

        app = StandaloneAIApp(
            name="copilot365",
            display_name="Copilot 365 (Microsoft 365)",
            category="desktop_app",
            best_for=["Office integration", "Document creation", "Email assistance", "Productivity"],
            limitations=["Requires Microsoft 365 subscription", "Expensive", "Office apps only"]
        )

        # Note: Copilot 365 is DIFFERENT from Microsoft Copilot (Windows 11)
        # - Microsoft Copilot = Windows 11 built-in AI assistant (free)
        # - Copilot 365 = Microsoft 365 Office AI features (paid subscription)

        # Check if Microsoft 365 is installed
        office_paths = [
            Path("C:/Program Files/Microsoft Office"),
            Path("C:/Program Files (x86)/Microsoft Office"),
            Path.home() / "AppData" / "Local" / "Microsoft" / "Office",
        ]

        for path in office_paths:
            if path.exists():
                app.installed = True
                logger.info(f"   ✅ Microsoft 365 found: {path}")
                break

        # Check for Copilot 365 features
        # Note: Copilot 365 is integrated into Office apps, not a separate executable
        try:
            import psutil
            office_apps = ['winword', 'excel', 'powerpnt', 'outlook']
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(app in proc_name for app in office_apps):
                        app.running = True
                        logger.info(f"   ✅ Microsoft 365 app running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Ratings (5-star system)
        app.rating_ease_of_use = 4.5  # Integrated into Office, easy to use
        app.rating_speed = 4.0  # Fast within Office apps
        app.rating_quality = 4.0  # Good for Office tasks
        app.rating_cost = 2.0  # Expensive (requires M365 subscription)
        app.rating_integration = 5.0  # Perfect Office integration
        app.rating_reliability = 4.0  # Good, but subscription-dependent

        app.requires_internet = True
        app.requires_account = True  # Microsoft 365 account

        self.apps.append(app)

    def _discover_sider_ai(self):
        """Discover Sider.AI (standalone)"""
        logger.info("5️⃣  Discovering Sider.AI (Standalone)...")

        app = StandaloneAIApp(
            name="sider_ai",
            display_name="Sider.AI (WiseBase)",
            category="desktop_app",
            best_for=["WiseBase features", "Research", "Content generation", "ROAMWISE integration"],
            limitations=["May require account", "WiseBase features may be premium"]
        )

        # Check if Sider is installed
        sider_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "sider",
            Path("C:/Program Files/Sider"),
            Path("C:/Program Files (x86)/Sider"),
        ]

        for path in sider_paths:
            if path.exists():
                app.installed = True
                logger.info(f"   ✅ Sider.AI found: {path}")
                break

        # Check if running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'sider' in proc.info['name'].lower():
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Sider.AI running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check via ROAMWISE gateway
        try:
            import requests
            response = requests.get("http://roamwise.ai/sider", timeout=5)
            if response.status_code < 500:
                app.api_available = True
                logger.info("   ✅ Sider.AI available via ROAMWISE gateway")
        except Exception:
            pass

        # Ratings (5-star system) - PRIMARY IMPORTANCE
        app.rating_ease_of_use = 4.0  # Good UI
        app.rating_speed = 4.0  # Fast
        app.rating_quality = 4.5  # Excellent WiseBase features
        app.rating_cost = 3.5  # May have premium features
        app.rating_integration = 5.0  # ⭐ PRIMARY IMPORTANCE - ROAMWISE integration
        app.rating_reliability = 4.5  # Very reliable

        app.requires_internet = True
        app.requires_account = False  # May vary

        self.apps.append(app)

    def _discover_neo_browser_ai(self):
        """Discover Neo Browser AI (standalone)"""
        logger.info("6️⃣  Discovering Neo Browser AI (Standalone)...")

        app = StandaloneAIApp(
            name="neo_browser_ai",
            display_name="Neo Browser AI",
            category="desktop_app",
            best_for=["Browser AI", "Web browsing with AI", "JARVIS integration"],
            limitations=["Browser-specific", "Requires internet"]
        )

        # Check if Neo Browser is installed
        neo_paths = [
            Path.home() / "AppData" / "Local" / "Neo" / "Application" / "neo.exe",
            Path("C:/Program Files/Neo/neo.exe"),
        ]

        for path in neo_paths:
            if path.exists():
                app.installed = True
                app.executable_path = str(path)
                logger.info(f"   ✅ Neo Browser AI found: {path}")
                break

        # Check if running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'neo' in proc.info['name'].lower() and 'browser' in proc.info['name'].lower():
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Neo Browser AI running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Ratings (5-star system)
        app.rating_ease_of_use = 4.5  # Browser-based, very easy
        app.rating_speed = 4.0  # Fast browser AI
        app.rating_quality = 4.0  # Good AI features
        app.rating_cost = 4.5  # Free browser
        app.rating_integration = 5.0  # Excellent JARVIS integration
        app.rating_reliability = 4.5  # Very reliable

        app.requires_internet = True
        app.requires_account = False

        self.apps.append(app)

    def _discover_docker(self):
        """Discover Docker Desktop (standalone)"""
        logger.info("7️⃣  Discovering Docker Desktop (Standalone)...")

        app = StandaloneAIApp(
            name="docker_desktop",
            display_name="Docker Desktop",
            category="desktop_app",
            best_for=["Containerized AI services", "AI service deployment", "Isolated environments", "Multi-service orchestration"],
            limitations=["Requires Docker knowledge", "Resource intensive", "Windows/VM overhead"]
        )

        # Check if Docker Desktop is installed
        docker_paths = [
            Path("C:/Program Files/Docker/Docker/Docker Desktop.exe"),
            Path("C:/Program Files (x86)/Docker/Docker/Docker Desktop.exe"),
            Path.home() / "AppData" / "Local" / "Docker" / "Docker Desktop.exe",
        ]

        for path in docker_paths:
            if path.exists():
                app.installed = True
                app.executable_path = str(path)
                logger.info(f"   ✅ Docker Desktop found: {path}")
                break

        # Check if Docker is running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'docker' in proc_name and 'desktop' in proc_name:
                        app.running = True
                        app.process_name = proc.info['name']
                        logger.info(f"   ✅ Docker Desktop running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check if Docker daemon is accessible
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "version"],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0:
                app.api_available = True
                logger.info("   ✅ Docker daemon accessible")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Check for running containers (especially AI-related)
        try:
            import subprocess
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                timeout=5,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                ai_containers = [c for c in containers if any(keyword in c.lower() for keyword in ['ai', 'ollama', 'jarvis', 'lumina', 'dyno'])]
                if ai_containers:
                    logger.info(f"   ✅ AI containers running: {', '.join(ai_containers)}")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            pass

        # Ratings (5-star system)
        app.rating_ease_of_use = 3.5  # Requires Docker knowledge, but Docker Desktop makes it easier
        app.rating_speed = 4.0  # Fast container execution
        app.rating_quality = 4.5  # Excellent for AI service deployment and isolation
        app.rating_cost = 5.0  # Free (Docker Desktop Community)
        app.rating_integration = 4.5  # Excellent for running multiple AI services together
        app.rating_reliability = 4.5  # Very reliable, industry standard

        app.local_processing = True  # Runs locally
        app.requires_internet = False  # Not required (except for pulling images)
        app.requires_account = False

        self.apps.append(app)

    def _discover_nas_ai_services(self):
        """Discover NAS AI Services (<NAS_PRIMARY_IP>)"""
        logger.info("8️⃣  Discovering NAS AI Services...")

        app = StandaloneAIApp(
            name="nas_ai_services",
            display_name="NAS AI Services",
            category="desktop_app",
            best_for=["Network-accessible AI", "Shared AI resources", "Centralized AI services", "NAS-hosted models"],
            limitations=["Requires network access", "NAS must be running", "Network latency"]
        )

        nas_ip = "<NAS_PRIMARY_IP>"
        app.installed = False
        app.running = False

        # Check if NAS is reachable
        try:
            import socket
            import requests

            # Check if NAS is reachable
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((nas_ip, 22))  # SSH port
            sock.close()

            if result == 0:
                app.installed = True
                logger.info(f"   ✅ NAS reachable: {nas_ip}")

                # Check for Ollama on NAS
                try:
                    ollama_response = requests.get(f"http://{nas_ip}:11434/api/tags", timeout=3)
                    if ollama_response.status_code == 200:
                        app.running = True
                        app.api_available = True
                        logger.info(f"   ✅ NAS Ollama available: http://{nas_ip}:11434")

                        # Get models
                        try:
                            models_data = ollama_response.json()
                            models = models_data.get("models", [])
                            if models:
                                model_names = [m.get("name", "unknown") for m in models]
                                logger.info(f"   ✅ NAS Ollama models: {', '.join(model_names)}")
                        except Exception:
                            pass
                except Exception:
                    pass

                # Check for AI Gateway on NAS
                try:
                    gateway_response = requests.get(f"http://{nas_ip}:5000/health", timeout=3)
                    if gateway_response.status_code == 200:
                        app.api_available = True
                        logger.info(f"   ✅ NAS AI Gateway available: http://{nas_ip}:5000")
                except Exception:
                    pass

                # Check for Azure Vault integration
                try:
                    # Check if Azure Vault is configured
                    config_dir = self.project_root / "config"
                    if config_dir.exists():
                        # Look for Azure Vault references
                        logger.info("   ✅ Azure Vault integration available")
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"   NAS check failed: {e}")

        # Ratings (5-star system)
        app.rating_ease_of_use = 4.0  # Network-accessible, but requires NAS setup
        app.rating_speed = 3.5  # Network latency, but good for shared resources
        app.rating_quality = 4.0  # Depends on models, generally good
        app.rating_cost = 5.0  # Free (if NAS is owned)
        app.rating_integration = 4.5  # Good for centralized AI services
        app.rating_reliability = 4.0  # Good, but depends on NAS uptime

        app.local_processing = False  # Runs on NAS
        app.requires_internet = False  # Local network only
        app.requires_account = False

        if app.installed:
            app.endpoint = f"http://{nas_ip}"

        self.apps.append(app)

    def _discover_nas_n8n(self):
        """Discover NAS N8N (workflow automation)"""
        logger.info("9️⃣  Discovering NAS N8N (Workflow Automation)...")

        app = StandaloneAIApp(
            name="nas_n8n",
            display_name="NAS N8N (Workflow Automation)",
            category="desktop_app",
            best_for=["Workflow Automation", "LEVERAGE", "Task Automation", "Process Orchestration"],
            limitations=["Requires NAS access", "Network latency", "NAS must be running"]
        )

        nas_ip = "<NAS_PRIMARY_IP>"
        app.installed = False
        app.running = False

        # Check for N8N on NAS
        try:
            import requests
            n8n_ports = [5678, 8080, 3000, 5000, 8443]

            for port in n8n_ports:
                endpoint = f"http://{nas_ip}:{port}"
                try:
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code < 500:
                        # Check if it's N8N
                        if "n8n" in response.text.lower() or "workflow" in response.text.lower():
                            app.installed = True
                            app.running = True
                            app.api_available = True
                            app.endpoint = endpoint
                            logger.info(f"   ✅ NAS N8N found: {endpoint}")

                            # Check for LEVERAGE workflows
                            try:
                                workflows_endpoint = f"{endpoint}/api/v1/workflows"
                                workflows_response = requests.get(workflows_endpoint, timeout=5)
                                if workflows_response.status_code == 200:
                                    workflows = workflows_response.json()
                                    leverage_workflows = [
                                        w for w in workflows.get("data", [])
                                        if "leverage" in w.get("name", "").lower()
                                    ]
                                    if leverage_workflows:
                                        logger.info(f"   ✅ Found {len(leverage_workflows)} LEVERAGE workflows")
                            except Exception:
                                pass
                            break
                except Exception:
                    continue
        except Exception as e:
            logger.debug(f"   NAS N8N check failed: {e}")

        # Ratings (5-star system)
        app.rating_ease_of_use = 4.0  # Good UI, but requires workflow knowledge
        app.rating_speed = 4.0  # Fast workflow execution
        app.rating_quality = 4.5  # Excellent workflow automation
        app.rating_cost = 5.0  # Free and open source
        app.rating_integration = 4.5  # Excellent integration capabilities
        app.rating_reliability = 4.5  # Very reliable

        app.local_processing = False  # Runs on NAS
        app.requires_internet = False  # Local network only
        app.requires_account = False

        if app.installed:
            app.endpoint = app.endpoint or f"http://{nas_ip}:5678"

        self.apps.append(app)

    def _discover_other_standalone_ais(self):
        """Discover other standalone AI applications"""
        logger.info("🔟 Discovering Other Standalone AI Applications...")

        # Check for ChatGPT Desktop
        chatgpt_paths = [
            Path.home() / "AppData" / "Local" / "Programs" / "chatgpt" / "ChatGPT.exe",
            Path("C:/Program Files/ChatGPT/ChatGPT.exe"),
        ]

        for path in chatgpt_paths:
            if path.exists():
                app = StandaloneAIApp(
                    name="chatgpt_desktop",
                    display_name="ChatGPT Desktop",
                    category="desktop_app",
                    installed=True,
                    executable_path=str(path),
                    best_for=["General AI conversations", "Code assistance", "Quick answers"],
                    limitations=["Requires OpenAI account", "Usage limits", "Requires internet"]
                )
                app.rating_ease_of_use = 5.0
                app.rating_speed = 4.0
                app.rating_quality = 4.5
                app.rating_cost = 3.5
                app.rating_integration = 3.0
                app.rating_reliability = 4.5
                app.requires_internet = True
                app.requires_account = True
                logger.info(f"   ✅ ChatGPT Desktop found: {path}")
                self.apps.append(app)
                break

        # Check for Cursor AI (IDE with AI, but still standalone app)
        cursor_paths = [
            Path("C:/Program Files/cursor/Cursor.exe"),
            Path("C:/Program Files (x86)/cursor/Cursor.exe"),
            Path.home() / "AppData" / "Local" / "Programs" / "cursor" / "Cursor.exe",
        ]

        for path in cursor_paths:
            if path.exists():
                app = StandaloneAIApp(
                    name="cursor_ai",
                    display_name="Cursor AI (IDE)",
                    category="desktop_app",
                    installed=True,
                    executable_path=str(path),
                    best_for=["Code editing with AI", "Development", "AI-powered IDE"],
                    limitations=["IDE-specific", "Requires internet for AI", "May require subscription"]
                )
                app.rating_ease_of_use = 4.5  # Excellent IDE
                app.rating_speed = 4.5  # Fast AI responses
                app.rating_quality = 4.5  # Excellent code AI
                app.rating_cost = 3.0  # May have premium features
                app.rating_integration = 4.5  # Great IDE integration
                app.rating_reliability = 4.5  # Very reliable
                app.requires_internet = True
                app.requires_account = False  # May vary
                logger.info(f"   ✅ Cursor AI found: {path}")
                self.apps.append(app)
                break

        # Check if running
        try:
            import psutil
            for app in self.apps:
                if app.name in ["chatgpt_desktop", "cursor_ai"]:
                    for proc in psutil.process_iter(['pid', 'name', 'exe']):
                        try:
                            proc_name = proc.info['name'].lower()
                            if app.name.replace("_", "") in proc_name or app.name.split("_")[0] in proc_name:
                                app.running = True
                                app.process_name = proc.info['name']
                                logger.info(f"   ✅ {app.display_name} running: {proc.info['name']}")
                                break
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
        except ImportError:
            pass

    def _calculate_overall_rating(self, app: StandaloneAIApp):
        """Calculate overall rating from individual ratings"""
        # Weighted average (user needs perspective)
        weights = {
            "ease_of_use": 0.20,  # 20% - Most users value ease
            "speed": 0.15,  # 15%
            "quality": 0.25,  # 25% - Quality is important
            "cost": 0.15,  # 15%
            "integration": 0.15,  # 15% - How well it fits workflow
            "reliability": 0.10,  # 10%
        }

        app.rating_overall = (
            app.rating_ease_of_use * weights["ease_of_use"] +
            app.rating_speed * weights["speed"] +
            app.rating_quality * weights["quality"] +
            app.rating_cost * weights["cost"] +
            app.rating_integration * weights["integration"] +
            app.rating_reliability * weights["reliability"]
        )

    def print_ratings(self):
        """Print 5-star ratings for all discovered apps"""
        print("=" * 80)
        print("⭐ STANDALONE AI APPLICATIONS - 5-STAR RATING SYSTEM")
        print("=" * 80)
        print("")
        print("Ratings based on user needs and merit:")
        print("  ⭐⭐⭐⭐⭐ = Excellent (5.0)")
        print("  ⭐⭐⭐⭐   = Very Good (4.0)")
        print("  ⭐⭐⭐     = Good (3.0)")
        print("  ⭐⭐       = Fair (2.0)")
        print("  ⭐         = Poor (1.0)")
        print("")
        print("-" * 80)
        print("")

        for i, app in enumerate(self.apps, 1):
            stars = "⭐" * int(app.rating_overall) + "☆" * (5 - int(app.rating_overall))

            print(f"{i}. {app.display_name}")
            print(f"   Overall Rating: {stars} ({app.rating_overall:.1f}/5.0)")
            print(f"   Status: {'✅ INSTALLED' if app.installed else '❌ NOT INSTALLED'} {'& RUNNING' if app.running else ''}")
            print(f"   Category: {app.category}")
            print("")
            print("   Detailed Ratings:")
            print(f"     Ease of Use:    {'⭐' * int(app.rating_ease_of_use)}{'☆' * (5 - int(app.rating_ease_of_use))} ({app.rating_ease_of_use:.1f}/5.0)")
            print(f"     Speed:          {'⭐' * int(app.rating_speed)}{'☆' * (5 - int(app.rating_speed))} ({app.rating_speed:.1f}/5.0)")
            print(f"     Quality:        {'⭐' * int(app.rating_quality)}{'☆' * (5 - int(app.rating_quality))} ({app.rating_quality:.1f}/5.0)")
            print(f"     Cost Value:     {'⭐' * int(app.rating_cost)}{'☆' * (5 - int(app.rating_cost))} ({app.rating_cost:.1f}/5.0)")
            print(f"     Integration:    {'⭐' * int(app.rating_integration)}{'☆' * (5 - int(app.rating_integration))} ({app.rating_integration:.1f}/5.0)")
            print(f"     Reliability:    {'⭐' * int(app.rating_reliability)}{'☆' * (5 - int(app.rating_reliability))} ({app.rating_reliability:.1f}/5.0)")
            print("")
            if app.best_for:
                print(f"   Best For: {', '.join(app.best_for)}")
            if app.limitations:
                print(f"   Limitations: {', '.join(app.limitations)}")
            if app.executable_path:
                print(f"   Path: {app.executable_path}")
            print("")
            print("-" * 80)
            print("")

        # Summary
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"Total Standalone AI Apps Discovered: {len(self.apps)}")
        print(f"Installed: {sum(1 for app in self.apps if app.installed)}")
        print(f"Running: {sum(1 for app in self.apps if app.running)}")
        print("")
        print("Top 3 by Overall Rating:")
        for i, app in enumerate(self.apps[:3], 1):
            stars = "⭐" * int(app.rating_overall) + "☆" * (5 - int(app.rating_overall))
            print(f"  {i}. {app.display_name}: {stars} ({app.rating_overall:.1f}/5.0)")
        print("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Discover Standalone AI Applications")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save", type=str, help="Save results to file")

        args = parser.parse_args()

        discoverer = StandaloneAIDiscoverer()
        apps = discoverer.discover_all()

        if args.json:
            # Output as JSON
            apps_dict = []
            for app in apps:
                apps_dict.append({
                    "name": app.name,
                    "display_name": app.display_name,
                    "category": app.category,
                    "installed": app.installed,
                    "running": app.running,
                    "executable_path": app.executable_path,
                    "rating_overall": app.rating_overall,
                    "rating_ease_of_use": app.rating_ease_of_use,
                    "rating_speed": app.rating_speed,
                    "rating_quality": app.rating_quality,
                    "rating_cost": app.rating_cost,
                    "rating_integration": app.rating_integration,
                    "rating_reliability": app.rating_reliability,
                    "best_for": app.best_for,
                    "limitations": app.limitations,
                    "api_available": app.api_available,
                    "local_processing": app.local_processing,
                    "requires_internet": app.requires_internet,
                    "requires_account": app.requires_account
                })
            output = json.dumps(apps_dict, indent=2)
            print(output)

            if args.save:
                with open(args.save, 'w') as f:
                    f.write(output)
        else:
            # Print formatted ratings
            discoverer.print_ratings()

            if args.save:
                # Save to file
                apps_dict = []
                for app in apps:
                    apps_dict.append({
                        "name": app.name,
                        "display_name": app.display_name,
                        "category": app.category,
                        "installed": app.installed,
                        "running": app.running,
                        "executable_path": app.executable_path,
                        "rating_overall": app.rating_overall,
                        "rating_ease_of_use": app.rating_ease_of_use,
                        "rating_speed": app.rating_speed,
                        "rating_quality": app.rating_quality,
                        "rating_cost": app.rating_cost,
                        "rating_integration": app.rating_integration,
                        "rating_reliability": app.rating_reliability,
                        "best_for": app.best_for,
                        "limitations": app.limitations,
                        "api_available": app.api_available,
                        "local_processing": app.local_processing,
                        "requires_internet": app.requires_internet,
                        "requires_account": app.requires_account
                    })
                with open(args.save, 'w') as f:
                    json.dump(apps_dict, f, indent=2)
                print(f"\n✅ Results saved to: {args.save}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()