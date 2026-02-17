#!/usr/bin/env python3
"""
AIOS Service - Docker-native service implementation

Runs AIOS as a service in Docker containers.

Tags: #SERVICE #DOCKER #AIOS @JARVIS @LUMINA
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIOSService")


def run_service():
    """Run AIOS as a service"""
    try:
        from lumina.aios import AIOS
        from fastapi import FastAPI
        import uvicorn

        # Initialize AIOS
        logger.info("🚀 Starting AIOS Service...")
        aios = AIOS()

        # Create FastAPI app
        app = FastAPI(title="AIOS - AI Operating System", version="1.0.0")

        @app.get("/")
        async def root():
            return {
                "service": "AIOS",
                "status": "operational",
                "version": "1.0.0"
            }

        @app.get("/status")
        async def status():
            return aios.get_status()

        @app.post("/execute")
        async def execute(query: dict):
            result = aios.execute(
                query.get("query", ""),
                use_flow=query.get("use_flow", False),
                use_pegl=query.get("use_pegl", False)
            )
            return result

        @app.get("/health")
        async def health():
            status = aios.get_status()
            return {
                "healthy": status.get("initialized", False),
                "status": "operational" if status.get("initialized") else "degraded"
            }

        logger.info("✅ AIOS Service ready")
        logger.info("   API: http://0.0.0.0:8080")
        logger.info("   Health: http://0.0.0.0:8080/health")

        # Run server
        uvicorn.run(app, host="0.0.0.0", port=8080, log_level="info")

    except Exception as e:
        logger.error(f"❌ Service failed: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main service entry point"""
    parser = argparse.ArgumentParser(description="AIOS Service")
    parser.add_argument("--start", action="store_true", help="Start service")
    parser.add_argument("--stop", action="store_true", help="Stop service")
    parser.add_argument("--status", action="store_true", help="Get status")

    args = parser.parse_args()

    if args.start or not any(vars(args).values()):
        run_service()
    elif args.status:
        try:
            from lumina.aios import AIOS
            aios = AIOS()
            status = aios.get_status()
            print(f"Status: {'✅ Operational' if status.get('initialized') else '❌ Not operational'}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)


if __name__ == "__main__":


    main()