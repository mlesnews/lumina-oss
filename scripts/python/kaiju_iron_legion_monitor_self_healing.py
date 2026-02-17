#!/usr/bin/env python3
"""
KAIJU Iron Legion Status Monitor with Self-Audit & Self-Healing
Runs as cron job/daemon on NAS scheduler with automatic problem detection and fixing

Features:
- Health monitoring every 30 minutes
- Self-audit: Detects common issues
- Self-healing: Automatically fixes problems
- NAS-based execution via cron
- Logging to NAS centralized logs
"""

import sys
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

# Try to import NAS SSH integration
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_SSH_AVAILABLE = True
except ImportError:
    NAS_SSH_AVAILABLE = False

# Configuration
IRON_LEGION_ENDPOINTS = [
    "http://kaiju_no_8:11437",
    "http://localhost:11437",
    "http://127.0.0.1:11437",
    "http://<NAS_IP>:11437",  # Direct IP if hostname fails
]

IRON_LEGION_MODELS = {
    "codellama:13b": {"mark": "Mark I", "purpose": "Primary code generation"},
    "llama3.2:11b": {"mark": "Mark II", "purpose": "Secondary general"},
    "qwen2.5-coder:1.5b-base": {"mark": "Mark III", "purpose": "Lightweight quick"},
    "llama3": {"mark": "Mark IV", "purpose": "General purpose"},
    "mistral": {"mark": "Mark V", "purpose": "General reasoning"},
    "mixtral-8x7b": {"mark": "Mark VI", "purpose": "High complexity"},
    "gemma-2b": {"mark": "Mark VII", "purpose": "Lightweight fallback"}
}

# NAS Configuration
NAS_LOG_PATH = Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\logs\\iron_legion_monitoring")
NAS_SSH_HOST = "<NAS_PRIMARY_IP>"
NAS_SSH_USER = "backupadm"

