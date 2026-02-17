"""
Quick screenshot analysis script
Tries multiple methods: OCR, vision model, or basic image info
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PIL import Image
import json

def analyze_screenshot(image_path: Path):
    """Analyze screenshot using available methods."""
    print(f"Analyzing screenshot: {image_path}")

    if not image_path.exists():
        print(f"❌ Image not found: {image_path}")
        return

    img = Image.open(image_path)
    print(f"✅ Image loaded: {img.size[0]}x{img.size[1]} pixels")
    print(f"   Format: {img.format}, Mode: {img.mode}")

    # Try OCR with pytesseract
    try:
        import pytesseract
        print("\n🔍 Trying OCR (pytesseract)...")
        text = pytesseract.image_to_string(img)
        if text.strip():
            print("✅ OCR extracted text:")
            print("-" * 80)
            print(text[:500])  # First 500 chars
            if len(text) > 500:
                print("... (truncated)")
            print("-" * 80)

            # Save extracted text
            txt_file = image_path.parent / f"{image_path.stem}_extracted_text.txt"
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"\n✅ Full text saved to: {txt_file}")
            return text
        else:
            print("⚠️  OCR found no text")
    except ImportError:
        print("⚠️  pytesseract not installed (pip install pytesseract)")
    except Exception as e:
        print(f"⚠️  OCR error: {e}")

    # Try vision model if available
    try:
        import ollama
        print("\n🔍 Trying vision model (ollama)...")
        # Try to use a vision model
        with open(image_path, 'rb') as f:
            response = ollama.chat(
                model='llava',  # Common vision model name
                messages=[{
                    'role': 'user',
                    'content': 'Describe what you see in this image, especially any text content.',
                    'images': [f.read()]
                }]
            )
        if response and 'message' in response:
            description = response['message'].get('content', '')
            print("✅ Vision model analysis:")
            print("-" * 80)
            print(description[:500])
            if len(description) > 500:
                print("... (truncated)")
            print("-" * 80)
            return description
    except ImportError:
        print("⚠️  ollama not available")
    except Exception as e:
        print(f"⚠️  Vision model error: {e}")

    print("\n⚠️  No text extraction available - image info only")
    return None

if __name__ == "__main__":
    screenshot_path = project_root / "data" / "imva_frame_capture" / "current_screen.png"
    analyze_screenshot(screenshot_path)
