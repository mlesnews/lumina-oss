#!/usr/bin/env python3
"""
Check Cluster Status After Delay
Waits 5 minutes then checks Iron Legion cluster status

Tags: #CLUSTER #STATUS #CHECK @JARVIS @LUMINA
"""
import sys
import time
import requests
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("CheckClusterStatusDelayed")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CheckClusterStatusDelayed")


def check_cluster_status():
    """Check Iron Legion cluster status"""
    kaiju_ip = "<NAS_IP>"

    logger.info("=" * 70)
    logger.info("🔍 CHECKING IRON LEGION CLUSTER STATUS")
    logger.info("=" * 70)
    logger.info("")

    status = {
        "main_cluster": False,
        "models": {},
        "timestamp": datetime.now().isoformat()
    }

    # Check main cluster
    logger.info("Checking main cluster router (port 3000)...")
    try:
        response = requests.get(f"http://{kaiju_ip}:3000/health", timeout=5)
        if response.status_code == 200:
            logger.info("✅ Iron Legion main cluster (port 3000) is ONLINE")
            status["main_cluster"] = True
        else:
            logger.warning(f"⚠️  Main cluster error: {response.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning("⚠️  Main cluster (port 3000) is OFFLINE")
    except Exception as e:
        logger.error(f"❌ Error checking main cluster: {e}")

    logger.info("")

    # Check individual models
    logger.info("Checking individual models...")
    for port in range(3001, 3008):
        model_name = f"Mark {port - 3000}"
        model_num = port - 3000
        logger.info(f"  Checking {model_name} (port {port})...")
        try:
            response = requests.get(f"http://{kaiju_ip}:{port}/health", timeout=3)
            if response.status_code == 200:
                logger.info(f"    ✅ {model_name} (port {port}) is ONLINE")
                status["models"][model_name] = True
            else:
                logger.warning(f"    ⚠️  {model_name} (port {port}) error: {response.status_code}")
                status["models"][model_name] = False
        except requests.exceptions.ConnectionError:
            logger.warning(f"    ⚠️  {model_name} (port {port}) is OFFLINE")
            status["models"][model_name] = False
        except Exception as e:
            logger.error(f"    ❌ Error checking {model_name}: {e}")
            status["models"][model_name] = False

    logger.info("")
    logger.info("=" * 70)
    logger.info("📊 SUMMARY")
    logger.info("=" * 70)
    logger.info("")

    if status["main_cluster"]:
        logger.info("✅ Main cluster router: ONLINE")
    else:
        logger.error("❌ Main cluster router: OFFLINE")

    models_online = sum(1 for v in status["models"].values() if v)
    models_total = len(status["models"])
    logger.info(f"📊 Models: {models_online}/{models_total} online")

    if models_online < models_total:
        offline = [name for name, status_val in status["models"].items() if not status_val]
        logger.warning(f"⚠️  Offline models: {', '.join(offline)}")
    else:
        logger.info("✅ All models are online!")

    logger.info("")

    return status


def main():
    try:
        """Main execution"""
        wait_seconds = 300  # 5 minutes

        logger.info("=" * 70)
        logger.info("⏳ WAITING 5 MINUTES BEFORE CHECKING CLUSTER STATUS")
        logger.info("=" * 70)
        logger.info("")
        logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Will check status at: {(datetime.now().timestamp() + wait_seconds):.0f}")
        logger.info("")
        logger.info("Waiting 5 minutes (300 seconds)...")
        logger.info("")

        # Wait in 30-second increments with progress updates
        for i in range(0, wait_seconds, 30):
            remaining = wait_seconds - i
            minutes = remaining // 60
            seconds = remaining % 60
            logger.info(f"  ⏳ {minutes}m {seconds}s remaining...")
            time.sleep(30)

        logger.info("")
        logger.info("✅ Wait complete! Checking cluster status now...")
        logger.info("")

        status = check_cluster_status()

        # Save report
        import json
        report_file = project_root / "data" / "syphon_results" / f"cluster_status_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(json.dumps(status, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    sys.exit(main())