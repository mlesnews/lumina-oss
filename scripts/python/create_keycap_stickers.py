#!/usr/bin/env python3
"""
Create Custom Keycap Stickers
Generates printable stickers for macro buttons

Tags: #KEYCAPS #STICKERS #CUSTOMIZATION @JARVIS @LUMINA
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
import logging
logger = logging.getLogger("create_keycap_stickers")


project_root = Path(__file__).parent.parent.parent
output_dir = project_root / "data" / "keycap_stickers"
output_dir.mkdir(parents=True, exist_ok=True)


def create_keycap_sticker(text: str, size: tuple = (19, 19), bg_color: str = "white", text_color: str = "black", filename: str = None):
    """
    Create a keycap sticker design

    Standard keycap size: ~19mm x 19mm (0.75" x 0.75")
    """
    # Create image
    img = Image.new('RGB', size, bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load font, fallback to default
    try:
        font_size = 12
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (size[0] - text_width) // 2
    y = (size[1] - text_height) // 2

    # Draw text
    draw.text((x, y), text, fill=text_color, font=font)

    # Save
    if filename is None:
        filename = f"keycap_{text.replace('@', '').replace(' ', '_').lower()}.png"

    output_path = output_dir / filename
    img.save(output_path)

    return output_path


def create_all_stickers():
    try:
        """Create stickers for all macro buttons"""
        stickers = [
            {
                "text": "@DOIT",
                "bg_color": "red",
                "text_color": "white",
                "filename": "keycap_doit.png"
            },
            {
                "text": "@JARVIS",
                "bg_color": "blue",
                "text_color": "white",
                "filename": "keycap_jarvis.png"
            }
        ]

        results = []

        for sticker in stickers:
            path = create_keycap_sticker(**sticker)
            results.append({
                "text": sticker["text"],
                "file": str(path),
                "size": "19mm x 19mm"
            })
            print(f"✅ Created: {path.name}")

        # Create instructions file
        instructions = {
            "keycap_size": "19mm x 19mm (0.75\" x 0.75\")",
            "printing": {
                "method": "Print on sticker paper or label sheet",
                "scale": "100% (actual size)",
                "cutting": "Cut to exact size, apply to keycap"
            },
            "stickers": results
        }

        instructions_path = output_dir / "instructions.json"
        with open(instructions_path, 'w') as f:
            json.dump(instructions, f, indent=2)

        print()
        print(f"✅ Instructions saved: {instructions_path}")
        print()
        print("To use:")
        print("  1. Print stickers at 100% scale")
        print("  2. Cut to 19mm x 19mm size")
        print("  3. Apply to keycaps")
        print()

        return results


    except Exception as e:
        logger.error(f"Error in create_all_stickers: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    print("=" * 80)
    print("KEYCAP STICKER GENERATOR")
    print("=" * 80)
    print()

    try:
        create_all_stickers()
        print("✅ All stickers created!")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("   Install: pip install Pillow")
