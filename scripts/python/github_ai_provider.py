#!/usr/bin/env python3
"""
GitHub AI Provider Integration for LUMINA

Integrates GitHub Models API into LUMINA's multi-provider AI system.
Supports chat completions, embeddings, and token pool management.

Features:
- GitHub Models API integration
- Token pool management and tracking
- Automatic fallback to local models when GitHub tokens exhausted
- Provider routing and load balancing

Tags: #GITHUB #AI #MODELS #API #INTEGRATION #TOKEN_POOL @LUMINA @JARVIS
"""

import os
import sys
import json
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GitHubAIProvider")


@dataclass
class GitHubModel:
    """GitHub Model Configuration"""
    name: str
    model_id: str  # e.g., "openai/gpt-4o", "anthropic/claude-3-5-sonnet"
    provider: str  # "openai", "anthropic", "meta", etc.
    modality: str  # "text", "image", "embedding"
    context_length: int
    max_tokens: int = 4096
    supports_function_calling: bool = False
    supports_structured_output: bool = False
    cost_per_token: float = 0.0  # Cost in USD per 1K tokens
    rate_limit_per_minute: int = 60


@dataclass
class GitHubTokenPool:
    """GitHub Token Pool Management"""
    total_tokens: int = 50000  # $20 subscription typically gives ~50K tokens
    used_tokens: int = 0
    reset_date: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=30))
    emergency_mode: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

    @property
    def remaining_tokens(self) -> int:
        return max(0, self.total_tokens - self.used_tokens)

    @property
    def usage_percent(self) -> float:
        return (self.used_tokens / self.total_tokens) * 100 if self.total_tokens > 0 else 100

    def can_make_request(self, estimated_tokens: int = 1000) -> bool:
        """Check if we can make a request with estimated token usage"""
        if self.emergency_mode:
            return False
        return self.remaining_tokens >= estimated_tokens

    def consume_tokens(self, tokens_used: int) -> bool:
        """Consume tokens and return success"""
        if self.remaining_tokens >= tokens_used:
            self.used_tokens += tokens_used
            self.last_updated = datetime.now()

            # Enter emergency mode at 95% usage
            if self.usage_percent >= 95 and not self.emergency_mode:
                self.emergency_mode = True
                logger.warning("🚨 GITHUB TOKEN POOL EMERGENCY MODE ACTIVATED (95% usage)")

            return True
        return False


