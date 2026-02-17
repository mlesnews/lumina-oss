#!/usr/bin/env python3
"""
LUMINA Affiliate Programs

"AFFILIATE PROGRAMS. TAKE ADVANTAGE OF. AND TO CREATE OUR OWN"

This system:
- Manages using existing affiliate programs (take advantage of)
- Creates and manages our own affiliate program
- Tracks commissions, referrals, partnerships
- Integrates with LUMINA Trading Premium and other products
- Token-based rewards using BAT (Brave Browser) and ICP (Internet Computer Protocol)
- Web2/Web3 hybrid infrastructure
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaAffiliatePrograms")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AffiliateStatus(Enum):
    """Affiliate status"""
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class CommissionType(Enum):
    """Commission types"""
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    TIERED = "tiered"


@dataclass
class ExternalAffiliateProgram:
    """External affiliate program we're participating in"""
    program_id: str
    name: str
    description: str
    url: str
    affiliate_link: str
    commission_rate: float
    commission_type: CommissionType
    cookie_duration_days: int = 30
    status: AffiliateStatus = AffiliateStatus.ACTIVE
    products: List[str] = field(default_factory=list)
    notes: str = ""
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["commission_type"] = self.commission_type.value
        data["status"] = self.status.value
        return data


@dataclass
class LuminAffiliatePartner:
    """Partner in LUMINA's affiliate program"""
    partner_id: str
    name: str
    email: str
    referral_code: str
    affiliate_link: str
    commission_rate: float
    commission_type: CommissionType
    status: AffiliateStatus = AffiliateStatus.PENDING
    total_referrals: int = 0
    total_commissions: float = 0.0
    paid_commissions: float = 0.0
    pending_commissions: float = 0.0
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_referral_date: Optional[str] = None
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["commission_type"] = self.commission_type.value
        data["status"] = self.status.value
        return data


