#!/usr/bin/env python3
"""
Execute the Beef - Actually Use the Systems We Built

Takes the systems we've built and actually EXECUTES them:
- Run perspective validations
- Address overlooked intents
- Execute blind tests
- Integrate into workflows

Tags: #EXECUTION #THE_BEEF #ACTUAL_WORK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("ExecuteTheBeef")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ExecuteTheBeef")

try:
    from perspective_validation_system import PerspectiveValidationSystem, TestingMethod
    PERSPECTIVE_VALIDATION_AVAILABLE = True
except ImportError:
    PERSPECTIVE_VALIDATION_AVAILABLE = False
    logger.warning("Perspective validation system not available")

try:
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem, TicketType, TicketPriority
    TICKET_SYSTEM_AVAILABLE = True
except ImportError:
    TICKET_SYSTEM_AVAILABLE = False
    logger.warning("Ticket system not available")


class ExecuteTheBeef:
    """
    Execute the Beef - Actually Use the Systems

    Where's the Beef? = Where's the actual execution?
    This class actually RUNS the systems we built.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.results_dir = self.project_root / "data" / "execution_results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        logger.info("="*80)
        logger.info("🥩 EXECUTE THE BEEF - ACTUAL IMPLEMENTATION")
        logger.info("="*80)
        logger.info("")

    def execute_all(self) -> Dict[str, Any]:
        try:
            """Execute all systems - get the beef"""
            results = {
                "execution_date": datetime.now().isoformat(),
                "perspective_validations": [],
                "overlooked_intents_addressed": [],
                "blind_tests_run": [],
                "tickets_created": []
            }

            # 1. Run perspective validation on a real decision
            logger.info("🥩 1. Running Perspective Validation...")
            validation_result = self._run_perspective_validation()
            if validation_result:
                results["perspective_validations"].append(validation_result)

            # 2. Address top overlooked intent
            logger.info("🥩 2. Addressing Overlooked Intent...")
            intent_result = self._address_overlooked_intent()
            if intent_result:
                results["overlooked_intents_addressed"].append(intent_result)

            # 3. Run blind test
            logger.info("🥩 3. Running Blind Test...")
            blind_test_result = self._run_blind_test()
            if blind_test_result:
                results["blind_tests_run"].append(blind_test_result)

            # 4. Create ticket for execution
            logger.info("🥩 4. Creating Execution Ticket...")
            ticket_result = self._create_execution_ticket()
            if ticket_result:
                results["tickets_created"].append(ticket_result)

            # Save results
            results_file = self.results_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info("")
            logger.info("="*80)
            logger.info("✅ EXECUTION COMPLETE - THE BEEF DELIVERED")
            logger.info("="*80)
            logger.info(f"   Perspective Validations: {len(results['perspective_validations'])}")
            logger.info(f"   Overlooked Intents Addressed: {len(results['overlooked_intents_addressed'])}")
            logger.info(f"   Blind Tests Run: {len(results['blind_tests_run'])}")
            logger.info(f"   Tickets Created: {len(results['tickets_created'])}")
            logger.info(f"   Results: {results_file}")
            logger.info("")

            return results

        except Exception as e:
            self.logger.error(f"Error in execute_all: {e}", exc_info=True)
            raise
    def _run_perspective_validation(self) -> Optional[Dict[str, Any]]:
        """Run actual perspective validation"""
        if not PERSPECTIVE_VALIDATION_AVAILABLE:
            logger.warning("   ⚠️  Perspective validation system not available")
            return None

        try:
            system = PerspectiveValidationSystem(self.project_root)

            # Example: Validate our approach to ticket system
            result = system.validate_perspectives(
                our_perspective="Our three ticket types (PM, C, T) system is the correct approach for organizing help desk tickets",
                their_perspective="A single unified ticket system would be simpler and better",
                overall_perspective="Industry standard is to have separate systems for problems, changes, and tasks",
                testing_method=TestingMethod.DOUBLE_BLIND
            )

            logger.info(f"   ✅ Perspective validation complete")
            logger.info(f"      Our perspective correct: {result.our_perspective_correct}")
            logger.info(f"      Confidence: {result.confidence_score:.2f}")

            return {
                "validated": result.validated,
                "our_correct": result.our_perspective_correct,
                "confidence": result.confidence_score,
                "recommendations": result.recommendations
            }
        except Exception as e:
            logger.error(f"   ❌ Perspective validation failed: {e}")
            return None

    def _address_overlooked_intent(self) -> Optional[Dict[str, Any]]:
        """Address top overlooked intent"""
        intents_file = self.project_root / "data" / "user_intents" / "all_intents_extraction_report.json"

        if not intents_file.exists():
            logger.warning("   ⚠️  Intent extraction report not found")
            return None

        try:
            with open(intents_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Find highest repetition overlooked intent
            intents = data.get("consolidated_intents", [])
            overlooked = [
                i for i in intents 
                if i.get("repetition_count", 0) > 5 and 
                i.get("fulfillment_status") in ["unknown", "overlooked"]
            ]

            if not overlooked:
                logger.info("   ℹ️  No overlooked intents found")
                return None

            # Sort by repetition count
            overlooked.sort(key=lambda x: x.get("repetition_count", 0), reverse=True)
            top_intent = overlooked[0]

            logger.info(f"   ✅ Found overlooked intent: {top_intent.get('intent_text', '')[:60]}...")
            logger.info(f"      Repeated {top_intent.get('repetition_count')} times")

            # Create ticket for it
            if TICKET_SYSTEM_AVAILABLE:
                ticket_system = JARVISHelpdeskTicketSystem(self.project_root)
                ticket = ticket_system.create_ticket(
                    title=f"Address Overlooked Intent: {top_intent.get('intent_text', '')[:50]}",
                    description=f"Intent repeated {top_intent.get('repetition_count')} times. Original: {top_intent.get('intent_text', '')}",
                    ticket_type=TicketType.PROBLEM,
                    priority=TicketPriority.HIGH,
                    component="Intent Fulfillment",
                    issue_type="overlooked_intent",
                    tags=["overlooked-intent", "high-repetition", "the-beef"]
                )

                logger.info(f"   ✅ Created ticket: {ticket.ticket_id}")

                return {
                    "intent_id": top_intent.get("intent_id"),
                    "intent_text": top_intent.get("intent_text"),
                    "repetition_count": top_intent.get("repetition_count"),
                    "ticket_created": ticket.ticket_id
                }

            return {
                "intent_id": top_intent.get("intent_id"),
                "intent_text": top_intent.get("intent_text"),
                "repetition_count": top_intent.get("repetition_count"),
                "ticket_created": None
            }
        except Exception as e:
            logger.error(f"   ❌ Failed to address overlooked intent: {e}")
            return None

    def _run_blind_test(self) -> Optional[Dict[str, Any]]:
        """Run actual blind test"""
        if not PERSPECTIVE_VALIDATION_AVAILABLE:
            logger.warning("   ⚠️  Perspective validation system not available")
            return None

        try:
            system = PerspectiveValidationSystem(self.project_root)

            # Example: Blind test on implementation approach
            result = system.validate_perspectives(
                our_perspective="Incremental implementation is the best approach",
                their_perspective="Big bang implementation is better",
                overall_perspective="Industry best practice is incremental with validation",
                testing_method=TestingMethod.DOUBLE_BLIND
            )

            logger.info(f"   ✅ Blind test complete")
            logger.info(f"      Testing method: DOUBLE_BLIND")
            logger.info(f"      Our perspective correct: {result.our_perspective_correct}")

            return {
                "testing_method": "double_blind",
                "our_correct": result.our_perspective_correct,
                "confidence": result.confidence_score,
                "blinded": result.validation_metadata.get("blinded", False)
            }
        except Exception as e:
            logger.error(f"   ❌ Blind test failed: {e}")
            return None

    def _create_execution_ticket(self) -> Optional[Dict[str, Any]]:
        """Create ticket for execution tracking"""
        if not TICKET_SYSTEM_AVAILABLE:
            logger.warning("   ⚠️  Ticket system not available")
            return None

        try:
            ticket_system = JARVISHelpdeskTicketSystem(self.project_root)
            ticket = ticket_system.create_ticket(
                title="Execute the Beef - Actually Use the Systems We Built",
                description="""Execute the systems we've built:
- Run perspective validations on real decisions
- Address overlooked intents
- Execute blind tests
- Integrate systems into workflows

Where's the Beef? = Actually using the systems, not just building them.""",
                ticket_type=TicketType.CHANGE_TASK,
                priority=TicketPriority.HIGH,
                component="System Execution",
                issue_type="execution",
                tags=["the-beef", "execution", "implementation", "where-the-beef"]
            )

            logger.info(f"   ✅ Created execution ticket: {ticket.ticket_id}")

            return {
                "ticket_id": ticket.ticket_id,
                "title": ticket.title,
                "status": ticket.status.value
            }
        except Exception as e:
            logger.error(f"   ❌ Failed to create execution ticket: {e}")
            return None


def main():
    try:
        """Main execution"""
        project_root = Path(__file__).parent.parent.parent
        executor = ExecuteTheBeef(project_root)
        results = executor.execute_all()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())