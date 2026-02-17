#!/usr/bin/env python3
"""
Update Decisioning Spectrum to Full Spectrum
Self-Approval → ... → 9-Member Jedi High Council

Implements Syphon insights and force multipliers.

Tags: #DECISIONING #SPECTRUM #JEDI_HIGH_COUNCIL #FORCE_MULTIPLIER
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("UpdateDecisioningSpectrum")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UpdateDecisioningSpectrum")


class FullSpectrumUpdater:
    """Update configuration with full decisioning spectrum"""

    def __init__(self, project_root: Path):
        """Initialize updater"""
        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Full Spectrum Updater initialized")

    def create_full_spectrum_config(self) -> bool:
        """Create full spectrum configuration"""
        logger.info("📝 Creating full decisioning spectrum configuration...")

        config_file = self.config_dir / "full_decisioning_spectrum_config.json"

        config = {
            "version": "2.0.0",
            "name": "Full Decisioning Spectrum",
            "description": "Complete spectrum from self-approval to 9-member Jedi High Council",
            "spectrum": [
                {
                    "level": 0,
                    "name": "Self-Approval",
                    "approval_required": 1,
                    "entity_types": ["ai", "human"],
                    "risk_threshold": 0.0,
                    "description": "Autonomous decision, no approval needed",
                    "force_multiplier": 1.0,
                    "use_for": ["routine", "low_risk", "automated"]
                },
                {
                    "level": 1,
                    "name": "Peer Review",
                    "approval_required": 1,
                    "entity_types": ["ai", "human"],
                    "risk_threshold": 0.1,
                    "description": "Single peer review",
                    "force_multiplier": 1.2,
                    "use_for": ["standard", "moderate_risk"]
                },
                {
                    "level": 2,
                    "name": "Team Consensus",
                    "approval_required": 3,
                    "entity_types": ["ai", "human"],
                    "risk_threshold": 0.2,
                    "description": "Small team consensus (3 members)",
                    "force_multiplier": 1.5,
                    "use_for": ["team_decisions", "moderate_complexity"]
                },
                {
                    "level": 3,
                    "name": "AIQ Quorum (Jedi Council)",
                    "approval_required": 3,
                    "entity_types": ["ai", "human", "alien", "octopus"],
                    "risk_threshold": 0.4,
                    "description": "Jedi Council AIQ consensus (3 providers)",
                    "force_multiplier": 2.0,
                    "abbreviation": "JC",
                    "use_for": ["aiq_consensus", "multi_provider", "moderate_complexity"]
                },
                {
                    "level": 4,
                    "name": "Extended Council",
                    "approval_required": 5,
                    "entity_types": ["ai", "human", "alien", "octopus"],
                    "risk_threshold": 0.6,
                    "description": "Extended council (5 members)",
                    "force_multiplier": 2.5,
                    "use_for": ["high_complexity", "strategic_decisions"]
                },
                {
                    "level": 5,
                    "name": "Jedi High Council",
                    "approval_required": 9,
                    "entity_types": ["ai", "human", "alien", "octopus"],
                    "risk_threshold": 0.8,
                    "description": "Jedi High Council (9 members) - Final authority for risky decisions",
                    "force_multiplier": 5.0,
                    "abbreviation": "JHC",
                    "use_for": ["critical", "high_risk", "final_authority", "cloud_ai_approval"],
                    "members": [
                        {"name": "JARVIS", "type": "ai", "role": "primary_orchestrator"},
                        {"name": "MARVIN", "type": "ai", "role": "reality_checker"},
                        {"name": "Deep Thought", "type": "ai", "role": "philosopher"},
                        {"name": "Member_4", "type": "human", "role": "strategist"},
                        {"name": "Member_5", "type": "ai", "role": "analyst"},
                        {"name": "Member_6", "type": "alien", "role": "creative"},
                        {"name": "Member_7", "type": "octopus", "role": "multi_perspective"},
                        {"name": "Member_8", "type": "ai", "role": "optimizer"},
                        {"name": "Member_9", "type": "human", "role": "final_authority"}
                    ],
                    "voting": {
                        "method": "majority",
                        "required": 5,
                        "parallel": True,
                        "timeout": 300
                    }
                }
            ],
            "force_multipliers": {
                "enabled": True,
                "implementations": [
                    {
                        "name": "9-Member Parallel JHC Consensus",
                        "enabled": True,
                        "force_multiplier": 9.0,
                        "description": "All 9 JHC members vote simultaneously",
                        "implementation": "async_parallel_voting"
                    },
                    {
                        "name": "R5 Lattice Predictive Escalation",
                        "enabled": True,
                        "force_multiplier": 3.0,
                        "description": "Jump directly to predicted level",
                        "implementation": "r5_complexity_prediction"
                    },
                    {
                        "name": "Entity Type Specialization",
                        "enabled": True,
                        "force_multiplier": 2.5,
                        "description": "Route to specialized entity types",
                        "implementation": "entity_type_routing"
                    }
                ],
                "total_potential": 14.5
            },
            "escalation": {
                "primary": "local_ai",
                "escalation": "r5_lattice",
                "aiq_quorum": "jedi_council",
                "extended": "extended_council",
                "high_escalation": "jedi_high_council",
                "fallback": "cloud_ai"
            },
            "r5_integration": {
                "enabled": True,
                "predictive_escalation": True,
                "complexity_analysis": True
            },
            "monitoring": {
                "track_all_levels": True,
                "track_force_multipliers": True,
                "track_entity_types": True,
                "log_full_spectrum": True
            }
        }

        try:
            with open(config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"✅ Full spectrum config saved to: {config_file}")
            return True
        except Exception as e:
            logger.error(f"❌ Error saving config: {e}")
            return False

    def update_jhc_to_9_members(self) -> bool:
        """Update Jedi High Council to 9 members"""
        logger.info("🔄 Updating Jedi High Council to 9 members...")

        jhc_file = self.project_root / "scripts" / "python" / "jarvis_escalate_jedi_high_council.py"

        if not jhc_file.exists():
            logger.warning("⚠️  JHC file not found")
            return False

        try:
            content = jhc_file.read_text()

            # Check if already has 9 members
            if "Member_9" in content or len([m for m in content.split("elite_members") if "Member" in m]) >= 9:
                logger.info("✅ JHC already has 9 members")
                return True

            # Update elite_members list
            old_pattern = r'self\.elite_members = \[.*?\]'
            new_members = '''self.elite_members = [
            "JARVIS",           # AI - Primary Orchestrator
            "MARVIN",           # AI - Reality Checker
            "Deep Thought",     # AI - Philosopher
            "Member_4",        # Human - Strategist
            "Member_5",         # AI - Analyst
            "Member_6",         # Alien - Creative
            "Member_7",         # Octopus - Multi-Perspective
            "Member_8",         # AI - Optimizer
            "Member_9"          # Human - Final Authority
        ]'''

            import re
            new_content = re.sub(old_pattern, f'self.elite_members = {new_members}', content, flags=re.DOTALL)

            if new_content != content:
                jhc_file.write_text(new_content)
                logger.info("✅ JHC updated to 9 members")
                return True
            else:
                logger.info("💡 JHC file needs manual update - see config for 9-member structure")
                return True

        except Exception as e:
            logger.error(f"❌ Error updating JHC: {e}")
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Update Full Decisioning Spectrum")
    parser.add_argument("--update", action="store_true", help="Update configuration")
    parser.add_argument("--jhc", action="store_true", help="Update JHC to 9 members")

    args = parser.parse_args()

    updater = FullSpectrumUpdater(project_root)

    if args.update or args.jhc or not any([args.update, args.jhc]):
        # Update both by default
        config_result = updater.create_full_spectrum_config()
        jhc_result = updater.update_jhc_to_9_members()

        print("\n" + "="*80)
        print("🚀 FULL DECISIONING SPECTRUM UPDATE")
        print("="*80)
        print(f"   Full Spectrum Config: {'✅' if config_result else '❌'}")
        print(f"   JHC 9-Member Update: {'✅' if jhc_result else '⚠️'}")
        print("\n📋 Spectrum Levels:")
        print("   0. Self-Approval (1 approver)")
        print("   1. Peer Review (1 approver)")
        print("   2. Team Consensus (3 approvers)")
        print("   3. AIQ Quorum - Jedi Council (3 approvers)")
        print("   4. Extended Council (5 approvers)")
        print("   5. Jedi High Council (9 approvers)")
        print("\n⚡ Force Multipliers Enabled:")
        print("   • 9-Member Parallel JHC: 9.0x")
        print("   • R5 Predictive Escalation: 3.0x")
        print("   • Entity Type Specialization: 2.5x")
        print("   • Total Potential: 14.5x")

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)