"""Try EasyOCR for screenshot analysis"""
import sys
from pathlib import Path

try:
    import easyocr
    from PIL import Image

    screenshot_path = Path(__file__).parent.parent.parent / "data" / "imva_frame_capture" / "current_screen.png"

    print("Initializing EasyOCR reader (this may take a moment on first run)...")
    reader = easyocr.Reader(['en'], gpu=False)

    print(f"Reading screenshot: {screenshot_path}")
    results = reader.readtext(str(screenshot_path))

    print("\n" + "="*80)
    print("EXTRACTED TEXT:")
    print("="*80)

    all_text = []
    for (bbox, text, confidence) in results:
        if confidence > 0.5:  # Only high confidence text
            print(f"[{confidence:.2f}] {text}")
            all_text.append(text)

    full_text = "\n".join(all_text)

    # Save to file
    output_file = screenshot_path.parent / "extracted_text.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_text)

    print(f"\n✓ Full text saved to: {output_file}")

except ImportError:
    print("EasyOCR not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "easyocr"])
    print("✓ EasyOCR installed. Please run this script again.")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
