#!/usr/bin/env python3
"""
JARVIS Neo Browser API Server

Secure API server for JARVIS control over Neo Browser.
Uses HTTPS with authentication tokens.

Tags: #JARVIS #NEO #API #SECURE #TUNNEL @JARVIS @LUMINA
"""

import sys
import json
import time
import secrets
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hmac

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

logger = get_logger("JARVISNeoAPI")

# Try to import Flask/FastAPI for API server
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    logger.warning("⚠️  Flask not available - install: pip install flask flask-cors")

try:
    from fastapi import FastAPI, HTTPException, Depends, Security
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    from fastapi.middleware.cors import CORSMiddleware
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    logger.warning("⚠️  FastAPI not available - install: pip install fastapi uvicorn")

# Import JARVIS Neo control
try:
    from jarvis_neo_full_control import JARVISNeoFullControl
except ImportError:
    logger.error("❌ JARVIS Neo Full Control not available")
    JARVISNeoFullControl = None


class JARVISNeoAPIServer:
    """
    Secure API Server for JARVIS Neo Browser Control

    Features:
    - Token-based authentication
    - HTTPS support (via reverse proxy or SSL)
    - Secure tunnel (API endpoints are naturally secure)
    - Full JARVIS control endpoints
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize API server"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # API configuration
        self.api_config_file = self.config_dir / "jarvis_neo_api_config.json"
        self.api_config = self._load_config()

        # Initialize JARVIS control
        self.jarvis_control = JARVISNeoFullControl(project_root) if JARVISNeoFullControl else None

        # API tokens (in production, use proper token storage)
        self.tokens: Dict[str, Dict[str, Any]] = {}
        self._load_tokens()

        logger.info("✅ JARVIS Neo API Server initialized")
        logger.info(f"   Port: {self.api_config.get('port', 8888)}")
        logger.info(f"   Secure: {self.api_config.get('secure', True)}")

    def _load_config(self) -> Dict[str, Any]:
        """Load API configuration"""
        default_config = {
            "port": 8888,
            "host": "127.0.0.1",  # Localhost by default (secure)
            "secure": True,
            "cors_enabled": True,
            "token_expiry_hours": 24,
            "max_requests_per_minute": 60
        }

        if self.api_config_file.exists():
            try:
                with open(self.api_config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load config: {e}")

        # Save default config
        with open(self.api_config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def _load_tokens(self):
        """Load API tokens"""
        tokens_file = self.config_dir / "jarvis_neo_api_tokens.json"
        if tokens_file.exists():
            try:
                with open(tokens_file, 'r') as f:
                    self.tokens = json.load(f)
            except:
                pass

    def _save_tokens(self):
        try:
            """Save API tokens"""
            tokens_file = self.config_dir / "jarvis_neo_api_tokens.json"
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
            # Token expired
            del self.tokens[token]
            self._save_tokens()
            return False

        # Update last used
        token_data["last_used"] = datetime.now().isoformat()
        self._save_tokens()
        return True

    def create_flask_app(self):
        """Create Flask API app"""
        if not FLASK_AVAILABLE:
            raise ImportError("Flask not available")

        app = Flask(__name__)

        if self.api_config.get("cors_enabled"):
            CORS(app)

        def require_token():
            """Require valid token"""
            token = request.headers.get("Authorization", "").replace("Bearer ", "")
            if not self.validate_token(token):
                return jsonify({"error": "Invalid or expired token"}), 401
            return None

        @app.route("/api/health", methods=["GET"])
        def health():
            return jsonify({"status": "ok", "service": "JARVIS Neo API"})

        @app.route("/api/token/generate", methods=["POST"])
        def generate_token_endpoint():
            data = request.get_json() or {}
            name = data.get("name", "default")
            token = self.generate_token(name)
            return jsonify({"token": token, "expires": self.tokens[token]["expires"]})

        @app.route("/api/neo/navigate", methods=["POST"])
        def navigate():
            auth_error = require_token()
            if auth_error:
                return auth_error

            data = request.get_json()
            url = data.get("url")
            if not url:
                return jsonify({"error": "URL required"}), 400

            success = self.jarvis_control.navigate(url) if self.jarvis_control else False
            return jsonify({"success": success, "url": url})

        @app.route("/api/neo/click", methods=["POST"])
        def click():
            auth_error = require_token()
            if auth_error:
                return auth_error

            data = request.get_json()
            selector = data.get("selector")
            if not selector:
                return jsonify({"error": "Selector required"}), 400

            success = self.jarvis_control.click(selector) if self.jarvis_control else False
            return jsonify({"success": success})

        @app.route("/api/neo/fill", methods=["POST"])
        def fill():
            auth_error = require_token()
            if auth_error:
                return auth_error

            data = request.get_json()
            selector = data.get("selector")
            text = data.get("text")
            if not selector or not text:
                return jsonify({"error": "Selector and text required"}), 400

            success = self.jarvis_control.fill(selector, text) if self.jarvis_control else False
            return jsonify({"success": success})

        @app.route("/api/neo/export-cookies", methods=["POST"])
        def export_cookies():
            auth_error = require_token()
            if auth_error:
                return auth_error

            data = request.get_json() or {}
            domain = data.get("domain", "youtube.com")

            success = self.jarvis_control.export_cookies_automatically(domain) if self.jarvis_control else False
            return jsonify({"success": success, "domain": domain})

        @app.route("/api/neo/info", methods=["GET"])
        def info():
            auth_error = require_token()
            if auth_error:
                return auth_error

            info = self.jarvis_control.get_page_info() if self.jarvis_control else {}
            return jsonify(info)

        return app

    def create_fastapi_app(self):
        """Create FastAPI app"""
        if not FASTAPI_AVAILABLE:
            raise ImportError("FastAPI not available")

        app = FastAPI(title="JARVIS Neo Browser API", version="1.0.0")

        if self.api_config.get("cors_enabled"):
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],  # Configure appropriately
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
            return {"status": "ok", "service": "JARVIS Neo API"}

        @app.post("/api/token/generate")
        def generate_token_endpoint(data: Dict[str, Any]):
            name = data.get("name", "default")
            token = self.generate_token(name)
            return {"token": token, "expires": self.tokens[token]["expires"]}

        @app.post("/api/neo/navigate")
        def navigate(data: Dict[str, Any], token: str = Depends(verify_token)):
            url = data.get("url")
            if not url:
                raise HTTPException(status_code=400, detail="URL required")

            success = self.jarvis_control.navigate(url) if self.jarvis_control else False
            return {"success": success, "url": url}

        @app.post("/api/neo/click")
        def click(data: Dict[str, Any], token: str = Depends(verify_token)):
            selector = data.get("selector")
            if not selector:
                raise HTTPException(status_code=400, detail="Selector required")

            success = self.jarvis_control.click(selector) if self.jarvis_control else False
            return {"success": success}

        @app.post("/api/neo/fill")
        def fill(data: Dict[str, Any], token: str = Depends(verify_token)):
            selector = data.get("selector")
            text = data.get("text")
            if not selector or not text:
                raise HTTPException(status_code=400, detail="Selector and text required")

            success = self.jarvis_control.fill(selector, text) if self.jarvis_control else False
            return {"success": success}

        @app.post("/api/neo/export-cookies")
        def export_cookies(data: Dict[str, Any] = {}, token: str = Depends(verify_token)):
            domain = data.get("domain", "youtube.com")
            success = self.jarvis_control.export_cookies_automatically(domain) if self.jarvis_control else False
            return {"success": success, "domain": domain}

        @app.get("/api/neo/info")
        def info(token: str = Depends(verify_token)):
            info = self.jarvis_control.get_page_info() if self.jarvis_control else {}
            return info

        return app

    def run(self, framework: str = "fastapi"):
        """Run API server"""
        if framework == "fastapi" and FASTAPI_AVAILABLE:
            app = self.create_fastapi_app()
            import uvicorn
            uvicorn.run(
                app,
                host=self.api_config.get("host", "127.0.0.1"),
                port=self.api_config.get("port", 8888),
                log_level="info"
            )
        elif framework == "flask" and FLASK_AVAILABLE:
            app = self.create_flask_app()
            app.run(
                host=self.api_config.get("host", "127.0.0.1"),
                port=self.api_config.get("port", 8888),
                debug=False
            )
        else:
            logger.error("❌ No API framework available")
            logger.info("   Install: pip install fastapi uvicorn OR flask flask-cors")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Neo Browser API Server")
    parser.add_argument("--framework", choices=["fastapi", "flask"], default="fastapi",
                       help="API framework to use")
    parser.add_argument("--port", type=int, help="Port to run on")
    parser.add_argument("--generate-token", action="store_true", help="Generate API token")
    parser.add_argument("--token-name", default="default", help="Token name")

    args = parser.parse_args()

    server = JARVISNeoAPIServer()

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

    logger.info("🚀 Starting JARVIS Neo API Server...")
    logger.info("   Generate token: python jarvis_neo_api_server.py --generate-token")
    server.run(framework=args.framework)


if __name__ == "__main__":


    main()