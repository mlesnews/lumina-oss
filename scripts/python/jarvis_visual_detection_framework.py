#!/usr/bin/env python3
"""
JARVIS Visual Detection Framework

Uses MDV (Manus Desktop Video) to visually detect JARVIS instances on desktop.
Implements the knowledge we have about what JARVIS looks like.

Tags: #JARVIS #MDV #VISUAL_DETECTION #FRAMEWORK @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass

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

logger = get_logger("JARVISVisualDetection")


@dataclass
class JARVISVisualCriteria:
    """What we KNOW JARVIS looks like - from the beginning"""
    # Colors (from drawing code)
    primary_color: str = "#00ccff"  # JARVIS cyan
    text_color: str = "#00ccff"     # JARVIS name text
    subtitle_color: str = "#00ccff"  # "Intelligent Assistant" text

    # Text patterns (from drawing code)
    name_text: str = "J.A.R.V.I.S"  # Exact text pattern
    subtitle_text: str = "Intelligent Assistant"

    # Shape characteristics (from drawing code)
    is_circular: bool = True  # JARVIS face is circular
    min_radius: int = 50      # Minimum window size
    max_radius: int = 200     # Maximum window size
    circularity_threshold: float = 0.7  # How circular (0-1)

    # Size characteristics
    window_width: int = 300   # Typical JARVIS window width
    window_height: int = 300  # Typical JARVIS window height

    # Visual features
    has_eye: bool = True      # Central eye
    has_gradient_rings: bool = True  # Multiple gradient rings
    has_hud_elements: bool = True    # HUD arcs and lines


class JARVISVisualDetectionFramework:
    """Framework to detect JARVIS using visual knowledge we have"""

    def __init__(self):
        self.criteria = JARVISVisualCriteria()
        self.mdv_available = False
        self._initialize_mdv()

    def _initialize_mdv(self):
        """Initialize MDV (Manus Desktop Video) for visual detection"""
        try:
            import pyautogui
            import cv2
            import numpy as np
            self.pyautogui = pyautogui
            self.cv2 = cv2
            self.np = np
            self.mdv_available = True
            logger.info("✅ MDV initialized for visual detection")
        except ImportError as e:
            logger.warning(f"⚠️  MDV dependencies not available: {e}")
            logger.warning("   Install: pip install pyautogui opencv-python numpy")
            self.mdv_available = False

    def detect_jarvis_instances(self) -> List[Dict]:
        """Detect all JARVIS instances on desktop using visual criteria"""
        if not self.mdv_available:
            logger.warning("⚠️  MDV not available - cannot detect visually")
            return []

        try:
            # Capture full desktop
            screenshot = self.pyautogui.screenshot()
            screen_array = self.np.array(screenshot)

            # Convert to different color spaces for detection
            rgb = screen_array
            hsv = self.cv2.cvtColor(rgb, self.cv2.COLOR_RGB2HSV)
            gray = self.cv2.cvtColor(rgb, self.cv2.COLOR_RGB2GRAY)

            # Detect using multiple criteria
            detections = []

            # Method 1: Color-based detection (JARVIS cyan)
            cyan_regions = self._detect_cyan_regions(hsv)

            # Method 2: Shape-based detection (circular faces)
            circular_regions = self._detect_circular_regions(gray, cyan_regions)

            # Method 3: Text-based detection ("J.A.R.V.I.S")
            text_regions = self._detect_text_regions(rgb)

            # Combine detections (regions that match multiple criteria)
            for region in circular_regions:
                # Check if region also has text nearby
                has_text = self._region_has_text(region, text_regions)

                # Check if region matches size criteria
                matches_size = self._matches_size_criteria(region)

                if has_text or matches_size:
                    detections.append({
                        "center": region["center"],
                        "radius": region["radius"],
                        "confidence": self._calculate_confidence(region, has_text, matches_size),
                        "bbox": region["bbox"]
                    })

            logger.info(f"👁️  MDV Visual Detection: Found {len(detections)} JARVIS instance(s)")
            return detections

        except Exception as e:
            logger.error(f"Error in visual detection: {e}")
            return []

    def _detect_cyan_regions(self, hsv) -> List[Dict]:
        """Detect cyan regions (JARVIS signature color)"""
        # Convert hex color to HSV
        # #00ccff in RGB = (0, 204, 255)
        # In HSV: approximately (180, 255, 255) but OpenCV uses (0-179, 0-255, 0-255)
        # Cyan in OpenCV HSV: around (85-105, 100-255, 100-255)
        lower_cyan = self.np.array([85, 100, 100])
        upper_cyan = self.np.array([105, 255, 255])

        mask = self.cv2.inRange(hsv, lower_cyan, upper_cyan)

        # Find contours
        contours, _ = self.cv2.findContours(mask, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE)

        regions = []
        for contour in contours:
            area = self.cv2.contourArea(contour)
            if area > 100:  # Minimum area
                M = self.cv2.moments(contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    x, y, w, h = self.cv2.boundingRect(contour)
                    regions.append({
                        "center": (cx, cy),
                        "area": area,
                        "bbox": (x, y, w, h)
                    })

        return regions

    def _detect_circular_regions(self, gray, cyan_regions: List[Dict]) -> List[Dict]:
        """Detect circular regions matching JARVIS face shape"""
        circular_regions = []

        for region in cyan_regions:
            # Calculate circularity
            # Get contour for this region
            x, y, w, h = region["bbox"]

            # Extract region
            if y + h < gray.shape[0] and x + w < gray.shape[1]:
                region_gray = gray[y:y+h, x:x+w]

                # Find contours in this region
                contours, _ = self.cv2.findContours(
                    region_gray, self.cv2.RETR_EXTERNAL, self.cv2.CHAIN_APPROX_SIMPLE
                )

                for contour in contours:
                    area = self.cv2.contourArea(contour)
                    if area > 0:
                        perimeter = self.cv2.arcLength(contour, True)
                        if perimeter > 0:
                            circularity = 4 * self.np.pi * area / (perimeter * perimeter)

                            if circularity >= self.criteria.circularity_threshold:
                                radius = self.np.sqrt(area / self.np.pi)
                                if self.criteria.min_radius <= radius <= self.criteria.max_radius:
                                    circular_regions.append({
                                        "center": region["center"],
                                        "radius": radius,
                                        "circularity": circularity,
                                        "bbox": region["bbox"],
                                        "area": area
                                    })

        return circular_regions

    def _detect_text_regions(self, rgb) -> List[Dict]:
        """Detect text regions containing 'J.A.R.V.I.S' or 'Intelligent Assistant'"""
        # For now, use simple pattern matching
        # In production, could use OCR (pytesseract) or ML text detection
        text_regions = []

        # Look for text patterns in image
        # This is a simplified version - full implementation would use OCR
        try:
            # Try OCR if available
            import pytesseract
            from PIL import Image

            pil_image = Image.fromarray(rgb)
            # Get text from image
            text = pytesseract.image_to_string(pil_image)

            # Search for JARVIS text patterns
            if "J.A.R.V.I.S" in text or "JARVIS" in text:
                # Get bounding boxes for text
                boxes = pytesseract.image_to_boxes(pil_image)
                for box in boxes.splitlines():
                    if "J" in box or "A" in box or "R" in box or "V" in box or "I" in box or "S" in box:
                        parts = box.split()
                        if len(parts) >= 6:
                            x, y, w, h = int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])
                            text_regions.append({
                                "bbox": (x, y, w, h),
                                "text": parts[0]
                            })
        except ImportError:
            # OCR not available - use fallback
            logger.debug("OCR not available - using fallback text detection")

        return text_regions

    def _region_has_text(self, region: Dict, text_regions: List[Dict]) -> bool:
        """Check if region has text nearby"""
        rx, ry, rw, rh = region["bbox"]
        region_center_x = rx + rw // 2
        region_center_y = ry + rh // 2

        for text_region in text_regions:
            tx, ty, tw, th = text_region["bbox"]
            text_center_x = tx + tw // 2
            text_center_y = ty + th // 2

            # Check if text is within reasonable distance of region
            distance = self.np.sqrt(
                (region_center_x - text_center_x)**2 + 
                (region_center_y - text_center_y)**2
            )

            if distance < region["radius"] * 2:  # Text within 2x radius
                return True

        return False

    def _matches_size_criteria(self, region: Dict) -> bool:
        """Check if region matches JARVIS size criteria"""
        radius = region.get("radius", 0)
        return self.criteria.min_radius <= radius <= self.criteria.max_radius

    def _calculate_confidence(self, region: Dict, has_text: bool, matches_size: bool) -> float:
        """Calculate detection confidence (0-1)"""
        confidence = 0.5  # Base confidence

        if has_text:
            confidence += 0.3  # Text match increases confidence

        if matches_size:
            confidence += 0.2  # Size match increases confidence

        # Circularity bonus
        circularity = region.get("circularity", 0)
        if circularity > 0.8:
            confidence += 0.1

        return min(1.0, confidence)

    def count_jarvis_instances(self) -> int:
        """Count JARVIS instances on desktop"""
        detections = self.detect_jarvis_instances()
        return len(detections)

    def verify_all_closed(self) -> bool:
        """Verify all JARVIS windows are closed"""
        count = self.count_jarvis_instances()
        return count == 0


# Singleton instance
_detection_framework_instance = None

def get_jarvis_visual_detection_framework():
    """Get singleton instance of visual detection framework"""
    global _detection_framework_instance
    if _detection_framework_instance is None:
        _detection_framework_instance = JARVISVisualDetectionFramework()
    return _detection_framework_instance