@dataclass
class Referral:
    """A referral from an affiliate"""
    referral_id: str
    partner_id: str
    customer_email: str
    product: str
    amount: float
    commission: float
    status: str  # "pending", "approved", "paid", "cancelled"
    referral_date: str = field(default_factory=lambda: datetime.now().isoformat())
    approval_date: Optional[str] = None
    payment_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaAffiliatePrograms:
    """
    LUMINA Affiliate Programs

    "AFFILIATE PROGRAMS. TAKE ADVANTAGE OF. AND TO CREATE OUR OWN"

    Manages:
    - Using existing affiliate programs (external)
    - Creating and managing our own affiliate program (internal)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize LUMINA Affiliate Programs"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaAffiliatePrograms")

        # External affiliate programs (we participate in)
        self.external_programs: List[ExternalAffiliateProgram] = []

        # Our affiliate program (partners who refer to us)
        self.partners: List[LuminAffiliatePartner] = []
        self.referrals: List[Referral] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_affiliate_programs"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self._load_data()

        # Initialize with common affiliate programs
        self._initialize_external_programs()

        self.logger.info("💰 LUMINA Affiliate Programs initialized")
        self.logger.info("   Taking advantage of existing programs")
        self.logger.info("   Creating our own affiliate program")

    def _load_data(self) -> None:
        """Load existing affiliate program data"""
        external_file = self.data_dir / "external_programs.json"
        partners_file = self.data_dir / "partners.json"
        referrals_file = self.data_dir / "referrals.json"

        if external_file.exists():
            try:
                with open(external_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.external_programs = [
                        ExternalAffiliateProgram(
                            status=AffiliateStatus(p['status']),
                            commission_type=CommissionType(p['commission_type']),
                            **{k: v for k, v in p.items() if k not in ['status', 'commission_type']}
                        ) for p in data
                    ]
            except Exception as e:
                self.logger.warning(f"  Could not load external programs: {e}")

        if partners_file.exists():
            try:
                with open(partners_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.partners = [
                        LuminAffiliatePartner(
                            status=AffiliateStatus(p['status']),
                            commission_type=CommissionType(p['commission_type']),
                            **{k: v for k, v in p.items() if k not in ['status', 'commission_type']}
                        ) for p in data
                    ]
            except Exception as e:
                self.logger.warning(f"  Could not load partners: {e}")

        if referrals_file.exists():
            try:
                with open(referrals_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.referrals = [Referral(**r) for r in data]
            except Exception as e:
                self.logger.warning(f"  Could not load referrals: {e}")

    def _save_data(self) -> None:
        try:
            """Save affiliate program data"""
            external_file = self.data_dir / "external_programs.json"
            partners_file = self.data_dir / "partners.json"
            referrals_file = self.data_dir / "referrals.json"

            with open(external_file, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.external_programs], f, indent=2)

            with open(partners_file, 'w', encoding='utf-8') as f:
                json.dump([p.to_dict() for p in self.partners], f, indent=2)

            with open(referrals_file, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in self.referrals], f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_data: {e}", exc_info=True)
            raise
    def _initialize_external_programs(self) -> None:
        """Initialize with common affiliate programs to consider"""
        if self.external_programs:
            return  # Already loaded

        # Common affiliate programs to take advantage of
        programs = [
            ExternalAffiliateProgram(
                program_id="aws",
                name="Amazon Web Services (AWS)",
                description="Cloud services affiliate program",
                url="https://aws.amazon.com/",
                affiliate_link="[TO_BE_SET]",
                commission_rate=0.0,  # Varies by service
                commission_type=CommissionType.PERCENTAGE,
                status=AffiliateStatus.PENDING,
                notes="Research commission rates and sign up"
            ),
            ExternalAffiliateProgram(
                program_id="google-cloud",
                name="Google Cloud Platform",
                description="Cloud services affiliate program",
                url="https://cloud.google.com/",
                affiliate_link="[TO_BE_SET]",
                commission_rate=0.0,
                commission_type=CommissionType.PERCENTAGE,
                status=AffiliateStatus.PENDING,
                notes="Research commission rates and sign up"
            ),
            ExternalAffiliateProgram(
                program_id="github",
                name="GitHub",
                description="Developer tools affiliate program",
                url="https://github.com/",
                affiliate_link="[TO_BE_SET]",
                commission_rate=0.0,
                commission_type=CommissionType.PERCENTAGE,
                status=AffiliateStatus.PENDING,
                notes="Check if affiliate program exists"
            )
        ]

        self.external_programs = programs
        self._save_data()
        self.logger.info(f"  ✅ Initialized {len(programs)} external affiliate programs")

    def add_external_program(
        self,
        name: str,
        url: str,
        affiliate_link: str,
        commission_rate: float,
        description: str = "",
        commission_type: CommissionType = CommissionType.PERCENTAGE
    ) -> ExternalAffiliateProgram:
        """Add an external affiliate program we're participating in"""
        program_id = name.lower().replace(" ", "-").replace("_", "-")

        program = ExternalAffiliateProgram(
            program_id=program_id,
            name=name,
            description=description,
            url=url,
            affiliate_link=affiliate_link,
            commission_rate=commission_rate,
            commission_type=commission_type,
            status=AffiliateStatus.ACTIVE
        )

        self.external_programs.append(program)
        self._save_data()
        self.logger.info(f"  ✅ Added external affiliate program: {name}")

        return program

    def create_affiliate_partner(
        self,
        name: str,
        email: str,
        commission_rate: float = 20.0,  # Default 20%
        commission_type: CommissionType = CommissionType.PERCENTAGE
    ) -> LuminAffiliatePartner:
        """Create a new affiliate partner in our program"""
        partner_id = f"partner_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        referral_code = name.lower().replace(" ", "-")[:20] + "-" + partner_id[-8:]
        affiliate_link = f"https://lumina.ai/ref/{referral_code}"

        partner = LuminAffiliatePartner(
            partner_id=partner_id,
            name=name,
            email=email,
            referral_code=referral_code,
            affiliate_link=affiliate_link,
            commission_rate=commission_rate,
            commission_type=commission_type,
            status=AffiliateStatus.PENDING
        )

        self.partners.append(partner)
        self._save_data()
        self.logger.info(f"  ✅ Created affiliate partner: {name} ({referral_code})")

        return partner

    def record_referral(
        self,
        partner_id: str,
        customer_email: str,
        product: str,
        amount: float
    ) -> Referral:
        """Record a referral from an affiliate partner"""
        partner = next((p for p in self.partners if p.partner_id == partner_id), None)
        if not partner:
            raise ValueError(f"Partner {partner_id} not found")

        # Calculate commission
        if partner.commission_type == CommissionType.PERCENTAGE:
            commission = amount * (partner.commission_rate / 100.0)
        else:
            commission = partner.commission_rate  # Fixed amount

        referral_id = f"ref_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        referral = Referral(
            referral_id=referral_id,
            partner_id=partner_id,
            customer_email=customer_email,
            product=product,
            amount=amount,
            commission=commission,
            status="pending"
        )

        self.referrals.append(referral)

        # Update partner stats
        partner.total_referrals += 1
        partner.pending_commissions += commission
        partner.total_commissions += commission
        partner.last_referral_date = datetime.now().isoformat()

        self._save_data()
        self.logger.info(f"  ✅ Recorded referral: {product} (${amount:.2f}) -> ${commission:.2f} commission")

        return referral

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of affiliate programs"""
        active_external = len([p for p in self.external_programs if p.status == AffiliateStatus.ACTIVE])
        active_partners = len([p for p in self.partners if p.status == AffiliateStatus.ACTIVE])
        total_referrals = len(self.referrals)
        total_commissions = sum([p.total_commissions for p in self.partners])
        pending_commissions = sum([p.pending_commissions for p in self.partners])

        return {
            "external_programs": {
                "total": len(self.external_programs),
                "active": active_external,
                "pending": len([p for p in self.external_programs if p.status == AffiliateStatus.PENDING])
            },
            "our_affiliate_program": {
                "total_partners": len(self.partners),
                "active_partners": active_partners,
                "total_referrals": total_referrals,
                "total_commissions": total_commissions,
                "pending_commissions": pending_commissions,
                "paid_commissions": sum([p.paid_commissions for p in self.partners])
            },
            "philosophy": "Take advantage of existing affiliate programs. Create our own affiliate program."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Affiliate Programs")
    parser.add_argument("--summary", action="store_true", help="Get affiliate program summary")
    parser.add_argument("--add-external", nargs=5, metavar=("NAME", "URL", "LINK", "RATE", "DESC"), help="Add external affiliate program")
    parser.add_argument("--create-partner", nargs=3, metavar=("NAME", "EMAIL", "RATE"), help="Create affiliate partner")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    affiliate = LuminaAffiliatePrograms()

    if args.summary:
        summary = affiliate.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n💰 LUMINA Affiliate Programs Summary")
            print(f"\n   External Programs (Taking Advantage Of):")
            print(f"     Total: {summary['external_programs']['total']}")
            print(f"     Active: {summary['external_programs']['active']}")
            print(f"\n   Our Affiliate Program:")
            print(f"     Partners: {summary['our_affiliate_program']['total_partners']}")
            print(f"     Active: {summary['our_affiliate_program']['active_partners']}")
            print(f"     Referrals: {summary['our_affiliate_program']['total_referrals']}")
            print(f"     Total Commissions: ${summary['our_affiliate_program']['total_commissions']:.2f}")
            print(f"     Pending: ${summary['our_affiliate_program']['pending_commissions']:.2f}")
            print(f"\n   Philosophy: {summary['philosophy']}")

    elif args.add_external:
        name, url, link, rate, desc = args.add_external
        program = affiliate.add_external_program(name, url, link, float(rate), desc)
        print(f"✅ Added external program: {program.name}")

    elif args.create_partner:
        name, email, rate = args.create_partner
        partner = affiliate.create_affiliate_partner(name, email, float(rate))
        print(f"✅ Created partner: {partner.name}")
        print(f"   Referral Code: {partner.referral_code}")
        print(f"   Affiliate Link: {partner.affiliate_link}")

    else:
        parser.print_help()
        print("\n💰 LUMINA Affiliate Programs")
        print("   Take advantage of existing programs")
        print("   Create our own affiliate program")

