#!/usr/bin/env python3
"""
Test JARVIS Neo API Server

Tests the API server endpoints and functionality.

Tags: #JARVIS #NEO #API #TEST @JARVIS @LUMINA
"""

import sys
import requests
import json
from pathlib import Path
from typing import Optional

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

logger = get_logger("TestJARVISNeoAPI")


def test_api_server(base_url: str = "http://127.0.0.1:8888", token: Optional[str] = None):
    """Test API server endpoints"""
    logger.info("=" * 80)
    logger.info("🧪 Testing JARVIS Neo API Server")
    logger.info("=" * 80)
    logger.info("")

    # Test 1: Health check
    logger.info("1️⃣  Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/api/health", timeout=5)
        if response.status_code == 200:
            logger.info("   ✅ Health check passed")
            logger.info(f"   Response: {response.json()}")
        else:
            logger.error(f"   ❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ Cannot connect to API server")
        logger.info("   💡 Start server: python scripts/python/jarvis_neo_api_server.py")
        return False
    except Exception as e:
        logger.error(f"   ❌ Health check error: {e}")
        return False

    logger.info("")

    # Test 2: Generate token (if not provided)
    if not token:
        logger.info("2️⃣  Generating API Token...")
        try:
            response = requests.post(
                f"{base_url}/api/token/generate",
                json={"name": "test-token"},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                logger.info("   ✅ Token generated")
                logger.info(f"   Token: {token[:20]}...")
                logger.info(f"   Expires: {data.get('expires')}")
            else:
                logger.error(f"   ❌ Token generation failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"   ❌ Token generation error: {e}")
            return False
    else:
        logger.info("2️⃣  Using provided token...")
        logger.info(f"   Token: {token[:20]}...")

    logger.info("")

    # Test 3: Export cookies (requires token)
    logger.info("3️⃣  Testing Cookie Export...")
    try:
        response = requests.post(
            f"{base_url}/api/neo/export-cookies",
            headers={"Authorization": f"Bearer {token}"},
            json={"domain": "youtube.com"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            logger.info("   ✅ Cookie export request successful")
            logger.info(f"   Response: {data}")
        else:
            logger.warning(f"   ⚠️  Cookie export returned: {response.status_code}")
            logger.warning(f"   Response: {response.text}")
    except Exception as e:
        logger.error(f"   ❌ Cookie export error: {e}")

    logger.info("")

    # Test 4: Navigate (requires token)
    logger.info("4️⃣  Testing Navigate...")
    try:
        response = requests.post(
            f"{base_url}/api/neo/navigate",
            headers={"Authorization": f"Bearer {token}"},
            json={"url": "https://www.google.com"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            logger.info("   ✅ Navigate request successful")
            logger.info(f"   Response: {data}")
        else:
            logger.warning(f"   ⚠️  Navigate returned: {response.status_code}")
    except Exception as e:
        logger.error(f"   ❌ Navigate error: {e}")

    logger.info("")

    # Test 5: Get page info (requires token)
    logger.info("5️⃣  Testing Get Page Info...")
    try:
        response = requests.get(
            f"{base_url}/api/neo/info",
            headers={"Authorization": f"Bearer {token}"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            logger.info("   ✅ Get page info successful")
            logger.info(f"   Response: {json.dumps(data, indent=2)}")
        else:
            logger.warning(f"   ⚠️  Get page info returned: {response.status_code}")
    except Exception as e:
        logger.error(f"   ❌ Get page info error: {e}")

    logger.info("")
    logger.info("=" * 80)
    logger.info("✅ API Testing Complete")
    logger.info("=" * 80)

    return True


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test JARVIS Neo API Server")
    parser.add_argument("--url", default="http://127.0.0.1:8888", help="API server URL")
    parser.add_argument("--token", help="API token (if not provided, will generate)")

    args = parser.parse_args()

    test_api_server(base_url=args.url, token=args.token)


if __name__ == "__main__":


    main()