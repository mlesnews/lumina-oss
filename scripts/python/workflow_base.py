#!/usr/bin/env python3
"""
Workflow Base Class - Always Tracks Steps

All workflows inherit from this base class which MANDATORY step tracking.
Prevents hallucination by requiring explicit step completion verification.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Iterator
from datetime import datetime
from pathlib import Path
import json

# Parallel processing support
try:
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
    PARALLEL_AVAILABLE = True
except ImportError:
    PARALLEL_AVAILABLE = False
    ThreadPoolExecutor = None
    ProcessPoolExecutor = None
    as_completed = None

try:
    from workflow_step_tracker import WorkflowStepTracker, WorkflowStep
    STEP_TRACKING_AVAILABLE = True
except ImportError:
    STEP_TRACKING_AVAILABLE = False
    WorkflowStepTracker = None
    WorkflowStep = None

try:
    from workflow_memory_persistence import WorkflowMemoryPersistence, MemoryTier
    MEMORY_PERSISTENCE_AVAILABLE = True
except ImportError:
    MEMORY_PERSISTENCE_AVAILABLE = False
    WorkflowMemoryPersistence = None
    MemoryTier = None

try:
    from workflow_completion_verifier import WorkflowCompletionVerifier, verify_workflow_completion
    COMPLETION_VERIFIER_AVAILABLE = True
except ImportError:
    COMPLETION_VERIFIER_AVAILABLE = False
    WorkflowCompletionVerifier = None
    verify_workflow_completion = None

try:
    from v3_verification import V3Verification, V3VerificationConfig
    V3_VERIFICATION_AVAILABLE = True
except ImportError:
    V3_VERIFICATION_AVAILABLE = False
    V3Verification = None
    V3VerificationConfig = None

try:
    from workflow_scope_mode_orchestrator import WorkflowScopeModeOrchestrator
    SCOPE_MODE_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    SCOPE_MODE_ORCHESTRATOR_AVAILABLE = False
    WorkflowScopeModeOrchestrator = None

try:
    from workflow_auto_review_fix import WorkflowAutoReviewFix
    AUTO_REVIEW_FIX_AVAILABLE = True
except ImportError:
    AUTO_REVIEW_FIX_AVAILABLE = False
    WorkflowAutoReviewFix = None

try:
    from wopr_workflow_pattern_mapper import WOPRWorkflowPatternMapper
    WOPR_PATTERN_MAPPER_AVAILABLE = True
except ImportError:
    WOPR_PATTERN_MAPPER_AVAILABLE = False
    WOPRWorkflowPatternMapper = None

try:
    from master_session_manager import MasterSessionManager
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False
    MasterSessionManager = None

try:
    from llm_confidence_scorer import LLMConfidenceScorer, ConfidenceLevel
    CONFIDENCE_SCORER_AVAILABLE = True
except ImportError:
    CONFIDENCE_SCORER_AVAILABLE = False
    LLMConfidenceScorer = None
    ConfidenceLevel = None

try:
    from workflow_outcome_tracker import get_outcome_tracker, WorkflowOutcomeTracker
    OUTCOME_TRACKING_AVAILABLE = True
except ImportError:
    OUTCOME_TRACKING_AVAILABLE = False
    get_outcome_tracker = None
    WorkflowOutcomeTracker = None


class WorkflowBase(ABC):
    """
    Base class for ALL workflows

    MANDATORY: Step tracking always enabled - no exceptions
    """

    def __init__(self, workflow_name: str, total_steps: int, execution_id: Optional[str] = None,
                 verification_template_path: Optional[str] = None):
        """
        Initialize workflow with mandatory step tracking

        Args:
            workflow_name: Name of the workflow
            total_steps: Total number of steps in this workflow
            execution_id: Optional execution ID (generated if not provided)
            verification_template_path: Optional path to verification template JSON
        """
        self.workflow_name = workflow_name
        self.total_steps = total_steps
        self.execution_id = execution_id or f"{workflow_name}_{int(datetime.now().timestamp())}"
        self.verification_template_path = verification_template_path

        # ALWAYS initialize step tracker - no exceptions
        self.step_tracker = None
        if STEP_TRACKING_AVAILABLE:
            # Create a custom step tracker for workflows with different step counts
            self.step_tracker = self._create_step_tracker()

        self.logger = self._setup_logging()

        # Initialize memory persistence
        self.memory_persistence = None
        if MEMORY_PERSISTENCE_AVAILABLE and WorkflowMemoryPersistence:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.memory_persistence = WorkflowMemoryPersistence(project_root=project_root)
            except Exception as e:
                self.logger.warning(f"Memory persistence not available: {e}")

        # Initialize Workflow Scope & Mode Orchestrator
        self.scope_mode_orchestrator = None
        if SCOPE_MODE_ORCHESTRATOR_AVAILABLE and WorkflowScopeModeOrchestrator:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.scope_mode_orchestrator = WorkflowScopeModeOrchestrator(project_root)
                self.logger.info("✅ Workflow Scope & Mode Orchestrator initialized")
            except Exception as e:
                self.logger.warning(f"Scope/Mode orchestrator not available: {e}")

        # Initialize outcome tracker for Lumina Data Mining Feedback Loop
        self.outcome_tracker = None
        if OUTCOME_TRACKING_AVAILABLE and get_outcome_tracker:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.outcome_tracker = get_outcome_tracker(project_root)
                self.logger.info("✅ Outcome tracker initialized for Lumina feedback loop")
            except Exception as e:
                self.logger.warning(f"Outcome tracker not available: {e}")

        # Initialize v3_verification (runs BEFORE workflow execution)
        self.v3_verifier = None
        if V3_VERIFICATION_AVAILABLE and V3Verification:
            try:
                project_root = Path(__file__).parent.parent.parent
                v3_config = V3VerificationConfig(
                    auto_verify=True,
                    verification_required=False,  # Don't fail workflow if v3 fails
                    log_verification=True
                )
                self.v3_verifier = V3Verification(config=v3_config)
            except Exception as e:
                self.logger.warning(f"v3_verification not available: {e}")

        # Initialize completion verifier (runs AFTER workflow execution)
        self.completion_verifier = None
        self.expected_deliverables = []  # Set by subclass or workflow

        # Auto-load verification template if available
        template_data = self._load_verification_template()
        if template_data:
            # Auto-populate expected_deliverables from template
            if "deliverables" in template_data:
                self.expected_deliverables = template_data["deliverables"]
                self.logger.info(f"✅ Loaded {len(self.expected_deliverables)} expected deliverables from template")

        if COMPLETION_VERIFIER_AVAILABLE and WorkflowCompletionVerifier:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.completion_verifier = WorkflowCompletionVerifier(project_root=project_root)
            except Exception as e:
                self.logger.warning(f"Completion verifier not available: {e}")

        # Initialize Auto Review & Fix component
        self.auto_review_fix = None
        if AUTO_REVIEW_FIX_AVAILABLE and WorkflowAutoReviewFix:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.auto_review_fix = WorkflowAutoReviewFix(
                    project_root=project_root,
                    workflow_id=self.execution_id
                )
                self.logger.info("✅ Auto Review & Fix component initialized")
            except Exception as e:
                self.logger.warning(f"Auto Review & Fix not available: {e}")

        # Initialize WOPR Workflow Pattern Mapper (CORE @WOPR)
        self.wopr_pattern_mapper = None
        if WOPR_PATTERN_MAPPER_AVAILABLE and WOPRWorkflowPatternMapper:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.wopr_pattern_mapper = WOPRWorkflowPatternMapper(project_root=project_root)
                self.logger.info("✅ WOPR Pattern Mapper initialized (CORE @WOPR)")
            except Exception as e:
                self.logger.warning(f"WOPR Pattern Mapper not available: {e}")

        # Initialize Master Session Manager (JARVIS Lead Session)
        self.master_session = None
        if MASTER_SESSION_AVAILABLE and MasterSessionManager:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.master_session = MasterSessionManager(project_root=project_root)
                # Ensure master session exists
                self.master_session.create_or_set_master_session()
                self.logger.info("✅ Master Session Manager initialized (JARVIS Lead Session)")
            except Exception as e:
                self.logger.warning(f"Master Session Manager not available: {e}")

        # Initialize Confidence Scorer (Anti-Hallucination System)
        self.confidence_scorer = None
        try:
            from llm_confidence_scorer import LLMConfidenceScorer
            project_root = Path(__file__).parent.parent.parent
            self.confidence_scorer = LLMConfidenceScorer(project_root=project_root)
            self.logger.info("🧠 Confidence Scorer initialized (Anti-Hallucination System)")
        except ImportError:
            self.logger.debug("Confidence Scorer not available - hallucinations may occur")
        except Exception as e:
            self.logger.warning(f"Confidence Scorer initialization failed: {e}")

        # Track that workflow started
        self._mark_step(1, "Issue Received", "completed")

    def _load_verification_template(self) -> Optional[Dict[str, Any]]:
        """Auto-load verification template if available"""
        project_root = Path(__file__).parent.parent.parent

        # Try custom template path first
        if self.verification_template_path:
            template_path = Path(self.verification_template_path)
            if not template_path.is_absolute():
                template_path = project_root / template_path
        else:
            # Try default location: templates/workflow_verification_template.json
            template_path = project_root / "templates" / "workflow_verification_template.json"

        if template_path.exists():
            try:
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    self.logger.debug(f"Loaded verification template from {template_path}")
                    return template_data
            except Exception as e:
                self.logger.warning(f"Failed to load verification template from {template_path}: {e}")

        return None

    def _create_step_tracker(self):
        """Create step tracker - override in subclasses if needed"""
        # For now, use a simple dict-based tracker for custom step counts
        return {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow_name,
            "total_steps": self.total_steps,
            "steps": {},
            "current_step": 0,
            "started_at": datetime.now().isoformat()
        }

    def _setup_logging(self):
        """Setup logging - override in subclasses"""
        import logging
        logger = logging.getLogger(self.workflow_name)
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                f'%(asctime)s - 📊 {self.workflow_name} - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def _mark_step(self, step_number: int, step_name: str, status: str, details: Optional[Dict[str, Any]] = None):
        """
        Mark a step as completed/failed/in_progress

        MANDATORY: All workflows must call this for every step
        """
        if self.step_tracker:
            if isinstance(self.step_tracker, dict):
                # Simple dict-based tracker
                self.step_tracker["steps"][step_number] = {
                    "step_number": step_number,
                    "step_name": step_name,
                    "status": status,
                    "timestamp": datetime.now().isoformat(),
                    "details": details or {}
                }
                if status == "completed":
                    self.step_tracker["current_step"] = max(self.step_tracker["current_step"], step_number)
            else:
                # WorkflowStepTracker instance
                # Map step number to WorkflowStep enum if possible
                if hasattr(WorkflowStep, f"STEP_{step_number}"):
                    step_enum = getattr(WorkflowStep, f"STEP_{step_number}")
                    self.step_tracker.mark_step(step_enum, status, details)

        self.logger.info(f"   Step {step_number}/{self.total_steps}: {step_name} - {status}")

    def get_progress(self) -> Dict[str, Any]:
        """Get current progress"""
        if self.step_tracker:
            if isinstance(self.step_tracker, dict):
                completed = [s for s, data in self.step_tracker["steps"].items() 
                            if data.get("status") == "completed"]
                missing = [s for s in range(1, self.total_steps + 1) if s not in completed]

                return {
                    "execution_id": self.execution_id,
                    "workflow_name": self.workflow_name,
                    "current_step": self.step_tracker["current_step"],
                    "total_steps": self.total_steps,
                    "completed_steps": len(completed),
                    "missing_steps": len(missing),
                    "completion_percentage": (len(completed) / self.total_steps) * 100,
                    "missing_step_numbers": missing,
                    "status": f"step_{self.step_tracker['current_step']}_of_{self.total_steps}"
                }
            else:
                return self.step_tracker.get_progress()

        return {"status": "tracking_unavailable"}

    def verify_completion(self) -> Dict[str, Any]:
        """
        Verify all steps are complete

        MANDATORY: Cannot declare completion without this verification

        AUTOMATIC: Also runs completion verifier to check deliverables
        """
        # First verify step completion
        step_verification = None
        if self.step_tracker:
            if isinstance(self.step_tracker, dict):
                completed = [s for s, data in self.step_tracker["steps"].items() 
                            if data.get("status") == "completed"]
                missing = [s for s in range(1, self.total_steps + 1) if s not in completed]

                if missing:
                    step_verification = {
                        "verified": False,
                        "reason": f"Missing {len(missing)} steps: {missing}",
                        "current_step": self.step_tracker["current_step"],
                        "total_steps": self.total_steps,
                        "can_declare_complete": False
                    }
                else:
                    step_verification = {
                        "verified": True,
                        "reason": f"All {self.total_steps} steps completed",
                        "current_step": self.step_tracker["current_step"],
                        "total_steps": self.total_steps,
                        "can_declare_complete": True
                    }
            else:
                step_verification = self.step_tracker.verify_completion()

        if step_verification is None:
            step_verification = {
                "verified": False,
                "reason": "Step tracker not available",
                "can_declare_complete": False
            }

        # AUTOMATIC: Run v3_verification (pre-workflow checks)
        v3_verification = None
        if self.v3_verifier:
            try:
                workflow_data = self.to_dict()
                v3_result = self.v3_verifier.verify_workflow_preconditions(workflow_data)
                v3_verification = {
                    "passed": v3_result.passed,
                    "message": v3_result.message,
                    "step_name": v3_result.step_name,
                    "details": v3_result.details
                }
                if v3_result.passed:
                    self.logger.debug(f"✅ v3_verification: {v3_result.message}")
                else:
                    self.logger.warning(f"⚠️  v3_verification: {v3_result.message}")
            except Exception as e:
                self.logger.warning(f"v3_verification error: {e}")

        # AUTOMATIC: Run completion verifier if available
        completion_verification = None
        if self.completion_verifier:
            # WARN if expected_deliverables not set
            if not self.expected_deliverables:
                self.logger.warning(
                    f"⚠️  Workflow {self.workflow_name} has no expected_deliverables set. "
                    "Completion verification will be incomplete. "
                    "Set self.expected_deliverables in workflow __init__."
                )

            if self.expected_deliverables:
                try:
                    # Get expected tasks from step tracker
                    expected_tasks = []
                    if self.step_tracker and isinstance(self.step_tracker, dict):
                        for step_num, step_data in self.step_tracker.get("steps", {}).items():
                            expected_tasks.append({
                                "task_id": f"step_{step_num}",
                                "description": step_data.get("step_name", f"Step {step_num}"),
                                "verification_notes": []
                            })

                    # Run automatic verification
                    verification_result = self.completion_verifier.verify_workflow(
                        workflow_id=self.execution_id,
                        workflow_name=self.workflow_name,
                        expected_tasks=expected_tasks,
                        deliverables=self.expected_deliverables,
                        workflow_context={"step_verification": step_verification}
                    )

                    completion_verification = {
                        "overall_status": verification_result.overall_status.value,
                        "completion_percentage": verification_result.completion_percentage,
                        "summary": verification_result.verification_summary,
                        "missing_items": verification_result.missing_items,
                        "next_steps": verification_result.next_steps
                    }

                    # Log verification result
                    self.logger.info(f"✅ Automatic completion verification: {verification_result.completion_percentage:.1f}% complete")
                    if verification_result.next_steps:
                        self.logger.info(f"   Next: {verification_result.next_steps[0]}")

                except Exception as e:
                    self.logger.error(f"❌ Completion verifier error: {e}", exc_info=True)
                    # Don't fail workflow on verification error, but log clearly
                    completion_verification = {
                        "overall_status": "error",
                        "completion_percentage": 0.0,
                        "summary": f"Verification failed: {str(e)}",
                        "missing_items": [],
                        "next_steps": ["Fix verification system error"]
                    }

        # Combine step verification, v3_verification, and completion verification
        result = step_verification.copy()

        # Add v3_verification results (pre-workflow checks)
        if v3_verification:
            result["v3_verification"] = v3_verification
            # v3_verification failures don't block completion, but are logged

        # Add completion verification results (post-workflow checks)
        if completion_verification:
            result["completion_verification"] = completion_verification
            # If completion verification says incomplete, mark as cannot complete
            if completion_verification.get("completion_percentage", 100.0) < 100.0:
                result["can_declare_complete"] = False
                result["reason"] = f"Steps complete but deliverables missing: {len(completion_verification.get('missing_items', []))} items"

        return result

    def can_declare_complete(self) -> bool:
        """Check if workflow can declare completion"""
        verification = self.verify_completion()
        return verification.get("can_declare_complete", False)

    def track_outcome(self, result: Dict[str, Any], execution_start_time: Optional[datetime] = None) -> None:
        """
        Track workflow outcome for Lumina Data Mining Feedback Loop

        Call this after execute() completes to record the outcome.

        Args:
            result: Workflow execution result dictionary
            execution_start_time: Start time of execution (for duration calculation)
        """
        if not self.outcome_tracker:
            return

        try:
            import time
            from datetime import datetime

            # Calculate duration
            duration = 0.0
            if execution_start_time:
                duration = (datetime.now() - execution_start_time).total_seconds()
            elif 'duration' in result:
                duration = result.get('duration', 0.0)
            elif 'execution_time' in result:
                duration = result.get('execution_time', 0.0)

            # Determine success
            success = result.get('success', result.get('status') == 'completed' or result.get('final_status') == 'completed')

            # Extract outcome text
            outcome_text = (
                result.get('outcome_text') or
                result.get('result') or
                result.get('message') or
                str(result.get('final_status', 'completed' if success else 'failed'))
            )

            # Extract metrics
            metrics = result.get('metrics', {})
            if duration > 0:
                metrics['duration_seconds'] = duration

            # Track outcome
            self.outcome_tracker.track_outcome(
                workflow_name=self.workflow_name,
                execution_id=self.execution_id,
                success=success,
                outcome_text=outcome_text,
                intent_id=result.get('intent_id') or result.get('ask_id'),
                metrics=metrics,
                duration_seconds=duration,
                workflow_data=result
            )

            self.logger.info(f"✅ Workflow outcome tracked for {self.workflow_name}/{self.execution_id}")
        except Exception as e:
            self.logger.warning(f"Could not track workflow outcome: {e}")

    @abstractmethod
    async def execute(self) -> Dict[str, Any]:
        """
        Execute the workflow

        MANDATORY: Must track all steps during execution

        NOTE: After execution, call track_outcome() to record the result for Lumina feedback loop
        """
        pass

    def parallel_execute(self, tasks: List[Callable], max_workers: Optional[int] = None, 
                        use_processes: bool = False) -> Iterator[Any]:
        """
        Execute tasks in parallel with resource awareness.

        ALWAYS CONSIDER: Use parallel processing whenever possible for better performance.

        Args:
            tasks: List of callable tasks to execute
            max_workers: Maximum number of parallel workers (None = auto-detect)
            use_processes: Use ProcessPoolExecutor instead of ThreadPoolExecutor

        Yields:
            Results from completed tasks
        """
        if not PARALLEL_AVAILABLE:
            self.logger.warning("Parallel processing not available - executing sequentially")
            for task in tasks:
                try:
                    yield task()
                except Exception as e:
                    self.logger.error(f"Task failed: {e}")
            return

        if not tasks:
            return

        # Resource-aware worker limit
        if max_workers is None:
            import os
            cpu_count = os.cpu_count() or 4
            max_workers = min(4, len(tasks), max(1, cpu_count - 1))

        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor

        self.logger.info(f"Executing {len(tasks)} tasks in parallel with {max_workers} workers")

        with executor_class(max_workers=max_workers) as executor:
            futures = {executor.submit(task): i for i, task in enumerate(tasks)}

            for future in as_completed(futures):
                task_index = futures[future]
                try:
                    result = future.result()
                    yield result
                except Exception as e:
                    self.logger.error(f"Parallel task {task_index} failed: {e}", exc_info=True)

    def batch_process(self, items: List[Any], processor: Callable[[Any], Any], 
                     batch_size: int = 10, max_workers: Optional[int] = None) -> Iterator[Any]:
        """
        Process items in batches with parallel execution.

        ALWAYS CONSIDER: Use batch processing for large datasets.

        Args:
            items: List of items to process
            processor: Function to process each item
            batch_size: Number of items per batch
            max_workers: Maximum parallel workers per batch

        Yields:
            Results from processed items
        """
        total_batches = (len(items) + batch_size - 1) // batch_size
        self.logger.info(f"Processing {len(items)} items in {total_batches} batches (size: {batch_size})")

        for batch_num, i in enumerate(range(0, len(items), batch_size), 1):
            batch = items[i:i + batch_size]
            self.logger.debug(f"Processing batch {batch_num}/{total_batches} ({len(batch)} items)")

            # Create tasks for this batch
            tasks = [lambda item=x: processor(item) for x in batch]

            # Process batch in parallel
            for result in self.parallel_execute(tasks, max_workers=max_workers):
                yield result

    def auto_review_and_fix(self) -> Dict[str, Any]:
        """
        Execute automatic review and fix cycle

        Maintains chat histories, accepts changes, reviews, fixes, and feeds back.
        This is automatically called after workflow execution.
        """
        if not self.auto_review_fix:
            self.logger.warning("Auto Review & Fix not available")
            return {"status": "not_available"}

        self.logger.info("🔄 Executing auto review and fix cycle...")

        # Execute full cycle
        cycle_result = self.auto_review_fix.execute_full_cycle()

        # Feed back to workflow
        feedback = cycle_result.get("workflow_feedback", {})

        # Mark step
        self._mark_step(
            self.total_steps,
            "Auto Review & Fix Complete",
            "completed",
            details=feedback
        )

        return cycle_result

    def add_chat_history(self, agent: str, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Add entry to chat history (maintains agent chat histories)

        Also adds to master session for JARVIS lead session tracking.
        """
        if self.auto_review_fix:
            self.auto_review_fix.add_chat_history(agent, message, context)
        else:
            self.logger.debug(f"Chat history: {agent}: {message[:50]}")

        # Add to master session (JARVIS lead session)
        if self.master_session:
            try:
                self.master_session.add_to_master_session(
                    agent=agent,
                    message=message,
                    workflow_id=self.execution_id,
                    context=context
                )
            except Exception as e:
                self.logger.debug(f"Could not add to master session: {e}")

    def track_change(self, file_path: str, change_type: str, diff: Optional[str] = None):
        """Track a file change for review"""
        if self.auto_review_fix:
            return self.auto_review_fix.track_change(file_path, change_type, diff)
        else:
            self.logger.debug(f"Change tracked: {change_type} {file_path}")
            return None

    async def execute_llm_with_confidence_check(self, llm_call_func, context: str,
                                        task_type: str = "general") -> Dict[str, Any]:
        """
        Execute LLM call with confidence scoring to prevent hallucinations

        This creates a two-layer defense:
        1. Probabilistic confidence analysis (blocks hallucinations)
        2. Deterministic verification (ensures completion)

        Args:
            llm_call_func: Async function that makes the LLM call
            context: Context/prompt provided to LLM
            task_type: Type of task for scoring calibration

        Returns:
            Dict with llm_response, confidence_score, and decision

        Raises:
            HallucinationDetectedException: If LLM output is flagged as hallucinated
        """
        if not self.confidence_scorer:
            self.logger.warning("⚠️ Confidence Scorer not available - proceeding without hallucination protection")
            # Fallback to direct LLM call
            llm_response = await llm_call_func()
            return {
                "llm_response": llm_response,
                "confidence_score": None,
                "should_proceed": True,
                "warning": "No hallucination protection active"
            }

        # Make the LLM call
        llm_response = await llm_call_func()

        # Score confidence to detect hallucinations
        from llm_confidence_scorer import should_trust_llm_output, get_risk_level

        confidence_score = self.confidence_scorer.analyze_llm_output(
            prompt=context,  # Original prompt/context sent to LLM
            response=llm_response,  # LLM response to analyze
            context=context,  # Additional context (same as prompt in this case)
            expected_deliverables=None  # No expected deliverables info available here
        )

        # Make decision
        should_proceed = should_trust_llm_output(confidence_score)
        risk_level = get_risk_level(confidence_score)

        result = {
            "llm_response": llm_response,
            "confidence_score": confidence_score,
            "should_proceed": should_proceed,
            "risk_level": risk_level,
            "recommendations": confidence_score.recommendations
        }

        if should_proceed:
            self.logger.info(f"✅ LLM output trusted ({confidence_score.overall_confidence:.2f}) - proceeding to verification")
        else:
            self.logger.warning(f"🚨 LLM output flagged ({confidence_score.overall_confidence:.2f}) - {risk_level}")
            for rec in confidence_score.recommendations[:2]:
                self.logger.warning(f"   💡 {rec}")

            # Could raise exception here to block workflow
            # raise HallucinationDetectedException(f"LLM hallucination detected: {confidence_score.red_flags}")

        return result

    def register_with_wopr_patterns(self):
        """
        Register workflow with WOPR pattern mapping (CORE @WOPR)

        Principle: #pattern = @wopr workflows
        All workflows are identified and mapped to patterns for WOPR processing.
        """
        if not self.wopr_pattern_mapper:
            self.logger.warning("WOPR Pattern Mapper not available")
            return {"status": "not_available"}

        self.logger.info("🔗 Registering workflow with WOPR patterns...")

        # Process workflow mapping
        result = self.wopr_pattern_mapper.process_workflow_mapping()

        # Mark step
        self._mark_step(
            self.total_steps,
            "WOPR Pattern Mapping Complete",
            "completed",
            details=result
        )

        return result

    def process_with_master_session(self) -> Dict[str, Any]:
        """
        Process workflow with master session (JARVIS lead session)

        Uses workflow pattern matching to identify correct workflow(s) and process them.
        Applies master feedback loop to enhance workflows.
        """
        if not self.master_session:
            self.logger.warning("Master Session Manager not available")
            return {"status": "not_available"}

        self.logger.info("🔄 Processing workflow with master session...")

        # Process workflows from master session
        workflow_result = self.master_session.process_workflows_from_master()

        # Apply master feedback loop
        feedback_result = self.master_session.apply_master_feedback_loop()

        # Mark step
        self._mark_step(
            self.total_steps,
            "Master Session Processing Complete",
            "completed",
            details={
                "workflow_result": workflow_result,
                "feedback_result": feedback_result
            }
        )

        return {
            "workflow_processing": workflow_result,
            "feedback_loop": feedback_result
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow state to dictionary"""
        result = {
            "execution_id": self.execution_id,
            "workflow_name": self.workflow_name,
            "total_steps": self.total_steps,
            "progress": self.get_progress(),
            "verification": self.verify_completion(),
            "step_tracker": self.step_tracker
        }

        # Add review/fix status if available
        if self.auto_review_fix:
            result["review_fix_status"] = {
                "chat_history_count": len(self.auto_review_fix.chat_history),
                "changes_summary": self.auto_review_fix.get_changes_summary()
            }

        return result

    def store_in_memory(
        self,
        memory_tier: Optional[MemoryTier] = None,
        importance: float = 1.0,
        tags: Optional[List[str]] = None,
        success: bool = True
    ) -> Optional[str]:
        """
        Store workflow in persistent memory

        Args:
            memory_tier: Memory tier (default: SHORT_TERM)
            importance: Importance score (0.0-1.0)
            tags: Tags for categorization
            success: Whether workflow succeeded

        Returns:
            Workflow ID if stored, None otherwise
        """
        if not self.memory_persistence:
            return None

        if memory_tier is None:
            memory_tier = MemoryTier.SHORT_TERM

        try:
            workflow_id = self.memory_persistence.store_workflow(
                workflow_data=self.to_dict(),
                workflow_type=self.workflow_name,
                memory_tier=memory_tier,
                importance=importance,
                tags=tags or [self.workflow_name],
                success=success
            )
            self.logger.info(f"Workflow stored in {memory_tier.value} memory: {workflow_id}")
            return workflow_id
        except Exception as e:
            self.logger.error(f"Failed to store workflow in memory: {e}")
            return None

    def analyze_llm_output_safety(self, prompt: str, llm_response: str,
                                context: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze LLM output for hallucinations before processing

        PREVENTS: Probabilistic LLM outputs from becoming deterministic workflow failures

        Args:
            prompt: Original prompt sent to LLM
            llm_response: LLM response to analyze
            context: Additional context provided to LLM

        Returns:
            Analysis result with safety assessment
        """
        if not self.confidence_scorer:
            self.logger.warning("🧠 Confidence Scorer not available - proceeding without hallucination analysis")
            return {
                "safety_status": "unknown",
                "confidence_score": 0.5,
                "recommendations": ["Install LLM Confidence Scorer for hallucination detection"],
                "can_proceed": True
            }

        try:
            # Analyze LLM output for hallucinations
            confidence_score = self.confidence_scorer.analyze_llm_output(
                prompt=prompt,
                response=llm_response,
                context=context,
                expected_deliverables=self.expected_deliverables
            )

            # Determine if it's safe to proceed
            if confidence_score.confidence_level.value == "low":
                safety_status = "unsafe"
                can_proceed = False
                log_level = "error"
            elif confidence_score.confidence_level.value == "medium":
                safety_status = "caution"
                can_proceed = True  # Allow but with warnings
                log_level = "warning"
            else:
                safety_status = "safe"
                can_proceed = True
                log_level = "info"

            # Log analysis results
            getattr(self.logger, log_level)(
                f"🧠 LLM Safety Analysis: {confidence_score.overall_confidence:.2f} "
                f"({confidence_score.confidence_level.value}) - {len(confidence_score.hallucinations_detected)} "
                f"potential hallucinations detected"
            )

            # Log specific hallucinations
            for hallucination in confidence_score.hallucinations_detected:
                self.logger.warning(
                    f"🚨 HALLUCINATION: {hallucination.hallucination_type.value} - "
                    f"{hallucination.evidence}"
                )

            return {
                "safety_status": safety_status,
                "confidence_score": confidence_score.overall_confidence,
                "confidence_level": confidence_score.confidence_level.value,
                "hallucinations_detected": len(confidence_score.hallucinations_detected),
                "recommendations": confidence_score.recommendations,
                "can_proceed": can_proceed,
                "analysis_details": {
                    "semantic_coherence": confidence_score.semantic_coherence,
                    "factual_grounding": confidence_score.factual_grounding,
                    "deliverable_alignment": confidence_score.deliverable_alignment,
                    "completion_claim_validity": confidence_score.completion_claim_validity
                }
            }

        except Exception as e:
            self.logger.error(f"🧠 LLM Safety Analysis failed: {e}")
            return {
                "safety_status": "error",
                "confidence_score": 0.0,
                "recommendations": [f"Analysis failed: {str(e)}"],
                "can_proceed": False  # Be safe and block on analysis failure
            }


def require_step_tracking(func):
    """
    Decorator to require step tracking for workflow methods

    Ensures steps are tracked before declaring completion
    """
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'step_tracker') or self.step_tracker is None:
            raise RuntimeError(f"Step tracking required for {func.__name__} - no exceptions")
        return func(self, *args, **kwargs)
    return wrapper

