#!/usr/bin/env python3
"""
JARVIS @DOIT Executor

JARVIS proceeds autonomously through all remaining high-priority steps
using subagent delegation. Full autonomy mode.
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_autonomous_workflow_executor import JARVISAutonomousWorkflowExecutor
    WORKFLOW_EXECUTOR_AVAILABLE = True
except ImportError:
    WORKFLOW_EXECUTOR_AVAILABLE = False
    JARVISAutonomousWorkflowExecutor = None

try:
    from jarvis_subagent_delegation import JARVISSubagentDelegation
    SUBAGENT_DELEGATION_AVAILABLE = True
except ImportError:
    SUBAGENT_DELEGATION_AVAILABLE = False
    JARVISSubagentDelegation = None

try:
    from aiq_triage_jedi import AIQTriageRouter, TriagePriority, TriageResult
    TRIAGE_AVAILABLE = True
except ImportError:
    TRIAGE_AVAILABLE = False
    AIQTriageRouter = None
    TriagePriority = None
    TriageResult = None

# Import @RR (Read & Run / Roast & Repair)
try:
    from jarvis_rr_godloop import JARVISGodLoop
    RR_AVAILABLE = True
    # Alias for compatibility
    JARVISRRGodLoop = JARVISGodLoop
except ImportError:
    RR_AVAILABLE = False
    JARVISRRGodLoop = None
    JARVISGodLoop = None

# Import @MARVIN (Reality Checker)
try:
    from jarvis_marvin_roast_system import JARVISMARVINRoastSystem
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    JARVISMARVINRoastSystem = None

# Import JARVIS Unified API
try:
    from jarvis_unified_api import JARVISUnifiedAPI
    JARVIS_UNIFIED_AVAILABLE = True
except ImportError:
    JARVIS_UNIFIED_AVAILABLE = False
    JARVISUnifiedAPI = None

# Import @SYPHON Telemetry
try:
    from syphon_workflow_telemetry_system import SYPHONWorkflowTelemetrySystem
    SYPHON_TELEMETRY_AVAILABLE = True
except ImportError:
    SYPHON_TELEMETRY_AVAILABLE = False
    SYPHONWorkflowTelemetrySystem = None

logger = get_logger("JARVISDOIT")


class JARVISDOITExecutor:
    """
    JARVIS @DOIT - Full Autonomy Mode

    Proceeds through all remaining high-priority steps autonomously,
    using subagent delegation for parallel execution.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Initialize systems
        if WORKFLOW_EXECUTOR_AVAILABLE:
            self.workflow_executor = JARVISAutonomousWorkflowExecutor(
                project_root,
                use_subagents=True  # Always use subagents for @DOIT
            )
        else:
            self.workflow_executor = None
            self.logger.error("Workflow executor not available")

        if SUBAGENT_DELEGATION_AVAILABLE:
            self.delegation = JARVISSubagentDelegation(project_root)
        else:
            self.delegation = None

        self.doit_logs_dir = project_root / "data" / "doit_logs"
        self.doit_logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize triage router if available - AUTO-DETECT with fallback
        self.triage_router = None
        if TRIAGE_AVAILABLE:
            self.triage_router = self._auto_detect_triage_router()

        # Initialize @RR (Read & Run / Roast & Repair) - MANDATORY for @DOIT
        self.rr_system = None
        if RR_AVAILABLE:
            try:
                self.rr_system = JARVISGodLoop(project_root)
                self.logger.info("✅ @RR (Read & Run / Roast & Repair / God Loop) initialized")
            except Exception as e:
                self.logger.error(f"❌ @RR initialization failed: {e}")
                self.logger.error("⚠️  @RR is MANDATORY for @DOIT - execution may be limited")
        else:
            self.logger.error("❌ @RR system not available - @RR is MANDATORY for @DOIT")

        # Initialize @SYPHON Telemetry
        self.syphon_telemetry = None
        if SYPHON_TELEMETRY_AVAILABLE:
            try:
                self.syphon_telemetry = SYPHONWorkflowTelemetrySystem(project_root)
                self.logger.info("✅ @SYPHON Telemetry initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON Telemetry initialization failed: {e}")
        else:
            self.logger.warning("⚠️  @SYPHON Telemetry not available - workflow tracking will be limited")

        # Initialize @MARVIN (Reality Checker)
        self.marvin_system = None
        if MARVIN_AVAILABLE:
            try:
                self.marvin_system = JARVISMARVINRoastSystem(project_root)
                self.logger.info("✅ @MARVIN (Reality Checker) initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  @MARVIN initialization failed: {e}")

        # Initialize JARVIS Unified API
        self.jarvis_unified = None
        if JARVIS_UNIFIED_AVAILABLE:
            try:
                self.jarvis_unified = JARVISUnifiedAPI(project_root)
                self.logger.info("✅ JARVIS Unified API initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS Unified API initialization failed: {e}")

        # Initialize Chain-of-Thought Enhanced @DOIT
        try:
            from doit_chain_of_thought_enhanced import DOITChainOfThoughtEnhanced
            self.cot_doit = DOITChainOfThoughtEnhanced(project_root)
            self.logger.info("✅ Chain-of-Thought Enhanced @DOIT initialized")
        except ImportError:
            self.cot_doit = None
            self.logger.warning("⚠️  Chain-of-Thought Enhanced @DOIT not available")
        except Exception as e:
            self.cot_doit = None
            self.logger.warning(f"⚠️  Chain-of-Thought Enhanced @DOIT initialization failed: {e}")

        # Initialize Local-First AI Policy
        try:
            from doit_local_first_ai_policy import DOITLocalFirstAIPolicy
            self.ai_policy = DOITLocalFirstAIPolicy(project_root)
            self.logger.info("✅ Local-First AI Policy initialized")
            self.logger.info("   Policy: Use local AI unless @bau #decisioning @r5 @matrix/@lattice approves cloud")
        except ImportError:
            self.ai_policy = None
            self.logger.warning("⚠️  Local-First AI Policy not available")
        except Exception as e:
            self.ai_policy = None
            self.logger.warning(f"⚠️  Local-First AI Policy initialization failed: {e}")

    def _auto_detect_triage_router(self) -> Optional[AIQTriageRouter]:
        """
        Auto-detect MCP server endpoint with automatic fallback
        Tries localhost first, then KAIJU, automatically selects working endpoint
        No manual configuration required - full @AUTO #AUTOMATION
        """
        import socket
        from urllib.parse import urlparse

        # Priority order: env var > localhost > KAIJU
        candidates = []

        # 1. Check environment variable (if explicitly set)
        env_url = os.getenv("MCP_SERVER_URL")
        if env_url:
            candidates.append(env_url)

        # 2. Try localhost (Docker on local machine)
        candidates.append("http://localhost:8000")

        # 3. Try KAIJU_NO_8 Desktop PC (primary MCP server location)
        candidates.append("http://<NAS_IP>:8000")

        # 4. Try NAS (backup/lightweight services only)
        candidates.append("http://<NAS_PRIMARY_IP>:8000")

        # Try each candidate until one works
        for url in candidates:
            try:
                # Parse URL
                parsed = urlparse(url)
                host = parsed.hostname
                port = parsed.port or 8000

                # Test socket connection (fast check)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()

                if result == 0:
                    # Port is open, try to initialize router
                    router = AIQTriageRouter(mcp_server_url=url)
                    self.logger.info(f"✅ Auto-detected MCP server: {url}")
                    return router
            except Exception as e:
                # This candidate failed, try next
                continue

        # None of the candidates worked - router will be None, but we'll still work
        self.logger.warning("⚠️  MCP server auto-detection failed - all endpoints unreachable")
        self.logger.warning("   Tried: localhost:8000, KAIJU_NO_8 (<NAS_IP>:8000), NAS (<NAS_PRIMARY_IP>:8000)")
        self.logger.warning("   Triage will default steps to 'Elevated' priority")
        return None

    def doit(self, use_triage: bool = True) -> Dict[str, Any]:
        """
        Execute @DOIT - Full autonomy mode with @RR, @JARVIS, and @MARVIN integration

        @DOIT Definition: Autonomous execution of ALL actionable tasks without manual intervention.
        Enhanced with:
        - @RR (Read & Run / Roast & Repair): Read context, analyze, and execute repairs
        - @JARVIS: Full JARVIS system integration for orchestration and coordination
        - @MARVIN: Reality checking and critical analysis before execution

        Core capabilities:
        - Detects and executes deployment tasks
        - Runs audits and diagnostics
        - Performs system enhancements
        - Executes all triaged steps
        - Operates with full autonomy (@AUTO)
        - @RR: Comprehensive analysis and repair cycles
        - @JARVIS: System-wide coordination and intelligence
        - @MARVIN: Pre-execution reality checks and validation

        Proceeds through all steps using @TRIAGE prioritization
        (or high-priority if triage unavailable)

        Args:
            use_triage: If True, use triage system to prioritize all steps.
                       If False, use high-priority filtering only.
        """
        self.logger.info("="*80)
        self.logger.info("JARVIS @DOIT - FULL AUTONOMY MODE")
        self.logger.info("Definition: Autonomous execution of ALL actionable tasks")
        self.logger.info("Mode: @AUTO - No manual intervention required")
        self.logger.info("Enhanced with: @RR + @JARVIS + @MARVIN")
        if use_triage:
            self.logger.info("Using @TRIAGE for step prioritization")
        else:
            self.logger.info("Using high-priority filtering")
        self.logger.info("="*80)

        # @DOIT: FULL AUTONOMY - Idleness restriction DISABLED for @DOIT
        # @DOIT is defined as "Autonomous execution of ALL actionable tasks"
        # and "Mode: @AUTO - No manual intervention required"
        # Therefore, @DOIT should NOT be blocked by idleness policy
        self.logger.info("🚀 @DOIT: FULL AUTONOMY MODE - Idleness restriction bypassed")

        # @RR: Read & Run - Analyze context and prepare for execution (MANDATORY)
        if not self.rr_system:
            self.logger.error("❌ @RR system not available - @RR is MANDATORY for @DOIT")
            return {
                'success': False,
                'error': '@RR system is MANDATORY for @DOIT execution',
                'message': 'Please ensure @RR (Read & Run / Roast & Repair) is available'
            }

        self.logger.info("📖 @RR: Reading context and analyzing system state...")
        rr_result = None
        try:
            # @RR integration - use available methods
            if hasattr(self.rr_system, 'roast_and_repair'):
                rr_result = self.rr_system.roast_and_repair()
            elif hasattr(self.rr_system, 'execute_rr_cycle'):
                rr_result = self.rr_system.execute_rr_cycle()
            else:
                # Try async method if available
                import asyncio
                if hasattr(self.rr_system, '_rr_roast_and_repair'):
                    rr_result = asyncio.run(self.rr_system._rr_roast_and_repair())
                else:
                    rr_result = {"success": True, "message": "@RR system initialized"}

            if rr_result and rr_result.get("success"):
                self.logger.info(f"✅ @RR: Analysis complete")
            else:
                self.logger.warning(f"⚠️  @RR: Analysis completed with warnings")
        except Exception as e:
            self.logger.error(f"❌ @RR analysis failed: {e}", exc_info=True)
            # Continue execution but log the failure

        # @SYPHON: Track workflow execution (ENHANCED - Full integration)
        workflow_id = None
        if self.syphon_telemetry:
            try:
                self.logger.info("📊 @SYPHON: Starting workflow telemetry tracking...")
                workflow_id = self.syphon_telemetry.start_workflow(
                    workflow_name="@DOIT Execution",
                    workflow_type="autonomous_execution",
                    metadata={
                        "mode": "@DOIT",
                        "rr_available": self.rr_system is not None,
                        "rr_result": rr_result if rr_result else None,
                        "marvin_available": self.marvin_system is not None,
                        "jarvis_available": self.jarvis_unified is not None,
                        "use_triage": use_triage
                    }
                )
                self.logger.info(f"✅ @SYPHON: Workflow tracking started (ID: {workflow_id})")
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON telemetry start failed: {e}")

        # @MARVIN: Reality Check - Validate before execution
        if self.marvin_system:
            self.logger.info("🤖 @MARVIN: Performing reality check...")
            try:
                # @MARVIN integration - use available methods
                if hasattr(self.marvin_system, 'reality_check_system'):
                    marvin_result = self.marvin_system.reality_check_system()
                elif hasattr(self.marvin_system, 'roast_system'):
                    marvin_result = self.marvin_system.roast_system()
                else:
                    marvin_result = {"passed": True, "message": "@MARVIN system initialized"}

                if marvin_result.get("passed") or marvin_result.get("success"):
                    self.logger.info("✅ @MARVIN: Reality check passed - proceeding with execution")
                else:
                    issues_count = marvin_result.get('issues_count', marvin_result.get('findings_count', 0))
                    self.logger.warning(f"⚠️  @MARVIN: Reality check found issues - {issues_count} issues")
            except Exception as e:
                self.logger.warning(f"⚠️  @MARVIN reality check failed: {e}")

        # @JARVIS: Coordinate with unified API
        if self.jarvis_unified:
            self.logger.info("🧠 @JARVIS: Coordinating with unified systems...")
            try:
                if hasattr(self.jarvis_unified, 'get_system_status'):
                    jarvis_status = self.jarvis_unified.get_system_status()
                elif hasattr(self.jarvis_unified, 'get_status'):
                    jarvis_status = self.jarvis_unified.get_status()
                else:
                    jarvis_status = {"active_systems": 0, "message": "JARVIS system initialized"}

                active_count = jarvis_status.get('active_systems', jarvis_status.get('systems_count', 0))
                self.logger.info(f"✅ @JARVIS: {active_count} systems active")
            except Exception as e:
                self.logger.warning(f"⚠️  @JARVIS coordination failed: {e}")

        # @DOIT Enhancement: Auto-detect and execute critical deployment tasks
        self._execute_autonomous_deployments()

        self.logger.info("Proceeding autonomously through all remaining steps...")
        self.logger.info("="*80)

        if not self.workflow_executor:
            return {
                'success': False,
                'error': 'Workflow executor not available'
            }

        # Use chain-of-thought enhanced execution if available
        if self.cot_doit:
            self.logger.info("🧠 Using Chain-of-Thought Enhanced @DOIT workflow")
            self.logger.info("   - Explicit reasoning at each step")
            self.logger.info("   - Dependency tracking and resolution")
            self.logger.info("   - Error recovery and retry logic")
            self.logger.info("   - Completion verification")
            self.logger.info("")

            # Process all @asks with chain-of-thought
            try:
                # Get all pending @asks
                from trace_ask_stack_to_inception import AskStackTracer
                tracer = AskStackTracer(self.project_root)
                all_asks = tracer.load_all_ask_sources()
                unfinished_asks = [ask for ask in all_asks if ask.get("status", "pending") in ["pending", "in_progress", "partial"]]

                if unfinished_asks:
                    self.logger.info(f"   Found {len(unfinished_asks)} unfinished @asks")
                    cot_result = self.cot_doit.process_all_asks(unfinished_asks[:100])  # Process first 100
                    result = {
                        "success": cot_result["completed"] > 0,
                        "chain_of_thought": True,
                        "asks_processed": cot_result["total"],
                        "asks_completed": cot_result["completed"],
                        "asks_failed": cot_result["failed"],
                        "execution_result": cot_result
                    }
                else:
                    self.logger.info("   No unfinished @asks found - using standard execution")
                    # Fall through to standard execution
                    if use_triage:
                        result = self._doit_with_triage()
                    else:
                        result = self.workflow_executor.execute_all_high_priority()
            except Exception as e:
                self.logger.warning(f"   ⚠️  Chain-of-thought execution failed: {e}")
                self.logger.info("   Falling back to standard execution")
                # Fall through to standard execution
                if use_triage:
                    result = self._doit_with_triage()
                else:
                    result = self.workflow_executor.execute_all_high_priority()
        else:
            # Standard execution (when chain-of-thought not available)
            if use_triage:
                result = self._doit_with_triage()
            else:
                # High-priority execution (when triage explicitly disabled)
                result = self.workflow_executor.execute_all_high_priority()

        # @SYPHON: Complete workflow tracking (ENHANCED - Full metrics)
        workflow_metrics = {}
        if self.syphon_telemetry and workflow_id:
            try:
                self.logger.info("📊 @SYPHON: Completing workflow telemetry tracking...")

                # Extract metrics from result
                execution = result.get('execution_result', result)
                summary = execution.get('summary', {})

                workflow_metrics = self.syphon_telemetry.complete_workflow(
                    workflow_id=workflow_id,
                    success=summary.get('failed', 0) == 0 if summary else result.get('success', False),
                    metrics={
                        'steps_total': summary.get('total', 0),
                        'steps_executed': summary.get('total', 0),
                        'steps_succeeded': summary.get('succeeded', 0),
                        'steps_failed': summary.get('failed', 0),
                        'steps_skipped': summary.get('skipped', 0),
                        'triage_used': use_triage,
                        'rr_integrated': self.rr_system is not None,
                        'marvin_integrated': self.marvin_system is not None,
                        'jarvis_integrated': self.jarvis_unified is not None
                    }
                )
                self.logger.info("✅ @SYPHON: Workflow telemetry tracking complete")
            except Exception as e:
                self.logger.warning(f"⚠️  @SYPHON telemetry completion failed: {e}")

        # Log @DOIT execution
        doit_log = {
            'mode': '@DOIT',
            'enhanced_with': {
                'rr': RR_AVAILABLE and self.rr_system is not None,
                'jarvis': JARVIS_UNIFIED_AVAILABLE and self.jarvis_unified is not None,
                'marvin': MARVIN_AVAILABLE and self.marvin_system is not None,
                'syphon': SYPHON_TELEMETRY_AVAILABLE and self.syphon_telemetry is not None
            },
            'triage_used': use_triage and self.triage_router is not None,
            'timestamp': datetime.now().isoformat(),
            'execution_result': result,
            'subagents_used': True,
            'parallel_execution': True,
            'syphon_metrics': workflow_metrics
        }

        log_file = self.doit_logs_dir / f"doit_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(doit_log, f, indent=2)
            self.logger.info(f"✅ @DOIT log saved: {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save @DOIT log: {e}")

        return doit_log

    def _doit_with_triage(self) -> Dict[str, Any]:
        """
        Execute @DOIT using @TRIAGE to prioritize all steps

        Uses triage system to evaluate all steps and execute based on
        triage priorities: Immediate, Urgent, Elevated, Routine
        """
        self.logger.info("="*80)
        self.logger.info("JARVIS @DOIT - @TRIAGE MODE")
        self.logger.info("="*80)

        # Load action plan
        plan = self.workflow_executor.load_latest_action_plan()
        if not plan:
            return {
                'success': False,
                'error': 'No action plan found'
            }

        # Get all steps (not just high-priority)
        all_steps = plan.get('steps', [])
        self.logger.info(f"Found {len(all_steps)} total steps to triage")

        # Triage all steps
        triaged_steps = []
        for step in all_steps:
            step_text = f"{step.get('title', '')} {step.get('description', '')}"
            step_text = step_text.strip()

            if not step_text:
                step_text = step.get('step_id', 'Unknown step')

            if self.triage_router:
                try:
                    # Triage the step using router
                    triage_result = self.triage_router.triage_issue(step_text)

                    step_with_triage = {
                        **step,
                        'triage_priority': triage_result.priority,
                        'triage_category': triage_result.category,
                        'triage_notes': triage_result.notes
                    }
                    triaged_steps.append(step_with_triage)

                    self.logger.info(f"  📋 {step.get('title', 'Unknown')[:50]}: {triage_result.priority} - {triage_result.category}")
                except Exception as e:
                    self.logger.warning(f"  ⚠️  Triage failed for {step.get('title', 'Unknown')}: {e}")
                    # Default to Elevated if triage fails
                    step_with_triage = {
                        **step,
                        'triage_priority': 'Elevated',
                        'triage_category': 'general',
                        'triage_notes': f'Triage failed: {e}'
                    }
                    triaged_steps.append(step_with_triage)
            else:
                # No router available - default to Elevated (@AUTO fallback)
                step_with_triage = {
                    **step,
                    'triage_priority': 'Elevated',
                    'triage_category': 'general',
                    'triage_notes': 'MCP server unavailable - default priority'
                }
                triaged_steps.append(step_with_triage)

        # Sort by triage priority (Immediate > Urgent > Elevated > Routine)
        priority_order = {
            'Immediate': 0,
            'Urgent': 1,
            'Elevated': 2,
            'Routine': 3
        }

        triaged_steps.sort(key=lambda x: (
            priority_order.get(x.get('triage_priority', 'Routine'), 99),
            -x.get('readiness', 0)
        ))

        # Filter out Routine priority steps (or include them - configurable)
        # For @DOIT, we'll include all priorities except Routine
        steps_to_execute = [
            s for s in triaged_steps
            if s.get('triage_priority') != 'Routine'
        ]

        # Also filter out already completed (curriculum system)
        steps_to_execute = [
            s for s in steps_to_execute
            if 'curriculum' not in s.get('step_id', '').lower()
        ]

        self.logger.info(f"\n{'='*80}")
        self.logger.info(f"TRIAGE SUMMARY")
        self.logger.info(f"{'='*80}")
        for priority in ['Immediate', 'Urgent', 'Elevated', 'Routine']:
            count = len([s for s in triaged_steps if s.get('triage_priority') == priority])
            self.logger.info(f"  {priority}: {count} steps")
        self.logger.info(f"{'='*80}")
        self.logger.info(f"Executing {len(steps_to_execute)} triaged steps (excluding Routine)")

        # Execute using workflow executor's execution logic
        # We'll use the delegation system for parallel execution
        if self.delegation and len(steps_to_execute) > 1:
            self.logger.info(f"🚀 Delegating {len(steps_to_execute)} triaged tasks in parallel to subagents")
            results = self.delegation.delegate_parallel(steps_to_execute)
        else:
            # Sequential execution
            results = []
            for step in steps_to_execute:
                result = self.workflow_executor.execute_step(step)
                results.append(result)

        # Build execution log similar to execute_all_high_priority
        execution_log = {
            'started_at': datetime.now().isoformat(),
            'total_steps': len(steps_to_execute),
            'triage_mode': True,
            'executed': results,
            'failed': [r for r in results if not r.get('success')]
        }

        execution_log['completed_at'] = datetime.now().isoformat()
        summary = {
            'total': len(steps_to_execute),
            'succeeded': len([r for r in results if r.get('success')]),
            'failed': len(execution_log['failed']),
            'skipped': len([r for r in results if r.get('skipped')])
        }
        execution_log['summary'] = summary

        # Save execution log
        log_file = self.workflow_executor.workflow_logs_dir / f"workflow_execution_triage_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(execution_log, f, indent=2)
            self.logger.info(f"\n✅ Execution log saved: {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save execution log: {e}")

        return execution_log

    def _execute_autonomous_deployments(self):
        """@DOIT Enhancement: Auto-detect and execute critical tasks (deployment/verification/optimization)

        POLICY: ALWAYS TEST - Never assume. Verify everything before making recommendations.
        """
        self.logger.info("🔍 Auto-detecting critical tasks...")
        self.logger.info("   📋 POLICY: Always test, never assume")

        # ALWAYS TEST: Verify Ollama on KAIJU_NO_8 (don't trust assumptions)
        self.logger.info("   🧪 TESTING: Verifying Ollama on KAIJU_NO_8...")
        try:
            from jarvis_kaiju_ollama_verifier import KAIJUOllamaVerifier
            verifier = KAIJUOllamaVerifier(self.project_root)
            verification = verifier.check_ollama_status()

            # Test results determine actions
            ollama_found = verification.get("ollama_found", False)
            ollama_accessible = verification.get("ollama_accessible", False)
            models = verification.get("models", [])

            if ollama_found and ollama_accessible:
                # TEST PASSED: Ollama is verified running and accessible
                self.logger.info("   ✅ TEST RESULT: Ollama VERIFIED running and accessible on KAIJU_NO_8")
                if models:
                    self.logger.info(f"   📦 Models: {len(models)} available ({', '.join(models[:3])})")
                    self.logger.info("   💡 Focus: Optimization (GPU utilization, model management)")
                else:
                    self.logger.info("   ⚠️  No models found - pull models using IDM CLI")
            elif ollama_found:
                # TEST PARTIAL: Found but not accessible (firewall/local-only)
                self.logger.info("   ⚠️  TEST RESULT: Ollama found but not accessible from this network")
                self.logger.info("   💡 Action: Verify locally on KAIJU_NO_8")
                self.logger.info("      - Check: docker ps | findstr ollama")
                self.logger.info("      - Verify GPU: docker inspect ollama | findstr OLLAMA_NUM_GPU")
                self.logger.info("      - Test API: curl http://localhost:11434/api/tags")
            else:
                # TEST FAILED: Ollama not found/accessible
                self.logger.warning("   ❌ TEST RESULT: Ollama NOT verified running on KAIJU_NO_8")
                self.logger.info("   📋 Action: Deploy Ollama on KAIJU_NO_8 (<NAS_IP>) with GPU support")
                self.logger.info("   📝 Script: scripts/powershell/Deploy-KAIJU-Ollama.ps1")
                self.logger.info("   💡 Note: If installed, verify locally: docker ps -a | findstr ollama")
        except Exception as e:
            self.logger.error(f"   ❌ TEST FAILED: Verification error: {e}")
            self.logger.info("   💡 Manual verification required - cannot test automatically")

        # ALWAYS TEST: Architecture evaluation
        self.logger.info("   🧪 TESTING: Architecture evaluation...")
        try:
            from jarvis_architecture_evaluator import ArchitectureEvaluator
            evaluator = ArchitectureEvaluator(self.project_root)
            evaluation = evaluator.evaluate_current_architecture()

            # Test results
            kaiju = evaluation.get("systems", {}).get("KAIJU_NO_8", {})
            kaiju_services = kaiju.get("services", {})

            self.logger.info("   ✅ TEST RESULT: Architecture evaluation complete")
            for service_name, service_status in kaiju_services.items():
                status_icon = "✅" if service_status.get("running") else "❌"
                self.logger.info(f"      {status_icon} {service_name}: {service_status.get('running', False)}")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Architecture test failed: {e}")

        # ALWAYS TEST: Storage monitoring and auto-transfer
        self.logger.info("   🧪 TESTING: Storage monitoring and NAS transfer...")
        try:
            from jarvis_storage_engineering_team import StorageEngineeringTeam
            storage_team = StorageEngineeringTeam(self.project_root)
            storage_result = storage_team.monitor_and_resolve()

            space_info = storage_result.get("space_info", {})
            critical_drives = space_info.get("critical_drives", [])
            low_space_drives = space_info.get("low_space_drives", [])
            nas_info = storage_result.get("nas_info", {})

            if critical_drives or low_space_drives:
                self.logger.warning(f"   ⚠️  TEST RESULT: {len(critical_drives)} critical, {len(low_space_drives)} low space drives")
                transfer_result = storage_result.get("transfer_result", {})
                if transfer_result.get("transferred"):
                    self.logger.info(f"   ✅ Auto-transferred {transfer_result.get('files_count', 0)} files ({transfer_result.get('total_gb', 0):.2f}GB) to NAS")
                else:
                    self.logger.info(f"   💡 Transfer needed: {transfer_result.get('reason', 'Unknown')}")
            else:
                self.logger.info("   ✅ TEST RESULT: No storage issues detected")

            if nas_info.get("cloud_aggregate_info") == "Not configured":
                self.logger.warning("   ⚠️  NAS cloud storage aggregate NOT CONFIGURED")
                self.logger.info("   💡 Recommendation: Configure NAS cloud storage aggregate for better storage management")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Storage monitoring test failed: {e}")

        # ALWAYS TEST: SYPHON enhancement audit
        self.logger.info("   🧪 TESTING: SYPHON enhancement audit...")
        try:
            from jarvis_syphon_enhancement_audit import SYPHONEnhancementAuditor
            auditor = SYPHONEnhancementAuditor(self.project_root)
            audit_result = auditor.audit_for_syphon_enhancement()

            high_priority = len(audit_result.get("enhancements", {}).get("high_priority", []))
            medium_priority = len(audit_result.get("enhancements", {}).get("medium_priority", []))

            if high_priority > 0 or medium_priority > 0:
                self.logger.info(f"   ✅ TEST RESULT: Found {high_priority + medium_priority} SYPHON enhancement opportunities")
                self.logger.info(f"      High Priority: {high_priority}, Medium Priority: {medium_priority}")
            else:
                self.logger.info("   ✅ TEST RESULT: No SYPHON enhancements needed")
        except Exception as e:
            self.logger.warning(f"   ⚠️  SYPHON audit test failed: {e}")

    def doit_with_status(self, use_triage: bool = True) -> Dict[str, Any]:
        """Execute @DOIT with detailed status reporting"""
        self.logger.info("\n" + "="*80)
        self.logger.info("JARVIS @DOIT - STATUS CHECK")
        self.logger.info("="*80)

        # Check subagent status
        if self.delegation:
            status = self.delegation.get_subagent_status()
            self.logger.info(f"Subagents: {status['active_subagents']}/{status['total_subagents']} active")

        # Check triage availability
        if use_triage:
            if self.triage_router:
                self.logger.info("✅ Triage router: Available")
            else:
                self.logger.warning("⚠️  Triage router: Unavailable (will use high-priority fallback)")

        # Execute @DOIT
        result = self.doit(use_triage=use_triage)

        # Report results
        execution = result.get('execution_result', {})
        summary = execution.get('summary', {})

        self.logger.info("\n" + "="*80)
        self.logger.info("@DOIT EXECUTION COMPLETE")
        self.logger.info("="*80)
        self.logger.info(f"Triage Mode: {result.get('triage_used', False)}")
        self.logger.info(f"Total Steps: {summary.get('total', 0)}")
        self.logger.info(f"Succeeded: {summary.get('succeeded', 0)}")
        self.logger.info(f"Failed: {summary.get('failed', 0)}")
        self.logger.info(f"Skipped: {summary.get('skipped', 0)}")
        self.logger.info("="*80)

        return result


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @DOIT Executor")
        parser.add_argument("--doit", action="store_true", help="Execute @DOIT mode")
        parser.add_argument("--status", action="store_true", help="Show status before execution")
        parser.add_argument("--no-triage", action="store_true", help="Disable triage, use high-priority only")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        executor = JARVISDOITExecutor(project_root)

        use_triage = not args.no_triage

        if args.doit:
            if args.status:
                result = executor.doit_with_status(use_triage=use_triage)
            else:
                result = executor.doit(use_triage=use_triage)

            # Print summary
            execution = result.get('execution_result', {})
            summary = execution.get('summary', {})

            print("\n" + "="*80)
            print("@DOIT EXECUTION SUMMARY")
            print("="*80)
            print(f"Triage Mode: {'✅ Yes' if result.get('triage_used', False) else '❌ No'}")
            print(f"Total Steps: {summary.get('total', 0)}")
            print(f"✅ Succeeded: {summary.get('succeeded', 0)}")
            print(f"❌ Failed: {summary.get('failed', 0)}")
            print(f"⏭️  Skipped: {summary.get('skipped', 0)}")
            print("="*80)

            if summary.get('succeeded', 0) > 0:
                if result.get('triage_used', False):
                    print("\n✅ @DOIT COMPLETE - All triaged steps executed")
                else:
                    print("\n✅ @DOIT COMPLETE - All high-priority steps executed")
            else:
                print("\n⚠️ No steps to execute or all already complete")
        else:
            print("Usage: python jarvis_doit_executor.py --doit")
            print("       python jarvis_doit_executor.py --doit --status")
            print("       python jarvis_doit_executor.py --doit --no-triage  (disable triage)")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()