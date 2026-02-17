#!/usr/bin/env python3
"""
Kenny Design Spectrum Explorer

Tests design variations from simple (circle) to complex (full helmet)
using dynamic scaling to explore what's possible vs impossible.

Spectrum Levels:
- Level 0: Simple circle (current)
- Level 1: Circle + HUD rectangle
- Level 2: Circle + HUD rectangle + face
- Level 3: Helmet outline + HUD + face
- Level 4: Full helmet + HUD + face + arc reactor
- Level 5+: More complex (test feasibility)

Tags: #KENNY #DESIGN #SPECTRUM #EXPLORATION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
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

logger = get_logger("KennyDesignSpectrumExplorer")

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None
    ImageDraw = None

# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logger.error("❌ PIL not available")


class DesignLevel(Enum):
    """Design complexity levels"""
    LEVEL_0_SIMPLE_CIRCLE = 0  # Current: Orange circle with black center
    LEVEL_1_CIRCLE_HUD = 1  # Circle + HUD rectangle
    LEVEL_2_CIRCLE_HUD_FACE = 2  # Circle + HUD rectangle + face
    LEVEL_3_HELMET_HUD_FACE = 3  # Helmet outline + HUD + face
    LEVEL_4_FULL_HELMET = 4  # Full helmet + HUD + face + arc reactor
    LEVEL_5_COMPLEX = 5  # Maximum complexity (test feasibility)


@dataclass
class DesignConfig:
    """Design configuration for a level"""
    level: DesignLevel
    name: str
    description: str
    size: int = 60
    size_scale: float = 1.0

    # Colors
    body_color: Tuple[int, int, int, int] = (255, 140, 0, 255)  # Orange
    hud_color: Tuple[int, int, int, int] = (0, 0, 0, 255)  # Black
    face_color: Tuple[int, int, int, int] = (200, 180, 160, 255)  # Skin tone
    arc_reactor_color: Tuple[int, int, int, int] = (0, 255, 255, 255)  # Cyan


class DesignSpectrumExplorer:
    """
    Explore design spectrum from simple to complex.

    Uses dynamic scaling to test what's possible at different sizes.
    """

    def __init__(self, output_dir: Path = None):
        """
        Initialize explorer.

        Args:
            output_dir: Directory to save design variations
        """
        if output_dir is None:
            output_dir = project_root / "data" / "kenny_design_spectrum"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Test sizes (using dynamic scaling)
        self.test_sizes = [30, 60, 90, 120]  # Small to large

        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")

        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")

    def generate_design(self, config: DesignConfig) -> Image.Image:
        """
        Generate design at specified level.

        Args:
            config: Design configuration

        Returns:
            PIL Image of design
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available")

        size = config.size
        scale = config.size_scale
        center_x = size / 2
        center_y = size / 2

        # Create transparent background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        if config.level == DesignLevel.LEVEL_0_SIMPLE_CIRCLE:
            # Level 0: Simple circle (current design)
            body_radius = size / 2
            draw.ellipse(
                [center_x - body_radius, center_y - body_radius,
                 center_x + body_radius, center_y + body_radius],
                fill=config.body_color
            )
            # Black center (face placeholder)
            face_radius = body_radius * 0.55
            draw.ellipse(
                [center_x - face_radius, center_y - face_radius,
                 center_x + face_radius, center_y + face_radius],
                fill=config.hud_color
            )

        elif config.level == DesignLevel.LEVEL_1_CIRCLE_HUD:
            # Level 1: Circle + HUD rectangle
            body_radius = size / 2
            draw.ellipse(
                [center_x - body_radius, center_y - body_radius,
                 center_x + body_radius, center_y + body_radius],
                fill=config.body_color
            )
            # HUD rectangle (centered)
            hud_width = int(size * 0.5 * scale)
            hud_height = int(size * 0.4 * scale)
            draw.rectangle(
                [center_x - hud_width/2, center_y - hud_height/2,
                 center_x + hud_width/2, center_y + hud_height/2],
                fill=config.hud_color
            )

        elif config.level == DesignLevel.LEVEL_2_CIRCLE_HUD_FACE:
            # Level 2: Circle + HUD rectangle + face
            body_radius = size / 2
            draw.ellipse(
                [center_x - body_radius, center_y - body_radius,
                 center_x + body_radius, center_y + body_radius],
                fill=config.body_color
            )
            # HUD rectangle
            hud_width = int(size * 0.5 * scale)
            hud_height = int(size * 0.4 * scale)
            draw.rectangle(
                [center_x - hud_width/2, center_y - hud_height/2,
                 center_x + hud_width/2, center_y + hud_height/2],
                fill=config.hud_color
            )
            # Face circle (inside HUD)
            face_radius = int(size * 0.15 * scale)
            draw.ellipse(
                [center_x - face_radius, center_y - face_radius,
                 center_x + face_radius, center_y + face_radius],
                fill=config.face_color
            )

        elif config.level == DesignLevel.LEVEL_3_HELMET_HUD_FACE:
            # Level 3: Helmet outline + HUD + face
            # Helmet shape (simplified - rounded rectangle outline)
            helmet_width = int(size * 0.9 * scale)
            helmet_height = int(size * 0.85 * scale)
            # Draw helmet outline (thicker)
            outline_width = max(2, int(3 * scale))
            draw.rounded_rectangle(
                [center_x - helmet_width/2, center_y - helmet_height/2,
                 center_x + helmet_width/2, center_y + helmet_height/2],
                radius=int(10 * scale),
                outline=config.body_color,
                width=outline_width,
                fill=None
            )
            # HUD rectangle
            hud_width = int(size * 0.45 * scale)
            hud_height = int(size * 0.35 * scale)
            draw.rectangle(
                [center_x - hud_width/2, center_y - hud_height/2,
                 center_x + hud_width/2, center_y + hud_height/2],
                fill=config.hud_color
            )
            # Face circle
            face_radius = int(size * 0.12 * scale)
            draw.ellipse(
                [center_x - face_radius, center_y - face_radius,
                 center_x + face_radius, center_y + face_radius],
                fill=config.face_color
            )

        elif config.level == DesignLevel.LEVEL_4_FULL_HELMET:
            # Level 4: Full helmet + HUD + face + arc reactor
            # Helmet shape (filled with outline)
            helmet_width = int(size * 0.9 * scale)
            helmet_height = int(size * 0.85 * scale)
            draw.rounded_rectangle(
                [center_x - helmet_width/2, center_y - helmet_height/2,
                 center_x + helmet_width/2, center_y + helmet_height/2],
                radius=int(10 * scale),
                outline=config.body_color,
                width=max(2, int(3 * scale)),
                fill=(255, 200, 100, 255)  # Lighter orange fill
            )
            # HUD rectangle
            hud_width = int(size * 0.45 * scale)
            hud_height = int(size * 0.35 * scale)
            draw.rectangle(
                [center_x - hud_width/2, center_y - hud_height/2,
                 center_x + hud_width/2, center_y + hud_height/2],
                fill=config.hud_color
            )
            # Face circle
            face_radius = int(size * 0.12 * scale)
            draw.ellipse(
                [center_x - face_radius, center_y - face_radius,
                 center_x + face_radius, center_y + face_radius],
                fill=config.face_color
            )
            # Arc reactor (center chest)
            arc_radius = int(size * 0.08 * scale)
            draw.ellipse(
                [center_x - arc_radius, center_y + helmet_height/4 - arc_radius,
                 center_x + arc_radius, center_y + helmet_height/4 + arc_radius],
                fill=config.arc_reactor_color,
                outline=(255, 255, 255, 255),
                width=max(1, int(1 * scale))
            )

        else:
            # Level 5+: Maximum complexity (test feasibility)
            # Same as Level 4 for now - can add more detail
            return self.generate_design(DesignConfig(
                level=DesignLevel.LEVEL_4_FULL_HELMET,
                name=config.name,
                description=config.description,
                size=config.size,
                size_scale=config.size_scale
            ))

        return img

    def explore_spectrum(self) -> Dict[str, Any]:
        """
        Explore full design spectrum.

        Returns:
            Dictionary with results for each level/size combination
        """
        results = {}

        for level in DesignLevel:
            level_name = level.name
            results[level_name] = {}

            for size in self.test_sizes:
                scale = size / 60.0  # Dynamic scaling (60px = 1.0 scale)

                config = DesignConfig(
                    level=level,
                    name=f"Level {level.value}",
                    description=f"Design level {level.value} at {size}px",
                    size=size,
                    size_scale=scale
                )

                try:
                    img = self.generate_design(config)

                    # Save image
                    output_file = self.output_dir / f"level_{level.value}_size_{size}px.png"
                    img.save(output_file, "PNG")

                    results[level_name][f"{size}px"] = {
                        "success": True,
                        "file": str(output_file),
                        "size": size,
                        "scale": scale
                    }

                    logger.info(f"✅ Generated {level_name} at {size}px -> {output_file.name}")

                except Exception as e:
                    results[level_name][f"{size}px"] = {
                        "success": False,
                        "error": str(e),
                        "size": size,
                        "scale": scale
                    }
                    logger.error(f"❌ Failed {level_name} at {size}px: {e}")

        return results

    def generate_comparison_grid(self, results: Dict[str, Any]) -> Image.Image:
        """
        Generate comparison grid showing all designs.

        Args:
            results: Results from explore_spectrum()

        Returns:
            PIL Image of comparison grid
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available")

        # Calculate grid size
        num_levels = len(DesignLevel)
        num_sizes = len(self.test_sizes)
        cell_size = 80  # Size of each cell in grid
        padding = 10

        grid_width = num_sizes * cell_size + (num_sizes + 1) * padding
        grid_height = num_levels * cell_size + (num_levels + 1) * padding + 30  # Extra for labels

        grid_img = Image.new('RGBA', (grid_width, grid_height), (255, 255, 255, 255))
        grid_draw = ImageDraw.Draw(grid_img)

        # Draw grid
        y = padding + 30  # Start below labels
        for level_idx, level in enumerate(DesignLevel):
            x = padding
            for size_idx, size in enumerate(self.test_sizes):
                level_name = level.name
                size_key = f"{size}px"

                if level_name in results and size_key in results[level_name]:
                    result = results[level_name][size_key]
                    if result.get("success"):
                        # Load and paste image
                        try:
                            design_img = Image.open(result["file"])
                            design_img = design_img.resize((cell_size - 4, cell_size - 4), Image.LANCZOS)
                            grid_img.paste(design_img, (x + 2, y + 2), design_img)
                        except Exception as e:
                            logger.error(f"Error loading {result['file']}: {e}")
                            # Draw error box
                            grid_draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(255, 0, 0, 255))
                    else:
                        # Draw error box
                        grid_draw.rectangle([x, y, x + cell_size, y + cell_size], fill=(128, 128, 128, 255))

                x += cell_size + padding

            y += cell_size + padding

        return grid_img


def main():
    """Main exploration"""
    explorer = DesignSpectrumExplorer()

    logger.info("🔍 Exploring design spectrum...")
    results = explorer.explore_spectrum()

    # Generate comparison grid
    logger.info("📊 Generating comparison grid...")
    try:
        grid_img = explorer.generate_comparison_grid(results)
        grid_file = explorer.output_dir / "design_spectrum_comparison.png"
        grid_img.save(grid_file, "PNG")
        logger.info(f"✅ Comparison grid saved: {grid_file}")
    except Exception as e:
        logger.error(f"❌ Failed to generate comparison grid: {e}")

    # Print summary
    print("\n" + "="*80)
    print("DESIGN SPECTRUM EXPLORATION RESULTS")
    print("="*80)

    for level in DesignLevel:
        level_name = level.name
        print(f"\n{level_name} (Level {level.value}):")
        if level_name in results:
            for size_key, result in results[level_name].items():
                status = "✅" if result.get("success") else "❌"
                print(f"  {status} {size_key}: {result.get('file', result.get('error', 'Unknown'))}")

    print("\n" + "="*80)
    print(f"📁 Results saved to: {explorer.output_dir}")
    print("="*80 + "\n")


if __name__ == "__main__":


    main()