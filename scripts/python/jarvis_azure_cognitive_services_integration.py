#!/usr/bin/env python3
"""
JARVIS Azure Cognitive Services Integration

Full integration with Azure Cognitive Services:
- Speech Services: Enhanced voice transcript quality
- Text Analytics: Sentiment analysis, key phrase extraction
- Computer Vision: Screenshot analysis

Tags: #AZURE #COGNITIVE_SERVICES #AI #SPEECH #TEXT_ANALYTICS #VISION #LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAzureCognitive")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISAzureCognitive")

# Azure Cognitive Services SDKs
try:
    from azure.cognitiveservices.speech import SpeechConfig, SpeechRecognizer, AudioConfig
    from azure.cognitiveservices.speech.audio import AudioInputStream
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    AZURE_SPEECH_AVAILABLE = False
    logger.warning("Azure Speech SDK not available. Install with: pip install azure-cognitiveservices-speech")

try:
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    AZURE_TEXT_ANALYTICS_AVAILABLE = True
except ImportError:
    AZURE_TEXT_ANALYTICS_AVAILABLE = False
    logger.warning("Azure Text Analytics SDK not available. Install with: pip install azure-ai-textanalytics")

try:
    from azure.cognitiveservices.vision.computervision import ComputerVisionClient
    from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
    from msrest.authentication import CognitiveServicesCredentials
    AZURE_VISION_AVAILABLE = True
except ImportError:
    AZURE_VISION_AVAILABLE = False
    logger.warning("Azure Computer Vision SDK not available. Install with: pip install azure-cognitiveservices-vision-computervision")

# Azure Key Vault for secrets
try:
    from azure.keyvault.secrets import SecretClient
    from azure.identity import DefaultAzureCredential
    AZURE_KV_AVAILABLE = True
except ImportError:
    AZURE_KV_AVAILABLE = False


class AzureCognitiveServicesIntegration:
    """Azure Cognitive Services integration for JARVIS/LUMINA"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_file = project_root / "config" / "azure_services_config.json"
        self.config = self.load_config()

        # Speech Services
        self.speech_config = None
        self.speech_recognizer = None

        # Text Analytics
        self.text_analytics_client = None

        # Computer Vision
        self.vision_client = None

        self._initialize_services()

    def load_config(self) -> Dict[str, Any]:
        """Load Azure services configuration"""
        default_config = {
            "cognitive_services": {
                "enabled": False,
                "services": {}
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    azure_config = data.get("azure_services_config", {})
                    if azure_config.get("cognitive_services"):
                        default_config["cognitive_services"].update(azure_config["cognitive_services"])
            except Exception as e:
                logger.error(f"Error loading Azure config: {e}")

        return default_config

    def _get_service_key(self, service_name: str) -> Optional[str]:
        """Get Cognitive Service key from Key Vault"""
        if AZURE_KV_AVAILABLE:
            try:
                vault_url = self.config.get("key_vault", {}).get("vault_url") or "https://jarvis-lumina.vault.azure.net/"
                secret_name = self.config.get("cognitive_services", {}).get("services", {}).get(service_name, {}).get("key_secret", f"cognitive-{service_name}-key")

                credential = DefaultAzureCredential(


                                    exclude_interactive_browser_credential=False,


                                    exclude_shared_token_cache_credential=False


                                )
                secret_client = SecretClient(vault_url=vault_url, credential=credential)
                key = secret_client.get_secret(secret_name).value
                return key
            except Exception as e:
                logger.debug(f"Could not get service key from Key Vault: {e}")

        import os
        return os.getenv(f"AZURE_COGNITIVE_{service_name.upper()}_KEY")

    def _get_service_endpoint(self, service_name: str) -> Optional[str]:
        """Get Cognitive Service endpoint"""
        service_config = self.config.get("cognitive_services", {}).get("services", {}).get(service_name, {})
        service_name_value = service_config.get("name", f"jarvis-lumina-{service_name}")
        location = self.config.get("location", "eastus")

        # Construct endpoint based on service type
        if service_name == "speech":
            return f"https://{location}.tts.speech.microsoft.com"
        elif service_name == "text_analytics":
            return f"https://{service_name_value}.cognitiveservices.azure.com/"
        elif service_name == "vision":
            return f"https://{service_name_value}.cognitiveservices.azure.com/"

        import os
        return os.getenv(f"AZURE_COGNITIVE_{service_name.upper()}_ENDPOINT")

    def _initialize_services(self):
        """Initialize all Cognitive Services"""
        if not self.config.get("cognitive_services", {}).get("enabled", False):
            logger.info("Azure Cognitive Services not enabled in config")
            return

        # Initialize Speech Services
        if AZURE_SPEECH_AVAILABLE:
            try:
                speech_key = self._get_service_key("speech")
                speech_endpoint = self._get_service_endpoint("speech")
                if speech_key:
                    self.speech_config = SpeechConfig(subscription=speech_key, region="eastus")
                    logger.info("✅ Azure Speech Services initialized")
            except Exception as e:
                logger.debug(f"Could not initialize Speech Services: {e}")

        # Initialize Text Analytics
        if AZURE_TEXT_ANALYTICS_AVAILABLE:
            try:
                text_key = self._get_service_key("text_analytics")
                text_endpoint = self._get_service_endpoint("text_analytics")
                if text_key and text_endpoint:
                    credential = AzureKeyCredential(text_key)
                    self.text_analytics_client = TextAnalyticsClient(endpoint=text_endpoint, credential=credential)
                    logger.info("✅ Azure Text Analytics initialized")
            except Exception as e:
                logger.debug(f"Could not initialize Text Analytics: {e}")

        # Initialize Computer Vision
        if AZURE_VISION_AVAILABLE:
            try:
                vision_key = self._get_service_key("vision")
                vision_endpoint = self._get_service_endpoint("vision")
                if vision_key and vision_endpoint:
                    credentials = CognitiveServicesCredentials(vision_key)
                    self.vision_client = ComputerVisionClient(vision_endpoint, credentials)
                    logger.info("✅ Azure Computer Vision initialized")
            except Exception as e:
                logger.debug(f"Could not initialize Computer Vision: {e}")

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of text"""
        if not self.text_analytics_client:
            return {
                "success": False,
                "error": "Text Analytics client not initialized"
            }

        try:
            response = self.text_analytics_client.analyze_sentiment([text])[0]
            return {
                "success": True,
                "sentiment": response.sentiment,
                "confidence_scores": {
                    "positive": response.confidence_scores.positive,
                    "neutral": response.confidence_scores.neutral,
                    "negative": response.confidence_scores.negative
                }
            }
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def extract_key_phrases(self, text: str) -> Dict[str, Any]:
        """Extract key phrases from text"""
        if not self.text_analytics_client:
            return {
                "success": False,
                "error": "Text Analytics client not initialized"
            }

        try:
            response = self.text_analytics_client.extract_key_phrases([text])[0]
            return {
                "success": True,
                "key_phrases": response.key_phrases
            }
        except Exception as e:
            logger.error(f"Error extracting key phrases: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_image(self, image_path: Path) -> Dict[str, Any]:
        """Analyze image using Computer Vision"""
        if not self.vision_client:
            return {
                "success": False,
                "error": "Computer Vision client not initialized"
            }

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Analyze image
            analysis = self.vision_client.analyze_image_in_stream(image_data, visual_features=['Categories', 'Description', 'Tags'])

            return {
                "success": True,
                "description": analysis.description.captions[0].text if analysis.description.captions else None,
                "tags": [tag.name for tag in analysis.tags],
                "categories": [cat.name for cat in analysis.categories]
            }
        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {
                "success": False,
                "error": str(e)
            }


def get_azure_cognitive_services(project_root: Path = None) -> AzureCognitiveServicesIntegration:
    try:
        """Get or create Azure Cognitive Services integration instance"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return AzureCognitiveServicesIntegration(project_root)


    except Exception as e:
        logger.error(f"Error in get_azure_cognitive_services: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # Test
    cognitive = get_azure_cognitive_services()
    print(f"Speech Services: {cognitive.speech_config is not None}")
    print(f"Text Analytics: {cognitive.text_analytics_client is not None}")
    print(f"Computer Vision: {cognitive.vision_client is not None}")
