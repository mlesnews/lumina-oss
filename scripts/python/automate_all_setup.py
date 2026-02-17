#!/usr/bin/env python3
"""
Automate All Setup - Non-interactive setup automation
Creates all guides, checklists, and automation scripts
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

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

logger = get_logger("AutomateAllSetup")


def create_financial_setup_guide():
    """Create comprehensive financial setup guide"""
    guide_content = """# Financial Setup Guide

## Step 1: Business Bank Account

### Why It's Critical
- Separates business and personal finances
- Required for professional operations
- Easier accounting and tax preparation

### What You Need
- EIN (Employer Identification Number)
- Articles of Incorporation/Organization
- Business license (if required)
- Operating Agreement (for LLC)

### Recommended Banks
- **Local Banks/Credit Unions**: Better service, local support
- **Chase Business**: Good for larger operations
- **Bank of America**: Extensive branch network
- **Online Banks**: Lower fees, better rates

### Estimated Time: 1-2 hours

---

## Step 2: Accounting Software

### Options Comparison

| Software | Price | Best For |
|----------|-------|----------|
| **QuickBooks Online** | $25-150/month | Full-featured, most popular |
| **Xero** | $13-70/month | Modern interface, good integrations |
| **FreshBooks** | $15-50/month | Service-based businesses |
| **Spreadsheet** | Free | Very small operations |

### QuickBooks Setup Checklist
- [ ] Create account
- [ ] Set up chart of accounts
- [ ] Connect bank account
- [ ] Set up invoice templates
- [ ] Configure tax settings
- [ ] Set up expense categories

### Estimated Time: 1-2 hours

---

## Step 3: Payment Processor

### Options

**Stripe**
- Fees: 2.9% + $0.30 per transaction
- Best for: Online businesses, subscriptions
- Setup: 30-60 minutes

**PayPal Business**
- Fees: 2.9% + $0.30 per transaction
- Best for: Quick setup, wide acceptance
- Setup: 15-30 minutes

**Square**
- Fees: 2.6% + $0.10 per transaction
- Best for: In-person sales, small businesses
- Setup: 30 minutes

### Setup Steps
1. Create business account
2. Verify business information
3. Connect bank account
4. Set up payment forms/links
5. Test transaction
6. Integrate with accounting software

### Estimated Time: 30-60 minutes

---

## Step 4: Business Credit Card

### Benefits
- Separates business expenses
- Builds business credit
- Easier expense tracking
- Rewards/cashback

### Recommended Cards
- **Chase Ink Business**: Good rewards
- **American Express Business**: Premium benefits
- **Capital One Spark**: Simple, good for startups

### Estimated Time: 30 minutes

---

## Step 5: Start Expense Tracking

### Use Our Expense Tracker
```powershell
python scripts/python/track_expenses.py
```

### Best Practices
- Track every expense immediately
- Keep receipts (digital or physical)
- Categorize expenses properly
- Review weekly
- Reconcile monthly

### Expense Categories
- Office Supplies
- Software/Subscriptions
- Marketing
- Professional Services
- Travel
- Utilities
- Insurance
- Legal/Accounting

---

## Financial Setup Checklist

- [ ] Business bank account opened
- [ ] Accounting software set up
- [ ] Payment processor configured
- [ ] Business credit card applied for
- [ ] Expense tracking started
- [ ] Bank account connected to accounting software
- [ ] Invoice system tested
- [ ] Payment methods set up for clients

---

## Next Steps After Financial Setup

1. Generate first invoice: `python scripts/python/generate_invoice.py`
2. Set up recurring billing (if applicable)
3. Create financial reports template
4. Set up tax preparation system
5. Establish monthly financial review process

---

**Created:** [TIMESTAMP]
"""

    guide_file = script_dir / "docs" / "business" / "FINANCIAL_SETUP_GUIDE.md"
    guide_file.parent.mkdir(parents=True, exist_ok=True)

    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content.replace("[TIMESTAMP]", datetime.now().isoformat()))

    logger.info(f"✅ Created financial setup guide: {guide_file}")
    return guide_file


def create_legal_verification_guide():
    """Create legal verification guide"""
    guide_content = """# Legal Verification Checklist

