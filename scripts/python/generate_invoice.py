#!/usr/bin/env python3
"""
Generate Invoice from Template
Creates a professional invoice from the template
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("GenerateInvoice")


def load_template() -> str:
    try:
        """Load invoice template"""
        template_path = script_dir / "templates" / "invoice_template.html"
        if not template_path.exists():
            raise FileNotFoundError(f"Invoice template not found: {template_path}")

        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()


    except Exception as e:
        logger.error(f"Error in load_template: {e}", exc_info=True)
        raise
def generate_invoice(
    invoice_data: Dict[str, Any],
    output_path: Optional[Path] = None
) -> Path:
    """
    Generate invoice from template

    Args:
        invoice_data: Dictionary with invoice data
        output_path: Optional output path (defaults to invoices directory)

    Returns:
        Path to generated invoice
    """
    template = load_template()

    # Get company info from Azure Vault or use defaults
    company_name = invoice_data.get("company_name", "[COMPANY_NAME]")
    company_address = invoice_data.get("company_address", "[COMPANY_ADDRESS]")
    company_city = invoice_data.get("company_city", "[COMPANY_CITY]")
    company_state = invoice_data.get("company_state", "[COMPANY_STATE]")
    company_zip = invoice_data.get("company_zip", "[COMPANY_ZIP]")
    company_phone = invoice_data.get("company_phone", "[COMPANY_PHONE]")
    company_email = invoice_data.get("company_email", "[COMPANY_EMAIL]")
    company_website = invoice_data.get("company_website", "[COMPANY_WEBSITE]")

    # Invoice details
    invoice_number = invoice_data.get("invoice_number", f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}")
    invoice_date = invoice_data.get("invoice_date", datetime.now().strftime("%B %d, %Y"))
    due_date = invoice_data.get("due_date", (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y"))
    status = invoice_data.get("status", "Pending")

    # Client info
    client_name = invoice_data.get("client_name", "[CLIENT_NAME]")
    client_address = invoice_data.get("client_address", "[CLIENT_ADDRESS]")
    client_city = invoice_data.get("client_city", "[CLIENT_CITY]")
    client_state = invoice_data.get("client_state", "[CLIENT_STATE]")
    client_zip = invoice_data.get("client_zip", "[CLIENT_ZIP]")
    client_email = invoice_data.get("client_email", "[CLIENT_EMAIL]")

    # Line items
    line_items = invoice_data.get("line_items", [])
    if not line_items:
        line_items = [{
            "description": "[SERVICE_DESCRIPTION]",
            "quantity": "1",
            "rate": "0.00",
            "amount": "0.00"
        }]

    # Calculate totals
    subtotal = sum(float(item.get("amount", 0)) for item in line_items)
    tax_rate = float(invoice_data.get("tax_rate", 0))
    tax_amount = subtotal * (tax_rate / 100)
    discount = float(invoice_data.get("discount", 0))
    total = subtotal + tax_amount - discount

    # Payment info
    payment_terms = invoice_data.get("payment_terms", "Net 30")
    bank_account = invoice_data.get("bank_account", "[BANK_ACCOUNT_INFO]")
    payment_link = invoice_data.get("payment_link", "[PAYMENT_LINK]")
    invoice_notes = invoice_data.get("notes", "")

    # Replace template variables
    replacements = {
        "[COMPANY_NAME]": company_name,
        "[COMPANY_ADDRESS]": company_address,
        "[COMPANY_CITY]": company_city,
        "[COMPANY_STATE]": company_state,
        "[COMPANY_ZIP]": company_zip,
        "[COMPANY_PHONE]": company_phone,
        "[COMPANY_EMAIL]": company_email,
        "[COMPANY_WEBSITE]": company_website,
        "[INVOICE_NUMBER]": invoice_number,
        "[INVOICE_DATE]": invoice_date,
        "[DUE_DATE]": due_date,
        "[STATUS]": status,
        "[CLIENT_NAME]": client_name,
        "[CLIENT_ADDRESS]": client_address,
        "[CLIENT_CITY]": client_city,
        "[CLIENT_STATE]": client_state,
        "[CLIENT_ZIP]": client_zip,
        "[CLIENT_EMAIL]": client_email,
        "[SUBTOTAL]": f"{subtotal:.2f}",
        "[TAX_RATE]": f"{tax_rate:.1f}",
        "[TAX_AMOUNT]": f"{tax_amount:.2f}",
        "[DISCOUNT]": f"{discount:.2f}",
        "[TOTAL]": f"{total:.2f}",
        "[PAYMENT_TERMS]": payment_terms,
        "[BANK_ACCOUNT_INFO]": bank_account,
        "[PAYMENT_LINK]": payment_link,
        "[INVOICE_NOTES]": invoice_notes,
    }

    # Replace basic variables
    for key, value in replacements.items():
        template = template.replace(key, str(value))

    # Replace line items
    if line_items:
        first_item = line_items[0]
        template = template.replace("[SERVICE_DESCRIPTION_1]", first_item.get("description", ""))
        template = template.replace("[QUANTITY_1]", str(first_item.get("quantity", "")))
        template = template.replace("[RATE_1]", f"{float(first_item.get('rate', 0)):.2f}")
        template = template.replace("[AMOUNT_1]", f"{float(first_item.get('amount', 0)):.2f}")

    # Save invoice
    if output_path is None:
        invoices_dir = script_dir / "data" / "invoices"
        invoices_dir.mkdir(parents=True, exist_ok=True)
        output_path = invoices_dir / f"invoice_{invoice_number.replace('-', '_')}.html"

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)

    logger.info(f"✅ Invoice generated: {output_path}")
    return output_path


def main():
    """Interactive invoice generation"""
    print("=" * 80)
    print("📄 Invoice Generator")
    print("=" * 80)
    print()

    # Collect invoice data
    invoice_data = {}

    print("Company Information:")
    invoice_data["company_name"] = input("Company Name: ").strip() or "[COMPANY_NAME]"
    invoice_data["company_address"] = input("Company Address: ").strip() or "[COMPANY_ADDRESS]"
    invoice_data["company_city"] = input("City: ").strip() or "[COMPANY_CITY]"
    invoice_data["company_state"] = input("State: ").strip() or "[COMPANY_STATE]"
    invoice_data["company_zip"] = input("ZIP: ").strip() or "[COMPANY_ZIP]"
    invoice_data["company_phone"] = input("Phone: ").strip() or "[COMPANY_PHONE]"
    invoice_data["company_email"] = input("Email: ").strip() or "[COMPANY_EMAIL]"
    invoice_data["company_website"] = input("Website: ").strip() or "[COMPANY_WEBSITE]"

    print()
    print("Invoice Details:")
    invoice_data["invoice_number"] = input("Invoice Number (or press Enter for auto): ").strip()
    if not invoice_data["invoice_number"]:
        invoice_data["invoice_number"] = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    invoice_data["invoice_date"] = input(f"Invoice Date (default: {datetime.now().strftime('%B %d, %Y')}): ").strip() or datetime.now().strftime("%B %d, %Y")
    invoice_data["due_date"] = input(f"Due Date (default: {(datetime.now() + timedelta(days=30)).strftime('%B %d, %Y')}): ").strip() or (datetime.now() + timedelta(days=30)).strftime("%B %d, %Y")

    print()
    print("Client Information:")
    invoice_data["client_name"] = input("Client Name: ").strip() or "[CLIENT_NAME]"
    invoice_data["client_address"] = input("Client Address: ").strip() or "[CLIENT_ADDRESS]"
    invoice_data["client_city"] = input("City: ").strip() or "[CLIENT_CITY]"
    invoice_data["client_state"] = input("State: ").strip() or "[CLIENT_STATE]"
    invoice_data["client_zip"] = input("ZIP: ").strip() or "[CLIENT_ZIP]"
    invoice_data["client_email"] = input("Email: ").strip() or "[CLIENT_EMAIL]"

    print()
    print("Line Items (at least one required):")
    line_items = []
    while True:
        desc = input("Description (or 'done' to finish): ").strip()
        if desc.lower() == 'done' and line_items:
            break
        if not desc:
            continue

        qty = input("  Quantity: ").strip() or "1"
        rate = input("  Rate: $").strip() or "0.00"
        amount = float(qty) * float(rate)
        line_items.append({
            "description": desc,
            "quantity": qty,
            "rate": rate,
            "amount": f"{amount:.2f}"
        })
        print(f"  → Added: {desc} (${amount:.2f})")

    invoice_data["line_items"] = line_items

    print()
    invoice_data["tax_rate"] = input("Tax Rate (%): ").strip() or "0"
    invoice_data["discount"] = input("Discount ($): ").strip() or "0"
    invoice_data["payment_terms"] = input("Payment Terms (default: Net 30): ").strip() or "Net 30"
    invoice_data["notes"] = input("Notes (optional): ").strip() or ""

    print()
    print("💾 Generating invoice...")
    output_path = generate_invoice(invoice_data)

    print()
    print(f"✅ Invoice generated successfully!")
    print(f"📄 Location: {output_path}")
    print()
    print("💡 Tip: Open the HTML file in a browser to view or print the invoice.")


if __name__ == "__main__":


    main()