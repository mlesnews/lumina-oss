#!/usr/bin/env python3
"""
JARVIS Workflow Certification Manager

Manages certification status for workflows, tickets, and business/technical areas.
Certification is required before automatic archiving.

Tags: #CERTIFICATION #WORKFLOW #HELPDESK #FINTECH
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCertManager")


class WorkflowCertificationManager:
    """Manages workflow certification status"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.certification_dir = project_root / "data" / "workflow_certifications"
        self.certification_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Workflow Certification Manager initialized")

    def certify(self, item_id: str, item_type: str = "agent",
                    certified_by: str = "JARVIS",
                    certification_notes: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Certify a workflow, ticket, or area"""
            cert_file = self.certification_dir / f"{item_type}_{item_id}_certification.json"

            cert_data = {
                "item_id": item_id,
                "item_type": item_type,
                "status": "certified",
                "passed": True,
                "certified_at": datetime.now().isoformat(),
                "certified_by": certified_by,
                "certification_notes": certification_notes or "Certification passed",
                "certification_criteria": {
                    "functionality_verified": True,
                    "integration_tested": True,
                    "performance_acceptable": True,
                    "security_validated": True
                }
            }

            with open(cert_file, 'w', encoding='utf-8') as f:
                json.dump(cert_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ✅ Certified {item_type} {item_id}")
            return cert_data

        except Exception as e:
            logger.error(f"Error in certify: {e}", exc_info=True)
            raise

    def revoke_certification(self, item_id: str, item_type: str = "agent",
                                reason: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Revoke certification for an item"""
            cert_file = self.certification_dir / f"{item_type}_{item_id}_certification.json"

            if cert_file.exists():
                with open(cert_file, 'r', encoding='utf-8') as f:
                    cert_data = json.load(f)

            cert_data["status"] = "revoked"
            cert_data["passed"] = False
            cert_data["revoked_at"] = datetime.now().isoformat()
            cert_data["revocation_reason"] = reason or "Certification revoked"

            with open(cert_file, 'w', encoding='utf-8') as f:
                json.dump(cert_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"   ⚠️  Revoked certification for {item_type} {item_id}")
            return cert_data

        except Exception as e:
            self.logger.error(f"Error in revoke_certification: {e}", exc_info=True)
            raise
    def get_certification(self, item_id: str, item_type: str = "agent") -> Optional[Dict]:
        """Get certification status"""
        cert_file = self.certification_dir / f"{item_type}_{item_id}_certification.json"

        if not cert_file.exists():
            return None

        try:
            with open(cert_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Workflow Certification Manager")
        parser.add_argument("--certify", type=str,
                           help="Certify an item (format: ITEM_ID:TYPE)")
        parser.add_argument("--revoke", type=str,
                           help="Revoke certification (format: ITEM_ID:TYPE)")
        parser.add_argument("--status", type=str,
                           help="Get certification status (format: ITEM_ID:TYPE)")
        parser.add_argument("--notes", type=str,
                           help="Certification notes")

        args = parser.parse_args()

        manager = WorkflowCertificationManager()

        if args.certify:
            parts = args.certify.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.certify(item_id, item_type, certification_notes=args.notes)
            print(json.dumps(result, indent=2))
        elif args.revoke:
            parts = args.revoke.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.revoke_certification(item_id, item_type, reason=args.notes)
            print(json.dumps(result, indent=2))
        elif args.status:
            parts = args.status.split(":")
            item_id = parts[0]
            item_type = parts[1] if len(parts) > 1 else "agent"
            result = manager.get_certification(item_id, item_type)
            if result:
                print(json.dumps(result, indent=2))
            else:
                print(f"No certification found for {item_type} {item_id}")
        else:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())