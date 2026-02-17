#!/usr/bin/env python3
"""
PDF Generator for Documentation
@PEAK Optimized

Generate PDF files from Markdown and JSON documentation.
Supports triplicate format requirement (.MD, .JSON, .PDF).

Author: <COMPANY_NAME> LLC
Date: 2025-01-27
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import subprocess
import sys
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PDFGenerator")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PDFGenerator:
    """
    @PEAK: PDF Generator

    Generate PDF files from Markdown using available tools.
    Supports multiple conversion methods.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize PDF generator"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.conversion_methods = self._detect_conversion_methods()

    def _detect_conversion_methods(self) -> Dict[str, bool]:
        """Detect available PDF conversion methods"""
        methods = {
            "pandoc": False,
            "markdown_pdf": False,
            "weasyprint": False,
            "reportlab": False
        }

        # Check for pandoc
        try:
            result = subprocess.run(
                ["pandoc", "--version"],
                capture_output=True,
                timeout=5
            )
            methods["pandoc"] = result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Check for Python libraries
        try:
            import weasyprint
            methods["weasyprint"] = True
        except ImportError:
            pass

        try:
            import reportlab
            methods["reportlab"] = True
        except ImportError:
            pass

        try:
            import markdown_pdf
            methods["markdown_pdf"] = True
        except ImportError:
            pass

        logger.info(f"Available conversion methods: {[k for k, v in methods.items() if v]}")
        return methods

    def generate_pdf_from_markdown(
        self,
        markdown_path: Path,
        output_path: Optional[Path] = None,
        method: Optional[str] = None
    ) -> bool:
        """
        @PEAK: Generate PDF from Markdown

        Convert Markdown file to PDF using available method.

        Args:
            markdown_path: Path to Markdown file
            output_path: Optional output path (default: same name with .pdf)
            method: Optional conversion method (auto-detect if None)

        Returns:
            True if successful, False otherwise
        """
        if not markdown_path.exists():
            logger.error(f"Markdown file not found: {markdown_path}")
            return False

        if output_path is None:
            output_path = markdown_path.with_suffix(".pdf")

        # Auto-detect method if not specified
        if method is None:
            if self.conversion_methods["pandoc"]:
                method = "pandoc"
            elif self.conversion_methods["weasyprint"]:
                method = "weasyprint"
            elif self.conversion_methods["markdown_pdf"]:
                method = "markdown_pdf"
            else:
                logger.warning("No PDF conversion method available")
                return self._generate_pdf_instructions(markdown_path, output_path)

        # Execute conversion
        if method == "pandoc":
            return self._convert_with_pandoc(markdown_path, output_path)
        elif method == "weasyprint":
            return self._convert_with_weasyprint(markdown_path, output_path)
        elif method == "markdown_pdf":
            return self._convert_with_markdown_pdf(markdown_path, output_path)
        else:
            logger.warning(f"Unknown conversion method: {method}")
            return self._generate_pdf_instructions(markdown_path, output_path)

    def _convert_with_pandoc(self, markdown_path: Path, output_path: Path) -> bool:
        """Convert using pandoc"""
        try:
            subprocess.run(
                [
                    "pandoc",
                    str(markdown_path),
                    "-o", str(output_path),
                    "--pdf-engine=xelatex",
                    "-V", "geometry:margin=1in"
                ],
                check=True,
                timeout=60
            )
            logger.info(f"PDF generated: {output_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.error(f"Pandoc conversion failed: {e}")
            return False

    def _convert_with_weasyprint(self, markdown_path: Path, output_path: Path) -> bool:
        """Convert using weasyprint"""
        try:
            from weasyprint import HTML, CSS
            from markdown import markdown

            # Read markdown
            with open(markdown_path, "r", encoding="utf-8") as f:
                md_content = f.read()

            # Convert to HTML
            html_content = markdown(md_content, extensions=["extra", "codehilite"])

            # Generate PDF
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"PDF generated: {output_path}")
            return True
        except Exception as e:
            logger.error(f"WeasyPrint conversion failed: {e}")
            return False

    def _convert_with_markdown_pdf(self, markdown_path: Path, output_path: Path) -> bool:
        """Convert using markdown-pdf"""
        try:
            import markdown_pdf
            markdown_pdf.convert(str(markdown_path), str(output_path))
            logger.info(f"PDF generated: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Markdown-PDF conversion failed: {e}")
            return False

    def _generate_pdf_instructions(self, markdown_path: Path, output_path: Path) -> bool:
        """Generate instructions file when no converter available"""
        instructions = f"""
PDF Generation Instructions
==========================

No PDF conversion tool is currently available on this system.

To generate PDF from: {markdown_path.name}

Option 1: Install Pandoc
--------------------------
1. Install Pandoc: https://pandoc.org/installing.html
2. Install LaTeX (for PDF): https://www.latex-project.org/get/
3. Run: pandoc {markdown_path.name} -o {output_path.name}

Option 2: Use Online Converter
-------------------------------
1. Upload {markdown_path.name} to:
   - https://www.markdowntopdf.com/
   - https://dillinger.io/ (export as PDF)
   - https://www.markdowntohtml.com/ (then print to PDF)

Option 3: Use VS Code Extension
-------------------------------
1. Install "Markdown PDF" extension in VS Code
2. Open {markdown_path.name}
3. Right-click → "Markdown PDF: Export (pdf)"

Option 4: Install Python Library
---------------------------------
pip install weasyprint markdown
python scripts/python/pdf_generator.py

The file has been prepared for PDF conversion.
"""
        instructions_path = output_path.with_suffix(".pdf.instructions.txt")
        with open(instructions_path, "w", encoding="utf-8") as f:
            f.write(instructions)

        logger.info(f"PDF instructions saved to: {instructions_path}")
        return False

    def generate_all_pdfs(self, docs_dir: Optional[Path] = None) -> Dict[str, bool]:
        """
        @PEAK: Generate All PDFs

        Generate PDFs for all Markdown files in documentation directory.

        Args:
            docs_dir: Documentation directory (default: docs/financial)

        Returns:
            Dictionary of file paths and success status
        """
        if docs_dir is None:
            docs_dir = self.project_root / "docs" / "financial"

        results = {}
        md_files = list(docs_dir.glob("*.md"))

        for md_file in md_files:
            pdf_file = md_file.with_suffix(".pdf")
            success = self.generate_pdf_from_markdown(md_file, pdf_file)
            results[str(md_file)] = success

        return results


def main() -> int:
    try:
        """Main entry point"""
        generator = PDFGenerator()

        # Generate PDFs for Bitcoin documentation
        docs_dir = generator.project_root / "docs" / "financial"
        results = generator.generate_all_pdfs(docs_dir)

        print("\nPDF Generation Results:")
        print("=" * 60)
        for file_path, success in results.items():
            status = "✓ SUCCESS" if success else "✗ FAILED"
            print(f"{status}: {Path(file_path).name}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    import sys



    sys.exit(main())