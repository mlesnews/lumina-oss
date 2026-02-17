#!/usr/bin/env python3
"""
Iron Legion Dynamic Router
Dynamic routing system for Iron Legion cluster with job metrics and load balancing

Tags: #IRON_LEGION #ROUTING #DYNAMIC #METRICS @JARVIS @LUMINA @DOIT
"""

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

import requests


@dataclass
class JobMetrics:
    """Job execution metrics"""
    job_id: str
    model: str
    endpoint: str
    start_time: float
    end_time: Optional[float] = None
    tokens_generated: int = 0
    response_time: float = 0.0
    success: bool = False
    error: Optional[str] = None

    @property
    def duration(self) -> float:
        """Get job duration in seconds"""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time


class IronLegionDynamicRouter:
    """Dynamic router for Iron Legion cluster with metrics tracking"""

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize dynamic router"""
        script_dir = Path(__file__).parent
        project_root = script_dir.parent.parent

        if config_path is None:
            config_path = project_root / "config" / "iron_legion_cluster_config.json"

        self.config_path = config_path
        self.config = self._load_config()
        self.base_url = self.config.get("base_url", "http://<NAS_IP>")
        self.ports = self.config.get("ports", [3001, 3002, 3003, 3004, 3005, 3006, 3007])
        self.job_metrics: List[JobMetrics] = []
        self.model_loads: Dict[str, float] = {}

    def _load_config(self) -> Dict:
        """Load configuration"""
        try:
            if self.config_path.exists():
                with open(self.config_path, encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")

        # Default configuration
        return {
            "base_url": "http://<NAS_IP>",
            "ports": [3001, 3002, 3003, 3004, 3005, 3006, 3007],
            "routing_strategy": "round_robin",
            "health_check_interval": 30
        }

    def check_model_health(self, port: int, timeout: int = 3) -> bool:
        """Check if model on port is healthy"""
        try:
            response = requests.get(f"{self.base_url}:{port}/api/tags", timeout=timeout)
            return response.status_code == 200
        except:
            return False

    def get_available_models(self) -> List[int]:
        """Get list of available model ports"""
        available = []
        for port in self.ports:
            if self.check_model_health(port):
                available.append(port)
        return available

    def route_request(self, prompt: str, task_type: Optional[str] = None) -> Dict:
        """Route request to appropriate model"""
        job_id = f"job_{int(time.time() * 1000)}"
        start_time = time.time()

        # Get available models
        available = self.get_available_models()
        if not available:
            return {
                "success": False,
                "error": "No available models",
                "job_id": job_id
            }

        # Select model (round-robin or based on task type)
        selected_port = available[0]  # Simple selection for now
        endpoint = f"{self.base_url}:{selected_port}"

        # Create metrics
        metrics = JobMetrics(
            job_id=job_id,
            model=f"mark-{selected_port - 3000}",
            endpoint=endpoint,
            start_time=start_time
        )

        try:
            # Forward request to model
            response = requests.post(
                f"{endpoint}/api/generate",
                json={"model": "default", "prompt": prompt},
                timeout=60
            )

            metrics.end_time = time.time()
            metrics.response_time = metrics.duration
            metrics.success = response.status_code == 200

            if metrics.success:
                result = response.json()
                metrics.tokens_generated = len(result.get("response", "").split())
                self.job_metrics.append(metrics)

                return {
                    "success": True,
                    "job_id": job_id,
                    "model": metrics.model,
                    "response": result.get("response", ""),
                    "metrics": {
                        "response_time": metrics.response_time,
                        "tokens": metrics.tokens_generated
                    }
                }
            else:
                metrics.error = f"HTTP {response.status_code}"
                self.job_metrics.append(metrics)
                return {
                    "success": False,
                    "error": f"Model returned {response.status_code}",
                    "job_id": job_id
                }

        except Exception as e:
            metrics.end_time = time.time()
            metrics.error = str(e)
            metrics.success = False
            self.job_metrics.append(metrics)

            return {
                "success": False,
                "error": str(e),
                "job_id": job_id
            }

    def get_metrics(self) -> Dict:
        """Get routing metrics"""
        total_jobs = len(self.job_metrics)
        successful = sum(1 for m in self.job_metrics if m.success)
        avg_response_time = sum(m.response_time for m in self.job_metrics) / total_jobs if total_jobs > 0 else 0

        return {
            "total_jobs": total_jobs,
            "successful": successful,
            "failed": total_jobs - successful,
            "average_response_time": avg_response_time,
            "available_models": len(self.get_available_models()),
            "total_models": len(self.ports)
        }
