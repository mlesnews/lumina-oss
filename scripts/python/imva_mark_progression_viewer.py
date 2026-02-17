#!/usr/bin/env python3
"""
IMVA Mark Progression Viewer

Displays Iron Man Virtual Assistant Mark I through Mark VII to ULTRON progression,
showing increasing complexity and skill levels, mirroring ASUS Armoury Crate API.

Features:
- Visual progression of all Marks (I-VII) and ULTRON
- Skill/complexity indicators
- Feature comparison
- ASUS Armoury Crate API integration
- Live status of each Mark
- Interactive progression viewer

Tags: #IMVA #MARK_PROGRESSION #ARMOURY_CRATE #ULTRON @JARVIS @LUMINA
"""

import sys
import time
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("IMVAMarkProgressionViewer")


class MarkLevel(Enum):
    """Mark progression levels"""
    MARK_I = 1
    MARK_II = 2
    MARK_III = 3
    MARK_IV = 4
    MARK_V = 5
    MARK_VI = 6
    MARK_VII = 7
    ULTRON = 8


@dataclass
class MarkSpecification:
    """Mark specification with features and capabilities"""
    mark: MarkLevel
    name: str
    model_name: str
    system: str
    endpoint: str
    description: str
    complexity_level: int  # 1-10
    skill_level: int  # 1-10
    features: List[str] = field(default_factory=list)
    capabilities: Dict[str, Any] = field(default_factory=dict)
    visual_style: Dict[str, Any] = field(default_factory=dict)
    armoury_crate_compatible: bool = True


