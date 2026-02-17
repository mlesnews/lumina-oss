"""
HVAC Bid Extractor
Extracts bid information from contractor attachments (PDF, DOCX, TXT, etc.)
and converts them to the bid comparison format.

#JARVIS #LUMINA #PEAK
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Setup logging
logger = logging.getLogger(__name__)


class BidExtractor:
    """Extract bid information from various file formats."""

    def __init__(self, project_root: Path):
        """
        Initialize the bid extractor.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def extract_from_text(self, text: str, contractor_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Extract bid information from plain text using pattern matching.

        Args:
            text: Text content from the bid document
            contractor_name: Optional contractor name if known

        Returns:
            Dictionary containing extracted bid data
        """
        bid_data = {}

        # Normalize text
        text_lower = text.lower()
        text_upper = text.upper()

        # Extract contractor name
        if not contractor_name:
            # Look for common patterns
            name_patterns = [
                r'(?:company|contractor|business|firm)[\s:]+([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
                r'^([A-Z][A-Za-z\s&,\.]+?)(?:\s+(?:HVAC|Heating|Cooling|Contractor))',
                r'from[:\s]+([A-Z][A-Za-z\s&,\.]+?)(?:\n|$)',
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text, re.MULTILINE | re.IGNORECASE)
                if match:
                    contractor_name = match.group(1).strip()
                    break

        if contractor_name:
            bid_data["contractor_name"] = contractor_name

        # Extract costs - look for dollar amounts
        cost_patterns = {
            "total": [
                r'total[:\s]+\$?([\d,]+\.?\d*)',
                r'\$([\d,]+\.?\d*)\s*(?:total|grand\s*total)',
                r'grand\s*total[:\s]+\$?([\d,]+\.?\d*)',
                r'price[:\s]+\$?([\d,]+\.?\d*)',
                r'cost[:\s]+\$?([\d,]+\.?\d*)',
            ],
            "equipment": [
                r'equipment[:\s]+\$?([\d,]+\.?\d*)',
                r'furnace[:\s]+\$?([\d,]+\.?\d*)',
                r'unit[:\s]+\$?([\d,]+\.?\d*)',
            ],
            "labor": [
                r'labor[:\s]+\$?([\d,]+\.?\d*)',
                r'installation[:\s]+\$?([\d,]+\.?\d*)',
                r'work[:\s]+\$?([\d,]+\.?\d*)',
            ],
            "permit": [
                r'permit[:\s]+\$?([\d,]+\.?\d*)',
            ],
            "disposal": [
                r'disposal[:\s]+\$?([\d,]+\.?\d*)',
                r'removal[:\s]+\$?([\d,]+\.?\d*)',
                r'haul[:\s]+\$?([\d,]+\.?\d*)',
            ],
        }

        for cost_type, patterns in cost_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    try:
                        cost_value = float(match.group(1).replace(',', ''))
                        bid_data[f"{cost_type}_cost"] = cost_value
                        break
                    except (ValueError, IndexError):
                        continue

        # If we have individual costs but no total, calculate it
        if "total_cost" not in bid_data:
            total = 0
            for cost_key in ["equipment_cost", "labor_cost", "permit_cost", "disposal_cost"]:
                if cost_key in bid_data:
                    total += bid_data[cost_key]
            if total > 0:
                bid_data["total_cost"] = total

        # Extract equipment information
        equipment = {}

        # Brand
        brand_patterns = [
            r'brand[:\s]+([A-Z][A-Za-z\s]+?)(?:\n|$)',
            r'(Carrier|Lennox|Trane|Rheem|Goodman|York|Bryant|American\s*Standard|Ruud)',
        ]
        for pattern in brand_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                equipment["brand"] = match.group(1).strip()
                break

        # Model
        model_patterns = [
            r'model[:\s]+([A-Z0-9\-\s]+?)(?:\n|$)',
            r'model\s*#?[:\s]+([A-Z0-9\-\s]+?)(?:\n|$)',
        ]
        for pattern in model_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                equipment["model"] = match.group(1).strip()
                break

        # Efficiency
        efficiency_patterns = [
            r'(\d+\.?\d*)\s*%?\s*AFUE',
            r'efficiency[:\s]+(\d+\.?\d*)\s*%',
            r'(\d+\.?\d*)\s*%?\s*efficient',
        ]
        for pattern in efficiency_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                efficiency_value = match.group(1)
                equipment["efficiency_rating"] = f"{efficiency_value}% AFUE"
                break

        # Capacity
        capacity_patterns = [
            r'(\d{1,3}[,\d]*)\s*BTU',
            r'capacity[:\s]+(\d{1,3}[,\d]*)\s*BTU',
        ]
        for pattern in capacity_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                equipment["capacity"] = f"{match.group(1).replace(',', '')} BTU"
                break

        # Warranty
        warranty_patterns = [
            r'warranty[:\s]+(\d+)\s*years?',
            r'(\d+)\s*year\s*warranty',
        ]
        for pattern in warranty_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    equipment["warranty_years"] = int(match.group(1))
                    break
                except ValueError:
                    continue

        if equipment:
            bid_data["equipment"] = equipment

        # Extract other information
        # Timeline
        timeline_patterns = [
            r'(?:timeline|schedule|duration)[:\s]+([^\n]+)',
            r'(\d+\s*-\s*\d+\s*days?)',
            r'(\d+\s*weeks?)',
        ]
        for pattern in timeline_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                bid_data["installation_timeline"] = match.group(1).strip()
                break

        # Payment terms
        payment_patterns = [
            r'payment[:\s]+([^\n]+)',
            r'terms[:\s]+([^\n]+)',
        ]
        for pattern in payment_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                bid_data["payment_terms"] = match.group(1).strip()
                break

        # Contact info
        phone_pattern = r'(?:phone|tel)[:\s]*\(?(\d{3})\)?\s*-?\s*(\d{3})\s*-?\s*(\d{4})'
        phone_match = re.search(phone_pattern, text, re.IGNORECASE)
        if phone_match:
            phone = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
            bid_data["contact_info"] = phone

        email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
        email_match = re.search(email_pattern, text)
        if email_match:
            if "contact_info" in bid_data:
                bid_data["contact_info"] += f" | Email: {email_match.group(1)}"
            else:
                bid_data["contact_info"] = f"Email: {email_match.group(1)}"

        # Date
        date_patterns = [
            r'(\d{4}-\d{2}-\d{2})',
            r'(\d{1,2}/\d{1,2}/\d{4})',
            r'(\d{1,2}-\d{1,2}-\d{4})',
        ]
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                bid_data["bid_date"] = match.group(1)
                break

        # Notes - extract bullet points or list items
        notes = []
        note_patterns = [
            r'[•\-\*]\s*([^\n]+)',
            r'\d+\.\s*([^\n]+)',
        ]
        for pattern in note_patterns:
            matches = re.findall(pattern, text)
            for match in matches[:10]:  # Limit to 10 notes
                note = match.strip()
                if len(note) > 10 and note not in notes:
                    notes.append(note)

        if notes:
            bid_data["notes"] = notes

        return bid_data

    def read_pdf(self, file_path: Path) -> str:
        """
        Extract text from PDF file.

        Args:
            file_path: Path to PDF file

        Returns:
            Extracted text content
        """
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
            return ""
        except Exception as e:
            logger.error(f"Error reading PDF {file_path}: {e}")
            return ""

    def read_docx(self, file_path: Path) -> str:
        """
        Extract text from DOCX file.

        Args:
            file_path: Path to DOCX file

        Returns:
            Extracted text content
        """
        try:
            from docx import Document
            doc = Document(file_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except ImportError:
            logger.warning("python-docx not installed. Install with: pip install python-docx")
            return ""
        except Exception as e:
            logger.error(f"Error reading DOCX {file_path}: {e}")
            return ""

    def read_text_file(self, file_path: Path) -> str:
        """
        Read text from a plain text file.

        Args:
            file_path: Path to text file

        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""

    def extract_from_file(self, file_path: Path, contractor_name: Optional[str] = None) -> Dict[str, Any]:
        try:
            """
            Extract bid information from a file.

            Args:
                file_path: Path to the bid file
                contractor_name: Optional contractor name

            Returns:
                Dictionary containing extracted bid data
            """
            file_path = Path(file_path)

            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return {}

            # Determine file type and extract text
            suffix = file_path.suffix.lower()

            if suffix == '.pdf':
                text = self.read_pdf(file_path)
            elif suffix in ['.docx', '.doc']:
                text = self.read_docx(file_path)
            elif suffix in ['.txt', '.md']:
                text = self.read_text_file(file_path)
            else:
                logger.warning(f"Unsupported file type: {suffix}. Trying as text file...")
                text = self.read_text_file(file_path)

            if not text.strip():
                logger.warning(f"No text extracted from {file_path}")
                return {}

            # Extract bid data from text
            bid_data = self.extract_from_text(text, contractor_name)
            bid_data["bid_file_path"] = str(file_path)

            return bid_data

        except Exception as e:
            self.logger.error(f"Error in extract_from_file: {e}", exc_info=True)
            raise
    def process_attachments(self, file_paths: List[Path], 
                           contractor_names: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Process multiple bid attachment files.

        Args:
            file_paths: List of file paths to process
            contractor_names: Optional list of contractor names (in same order as files)

        Returns:
            List of extracted bid data dictionaries
        """
        bids = []

        for i, file_path in enumerate(file_paths):
            contractor_name = None
            if contractor_names and i < len(contractor_names):
                contractor_name = contractor_names[i]

            logger.info(f"Processing {file_path.name}...")
            bid_data = self.extract_from_file(file_path, contractor_name)

            if bid_data:
                bids.append(bid_data)
                logger.info(f"✓ Extracted bid from {file_path.name}")
            else:
                logger.warning(f"✗ Failed to extract bid from {file_path.name}")

        return bids

    def save_extracted_bids(self, bids: List[Dict[str, Any]],
                               output_dir: Optional[Path] = None) -> List[Path]:
        try:
            """
            Save extracted bids to JSON files.

            Args:
                bids: List of bid data dictionaries
                output_dir: Optional output directory (defaults to data/hvac_bids)

            Returns:
                List of paths to saved JSON files
            """
            if output_dir is None:
                output_dir = self.data_dir

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            saved_files = []

            for i, bid in enumerate(bids, 1):
                contractor_name = bid.get("contractor_name", f"Contractor_{i}")
                # Sanitize filename
                safe_name = re.sub(r'[^\w\s-]', '', contractor_name).strip().replace(' ', '_')
                filename = f"{safe_name}_bid.json"
                output_path = output_dir / filename

                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(bid, f, indent=2, ensure_ascii=False)

                saved_files.append(output_path)
                logger.info(f"Saved bid to {output_path}")

            return saved_files


        except Exception as e:
            self.logger.error(f"Error in save_extracted_bids: {e}", exc_info=True)
            raise
def main():
    try:
        """Main function for CLI usage."""
        import argparse

        parser = argparse.ArgumentParser(description="HVAC Bid Extractor from Attachments")
        parser.add_argument("files", nargs="+", type=Path,
                           help="Path(s) to bid attachment files (PDF, DOCX, TXT)")
        parser.add_argument("--project-root", type=Path,
                           default=Path(__file__).parent.parent.parent,
                           help="Project root directory")
        parser.add_argument("--contractor-names", nargs="+",
                           help="Contractor names (in same order as files)")
        parser.add_argument("--output-dir", type=Path,
                           help="Output directory for JSON files (default: data/hvac_bids)")
        parser.add_argument("--auto-import", action="store_true",
                           help="Automatically import extracted bids into comparison system")

        args = parser.parse_args()

        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Initialize extractor
        extractor = BidExtractor(args.project_root)

        # Process files
        bids = extractor.process_attachments(args.files, args.contractor_names)

        if not bids:
            print("\n✗ No bids extracted. Check file formats and content.")
            return

        # Save extracted bids
        saved_files = extractor.save_extracted_bids(bids, args.output_dir)

        print(f"\n✓ Extracted {len(bids)} bid(s)")
        print(f"✓ Saved to:")
        for file_path in saved_files:
            print(f"    {file_path}")

        # Auto-import if requested
        if args.auto_import:
            print("\nImporting into comparison system...")
            from hvac_bid_comparison import HVACBidComparator

            comparator = HVACBidComparator(args.project_root)
            comparator.set_budget(7000.0)

            for bid in bids:
                comparator.import_bid_from_dict(bid)

            comparator.save_bids()
            comparator.print_summary()

            if len(comparator.bids) >= 2:
                report_path = comparator.generate_report()
                print(f"\n✓ Generated comparison report: {report_path}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()