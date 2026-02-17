"""
JARVIS Helpdesk Integration
Integrates the Droid Actor System at @helpdesk with JARVIS workflow execution.

This module provides:
- JARVIS workflow wrapper with droid actor verification
- @helpdesk service registration
- C-3PO → JARVIS escalation handler
- R5 knowledge ingestion from workflows
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from mcp_server.client import MCPClient
    MCP_AVAILABLE = True
except Exception:
    MCP_AVAILABLE = False

try:
    from droid_actor_system import (DroidActorSystem,
                                    verify_workflow_with_droid_actor)
    from v3_verification import V3Verification
    DROID_SYSTEM_AVAILABLE = True
except ImportError as e:
    DROID_SYSTEM_AVAILABLE = False
    logging.warning(f"Droid Actor System not available: {e}")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_SYSTEM_AVAILABLE = True
except ImportError:
    R5_SYSTEM_AVAILABLE = False
    logging.warning("R5 Living Context Matrix not available")

try:
    from jarvis_gitlens_automation import JARVISGitLensAutomation
    GITLENS_AUTOMATION_AVAILABLE = True
except ImportError:
    GITLENS_AUTOMATION_AVAILABLE = False
    logging.warning("GitLens automation not available")

try:
    from marvin_verification_system import MarvinVerificationSystem, verify_work_with_marvin
    MARVIN_VERIFICATION_AVAILABLE = True
except ImportError:
    MARVIN_VERIFICATION_AVAILABLE = False
    logging.warning("@MARVIN verification system not available")

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logging.debug("SYPHON system not available for workflow intelligence extraction")

try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False
    logging.debug("Azure Service Bus integration not available - using file-based fallback")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class JARVISHelpdeskIntegration:
    """
    Integration layer between JARVIS workflows and @helpdesk droid actor system.

    Provides:
    - Pre-workflow verification via droid actors
    - Post-workflow knowledge ingestion to R5
    - C-3PO → JARVIS escalation handling
    - Workflow execution with droid verification
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize JARVIS Helpdesk Integration.

        Args:
            project_root: Root directory of the project. If None, attempts to auto-detect.
        """
        if project_root is None:
            # Try to auto-detect project root
            current = Path(__file__).parent.parent
            if (current / "config" / "helpdesk").exists():
                project_root = current
            else:
                project_root = Path("D:/Dropbox/my_projects")

        self.project_root = Path(project_root)
        self.helpdesk_config_path = self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"

        # Initialize systems if available
        self.droid_system: Optional[DroidActorSystem] = None
        self.v3_system: Optional[Any] = None  # V3VerificationSystem - type may vary
        self.r5_system: Optional[R5LivingContextMatrix] = None

        # Initialize Service Bus client if available
        self.service_bus_client: Optional[AzureServiceBusClient] = None
        if SERVICE_BUS_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
                logging.info("Service Bus client initialized for JARVIS communication")
            except Exception as e:
                logging.warning(f"Service Bus not available, using file-based fallback: {e}")
                self.service_bus_client = None
        self.gitlens_automation: Optional[Any] = None  # JARVISGitLensAutomation - optional import
        self.marvin_verification: Optional[Any] = None  # MarvinVerificationSystem - optional import
        self.syphon_system: Optional[Any] = None  # SYPHONSystem - optional import

        if DROID_SYSTEM_AVAILABLE:
            try:
                self.droid_system = DroidActorSystem(project_root=self.project_root)
                # V3Verification is used via droid system
                self.v3_system = None  # Will be accessed via droid system if needed
            except Exception as e:
                logging.error(f"Failed to initialize droid system: {e}")

        if R5_SYSTEM_AVAILABLE:
            try:
                self.r5_system = R5LivingContextMatrix(project_root=self.project_root)
            except Exception as e:
                logging.error(f"Failed to initialize R5 system: {e}")

        if GITLENS_AUTOMATION_AVAILABLE:
            try:
                self.gitlens_automation = JARVISGitLensAutomation(repo_path=self.project_root, auto_commit=False)
                logging.info("GitLens automation initialized for JARVIS")
            except Exception as e:
                logging.warning(f"Failed to initialize GitLens automation: {e}")

        if MARVIN_VERIFICATION_AVAILABLE:
            try:
                self.marvin_verification = MarvinVerificationSystem()
                logging.info("@MARVIN @PEAK @AGGRESSIVE @ADVSERIAL verification system initialized")
            except Exception as e:
                logging.warning(f"Failed to initialize Marvin verification: {e}")

        # Initialize SYPHON for workflow intelligence extraction
        if SYPHON_AVAILABLE:
            try:
                config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.ENTERPRISE,
                    enable_self_healing=True,
                )
                self.syphon_system = SYPHONSystem(config)
                logging.info("✅ SYPHON system initialized for JARVIS workflow intelligence extraction (@COLAB @COOR @AGENTS @SUBAGENTS)")
            except Exception as e:
                logging.warning(f"SYPHON system initialization failed: {e}")

        # Load helpdesk configuration
        self.helpdesk_config = self._load_helpdesk_config()

    def _load_helpdesk_config(self) -> Dict[str, Any]:
        """Load @helpdesk structure configuration."""
        if self.helpdesk_config_path.exists():
            try:
                with open(self.helpdesk_config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.error(f"Failed to load helpdesk config: {e}")
                return {}
        return {}

    def verify_workflow_before_execution(
        self,
        workflow_data: Dict[str, Any],
        require_verification: bool = True,
        escalate_on_failure: bool = True,
        track_session: bool = False,
        session_id: Optional[str] = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify workflow using droid actor system before JARVIS execution.

        Enhanced with session tracking support.

        Args:
            workflow_data: Workflow data to verify
            require_verification: If True, workflow must pass verification to proceed
            escalate_on_failure: If True, escalate to JARVIS on verification failure
            track_session: If True, track verification in session
            session_id: Session ID for tracking

        Returns:
            Tuple of (verification_passed, verification_results)
        """
        # Check approval: #decisioning + #troubleshooting = approval for @workflows
        try:
            from src.cfservices.services.jarvis_core.workflow_approval import (
                has_approval_for_workflows, log_approval_check
            )
            approval = has_approval_for_workflows(self.project_root)
            log_approval_check("@workflows", approval)

            if not approval["approved"]:
                logging.warning(f"Workflow verification approval denied: {approval['reason']}")
                return False, {
                    "status": "approval_denied",
                    "approval_result": approval,
                    "error": approval["reason"]
                }
        except ImportError:
            logging.debug("Workflow approval module not available, proceeding without approval check")

        if not DROID_SYSTEM_AVAILABLE or self.droid_system is None:
            logging.warning("Droid system not available, skipping verification")
            return True, {"status": "skipped", "reason": "droid_system_unavailable"}

        try:
            # Perform droid actor verification
            passed, results = verify_workflow_with_droid_actor(
                workflow_data,
                project_root=self.project_root
            )

            if not passed and escalate_on_failure:
                # Check if escalation is needed
                if results.get("escalation_required", False) or results.get("escalated", False):
                    escalation_result = self._handle_escalation(workflow_data, results)
                    results["escalation"] = escalation_result

                    # Track escalation in session
                    if track_session and session_id:
                        try:
                            from scripts.python.jarvis_lock_issue_helpdesk_coordination import LockIssueHelpdeskCoordination
                            coordinator = LockIssueHelpdeskCoordination(project_root=self.project_root)
                            coordinator.add_message_to_session(
                                session_id,
                                "HELPDESK",
                                f"Escalation to JARVIS: {escalation_result.get('status', 'Unknown')}"
                            )
                        except Exception as e:
                            logging.debug(f"Session tracking failed: {e}")

                    # Check for JARVIS response if message ID is available
                    if escalation_result.get("jarvis_message_id"):
                        jarvis_response = self.check_jarvis_response(escalation_result["jarvis_message_id"])
                        if jarvis_response:
                            results["jarvis_response"] = jarvis_response
                            logging.info(f"JARVIS responded to escalation: {jarvis_response.get('status', 'unknown')}")

                            # Track JARVIS response in session
                            if track_session and session_id:
                                try:
                                    from scripts.python.jarvis_lock_issue_helpdesk_coordination import LockIssueHelpdeskCoordination
                                    coordinator = LockIssueHelpdeskCoordination(project_root=self.project_root)
                                    coordinator.add_message_to_session(
                                        session_id,
                                        "JARVIS",
                                        f"Response received: {jarvis_response.get('status', 'unknown')}"
                                    )
                                except Exception as e:
                                    logging.debug(f"Session tracking failed: {e}")

            if not passed and require_verification:
                logging.warning(f"Workflow verification failed: {results.get('verification_message', 'Unknown error')}")

                # Track verification failure in session
                if track_session and session_id:
                    try:
                        from scripts.python.jarvis_lock_issue_helpdesk_coordination import LockIssueHelpdeskCoordination
                        coordinator = LockIssueHelpdeskCoordination(project_root=self.project_root)
                        coordinator.add_message_to_session(
                            session_id,
                            "VERIFICATION",
                            f"Verification failed: {results.get('verification_message', 'Unknown error')}"
                        )
                    except Exception as e:
                        logging.debug(f"Session tracking failed: {e}")

            return passed, results

        except Exception as e:
            logging.error(f"Error during workflow verification: {e}")
            if require_verification:
                return False, {"status": "error", "error": str(e)}
            return True, {"status": "error_ignored", "error": str(e)}

    def execute_workflow_with_verification(
        self,
        workflow_data: Dict[str, Any],
        workflow_executor: callable,
        require_verification: bool = True,
        ingest_to_r5: bool = True,
        track_session: bool = True,
        enable_god_loop: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute JARVIS workflow with enhanced verification, session tracking, and GOD LOOP support.

        Enhanced features:
        - Workflow approval check (#decisioning + #troubleshooting)
        - Session history tracking (inception to archival)
        - SYPHON intelligence extraction
        - R5 knowledge ingestion
        - GOD LOOP integration for continuous repair
        - Error handling and retry logic

        Args:
            workflow_data: Workflow data
            workflow_executor: Function to execute the workflow
            require_verification: If True, workflow must pass verification
            ingest_to_r5: If True, ingest workflow results to R5
            track_session: If True, track workflow in agent chat session
            enable_god_loop: If True, enable GOD LOOP for continuous repair workflows

        Returns:
            Tuple of (success, execution_results)
        """
        workflow_name = workflow_data.get("workflow_name", "unknown")
        session_id = None

        # STEP 1: Start session tracking (if enabled)
        if track_session:
            try:
                from scripts.python.jarvis_lock_issue_helpdesk_coordination import LockIssueHelpdeskCoordination
                coordinator = LockIssueHelpdeskCoordination(project_root=self.project_root)
                session = coordinator.start_chat_session(
                    agents=["JARVIS", "WORKFLOW", "HELPDESK"]
                )
                session_id = session.session_id

                coordinator.add_message_to_session(
                    session_id,
                    "JARVIS",
                    f"Workflow '{workflow_name}' execution initiated",
                    "system"
                )

                coordinator.track_issue_in_session(
                    session_id,
                    f"Workflow: {workflow_name}"
                )

                logging.info(f"📋 Session tracking started: {session_id}")
            except Exception as e:
                logging.warning(f"Session tracking failed: {e}")
                track_session = False

        # STEP 2: Check approval: #decisioning + #troubleshooting = approval for @workflows
        try:
            from src.cfservices.services.jarvis_core.workflow_approval import (
                has_approval_for_workflows, log_approval_check
            )
            approval = has_approval_for_workflows(self.project_root)
            log_approval_check("@workflows", approval)

            if track_session and session_id:
                try:
                    coordinator.add_message_to_session(
                        session_id,
                        "WORKFLOW",
                        f"Approval check: {'✅ Approved' if approval['approved'] else '❌ Denied'} - {approval.get('reason', 'Unknown')}"
                    )
                except:
                    pass

            if not approval["approved"]:
                logging.warning(f"Workflow execution approval denied: {approval['reason']}")

                if track_session and session_id:
                    try:
                        coordinator.add_resolution_to_session(
                            session_id,
                            f"Workflow denied: {approval['reason']}"
                        )
                        coordinator.save_session(session_id)
                    except:
                        pass

                return False, {
                    "status": "approval_denied",
                    "approval_result": approval,
                    "error": approval["reason"],
                    "session_id": session_id
                }

            logging.info(f"Workflow execution approved: {approval['reason']}")
        except ImportError:
            logging.debug("Workflow approval module not available, proceeding without approval check")

        # STEP 3: Pre-execution verification
        verification_passed, verification_results = self.verify_workflow_before_execution(
            workflow_data,
            require_verification=require_verification,
            track_session=track_session,
            session_id=session_id
        )

        if track_session and session_id:
            try:
                coordinator.add_message_to_session(
                    session_id,
                    "WORKFLOW",
                    f"Verification: {'✅ Passed' if verification_passed else '❌ Failed'}"
                )
            except:
                pass

        if not verification_passed and require_verification:
            if track_session and session_id:
                try:
                    coordinator.add_resolution_to_session(
                        session_id,
                        "Workflow verification failed"
                    )
                    coordinator.save_session(session_id)
                except:
                    pass

            return False, {
                "status": "verification_failed",
                "verification": verification_results,
                "workflow_executed": False,
                "session_id": session_id
            }

        # STEP 4: Execute workflow (with GOD LOOP support if enabled)
        execution_result = None
        execution_success = False

        try:
            # Check if this is a lock repair workflow that should use GOD LOOP
            if enable_god_loop and "lock" in workflow_name.lower():
                logging.info("🔄 GOD LOOP enabled for lock repair workflow")
                try:
                    from scripts.python.jarvis_god_loop_lock_repair import JARVISGodLoop
                    import asyncio

                    god_loop = JARVISGodLoop(project_root=self.project_root)

                    if track_session and session_id:
                        try:
                            coordinator.add_message_to_session(
                                session_id,
                                "GOD_LOOP",
                                "GOD LOOP initiated for continuous repair"
                            )
                        except:
                            pass

                    # Run GOD LOOP (limited cycles for workflow integration)
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(god_loop.run_god_loop(
                        max_cycles=5,
                        cycle_interval=3.0,
                        stop_on_success=True
                    ))
                    loop.close()

                    execution_result = {
                        "success": True,
                        "method": "GOD_LOOP",
                        "cycles": god_loop.cycle_count,
                        "message": "GOD LOOP completed successfully"
                    }
                    execution_success = True
                except Exception as e:
                    logging.warning(f"GOD LOOP execution failed, falling back to standard: {e}")
                    execution_result = workflow_executor(workflow_data)
                    execution_success = execution_result.get("success", False)
            else:
                # Standard workflow execution
                execution_result = workflow_executor(workflow_data)
                execution_success = execution_result.get("success", False)

            if track_session and session_id:
                try:
                    coordinator.add_message_to_session(
                        session_id,
                        "WORKFLOW",
                        f"Execution: {'✅ Success' if execution_success else '❌ Failed'}"
                    )
                except:
                    pass

        except Exception as e:
            logging.error(f"Error during workflow execution: {e}", exc_info=True)
            execution_result = {
                "success": False,
                "error": str(e)
            }
            execution_success = False

            if track_session and session_id:
                try:
                    coordinator.add_message_to_session(
                        session_id,
                        "WORKFLOW",
                        f"Execution error: {str(e)}"
                    )
                except:
                    pass

        # STEP 5: Post-execution processing
        r5_ingested = False
        syphon_extracted = False

        if execution_success:
            # Ingest to R5
            if ingest_to_r5 and self.r5_system:
                try:
                    self._ingest_workflow_to_r5(workflow_data, execution_result)
                    r5_ingested = True

                    if track_session and session_id:
                        try:
                            coordinator.add_message_to_session(
                                session_id,
                                "R5",
                                "Knowledge ingested to R5"
                            )
                        except:
                            pass
                except Exception as e:
                    logging.warning(f"R5 ingestion failed: {e}")

            # Extract intelligence with SYPHON
            if self.syphon_system:
                try:
                    syphon_extracted = self._extract_workflow_intelligence_with_syphon(
                        workflow_data, execution_result, verification_results
                    )

                    if track_session and session_id:
                        try:
                            coordinator.add_message_to_session(
                                session_id,
                                "SYPHON",
                                f"Intelligence extracted: {syphon_extracted}"
                            )
                        except:
                            pass
                except Exception as e:
                    logging.warning(f"SYPHON extraction failed: {e}")

            # Add resolution to session
            if track_session and session_id:
                try:
                    coordinator.add_resolution_to_session(
                        session_id,
                        f"Workflow '{workflow_name}' completed successfully"
                    )
                except:
                    pass
        else:
            if track_session and session_id:
                try:
                    coordinator.add_resolution_to_session(
                        session_id,
                        f"Workflow '{workflow_name}' failed: {execution_result.get('error', 'Unknown')}"
                    )
                except:
                    pass

        # STEP 6: Save and optionally archive session
        if track_session and session_id:
            try:
                coordinator.save_session(session_id)
                # Don't archive immediately - keep active for monitoring
                # coordinator.archive_session(session_id)
            except Exception as e:
                logging.warning(f"Session save failed: {e}")

        return execution_success, {
            "status": "completed" if execution_success else "failed",
            "verification": verification_results,
            "execution": execution_result,
            "r5_ingested": r5_ingested,
            "syphon_extracted": syphon_extracted,
            "session_id": session_id,
            "workflow_name": workflow_name,
            "approval": approval if 'approval' in locals() else None
        }

    def _handle_escalation(
        self,
        workflow_data: Dict[str, Any],
        verification_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle C-3PO → JARVIS escalation.

        Args:
            workflow_data: Original workflow data
            verification_results: Results from droid verification

        Returns:
            Escalation result
        """
        escalation_data = {
            "escalated_at": datetime.now().isoformat(),
            "escalated_by": "C-3PO",
            "escalated_to": "JARVIS",
            "reason": verification_results.get("escalation_reason", "Protocol demands"),
            "workflow_data": workflow_data,
            "verification_results": verification_results
        }

        # Log escalation
        logging.info(f"C-3PO escalating to JARVIS: {escalation_data['reason']}")

        # Send escalation to JARVIS
        jarvis_message_id = self._send_escalation_to_jarvis(escalation_data)

        return {
            "status": "escalated",
            "escalation_data": escalation_data,
            "jarvis_notified": True,
            "jarvis_message_id": jarvis_message_id,
            "jarvis_intelligence_path": str(self.project_root / "data" / "jarvis_intelligence"),
            "response_check_path": str(self.project_root / "data" / "jarvis_intelligence" / f"{jarvis_message_id}_response.json")
        }

    def _send_escalation_to_jarvis(self, escalation_data: Dict[str, Any]) -> str:
        """
        Send escalation message to JARVIS via Azure Service Bus (preferred) or file-based (fallback).

        Args:
            escalation_data: Escalation data to send

        Returns:
            Message ID for tracking
        """
        import uuid

        # Create JARVIS escalation message payload
        message_payload = {
            "message_type": "escalation",
            "sender": "C-3PO",
            "recipient": "@jarvis",
            "priority": escalation_data.get("priority", "high"),
            "classification": "operational",
            "timestamp": datetime.now().isoformat(),
            "escalation": {
                "escalated_at": escalation_data["escalated_at"],
                "escalated_by": escalation_data["escalated_by"],
                "escalated_to": escalation_data["escalated_to"],
                "reason": escalation_data["reason"],
                "workflow_id": escalation_data["workflow_data"].get("workflow_id"),
                "workflow_name": escalation_data["workflow_data"].get("workflow_name"),
                "workflow_type": escalation_data["workflow_data"].get("workflow_type"),
                "complexity": escalation_data["verification_results"].get("workflow_context", {}).get("complexity", "unknown"),
                "domain": escalation_data["verification_results"].get("workflow_context", {}).get("domain", "unknown")
            },
            "workflow_data": escalation_data["workflow_data"],
            "verification_results": escalation_data["verification_results"],
            "status": "pending",
            "awaiting_response": True
        }

        message_id = str(uuid.uuid4())

        # PRIORITY 1: Azure Service Bus (preferred method)
        if self.service_bus_client:
            try:
                # Create Service Bus message
                sb_message = ServiceBusMessage(
                    message_id=message_id,
                    message_type=MessageType.ESCALATION,
                    timestamp=datetime.now(),
                    source="jarvis-helpdesk-integration",
                    destination="jarvis-escalation-handler",
                    payload={
                        "MessageType": "EscalationRequest",
                        "Priority": escalation_data.get("priority", "high"),
                        **message_payload
                    },
                    correlation_id=escalation_data["workflow_data"].get("workflow_id")
                )

                # Publish to Service Bus topic
                success = self.service_bus_client.publish_to_topic(
                    topic_name="jarvis.escalations",
                    message=sb_message
                )

                if success:
                    logging.info(f"Escalation sent to Service Bus: {message_id}")
                    # Also send to queue for guaranteed processing
                    self.service_bus_client.send_to_queue(
                        queue_name="jarvis-escalation-queue",
                        message=sb_message
                    )
                    # Mirror to filesystem for backward compatibility
                    self._write_escalation_file(message_id, message_payload)
                    return message_id
                else:
                    logging.warning("Service Bus publish failed, falling back to file-based")
            except Exception as e:
                logging.warning(f"Service Bus error, falling back to file-based: {e}")

        # PRIORITY 2: MCP if available
        if MCP_AVAILABLE:
            try:
                client = MCPClient()
                resp = client.post_message(message_payload, source="C-3PO")
                mid = resp.get("id")
                logging.info(f"Escalation posted to MCP: {mid}")
                # Mirror to filesystem for backward compatibility
                self._write_escalation_file(mid, message_payload)
                return mid
            except Exception as e:
                logging.error(f"Failed to post escalation to MCP: {e}")

        # PRIORITY 3: Fallback to file-based (backward compatibility)
        message_id = f"jarvis_escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{escalation_data['workflow_data'].get('workflow_id', 'unknown')}"
        self._write_escalation_file(message_id, message_payload)
        logging.info(f"Escalation written to filesystem (fallback): {message_id}")
        return message_id

    def _write_escalation_file(self, message_id: str, message_payload: Dict[str, Any]):
        """Write escalation file for backward compatibility"""
        jarvis_dir = self.project_root / "data" / "jarvis_intelligence"
        jarvis_dir.mkdir(parents=True, exist_ok=True)
        message_file = jarvis_dir / f"{message_id}.json"
        try:
            with open(message_file, 'w', encoding='utf-8') as f:
                json.dump({"message_id": message_id, **message_payload}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Failed to write escalation file: {e}")

    def check_jarvis_response(self, message_id: str, timeout_seconds: int = 300) -> Optional[Dict[str, Any]]:
        """
        Check for JARVIS response to escalation.

        Checks Service Bus first, then falls back to file-based.

        Args:
            message_id: JARVIS message ID to check
            timeout_seconds: Maximum time to wait for response (default 5 minutes)

        Returns:
            JARVIS response if available, None otherwise
        """
        # PRIORITY 1: Check Service Bus for response (if Service Bus was used)
        if self.service_bus_client:
            try:
                # Subscribe to jarvis.responses topic to check for responses
                # In production, this would use correlation_id to match request/response
                # For now, fall back to file-based check
                pass
            except Exception as e:
                logging.debug(f"Service Bus response check not implemented yet: {e}")

        # PRIORITY 2: Check file-based response (backward compatibility)
        jarvis_dir = self.project_root / "data" / "jarvis_intelligence"
        response_file = jarvis_dir / f"{message_id}_response.json"

        if response_file.exists():
            try:
                with open(response_file, 'r', encoding='utf-8') as f:
                    response = json.load(f)
                logging.info(f"JARVIS response found for {message_id}")
                return response
            except Exception as e:
                logging.error(f"Error reading JARVIS response: {e}")
                return None

        return None

    def _ingest_workflow_to_r5(
        self,
        workflow_data: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> bool:
        """
        Ingest workflow data and results into R5 Living Context Matrix.

        Args:
            workflow_data: Original workflow data
            execution_result: Workflow execution results

        Returns:
            True if ingestion successful
        """
        if not R5_SYSTEM_AVAILABLE or self.r5_system is None:
            return False

        try:
            session_data = {
                "session_id": workflow_data.get("workflow_id", f"workflow_{datetime.now().timestamp()}"),
                "workflow_name": workflow_data.get("workflow_name", "Unknown"),
                "workflow_type": workflow_data.get("workflow_type", "unknown"),
                "messages": [
                    {
                        "role": "system",
                        "content": f"Workflow: {workflow_data.get('workflow_name', 'Unknown')}"
                    },
                    {
                        "role": "assistant",
                        "content": json.dumps(execution_result, indent=2)
                    }
                ],
                "metadata": {
                    "source": "jarvis_workflow",
                    "verification_passed": True,
                    "execution_success": execution_result.get("success", False),
                    "timestamp": datetime.now().isoformat()
                }
            }

            self.r5_system.ingest_session(session_data)
            logging.info(f"Workflow ingested to R5: {session_data['session_id']}")
            return True

        except Exception as e:
            logging.error(f"Failed to ingest workflow to R5: {e}")
            return False

    def _extract_workflow_intelligence_with_syphon(
        self,
        workflow_data: Dict[str, Any],
        execution_result: Dict[str, Any],
        verification_results: Dict[str, Any]
    ) -> bool:
        """
        Extract intelligence from workflow using SYPHON (@COLAB @COOR @AGENTS @SUBAGENTS).

        Extracts:
        - Workflow execution patterns
        - Agent coordination (C-3PO, droids, subagents)
        - Collaboration patterns (@COLAB)
        - Coordination patterns (@COOR)
        - JARVIS CTO insights

        Args:
            workflow_data: Original workflow data
            execution_result: Workflow execution results
            verification_results: Verification results from droid system

        Returns:
            True if extraction successful
        """
        if not SYPHON_AVAILABLE or self.syphon_system is None:
            return False

        try:
            # Combine workflow data with execution and verification results
            combined_workflow_data = {
                **workflow_data,
                "execution_result": execution_result,
                "verification_results": verification_results,
                "timestamp": datetime.now().isoformat(),
                "extracted_by": "JARVISHelpdeskIntegration",
            }

            # Extract intelligence using SYPHON
            result = self.syphon_system.extract(
                source_type=DataSourceType.WORKFLOW,
                content=combined_workflow_data,
                metadata={
                    "source": "jarvis_workflow_execution",
                    "workflow_id": workflow_data.get("workflow_id", "unknown"),
                    "workflow_name": workflow_data.get("workflow_name", "unknown"),
                    "extraction_timestamp": datetime.now().isoformat(),
                }
            )

            if result.success and result.data:
                logging.info(f"✅ SYPHON extracted intelligence from workflow: {workflow_data.get('workflow_name', 'unknown')}")
                logging.debug(f"   Extracted {result.extracted_count if hasattr(result, 'extracted_count') else 0} items")
                return True
            else:
                logging.warning(f"SYPHON extraction failed: {result.error}")
                return False

        except Exception as e:
            logging.error(f"Error extracting workflow intelligence with SYPHON: {e}", exc_info=True)
            return False

    def register_helpdesk_service(self) -> Dict[str, Any]:
        try:
            """
            Register @helpdesk as a JARVIS core service.

            Returns:
                Registration result
            """
            registration = {
                "service_name": "@helpdesk",
                "service_type": "coordination",
                "coordinator": "C-3PO",
                "location": "@helpdesk",
                "droids": self.helpdesk_config.get("droids", []),
                "capabilities": [
                    "workflow_verification",
                    "droid_actor_routing",
                    "v3_verification",
                    "escalation_handling"
                ],
                "escalation_path": "C-3PO → JARVIS",
                "registered_at": datetime.now().isoformat(),
                "status": "active"
            }

            # Save registration
            registration_path = self.project_root / "config" / "jarvis_services" / "helpdesk_registration.json"
            registration_path.parent.mkdir(parents=True, exist_ok=True)

            with open(registration_path, 'w', encoding='utf-8') as f:
                json.dump(registration, f, indent=2)

            logging.info("@helpdesk registered as JARVIS service")
            return registration

        except Exception as e:
            logging.error(f"Error in register_helpdesk_service: {e}", exc_info=True)
            raise
    def handle_gitlens_follow_ups(self, auto_commit: bool = False, auto_push: bool = False, fullauto: bool = False) -> Dict[str, Any]:
        """
        Automatically handle all GitLens follow-ups.
        Part of JARVIS automated workflow system.

        Args:
            auto_commit: If True, automatically commit changes (default: False)
            auto_push: If True, automatically push after commit (default: False)
            fullauto: If True, enables full automation (auto-commit, auto-push, auto-pull, conflict resolution)
                      Overrides auto_commit and auto_push to True.

        Returns:
            Results dictionary with actions taken
        """
        if not GITLENS_AUTOMATION_AVAILABLE or self.gitlens_automation is None:
            logging.warning("GitLens automation not available")
            return {
                "status": "error",
                "message": "GitLens automation not available"
            }

        try:
            # Enable fullauto mode if requested (overrides other settings)
            if fullauto:
                self.gitlens_automation.fullauto = True
                self.gitlens_automation.auto_commit = True
                self.gitlens_automation.auto_push_enabled = True
                self.gitlens_automation.auto_pull_enabled = True
            else:
                # Enable auto-commit if requested
                if auto_commit:
                    self.gitlens_automation.auto_commit = True
                # Enable auto-push if requested
                if auto_push:
                    self.gitlens_automation.auto_push_enabled = True

            # Handle follow-ups (will use fullauto settings)
            results = self.gitlens_automation.handle_follow_ups()

            # Legacy: Auto-push if requested and commit was successful (for backward compatibility)
            if auto_push and not fullauto and any(
                action.get("action") == "auto_commit" and action.get("success")
                for action in results.get("actions_taken", [])
            ):
                push_success, push_msg = self.gitlens_automation.auto_push()
                results["actions_taken"].append({
                    "action": "auto_push",
                    "success": push_success,
                    "message": push_msg
                })

            # Ingest to R5 if available
            if self.r5_system and results.get("actions_taken"):
                try:
                    self.r5_system.ingest_session({
                        "session_id": f"gitlens_automation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "session_type": "gitlens_automation",
                        "timestamp": datetime.now().isoformat(),
                        "content": json.dumps(results, indent=2),
                        "metadata": {
                            "auto_commit": auto_commit,
                            "auto_push": auto_push
                        }
                    })
                    logging.info("GitLens automation results ingested to R5")
                except Exception as e:
                    logging.warning(f"Could not ingest GitLens results to R5: {e}")

            logging.info("✅ GitLens follow-ups handled automatically by JARVIS")
            return results

        except Exception as e:
            logging.error(f"Error handling GitLens follow-ups: {e}")
            return {
                "status": "error",
                "message": f"GitLens automation failed: {str(e)}",
                "error_details": str(e)
            }

    def verify_work_with_marvin(
        self,
        work_content: str,
        work_type: str = "general",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Use @MARVIN for @PEAK @AGGRESSIVE @ADVSERIAL work verification

        Args:
            work_content: The work to verify
            work_type: Type of work (code, documentation, etc.)
            context: Additional verification context

        Returns:
            Comprehensive verification results with Marvin's analysis
        """
        if not MARVIN_VERIFICATION_AVAILABLE or self.marvin_verification is None:
            logging.warning("@MARVIN verification system not available")
            return {
                "status": "error",
                "message": "@MARVIN verification system not available",
                "verified": False
            }

        try:
            logging.info(f"Delegating work verification to @MARVIN using @PEAK @AGGRESSIVE @ADVSERIAL protocol")

            # Perform Marvin's verification
            result = self.marvin_verification.verify_work(work_content, work_type, context)

            # Convert to dictionary for return
            result_dict = result.to_dict()

            # Add JARVIS coordination metadata
            result_dict.update({
                "coordinated_by": "JARVIS",
                "verification_protocol": "@PEAK_@AGGRESSIVE_@ADVSERIAL",
                "droid_agent": "@MARVIN",
                "escalation_available": True
            })

            # Ingest to R5 if available
            if self.r5_system and not result.verified:
                try:
                    verification_session = {
                        "session_id": f"marvin_verification_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "session_type": "work_verification",
                        "timestamp": datetime.now().isoformat(),
                        "content": f"Work Type: {work_type}\nVerified: {result.verified}\nConfidence: {result.confidence_score:.3f}\nIssues: {len(result.issues_found)}",
                        "metadata": result_dict
                    }
                    self.r5_system.ingest_session(verification_session)
                    logging.info("Verification results ingested to R5 for continuous improvement")
                except Exception as e:
                    logging.warning(f"Could not ingest verification to R5: {e}")

            logging.info(f"@MARVIN verification complete. Result: {'VERIFIED' if result.verified else 'REQUIRES_ATTENTION'}")
            return result_dict

        except Exception as e:
            logging.error(f"Error during @MARVIN verification: {e}")
            return {
                "status": "error",
                "message": f"@MARVIN verification failed: {str(e)}",
                "verified": False,
                "error_details": str(e)
            }

        except Exception as e:
            logging.error(f"Error handling GitLens follow-ups: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


def execute_jarvis_workflow_with_helpdesk(
    workflow_data: Dict[str, Any],
    workflow_executor: callable,
    project_root: Optional[Path] = None,
    require_verification: bool = True,
    ingest_to_r5: bool = True
) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to execute JARVIS workflow with @helpdesk integration.

    Args:
        workflow_data: Workflow data
        workflow_executor: Function to execute the workflow
        project_root: Project root directory
        require_verification: Require droid verification before execution
        ingest_to_r5: Ingest results to R5 after execution

    Returns:
        Tuple of (success, results)
    """
    integration = JARVISHelpdeskIntegration(project_root=project_root)
    return integration.execute_workflow_with_verification(
        workflow_data,
        workflow_executor,
        require_verification=require_verification,
        ingest_to_r5=ingest_to_r5
    )


if __name__ == "__main__":
    # Example usage
    print("JARVIS Helpdesk Integration")
    print("=" * 50)

    integration = JARVISHelpdeskIntegration()

    # Register helpdesk service
    registration = integration.register_helpdesk_service()
    print(f"\n@helpdesk registered: {registration['status']}")
    print(f"Coordinator: {registration['coordinator']}")
    print(f"Droids: {len(registration['droids'])}")

    # Example workflow verification
    example_workflow = {
        "workflow_id": "test_001",
        "workflow_name": "Test Workflow",
        "workflow_type": "technical",
        "steps": [{"step": 1, "action": "test"}]
    }

    passed, results = integration.verify_workflow_before_execution(example_workflow)
    print(f"\nWorkflow verification: {'PASSED' if passed else 'FAILED'}")
    if results.get("droid_assignment"):
        print(f"Droid: {results['droid_assignment'].get('droid_name', 'Unknown')}")

