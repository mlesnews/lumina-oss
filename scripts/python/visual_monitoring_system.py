#!/usr/bin/env python3
"""
Visual Monitoring System - Like OpenAI Atlas Operator

Monitors screen to see what's actually happening.
Uses screen capture to understand user intent and system state.

Tags: #VISUAL_MONITORING #ATLAS #SCREEN_CAPTURE #INTENT_DETECTION @JARVIS @LUMINA
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from drive_mapping_system import DriveMappingSystem
    from lumina_logger import get_logger
    from screen_capture_system import (SCREEN_CAPTURE_AVAILABLE,
                                       ScreenCaptureSystem)
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

# Try to import VLM integration
try:
    from vlm_integration import VLMIntegration
    VLM_AVAILABLE = True
except ImportError:
    VLM_AVAILABLE = False
    VLMIntegration = None

# Try to import OCR and CV libraries
try:
    import cv2
    import numpy as np
    import pytesseract
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    pytesseract = None
    cv2 = None
    np = None

logger = get_logger("VisualMonitoring")


class VisualMonitoringSystem:
    """
    Visual Monitoring System - Like OpenAI Atlas Operator

    Features:
    - Screen monitoring
    - Intent detection from visual context
    - Real-time screen capture
    - Video storage on NAS
    - Understanding what's actually on screen
    """

    def __init__(self, use_vlm: bool = True, vlm_provider: str = "local", vlm_model: Optional[str] = None):
        """
        Initialize visual monitoring system

        Args:
            use_vlm: Whether to use Vision Language Model for analysis (default: True, uses local)
            vlm_provider: VLM provider ("local" - default, "openai", "anthropic", "google")
            vlm_model: Specific VLM model name (optional, defaults to local model)
        """
        self.capture = ScreenCaptureSystem()
        self.drive_mapping = DriveMappingSystem()

        # Monitoring state
        self.monitoring = False
        self.screenshots: List[Path] = []
        self.observations: List[Dict[str, Any]] = []

        # VLM integration
        self.use_vlm = use_vlm and VLM_AVAILABLE
        self.vlm: Optional[VLMIntegration] = None
        if self.use_vlm:
            try:
                self.vlm = VLMIntegration(provider=vlm_provider, model=vlm_model)
            except Exception as e:
                logger.warning(f"Could not initialize VLM: {e}")
                self.use_vlm = False

        logger.info("=" * 80)
        logger.info("👁️  VISUAL MONITORING SYSTEM")
        logger.info("=" * 80)
        logger.info("   Like OpenAI Atlas Operator")
        logger.info("   Monitoring screen to understand intent")
        logger.info(f"   Screen Capture Available: {SCREEN_CAPTURE_AVAILABLE}")
        logger.info(f"   OCR Available: {OCR_AVAILABLE}")
        logger.info(f"   VLM Available: {self.use_vlm}")
        logger.info("=" * 80)

    def start_monitoring(self, session_name: Optional[str] = None):
        """Start visual monitoring"""
        if self.monitoring:
            logger.warning("Monitoring already active")
            return

        self.monitoring = True

        # Start recording
        video_path = self.capture.start_recording(session_name)

        logger.info("👁️  Started visual monitoring")
        logger.info(f"   Recording to: {video_path}")

    def stop_monitoring(self):
        """Stop visual monitoring"""
        if not self.monitoring:
            return

        self.monitoring = False

        # Stop recording
        video_path = self.capture.stop_recording()

        logger.info("👁️  Stopped visual monitoring")
        if video_path:
            logger.info(f"   Recording saved to: {video_path}")

    def capture_observation(self, description: Optional[str] = None) -> Dict[str, Any]:
        """Capture current screen state as observation"""
        # Capture screenshot
        screenshot_path = self.capture.capture_screenshot()
        self.screenshots.append(screenshot_path)

        observation = {
            "timestamp": datetime.now().isoformat(),
            "screenshot": str(screenshot_path),
            "description": description or "Screen observation",
            "monitoring": self.monitoring
        }

        self.observations.append(observation)

        logger.info(f"📸 Captured observation: {observation['description']}")
        return observation

    def extract_text_from_screen(self, screenshot_path: Optional[Path] = None) -> Dict[str, Any]:
        """Extract text from screen using OCR"""
        if not OCR_AVAILABLE:
            logger.warning("OCR not available. Install: pip install --user pytesseract")
            return {"text": "", "words": [], "confidence": 0.0, "available": False}

        if not screenshot_path:
            # Capture new screenshot
            screenshot_path = self.capture.capture_screenshot()

        if not screenshot_path or not screenshot_path.exists():
            logger.warning("Screenshot not available for OCR")
            return {"text": "", "words": [], "confidence": 0.0, "available": False}

        try:
            # Load image
            img = Image.open(str(screenshot_path))

            # Try to find tesseract executable
            try:
                # Perform OCR
                ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            except Exception as tess_error:
                # Try common Windows installation paths
                tesseract_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                    rf"C:\Users\{Path.home().name}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
                ]

                tesseract_found = False
                for tess_path in tesseract_paths:
                    if Path(tess_path).exists():
                        pytesseract.pytesseract.tesseract_cmd = tess_path
                        tesseract_found = True
                        break

                if tesseract_found:
                    # Retry OCR
                    ocr_data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
                else:
                    raise tess_error

            # Extract text and confidence
            text_parts = []
            words = []
            confidences = []

            for i, word in enumerate(ocr_data.get('text', [])):
                if word.strip():
                    conf = int(ocr_data.get('conf', [0])[i])
                    if conf > 0:  # Only include words with confidence > 0
                        text_parts.append(word)
                        words.append({
                            "text": word,
                            "confidence": conf,
                            "left": ocr_data.get('left', [0])[i],
                            "top": ocr_data.get('top', [0])[i],
                            "width": ocr_data.get('width', [0])[i],
                            "height": ocr_data.get('height', [0])[i]
                        })
                        confidences.append(conf)

            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0

            result = {
                "text": full_text,
                "words": words,
                "confidence": avg_confidence,
                "word_count": len(words),
                "available": True
            }

            logger.info(f"📝 Extracted {len(words)} words from screen (avg confidence: {avg_confidence:.1f}%)")
            return result

        except Exception as e:
            logger.error(f"Error during OCR: {e}")
            return {"text": "", "words": [], "confidence": 0.0, "available": False, "error": str(e)}

    def analyze_screen_with_cv(self, screenshot_path: Optional[Path] = None) -> Dict[str, Any]:
        """Analyze screen using computer vision"""
        if not OCR_AVAILABLE or cv2 is None:
            logger.warning("Computer vision not available")
            return {"ui_elements": [], "colors": {}, "edges": 0, "available": False}

        if not screenshot_path:
            screenshot_path = self.capture.capture_screenshot()

        if not screenshot_path or not screenshot_path.exists():
            logger.warning("Screenshot not available for CV analysis")
            return {"ui_elements": [], "colors": {}, "edges": 0, "available": False}

        try:
            # Load image with OpenCV
            img = cv2.imread(str(screenshot_path))
            if img is None:
                return {"ui_elements": [], "colors": {}, "edges": 0, "available": False}

            height, width = img.shape[:2]

            # Convert to different color spaces for analysis
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_count = int(np.sum(edges > 0))

            # Detect contours (potential UI elements)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            ui_elements = []
            for i, contour in enumerate(contours[:20]):  # Limit to top 20
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small noise
                    x, y, w, h = cv2.boundingRect(contour)
                    ui_elements.append({
                        "id": i,
                        "x": int(x),
                        "y": int(y),
                        "width": int(w),
                        "height": int(h),
                        "area": float(area)
                    })

            # Color analysis (dominant colors)
            pixels = img.reshape(-1, 3)
            unique_colors = len(np.unique(pixels, axis=0))

            # Calculate average brightness
            avg_brightness = float(np.mean(gray))

            result = {
                "ui_elements": ui_elements,
                "element_count": len(ui_elements),
                "screen_size": {"width": int(width), "height": int(height)},
                "edges": edge_count,
                "unique_colors": int(unique_colors),
                "avg_brightness": avg_brightness,
                "available": True
            }

            logger.info(f"🔍 Detected {len(ui_elements)} UI elements, {edge_count} edges")
            return result

        except Exception as e:
            logger.error(f"Error during CV analysis: {e}")
            return {"ui_elements": [], "colors": {}, "edges": 0, "available": False, "error": str(e)}

    def detect_intent_from_screen(self) -> Dict[str, Any]:
        """Detect user intent from what's on screen"""
        # Capture current state
        observation = self.capture_observation("Intent detection")
        screenshot_path = Path(observation["screenshot"]) if observation.get("screenshot") else None

        # Try VLM first if available (better understanding)
        vlm_result: Optional[Dict[str, Any]] = None
        if self.use_vlm and self.vlm and screenshot_path:
            logger.info("🤖 Using VLM for screen analysis...")
            vlm_result = self.vlm.analyze_screen_with_vlm(
                screenshot_path,
                prompt="Analyze this screen. What is the user trying to do? What UI elements are visible? Are there any errors, loading states, or important information?"
            )
            if vlm_result.get("available"):
                logger.info("✅ VLM analysis complete")

        # Extract text using OCR (fallback or supplement)
        ocr_result = self.extract_text_from_screen(screenshot_path)

        # Analyze screen with computer vision (fallback or supplement)
        cv_result = self.analyze_screen_with_cv(screenshot_path)

        # Analyze text for intent patterns
        intent_type = "unknown"
        confidence = 0.0
        suggested_action = None

        # Use VLM result if available (much better understanding)
        if vlm_result and vlm_result.get("available"):
            analysis = vlm_result.get("analysis", "").lower()

            # Extract intent from VLM analysis
            if any(keyword in analysis for keyword in ["error", "failed", "exception", "crash", "problem"]):
                intent_type = "error_detected"
                confidence = 0.9
                suggested_action = "VLM detected an error - investigate the issue"
            elif any(keyword in analysis for keyword in ["loading", "waiting", "processing", "please wait"]):
                intent_type = "waiting"
                confidence = 0.8
                suggested_action = "VLM detected a loading/waiting state"
            elif any(keyword in analysis for keyword in ["success", "completed", "done", "finished"]):
                intent_type = "success"
                confidence = 0.8
                suggested_action = "VLM detected successful completion"
            elif any(keyword in analysis for keyword in ["login", "password", "sign in", "authenticate", "authentication"]):
                intent_type = "authentication"
                confidence = 0.9
                suggested_action = "VLM detected authentication required"
            elif any(keyword in analysis for keyword in ["button", "click", "form", "input"]):
                intent_type = "user_interaction"
                confidence = 0.7
                suggested_action = "VLM detected interactive elements"
            else:
                intent_type = "general"
                confidence = 0.6
                suggested_action = f"VLM analysis: {analysis[:100]}..."

        # Fallback to OCR-based detection if VLM not available
        elif ocr_result.get("available") and ocr_result.get("text"):
            text = ocr_result["text"].lower()

            # Pattern matching for common intents
            if any(keyword in text for keyword in ["error", "failed", "exception", "crash"]):
                intent_type = "error_detected"
                confidence = 0.7
                suggested_action = "Investigate error message"
            elif any(keyword in text for keyword in ["loading", "please wait", "processing"]):
                intent_type = "waiting"
                confidence = 0.6
                suggested_action = "Wait for process to complete"
            elif any(keyword in text for keyword in ["success", "completed", "done", "finished"]):
                intent_type = "success"
                confidence = 0.7
                suggested_action = "Task completed successfully"
            elif any(keyword in text for keyword in ["login", "password", "sign in", "authenticate"]):
                intent_type = "authentication"
                confidence = 0.8
                suggested_action = "User needs to authenticate"
            elif any(keyword in text for keyword in ["save", "export", "download"]):
                intent_type = "file_operation"
                confidence = 0.6
                suggested_action = "File operation in progress"
            elif len(ocr_result.get("words", [])) > 50:
                intent_type = "text_content"
                confidence = 0.5
                suggested_action = "Screen contains significant text content"
            else:
                intent_type = "general"
                confidence = 0.3
                suggested_action = "General screen content"

        # Use CV results to refine intent
        if cv_result.get("available"):
            if cv_result.get("element_count", 0) > 10:
                # Many UI elements suggest active application
                if intent_type == "unknown":
                    intent_type = "active_application"
                    confidence = 0.4
                    suggested_action = "Active application window detected"

        detected = intent_type != "unknown" and confidence > 0.3

        intent = {
            "detected": detected,
            "confidence": confidence,
            "intent_type": intent_type,
            "screen_content": {
                "text": ocr_result.get("text", ""),
                "word_count": ocr_result.get("word_count", 0),
                "ui_elements": cv_result.get("element_count", 0),
                "ocr_confidence": ocr_result.get("confidence", 0.0)
            },
            "suggested_action": suggested_action,
            "observation": observation,
            "ocr_result": ocr_result,
            "cv_result": cv_result,
            "vlm_result": vlm_result if vlm_result else None,
            "method": "vlm" if (vlm_result and vlm_result.get("available")) else "ocr_cv"
        }

        if detected:
            logger.info(f"🔍 Intent detected: {intent_type} (confidence: {confidence:.1%})")
        else:
            logger.info("🔍 No clear intent detected from screen")

        return intent

    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get monitoring system status"""
        return {
            "monitoring": self.monitoring,
            "recording": self.capture.recording,
            "screenshots_captured": len(self.screenshots),
            "observations": len(self.observations),
            "storage_info": self.capture.get_storage_info(),
            "current_recording": str(self.capture.current_recording_path) if self.capture.current_recording_path else None
        }


def main():
    """Main function"""
    print("=" * 80)
    print("👁️  VISUAL MONITORING SYSTEM")
    print("=" * 80)
    print()
    print("Like OpenAI Atlas Operator:")
    print("  • Monitors screen to see what's actually happening")
    print("  • Captures screenshots and video")
    print("  • Detects intent from visual context")
    print("  • Stores videos on NAS (V: drive)")
    print()

    monitoring = VisualMonitoringSystem()

    # Show status
    status = monitoring.get_monitoring_status()
    print("Monitoring Status:")
    print(f"  Active: {status['monitoring']}")
    print(f"  Recording: {status['recording']}")
    print(f"  Storage: {status['storage_info']['storage_path']}")
    print()

    print("=" * 80)
    print("✅ VISUAL MONITORING SYSTEM READY")
    print("=" * 80)
    print()
    print("To start monitoring:")
    print("  monitoring.start_monitoring()")
    print()
    print("To capture observation:")
    print("  monitoring.capture_observation('What I see on screen')")
    print()
    print("To detect intent:")
    print("  monitoring.detect_intent_from_screen()")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()