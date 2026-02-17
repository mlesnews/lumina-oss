#!/usr/bin/env python3
"""
Synology API Base Class
Base class for all Synology DSM API interactions with proper SSL certificate handling
#JARVIS #MANUS #NAS #SYNOLOGY #API #SSL #CERTIFICATE
"""

import sys
import requests
from pathlib import Path
from typing import Optional, Dict, Any
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from nas_certificate_manager import NASCertificateManager
    CERT_MANAGER_AVAILABLE = True
except ImportError:
    CERT_MANAGER_AVAILABLE = False

logger = get_logger("SynologyAPIBase")


class SynologyAPIBase:
    """
    Base class for Synology DSM API interactions
    Handles SSL certificate verification for all API calls
    """

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", nas_port: int = 5001, verify_ssl: bool = True):
        """
        Initialize Synology API base

        Args:
            nas_ip: NAS IP address
            nas_port: NAS HTTPS port (default: 5001 for DSM)
            verify_ssl: Whether to verify SSL certificates
        """
        self.nas_ip = nas_ip
        self.nas_port = nas_port
        self.base_url = f"https://{nas_ip}:{nas_port}"
        self.verify_ssl = verify_ssl
        self.sid = None  # Session ID

        # Initialize session with proper SSL handling
        self.session = requests.Session()
        self._setup_ssl_verification()

        logger.info(f"🔌 Synology API Base initialized for {nas_ip}:{nas_port}")

    def _setup_ssl_verification(self) -> None:
        """Setup SSL verification using certificate manager"""
        if not self.verify_ssl:
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings()
            logger.debug("SSL verification disabled by user")
            return

        if not CERT_MANAGER_AVAILABLE:
            logger.warning("Certificate manager not available, disabling SSL verification")
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings()
            return

        try:
            cert_manager = NASCertificateManager()

            # First, try to ensure certificate exists
            cert_path = cert_manager.ensure_certificate(
                self.nas_ip,
                self.nas_port,
                auto_download=True,
                auto_generate=False
            )

            if cert_path and Path(cert_path).exists():
                self.session.verify = cert_path
                logger.info(f"✅ SSL verification enabled with certificate: {cert_path}")
            else:
                # Try to download certificate
                logger.info("📥 Certificate not found, attempting to download...")
                downloaded = cert_manager.download_nas_certificate(self.nas_ip, self.nas_port)

                if downloaded and downloaded.exists():
                    self.session.verify = str(downloaded)
                    logger.info(f"✅ Certificate downloaded and SSL verification enabled: {downloaded}")
                else:
                    logger.warning("⚠️  Could not download certificate, disabling SSL verification")
                    self.session.verify = False
                    import urllib3
                    urllib3.disable_warnings()

        except Exception as e:
            logger.warning(f"⚠️  Error setting up SSL verification: {e}")
            logger.warning("   Falling back to disabled SSL verification")
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings()

    def login(self, username: str, password: str, session_name: str = "DSM") -> bool:
        """
        Login to Synology DSM API

        Args:
            username: DSM username
            password: DSM password
            session_name: Session name (default: "DSM")

        Returns:
            True if login successful
        """
        login_url = f"{self.base_url}/webapi/auth.cgi"

        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": username,
            "passwd": password,
            "session": session_name,
            "format": "sid"
        }

        try:
            # Use session's verify setting (handles certificate path or False)
            response = self.session.get(login_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                logger.info(f"✅ Logged in to Synology DSM API (session: {session_name})")
                return True
            else:
                error = data.get("error", {})
                logger.error(f"❌ Login failed: {error.get('code')} - {error.get('errors')}")
                return False

        except requests.exceptions.SSLError as e:
            logger.error(f"❌ SSL error during login: {e}")
            logger.info("💡 Try downloading certificate:")
            logger.info(f"   python scripts/python/nas_certificate_manager.py --host {self.nas_ip} --port {self.nas_port} --download")
            # Retry with verification disabled
            logger.info("🔄 Retrying with SSL verification disabled...")
            self.session.verify = False
            import urllib3
            urllib3.disable_warnings()
            try:
                response = self.session.get(login_url, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                if data.get("success"):
                    self.sid = data.get("data", {}).get("sid")
                    logger.info(f"✅ Logged in (SSL verification disabled)")
                    return True
            except Exception as retry_e:
                logger.error(f"❌ Retry also failed: {retry_e}")
            return False
        except Exception as e:
            logger.error(f"❌ Error logging in: {e}")
            return False

    def logout(self) -> bool:
        """Logout from Synology DSM API"""
        if not self.sid:
            return True

        logout_url = f"{self.base_url}/webapi/auth.cgi"

        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "logout",
            "session": "DSM",
            "_sid": self.sid
        }

        try:
            response = self.session.get(logout_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                self.sid = None
                logger.info("✅ Logged out from Synology DSM API")
                return True
            else:
                logger.warning("⚠️  Logout may have failed")
                return False

        except Exception as e:
            logger.warning(f"⚠️  Error logging out: {e}")
            return False

    def api_call(self, api: str, method: str, version: str = "1", 
                 params: Optional[Dict[str, Any]] = None, 
                 require_auth: bool = True) -> Optional[Dict[str, Any]]:
        """
        Make a generic API call to Synology DSM

        Args:
            api: API name (e.g., "SYNO.Core.TaskScheduler")
            method: Method name (e.g., "list")
            version: API version (default: "1")
            params: Additional parameters
            require_auth: Whether authentication is required

        Returns:
            API response data or None if failed
        """
        if require_auth and not self.sid:
            logger.error("❌ Not authenticated. Call login() first.")
            return None

        api_url = f"{self.base_url}/webapi/entry.cgi"

        api_params = {
            "api": api,
            "version": version,
            "method": method
        }

        if self.sid:
            api_params["_sid"] = self.sid

        if params:
            api_params.update(params)

        try:
            response = self.session.get(api_url, params=api_params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                return data.get("data")
            else:
                error = data.get("error", {})
                logger.error(f"❌ API call failed: {error.get('code')} - {error.get('errors')}")
                return None

        except requests.exceptions.SSLError as e:
            logger.error(f"❌ SSL error in API call: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ Error in API call: {e}")
            return None

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - logout on exit"""
        self.logout()
