#!/usr/bin/env python3
"""
AI Connection Layer for AIOS

Unified interface to connect AIOS to all AI services:
- Local AI (Ollama - ULTRON, KAIJU)
- Cloud AI (Bedrock, OpenAI, Anthropic)

Tags: #AI_CONNECTION #AIOS #OLLAMA #BEDROCK @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
import requests
import json
import sys
import os
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

logger = get_logger("AIConnection")


class OllamaConnection:
    """Connection to Ollama (Local AI)"""

    def __init__(self, url: str, name: str = "ollama"):
        """
        Initialize Ollama connection.

        Args:
            url: Ollama server URL
            name: Connection name
        """
        self.url = url.rstrip('/')
        self.name = name
        self.available = False
        self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Ollama is available"""
        try:
            # Increased timeout for Docker network latency
            response = requests.get(f"{self.url}/api/tags", timeout=5)
            self.available = response.status_code == 200
            if self.available:
                logger.info(f"✅ {self.name} (Ollama) available at {self.url}")
            return self.available
        except Exception as e:
            logger.debug(f"{self.name} (Ollama) not available: {e}")
            self.available = False
            return False

    def is_available(self) -> bool:
        """Check if connection is available"""
        return self.available

    def infer(
        self,
        query: str,
        model: str = "llama2",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute inference through Ollama.

        Args:
            query: Query to infer
            model: Model to use
            **kwargs: Additional parameters

        Returns:
            Inference result
        """
        if not self.available:
            return {'error': f'{self.name} not available'}

        try:
            payload = {
                'model': model,
                'prompt': query,
                'stream': False,
                **kwargs
            }

            response = requests.post(
                f"{self.url}/api/generate",
                json=payload,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'response': result.get('response', ''),
                    'model': model,
                    'source': self.name
                }
            else:
                return {
                    'error': f'Request failed: {response.status_code}',
                    'source': self.name
                }
        except Exception as e:
            logger.error(f"Error with {self.name}: {e}")
            return {
                'error': str(e),
                'source': self.name
            }


class CloudAIConnection:
    """Connection to Cloud AI services"""

    def __init__(self):
        """Initialize cloud AI connections"""
        self.bedrock_available = False
        self.openai_available = False
        self.anthropic_available = False
        self._check_availability()

    def _check_availability(self):
        """Check cloud AI availability"""
        # Check for environment variables or config files
        # Bedrock
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_REGION"):
            self.bedrock_available = True
            logger.info("✅ AWS Bedrock configured (via environment)")

        # Azure OpenAI
        if os.getenv("AZURE_OPENAI_API_KEY") or os.getenv("AZURE_OPENAI_ENDPOINT"):
            self.openai_available = True
            logger.info("✅ Azure OpenAI configured (via environment)")

        # Anthropic (direct)
        if os.getenv("ANTHROPIC_API_KEY"):
            self.anthropic_available = True
            logger.info("✅ Anthropic API configured (via environment)")

    def infer(
        self,
        query: str,
        service: str = "bedrock",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute inference through cloud AI.

        Args:
            query: Query to infer
            service: Service to use (bedrock, openai)
            **kwargs: Additional parameters

        Returns:
            Inference result
        """
        if service == "bedrock" and not self.bedrock_available:
            return {'error': 'Bedrock not available'}

        if service == "openai" and not self.openai_available:
            return {'error': 'OpenAI not available'}

        # Placeholder for cloud AI implementation
        return {
            'error': 'Cloud AI not implemented yet',
            'service': service
        }


class AIConnectionManager:
    """
    AI Connection Manager

    Routes AI requests to appropriate services:
    - Local AI (Ollama - ULTRON, KAIJU) - Priority
    - Cloud AI (Bedrock, OpenAI) - Fallback
    """

    def __init__(self):
        """Initialize AI Connection Manager"""
        logger.info("🔌 Initializing AI Connection Manager...")

        # Get connection URLs from environment or use defaults
        # Docker-aware: use host.docker.internal on Windows/Mac, or actual host IP
        ultron_url = os.getenv("ULTRON_URL", "http://host.docker.internal:11434")
        kaiju_url = os.getenv("KAIJU_URL", "http://<NAS_IP>:11434")

        # If not in Docker, try localhost first
        if not os.getenv("DYNO_DOCKER_ENABLED"):
            ultron_url = os.getenv("ULTRON_URL", "http://localhost:11434")

        # Local AI connections
        self.ultron = OllamaConnection(ultron_url, "ULTRON")
        self.kaiju = OllamaConnection(kaiju_url, "KAIJU")

        # Cloud AI connections
        self.cloud = CloudAIConnection()

        # Routing strategy
        self.routing_strategy = "local_first"  # local_first, round_robin, health_based

        logger.info("✅ AI Connection Manager initialized")
        self._log_availability()

    def _log_availability(self):
        """Log AI service availability"""
        available = []
        if self.ultron.is_available():
            available.append("ULTRON")
        if self.kaiju.is_available():
            available.append("KAIJU")
        if self.cloud.bedrock_available:
            available.append("Bedrock")
        if self.cloud.openai_available:
            available.append("Azure OpenAI")
        if self.cloud.anthropic_available:
            available.append("Anthropic")

        if available:
            logger.info(f"Available AI services: {', '.join(available)}")
        else:
            logger.warning("⚠️  No AI services available")

    def infer(
        self,
        query: str,
        prefer_local: bool = True,
        model: Optional[str] = None,
        use_retry: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute inference through AI connection layer with retry support.

        Args:
            query: Query to infer
            prefer_local: Prefer local AI (default: True)
            model: Model to use (optional)
            use_retry: Use retry manager for AI token requests (default: True)
            **kwargs: Additional parameters

        Returns:
            Inference result
        """
        # Wrap inference in retry manager if enabled
        if use_retry:
            try:
                from ai_token_request_retry_manager import AITokenRequestRetryManager
                retry_manager = AITokenRequestRetryManager(max_retries=5, initial_delay=2.0)

                # Determine configured AI service
                if prefer_local:
                    if self.ultron.is_available():
                        retry_manager.set_configured_ai_service("ULTRON", self.ultron.url)
                    elif self.kaiju.is_available():
                        retry_manager.set_configured_ai_service("KAIJU", self.kaiju.url)

                # Execute with retry
                def _infer_with_retry():
                    return self._infer_internal(query, prefer_local, model, **kwargs)

                return retry_manager.retry_ai_token_request(_infer_with_retry)
            except ImportError:
                logger.warning("⚠️  AI token retry manager not available, using direct inference")
                return self._infer_internal(query, prefer_local, model, **kwargs)
        else:
            return self._infer_internal(query, prefer_local, model, **kwargs)

    def _infer_internal(
        self,
        query: str,
        prefer_local: bool = True,
        model: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Internal inference method (without retry wrapper)
        """
        # Local-first strategy
        if prefer_local:
            # Try ULTRON first
            if self.ultron.is_available():
                result = self.ultron.infer(query, model=model or "llama2", **kwargs)
                if 'error' not in result:
                    return result

            # Try KAIJU second
            if self.kaiju.is_available():
                result = self.kaiju.infer(query, model=model or "llama2", **kwargs)
                if 'error' not in result:
                    return result

        # Fallback to cloud
        if self.cloud.bedrock_available:
            result = self.cloud.infer(query, service="bedrock", **kwargs)
            if 'error' not in result:
                return result

        if self.cloud.openai_available:
            result = self.cloud.infer(query, service="openai", **kwargs)
            if 'error' not in result:
                return result

        # No AI available
        return {
            'error': 'No AI services available',
            'query': query
        }

    def get_available_services(self) -> List[str]:
        """Get list of available AI services"""
        available = []
        if self.ultron.is_available():
            available.append(f"ULTRON ({self.ultron.url})")
        if self.kaiju.is_available():
            available.append(f"KAIJU ({self.kaiju.url})")
        if self.cloud.bedrock_available:
            available.append("Bedrock")
        if self.cloud.openai_available:
            available.append("Azure OpenAI")
        if self.cloud.anthropic_available:
            available.append("Anthropic")
        return available

    def get_status(self) -> Dict[str, Any]:
        """Get AI connection status"""
        return {
            'ultron': {
                'available': self.ultron.is_available(),
                'url': self.ultron.url
            },
            'kaiju': {
                'available': self.kaiju.is_available(),
                'url': self.kaiju.url
            },
            'cloud': {
                'bedrock': self.cloud.bedrock_available,
                'openai': self.cloud.openai_available,
                'anthropic': self.cloud.anthropic_available
            },
            'routing_strategy': self.routing_strategy,
            'available_services': self.get_available_services()
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("🔌 AI CONNECTION MANAGER")
    print("=" * 80)
    print()

    manager = AIConnectionManager()

    # Status
    print("AI SERVICE STATUS:")
    print("-" * 80)
    status = manager.get_status()
    print(f"ULTRON: {'✅' if status['ultron']['available'] else '❌'} ({status['ultron']['url']})")
    print(f"KAIJU: {'✅' if status['kaiju']['available'] else '❌'} ({status['kaiju']['url']})")
    print(f"Bedrock: {'✅' if status['cloud']['bedrock'] else '❌'}")
    print(f"OpenAI: {'✅' if status['cloud']['openai'] else '❌'}")
    print()

    # Available services
    available = manager.get_available_services()
    if available:
        print("AVAILABLE SERVICES:")
        print("-" * 80)
        for service in available:
            print(f"  ✅ {service}")
    else:
        print("⚠️  No AI services available")
    print()

    # Test inference
    if available:
        print("TESTING INFERENCE:")
        print("-" * 80)
        result = manager.infer("What is balance?")
        if 'error' not in result:
            print(f"✅ Inference successful")
            print(f"Source: {result.get('source', 'unknown')}")
            print(f"Response: {result.get('response', '')[:100]}...")
        else:
            print(f"❌ Inference failed: {result.get('error', 'unknown')}")
    print()

    print("=" * 80)
    print("🔌 AI Connection Manager - Ready for AIOS")
    print("=" * 80)


if __name__ == "__main__":


    main()