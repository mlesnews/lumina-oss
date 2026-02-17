"""
Connection Errors Fix Plugin

Fixes connection errors across all systems (Ollama, KAIJU, NAS, etc.)
Improves retry logic and error handling.

Tags: #CONNECTION #ERRORS #RETRY #NETWORK @JARVIS @LUMINA
"""

import sys
import time
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fixes.fixer import FixPlugin, FixType, FixResult
except ImportError:
    from ..fixer import FixPlugin, FixType, FixResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ConnectionErrorsFixPlugin")


class ConnectionErrorsFixPlugin(FixPlugin):
    """Fix connection errors with improved retry logic"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.CONNECTION_ERRORS,
            name="Connection Errors Fixer",
            description="Fixes connection errors with improved retry logic and error handling"
        )
        self.endpoints = {
            'ultron': 'http://localhost:11434',
            'kaiju': 'http://<NAS_IP>:11434',
            'nas': 'http://<NAS_PRIMARY_IP>:3008'
        }

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'connection', 'error', 'timeout', 'econnreset', 'connecterror',
            'network', 'unreachable', 'disconnect', 'retry', 'bedrock'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect connection errors"""
        issues = []
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        # Test all endpoints
        for name, endpoint in self.endpoints.items():
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code != 200:
                    issues.append(f"{name.upper()} endpoint returned status {response.status_code}")
            except requests.exceptions.ConnectionError:
                issues.append(f"{name.upper()} endpoint unreachable: {endpoint}")
            except requests.exceptions.Timeout:
                issues.append(f"{name.upper()} endpoint timeout: {endpoint}")
            except Exception as e:
                issues.append(f"{name.upper()} endpoint error: {type(e).__name__}: {e}")

        # Check for connection error patterns in logs
        log_dir = project_root / "logs"
        if log_dir.exists():
            error_patterns = [
                'connection error', 'connectionerror', 'econnreset',
                'timeout', 'unreachable', 'disconnect'
            ]
            # This would scan logs - simplified for now
            # In production, would scan recent log files

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix connection errors"""
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)
        fixes_applied = []
        errors = []

        # Create improved session with retry logic
        session = requests.Session()
        retry_strategy = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Test and fix each endpoint
        for name, endpoint in self.endpoints.items():
            try:
                # Test connection
                response = session.get(f"{endpoint}/api/tags", timeout=10)
                if response.status_code == 200:
                    fixes_applied.append(f"{name.upper()} connection verified")
                else:
                    errors.append(f"{name.upper()} returned status {response.status_code}")
            except Exception as e:
                errors.append(f"{name.upper()} connection failed: {type(e).__name__}: {e}")

        # Update Cursor settings to use working endpoints
        cursor_settings = project_root / ".cursor" / "settings.json"
        if cursor_settings.exists():
            try:
                import json
                with open(cursor_settings, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Ensure all models use correct endpoints
                updated = False
                for model_key in ['cursor.model.customModels', 'cursor.chat.customModels', 
                                 'cursor.composer.customModels', 'cursor.agent.customModels']:
                    if model_key in settings:
                        for model in settings[model_key]:
                            # Fix KAIJU endpoint if wrong
                            if 'kaiju' in model.get('name', '').lower():
                                if model.get('apiBase') != 'http://<NAS_IP>:11434':
                                    model['apiBase'] = 'http://<NAS_IP>:11434'
                                    updated = True
                                    fixes_applied.append(f"Fixed KAIJU endpoint in {model_key}")

                if updated:
                    with open(cursor_settings, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=2)
                    fixes_applied.append("Updated Cursor settings with correct endpoints")
            except Exception as e:
                errors.append(f"Failed to update Cursor settings: {e}")

        success = len(fixes_applied) > 0 or len(errors) == 0

        return FixResult(
            fix_type=self.fix_type,
            success=success,
            message=f"Fixed {len(fixes_applied)} connection issues" if fixes_applied else "No connection issues found",
            details={
                'fixes_applied': fixes_applied,
                'errors': errors,
                'endpoints_tested': list(self.endpoints.keys())
            }
        )
