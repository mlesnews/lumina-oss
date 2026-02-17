#!/usr/bin/env python3
"""
List All Desktop AI Services

Comprehensive inventory of ALL AI services accessible from the desktop:
- Windows Copilot
- NAS AI services
- Neo Browser AI
- Local AI (Ollama/ULTRON/KAIJU)
- Cloud AI services
- Any other desktop AI integrations

Tags: #AI #DESKTOP #SERVICES #INVENTORY #COPILOT #NAS #NEO @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import os
import requests
import winreg
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

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

logger = get_logger("ListDesktopAIServices")


class DesktopAIServiceInventory:
    """
    Comprehensive Desktop AI Service Inventory

    Lists ALL AI services accessible from the desktop
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize desktop AI service inventory"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"

        self.inventory = {
            "timestamp": datetime.now().isoformat(),
            "sider_ai": {},
            "roamwise_ai": {},
            "roamresearch": {},
            "windows_ai": {},
            "nas_ai": {},
            "neo_browser_ai": {},
            "local_ai": {},
            "cloud_ai": {},
            "desktop_ai_integrations": []
        }

        logger.info("✅ Desktop AI Service Inventory initialized")

    def check_windows_copilot(self) -> Dict[str, Any]:
        """Check Windows Copilot availability"""
        logger.info("🔍 Checking Windows Copilot...")

        copilot_info = {
            "available": False,
            "enabled": False,
            "version": None,
            "process_running": False
        }

        # Check if Windows 11 (Copilot is Windows 11 feature)
        try:
            import platform
            if platform.system() == "Windows":
                version = platform.version()
                if int(version.split('.')[0]) >= 10:
                    copilot_info["windows_version"] = version

                    # Check for Copilot process
                    try:
                        import psutil
                        for proc in psutil.process_iter(['pid', 'name']):
                            try:
                                if 'copilot' in proc.info['name'].lower() or 'msedge' in proc.info['name'].lower():
                                    copilot_info["process_running"] = True
                                    break
                            except (psutil.NoSuchProcess, psutil.AccessDenied):
                                pass
                    except ImportError:
                        pass

                    # Check registry for Copilot settings
                    try:
                        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                                          r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced") as key:
                            try:
                                copilot_enabled = winreg.QueryValueEx(key, "ShowCopilotButton")[0]
                                copilot_info["enabled"] = bool(copilot_enabled)
                            except FileNotFoundError:
                                pass
                    except Exception:
                        pass

                    copilot_info["available"] = True
                    logger.info("   ✅ Windows Copilot available (Windows 11)")
        except Exception as e:
            logger.debug(f"   Error checking Copilot: {e}")

        return copilot_info

    def check_nas_ai_services(self) -> Dict[str, Any]:
        """Check NAS AI services"""
        logger.info("🔍 Checking NAS AI Services...")

        nas_ai = {
            "nas_reachable": False,
            "nas_ip": "<NAS_PRIMARY_IP>",
            "ai_services": []
        }

        # Check NAS connectivity
        try:
            response = requests.get(f"http://{nas_ai['nas_ip']}:5000", timeout=5)
            nas_ai["nas_reachable"] = True
            logger.info(f"   ✅ NAS reachable at {nas_ai['nas_ip']}")
        except Exception:
            logger.debug(f"   NAS not reachable at {nas_ai['nas_ip']}")

        # Check for AI services on NAS
        # Common NAS AI service ports/endpoints
        nas_ai_endpoints = [
            ("Ollama", 11434),
            ("AI API", 8080),
            ("AI Service", 3000),
            ("AI Gateway", 5000),
        ]

        for service_name, port in nas_ai_endpoints:
            try:
                response = requests.get(f"http://{nas_ai['nas_ip']}:{port}", timeout=2)
                if response.status_code < 500:
                    nas_ai["ai_services"].append({
                        "name": service_name,
                        "port": port,
                        "available": True
                    })
                    logger.info(f"   ✅ {service_name} available on port {port}")
            except Exception:
                pass

        # Check via Azure Key Vault (if configured)
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            nas_vault = NASAzureVaultIntegration()
            nas_ai["azure_vault_configured"] = True
            logger.info("   ✅ NAS Azure Vault integration available")
        except Exception:
            nas_ai["azure_vault_configured"] = False

        return nas_ai

    def check_sider_ai(self) -> Dict[str, Any]:
        """Check Sider.AI (WiseBase features) - PRIMARY IMPORTANCE"""
        logger.info("🔍 Checking Sider.AI...")
        logger.info("   ⭐ PRIMARY IMPORTANCE - WiseBase features")

        sider_ai = {
            "installed": False,
            "running": False,
            "wisebase_available": False,
            "api_available": False,
            "via_roamwise": False,
            "capabilities": ["WiseBase", "AI Assistant", "Content Generation", "Research"]
        }

        # Check if Sider is installed/running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    if 'sider' in proc.info['name'].lower():
                        sider_ai["installed"] = True
                        sider_ai["running"] = True
                        sider_ai["process_path"] = proc.info.get('exe', 'Unknown')
                        logger.info(f"   ✅ Sider.AI process found: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check for Sider API/endpoint (direct)
        sider_endpoints = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000"
        ]

        for endpoint in sider_endpoints:
            try:
                response = requests.get(f"{endpoint}/health", timeout=2)
                if response.status_code == 200:
                    sider_ai["api_available"] = True
                    sider_ai["endpoint"] = endpoint
                    logger.info(f"   ✅ Sider.AI API found: {endpoint}")
                    break
            except Exception:
                pass

        # Check via ROAMWISE.AI gateway (Sider.AI is half of ROAMWISE)
        try:
            # Check ROAMWISE.AI first
            roamwise_response = requests.get("http://roamwise.ai", timeout=5)
            if roamwise_response.status_code < 500:
                # Check if Sider/WiseBase is available via ROAMWISE
                sider_endpoint = "http://roamwise.ai/sider"
                try:
                    sider_response = requests.get(sider_endpoint, timeout=5)
                    if sider_response.status_code < 500:
                        sider_ai["api_available"] = True
                        sider_ai["via_roamwise"] = True
                        sider_ai["endpoint"] = sider_endpoint
                        sider_ai["wisebase_available"] = True
                        logger.info(f"   ✅ Sider.AI available via ROAMWISE.AI gateway: {sider_endpoint}")
                except Exception:
                    # Check if Sider/WiseBase mentioned in ROAMWISE response
                    if "sider" in roamwise_response.text.lower() or "wisebase" in roamwise_response.text.lower():
                        sider_ai["via_roamwise"] = True
                        sider_ai["endpoint"] = sider_endpoint
                        sider_ai["wisebase_available"] = True
                        logger.info("   ✅ Sider.AI component detected in ROAMWISE.AI")
        except Exception:
            pass

        # Check config file
        sider_config = self.config_dir / "sider_ai_config.json"
        if sider_config.exists():
            try:
                with open(sider_config, 'r') as f:
                    config = json.load(f)
                    if config.get("wisebase_enabled"):
                        sider_ai["wisebase_available"] = True
                        if not sider_ai.get("endpoint") and config.get("endpoints"):
                            sider_ai["endpoint"] = config.get("endpoints", [""])[0]
                        logger.info("   ✅ Sider.AI configured (WiseBase enabled)")
            except Exception:
                pass

        # Check ROAMWISE config for Sider.AI
        roamwise_config = self.config_dir / "roamwise_config.json"
        if roamwise_config.exists():
            try:
                with open(roamwise_config, 'r') as f:
                    config = json.load(f)
                    sider_config = config.get("siderai_wisebase", {})
                    if sider_config.get("enabled"):
                        sider_ai["wisebase_available"] = True
                        sider_ai["api_available"] = True
                        logger.info("   ✅ Sider.AI WiseBase enabled via ROAMWISE config")
            except Exception:
                pass

        return sider_ai

    def check_roamwise_ai(self) -> Dict[str, Any]:
        """Check ROAMWISE.AI (Web frontend portal/gateway - .local network only)"""
        logger.info("🔍 Checking ROAMWISE.AI...")

        roamwise_ai = {
            "available": False,
            "endpoint": None,
            "local_network_only": True,
            "components": {
                "sider_ai": False,
                "roamresearch": False
            },
            "capabilities": ["Web Portal", "Gateway", "WiseBase Integration", "RoamResearch Integration"]
        }

        # ROAMWISE is .local network only
        roamwise_endpoints = [
            "http://roamwise.ai",
            "http://roamwise.local",
            "http://<NAS_PRIMARY_IP>/roamwise",  # NAS
            "http://localhost:5000/roamwise",
            "http://localhost:3000/roamwise"
        ]

        for endpoint in roamwise_endpoints:
            try:
                response = requests.get(endpoint, timeout=2)
                if response.status_code < 500:
                    roamwise_ai["available"] = True
                    roamwise_ai["endpoint"] = endpoint
                    logger.info(f"   ✅ ROAMWISE.AI found: {endpoint}")
                    break
            except Exception:
                pass

        return roamwise_ai

    def check_roamresearch(self) -> Dict[str, Any]:
        """Check RoamResearch (Lifetime Account - Personal)"""
        logger.info("🔍 Checking RoamResearch...")

        roamresearch = {
            "installed": False,
            "running": False,
            "lifetime_account": False,
            "api_available": False,
            "capabilities": ["Knowledge Graph", "Note-taking", "Research", "Personal Knowledge Management"]
        }

        # Check for RoamResearch process
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'roam' in proc.info['name'].lower():
                        roamresearch["installed"] = True
                        roamresearch["running"] = True
                        logger.info(f"   ✅ RoamResearch process found")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check config for Lifetime Account
        roamresearch_config = self.config_dir / "roamresearch_config.json"
        if roamresearch_config.exists():
            try:
                with open(roamresearch_config, 'r') as f:
                    config = json.load(f)
                    if config.get("lifetime_account"):
                        roamresearch["lifetime_account"] = True
                        roamresearch["api_key"] = "configured" if config.get("api_key") else None
                        logger.info("   ✅ RoamResearch configured (Lifetime Account)")
            except Exception:
                pass

        return roamresearch

    def check_neo_browser_ai(self) -> Dict[str, Any]:
        """Check Neo Browser AI capabilities"""
        logger.info("🔍 Checking Neo Browser AI...")

        neo_ai = {
            "browser_installed": False,
            "browser_running": False,
            "ai_capabilities": [],
            "api_available": False,
            "cdp_available": False
        }

        # Check if Neo browser is installed
        neo_paths = [
            Path.home() / "AppData" / "Local" / "Neo" / "Application" / "neo.exe",
            Path("C:/Program Files/Neo/Neo.exe"),
            Path("C:/Program Files (x86)/Neo/Neo.exe"),
        ]

        for path in neo_paths:
            if path.exists():
                neo_ai["browser_installed"] = True
                neo_ai["browser_path"] = str(path)
                logger.info(f"   ✅ Neo Browser installed: {path}")
                break

        # Check if Neo is running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'neo' in proc.info['name'].lower():
                        neo_ai["browser_running"] = True
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check Neo AI capabilities
        # Neo Browser has built-in AI features
        neo_ai["ai_capabilities"] = [
            "Built-in AI Assistant",
            "AI-powered search",
            "AI content generation",
            "AI chat interface"
        ]

        # Check if JARVIS Neo integration is available
        try:
            from jarvis_neo_full_control import JARVISNeoFullControl
            neo_ai["jarvis_integration"] = True
            neo_ai["api_available"] = True  # Via JARVIS API
            logger.info("   ✅ JARVIS Neo integration available")
        except ImportError:
            neo_ai["jarvis_integration"] = False

        # Check CDP availability (for automation)
        try:
            response = requests.get("http://localhost:9222/json", timeout=2)
            if response.status_code == 200:
                neo_ai["cdp_available"] = True
                logger.info("   ✅ Neo CDP available (port 9222)")
        except Exception:
            pass

        return neo_ai

    def check_local_ai(self) -> Dict[str, Any]:
        """Check local AI services (Ollama, ULTRON, KAIJU)"""
        logger.info("🔍 Checking Local AI Services...")

        local_ai = {
            "ollama": {
                "installed": False,
                "running": False,
                "url": "http://localhost:11434",
                "models": []
            },
            "ultron": {
                "available": False,
                "url": "http://localhost:11434"
            },
            "kaiju": {
                "available": False,
                "url": "http://<NAS_IP>:11434"
            }
        }

        # Check Ollama
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                local_ai["ollama"]["installed"] = True
                local_ai["ollama"]["running"] = True
                models = response.json().get("models", [])
                local_ai["ollama"]["models"] = [
                    {"name": m.get("name", ""), "size": m.get("size", 0)}
                    for m in models
                ]
                logger.info(f"   ✅ Ollama running: {len(models)} models")
        except Exception:
            pass

        # Check ULTRON
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                local_ai["ultron"]["available"] = True
        except Exception:
            pass

        # Check KAIJU
        try:
            response = requests.get("http://<NAS_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                local_ai["kaiju"]["available"] = True
        except Exception:
            pass

        return local_ai

    def check_cloud_ai(self) -> Dict[str, Any]:
        """Check cloud AI service configurations"""
        logger.info("🔍 Checking Cloud AI Services...")

        cloud_ai = {
            "aws_bedrock": {"configured": bool(os.getenv("AWS_ACCESS_KEY_ID"))},
            "azure_openai": {"configured": bool(os.getenv("AZURE_OPENAI_API_KEY"))},
            "anthropic": {"configured": bool(os.getenv("ANTHROPIC_API_KEY"))},
            "openai": {"configured": bool(os.getenv("OPENAI_API_KEY"))}
        }

        return cloud_ai

    def generate_inventory(self) -> Dict[str, Any]:
        """Generate complete desktop AI service inventory"""
        logger.info("=" * 80)
        logger.info("📋 Generating Desktop AI Service Inventory")
        logger.info("=" * 80)
        logger.info("")

        # Check all AI services (priority order)
        # 1. Sider.AI (PRIMARY IMPORTANCE - WiseBase)
        self.inventory["sider_ai"] = self.check_sider_ai()
        logger.info("")

        # 2. ROAMWISE.AI (Web frontend portal/gateway - .local network only)
        self.inventory["roamwise_ai"] = self.check_roamwise_ai()
        logger.info("")

        # 3. RoamResearch (Lifetime Account - Personal)
        self.inventory["roamresearch"] = self.check_roamresearch()
        logger.info("")

        # 4. Windows Copilot
        self.inventory["windows_ai"] = self.check_windows_copilot()
        logger.info("")

        # 5. NAS AI Services
        self.inventory["nas_ai"] = self.check_nas_ai_services()
        logger.info("")

        # 6. Neo Browser AI
        self.inventory["neo_browser_ai"] = self.check_neo_browser_ai()
        logger.info("")

        # 7. Local AI
        self.inventory["local_ai"] = self.check_local_ai()
        logger.info("")

        # 8. Cloud AI
        self.inventory["cloud_ai"] = self.check_cloud_ai()
        logger.info("")

        # Summary
        logger.info("=" * 80)
        logger.info("📊 INVENTORY SUMMARY")
        logger.info("=" * 80)

        total_services = sum([
            1 if (self.inventory["sider_ai"].get("installed") or 
                  self.inventory["sider_ai"].get("running") or 
                  self.inventory["sider_ai"].get("api_available") or 
                  self.inventory["sider_ai"].get("via_roamwise")) else 0,
            1 if self.inventory["roamwise_ai"].get("available") else 0,
            1 if (self.inventory["roamresearch"].get("lifetime_account") or 
                  self.inventory["roamresearch"].get("running") or
                  self.inventory["roamresearch"].get("api_available")) else 0,
            1 if self.inventory["windows_ai"].get("available") else 0,
            len(self.inventory["nas_ai"].get("ai_services", [])),
            1 if self.inventory["neo_browser_ai"].get("browser_installed") else 0,
            1 if self.inventory["local_ai"]["ollama"].get("running") else 0,
            sum(1 for service in self.inventory["cloud_ai"].values() if service.get("configured"))
        ])

        logger.info(f"Total AI Services: {total_services}")
        logger.info("=" * 80)

        return self.inventory

    def print_inventory(self):
        """Print human-readable inventory"""
        print("\n" + "=" * 80)
        print("🤖 DESKTOP AI SERVICES INVENTORY")
        print("=" * 80)
        print()

        # Sider.AI (PRIMARY IMPORTANCE)
        print("⭐ SIDER.AI (PRIMARY IMPORTANCE - WiseBase):")
        print("-" * 80)
        sider = self.inventory["sider_ai"]
        if sider.get("installed") or sider.get("running") or sider.get("api_available") or sider.get("via_roamwise"):
            status_parts = []
            if sider.get("running"):
                status_parts.append("RUNNING")
            elif sider.get("installed"):
                status_parts.append("INSTALLED")
            elif sider.get("via_roamwise"):
                status_parts.append("AVAILABLE VIA ROAMWISE")
            elif sider.get("api_available"):
                status_parts.append("API AVAILABLE")

            print(f"Sider.AI: ✅ {' / '.join(status_parts) if status_parts else 'AVAILABLE'}")
            print(f"  WiseBase: {'✅' if sider.get('wisebase_available') else '❌'}")
            print(f"  API Available: {'✅' if sider.get('api_available') else '❌'}")
            if sider.get("via_roamwise"):
                print(f"  Via ROAMWISE Gateway: ✅")
                print(f"  Endpoint: {sider.get('endpoint', 'N/A')}")
            elif sider.get("endpoint"):
                print(f"  Endpoint: {sider.get('endpoint')}")
            print(f"  Capabilities: {', '.join(sider.get('capabilities', []))}")
        else:
            print("Sider.AI: ❌ NOT FOUND")
            print("  Note: Sider.AI may be available via ROAMWISE.AI gateway")
        print()

        # ROAMWISE.AI
        print("🌐 ROAMWISE.AI (Web Portal/Gateway - .local network only):")
        print("-" * 80)
        roamwise = self.inventory["roamwise_ai"]
        if roamwise.get("available"):
            print(f"ROAMWISE.AI: ✅ AVAILABLE")
            print(f"  Endpoint: {roamwise.get('endpoint', 'N/A')}")
            print(f"  Local Network Only: ✅")
            print(f"  Architecture:")
            print(f"    Half 1: Sider.AI (WiseBase) ⭐")
            print(f"    Half 2: RoamResearch (Lifetime Account)")
            print(f"  Components:")
            sider_component = roamwise.get('components', {}).get('sider_ai', False)
            roamresearch_component = roamwise.get('components', {}).get('roamresearch', False)
            # Also check if Sider.AI was found via ROAMWISE
            sider = self.inventory.get("sider_ai", {})
            if sider.get("via_roamwise"):
                sider_component = True
            print(f"    - Sider.AI (WiseBase): {'✅' if sider_component else '❌'}")
            print(f"    - RoamResearch: {'✅' if roamresearch_component else '❌'}")
        else:
            print("ROAMWISE.AI: ❌ NOT AVAILABLE (.local network only)")
        print()

        # RoamResearch
        print("📚 ROAMRESEARCH (Lifetime Account - Personal):")
        print("-" * 80)
        roamresearch = self.inventory["roamresearch"]
        if roamresearch.get("lifetime_account") or roamresearch.get("running"):
            print(f"RoamResearch: ✅ {'RUNNING' if roamresearch.get('running') else 'CONFIGURED'}")
            print(f"  Lifetime Account: {'✅' if roamresearch.get('lifetime_account') else '❌'}")
            print(f"  API Available: {'✅' if roamresearch.get('api_available') else '❌'}")
        else:
            print("RoamResearch: ❌ NOT CONFIGURED")
        print()

        # Windows AI
        print("🪟 WINDOWS AI:")
        print("-" * 80)
        copilot = self.inventory["windows_ai"]
        if copilot.get("available"):
            print(f"Windows Copilot: ✅ AVAILABLE")
            print(f"  Enabled: {'✅' if copilot.get('enabled') else '❌'}")
            print(f"  Process Running: {'✅' if copilot.get('process_running') else '❌'}")
        else:
            print("Windows Copilot: ❌ NOT AVAILABLE")
        print()

        # NAS AI
        print("🗄️  NAS AI SERVICES:")
        print("-" * 80)
        nas_ai = self.inventory["nas_ai"]
        print(f"NAS Reachable: {'✅' if nas_ai.get('nas_reachable') else '❌'} ({nas_ai.get('nas_ip', 'N/A')})")
        if nas_ai.get("ai_services"):
            for service in nas_ai["ai_services"]:
                print(f"  ✅ {service['name']} (port {service['port']})")
        else:
            print("  No AI services detected on NAS")
        print()

        # Neo Browser AI
        print("🌐 NEO BROWSER AI:")
        print("-" * 80)
        neo_ai = self.inventory["neo_browser_ai"]
        print(f"Neo Browser: {'✅ INSTALLED' if neo_ai.get('browser_installed') else '❌ NOT INSTALLED'}")
        if neo_ai.get("browser_installed"):
            print(f"  Running: {'✅' if neo_ai.get('browser_running') else '❌'}")
            print(f"  JARVIS Integration: {'✅' if neo_ai.get('jarvis_integration') else '❌'}")
            print(f"  CDP Available: {'✅' if neo_ai.get('cdp_available') else '❌'}")
            print(f"  AI Capabilities: {', '.join(neo_ai.get('ai_capabilities', []))}")
        print()

        # Local AI
        print("💻 LOCAL AI SERVICES:")
        print("-" * 80)
        local_ai = self.inventory["local_ai"]
        ollama = local_ai.get("ollama", {})
        print(f"Ollama: {'✅ RUNNING' if ollama.get('running') else '❌ NOT RUNNING'}")
        if ollama.get("running"):
            print(f"  Models: {len(ollama.get('models', []))}")
            for model in ollama.get("models", []):
                print(f"    - {model.get('name', 'Unknown')}")
        print(f"ULTRON: {'✅' if local_ai.get('ultron', {}).get('available') else '❌'}")
        print(f"KAIJU: {'✅' if local_ai.get('kaiju', {}).get('available') else '❌'}")
        print()

        # Cloud AI
        print("☁️  CLOUD AI SERVICES:")
        print("-" * 80)
        cloud_ai = self.inventory["cloud_ai"]
        for service_name, service_info in cloud_ai.items():
            status = "✅ CONFIGURED" if service_info.get("configured") else "❌ NOT CONFIGURED"
            print(f"{service_name.replace('_', ' ').title()}: {status}")

        print()
        print("=" * 80)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="List All Desktop AI Services")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--save", metavar="FILE", help="Save inventory to file")

        args = parser.parse_args()

        inventory = DesktopAIServiceInventory()
        result = inventory.generate_inventory()

        if args.json:
            print(json.dumps(result, indent=2, default=str))
        else:
            inventory.print_inventory()

        if args.save:
            with open(args.save, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Inventory saved to: {args.save}")
        else:
            # Save default
            default_file = inventory.project_root / "data" / "ai_service_inventory" / f"desktop_ai_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            default_file.parent.mkdir(parents=True, exist_ok=True)
            with open(default_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Inventory saved to: {default_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()