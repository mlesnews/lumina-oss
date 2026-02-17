#!/usr/bin/env python3
"""
VA.B Monitoring Setup

Sets up comprehensive monitoring for the complete JARVIS ecosystem:
- System metrics (CPU, memory, disk, network)
- Application performance
- AI model usage and costs
- Error tracking and alerting
- Health checks and status monitoring
"""

import json
import os
import subprocess
from pathlib import Path
from datetime import datetime, timedelta

def setup_monitoring_directories():
    try:
        """Create monitoring directories"""
        dirs = ["monitoring", "monitoring/metrics", "monitoring/logs", "monitoring/alerts", "monitoring/dashboards"]
        for dir_name in dirs:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
        print("📁 Created monitoring directories")

    except Exception as e:
        logger.error(f"Error in setup_monitoring_directories: {e}", exc_info=True)
        raise
def create_monitoring_config():
    try:
        """Create monitoring configuration"""
        config = {
            "monitoring": {
                "enabled": True,
                "interval_seconds": 60,
                "retention_days": 30,
                "alerts_enabled": True,
                "dashboard_enabled": True,
                "dashboard_port": 3000
            },
            "metrics": {
                "system": {
                    "cpu": True,
                    "memory": True,
                    "disk": True,
                    "network": True,
                    "temperature": False  # Enable if sensors available
                },
                "application": {
                    "response_time": True,
                    "throughput": True,
                    "error_rate": True,
                    "active_connections": True,
                    "memory_usage": True
                },
                "ai_models": {
                    "requests_per_minute": True,
                    "tokens_used": True,
                    "cost_per_hour": True,
                    "error_rate": True,
                    "average_latency": True
                },
                "jarvis": {
                    "conversations_active": True,
                    "emotional_states": True,
                    "braintrust_decisions": True,
                    "camera_frames_processed": True
                }
            },
            "alerts": {
                "rules": [
                    {
                        "name": "high_cpu_usage",
                        "metric": "system.cpu.usage",
                        "condition": "value > 90",
                        "severity": "critical",
                        "message": "CPU usage is critically high",
                        "action": "log_and_notify"
                    },
                    {
                        "name": "memory_pressure",
                        "metric": "system.memory.usage",
                        "condition": "value > 85",
                        "severity": "warning",
                        "message": "Memory usage is high",
                        "action": "log"
                    },
                    {
                        "name": "api_errors_high",
                        "metric": "application.error_rate",
                        "condition": "value > 5",
                        "severity": "warning",
                        "message": "API error rate is elevated",
                        "action": "log_and_alert"
                    },
                    {
                        "name": "jarvis_unresponsive",
                        "metric": "jarvis.response_time",
                        "condition": "value > 5000",
                        "severity": "critical",
                        "message": "JARVIS is unresponsive",
                        "action": "restart_service"
                    }
                ]
            },
            "health_checks": {
                "endpoints": [
                    {
                        "name": "jarvis_api",
                        "url": "http://localhost:8080/health",
                        "interval": 30,
                        "timeout": 10
                    },
                    {
                        "name": "braintrust_service",
                        "url": "http://localhost:8080/api/v1/braintrust/health",
                        "interval": 60,
                        "timeout": 15
                    },
                    {
                        "name": "ollama_service",
                        "url": "http://localhost:11434/api/tags",
                        "interval": 300,
                        "timeout": 30
                    }
                ]
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "handlers": {
                    "file": {
                        "filename": "monitoring/logs/va_b_monitoring.log",
                        "max_bytes": 10485760,  # 10MB
                        "backup_count": 5
                    },
                    "console": {
                        "enabled": True
                    }
                }
            }
        }

        with open("monitoring/monitoring_config.json", 'w') as f:
            json.dump(config, f, indent=2)

        print("✅ Created monitoring configuration")

    except Exception as e:
        logger.error(f"Error in create_monitoring_config: {e}", exc_info=True)
        raise