class IMVAMarkProgressionViewer:
    """IMVA Mark Progression Viewer with ASUS Armoury Crate integration"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.marks = self._define_marks()
        self.armoury_crate_api = self._init_armoury_crate_api()

    def _define_marks(self) -> Dict[MarkLevel, MarkSpecification]:
        """Define all Mark specifications with increasing complexity"""
        marks = {}

        # Mark I - Basic prototype
        marks[MarkLevel.MARK_I] = MarkSpecification(
            mark=MarkLevel.MARK_I,
            name="Mark I",
            model_name="codellama:13b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="Basic prototype - Primary code generation",
            complexity_level=3,
            skill_level=2,
            features=[
                "Basic code generation",
                "Simple responses",
                "Text-only interface"
            ],
            capabilities={
                "code_generation": "basic",
                "reasoning": "simple",
                "context_window": "small",
                "multimodal": False
            },
            visual_style={
                "color": "#8B0000",  # Dark red
                "glow": "minimal",
                "animations": "basic"
            }
        )

        # Mark II - Enhanced general
        marks[MarkLevel.MARK_II] = MarkSpecification(
            mark=MarkLevel.MARK_II,
            name="Mark II",
            model_name="llama3.2:11b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="Enhanced general purpose - Secondary general",
            complexity_level=4,
            skill_level=3,
            features=[
                "Enhanced code generation",
                "Better reasoning",
                "Improved context handling"
            ],
            capabilities={
                "code_generation": "enhanced",
                "reasoning": "improved",
                "context_window": "medium",
                "multimodal": False
            },
            visual_style={
                "color": "#DC143C",  # Crimson
                "glow": "moderate",
                "animations": "smooth"
            }
        )

        # Mark III - Lightweight quick
        marks[MarkLevel.MARK_III] = MarkSpecification(
            mark=MarkLevel.MARK_III,
            name="Mark III",
            model_name="qwen2.5-coder:1.5b-base",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="Lightweight quick response - Fast inference",
            complexity_level=5,
            skill_level=4,
            features=[
                "Fast inference",
                "Optimized for speed",
                "Quick responses"
            ],
            capabilities={
                "code_generation": "fast",
                "reasoning": "quick",
                "context_window": "small",
                "multimodal": False,
                "speed": "high"
            },
            visual_style={
                "color": "#FF4500",  # Orange Red
                "glow": "moderate",
                "animations": "fast"
            }
        )

        # Mark IV - General purpose
        marks[MarkLevel.MARK_IV] = MarkSpecification(
            mark=MarkLevel.MARK_IV,
            name="Mark IV",
            model_name="llama3:8b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="General purpose - Balanced performance",
            complexity_level=6,
            skill_level=5,
            features=[
                "Balanced performance",
                "General purpose reasoning",
                "Good context handling"
            ],
            capabilities={
                "code_generation": "balanced",
                "reasoning": "general",
                "context_window": "medium",
                "multimodal": False
            },
            visual_style={
                "color": "#FF6347",  # Tomato
                "glow": "enhanced",
                "animations": "smooth"
            }
        )

        # Mark V - General reasoning (Hot Rod Red)
        marks[MarkLevel.MARK_V] = MarkSpecification(
            mark=MarkLevel.MARK_V,
            name="Mark V",
            model_name="mistral:7b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="General reasoning - Advanced capabilities",
            complexity_level=7,
            skill_level=6,
            features=[
                "Advanced reasoning",
                "Better code quality",
                "Enhanced understanding"
            ],
            capabilities={
                "code_generation": "advanced",
                "reasoning": "enhanced",
                "context_window": "large",
                "multimodal": False
            },
            visual_style={
                "color": "#DC143C",  # Hot Rod Red (Crimson)
                "glow": "#FFD700",  # Gold glow
                "animations": "advanced",
                "special": "Hot Rod Red and Gold"
            }
        )

        # Mark VI - High complexity
        marks[MarkLevel.MARK_VI] = MarkSpecification(
            mark=MarkLevel.MARK_VI,
            name="Mark VI",
            model_name="mixtral-8x7b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="High complexity - Expert level",
            complexity_level=8,
            skill_level=7,
            features=[
                "Expert level reasoning",
                "Complex problem solving",
                "Advanced code generation"
            ],
            capabilities={
                "code_generation": "expert",
                "reasoning": "complex",
                "context_window": "very_large",
                "multimodal": False
            },
            visual_style={
                "color": "#B22222",  # Fire Brick
                "glow": "#FFD700",  # Gold
                "animations": "expert"
            }
        )

        # Mark VII - Lightweight fallback
        marks[MarkLevel.MARK_VII] = MarkSpecification(
            mark=MarkLevel.MARK_VII,
            name="Mark VII",
            model_name="gemma:2b",
            system="KAIJU",
            endpoint="http://<NAS_PRIMARY_IP>:11434",
            description="Lightweight fallback - Efficient",
            complexity_level=9,
            skill_level=8,
            features=[
                "Efficient operation",
                "Resource optimized",
                "Reliable fallback"
            ],
            capabilities={
                "code_generation": "efficient",
                "reasoning": "optimized",
                "context_window": "medium",
                "multimodal": False,
                "efficiency": "high"
            },
            visual_style={
                "color": "#DC143C",  # Crimson
                "glow": "#FFD700",  # Gold
                "animations": "efficient"
            }
        )

        # ULTRON - Ultimate AI
        marks[MarkLevel.ULTRON] = MarkSpecification(
            mark=MarkLevel.ULTRON,
            name="ULTRON",
            model_name="qwen2.5:72b",
            system="ULTRON",
            endpoint="http://localhost:11434",
            description="ULTRON Virtual Hybrid Cluster - Ultimate AI",
            complexity_level=10,
            skill_level=10,
            features=[
                "Ultimate AI capabilities",
                "Full JARVIS integration",
                "Complete Lumina ecosystem",
                "SYPHON intelligence",
                "R5 context aggregation",
                "Advanced reasoning",
                "Expert code generation",
                "Multimodal support"
            ],
            capabilities={
                "code_generation": "ultimate",
                "reasoning": "ultimate",
                "context_window": "maximum",
                "multimodal": True,
                "jarvis_integration": True,
                "syphon_integration": True,
                "r5_integration": True,
                "lumina_ecosystem": True
            },
            visual_style={
                "color": "#FF0000",  # Bright Red
                "glow": "#FFD700",  # Gold
                "animations": "ultimate",
                "special": "ULTRON Virtual Hybrid Cluster"
            }
        )

        return marks

    def _init_armoury_crate_api(self) -> Optional[Dict[str, Any]]:
        """Initialize ASUS Armoury Crate API integration"""
        # Check for Armoury Crate API availability
        # This would typically connect to local Armoury Crate service
        api_config = {
            "available": False,
            "endpoint": "http://localhost:8080/api",  # Typical AC API endpoint
            "features": []
        }

        try:
            # Try to connect to Armoury Crate API
            response = requests.get(f"{api_config['endpoint']}/status", timeout=2)
            if response.status_code == 200:
                api_config["available"] = True
                api_config["features"] = response.json().get("features", [])
                logger.info("✅ ASUS Armoury Crate API connected")
        except Exception as e:
            logger.debug(f"Armoury Crate API not available: {e}")

        return api_config

    def check_mark_status(self, mark: MarkSpecification) -> Dict[str, Any]:
        """Check status of a specific Mark"""
        status = {
            "mark": mark.name,
            "available": False,
            "endpoint": mark.endpoint,
            "model": mark.model_name,
            "system": mark.system
        }

        try:
            # Check if endpoint is available
            response = requests.get(f"{mark.endpoint}/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                status["available"] = any(m.get("name") == mark.model_name for m in models)
                status["models_available"] = len(models)
        except Exception as e:
            status["error"] = str(e)

        return status

    def display_progression(self):
        """Display the full Mark progression"""
        print("\n" * 2)
        print("=" * 100)
        print("IRON MAN VIRTUAL ASSISTANT - MARK PROGRESSION".center(100))
        print("=" * 100)
        print()
        print("Progression: Mark I → Mark II → Mark III → Mark IV → Mark V → Mark VI → Mark VII → ULTRON")
        print()
        print("=" * 100)
        print()

        for level in sorted(MarkLevel, key=lambda x: x.value):
            mark = self.marks[level]
            status = self.check_mark_status(mark)

            # Mark header
            print(f"┌{'─' * 98}┐")
            print(f"│ {mark.name:20} │ Complexity: {mark.complexity_level}/10 │ Skill: {mark.skill_level}/10 │ Status: {'✅' if status.get('available') else '❌'} │")
            print(f"├{'─' * 98}┤")

            # Model info
            print(f"│ Model: {mark.model_name:50} │ System: {mark.system:15} │")
            print(f"│ Description: {mark.description:80} │")

            # Features
            print(f"│ Features: {', '.join(mark.features[:3]):85} │")
            if len(mark.features) > 3:
                print(f"│          {', '.join(mark.features[3:]):85} │")

            # Capabilities
            print(f"│ Capabilities:")
            for cap_name, cap_value in list(mark.capabilities.items())[:3]:
                print(f"│   • {cap_name}: {cap_value:80} │")

            # Visual style
            print(f"│ Visual: Color={mark.visual_style.get('color', 'N/A'):15} │ Glow={mark.visual_style.get('glow', 'N/A'):15} │ Animations={mark.visual_style.get('animations', 'N/A'):15} │")

            # Status
            if status.get("available"):
                print(f"│ Status: ✅ Available │ Models: {status.get('models_available', 0)} │")
            else:
                error = status.get("error", "Not available")
                print(f"│ Status: ❌ {error[:80]:80} │")

            # Armoury Crate compatibility
            if mark.armoury_crate_compatible:
                print(f"│ Armoury Crate: ✅ Compatible │")

            print(f"└{'─' * 98}┘")
            print()

        # Summary
        print("=" * 100)
        print("PROGRESSION SUMMARY".center(100))
        print("=" * 100)
        print()

        total_marks = len(self.marks)
        available_marks = sum(1 for level in MarkLevel if self.check_mark_status(self.marks[level]).get("available"))

        print(f"Total Marks: {total_marks}")
        print(f"Available: {available_marks}/{total_marks}")
        print(f"Progression: Mark I (Basic) → ULTRON (Ultimate)")
        print()

        # Complexity progression
        print("Complexity Progression:")
        for level in sorted(MarkLevel, key=lambda x: x.value):
            mark = self.marks[level]
            bar = "█" * mark.complexity_level + "░" * (10 - mark.complexity_level)
            print(f"  {mark.name:10} [{bar}] {mark.complexity_level}/10")

        print()

        # Skill progression
        print("Skill Progression:")
        for level in sorted(MarkLevel, key=lambda x: x.value):
            mark = self.marks[level]
            bar = "█" * mark.skill_level + "░" * (10 - mark.skill_level)
            print(f"  {mark.name:10} [{bar}] {mark.skill_level}/10")

        print()
        print("=" * 100)
        print()

        # Armoury Crate integration
        if self.armoury_crate_api.get("available"):
            print("✅ ASUS Armoury Crate API: Connected")
            print(f"   Features: {', '.join(self.armoury_crate_api.get('features', []))}")
        else:
            print("ℹ️  ASUS Armoury Crate API: Not available (running standalone)")

        print()
        print("=" * 100)

    def export_progression_json(self, output_file: Path):
        try:
            """Export progression data to JSON"""
            progression_data = {
                "timestamp": datetime.now().isoformat(),
                "marks": {},
                "armoury_crate": self.armoury_crate_api
            }

            for level, mark in self.marks.items():
                status = self.check_mark_status(mark)
                progression_data["marks"][mark.name] = {
                    "mark_level": mark.mark.value,
                    "name": mark.name,
                    "model_name": mark.model_name,
                    "system": mark.system,
                    "endpoint": mark.endpoint,
                    "description": mark.description,
                    "complexity_level": mark.complexity_level,
                    "skill_level": mark.skill_level,
                    "features": mark.features,
                    "capabilities": mark.capabilities,
                    "visual_style": mark.visual_style,
                    "armoury_crate_compatible": mark.armoury_crate_compatible,
                    "status": status
                }

            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(progression_data, f, indent=2)

            logger.info(f"✅ Progression data exported: {output_file.name}")


        except Exception as e:
            self.logger.error(f"Error in export_progression_json: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="IMVA Mark Progression Viewer")
    parser.add_argument("--display", action="store_true", help="Display progression")
    parser.add_argument("--export", type=str, help="Export to JSON file")
    parser.add_argument("--mark", type=str, help="Show specific mark (Mark I-VII or ULTRON)")

    args = parser.parse_args()

    viewer = IMVAMarkProgressionViewer(project_root)

    if args.mark:
        # Show specific mark
        mark_name = args.mark.upper().replace(" ", "_")
        try:
            mark_level = MarkLevel[mark_name]
            mark = viewer.marks[mark_level]
            status = viewer.check_mark_status(mark)

            print(f"\n{mark.name} - Detailed Information")
            print("=" * 80)
            print(f"Model: {mark.model_name}")
            print(f"System: {mark.system}")
            print(f"Complexity: {mark.complexity_level}/10")
            print(f"Skill: {mark.skill_level}/10")
            print(f"Status: {'✅ Available' if status.get('available') else '❌ Not Available'}")
            print(f"\nFeatures: {', '.join(mark.features)}")
            print(f"\nCapabilities:")
            for cap, value in mark.capabilities.items():
                print(f"  • {cap}: {value}")
        except KeyError:
            print(f"❌ Unknown mark: {args.mark}")
    elif args.export:
        output_file = project_root / args.export
        viewer.export_progression_json(output_file)
    else:
        viewer.display_progression()


if __name__ == "__main__":


    main()