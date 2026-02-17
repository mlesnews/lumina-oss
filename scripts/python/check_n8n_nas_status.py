#!/usr/bin/env python3
"""
Check N8N on NAS Status

Properly checks N8N status on NAS - NEVER ASSUME, ALWAYS CHECK!

Tags: #N8N #NAS #CHECK #VERIFY @JARVIS @LUMINA
"""

import sys
import requests
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("CheckN8NStatus")


def check_n8n_status(nas_ip: str = "<NAS_PRIMARY_IP>", port: int = 5678) -> Dict[str, Any]:
    """Check N8N status on NAS - CHECK EVERYTHING!"""
    logger.info("="*80)
    logger.info("🔍 CHECKING N8N ON NAS STATUS")
    logger.info("="*80)
    logger.info("")

    base_url = f"http://{nas_ip}:{port}"
    results = {
        "nas_ip": nas_ip,
        "port": port,
        "base_url": base_url,
        "accessible": False,
        "endpoints_checked": {},
        "workflows_available": False,
        "api_available": False,
        "version": None,
        "workflow_count": 0
    }

    # Check multiple endpoints
    endpoints_to_check = [
        ("/", "Root"),
        ("/healthz", "Health Check"),
        ("/health", "Health"),
        ("/rest/settings", "Settings"),
        ("/api/v1/workflows", "Workflows API"),
        ("/api/v1/version", "Version API"),
        ("/webhook", "Webhook Base")
    ]

    logger.info("   Checking endpoints...")
    for endpoint, name in endpoints_to_check:
        url = f"{base_url}{endpoint}"
        try:
            response = requests.get(url, timeout=5, allow_redirects=True)
            status = response.status_code
            results["endpoints_checked"][name] = {
                "url": url,
                "status_code": status,
                "accessible": status < 500,
                "content_type": response.headers.get("Content-Type", ""),
                "redirected": len(response.history) > 0
            }

            if status < 500:
                results["accessible"] = True
                logger.info(f"   ✅ {name}: {status} ({url})")
            else:
                logger.info(f"   ❌ {name}: {status} ({url})")

        except requests.exceptions.ConnectionError:
            results["endpoints_checked"][name] = {
                "url": url,
                "status_code": None,
                "accessible": False,
                "error": "Connection refused"
            }
            logger.info(f"   ❌ {name}: Connection refused")
        except requests.exceptions.Timeout:
            results["endpoints_checked"][name] = {
                "url": url,
                "status_code": None,
                "accessible": False,
                "error": "Timeout"
            }
            logger.info(f"   ❌ {name}: Timeout")
        except Exception as e:
            results["endpoints_checked"][name] = {
                "url": url,
                "status_code": None,
                "accessible": False,
                "error": str(e)
            }
            logger.info(f"   ❌ {name}: {e}")

    logger.info("")

    # Try to get workflows if API is accessible
    if results["accessible"]:
        workflows_url = f"{base_url}/api/v1/workflows"
        try:
            response = requests.get(workflows_url, timeout=5)
            if response.status_code == 200:
                workflows = response.json()
                results["workflows_available"] = True
                results["api_available"] = True
                results["workflow_count"] = len(workflows.get("data", []))
                logger.info(f"   ✅ Workflows API accessible: {results['workflow_count']} workflows found")
            elif response.status_code == 401:
                logger.info("   ⚠️  Workflows API requires authentication")
                results["api_available"] = True  # API exists, just needs auth
            else:
                logger.info(f"   ⚠️  Workflows API returned: {response.status_code}")
        except Exception as e:
            logger.debug(f"   Could not fetch workflows: {e}")

        # Try to get version
        version_url = f"{base_url}/api/v1/version"
        try:
            response = requests.get(version_url, timeout=5)
            if response.status_code == 200:
                version_data = response.json()
                results["version"] = version_data.get("version", "Unknown")
                logger.info(f"   ✅ N8N Version: {results['version']}")
        except Exception as e:
            logger.debug(f"   Could not fetch version: {e}")

    # Summary
    logger.info("")
    logger.info("="*80)
    logger.info("📊 N8N STATUS SUMMARY")
    logger.info("="*80)
    logger.info(f"   Base URL: {base_url}")
    logger.info(f"   Accessible: {'✅ YES' if results['accessible'] else '❌ NO'}")
    if results["version"]:
        logger.info(f"   Version: {results['version']}")
    if results["workflows_available"]:
        logger.info(f"   Workflows: {results['workflow_count']} available")
    logger.info(f"   API Available: {'✅ YES' if results['api_available'] else '❌ NO'}")
    logger.info("")

    return results


def main():
    """Main execution"""
    results = check_n8n_status()

    # Return exit code based on accessibility
    if results["accessible"]:
        return 0
    else:
        logger.error("   ❌ N8N is not accessible - check network connection and N8N status")
        return 1


if __name__ == "__main__":


    exit(main())