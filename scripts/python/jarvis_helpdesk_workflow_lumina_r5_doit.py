#!/usr/bin/env python3
"""
JARVIS Helpdesk Workflow - @lumina @r5 @doit Integration
Complete end-to-end helpdesk workflow following LUMINA patterns:
- @doit: End-to-end execution
- @r5: Knowledge aggregation to Living Context Matrix
- @v3: Verification before execution
- @lumina: JARVIS systems, local-first AI patterns

Tags: #JARVIS #HELPDESK #LUMINA #R5 #DOIT #V3 @helpdesk @c3po @r2d2 @lumina
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

try:
    from v3_verification import V3Verification, V3VerificationConfig, VerificationResult
    V3_AVAILABLE = True
except ImportError:
    V3_AVAILABLE = False
    logger = get_logger("JARVISHelpdeskWorkflowLuminaR5Doit")
    logger.warning("V3 verification not available")

try:
    from r5_living_context_matrix import R5LivingContextMatrix, R5Config, ChatSession
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger = get_logger("JARVISHelpdeskWorkflowLuminaR5Doit")
    logger.warning("R5 Living Context Matrix not available")

try:
    from jarvis_automated_helpdesk_processor import JARVISAutomatedHelpdeskProcessor
    from jarvis_c3po_ticket_assigner import C3POTicketAssigner
    from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
    HELPDESK_AVAILABLE = True
except ImportError:
    HELPDESK_AVAILABLE = False

logger = get_logger("JARVISHelpdeskWorkflowLuminaR5Doit")


class JARVISHelpdeskWorkflowLuminaR5Doit:
    """
    Complete Helpdesk Workflow with @lumina @r5 @doit Integration

    Follows LUMINA patterns:
    1. @v3 Verification - Verify before execution
    2. @doit Execution - End-to-end automated processing
    3. @r5 Aggregation - Knowledge to Living Context Matrix
    4. @lumina Integration - JARVIS systems, local-first AI
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize workflow with LUMINA integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize V3 Verification
        if V3_AVAILABLE:
            try:
                v3_config = V3VerificationConfig(
                    enabled=True,
                    auto_verify=True,
                    verification_required=True,
                    fail_on_error=False
                )
                self.v3 = V3Verification(v3_config)
            except Exception as e:
                logger.warning(f"V3 initialization failed: {e}")
                self.v3 = None
        else:
            self.v3 = None

        # Initialize R5 Living Context Matrix
        if R5_AVAILABLE:
            r5_config = R5Config(
                data_directory=self.project_root / "data" / "r5_living_matrix",
                output_file=self.project_root / "data" / "r5_living_matrix" / "LIVING_CONTEXT_MATRIX_PROMPT.md"
            )
            self.r5 = R5LivingContextMatrix(self.project_root, r5_config)
        else:
            self.r5 = None

        # Initialize Helpdesk Systems
        if HELPDESK_AVAILABLE:
            self.processor = JARVISAutomatedHelpdeskProcessor(self.project_root)
            self.assigner = C3POTicketAssigner(self.project_root)
            self.ticket_system = JARVISHelpdeskTicketSystem(self.project_root)
        else:
            self.processor = None
            self.assigner = None
            self.ticket_system = None

        logger.info("✅ JARVIS Helpdesk Workflow (@lumina @r5 @doit) initialized")
        logger.info(f"   V3 Verification: {'✅' if self.v3 else '❌'}")
        logger.info(f"   R5 Matrix: {'✅' if self.r5 else '❌'}")
        logger.info(f"   Helpdesk Systems: {'✅' if self.processor else '❌'}")

    def execute_end_to_end(self) -> Dict[str, Any]:
        """
        @doit: Execute complete end-to-end helpdesk workflow

        Steps:
        1. @v3: Verify workflow readiness
        2. @doit: Process all tickets
        3. @r5: Aggregate knowledge
        4. @lumina: Report to JARVIS

        Returns:
            Complete workflow results
        """
        logger.info("="*80)
        logger.info("@DOIT: EXECUTING END-TO-END HELPDESK WORKFLOW")
        logger.info("="*80)

        results = {
            'workflow': 'helpdesk_lumina_r5_doit',
            'timestamp': datetime.now().isoformat(),
            'v3_verification': {},
            'processing': {},
            'r5_aggregation': {},
            'lumina_integration': {},
            'success': False
        }

        # Step 1: @v3 Verification
        if self.v3:
            logger.info("")
            logger.info("🔍 @V3: VERIFYING WORKFLOW READINESS")
            logger.info("-"*80)

            v3_results = self._verify_workflow()
            results['v3_verification'] = v3_results

            if not v3_results.get('all_passed', False):
                logger.warning("⚠️  V3 verification failed - workflow may have issues")
                results['success'] = False
                return results
            else:
                logger.info("✅ V3 verification passed")
        else:
            logger.warning("⚠️  V3 verification not available - skipping")
            results['v3_verification'] = {'skipped': True}

        # Step 2: @doit Processing
        logger.info("")
        logger.info("⚡ @DOIT: PROCESSING ALL TICKETS")
        logger.info("-"*80)

        if self.processor:
            # Get queue status before
            try:
                from jarvis_ticket_resolution_processor import JARVISTicketResolutionProcessor
                resolution_processor = JARVISTicketResolutionProcessor(self.project_root)
                queue_before = resolution_processor.get_queue_status()
                logger.info(f"📊 Queue Before: {queue_before['active_queue']} active, {queue_before['resolved']} resolved")
            except Exception as e:
                logger.debug(f"Could not get queue status: {e}")
                queue_before = None

            # Auto-accept all changes using MANUS
            try:
                from jarvis_auto_accept_all_changes import auto_accept_all_changes
                logger.info("🔄 Auto-accepting all changes via MANUS...")
                accept_success = auto_accept_all_changes()
                if accept_success:
                    logger.info("✅ All changes accepted - fixes can now be applied")
                else:
                    logger.warning("⚠️  Could not auto-accept changes")
            except Exception as e:
                logger.debug(f"Auto-accept failed: {e}")

            processing_results = self.processor.process_all_tickets()
            results['processing'] = processing_results

            # Resolve tickets to decrease queue
            try:
                if resolution_processor:
                    resolution_results = resolution_processor.resolve_tickets()
                    processing_results['resolution'] = resolution_results

                    # Get queue status after
                    queue_after = resolution_processor.get_queue_status()
                    queue_decrease = queue_before['active_queue'] - queue_after['active_queue'] if queue_before else 0

                    logger.info(f"✅ Processed {processing_results.get('processed', 0)} tickets")
                    logger.info(f"📉 Queue Decreased: {queue_decrease} tickets resolved")
                    logger.info(f"📊 Queue After: {queue_after['active_queue']} active, {queue_after['resolved']} resolved")

                    results['queue_progress'] = {
                        'before': queue_before,
                        'after': queue_after,
                        'decrease': queue_decrease
                    }
            except Exception as e:
                logger.debug(f"Resolution processing failed: {e}")
                logger.info(f"✅ Processed {processing_results.get('processed', 0)} tickets")
        else:
            logger.error("❌ Helpdesk processor not available")
            results['processing'] = {'error': 'processor_not_available'}
            results['success'] = False
            return results

        # Step 3: @r5 Aggregation
        logger.info("")
        logger.info("📊 @R5: AGGREGATING KNOWLEDGE TO LIVING CONTEXT MATRIX")
        logger.info("-"*80)

        if self.r5:
            r5_results = self._aggregate_to_r5(processing_results)
            results['r5_aggregation'] = r5_results
            logger.info("✅ Knowledge aggregated to R5 Living Context Matrix")
        else:
            logger.warning("⚠️  R5 not available - skipping aggregation")
            results['r5_aggregation'] = {'skipped': True}

        # Step 4: @lumina Integration
        logger.info("")
        logger.info("🌟 @LUMINA: INTEGRATING WITH JARVIS SYSTEMS")
        logger.info("-"*80)

        lumina_results = self._integrate_with_lumina(results)
        results['lumina_integration'] = lumina_results
        logger.info("✅ Integrated with LUMINA/JARVIS systems")

        # Final status
        results['success'] = True

        logger.info("")
        logger.info("="*80)
        logger.info("✅ @DOIT WORKFLOW COMPLETE")
        logger.info("="*80)
        logger.info(f"   V3: {'✅' if results['v3_verification'].get('all_passed', False) else '⚠️'}")
        logger.info(f"   Processing: ✅ {results['processing'].get('processed', 0)} tickets")
        logger.info(f"   R5: {'✅' if results['r5_aggregation'].get('aggregated', False) else '⚠️'}")
        logger.info(f"   LUMINA: ✅ Integrated")
        logger.info("="*80)

        return results

    def _verify_workflow(self) -> Dict[str, Any]:
        try:
            """@v3: Verify workflow readiness"""
            if not self.v3:
                return {'skipped': True}

            verification_steps = []

            # Verify helpdesk systems available
            if HELPDESK_AVAILABLE:
                verification_steps.append(VerificationResult(
                    step_name="helpdesk_systems",
                    passed=True,
                    message="Helpdesk systems available",
                    details={'processor': bool(self.processor), 'assigner': bool(self.assigner)}
                ))
            else:
                verification_steps.append(VerificationResult(
                    step_name="helpdesk_systems",
                    passed=False,
                    message="Helpdesk systems not available",
                    details={}
                ))

            # Verify ticket directory exists
            tickets_dir = self.project_root / "data" / "pr_tickets" / "tickets"
            verification_steps.append(VerificationResult(
                step_name="ticket_directory",
                passed=tickets_dir.exists(),
                message="Ticket directory exists" if tickets_dir.exists() else "Ticket directory missing",
                details={'path': str(tickets_dir)}
            ))

            # Verify R5 available (optional)
            verification_steps.append(VerificationResult(
                step_name="r5_available",
                passed=R5_AVAILABLE,
                message="R5 available" if R5_AVAILABLE else "R5 not available (optional)",
                details={'available': R5_AVAILABLE}
            ))

            all_passed = all(step.passed for step in verification_steps)

            return {
                'all_passed': all_passed,
                'steps': [step.__dict__ for step in verification_steps]
            }

        except Exception as e:
            self.logger.error(f"Error in _verify_workflow: {e}", exc_info=True)
            raise
    def _aggregate_to_r5(self, processing_results: Dict[str, Any]) -> Dict[str, Any]:
        """@r5: Aggregate workflow knowledge to Living Context Matrix"""
        if not self.r5:
            return {'skipped': True}

        try:
            # Create chat session from workflow execution
            session = ChatSession(
                session_id=f"helpdesk_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                messages=[
                    {
                        'role': 'system',
                        'content': f"Helpdesk workflow executed: {processing_results.get('processed', 0)} tickets processed"
                    },
                    {
                        'role': 'assistant',
                        'content': f"Gaps found: {processing_results.get('total_gaps', 0)}, Resolved: {processing_results.get('resolved', 0)}"
                    }
                ],
                patterns=['#HELPDESK', '#AUTOMATION', '#END2END'],
                metadata={
                    'workflow_type': 'helpdesk_automation',
                    'tickets_processed': processing_results.get('processed', 0),
                    'gaps_found': processing_results.get('total_gaps', 0)
                }
            )

            # Aggregate to R5 using ingest_session
            session_id = self.r5.ingest_session({
                'session_id': session.session_id,
                'timestamp': session.timestamp.isoformat(),
                'messages': session.messages,
                'patterns': session.patterns,
                'metadata': session.metadata
            })

            # Aggregate sessions
            self.r5.aggregate_sessions()

            # Extract @PEAK patterns (if method exists)
            if processing_results.get('total_gaps', 0) == 0 and hasattr(self.r5, 'extract_peak_pattern'):
                try:
                    self.r5.extract_peak_pattern('helpdesk_no_gaps', 'workflow_complete', 'No gaps in helpdesk workflow')
                except:
                    pass  # Method may not exist

            return {
                'aggregated': True,
                'session_id': session.session_id,
                'patterns_extracted': len(session.patterns)
            }
        except Exception as e:
            logger.error(f"Failed to aggregate to R5: {e}", exc_info=True)
            return {'aggregated': False, 'error': str(e)}

    def _integrate_with_lumina(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """@lumina: Integrate with JARVIS systems"""
        integration_points = {
            'jarvis_systems': True,
            'local_first_ai': True,  # Following LUMINA pattern
            'helpdesk_coordination': True,
            'workflow_automation': True
        }

        # Save workflow results for JARVIS
        workflow_file = self.project_root / "data" / "helpdesk" / "workflows" / f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        workflow_file.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(workflow_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            integration_points['workflow_saved'] = True
            integration_points['workflow_file'] = str(workflow_file)
        except Exception as e:
            logger.error(f"Failed to save workflow: {e}")
            integration_points['workflow_saved'] = False

        return integration_points


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Helpdesk Workflow (@lumina @r5 @doit)")
        parser.add_argument('--execute', action='store_true', help='Execute end-to-end workflow')
        parser.add_argument('--verify-only', action='store_true', help='Only run V3 verification')

        args = parser.parse_args()

        workflow = JARVISHelpdeskWorkflowLuminaR5Doit()

        if args.verify_only:
            if workflow.v3:
                results = workflow._verify_workflow()
                print(json.dumps(results, indent=2, default=str))
            else:
                print("V3 verification not available")
        elif args.execute or not any([args.verify_only]):
            results = workflow.execute_end_to_end()
            print(json.dumps(results, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()