# Setup logging
log_dir = project_root.parent / "logs" / "llama3.2:3b"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / f"monitor_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("IronLegionMonitor")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class IronLegionSelfHealer:
    """Self-healing capabilities for Iron Legion"""

    def __init__(self):
        self.healing_actions = []

    def audit_system(self, endpoint: Optional[str], models: List[Dict]) -> Dict[str, Any]:
        """Perform comprehensive system audit"""
        issues = []
        warnings = []
        healthy_items = []

        # 1. Check endpoint connectivity
        if not endpoint:
            issues.append({
                "type": "endpoint_unavailable",
                "severity": "critical",
                "message": "No Iron Legion endpoint responding",
                "suggested_fix": "restart_ollama_service"
            })
        else:
            healthy_items.append(f"Endpoint available: {endpoint}")

        # 2. Check model availability
        available_models = [m.get("name") for m in models]
        expected_models = list(IRON_LEGION_MODELS.keys())
        missing_models = [m for m in expected_models if m not in available_models]

        if missing_models:
            issues.append({
                "type": "missing_models",
                "severity": "warning" if len(missing_models) < 3 else "critical",
                "message": f"Missing {len(missing_models)} models: {', '.join(missing_models)}",
                "missing_models": missing_models,
                "suggested_fix": "pull_missing_models"
            })
        else:
            healthy_items.append(f"All {len(expected_models)} models available")

        # 3. Check model health (sample check on primary model)
        if endpoint and "codellama:13b" in available_models:
            try:
                response = requests.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": "codellama:13b",
                        "prompt": "test",
                        "stream": False,
                        "options": {"num_predict": 5}
                    },
                    timeout=30
                )
                if response.status_code != 200:
                    issues.append({
                        "type": "model_unresponsive",
                        "severity": "critical",
                        "message": "Primary model (codellama:13b) not responding",
                        "suggested_fix": "restart_model_container"
                    })
                else:
                    healthy_items.append("Primary model responding")
            except Exception as e:
                issues.append({
                    "type": "model_health_check_failed",
                    "severity": "warning",
                    "message": f"Health check failed: {e}",
                    "suggested_fix": "verify_service_status"
                })

        # 4. Check disk space (if endpoint available, check via API)
        # This would need NAS SSH access or docker stats

        return {
            "audit_timestamp": datetime.now().isoformat(),
            "issues": issues,
            "warnings": warnings,
            "healthy_items": healthy_items,
            "overall_status": "healthy" if not issues else "degraded" if len(issues) < 3 else "critical"
        }

    def apply_healing(self, audit_result: Dict[str, Any], endpoint: Optional[str]) -> Dict[str, Any]:
        """Apply self-healing fixes based on audit results"""
        healing_results = []

        for issue in audit_result.get("issues", []):
            fix_type = issue.get("suggested_fix")
            issue_type = issue.get("type")

            logger.info(f"🔧 Attempting to fix: {issue_type} using {fix_type}")

            try:
                if fix_type == "restart_ollama_service":
                    result = self._restart_ollama_service()
                    healing_results.append({
                        "issue": issue_type,
                        "action": fix_type,
                        "success": result["success"],
                        "message": result["message"]
                    })

                elif fix_type == "pull_missing_models":
                    missing = issue.get("missing_models", [])
                    result = self._pull_missing_models(missing, endpoint)
                    healing_results.append({
                        "issue": issue_type,
                        "action": fix_type,
                        "success": result["success"],
                        "message": result["message"],
                        "models_pulled": result.get("models_pulled", [])
                    })

                elif fix_type == "restart_model_container":
                    result = self._restart_model_container(endpoint)
                    healing_results.append({
                        "issue": issue_type,
                        "action": fix_type,
                        "success": result["success"],
                        "message": result["message"]
                    })

                elif fix_type == "verify_service_status":
                    result = self._verify_service_status(endpoint)
                    healing_results.append({
                        "issue": issue_type,
                        "action": fix_type,
                        "success": result["success"],
                        "message": result["message"]
                    })
                else:
                    logger.warning(f"Unknown fix type: {fix_type}")

            except Exception as e:
                logger.error(f"Error applying fix {fix_type}: {e}")
                healing_results.append({
                    "issue": issue_type,
                    "action": fix_type,
                    "success": False,
                    "message": f"Error: {e}"
                })

        return {
            "healing_timestamp": datetime.now().isoformat(),
            "actions_attempted": len(healing_results),
            "actions_successful": sum(1 for r in healing_results if r["success"]),
            "results": healing_results
        }

    def _restart_ollama_service(self) -> Dict[str, Any]:
        """Attempt to restart Ollama service"""
        try:
            # Try docker restart if available
            result = subprocess.run(
                ["docker", "ps", "-a", "--filter", "name=ollama", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                containers = result.stdout.strip().split('\n')
                for container in containers:
                    if container:
                        restart_result = subprocess.run(
                            ["docker", "restart", container],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )
                        if restart_result.returncode == 0:
                            logger.info(f"✅ Restarted container: {container}")
                            return {"success": True, "message": f"Restarted {container}"}

            # Try systemd service restart (Linux/NAS)
            result = subprocess.run(
                ["systemctl", "restart", "ollama"],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return {"success": True, "message": "Restarted Ollama service via systemctl"}

            return {"success": False, "message": "Could not restart service (docker/systemctl unavailable)"}

        except Exception as e:
            return {"success": False, "message": f"Error restarting service: {e}"}

    def _pull_missing_models(self, models: List[str], endpoint: Optional[str]) -> Dict[str, Any]:
        """Pull missing models via Ollama API"""
        if not endpoint:
            return {"success": False, "message": "No endpoint available to pull models"}

        pulled = []
        failed = []

        for model in models:
            try:
                logger.info(f"📥 Pulling model: {model}")
                response = requests.post(
                    f"{endpoint}/api/pull",
                    json={"name": model},
                    timeout=300,  # 5 minutes per model
                    stream=True
                )

                if response.status_code == 200:
                    # Stream response
                    for line in response.iter_lines():
                        if line:
                            try:
                                data = json.loads(line)
                                if data.get("status") == "success":
                                    pulled.append(model)
                                    logger.info(f"✅ Successfully pulled: {model}")
                                    break
                            except:
                                pass
                else:
                    failed.append(model)
                    logger.warning(f"❌ Failed to pull {model}: Status {response.status_code}")

            except Exception as e:
                failed.append(model)
                logger.error(f"❌ Error pulling {model}: {e}")

        return {
            "success": len(pulled) > 0,
            "message": f"Pulled {len(pulled)}/{len(models)} models",
            "models_pulled": pulled,
            "models_failed": failed
        }

    def _restart_model_container(self, endpoint: Optional[str]) -> Dict[str, Any]:
        """Restart specific model container"""
        # For Ollama, models are loaded in the same service
        # So we restart the Ollama service
        return self._restart_ollama_service()

    def _verify_service_status(self, endpoint: Optional[str]) -> Dict[str, Any]:
        """Verify service is running and responding"""
        if not endpoint:
            return {"success": False, "message": "No endpoint to verify"}

        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                return {"success": True, "message": "Service is responding"}
            else:
                return {"success": False, "message": f"Service returned status {response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Service not responding: {e}"}


class KAIJUIronLegionMonitorSelfHealing:
    """Monitor with self-audit and self-healing"""

    def __init__(self):
        self.endpoint: Optional[str] = None
        self.healer = IronLegionSelfHealer()
        self.status_log = project_root.parent / "data" / "monitoring" / "kaiju_iron_legion_status.json"
        self.status_log.parent.mkdir(parents=True, exist_ok=True)

    def find_active_endpoint(self) -> Optional[str]:
        """Find active Iron Legion endpoint"""
        for endpoint in IRON_LEGION_ENDPOINTS:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.endpoint = endpoint
                    return endpoint
            except Exception:
                continue
        return None

    def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        if not self.endpoint:
            self.find_active_endpoint()

        if not self.endpoint:
            return []

        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models = []

                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    model_info = {
                        "name": model_name,
                        "size": model.get("size", 0),
                        "modified": model.get("modified_at", ""),
                    }

                    if model_name in IRON_LEGION_MODELS:
                        model_info.update(IRON_LEGION_MODELS[model_name])

                    models.append(model_info)

                return models
        except Exception as e:
            logger.error(f"Error fetching models: {e}")

        return []

    def save_to_nas(self, data: Dict[str, Any], filename: str):
        """Save status to NAS centralized logs"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"iron_legion_status_{timestamp}_{filename}.json"

        # Try NAS SSH first
        if NAS_SSH_AVAILABLE:
            try:
                nas = NASAzureVaultIntegration(nas_ip=NAS_SSH_HOST)
                sftp = nas.get_sftp_client()
                if sftp:
                    remote_path = f"/volume1/backups/MATT_Backups/logs/iron_legion_monitoring/{log_filename}"
                    import tempfile
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                        json.dump(data, tmp, indent=2, default=str)
                        tmp_path = tmp.name
                    try:
                        sftp.put(tmp_path, remote_path)
                        import os
                        os.unlink(tmp_path)
                        logger.info(f"💾 Saved to NAS: {remote_path}")
                        return
                    except Exception as e:
                        logger.warning(f"NAS SFTP failed: {e}")
                        os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"NAS SSH unavailable: {e}")

        # Fallback to local
        try:
            NAS_LOG_PATH.mkdir(parents=True, exist_ok=True)
            log_path = NAS_LOG_PATH / log_filename
            with open(log_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            logger.info(f"💾 Saved locally: {log_path}")
        except Exception as e:
            logger.error(f"Failed to save log: {e}")

    def run_monitoring_cycle(self) -> Dict[str, Any]:
        """Run one complete monitoring cycle with audit and healing"""
        logger.info("=" * 70)
        logger.info("KAIJU IRON LEGION MONITORING CYCLE STARTED")
        logger.info(f"Timestamp: {datetime.now().isoformat()}")
        logger.info("=" * 70)

        # 1. Find endpoint
        endpoint = self.find_active_endpoint()
        logger.info(f"Endpoint: {endpoint if endpoint else 'OFFLINE'}")

        # 2. Get models
        models = self.get_models()
        logger.info(f"Models available: {len(models)}/{len(IRON_LEGION_MODELS)}")

        # 3. Perform audit
        logger.info("🔍 Performing system audit...")
        audit_result = self.healer.audit_system(endpoint, models)
        logger.info(f"Audit status: {audit_result['overall_status']}")
        logger.info(f"Issues found: {len(audit_result['issues'])}")

        # 4. Apply healing if needed
        healing_result = None
        if audit_result.get("issues"):
            logger.info("🔧 Applying self-healing fixes...")
            healing_result = self.healer.apply_healing(audit_result, endpoint)
            logger.info(f"Healing actions: {healing_result['actions_attempted']}")
            logger.info(f"Successful fixes: {healing_result['actions_successful']}")

            # Re-check after healing
            if healing_result['actions_successful'] > 0:
                logger.info("🔍 Re-auditing after healing...")
                endpoint = self.find_active_endpoint()  # Re-check
                models = self.get_models()
                audit_result = self.healer.audit_system(endpoint, models)

        # 5. Build status report
        status = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "status": "online" if endpoint else "offline",
            "models_available": len(models),
            "models_total": len(IRON_LEGION_MODELS),
            "audit": audit_result,
            "healing": healing_result,
            "models": models
        }

        # 6. Save status
        self.save_to_nas(status, "monitor_cycle")
        self._save_local_status(status)

        logger.info("=" * 70)
        logger.info("MONITORING CYCLE COMPLETE")
        logger.info("=" * 70)

        return status

    def _save_local_status(self, status: Dict[str, Any]):
        """Save status to local JSON file"""
        try:
            if self.status_log.exists():
                with open(self.status_log, 'r') as f:
                    log_data = json.load(f)
            else:
                log_data = {"history": []}

            log_data["history"].append({
                "timestamp": datetime.now().isoformat(),
                "status": status
            })
            log_data["history"] = log_data["history"][-48:]  # Keep last 48 (24 hours)
            log_data["last_updated"] = datetime.now().isoformat()
            log_data["current_status"] = status

            with open(self.status_log, 'w') as f:
                json.dump(log_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save local status: {e}")


def main():
    """Main entry point for cron job"""
    monitor = KAIJUIronLegionMonitorSelfHealing()
    status = monitor.run_monitoring_cycle()

    # Exit with error code if critical issues remain
    if status.get("audit", {}).get("overall_status") == "critical":
        sys.exit(1)
    elif status.get("status") == "offline":
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":



    main()