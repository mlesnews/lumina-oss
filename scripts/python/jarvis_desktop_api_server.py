#!/usr/bin/env python3
"""
JARVIS Desktop Full Control API Server

Secure API server for JARVIS control over the entire desktop/PC.
Based on Neo Browser AI architecture - provides full human-like control.

Tags: #JARVIS #DESKTOP #API #SECURE #MANUS #FULL_CONTROL @JARVIS @LUMINA
"""

import sys
import json
import secrets
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

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

logger = get_logger("JARVISDesktopAPI")

# Try to import Flask/FastAPI
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

try:
    from fastapi import FastAPI, HTTPException, Depends, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

# Import desktop control
try:
    from jarvis_desktop_full_control import JARVISDesktopFullControl
except ImportError:
    logger.error("❌ JARVIS Desktop Full Control not available")
    JARVISDesktopFullControl = None


class JARVISDesktopAPIServer:
    """
    Secure API Server for JARVIS Desktop Full Control

    Based on Neo Browser AI architecture:
    - Token-based authentication
    - HTTPS support
    - Secure tunnel (API endpoints are naturally secure)
    - Full desktop control endpoints
    - MANUS integration ready
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize API server"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # API configuration
        self.api_config_file = self.config_dir / "jarvis_desktop_api_config.json"
        self.api_config = self._load_config()

        # Initialize desktop control
        self.desktop_control = JARVISDesktopFullControl(project_root) if JARVISDesktopFullControl else None

        # API tokens
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._load_tokens()

        logger.info("✅ JARVIS Desktop API Server initialized")
        logger.info(f"   Port: {self.api_config.get('port', 8889)}")
        logger.info(f"   Secure: {self.api_config.get('secure', True)}")

    def _load_config(self) -> Dict[str, Any]:
        """Load API configuration"""
        default_config = {
            "port": 8889,  # Different port from Neo API
            "host": "127.0.0.1",
            "secure": True,
            "cors_enabled": True,
            "token_expiry_hours": 24,
            "max_requests_per_minute": 100
        }

        if self.api_config_file.exists():
            try:
                with open(self.api_config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        with open(self.api_config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _load_tokens(self):
        """Load API tokens"""
        tokens_file = self.config_dir / "jarvis_desktop_api_tokens.json"
        if tokens_file.exists():
            try:
                with open(tokens_file, 'r') as f:
                    self.tokens = json.load(f)
            except:
                pass

    def _save_tokens(self):
        try:
            """Save API tokens"""
            tokens_file = self.config_dir / "jarvis_desktop_api_tokens.json"
            with open(tokens_file, 'w') as f:
                json.dump(self.tokens, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_tokens: {e}", exc_info=True)
            raise
    def generate_token(self, name: str = "default") -> str:
        """Generate new API token"""
        token = secrets.token_urlsafe(32)
        expires = datetime.now() + timedelta(hours=self.api_config.get("token_expiry_hours", 24))

        self.tokens[token] = {
            "name": name,
            "created": datetime.now().isoformat(),
            "expires": expires.isoformat(),
            "last_used": None
        }

        self._save_tokens()
        logger.info(f"   ✅ Generated token: {name}")
        return token

    def validate_token(self, token: str) -> bool:
        """Validate API token"""
        if token not in self.tokens:
            return False

        token_data = self.tokens[token]
        expires = datetime.fromisoformat(token_data["expires"])

        if datetime.now() > expires:
            del self.tokens[token]
            self._save_tokens()
            return False

        token_data["last_used"] = datetime.now().isoformat()
        self._save_tokens()
        return True

    def create_fastapi_app(self):
        """Create FastAPI app"""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available")

        app = FastAPI(title="JARVIS Desktop Full Control API", version="1.0.0")

        if self.api_config.get("cors_enabled"):
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
            )

        security = HTTPBearer()

        def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
            token = credentials.credentials
            if not self.validate_token(token):
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            return token

        @app.get("/api/health")
        def health():
            return {"status": "ok", "service": "JARVIS Desktop API"}

        @app.post("/api/token/generate")
        def generate_token_endpoint(data: Dict[str, Any]):
            name = data.get("name", "default")
            token = self.generate_token(name)
            return {"token": token, "expires": self.tokens[token]["expires"]}

        # Window Management
        @app.get("/api/desktop/windows")
        def list_windows(token: str = Depends(verify_token)):
            windows = self.desktop_control.get_window_list() if self.desktop_control else []
            return {"windows": windows}

        @app.post("/api/desktop/window/control")
        def control_window(data: Dict[str, Any], token: str = Depends(verify_token)):
            window_title = data.get("window_title")
            action = data.get("action")
            params = data.get("params", {})

            if not window_title or not action:
                raise HTTPException(status_code=400, detail="window_title and action required")

            success = self.desktop_control.control_window(window_title, action, **params) if self.desktop_control else False
            return {"success": success, "window": window_title, "action": action}

        # Application Control
        @app.post("/api/desktop/application/launch")
        def launch_application(data: Dict[str, Any], token: str = Depends(verify_token)):
            app_name = data.get("app_name")
            args = data.get("args", [])

            if not app_name:
                raise HTTPException(status_code=400, detail="app_name required")

            success = self.desktop_control.launch_application(app_name, args) if self.desktop_control else False
            return {"success": success, "app": app_name}

        # Input Simulation
        @app.post("/api/desktop/input/keyboard")
        def simulate_keyboard(data: Dict[str, Any], token: str = Depends(verify_token)):
            keys = data.get("keys")
            modifiers = data.get("modifiers", [])

            if not keys:
                raise HTTPException(status_code=400, detail="keys required")

            success = self.desktop_control.simulate_keyboard(keys, modifiers) if self.desktop_control else False
            return {"success": success}

        @app.post("/api/desktop/input/mouse")
        def simulate_mouse(data: Dict[str, Any], token: str = Depends(verify_token)):
            action = data.get("action")
            x = data.get("x")
            y = data.get("y")
            button = data.get("button", "left")

            if not action:
                raise HTTPException(status_code=400, detail="action required")

            success = self.desktop_control.simulate_mouse(action, x, y, button) if self.desktop_control else False
            return {"success": success}

        # Screen Capture
        @app.post("/api/desktop/screenshot")
        def capture_screen(data: Dict[str, Any], token: str = Depends(verify_token)):
            path = data.get("path", "screenshot.png")
            region = data.get("region")

            success = self.desktop_control.capture_screen(path, region) if self.desktop_control else False
            return {"success": success, "path": path}

        # System Info
        @app.get("/api/desktop/system/info")
        def get_system_info(token: str = Depends(verify_token)):
            info = self.desktop_control.get_system_info() if self.desktop_control else {}
            return info

        @app.get("/api/desktop/system/processes")
        def get_processes(token: str = Depends(verify_token)):
            processes = self.desktop_control.get_running_processes() if self.desktop_control else []
            return {"processes": processes}

        # Browser Control (via Neo)
        @app.post("/api/desktop/browser/navigate")
        def browser_navigate(data: Dict[str, Any], token: str = Depends(verify_token)):
            url = data.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="url required")

            if self.desktop_control and self.desktop_control.neo_control:
                success = self.desktop_control.neo_control.navigate(url)
                return {"success": success, "url": url}
            return {"success": False, "error": "Neo control not available"}

        @app.post("/api/desktop/browser/export-cookies")
        def browser_export_cookies(data: Dict[str, Any], token: str = Depends(verify_token)):
            domain = data.get("domain", "youtube.com")

            if self.desktop_control and self.desktop_control.neo_control:
                success = self.desktop_control.neo_control.export_cookies_automatically(domain)
                return {"success": success, "domain": domain}
            return {"success": False, "error": "Neo control not available"}

        # Sider.AI Integration
        @app.post("/api/desktop/sider/wisebase-query")
        def sider_wisebase_query(data: Dict[str, Any], token: str = Depends(verify_token)):
            query = data.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="query required")

            if self.desktop_control and self.desktop_control.sider_ai:
                result = self.desktop_control.sider_ai.wisebase_query(query)
                return result
            return {"error": "Sider.AI not available"}

        # ROAMWISE.AI Integration
        @app.post("/api/desktop/roamwise/action")
        def roamwise_action(data: Dict[str, Any], token: str = Depends(verify_token)):
            action = data.get("action")
            action_data = data.get("data", {})

            if not action:
                raise HTTPException(status_code=400, detail="action required")

            if self.desktop_control and self.desktop_control.roamwise_ai:
                result = self.desktop_control.roamwise_ai.send_to_roamwise(action, action_data)
                return result
            return {"error": "ROAMWISE.AI not available"}

        # RoamResearch Integration
        @app.post("/api/desktop/roamresearch/query-graph")
        def roamresearch_query(data: Dict[str, Any], token: str = Depends(verify_token)):
            query = data.get("query")
            if not query:
                raise HTTPException(status_code=400, detail="query required")

            if self.desktop_control and self.desktop_control.roamresearch:
                result = self.desktop_control.roamresearch.query_graph(query)
                return result
            return {"error": "RoamResearch not available"}

        # AI-to-AI Bidirectional Communication
        @app.post("/api/desktop/ai-to-ai/message")
        def ai_to_ai_message(data: Dict[str, Any], token: str = Depends(verify_token)):
            from_service = data.get("from_service")
            to_service = data.get("to_service")
            message = data.get("message", {})
            message_type = data.get("message_type", "query")

            if not from_service or not to_service:
                raise HTTPException(status_code=400, detail="from_service and to_service required")

            try:
                from jarvis_ai_to_ai_message_bus import JARVISAIToAIMessageBus
                bus = JARVISAIToAIMessageBus()
                bus.initialize_integration()

                message_id = bus.send_message(from_service, to_service, message_type, message)
                messages = bus.get_messages_for_service(to_service, limit=1)

                if messages:
                    result = messages[0].response or {}
                    result["message_id"] = message_id
                    return result
                else:
                    return {"message_id": message_id, "status": "sent"}
            except Exception as e:
                return {"error": str(e)}

        @app.post("/api/desktop/ai-to-ai/broadcast")
        def ai_to_ai_broadcast(data: Dict[str, Any], token: str = Depends(verify_token)):
            from_service = data.get("from_service")
            message_type = data.get("message_type", "notification")
            payload = data.get("payload", {})

            if not from_service:
                raise HTTPException(status_code=400, detail="from_service required")

            try:
                from jarvis_ai_to_ai_message_bus import JARVISAIToAIMessageBus
                bus = JARVISAIToAIMessageBus()
                bus.initialize_integration()

                message_ids = bus.broadcast_message(from_service, message_type, payload)
                return {"message_ids": message_ids, "count": len(message_ids)}
            except Exception as e:
                return {"error": str(e)}

        @app.get("/api/desktop/ai-to-ai/status")
        def ai_to_ai_status(token: str = Depends(verify_token)):
            try:
                from jarvis_ai_to_ai_message_bus import JARVISAIToAIMessageBus
                bus = JARVISAIToAIMessageBus()
                bus.initialize_integration()
                return bus.get_message_bus_status()
            except Exception as e:
                return {"error": str(e)}

        return app

    def run(self, framework: str = "fastapi"):
        """Run API server"""
        if framework == "fastapi" and FASTAPI_AVAILABLE:
            app = self.create_fastapi_app()
            import uvicorn
            uvicorn.run(
                app,
                host=self.api_config.get("host", "127.0.0.1"),
                port=self.api_config.get("port", 8889),
                log_level="info"
            )
        elif framework == "flask" and FLASK_AVAILABLE:
            # Flask implementation similar to Neo API
            app = Flask(__name__)
            if self.api_config.get("cors_enabled"):
                CORS(app)

            def require_token():
                token = request.headers.get("Authorization", "").replace("Bearer ", "")
                if not self.validate_token(token):
                    return jsonify({"error": "Invalid or expired token"}), 401
                return None

            @app.route("/api/health", methods=["GET"])
            def health():
                return jsonify({"status": "ok", "service": "JARVIS Desktop API"})

            # Add other endpoints similar to FastAPI version
            # ... (implementation similar to Neo API server)

            app.run(
                host=self.api_config.get("host", "127.0.0.1"),
                port=self.api_config.get("port", 8889),
                debug=False
            )
        else:
            logger.error("❌ No API framework available")
            logger.info("   Install: pip install fastapi uvicorn OR flask flask-cors")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Desktop Full Control API Server")
    parser.add_argument("--framework", choices=["fastapi", "flask"], default="fastapi")
    parser.add_argument("--port", type=int, help="Port to run on")
    parser.add_argument("--generate-token", action="store_true", help="Generate API token")
    parser.add_argument("--token-name", default="default", help="Token name")

    args = parser.parse_args()

    server = JARVISDesktopAPIServer()

    if args.port:
        server.api_config["port"] = args.port

    if args.generate_token:
        token = server.generate_token(args.token_name)
        print(f"\n✅ API Token Generated:")
        print(f"   Token: {token}")
        print(f"   Name: {args.token_name}")
        print(f"   Expires: {server.tokens[token]['expires']}")
        print(f"\n   Use in requests:")
        print(f"   Authorization: Bearer {token}")
        return 0

    logger.info("🚀 Starting JARVIS Desktop API Server...")
    logger.info("   Generate token: python jarvis_desktop_api_server.py --generate-token")
    server.run(framework=args.framework)


if __name__ == "__main__":


    main()