## Business Registration Verification

### Checklist
- [ ] Verify business entity is properly registered
- [ ] Confirm registration number/documentation
- [ ] Check registration expiration date (if applicable)
- [ ] Verify registered agent information
- [ ] Confirm business name is correct
- [ ] Check for any pending compliance issues

### Where to Check
- **State Secretary of State website**: Search business database
- **Business registration documents**: Review original filing
- **Registered agent**: Confirm contact information is current

### Estimated Time: 30 minutes

---

## EIN Verification

### Checklist
- [ ] Confirm EIN is obtained from IRS
- [ ] Verify EIN is documented
- [ ] Check EIN letter from IRS (CP 575)
- [ ] Store EIN securely in Azure Vault
- [ ] Verify EIN matches business name
- [ ] Confirm EIN is used on all business documents

### Storage
- ✅ Store in Azure Vault: `business-ein`
- ❌ Do NOT store in files or code

### Estimated Time: 15 minutes

---

## Business Licenses

### State License
- [ ] Check state business license requirements
- [ ] Verify if license is required for your business type
- [ ] Apply for license if needed
- [ ] Document license number
- [ ] Note expiration date
- [ ] Set reminder for renewal

### Local/City License
- [ ] Check city/county business license requirements
- [ ] Apply for local license if required
- [ ] Document license number
- [ ] Note expiration date

### Industry-Specific Licenses
- [ ] Research industry-specific license requirements
- [ ] Apply for required licenses
- [ ] Document all license numbers
- [ ] Set up renewal reminders

### Estimated Time: 1-2 hours (varies by location)

---

## Insurance

### General Liability Insurance
- [ ] Research coverage needs
- [ ] Get quotes from 3+ providers
- [ ] Compare coverage and costs
- [ ] Purchase policy
- [ ] Document policy number and expiration
- [ ] Store in Azure Vault

### Professional Liability (E&O)
- [ ] Determine if needed for your business
- [ ] Get quotes if applicable
- [ ] Purchase if required
- [ ] Document policy information

### Workers Compensation
- [ ] Required if you have employees
- [ ] Research state requirements
- [ ] Purchase if applicable

### Business Property Insurance
- [ ] Assess property/assets to insure
- [ ] Get quotes
- [ ] Purchase policy

### Cyber Liability Insurance
- [ ] Consider if handling customer data
- [ ] Get quotes if applicable
- [ ] Purchase if recommended

### Estimated Time: 2-3 hours

---

## Tax Registration

### State Tax Registration
- [ ] Register for state income tax (if applicable)
- [ ] Register for state sales tax (if applicable)
- [ ] Get state tax ID number
- [ ] Document registration numbers

### Local Tax Registration
- [ ] Check local tax requirements
- [ ] Register if required
- [ ] Document registration

### Sales Tax Permit
- [ ] Determine if you need sales tax permit
- [ ] Apply for permit if selling products/services
- [ ] Document permit number
- [ ] Set up sales tax collection system

### Employer Tax Registration
- [ ] Register for employer taxes (if hiring)
- [ ] Set up payroll tax system
- [ ] Document registration numbers

### Estimated Time: 1-2 hours

---

## Legal Verification Summary

### Priority 1 (Do First)
1. ✅ Business registration verification
2. ✅ EIN verification and storage
3. ✅ Required business licenses

### Priority 2 (Do Soon)
4. ⏳ General liability insurance
5. ⏳ Tax registrations
6. ⏳ Professional liability insurance (if applicable)

### Priority 3 (As Needed)
7. ⏳ Additional insurance types
8. ⏳ Industry-specific licenses
9. ⏳ Employer registrations (when hiring)

---

## Storage of Legal Documents

### In Azure Vault (Sensitive)
- EIN
- Tax ID numbers
- License numbers
- Insurance policy numbers

### In Secure File System
- Registration documents
- License certificates
- Insurance certificates
- Tax registration confirmations

### File Locations
- `data/legal/registration/` - Business registration docs
- `data/legal/licenses/` - License certificates
- `data/legal/insurance/` - Insurance documents
- `data/legal/taxes/` - Tax registration docs