def create_dashboard_html():
    """Create monitoring dashboard HTML"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VA.B Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #1a1a2e;
            color: #ffffff;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .metric-card {
            background: linear-gradient(135deg, #16213e 0%, #0f3460 100%);
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .metric-title {
            font-size: 1.2em;
            margin-bottom: 10px;
            color: #00d4ff;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #00ff88;
        }
        .chart-container {
            background: #16213e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-healthy { background-color: #00ff88; }
        .status-warning { background-color: #ffa500; }
        .status-critical { background-color: #ff4444; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 VA.B Monitoring Dashboard</h1>
            <p>Real-time monitoring of the JARVIS ecosystem</p>
            <div id="system-status">
                <span class="status-indicator status-healthy"></span>
                System Status: <span id="status-text">HEALTHY</span>
            </div>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-title">CPU Usage</div>
                <div class="metric-value" id="cpu-usage">0%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Memory Usage</div>
                <div class="metric-value" id="memory-usage">0%</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Active Conversations</div>
                <div class="metric-value" id="active-conversations">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">AI Requests/Min</div>
                <div class="metric-value" id="ai-requests">0</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Total Cost</div>
                <div class="metric-value" id="total-cost">$0.00</div>
            </div>
            <div class="metric-card">
                <div class="metric-title">Braintrust Decisions</div>
                <div class="metric-value" id="braintrust-decisions">0</div>
            </div>
        </div>

        <div class="chart-container">
            <h3>System Performance (Last 24 Hours)</h3>
            <canvas id="performanceChart" width="400" height="200"></canvas>
        </div>

        <div class="chart-container">
            <h3>AI Model Usage</h3>
            <canvas id="modelUsageChart" width="400" height="200"></canvas>
        </div>
    </div>

    <script>
        // Update metrics every 5 seconds
        async function updateMetrics() {
            try {
                const response = await fetch('/api/v1/metrics');
                const data = await response.json();

                // Update metric values
                document.getElementById('cpu-usage').textContent = data.system.cpu + '%';
                document.getElementById('memory-usage').textContent = data.system.memory + '%';
                document.getElementById('active-conversations').textContent = data.jarvis.active_conversations;
                document.getElementById('ai-requests').textContent = data.ai.requests_per_minute;
                document.getElementById('total-cost').textContent = '$' + data.ai.total_cost.toFixed(2);
                document.getElementById('braintrust-decisions').textContent = data.braintrust.decisions_today;

                // Update status indicator
                const statusIndicator = document.querySelector('.status-indicator');
                const statusText = document.getElementById('status-text');

                if (data.system.cpu > 90 || data.system.memory > 90) {
                    statusIndicator.className = 'status-indicator status-critical';
                    statusText.textContent = 'CRITICAL';
                } else if (data.system.cpu > 70 || data.system.memory > 70) {
                    statusIndicator.className = 'status-indicator status-warning';
                    statusText.textContent = 'WARNING';
                } else {
                    statusIndicator.className = 'status-indicator status-healthy';
                    statusText.textContent = 'HEALTHY';
                }

            } catch (error) {
                console.error('Failed to fetch metrics:', error);
            }
        }

        // Initialize charts
        const performanceCtx = document.getElementById('performanceChart').getContext('2d');
        const modelUsageCtx = document.getElementById('modelUsageChart').getContext('2d');

        const performanceChart = new Chart(performanceCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU Usage %',
                    data: [],
                    borderColor: '#00d4ff',
                    tension: 0.1
                }, {
                    label: 'Memory Usage %',
                    data: [],
                    borderColor: '#00ff88',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });

        // Update metrics and charts
        updateMetrics();
        setInterval(updateMetrics, 5000);

        // Update charts every 30 seconds
        setInterval(async () => {
            try {
                const response = await fetch('/api/v1/metrics/history');
                const history = await response.json();

                // Update performance chart
                performanceChart.data.labels = history.timestamps;
                performanceChart.data.datasets[0].data = history.cpu_usage;
                performanceChart.data.datasets[1].data = history.memory_usage;
                performanceChart.update();

            } catch (error) {
                console.error('Failed to fetch history:', error);
            }
        }, 30000);

    </script>
</body>
</html>
"""

    with open("monitoring/dashboards/index.html", 'w') as f:
        f.write(html_content)

    print("✅ Created monitoring dashboard")

def create_health_check_script():
    """Create health check script"""
    script_content = """#!/usr/bin/env python3
import requests
import json
import time
from datetime import datetime

def check_service(name, url, timeout=10):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = (time.time() - start_time) * 1000

        if response.status_code == 200:
            return {
                "name": name,
                "status": "healthy",
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "name": name,
                "status": "unhealthy",
                "status_code": response.status_code,
                "response_time": round(response_time, 2),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "name": name,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

def main():
    try:
        services = [
            ("JARVIS API", "http://localhost:8080/health"),
            ("Braintrust API", "http://localhost:8080/api/v1/braintrust/health"),
            ("Ollama", "http://localhost:11434/api/tags"),
            ("LM Studio", "http://localhost:1234/v1/models")
        ]

        results = []
        for name, url in services:
            result = check_service(name, url)
            results.append(result)
            status_emoji = "✅" if result["status"] == "healthy" else "❌" if result["status"] == "error" else "⚠️"
            print(f"{status_emoji} {name}: {result['status']} ({result.get('response_time', 'N/A')}ms)")

        # Save results
        with open("monitoring/health_check_results.json", 'w') as f:
            json.dump(results, f, indent=2)

    except Exception as e:
        self.logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    main()
"""

    with open("monitoring/health_check.py", 'w') as f:
        f.write(script_content)

    # Make executable
    os.chmod("monitoring/health_check.py", 0o755)

    print("✅ Created health check script")

