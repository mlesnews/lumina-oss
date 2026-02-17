#!/usr/bin/env python3
"""
Test Kenny Sprite Debug - Save sprite to disk to verify creation

Tags: #KENNY #DEBUG #SPRITE @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageTk

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

def test_sprite_creation():
    """Test sprite creation - save to disk"""
    print("=" * 80)
    print("🧪 TESTING KENNY SPRITE CREATION")
    print("=" * 80)
    print()

    # Test parameters (matching kenny_imva_enhanced.py)
    size = 80
    center_x = size / 2
    center_y = size / 2

    # Create image with transparent background (like code)
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    print(f"Image size: {size}x{size}")
    print(f"Center: ({center_x}, {center_y})")
    print()

    # Current code pattern (from kenny_imva_enhanced.py)
    print("📝 Drawing with CURRENT code pattern...")
    body_radius = (size * 0.95) / 2
    body_bbox = [
        center_x - body_radius, center_y - body_radius,
        center_x + body_radius, center_y + body_radius
    ]
    print(f"  Body radius: {body_radius:.2f}")
    print(f"  Body bbox: {body_bbox}")

    draw.ellipse(
        body_bbox,
        fill=(255, 140, 0, 255)  # Orange - FULL opacity
    )

    face_radius = body_radius * 0.55
    face_bbox = [
        center_x - face_radius, center_y - face_radius,
        center_x + face_radius, center_y + face_radius
    ]
    print(f"  Face radius: {face_radius:.2f}")
    print(f"  Face bbox: {face_bbox}")

    draw.ellipse(
        face_bbox,
        fill=(0, 0, 0, 255)  # Black - FULL opacity
    )

    # Save to disk
    output_dir = project_root / "data" / "kenny_debug"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "kenny_sprite_current.png"
    img.save(output_file, "PNG")
    print(f"  ✅ Saved: {output_file}")
    print()

    # Test alternative: Use full size (100% instead of 95%)
    print("📝 Testing ALTERNATIVE: 100% size (no margin)...")
    img2 = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(img2)

    body_radius2 = size / 2
    body_bbox2 = [
        center_x - body_radius2, center_y - body_radius2,
        center_x + body_radius2, center_y + body_radius2
    ]
    print(f"  Body radius: {body_radius2:.2f} (100% of size)")

    draw2.ellipse(
        body_bbox2,
        fill=(255, 140, 0, 255)
    )

    face_radius2 = body_radius2 * 0.55
    face_bbox2 = [
        center_x - face_radius2, center_y - face_radius2,
        center_x + face_radius2, center_y + face_radius2
    ]

    draw2.ellipse(
        face_bbox2,
        fill=(0, 0, 0, 255)
    )

    output_file2 = output_dir / "kenny_sprite_100percent.png"
    img2.save(output_file2, "PNG")
    print(f"  ✅ Saved: {output_file2}")
    print()

    # Test with white background (to see transparency)
    print("📝 Testing with WHITE background (to see transparency)...")
    img3 = Image.new('RGBA', (size, size), (255, 255, 255, 255))  # White background
    draw3 = ImageDraw.Draw(img3)

    body_bbox3 = [
        center_x - body_radius, center_y - body_radius,
        center_x + body_radius, center_y + body_radius
    ]
    draw3.ellipse(
        body_bbox3,
        fill=(255, 140, 0, 255)
    )

    face_bbox3 = [
        center_x - face_radius, center_y - face_radius,
        center_x + face_radius, center_y + face_radius
    ]
    draw3.ellipse(
        face_bbox3,
        fill=(0, 0, 0, 255)
    )

    output_file3 = output_dir / "kenny_sprite_white_bg.png"
    img3.save(output_file3, "PNG")
    print(f"  ✅ Saved: {output_file3}")
    print()

    print("=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print(f"Check images in: {output_dir}")
    print("  - kenny_sprite_current.png (current code, transparent bg)")
    print("  - kenny_sprite_100percent.png (100% size, transparent bg)")
    print("  - kenny_sprite_white_bg.png (current code, white bg)")
    print()
    print("Compare these images to see if issue is in:")
    print("  1. Image creation (if images look wrong)")
    print("  2. Canvas display (if images look correct but Kenny is still Froot Loop)")
    print("=" * 80)

if __name__ == "__main__":
    test_sprite_creation()
