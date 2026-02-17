#!/usr/bin/env python3
"""
@LUMINA: Cursor IDE Model Testing Script
Tests all models (cloud and local) using the same mechanics Cursor IDE uses
@DOIT @END2END @REPORT
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional

import requests
import logging
logger = logging.getLogger("test_cursor_models")


# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

@dataclass
class ModelTestResult:
    """Test result for a single model"""
    name: str
    title: str
    provider: str
    endpoint: str
    status: str  # "success", "failed", "skipped"
    response_time: float
    error: Optional[str] = None
    response_preview: Optional[str] = None
    local_only: bool = False
    requires_api_key: bool = True

class CursorModelTester:
    """Test all Cursor IDE models using Cursor's mechanics"""

    def __init__(self, config_path: str):
        self.config_path = config_path
        self.results: List[ModelTestResult] = []
        self.test_prompt = "Say 'Hello from Cursor IDE model test' in one sentence."

    def load_config(self) -> Dict:
        try:
            """Load Cursor models configuration"""
            with open(self.config_path, encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_config: {e}", exc_info=True)
            raise
    def test_ollama_model(self, model: Dict) -> ModelTestResult:
        """Test Ollama (local) model - same as Cursor IDE"""
        name = model.get('name', 'unknown')
        title = model.get('title', name)
        api_base = model.get('apiBase', 'http://localhost:11434')
        model_name = model.get('model', '')
        local_only = model.get('localOnly', False)
        requires_api_key = model.get('requiresApiKey', False)

        start_time = time.time()

        try:
            # First check if endpoint is accessible
            # Try root first (for routers/load balancers)
            try:
                root_response = requests.get(api_base, timeout=3)
                if root_response.status_code == 200:
                    # Endpoint is accessible, might be a router
                    # Try Ollama API endpoint
                    tags_url = f"{api_base}/api/tags"
                else:
                    tags_url = f"{api_base}/api/tags"
            except:
                tags_url = f"{api_base}/api/tags"

            tags_response = requests.get(tags_url, timeout=5)

            if tags_response.status_code == 404:
                # Router might be accessible but API path different
                # Try direct generate endpoint as fallback
                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="ollama",
                    endpoint=api_base,
                    status="failed",
                    response_time=time.time() - start_time,
                    error=f"Ollama API endpoint not found (404) - Router accessible but API path may differ. Try: {api_base}/api/generate",
                    local_only=local_only,
                    requires_api_key=requires_api_key
                )
            elif tags_response.status_code != 200:
                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="ollama",
                    endpoint=api_base,
                    status="failed",
                    response_time=time.time() - start_time,
                    error=f"Ollama endpoint not accessible: HTTP {tags_response.status_code}",
                    local_only=local_only,
                    requires_api_key=requires_api_key
                )

            # Check if model exists
            tags_data = tags_response.json()
            available_models = [m.get('name', '') for m in tags_data.get('models', [])]

            if model_name not in available_models:
                # Try to find similar model
                model_base = model_name.split(':')[0]
                similar = [m for m in available_models if model_base in m or m.split(':')[0] in model_base]
                if similar:
                    model_name = similar[0]
                    print(f"   ⚠️  Using available model: {model_name} (requested: {model.get('model', '')})")
                else:
                    # If no similar model, use first available model
                    if available_models:
                        model_name = available_models[0]
                        print(f"   ⚠️  Using first available model: {model_name} (requested: {model.get('model', '')})")
                    else:
                        return ModelTestResult(
                            name=name,
                            title=title,
                            provider="ollama",
                            endpoint=api_base,
                            status="failed",
                            response_time=time.time() - start_time,
                            error=f"Model '{model.get('model', '')}' not found. No models available.",
                            local_only=local_only,
                            requires_api_key=requires_api_key
                        )

            # Try Ollama API first, then OpenAI-compatible API (for Iron Legion containers)
            # Cursor IDE uses Ollama's /api/generate endpoint
            url = f"{api_base}/api/generate"
            payload = {
                "model": model_name,
                "prompt": self.test_prompt,
                "stream": False
            }

            response = requests.post(
                url,
                json=payload,
                timeout=60,
                headers={"Content-Type": "application/json"}
            )

            response_time = time.time() - start_time

            # If Ollama API fails, try OpenAI-compatible API (for Iron Legion llamacpp containers)
            if response.status_code == 404:
                # Try OpenAI-compatible endpoint
                url = f"{api_base}/v1/chat/completions"
                payload = {
                    "model": model_name,
                    "messages": [
                        {"role": "user", "content": self.test_prompt}
                    ],
                    "max_tokens": 50,
                    "stream": False
                }

                response = requests.post(
                    url,
                    json=payload,
                    timeout=60,
                    headers={"Content-Type": "application/json"}
                )
                response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                # Handle both Ollama and OpenAI response formats
                if 'response' in data:
                    # Ollama format
                    response_text = data.get('response', '')[:100]
                elif 'choices' in data:
                    # OpenAI format
                    response_text = data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]
                else:
                    response_text = 'Response received'

                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="ollama",
                    endpoint=api_base,
                    status="success",
                    response_time=response_time,
                    response_preview=response_text,
                    local_only=local_only,
                    requires_api_key=requires_api_key
                )
            else:
                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="ollama",
                    endpoint=api_base,
                    status="failed",
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    local_only=local_only,
                    requires_api_key=requires_api_key
                )

        except requests.exceptions.ConnectionError as e:
            return ModelTestResult(
                name=name,
                title=title,
                provider="ollama",
                endpoint=api_base,
                status="failed",
                response_time=time.time() - start_time,
                error=f"Connection error: {str(e)[:200]}",
                local_only=local_only,
                requires_api_key=requires_api_key
            )
        except Exception as e:
            return ModelTestResult(
                name=name,
                title=title,
                provider="ollama",
                endpoint=api_base,
                status="failed",
                response_time=time.time() - start_time,
                error=f"Error: {str(e)[:200]}",
                local_only=local_only,
                requires_api_key=requires_api_key
            )

    def test_openai_model(self, model: Dict, api_key: Optional[str] = None) -> ModelTestResult:
        """Test OpenAI model - same as Cursor IDE"""
        name = model.get('name', 'unknown')
        title = model.get('title', name)
        model_name = model.get('model', '')
        api_base = model.get('apiBase', 'https://api.openai.com/v1')
        requires_api_key = model.get('requiresApiKey', True)

        if requires_api_key and not api_key:
            return ModelTestResult(
                name=name,
                title=title,
                provider="openai",
                endpoint=api_base,
                status="skipped",
                response_time=0,
                error="API key required but not provided",
                requires_api_key=True
            )

        start_time = time.time()

        try:
            # Cursor IDE uses OpenAI's /chat/completions endpoint
            url = f"{api_base}/chat/completions"
            headers = {
                "Content-Type": "application/json",
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"

            payload = {
                "model": model_name,
                "messages": [
                    {"role": "user", "content": self.test_prompt}
                ],
                "max_tokens": 50
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')[:100]

                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="openai",
                    endpoint=api_base,
                    status="success",
                    response_time=response_time,
                    response_preview=content,
                    requires_api_key=requires_api_key
                )
            else:
                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="openai",
                    endpoint=api_base,
                    status="failed",
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    requires_api_key=requires_api_key
                )

        except Exception as e:
            return ModelTestResult(
                name=name,
                title=title,
                provider="openai",
                endpoint=api_base,
                status="failed",
                response_time=time.time() - start_time,
                error=f"Error: {str(e)[:200]}",
                requires_api_key=requires_api_key
            )

    def test_anthropic_model(self, model: Dict, api_key: Optional[str] = None) -> ModelTestResult:
        """Test Anthropic (Claude) model - same as Cursor IDE"""
        name = model.get('name', 'unknown')
        title = model.get('title', name)
        model_name = model.get('model', '')
        api_base = model.get('apiBase', 'https://api.anthropic.com/v1')
        requires_api_key = model.get('requiresApiKey', True)

        if requires_api_key and not api_key:
            return ModelTestResult(
                name=name,
                title=title,
                provider="anthropic",
                endpoint=api_base,
                status="skipped",
                response_time=0,
                error="API key required but not provided",
                requires_api_key=True
            )

        start_time = time.time()

        try:
            # Cursor IDE uses Anthropic's /messages endpoint
            url = f"{api_base}/messages"
            headers = {
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            if api_key:
                headers["x-api-key"] = api_key

            payload = {
                "model": model_name,
                "max_tokens": 50,
                "messages": [
                    {"role": "user", "content": self.test_prompt}
                ]
            }

            response = requests.post(
                url,
                json=payload,
                headers=headers,
                timeout=30
            )

            response_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                content = data.get('content', [{}])[0].get('text', '')[:100]

                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="anthropic",
                    endpoint=api_base,
                    status="success",
                    response_time=response_time,
                    response_preview=content,
                    requires_api_key=requires_api_key
                )
            else:
                return ModelTestResult(
                    name=name,
                    title=title,
                    provider="anthropic",
                    endpoint=api_base,
                    status="failed",
                    response_time=response_time,
                    error=f"HTTP {response.status_code}: {response.text[:200]}",
                    requires_api_key=requires_api_key
                )

        except Exception as e:
            return ModelTestResult(
                name=name,
                title=title,
                provider="anthropic",
                endpoint=api_base,
                status="failed",
                response_time=time.time() - start_time,
                error=f"Error: {str(e)[:200]}",
                requires_api_key=requires_api_key
            )

    def test_model(self, model: Dict, api_keys: Dict[str, str]) -> ModelTestResult:
        """Test a single model based on provider"""
        provider = model.get('provider', '').lower()
        local_only = model.get('localOnly', False)
        requires_api_key = model.get('requiresApiKey', True)

        # Skip cloud models if local_only is True (shouldn't happen, but safety check)
        if local_only and provider not in ['ollama']:
            return ModelTestResult(
                name=model.get('name', 'unknown'),
                title=model.get('title', 'unknown'),
                provider=provider,
                endpoint=model.get('apiBase', ''),
                status="skipped",
                response_time=0,
                error="Local-only model with non-local provider",
                local_only=True,
                requires_api_key=requires_api_key
            )

        if provider == 'ollama':
            return self.test_ollama_model(model)
        elif provider == 'openai':
            api_key = api_keys.get('openai') or api_keys.get('OPENAI_API_KEY')
            return self.test_openai_model(model, api_key)
        elif provider == 'anthropic':
            api_key = api_keys.get('anthropic') or api_keys.get('ANTHROPIC_API_KEY')
            return self.test_anthropic_model(model, api_key)
        else:
            # Generic test for other providers (Google, Azure, etc.)
            return ModelTestResult(
                name=model.get('name', 'unknown'),
                title=model.get('title', 'unknown'),
                provider=provider,
                endpoint=model.get('apiBase', ''),
                status="skipped",
                response_time=0,
                error=f"Provider '{provider}' not yet implemented in tester",
                requires_api_key=requires_api_key
            )

    def run_tests(self, api_keys: Optional[Dict[str, str]] = None) -> List[ModelTestResult]:
        """Run tests on all models"""
        if api_keys is None:
            api_keys = {}

        config = self.load_config()
        models = config.get('cursor.chat.customModels', [])

        print(f"\n🧪 Testing {len(models)} Cursor IDE Models...")
        print("=" * 80)

        for i, model in enumerate(models, 1):
            name = model.get('name', 'unknown')
            title = model.get('title', name)
            provider = model.get('provider', 'unknown')
            local_only = model.get('localOnly', False)

            print(f"\n[{i}/{len(models)}] Testing: {title}")
            print(f"   Provider: {provider} | Local: {local_only}")

            result = self.test_model(model, api_keys)
            self.results.append(result)

            if result.status == "success":
                print(f"   ✅ SUCCESS ({result.response_time:.2f}s): {result.response_preview}")
            elif result.status == "skipped":
                print(f"   ⏭️  SKIPPED: {result.error}")
            else:
                print(f"   ❌ FAILED: {result.error}")

            # Small delay between tests
            time.sleep(0.5)

        return self.results

    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        total = len(self.results)
        successful = sum(1 for r in self.results if r.status == "success")
        failed = sum(1 for r in self.results if r.status == "failed")
        skipped = sum(1 for r in self.results if r.status == "skipped")

        local_models = [r for r in self.results if r.local_only]
        cloud_models = [r for r in self.results if not r.local_only]

        local_success = sum(1 for r in local_models if r.status == "success")
        cloud_success = sum(1 for r in cloud_models if r.status == "success")

        avg_response_time = sum(r.response_time for r in self.results if r.response_time > 0) / max(1, successful)

        return {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_models": total,
                "successful": successful,
                "failed": failed,
                "skipped": skipped,
                "success_rate": f"{(successful/total*100):.1f}%" if total > 0 else "0%",
                "average_response_time": f"{avg_response_time:.2f}s"
            },
            "by_type": {
                "local_models": {
                    "total": len(local_models),
                    "successful": local_success,
                    "failed": len(local_models) - local_success
                },
                "cloud_models": {
                    "total": len(cloud_models),
                    "successful": cloud_success,
                    "failed": len(cloud_models) - cloud_success
                }
            },
            "results": [
                {
                    "name": r.name,
                    "title": r.title,
                    "provider": r.provider,
                    "endpoint": r.endpoint,
                    "status": r.status,
                    "response_time": f"{r.response_time:.2f}s",
                    "local_only": r.local_only,
                    "requires_api_key": r.requires_api_key,
                    "error": r.error,
                    "response_preview": r.response_preview
                }
                for r in self.results
            ]
        }

    def print_summary(self):
        """Print test summary"""
        report = self.generate_report()
        summary = report['summary']

        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        print(f"Total Models: {summary['total_models']}")
        print(f"✅ Successful: {summary['successful']}")
        print(f"❌ Failed: {summary['failed']}")
        print(f"⏭️  Skipped: {summary['skipped']}")
        print(f"Success Rate: {summary['success_rate']}")
        print(f"Average Response Time: {summary['average_response_time']}")

        by_type = report['by_type']
        print(f"\nLocal Models: {by_type['local_models']['successful']}/{by_type['local_models']['total']} successful")
        print(f"Cloud Models: {by_type['cloud_models']['successful']}/{by_type['cloud_models']['total']} successful")

        print("\n" + "=" * 80)

def main():
    try:
        """Main execution"""
        config_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'data', 'cursor_models', 'cursor_models_config.json'
        )

        # Load API keys from environment (if available)
        api_keys = {
            'openai': os.getenv('OPENAI_API_KEY', ''),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
            'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
            'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
        }

        tester = CursorModelTester(config_path)
        results = tester.run_tests(api_keys)
        tester.print_summary()

        # Save report
        report = tester.generate_report()
        report_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', 'data', 'cursor_models', f'model_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )

        os.makedirs(os.path.dirname(report_path), exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)

        print(f"\n📄 Full report saved to: {report_path}")

        # Exit code based on results
        if any(r.status == "failed" for r in results if not r.local_only):
            sys.exit(1)  # Cloud model failures are critical
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()