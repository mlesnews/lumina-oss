#!/usr/bin/env python3
"""
JARVIS Remote Renderer - Offloads compute to Azure Framework
Pushes rendering, VLM processing, and heavy computation to remote servers.
"""
import json
import base64
import io
import requests
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
import time

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False

try:
    from lumina_logger import get_logger
    logger = get_logger("RemoteRenderer")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("RemoteRenderer")


class RemoteRenderService:
    """
    Remote rendering service that offloads compute to Azure Functions/API
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path(__file__).parent.parent.parent / "config" / "azure_services_config.json"
        self.config = self._load_config()
        self.azure_available = AZURE_AVAILABLE

        # Remote endpoints
        self.render_endpoint = None
        self.vlm_endpoint = None
        self.compute_endpoint = None

        # Cache for fallback
        self.last_rendered_frame = None
        self.cache_enabled = True

        self._initialize_endpoints()

    def _load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load config: {e}")
            return {}

    def _initialize_endpoints(self):
        """Initialize remote compute endpoints"""
        try:
            azure_config = self.config.get("azure_services_config", {})

            # Azure Functions endpoint for rendering
            functions_config = azure_config.get("azure_functions", {})
            if functions_config.get("enabled"):
                function_app = functions_config.get("function_app_name", "jarvis-lumina-functions")
                # Function names are lowercase in Azure
                self.render_endpoint = f"https://{function_app}.azurewebsites.net/api/renderironlegion"

            # Override with remote_compute config if available
            remote_compute = azure_config.get("remote_compute", {})
            if remote_compute.get("enabled") and remote_compute.get("render_endpoint"):
                self.render_endpoint = remote_compute.get("render_endpoint")

            # Azure Cognitive Services Vision for VLM
            cognitive_config = azure_config.get("cognitive_services", {})
            if cognitive_config.get("enabled"):
                vision_config = cognitive_config.get("services", {}).get("vision", {})
                if vision_config:
                    self.vlm_endpoint = f"https://{vision_config.get('name')}.cognitiveservices.azure.com/vision/v3.2/analyze"

            # Generic compute endpoint (can be custom API)
            self.compute_endpoint = azure_config.get("compute_endpoint") or self.render_endpoint

            logger.info(f"✅ Remote endpoints initialized: Render={bool(self.render_endpoint)}, VLM={bool(self.vlm_endpoint)}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize endpoints: {e}")

    def render_frame_remote(self,
                           state: str,
                           animation_frame: int,
                           transformation_progress: float,
                           size: int = 180) -> Optional[bytes]:
        """
        Request frame rendering from remote server

        Args:
            state: Current LegionState (suitcase, armor, working, sleeping)
            animation_frame: Current animation frame number
            transformation_progress: Transformation progress (0.0-1.0)
            size: Output size in pixels

        Returns:
            PNG image bytes or None if remote rendering fails
        """
        if not self.render_endpoint:
            logger.warning("⚠️  No remote render endpoint configured")
            return None

        try:
            payload = {
                "state": state,
                "animation_frame": animation_frame,
                "transformation_progress": transformation_progress,
                "size": size,
                "timestamp": datetime.now().isoformat()
            }

            # Get function key if needed (for function-level auth)
            function_key = self._get_function_key()
            url = self.render_endpoint
            if function_key and "code=" not in url:
                url = f"{url}?code={function_key}"

            # Request remote rendering
            response = requests.post(
                url,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=5.0  # Fast timeout for real-time
            )

            if response.status_code == 200:
                # Decode base64 image if returned as JSON
                if response.headers.get("Content-Type") == "application/json":
                    data = response.json()
                    image_data = base64.b64decode(data.get("image", ""))
                else:
                    image_data = response.content

                if self.cache_enabled:
                    self.last_rendered_frame = image_data

                logger.debug(f"✅ Remote render successful: {len(image_data)} bytes")
                return image_data
            else:
                logger.warning(f"⚠️  Remote render failed: {response.status_code}")
                return self._fallback_render()

        except requests.exceptions.Timeout:
            logger.warning("⚠️  Remote render timeout, using fallback")
            return self._fallback_render()
        except Exception as e:
            logger.error(f"❌ Remote render error: {e}")
            return self._fallback_render()

    def _fallback_render(self) -> Optional[bytes]:
        """Fallback to cached frame or None"""
        if self.cache_enabled and self.last_rendered_frame:
            logger.info("🔄 Using cached frame as fallback")
            return self.last_rendered_frame
        return None

    def process_vlm_remote(self, image_bytes: bytes, query: str) -> Optional[Dict[str, Any]]:
        """
        Process VLM analysis on remote server

        Args:
            image_bytes: Image to analyze
            query: Analysis query/question

        Returns:
            VLM analysis result or None
        """
        if not self.vlm_endpoint:
            logger.warning("⚠️  No VLM endpoint configured")
            return None

        try:
            # Azure Cognitive Services Vision API
            headers = {
                "Ocp-Apim-Subscription-Key": self._get_vision_key(),
                "Content-Type": "application/octet-stream"
            }

            params = {
                "visualFeatures": "Description,Tags,Objects",
                "details": "Celebrities,Landmarks",
                "language": "en"
            }

            response = requests.post(
                self.vlm_endpoint,
                headers=headers,
                params=params,
                data=image_bytes,
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"✅ VLM analysis successful")
                return result
            else:
                logger.warning(f"⚠️  VLM analysis failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ VLM analysis error: {e}")
            return None

    def _get_vision_key(self) -> str:
        """Get Azure Cognitive Services Vision API key"""
        try:
            if self.azure_available:
                vault_url = self.config.get("azure_services_config", {}).get("key_vault", {}).get("vault_url")
                if vault_url:
                    credential = DefaultAzureCredential(

                                        exclude_interactive_browser_credential=False,

                                        exclude_shared_token_cache_credential=False

                                    )
                    client = SecretClient(vault_url=vault_url, credential=credential)
                    secret = client.get_secret("cognitive-vision-key")
                    return secret.value
        except Exception as e:
            logger.warning(f"⚠️  Could not get vision key: {e}")

        # Fallback to environment variable
        import os
        return os.environ.get("AZURE_VISION_KEY", "")

    def _get_function_key(self) -> str:
        """Get Azure Function key for authentication"""
        try:
            if self.azure_available:
                vault_url = self.config.get("azure_services_config", {}).get("key_vault", {}).get("vault_url")
                if vault_url:
                    credential = DefaultAzureCredential(

                                        exclude_interactive_browser_credential=False,

                                        exclude_shared_token_cache_credential=False

                                    )
                    client = SecretClient(vault_url=vault_url, credential=credential)
                    try:
                        secret = client.get_secret("azure-function-app-key")
                        return secret.value
                    except:
                        pass
        except Exception as e:
            logger.debug(f"Could not get function key from vault: {e}")

        # Fallback to environment variable or config
        import os
        return os.environ.get("AZURE_FUNCTION_KEY", "")

    def offload_computation(self,
                          computation_type: str,
                          data: Dict[str, Any]) -> Optional[Any]:
        """
        Generic computation offloading to remote server

        Args:
            computation_type: Type of computation (e.g., "state_machine", "physics", "ai_decision")
            data: Computation input data

        Returns:
            Computation result or None
        """
        if not self.compute_endpoint:
            logger.warning("⚠️  No compute endpoint configured")
            return None

        try:
            payload = {
                "computation_type": computation_type,
                "data": data,
                "timestamp": datetime.now().isoformat()
            }

            response = requests.post(
                self.compute_endpoint,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=10.0
            )

            if response.status_code == 200:
                result = response.json()
                logger.debug(f"✅ Computation offloaded: {computation_type}")
                return result.get("result")
            else:
                logger.warning(f"⚠️  Computation failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Computation offload error: {e}")
            return None


class HybridRenderer:
    """
    Hybrid renderer that intelligently switches between remote and local rendering
    """

    def __init__(self):
        self.remote_service = RemoteRenderService()
        self.use_remote = True
        self.remote_success_count = 0
        self.remote_failure_count = 0
        self.fallback_threshold = 3  # Switch to local after 3 failures

    def should_use_remote(self) -> bool:
        """Determine if remote rendering should be used"""
        if not self.remote_service.render_endpoint:
            return False

        # Switch to local if too many failures
        if self.remote_failure_count >= self.fallback_threshold:
            return False

        return self.use_remote

    def render(self,
              state: str,
              animation_frame: int,
              transformation_progress: float,
              size: int = 180) -> Optional[bytes]:
        """
        Render frame using remote or local fallback
        """
        if self.should_use_remote():
            result = self.remote_service.render_frame_remote(
                state, animation_frame, transformation_progress, size
            )

            if result:
                self.remote_success_count += 1
                self.remote_failure_count = 0
                return result
            else:
                self.remote_failure_count += 1
                logger.warning(f"⚠️  Remote render failed ({self.remote_failure_count}/{self.fallback_threshold})")

        # Fallback to local rendering
        logger.info("🔄 Falling back to local rendering")
        return None  # Caller should handle local rendering


if __name__ == "__main__":
    # Test remote renderer
    renderer = HybridRenderer()
    print("🧪 Testing remote renderer...")

    test_result = renderer.render(
        state="armor",
        animation_frame=0,
        transformation_progress=1.0,
        size=180
    )

    if test_result:
        print(f"✅ Remote render successful: {len(test_result)} bytes")
    else:
        print("⚠️  Remote render unavailable, would use local fallback")