class GitHubAIProvider:
    """
    GitHub AI Provider for LUMINA

    Integrates GitHub Models API with full token pool management,
    automatic fallback, and multi-provider routing.
    """

    def __init__(self, github_token: Optional[str] = None, project_root: Optional[Path] = None):
        """Initialize GitHub AI Provider"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "github_ai"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configuration files
        self.config_file = self.data_dir / "github_config.json"
        self.token_pool_file = self.data_dir / "token_pool.json"
        self.models_cache_file = self.data_dir / "models_cache.json"

        # GitHub API configuration
        self.base_url = "https://models.github.ai"
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")

        if not self.github_token:
            logger.warning("⚠️  No GitHub token provided. Set GITHUB_TOKEN environment variable.")

        # Initialize components
        self.models: Dict[str, GitHubModel] = {}
        self.token_pool = GitHubTokenPool()
        self.models_cache: Dict[str, Any] = {}
        self.last_cache_update: Optional[datetime] = None

        # Load state
        self._load_config()
        self._load_token_pool()
        self._load_models_cache()

        logger.info("✅ GitHub AI Provider initialized")
        logger.info(f"   Token Pool: {self.token_pool.remaining_tokens}/{self.token_pool.total_tokens} remaining")
        logger.info(f"   Emergency Mode: {self.token_pool.emergency_mode}")

    def _load_config(self):
        """Load GitHub provider configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.base_url = config.get('base_url', self.base_url)
                    logger.info("✅ GitHub config loaded")
            except Exception as e:
                logger.error(f"Failed to load GitHub config: {e}")

    def _load_token_pool(self):
        """Load token pool state"""
        if self.token_pool_file.exists():
            try:
                with open(self.token_pool_file, 'r') as f:
                    pool_data = json.load(f)
                    self.token_pool = GitHubTokenPool(**pool_data)
                    # Convert string dates back to datetime
                    if isinstance(self.token_pool.reset_date, str):
                        self.token_pool.reset_date = datetime.fromisoformat(self.token_pool.reset_date)
                    if isinstance(self.token_pool.last_updated, str):
                        self.token_pool.last_updated = datetime.fromisoformat(self.token_pool.last_updated)
                    logger.info("✅ Token pool state loaded")
            except Exception as e:
                logger.error(f"Failed to load token pool: {e}")

    def _load_models_cache(self):
        """Load cached models information"""
        if self.models_cache_file.exists():
            try:
                with open(self.models_cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.models_cache = cache_data.get('models', {})
                    self.last_cache_update = datetime.fromisoformat(cache_data.get('last_update', datetime.now().isoformat()))
                    logger.info("✅ Models cache loaded")
            except Exception as e:
                logger.error(f"Failed to load models cache: {e}")

    def _save_token_pool(self):
        """Save token pool state"""
        try:
            pool_data = asdict(self.token_pool)
            # Convert datetime to string for JSON serialization
            pool_data['reset_date'] = self.token_pool.reset_date.isoformat()
            pool_data['last_updated'] = self.token_pool.last_updated.isoformat()

            with open(self.token_pool_file, 'w') as f:
                json.dump(pool_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save token pool: {e}")

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return {
            "Authorization": f"Bearer {self.github_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def refresh_models_cache(self) -> bool:
        """Refresh the models cache from GitHub API"""
        if not self.github_token:
            logger.error("Cannot refresh models cache: No GitHub token")
            return False

        try:
            url = f"{self.base_url}/catalog/models"
            response = requests.get(url, headers=self._get_headers(), timeout=30)

            if response.status_code == 200:
                models_data = response.json()
                self.models_cache = {model['name']: model for model in models_data}
                self.last_cache_update = datetime.now()

                # Save cache
                cache_data = {
                    'models': self.models_cache,
                    'last_update': self.last_cache_update.isoformat()
                }
                with open(self.models_cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)

                # Update our models registry
                self._update_models_registry(models_data)

                logger.info(f"✅ Refreshed models cache: {len(self.models_cache)} models available")
                return True
            else:
                logger.error(f"Failed to refresh models cache: HTTP {response.status_code}")
                return False

        except Exception as e:
            logger.error(f"Error refreshing models cache: {e}")
            return False

    def _update_models_registry(self, models_data: List[Dict[str, Any]]):
        """Update our models registry from GitHub API data"""
        for model_data in models_data:
            model_id = model_data['name']  # e.g., "openai/gpt-4o"
            provider_name = model_id.split('/')[0]

            model = GitHubModel(
                name=model_data.get('display_name', model_id),
                model_id=model_id,
                provider=provider_name,
                modality=model_data.get('modality', 'text'),
                context_length=model_data.get('context_length', 4096),
                max_tokens=model_data.get('max_output_tokens', 4096),
                supports_function_calling=model_data.get('supports_function_calling', False),
                supports_structured_output=model_data.get('supports_structured_output', False),
                cost_per_token=self._estimate_cost_per_token(model_id),
                rate_limit_per_minute=model_data.get('rate_limit_per_minute', 60)
            )

            self.models[model_id] = model

    def _estimate_cost_per_token(self, model_id: str) -> float:
        """Estimate cost per 1K tokens based on model"""
        # These are approximate costs for GitHub Models
        cost_estimates = {
            'openai/gpt-4o': 0.03,
            'openai/gpt-4o-mini': 0.00015,
            'anthropic/claude-3-5-sonnet': 0.015,
            'anthropic/claude-3-haiku': 0.00025,
            'meta/meta-llama-3.1-405b-instruct': 0.009,
            'meta/meta-llama-3.1-70b-instruct': 0.009,
            'meta/meta-llama-3.1-8b-instruct': 0.0003,
            'microsoft/wizardlm-2-8x22b': 0.006,
            'mistral/mistral-large': 0.008,
            'mistral/mistral-7b-instruct': 0.0002
        }
        return cost_estimates.get(model_id, 0.001)  # Default fallback

    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        if not self.models_cache:
            self.refresh_models_cache()

        return [
            {
                'id': model_id,
                'name': model_info.get('display_name', model_id),
                'provider': model_id.split('/')[0],
                'modality': model_info.get('modality', 'text'),
                'context_length': model_info.get('context_length', 4096),
                'rate_limit': model_info.get('rate_limit_per_minute', 60)
            }
            for model_id, model_info in self.models_cache.items()
        ]

    def chat_completion(self, model: str, messages: List[Dict[str, str]],
                       max_tokens: int = 1000, temperature: float = 0.7,
                       stream: bool = False) -> Optional[Dict[str, Any]]:
        """
        Perform chat completion using GitHub Models API

        Args:
            model: Model ID (e.g., "openai/gpt-4o")
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            stream: Whether to stream the response

        Returns:
            Response dict or None if failed
        """
        if not self.github_token:
            logger.error("Cannot make chat completion: No GitHub token")
            return None

        # Check token pool
        estimated_tokens = len(str(messages)) // 4 + max_tokens  # Rough estimate
        if not self.token_pool.can_make_request(estimated_tokens):
            logger.warning("🚫 GitHub token pool exhausted - cannot make request")
            return None

        try:
            url = f"{self.base_url}/inference/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": stream
            }

            response = requests.post(url, headers=self._get_headers(),
                                   json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()

                # Track token usage
                tokens_used = result.get('usage', {}).get('total_tokens', estimated_tokens)
                if self.token_pool.consume_tokens(tokens_used):
                    self._save_token_pool()
                    logger.debug(f"Consumed {tokens_used} GitHub tokens. Remaining: {self.token_pool.remaining_tokens}")

                return result
            else:
                logger.error(f"GitHub API error: HTTP {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error in chat completion: {e}")
            return None

    def create_embeddings(self, model: str, inputs: List[str]) -> Optional[Dict[str, Any]]:
        """Create embeddings using GitHub Models API"""
        if not self.github_token:
            logger.error("Cannot create embeddings: No GitHub token")
            return None

        # Check token pool (embeddings are cheaper)
        estimated_tokens = sum(len(text) for text in inputs) // 4
        if not self.token_pool.can_make_request(estimated_tokens):
            logger.warning("🚫 GitHub token pool exhausted - cannot create embeddings")
            return None

        try:
            url = f"{self.base_url}/inference/embeddings"
            payload = {
                "model": model,
                "inputs": inputs
            }

            response = requests.post(url, headers=self._get_headers(),
                                   json=payload, timeout=60)

            if response.status_code == 200:
                result = response.json()

                # Track token usage (embeddings use input tokens)
                tokens_used = result.get('usage', {}).get('total_tokens', estimated_tokens)
                if self.token_pool.consume_tokens(tokens_used):
                    self._save_token_pool()

                return result
            else:
                logger.error(f"GitHub embeddings API error: HTTP {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            return None

    def get_token_pool_status(self) -> Dict[str, Any]:
        """Get current token pool status"""
        return {
            'total_tokens': self.token_pool.total_tokens,
            'used_tokens': self.token_pool.used_tokens,
            'remaining_tokens': self.token_pool.remaining_tokens,
            'usage_percent': round(self.token_pool.usage_percent, 2),
            'emergency_mode': self.token_pool.emergency_mode,
            'reset_date': self.token_pool.reset_date.isoformat(),
            'last_updated': self.token_pool.last_updated.isoformat()
        }

    def reset_token_pool(self, new_total: Optional[int] = None):
        """Reset token pool (typically monthly)"""
        if new_total:
            self.token_pool.total_tokens = new_total

        self.token_pool.used_tokens = 0
        self.token_pool.emergency_mode = False
        self.token_pool.reset_date = datetime.now() + timedelta(days=30)
        self.token_pool.last_updated = datetime.now()

        self._save_token_pool()
        logger.info(f"✅ Token pool reset. New total: {self.token_pool.total_tokens}")

    def is_available(self) -> bool:
        """Check if GitHub AI provider is available"""
        if not self.github_token:
            return False

        if self.token_pool.emergency_mode:
            return False

        # Quick health check
        try:
            url = f"{self.base_url}/catalog/models"
            response = requests.get(url, headers=self._get_headers(), timeout=5)
            return response.status_code == 200
        except:
            return False


def main():
    """CLI interface for GitHub AI Provider"""
    import argparse

    parser = argparse.ArgumentParser(description="GitHub AI Provider for LUMINA")
    parser.add_argument("--refresh-models", action="store_true", help="Refresh models cache")
    parser.add_argument("--status", action="store_true", help="Show token pool status")
    parser.add_argument("--reset-pool", type=int, nargs='?', const=50000,
                       help="Reset token pool (optional: new total)")
    parser.add_argument("--test-chat", nargs=2, metavar=('MODEL', 'MESSAGE'),
                       help="Test chat completion")

    args = parser.parse_args()

    provider = GitHubAIProvider()

    if args.refresh_models:
        success = provider.refresh_models_cache()
        if success:
            print("✅ Models cache refreshed")
        else:
            print("❌ Failed to refresh models cache")

    elif args.status:
        status = provider.get_token_pool_status()
        print(f"GitHub Token Pool Status:")
        print(f"  Total: {status['total_tokens']:,} tokens")
        print(f"  Used: {status['used_tokens']:,} tokens")
        print(f"  Remaining: {status['remaining_tokens']:,} tokens")
        print(f"  Usage: {status['usage_percent']}%")
        print(f"  Emergency Mode: {status['emergency_mode']}")
        print(f"  Reset Date: {status['reset_date']}")

    elif args.reset_pool is not None:
        provider.reset_token_pool(args.reset_pool)
        print(f"✅ Token pool reset to {args.reset_pool:,} tokens")

    elif args.test_chat:
        model, message = args.test_chat
        messages = [{"role": "user", "content": message}]
        result = provider.chat_completion(model, messages)

        if result:
            content = result['choices'][0]['message']['content']
            print(f"Response from {model}:")
            print(content)
        else:
            print("❌ Chat completion failed")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()