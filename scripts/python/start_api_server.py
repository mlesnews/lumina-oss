#!/usr/bin/env python3
"""
Start API Server
Convenience script to start the JARVIS Master Agent API server

Usage:
    python scripts/python/start_api_server.py
    python scripts/python/start_api_server.py --port 8000
    python scripts/python/start_api_server.py --host 0.0.0.0 --port 8000
"""

import sys
import argparse
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import uvicorn
    from jarvis_master_agent_api_server import app
    SERVER_AVAILABLE = True
except ImportError:
    SERVER_AVAILABLE = False
    print("ERROR: FastAPI/uvicorn not available. Install with: pip install fastapi uvicorn")

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartAPIServer")


def main():
    """Start the API server"""
    parser = argparse.ArgumentParser(description="Start JARVIS Master Agent API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload (development)")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")

    args = parser.parse_args()

    if not SERVER_AVAILABLE:
        print("ERROR: Cannot start server - dependencies not available")
        sys.exit(1)

    print("=" * 60)
    print("JARVIS Master Agent API Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers}")
    print(f"Project Root: {project_root}")
    print("=" * 60)
    print("\nStarting server...")
    print(f"API Documentation: http://{args.host}:{args.port}/api/docs")
    print(f"ReDoc Documentation: http://{args.host}:{args.port}/api/redoc")
    print("\nPress Ctrl+C to stop")
    print("=" * 60)

    uvicorn.run(
        "jarvis_master_agent_api_server:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1,
        log_level="info"
    )


if __name__ == "__main__":


    main()