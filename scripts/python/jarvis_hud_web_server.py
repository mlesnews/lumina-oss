#!/usr/bin/env python3
"""
JARVIS HUD Web Server

Serves HUD interface and provides API/WebSocket for real-time updates:
- Serves HTML/CSS/JS for HUD display
- REST API for HUD data
- WebSocket for real-time updates
- Mobile and desktop support

Tags: #JARVIS #HUD #WEB_SERVER #API #WEBSOCKET @JARVIS @LUMINA @PEAK @DTN
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_hud_system import JARVISHUDSystem
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    logger = get_logger("JARVISHUDWebServer")
    logger.warning(f"Some imports not available: {e}")
    JARVISHUDSystem = None

logger = get_logger("JARVISHUDWebServer")


class HUDRequestHandler(BaseHTTPRequestHandler):
    """HTTP request handler for HUD web server"""

    def __init__(self, *args, hud_system=None, **kwargs):
        self.hud_system = hud_system
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        # Serve static files
        if path == '/' or path == '/index.html':
            self.serve_file('web/jarvis_hud/index.html', 'text/html')
        elif path == '/styles.css':
            self.serve_file('web/jarvis_hud/styles.css', 'text/css')
        elif path == '/hud.js':
            self.serve_file('web/jarvis_hud/hud.js', 'application/javascript')

        # API endpoints
        elif path == '/api/hud/status':
            self.serve_json(self.hud_system.get_hud_status() if self.hud_system else {})
        elif path == '/api/hud/data':
            self.serve_json(self.hud_system.generate_hud_data() if self.hud_system else {})
        else:
            self.send_error(404)

    def serve_file(self, file_path: str, content_type: str):
        """Serve static file"""
        # Get project root from hud_system or use default
        if self.hud_system:
            project_root = self.hud_system.project_root
        else:
            project_root = Path(__file__).parent.parent.parent

        full_path = project_root / file_path

        if full_path.exists():
            try:
                with open(full_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', len(content))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(content)
            except Exception as e:
                logger.error(f"Error serving file {file_path}: {e}")
                self.send_error(500)
        else:
            logger.warning(f"File not found: {full_path}")
            self.send_error(404)

    def serve_json(self, data: Dict[str, Any]):
        try:
            """Serve JSON response"""
            content = json.dumps(data, indent=2, default=str).encode('utf-8')

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            self.logger.error(f"Error in serve_json: {e}", exc_info=True)
            raise
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.debug(f"{self.address_string()} - {format % args}")


class JARVISHUDWebServer:
    """
    JARVIS HUD Web Server

    Serves HUD interface and provides API for real-time updates
    """

    def __init__(self, project_root: Optional[Path] = None, port: int = 8080):
        """Initialize HUD web server"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.port = port
        self.server = None
        self.server_thread = None

        # Initialize HUD system
        if JARVISHUDSystem:
            self.hud_system = JARVISHUDSystem(project_root=project_root)
        else:
            self.hud_system = None
            logger.warning("HUD System not available")

        logger.info("✅ JARVIS HUD Web Server initialized")
        logger.info(f"   Port: {port}")
        logger.info(f"   HUD System: {'✅' if self.hud_system else '❌'}")

    def start(self):
        """Start web server"""
        def handler(*args, **kwargs):
            return HUDRequestHandler(*args, hud_system=self.hud_system, **kwargs)

        self.server = HTTPServer(('0.0.0.0', self.port), handler)

        def run_server():
            logger.info(f"🚀 HUD Web Server starting on port {self.port}")
            logger.info(f"   Access at: http://localhost:{self.port}")
            self.server.serve_forever()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        logger.info("✅ HUD Web Server started")

    def stop(self):
        """Stop web server"""
        if self.server:
            self.server.shutdown()
            logger.info("✅ HUD Web Server stopped")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS HUD Web Server")
    parser.add_argument("--port", type=int, default=8080, help="Server port")
    parser.add_argument("--start", action="store_true", help="Start server")

    args = parser.parse_args()

    server = JARVISHUDWebServer(port=args.port)

    if args.start:
        server.start()
        try:
            # Keep running
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            server.stop()
    else:
        parser.print_help()


if __name__ == "__main__":


    main()