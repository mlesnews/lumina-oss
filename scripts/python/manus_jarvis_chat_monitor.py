#!/usr/bin/env python3
"""
MANUS JARVIS Chat Monitor - Video Feed Integration

Uses MANUS desktop video feed to monitor and diagnose JARVIS Chat issues.
Captures visual state and correlates with backend health.

Tags: #MANUS #JARVIS #CHAT #MONITOR #VIDEOFEED @JARVIS @LUMINA
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from manus_rdp_screenshot_capture import MANUSRDPScreenshotCapture

    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ManusJarvisChatMonitor")


class ManusJarvisChatMonitor:
    """
    MANUS-powered monitor for JARVIS Chat system.
    Combines visual feed with backend health checks.
    """

    def __init__(self):
        self.project_root = project_root
        self.cluster_url = "http://localhost:8080"
        self.ollama_url = "http://localhost:11434"

        # MANUS Video Feed (if available)
        if MANUS_AVAILABLE:
            try:
                self.vision = MANUSRDPScreenshotCapture()
                logger.info("🎥 MANUS Video Feed initialized")
            except Exception as e:
                logger.warning(f"⚠️ MANUS Video Feed unavailable: {e}")
                self.vision = None
        else:
            self.vision = None
            logger.warning("⚠️ MANUS not available - text-only monitoring")

        # Status tracking
        self.status_history = []

    async def check_cluster_health(self) -> Dict[str, Any]:
        """Check ULTRON Cluster Router health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.cluster_url}/health", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return {
                            "status": "healthy",
                            "cluster": data.get("cluster", "unknown"),
                            "ultron_health": data.get("ultron_health", 0),
                            "iron_legion_health": data.get("iron_legion_health", 0),
                        }
        except Exception as e:
            logger.debug(f"Cluster health check failed: {e}")
        return {"status": "offline", "error": str(e) if "e" in dir() else "Connection failed"}

    async def check_ollama_health(self) -> Dict[str, Any]:
        """Check direct Ollama health"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.ollama_url}/api/tags", timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m.get("name") for m in data.get("models", [])]
                        return {"status": "healthy", "models": models, "model_count": len(models)}
        except Exception as e:
            logger.debug(f"Ollama health check failed: {e}")
        return {"status": "offline"}

    async def test_chat_endpoint(self) -> Dict[str, Any]:
        """Test the chat completions endpoint"""
        test_payload = {
            "model": "qwen2.5:7b",
            "messages": [{"role": "user", "content": "ping"}],
            "stream": False,
        }

        # Try cluster first
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.cluster_url}/v1/chat/completions", json=test_payload, timeout=30
                ) as resp:
                    if resp.status == 200:
                        return {"status": "working", "endpoint": "cluster"}
                    elif resp.status in [502, 503]:
                        logger.info("Cluster returned 503, trying direct Ollama...")
        except Exception as e:
            logger.debug(f"Cluster chat failed: {e}")

        # Fallback to direct Ollama
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.ollama_url}/v1/chat/completions", json=test_payload, timeout=30
                ) as resp:
                    if resp.status == 200:
                        return {"status": "working", "endpoint": "direct_ollama"}
        except Exception as e:
            logger.debug(f"Direct Ollama chat failed: {e}")

        return {"status": "failed", "endpoint": "none"}

    def capture_video_feed(self, context: str = "JARVIS Chat Monitor") -> Optional[str]:
        """Capture MANUS desktop video feed frame"""
        if not self.vision:
            return None

        try:
            metadata = self.vision.capture_with_context(context, auto_capture=True)
            return metadata.get("screenshot_path")
        except Exception as e:
            logger.warning(f"Video feed capture failed: {e}")
            return None

    async def run_diagnostic(self) -> Dict[str, Any]:
        """Run full diagnostic check"""
        timestamp = datetime.now().isoformat()
        logger.info("=" * 60)
        logger.info("🔍 MANUS JARVIS Chat Diagnostic")
        logger.info("=" * 60)

        # 1. Check cluster health
        logger.info("\n📡 Checking ULTRON Cluster Router...")
        cluster = await self.check_cluster_health()
        if cluster["status"] == "healthy":
            logger.info(f"   ✅ Cluster: {cluster['cluster']}")
            logger.info(f"   📊 ULTRON: {cluster['ultron_health']:.1f}%")
            logger.info(f"   🦾 Iron Legion: {cluster['iron_legion_health']:.1f}%")
        else:
            logger.warning("   ❌ Cluster offline")

        # 2. Check Ollama health
        logger.info("\n🦙 Checking Ollama...")
        ollama = await self.check_ollama_health()
        if ollama["status"] == "healthy":
            logger.info(f"   ✅ Ollama running - {ollama['model_count']} models")
            logger.info(f"   📋 Models: {', '.join(ollama['models'][:5])}...")
        else:
            logger.warning("   ❌ Ollama offline")

        # 3. Test chat endpoint
        logger.info("\n💬 Testing chat endpoint...")
        chat = await self.test_chat_endpoint()
        if chat["status"] == "working":
            logger.info(f"   ✅ Chat working via: {chat['endpoint']}")
        else:
            logger.error("   ❌ Chat endpoint FAILED")

        # 4. Capture video feed (if available)
        screenshot = None
        if self.vision:
            logger.info("\n🎥 Capturing MANUS video feed...")
            screenshot = self.capture_video_feed(f"Diagnostic at {timestamp}")
            if screenshot:
                logger.info(f"   📸 Captured: {screenshot}")

        # Compile result
        result = {
            "timestamp": timestamp,
            "cluster": cluster,
            "ollama": ollama,
            "chat": chat,
            "screenshot": screenshot,
            "overall_status": "healthy" if chat["status"] == "working" else "degraded",
        }

        # Summary
        logger.info("\n" + "=" * 60)
        if result["overall_status"] == "healthy":
            logger.info("✅ JARVIS Chat System: HEALTHY")
        else:
            logger.error("❌ JARVIS Chat System: DEGRADED")
            self._suggest_fixes(result)
        logger.info("=" * 60)

        self.status_history.append(result)
        return result

    def _suggest_fixes(self, result: Dict[str, Any]):
        """Suggest fixes based on diagnostic result"""
        logger.info("\n🔧 Suggested Fixes:")

        if result["ollama"]["status"] == "offline":
            logger.info("   1. Start Ollama: ollama serve")

        if result["cluster"]["status"] == "offline":
            logger.info("   2. Start ULTRON Router:")
            logger.info("      python scripts/python/ultron_cluster_router_api.py")

        if result["chat"]["status"] == "failed":
            logger.info("   3. Reload Cursor IDE to refresh extension")
            logger.info("   4. Check extension logs: Developer Tools > Console")

    async def monitor_loop(self, interval: int = 30):
        """Continuous monitoring loop"""
        logger.info(f"🔄 Starting monitor loop (interval: {interval}s)")
        logger.info("   Press Ctrl+C to stop\n")

        try:
            while True:
                await self.run_diagnostic()
                logger.info(f"\n⏳ Next check in {interval}s...\n")
                await asyncio.sleep(interval)
        except KeyboardInterrupt:
            logger.info("\n🛑 Monitor stopped by user")


async def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS JARVIS Chat Monitor")
    parser.add_argument("--loop", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--interval", type=int, default=30, help="Monitor interval (seconds)")
    args = parser.parse_args()

    monitor = ManusJarvisChatMonitor()

    if args.loop:
        await monitor.monitor_loop(args.interval)
    else:
        await monitor.run_diagnostic()


if __name__ == "__main__":
    asyncio.run(main())
