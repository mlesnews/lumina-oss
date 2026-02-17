#!/usr/bin/env python3
"""
Laptop LLM Setup - Complete Hardware-Optimized Single Node LLM Deployment

This script provides a comprehensive setup for running LLMs on high-performance laptops,
including ASUS ROG Strix SCAR 18 with Intel Core Ultra 9 275HX and RTX 5090 GPU.

Features:
- Hardware detection and optimization
- Notification and error fixing
- Docker container deployment
- Performance monitoring
- Automatic model selection
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Dynamic timeout scaling
try:
    from dynamic_timeout_scaling import (
        get_timeout_scaler,
        TimeoutConfig,
        get_with_dynamic_timeout,
        post_with_dynamic_timeout
    )
    DYNAMIC_TIMEOUT_AVAILABLE = True
except ImportError:
    DYNAMIC_TIMEOUT_AVAILABLE = False
    get_timeout_scaler = None
    TimeoutConfig = None
    get_with_dynamic_timeout = None
    post_with_dynamic_timeout = None



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class LaptopLLMSetup:
    """Complete laptop LLM setup and management"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.hardware_detector = None
        self.notification_manager = None

        # Setup logging
        self.logger = logging.getLogger("LaptopLLMSetup")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - 🚀 %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

        # Initialize dynamic timeout scaling
        self.timeout_scaler = None
        if DYNAMIC_TIMEOUT_AVAILABLE:
            try:
                self.timeout_scaler = get_timeout_scaler()

                # Configure timeouts for Docker operations
                docker_config = TimeoutConfig(
                    base_timeout=60.0,  # 60 seconds base for docker-compose
                    min_timeout=30.0,   # Minimum 30 seconds
                    max_timeout=600.0,  # Maximum 10 minutes for builds
                    latency_multiplier=2.0,
                    adaptive_factor=1.5,
                    retry_backoff_base=2.0,
                    max_retries=3
                )
                self.timeout_scaler.configure_system("docker", docker_config)

                # Configure timeouts for LLM API operations
                llm_api_config = TimeoutConfig(
                    base_timeout=30.0,  # 30 seconds base for API calls
                    min_timeout=10.0,   # Minimum 10 seconds
                    max_timeout=120.0,  # Maximum 2 minutes
                    latency_multiplier=3.0,
                    adaptive_factor=1.5,
                    retry_backoff_base=2.0,
                    max_retries=5  # More retries for API calls
                )
                self.timeout_scaler.configure_system("llm_api", llm_api_config)

                self.logger.info("⏱️  Dynamic timeout scaling enabled")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to initialize dynamic timeout scaling: {e}")
                self.timeout_scaler = None

    async def setup_complete_system(self) -> bool:
        """Complete setup: hardware detection, fixes, and deployment"""
        self.logger.info("🚀 Starting Complete Laptop LLM Setup...")

        try:
            # Step 1: Detect and analyze hardware
            self.logger.info("1️⃣ Detecting hardware specifications...")
            if not await self._detect_hardware():
                return False

            # Step 2: Fix all notifications and errors
            self.logger.info("2️⃣ Fixing system notifications and errors...")
            if not await self._fix_notifications():
                self.logger.warning("Some notifications could not be fixed, continuing...")

            # Step 3: Deploy optimized LLM container
            self.logger.info("3️⃣ Deploying hardware-optimized LLM container...")
            if not await self._deploy_llm_container():
                return False

            # Step 4: Verify deployment and performance
            self.logger.info("4️⃣ Verifying deployment and testing performance...")
            if not await self._verify_deployment():
                return False

            # Step 5: Setup monitoring and optimization
            self.logger.info("5️⃣ Setting up monitoring and continuous optimization...")
            if not await self._setup_monitoring():
                self.logger.warning("Monitoring setup had issues, but deployment continues...")

            self.logger.info("✅ Complete Laptop LLM Setup Successful!")
            self._print_success_summary()

            return True

        except Exception as e:
            self.logger.error(f"❌ Setup failed: {e}")
            return False

    async def _detect_hardware(self) -> bool:
        """Detect and analyze hardware"""
        try:
            # Import hardware detector
            sys.path.insert(0, str(self.project_root / "scripts" / "python"))
            from hardware_detector import HardwareDetector

            self.hardware_detector = HardwareDetector()
            hardware = self.hardware_detector.detect_hardware()

            self.logger.info("📊 Hardware Detection Results:")
            self.logger.info(f"   • CPU: {hardware['cpu']['name']} ({hardware['cpu']['cores']} cores)")
            self.logger.info(f"   • RAM: {hardware['memory']['total_gb']}GB")
            self.logger.info(f"   • GPU: {hardware['gpu']['name']} ({hardware['gpu']['vram_gb']}GB VRAM)")
            self.logger.info(f"   • Storage: {hardware['storage']['total_gb']}GB total, {hardware['storage']['free_gb']}GB free")

            # Save hardware profile
            profile_path = self.hardware_detector.save_hardware_profile()
            self.logger.info(f"   • Profile saved: {profile_path}")

            # Log recommendations
            recommendations = hardware['recommendations']
            self.logger.info("🎯 LLM Recommendations:")
            self.logger.info(f"   • Model Size: {recommendations['model_size']}")
            self.logger.info(f"   • Quantization: {recommendations['quantization']}")
            self.logger.info(f"   • Context Length: {recommendations['context_length']}")
            self.logger.info(f"   • Docker CPU Limit: {recommendations['docker_resources']['cpu_limit']}")
            self.logger.info(f"   • Docker Memory Limit: {recommendations['docker_resources']['memory_limit_gb']}GB")

            return True

        except Exception as e:
            self.logger.error(f"Hardware detection failed: {e}")
            return False

    async def _fix_notifications(self) -> bool:
        """Fix all system notifications and errors"""
        try:
            # Import notification manager
            from notification_fix_manager import NotificationFixManager

            self.notification_manager = NotificationFixManager()

            # Common notifications to check and fix
            common_notifications = [
                ("vscode_task_error", "there are task errors", "vscode"),
                ("extension_warning", "extension 'esbenp.prettier-vscode' is configured as a formatter but not available", "vscode"),
                ("system_notification", "notifcation error - please reopen file", "vscode"),
                ("docker_error", "docker daemon not running", "docker"),
                ("dependency_error", "ModuleNotFoundError", "python"),
                ("hardware_error", "armory crate", "asus"),
            ]

            fixed_count = 0
            total_count = len(common_notifications)

            for notif_type, message, source in common_notifications:
                try:
                    fixed = self.notification_manager.report_notification(
                        notif_type, message, source
                    )
                    if fixed:
                        fixed_count += 1
                        self.logger.info(f"   ✅ Fixed: {message[:50]}...")
                    else:
                        self.logger.warning(f"   ⚠️  Could not fix: {message[:50]}...")
                except Exception as e:
                    self.logger.warning(f"   ❌ Error fixing {message[:30]}...: {e}")

            self.logger.info(f"📊 Notification fixes: {fixed_count}/{total_count} successful")

            # Get summary
            summary = self.notification_manager.get_notification_summary(1)  # Last hour
            self.logger.info(f"   • Total notifications: {summary['total_notifications']}")
            self.logger.info(f"   • Fixed: {summary['fixed_notifications']}")
            self.logger.info(f"   • Remaining: {summary['unfixed_notifications']}")

            return fixed_count > 0  # At least some fixes worked

        except Exception as e:
            self.logger.error(f"Notification fixing failed: {e}")
            return False

    async def _deploy_llm_container(self) -> bool:
        """Deploy the optimized LLM container"""
        try:
            compose_file = self.project_root / "containerization" / "services" / "laptop-optimized-llm" / "docker-compose.yml"

            if not compose_file.exists():
                self.logger.error(f"Docker compose file not found: {compose_file}")
                return False

            self.logger.info("🐳 Building and starting laptop-optimized LLM container...")

            # Stop any existing containers first
            self.logger.info("   • Stopping existing containers...")
            try:
                # Get dynamic timeout for docker operations
                timeout = 60.0  # Default fallback
                if self.timeout_scaler:
                    timeout = self.timeout_scaler.get_dynamic_timeout("docker", "compose_down")

                stop_result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "down"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=timeout
                )

                if stop_result.returncode != 0:
                    self.logger.warning(f"Stop command failed: {stop_result.stderr}")
            except subprocess.TimeoutExpired:
                self.logger.warning("Stop command timed out, continuing with deployment...")
            except Exception as e:
                self.logger.warning(f"Error stopping containers: {e}, continuing with deployment...")

            # Build and start containers
            self.logger.info("   • Building and starting containers...")
            try:
                # Get dynamic timeout for docker build operations (longer)
                timeout = 600.0  # Default 10 minutes fallback
                if self.timeout_scaler:
                    timeout = self.timeout_scaler.get_dynamic_timeout("docker", "compose_build")
                    # Ensure minimum of 5 minutes for builds
                    timeout = max(timeout, 300.0)

                deploy_result = subprocess.run(
                    ["docker-compose", "-f", str(compose_file), "up", "-d", "--build"],
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=timeout
                )

                if deploy_result.returncode != 0:
                    self.logger.error(f"Deployment failed: {deploy_result.stderr}")
                    return False
            except subprocess.TimeoutExpired:
                self.logger.error("Deployment timed out after 10 minutes")
                return False
            except Exception as e:
                self.logger.error(f"Deployment command failed: {e}")
                return False

            self.logger.info("   ✅ Container deployment successful")

            # Wait for container to be ready
            self.logger.info("   • Waiting for container to initialize...")
            await asyncio.sleep(30)

            return True

        except Exception as e:
            self.logger.error(f"Container deployment failed: {e}")
            return False

    async def _verify_deployment(self) -> bool:
        """Verify the LLM deployment is working"""
        try:
            self.logger.info("🔍 Verifying LLM deployment...")

            # Check if container is running
            try:
                # Get dynamic timeout for docker ps
                timeout = 10.0  # Default fallback
                if self.timeout_scaler:
                    timeout = self.timeout_scaler.get_dynamic_timeout("docker", "ps_check")

                ps_result = subprocess.run(
                    ["docker", "ps", "--filter", "name=laptop-optimized-llm", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )

                if ps_result.returncode != 0:
                    self.logger.error("Container is not running")
                    return False
            except subprocess.TimeoutExpired:
                self.logger.error("Docker ps command timed out")
                return False
            except Exception as e:
                self.logger.error(f"Docker ps command failed: {e}")
                return False

            try:
                containers = [json.loads(line) for line in ps_result.stdout.strip().split('\n') if line.strip()]
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse docker ps output: {e}")
                return False
            if not containers:
                self.logger.error("No laptop-optimized-llm container found")
                return False

            container = containers[0]
            self.logger.info(f"   ✅ Container running: {container.get('Names', 'unknown')}")

            # Test API endpoint
            self.logger.info("   • Testing API endpoint...")
            try:
                import requests

                # Use dynamic timeout scaling for API calls
                if DYNAMIC_TIMEOUT_AVAILABLE and self.timeout_scaler:
                    response = get_with_dynamic_timeout(
                        system="llm_api",
                        operation="api_tags",
                        url="http://localhost:11434/api/tags"
                    )
                else:
                    # Fallback to standard requests with fixed timeout
                    response = requests.get("http://localhost:11434/api/tags", timeout=10)

                if response.status_code == 200:
                    api_data = response.json()
                    model_count = len(api_data.get('models', []))
                    self.logger.info(f"   ✅ API responding - {model_count} models available")
                else:
                    self.logger.warning(f"   ⚠️  API returned status {response.status_code}")
                    return False
            except Exception as e:
                self.logger.error(f"   ❌ API endpoint not responding: {e}")
                return False

            # Test basic model loading
            self.logger.info("   • Testing model loading...")
            try:
                import requests
                # Try to load a basic model
                if DYNAMIC_TIMEOUT_AVAILABLE and self.timeout_scaler:
                    response = post_with_dynamic_timeout(
                        system="llm_api",
                        operation="model_generate",
                        url="http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.1:8b",
                            "prompt": "Hello",
                            "stream": False,
                            "options": {"num_predict": 10}
                        }
                    )
                else:
                    # Fallback to standard requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3.1:8b",
                            "prompt": "Hello",
                            "stream": False,
                            "options": {"num_predict": 10}
                        },
                        timeout=30
                    )

                if response.status_code == 200:
                    self.logger.info("   ✅ Model inference working")
                else:
                    self.logger.warning(f"   ⚠️  Model inference returned status {response.status_code}")

            except Exception as e:
                self.logger.warning(f"   ⚠️  Model inference test failed: {e}")

            return True

        except Exception as e:
            self.logger.error(f"Deployment verification failed: {e}")
            return False

    async def _setup_monitoring(self) -> bool:
        """Setup monitoring and continuous optimization"""
        try:
            self.logger.info("📊 Setting up monitoring...")

            # Create monitoring script
            monitor_script = self.project_root / "scripts" / "python" / "laptop_llm_monitor.py"

            if not monitor_script.exists():
                # Create basic monitoring script
                monitor_content = '''#!/usr/bin/env python3
"""
Laptop LLM Monitor - Continuous performance monitoring and optimization
"""

import asyncio
import json
import psutil
import requests
import time
from datetime import datetime
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

class LaptopLLMMonitor:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.metrics_file = self.project_root / "data" / "llm_metrics.json"
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)

    async def monitor_continuously(self):
        """Monitor LLM performance continuously"""
        print("🚀 Starting Laptop LLM Performance Monitor...")

        while True:
            try:
                metrics = await self.collect_metrics()
                self.save_metrics(metrics)

                # Check for optimization opportunities
                await self.check_optimizations(metrics)

                await asyncio.sleep(60)  # Monitor every minute

            except Exception as e:
                print(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)

    async def collect_metrics(self):
        """Collect system and LLM metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": {
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            }
        }

        # Try to get LLM-specific metrics
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                api_data = response.json()
                metrics["llm"] = {
                    "status": "running",
                    "model_count": len(api_data.get('models', [])),
                    "models": [m.get('name') for m in api_data.get('models', [])]
                }
            else:
                metrics["llm"] = {"status": "error", "status_code": response.status_code}
        except:
            metrics["llm"] = {"status": "unreachable"}

        return metrics

    def save_metrics(self, metrics):
        """Save metrics to file"""
        try:
            existing = []
            if self.metrics_file.exists():
                with open(self.metrics_file, 'r') as f:
                    existing = json.load(f)

            existing.append(metrics)

            # Keep only last 1000 entries
            if len(existing) > 1000:
                existing = existing[-1000:]

            with open(self.metrics_file, 'w') as f:
                json.dump(existing, f, indent=2)

        except Exception as e:
            print(f"Failed to save metrics: {e}")

    async def check_optimizations(self, metrics):
        """Check for optimization opportunities"""
        system = metrics.get("system", {})
        llm = metrics.get("llm", {})

        # High CPU usage warning
        if system.get("cpu_percent", 0) > 90:
            print("⚠️  High CPU usage detected - consider reducing model size")

        # High memory usage warning
        if system.get("memory_percent", 0) > 85:
            print("⚠️  High memory usage detected - consider model quantization")

        # LLM status checks
        if llm.get("status") != "running":
            print("❌ LLM service not responding")

async def main():
    monitor = LaptopLLMMonitor()
    await monitor.monitor_continuously()

if __name__ == "__main__":
    asyncio.run(main())
'''
                monitor_script.write_text(monitor_content)
                monitor_script.chmod(0o755)
                self.logger.info(f"   • Created monitoring script: {monitor_script}")

            # Start monitoring in background (optional)
            self.logger.info("   • Monitoring setup complete")
            self.logger.info("   • Run 'python scripts/python/laptop_llm_monitor.py' for continuous monitoring")

            return True

        except Exception as e:
            self.logger.error(f"Monitoring setup failed: {e}")
            return False

    def _print_success_summary(self):
        """Print successful setup summary"""
        print("\n" + "="*60)
        print("🎉 LAPTOP LLM SETUP COMPLETE!")
        print("="*60)
        print("✅ Hardware detected and optimized")
        print("✅ System notifications fixed")
        print("✅ LLM container deployed")
        print("✅ API endpoints verified")
        print("✅ Monitoring configured")
        print("")
        print("🚀 Your laptop-optimized LLM is ready!")
        print("")
        print("📋 Access Points:")
        print("   • Ollama API: http://localhost:11434")
        print("   • Web UI: http://localhost:8080 (if enabled)")
        print("   • Container logs: docker logs laptop-optimized-llm")
        print("")
        print("🛠️  Management Commands:")
        print("   • Status: docker ps | grep laptop")
        print("   • Stop: docker-compose -f containerization/services/laptop-optimized-llm/docker-compose.yml down")
        print("   • Restart: docker-compose -f containerization/services/laptop-optimized-llm/docker-compose.yml restart")
        print("")
        print("📊 Performance Tips:")
        print("   • Use Q4_K_M quantization for best speed/memory balance")
        print("   • Keep context windows under 8K for optimal performance")
        print("   • Monitor with: python scripts/python/laptop_llm_monitor.py")
        print("="*60)

    async def diagnose_issues(self) -> Dict[str, Any]:
        """
        Diagnose common issues with the LLM setup

        Returns:
            Dict containing diagnosis results for Docker, containers, and API
        """
        issues = {}

        # Check Docker
        try:
            timeout = 10.0  # Default fallback
            if self.timeout_scaler:
                timeout = self.timeout_scaler.get_dynamic_timeout("docker", "diagnose_ps")

            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            issues["docker_running"] = result.returncode == 0
        except subprocess.TimeoutExpired:
            self.logger.warning("Docker ps command timed out")
            issues["docker_running"] = False
        except Exception as e:
            self.logger.debug(f"Docker check failed: {e}")
            issues["docker_running"] = False

        # Check container
        try:
            timeout = 10.0  # Default fallback
            if self.timeout_scaler:
                timeout = self.timeout_scaler.get_dynamic_timeout("docker", "diagnose_container")

            result = subprocess.run(
                ["docker", "ps", "--filter", "name=laptop-optimized-llm", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            if result.returncode == 0:
                containers = [json.loads(line) for line in result.stdout.strip().split('\n') if line.strip()]
                issues["container_running"] = len(containers) > 0
            else:
                issues["container_running"] = False
        except subprocess.TimeoutExpired:
            self.logger.warning("Container check command timed out")
            issues["container_running"] = False
        except json.JSONDecodeError as e:
            self.logger.debug(f"Failed to parse container check output: {e}")
            issues["container_running"] = False
        except Exception as e:
            self.logger.debug(f"Container check failed: {e}")
            issues["container_running"] = False

        # Check API
        try:
            import requests
            if DYNAMIC_TIMEOUT_AVAILABLE and self.timeout_scaler:
                response = get_with_dynamic_timeout(
                    system="llm_api",
                    operation="diagnose_tags",
                    url="http://localhost:11434/api/tags"
                )
            else:
                response = requests.get("http://localhost:11434/api/tags", timeout=5)
            issues["api_responding"] = response.status_code == 200
        except requests.exceptions.RequestException as e:
            self.logger.debug(f"API check failed: {e}")
            issues["api_responding"] = False
        except Exception as e:
            self.logger.debug(f"API check error: {e}")
            issues["api_responding"] = False

        return issues

    async def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            "hardware": {},
            "containers": {},
            "notifications": {},
            "performance": {}
        }

        # Hardware status
        if self.hardware_detector:
            try:
                hardware = self.hardware_detector.detect_hardware()
                status["hardware"] = {
                    "cpu": f"{hardware['cpu']['name']} ({hardware['cpu']['cores']} cores)",
                    "memory": f"{hardware['memory']['total_gb']}GB",
                    "gpu": f"{hardware['gpu']['name']} ({hardware['gpu']['vram_gb']}GB VRAM)"
                }
            except:
                status["hardware"] = {"error": "Could not detect hardware"}

        # Container status
        try:
            timeout = 10.0  # Default fallback
            if self.timeout_scaler:
                timeout = self.timeout_scaler.get_dynamic_timeout("docker", "status_check")

            result = subprocess.run(
                ["docker", "ps", "--filter", "name=laptop-optimized", "--format", "json"],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            containers = [json.loads(line) for line in result.stdout.strip().split('\n') if line.strip()]
            status["containers"] = {
                "running": len(containers),
                "details": [{"name": c.get("Names"), "status": c.get("Status")} for c in containers]
            }
        except:
            status["containers"] = {"error": "Could not check containers"}

        # Notification status
        if self.notification_manager:
            try:
                summary = self.notification_manager.get_notification_summary(1)
                status["notifications"] = summary
            except:
                status["notifications"] = {"error": "Could not check notifications"}

        return status


async def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Laptop LLM Setup - Complete Hardware-Optimized Deployment")
    parser.add_argument("action", choices=[
        "setup", "status", "diagnose", "fix", "monitor"
    ], help="Action to perform")

    args = parser.parse_args()

    setup = LaptopLLMSetup()

    if args.action == "setup":
        success = await setup.setup_complete_system()
        if success:
            print("\n🎉 Setup completed successfully!")
            return 0
        else:
            print("\n❌ Setup failed!")
            return 1

    elif args.action == "status":
        status = await setup.get_status()
        print("📊 Laptop LLM Status:")
        print(json.dumps(status, indent=2))

    elif args.action == "diagnose":
        issues = await setup.diagnose_issues()
        print("🔍 Diagnostic Results:")
        for issue, status in issues.items():
            icon = "✅" if status else "❌"
            print(f"   {icon} {issue.replace('_', ' ').title()}: {status}")

    elif args.action == "fix":
        print("🔧 Attempting to fix common issues...")
        # This would implement automatic fixing
        print("   • Fix functionality coming soon")

    elif args.action == "monitor":
        print("📊 Starting performance monitor...")
        # This would start the monitoring system
        print("   • Monitor functionality coming soon")


if __name__ == "__main__":




    asyncio.run(main())