---

## Compliance Reminders

### Set Up Reminders For
- License renewals
- Insurance renewals
- Tax filing deadlines
- Annual report filings
- Registration updates

### Recommended Tools
- Calendar reminders
- Task management system
- N8N automation workflows

---

**Created:** [TIMESTAMP]
**Next Review:** [NEXT_MONTH]
"""

    guide_file = script_dir / "docs" / "business" / "LEGAL_VERIFICATION_GUIDE.md"
    guide_file.parent.mkdir(parents=True, exist_ok=True)

    next_month = (datetime.now().replace(day=1) + timedelta(days=32)).replace(day=1)

    with open(guide_file, 'w', encoding='utf-8') as f:
        content = guide_content.replace("[TIMESTAMP]", datetime.now().isoformat())
        content = content.replace("[NEXT_MONTH]", next_month.strftime("%B %Y"))
        f.write(content)

    logger.info(f"✅ Created legal verification guide: {guide_file}")
    return guide_file


def create_master_checklist():
    try:
        """Create master startup checklist"""
        checklist = {
            "startup_master_checklist": {
                "phase_1_foundation": {
                    "legal_financial": {
                        "business_registration": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "30 minutes"
                        },
                        "ein_verification": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "15 minutes"
                        },
                        "business_bank_account": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "1-2 hours"
                        },
                        "accounting_software": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "1-2 hours"
                        },
                        "payment_processor": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "30-60 minutes"
                        }
                    },
                    "communication": {
                        "elevenlabs_comms": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "15 minutes"
                        },
                        "email_signature": {
                            "status": "pending",
                            "priority": "medium",
                            "estimated_time": "15 minutes"
                        }
                    },
                    "operations": {
                        "business_config": {
                            "status": "pending",
                            "priority": "high",
                            "estimated_time": "15 minutes"
                        },
                        "sensitive_data_storage": {
                            "status": "pending",
                            "priority": "critical",
                            "estimated_time": "30 minutes"
                        },
                        "first_sop": {
                            "status": "pending",
                            "priority": "medium",
                            "estimated_time": "1 hour"
                        },
                        "task_management": {
                            "status": "completed",
                            "priority": "medium",
                            "estimated_time": "N/A"
                        }
                    }
                },
                "phase_2_growth": {
                    "marketing": {
                        "website": {"status": "pending", "priority": "medium"},
                        "social_media": {"status": "pending", "priority": "low"},
                        "business_cards": {"status": "pending", "priority": "low"}
                    },
                    "sales": {
                        "crm_setup": {"status": "pending", "priority": "medium"},
                        "proposal_template": {"status": "completed", "priority": "medium"},
                        "contract_templates": {"status": "pending", "priority": "medium"}
                    }
                }
            },
            "created": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }

        checklist_file = script_dir / "docs" / "business" / "MASTER_STARTUP_CHECKLIST.json"
        checklist_file.parent.mkdir(parents=True, exist_ok=True)

        with open(checklist_file, 'w', encoding='utf-8') as f:
            json.dump(checklist, f, indent=2, ensure_ascii=False)

        logger.info(f"✅ Created master checklist: {checklist_file}")
        return checklist_file


    except Exception as e:
        logger.error(f"Error in create_master_checklist: {e}", exc_info=True)
        raise
def main():
    """Run all automation"""
    print("="*80)
    print("🚀 AUTOMATING ALL STARTUP SETUP")
    print("="*80)
    print()

    files_created = []

    print("📋 Creating Financial Setup Guide...")
    files_created.append(create_financial_setup_guide())

    print("📋 Creating Legal Verification Guide...")
    files_created.append(create_legal_verification_guide())

    print("📋 Creating Master Startup Checklist...")
    files_created.append(create_master_checklist())

    print()
    print("="*80)
    print("✅ AUTOMATION COMPLETE")
    print("="*80)
    print()
    print(f"📄 Created {len(files_created)} files:")
    for file in files_created:
        print(f"   ✅ {file.relative_to(script_dir)}")
    print()
    print("📚 All guides and checklists are ready!")
    print("   Review and complete the items in each guide.")
    print()


if __name__ == "__main__":


    main()