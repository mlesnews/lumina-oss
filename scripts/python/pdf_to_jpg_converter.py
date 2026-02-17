"""
Convert PDF to JPG with size constraint (under 1MB)
"""
import os
import sys
from pathlib import Path
from PIL import Image
import io
import logging
logger = logging.getLogger("pdf_to_jpg_converter")


try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    try:
        from pdf2image import convert_from_path
        HAS_PDF2IMAGE = True
    except ImportError:
        HAS_PDF2IMAGE = False


def convert_pdf_to_jpg(pdf_path, output_path=None, max_size_mb=1.0, quality=85):
    try:
        """
        Convert PDF to JPG, ensuring output is under max_size_mb.

        Args:
            pdf_path: Path to input PDF file
            output_path: Path to output JPG file (default: same name with .jpg extension)
            max_size_mb: Maximum file size in MB (default: 1.0)
            quality: Initial JPEG quality (default: 85, will be reduced if needed)

        Returns:
            Path to output JPG file
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if output_path is None:
            output_path = pdf_path.with_suffix('.jpg')
        else:
            output_path = Path(output_path)

        max_size_bytes = int(max_size_mb * 1024 * 1024)

        print(f"Converting {pdf_path.name} to JPG...")

        # Convert PDF to image(s)
        if HAS_PYMUPDF:
            # Use PyMuPDF (fitz)
            doc = fitz.open(str(pdf_path))
            images = []
            for page_num in range(len(doc)):
                page = doc[page_num]
                # Render page at 2x resolution for better quality
                mat = fitz.Matrix(2, 2)
                pix = page.get_pixmap(matrix=mat)
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))
                images.append(img)
            doc.close()
        elif HAS_PDF2IMAGE:
            # Use pdf2image
            images = convert_from_path(str(pdf_path), dpi=200)
        else:
            raise ImportError(
                "Neither PyMuPDF nor pdf2image is installed. "
                "Install one with: pip install PyMuPDF OR pip install pdf2image"
            )

        # Combine all pages into a single image (stacked vertically)
        if len(images) == 1:
            combined_img = images[0]
        else:
            # Calculate dimensions for combined image
            max_width = max(img.width for img in images)
            total_height = sum(img.height for img in images)
            combined_img = Image.new('RGB', (max_width, total_height), color='white')

            y_offset = 0
            for img in images:
                # Center images if widths differ
                x_offset = (max_width - img.width) // 2
                combined_img.paste(img, (x_offset, y_offset))
                y_offset += img.height

        # Save with compression, reducing quality if needed
        current_quality = quality
        output_path_str = str(output_path)

        while True:
            # Save to bytes first to check size
            buffer = io.BytesIO()
            combined_img.save(buffer, format='JPEG', quality=current_quality, optimize=True)
            file_size = buffer.tell()

            if file_size <= max_size_bytes:
                # Size is acceptable, save to file
                buffer.seek(0)
                with open(output_path_str, 'wb') as f:
                    f.write(buffer.read())
                print(f"✓ Successfully converted to {output_path.name}")
                print(f"  File size: {file_size / 1024 / 1024:.2f} MB")
                print(f"  Quality: {current_quality}")
                return output_path

            # File too large, reduce quality or resize
            if current_quality > 30:
                current_quality -= 10
                print(f"  File too large ({file_size / 1024 / 1024:.2f} MB), reducing quality to {current_quality}...")
            else:
                # Quality already low, need to resize
                print(f"  File still too large ({file_size / 1024 / 1024:.2f} MB) at quality {current_quality}, resizing...")
                # Resize to 80% of current size
                new_width = int(combined_img.width * 0.8)
                new_height = int(combined_img.height * 0.8)
                combined_img = combined_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                current_quality = quality  # Reset quality after resize
                print(f"  Resized to {new_width}x{new_height}, retrying with quality {current_quality}...")


    except Exception as e:
        logger.error(f"Error in convert_pdf_to_jpg: {e}", exc_info=True)
        raise
def find_pdf_file(filename):
    try:
        """Search for PDF file in common locations"""
        import os
        from pathlib import Path

        search_paths = [
            Path.cwd(),
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path(__file__).parent.parent.parent,  # Workspace root
        ]

        # Also search in workspace recursively (limited depth)
        workspace = Path(__file__).parent.parent.parent
        if workspace.exists():
            for pdf_file in workspace.rglob("*.pdf"):
                if filename.lower() in pdf_file.name.lower():
                    return pdf_file

        # Check common locations
        for search_path in search_paths:
            if search_path.exists():
                pdf_path = search_path / filename
                if pdf_path.exists():
                    return pdf_path

        return None


    except Exception as e:
        logger.error(f"Error in find_pdf_file: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python pdf_to_jpg_converter.py <pdf_file> [output_file]")
        sys.exit(1)

    pdf_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    # If file doesn't exist, try to find it
    pdf_path = Path(pdf_file)
    if not pdf_path.exists():
        print(f"File not found at {pdf_file}, searching...")
        found_path = find_pdf_file(pdf_path.name)
        if found_path:
            print(f"Found file at: {found_path}")
            pdf_file = str(found_path)
        else:
            print(f"Error: Could not find PDF file: {pdf_path.name}")
            print("\nPlease provide the full path to the PDF file.")
            sys.exit(1)

    try:
        result = convert_pdf_to_jpg(pdf_file, output_file, max_size_mb=1.0)
        print(f"\nConversion complete: {result}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