def create_metrics_collector():
    """Create metrics collection script"""
    script_content = """#!/usr/bin/env python3
import psutil
import json
import time
from datetime import datetime
import requests
import logging
logger = logging.getLogger("setup_monitoring")


def collect_system_metrics():
    return {
        "cpu": {
            "usage": psutil.cpu_percent(interval=1),
            "cores": psutil.cpu_count(),
            "frequency": psutil.cpu_freq().current if psutil.cpu_freq() else None
        },
        "memory": {
            "usage": psutil.virtual_memory().percent,
            "total": psutil.virtual_memory().total,
            "available": psutil.virtual_memory().available
        },
        "disk": {
            "usage": psutil.disk_usage('/').percent,
            "total": psutil.disk_usage('/').total,
            "free": psutil.disk_usage('/').free
        },
        "network": {
            "bytes_sent": psutil.net_io_counters().bytes_sent,
            "bytes_recv": psutil.net_io_counters().bytes_recv
        }
    }

def collect_application_metrics():
    try:
        # Check JARVIS API
        response = requests.get("http://localhost:8080/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass

    # Fallback metrics
    return {
        "response_time": 0,
        "error_rate": 0,
        "active_connections": 0,
        "memory_usage": psutil.Process().memory_percent()
    }

def main():
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "system": collect_system_metrics(),
        "application": collect_application_metrics()
    }

    # Save to file
    with open("monitoring/metrics/current.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    # Append to history (keep last 24 hours)
    history_file = "monitoring/metrics/history.json"
    try:
        with open(history_file, 'r') as f:
            history = json.load(f)
    except:
        history = {"timestamps": [], "cpu_usage": [], "memory_usage": [], "max_entries": 1440}  # 24 hours * 60 minutes

    history["timestamps"].append(metrics["timestamp"])
    history["cpu_usage"].append(metrics["system"]["cpu"]["usage"])
    history["memory_usage"].append(metrics["system"]["memory"]["usage"])

    # Keep only last 1440 entries (24 hours at 1-minute intervals)
    if len(history["timestamps"]) > history["max_entries"]:
        for key in history:
            if key != "max_entries":
                history[key] = history[key][-history["max_entries"]:]

    with open(history_file, 'w') as f:
        json.dump(history, f, indent=2)

    print("✅ Metrics collected and saved")

if __name__ == "__main__":
    main()
"""

    with open("monitoring/metrics_collector.py", 'w') as f:
        f.write(script_content)

    os.chmod("monitoring/metrics_collector.py", 0o755)

    print("✅ Created metrics collector")

def setup_cron_jobs():
    try:
        """Set up cron jobs for automated monitoring"""
        cron_jobs = [
            "*/1 * * * * cd /path/to/lumina && python monitoring/metrics_collector.py",  # Every minute
            "*/5 * * * * cd /path/to/lumina && python monitoring/health_check.py",       # Every 5 minutes
            "0 * * * * cd /path/to/lumina && python scripts/python/backup_system.py"     # Hourly backup
        ]

        # Note: This would need to be adapted for Windows Task Scheduler or actual cron
        with open("monitoring/cron_setup.txt", 'w') as f:
            f.write("# Add these lines to your crontab (Linux/Mac) or Task Scheduler (Windows)\n")
            f.write("# Replace /path/to/lumina with the actual path to your lumina directory\n\n")
            for job in cron_jobs:
                f.write(job + "\n")

        print("✅ Created cron job setup instructions")

    except Exception as e:
        logger.error(f"Error in setup_cron_jobs: {e}", exc_info=True)
        raise
def main():
    """Set up complete monitoring system"""
    print("📊 Setting up VA.B Monitoring System")
    print("="*50)

    # Create directories
    setup_monitoring_directories()

    # Create configuration
    create_monitoring_config()

    # Create dashboard
    create_dashboard_html()

    # Create health check script
    create_health_check_script()

    # Create metrics collector
    create_metrics_collector()

    # Setup automation
    setup_cron_jobs()

    print("\n✅ Monitoring system setup complete!")
    print("📁 Monitoring files created in: monitoring/")
    print("\n🚀 To start monitoring:")
    print("   1. Run: python monitoring/metrics_collector.py")
    print("   2. Run: python monitoring/health_check.py")
    print("   3. Open: monitoring/dashboards/index.html")
    print("   4. Set up automated monitoring using cron_setup.txt")

if __name__ == "__main__":
    main()