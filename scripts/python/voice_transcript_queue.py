#!/usr/bin/env python3
"""
Voice Transcript Queue System

Queues voice transcripts the same way as normal text requests.
Prevents control conflicts and ensures proper ordering.

Tags: #VOICE_INPUT #QUEUE #CONTROL #LUMINA_CORE
"""

import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from queue import Empty, Queue
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("VoiceTranscriptQueue")


class RequestType(Enum):
    """Type of request"""
    TEXT = "text"
    VOICE_TRANSCRIPT = "voice_transcript"
    COMMAND = "command"


@dataclass
class QueuedRequest:
    """A queued request (text or voice transcript)"""
    request_id: str
    request_type: RequestType
    content: str
    timestamp: datetime
    priority: int = 0  # Higher = more priority
    metadata: Optional[Dict[str, Any]] = None


class VoiceTranscriptQueue:
    """
    Queue system for voice transcripts (same as text requests)

    Prevents control conflicts by:
    - Queuing all requests (text and voice) in order
    - Processing one at a time
    - Allowing cancellation/stopping
    - Preventing fighting for control
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice transcript queue with parallel startup optimization"""
        startup_start = time.time()

        if project_root is None:
            project_root_path = Path(__file__).parent.parent.parent
        else:
            project_root_path = Path(project_root)

        self.project_root = project_root_path

        # Voice filter system (lazy-loaded)
        self._voice_filter_system = None

        # Thread pool for parallel operations
        self._executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="VoiceQueue")

        # Parallel initialization tasks
        init_futures = {}

        # NAS storage initialization (parallel)
        def init_nas_storage():
            try:
                from nas_storage_utility import get_nas_storage
                nas = get_nas_storage()
                storage_info = nas.get_storage_info()
                return nas, storage_info
            except ImportError:
                return None, None

        init_futures['nas'] = self._executor.submit(init_nas_storage)

        # Pre-initialize voice filter system (parallel)
        def init_voice_filter():
            try:
                from voice_filter_system import VoiceFilterSystem
                return VoiceFilterSystem(project_root=self.project_root)
            except (ImportError, IndentationError, SyntaxError, Exception) as e:
                logger.debug(f"   Voice filter initialization error: {e}")
                return None

        init_futures['voice_filter'] = self._executor.submit(init_voice_filter)

        # Wait for parallel initialization to complete (with error handling)
        try:
            nas_result, storage_info = init_futures['nas'].result(timeout=5.0)
            self.nas_storage = nas_result
            if storage_info:
                logger.debug("   📁 Using %s storage: %s",
                            "NAS" if storage_info["nas_available"] else "Local",
                            storage_info["storage_path"])
            else:
                logger.debug("   📁 Using local storage (NAS utility not available)")
        except Exception as e:
            logger.debug(f"   NAS storage initialization error: {e}")
            self.nas_storage = None
            logger.debug("   📁 Using local storage (NAS utility not available)")

        # Voice filter will be lazy-loaded when needed, but pre-initialized in background
        try:
            voice_filter_result = init_futures['voice_filter'].result(timeout=5.0)
            if voice_filter_result:
                self._voice_filter_system = voice_filter_result
        except Exception as e:
            logger.debug(f"   Voice filter initialization error: {e}")
            self._voice_filter_system = None

        # Request queue (FIFO, but priority-aware)
        # ENHANCED: Allow multiple submissions, process in queue
        self.request_queue = Queue()
        self.processing = False
        self.current_request = None
        self.processing_thread = None
        self.processing_queue: List[QueuedRequest] = []  # Active processing queue
        self.max_concurrent = 1  # Can be increased if Cursor supports parallel

        # Control flags
        self.stopped = False
        self.paused = False

        # Statistics
        self.stats = {
            "total_queued": 0,
            "total_processed": 0,
            "text_requests": 0,
            "voice_transcripts": 0,
            "cancelled": 0,
            "errors": 0,
            "startup_time_ms": 0,
            "shutdown_time_ms": 0
        }

        startup_time = (time.time() - startup_start) * 1000
        self.stats["startup_time_ms"] = startup_time
        logger.info("✅ Voice Transcript Queue initialized (startup: %.1fms)", startup_time)

    def queue_request(
        self,
        content: str,
        request_type: RequestType = RequestType.TEXT,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Queue a request (text or voice transcript)

        Args:
            content: Request content (text or transcript)
            request_type: Type of request (TEXT or VOICE_TRANSCRIPT)
            priority: Priority (higher = processed first)
            metadata: Optional metadata

        Returns:
            Request ID
        """
        request_id = f"req_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        queued_request = QueuedRequest(
            request_id=request_id,
            request_type=request_type,
            content=content,
            timestamp=datetime.now(),
            priority=priority,
            metadata=metadata or {}
        )

        self.request_queue.put(queued_request)
        self.stats["total_queued"] += 1

        if request_type == RequestType.TEXT:
            self.stats["text_requests"] += 1
        elif request_type == RequestType.VOICE_TRANSCRIPT:
            self.stats["voice_transcripts"] += 1

        queue_size = self.request_queue.qsize()
        logger.info(
            "   📥 Queued %s request (ID: %s, priority: %d, queue size: %d)",
            request_type.value,
            request_id,
            priority,
            queue_size
        )

        # ENHANCED: Allow multiple submissions even while processing
        # The queue already supports this - you can submit multiple voice transcriptions
        # They will process sequentially in order
        if request_type == RequestType.VOICE_TRANSCRIPT:
            if queue_size > 1:
                logger.info(
                    "   ✅ Multiple voice transcriptions queued - will process in order"
                )
                logger.info(
                    "   💡 You can submit multiple voice transcriptions even while one is processing"
                )

            # RECORD INTERACTION
            try:
                from jarvis_interaction_recorder import get_jarvis_interaction_recorder, InteractionType
                recorder = get_jarvis_interaction_recorder()
                recorder.record_interaction(
                    InteractionType.VOICE_COMMAND,
                    content=content[:100],  # First 100 chars
                    context={"queue_size": queue_size, "priority": priority},
                    outcome={"queued": True, "request_id": request_id}
                )
            except Exception as e:
                logger.debug(f"Could not record voice transcript interaction: {e}")

        # Start processing if not already running
        if not self.processing:
            self.start_processing()

        return request_id

    def queue_voice_transcript(
        self,
        transcript: str,
        audio_data: Optional[Any] = None,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Queue a voice transcript (same as text request)

        ENHANCED: Works even when agent is actively working/pinned.
        Voice input will be queued and sent to the active agent.
        OPTIMIZED: Parallel processing for faster startup.

        Args:
            transcript: Transcribed text
            audio_data: Optional audio data
            confidence: Optional transcription confidence
            metadata: Optional metadata

        Returns:
            Request ID
        """
        processing_start = time.time()
        transcript_lower = transcript.lower().strip()

        # PARALLEL PROCESSING: Run independent operations concurrently
        futures = {}

        # Task 1: REQUEST ID POWER WORD (independent)
        def create_request_id():
            try:
                from request_id_power_word_system import create_request
                request = create_request(
                    command=transcript,
                    user_id="voice_user",
                    problem=None,
                    solution_idea=None,
                    value=None
                )
                return request
            except (AttributeError, KeyError, ValueError) as e:
                logger.debug("   Could not create request ID: %s", e)
                return None

        futures['request_id'] = self._executor.submit(create_request_id)

        # Task 2: DECISIONING (independent)
        def process_decisioning():
            try:
                from decisioning_troubleshooting_system import (
                    get_decisioning_system, track_question)
                if "?" in transcript:
                    question = track_question(transcript, source="voice")
                    decisioning_system = get_decisioning_system()
                    ask_required = None
                    if question.troubleshooting_related:
                        ask_required = decisioning_system.check_ask_required(question.context_score)
                    return question, ask_required
            except Exception as e:
                logger.debug(f"   Could not track question: {e}")
            return None, None

        futures['decisioning'] = self._executor.submit(process_decisioning)

        # Task 3: INTENT PRESERVATION (independent)
        def analyze_intent_parallel():
            try:
                from intent_preservation_system import analyze_intent
                from jarvis_api_cli_control import get_jarvis_api_cli
                intent_analysis = analyze_intent(transcript, source="voice")
                jarvis_available = False
                try:
                    get_jarvis_api_cli()
                    jarvis_available = True
                except Exception:
                    pass
                return intent_analysis, jarvis_available
            except Exception as e:
                logger.debug(f"   Could not analyze intent: {e}")
            return None, False

        futures['intent'] = self._executor.submit(analyze_intent_parallel)

        # Task 4: MARK ACTIVITY (independent)
        def mark_activity_parallel():
            try:
                from cursor_auto_send_monitor import get_auto_send_monitor
                monitor = get_auto_send_monitor()
                if monitor:
                    monitor.mark_activity()
                    return True
            except Exception as e:
                logger.debug(f"   Could not mark activity: {e}")
            return False

        futures['activity'] = self._executor.submit(mark_activity_parallel)

        # Task 5: SPOCK Command Detection (independent)
        def check_spock():
            if transcript_lower.startswith("spock") or transcript_lower.startswith("@spock"):
                try:
                    from spock_command_system import process_spock_command
                    return process_spock_command(transcript)
                except Exception as e:
                    logger.debug(f"   Could not process SPOCK command: {e}")
            return None

        futures['spock'] = self._executor.submit(check_spock)

        # Task 6: BONES Command Detection (independent)
        def check_bones():
            if transcript_lower.startswith("bones") or transcript_lower.startswith("@bones"):
                try:
                    from bones_command_system import process_bones_command
                    return process_bones_command(transcript)
                except Exception as e:
                    logger.debug(f"   Could not process BONES command: {e}")
            return None

        futures['bones'] = self._executor.submit(check_bones)

        # Wait for all parallel tasks to complete and process results
        for future_name, future in futures.items():
            try:
                result = future.result(timeout=2.0)  # 2 second timeout per task

                if future_name == 'request_id' and result:
                    logger.info("   🎯 Request ID created: %s", result.request_id)
                    logger.info("   ⚡ Power word: %s", result.power_word.value)
                    logger.info("   📖 Story: %s", result.story.value)
                    logger.info("   🪞 Mirror perspective: %s",
                               result.mirror_perspective.get('framework', 'Unknown'))

                elif future_name == 'decisioning' and result[0]:
                    question, ask_required = result
                    logger.info(f"   ❓ Question tracked: {question.format.value}")
                    logger.info(f"      Context score: {question.context_score:.2f}")
                    logger.info(f"      Troubleshooting: {question.troubleshooting_related}")
                    if ask_required:
                        logger.info("   📋 @ASK required: Context score below decisioning threshold")

                elif future_name == 'intent' and result[0]:
                    intent_analysis, jarvis_available = result
                    logger.info(f"   🎯 INTENT CAPTURED: {intent_analysis.intent_summary}")
                    logger.info(f"   💬 {intent_analysis.feedback_message}")
                    logger.info(f"   📊 Clarity: {intent_analysis.clarity.value}, Confidence: {intent_analysis.confidence:.2f}")
                    logger.info(f"   🧩 Building blocks: {len(intent_analysis.building_blocks)}")
                    if jarvis_available:
                        logger.info("   🤖 @JARVIS assisting with context & intent establishment")
                    if intent_analysis.requires_clarification:
                        logger.warning(f"   ⚠️  Intent unclear - may need clarification: {intent_analysis.feedback_message}")
                        logger.info("   📋 @ASK may be required for clarification")

                elif future_name == 'activity' and result:
                    logger.debug("   ✅ Activity marked - voice transcript received")
                    logger.info("   🎤 Voice input detected - will be sent to active agent")

                elif future_name == 'spock' and result:
                    logger.info(f"   🖖 SPOCK command detected - analysis complete: {result.workflow_name}")
                    logger.info(f"      Context: {result.context.value}")
                    logger.info(f"      Steps: {len(result.steps)}")
                    logger.info(f"      Puzzle Pieces: {len(result.puzzle_pieces)}")

                elif future_name == 'bones' and result:
                    logger.info(f"   🩺 BONES command detected - diagnosis complete: {result.problem_description}")
                    logger.info(f"      Problem Type: {result.problem_type.value}")
                    logger.info(f"      Checks: {len(result.checks)}")
                    logger.info(f"      Symptoms: {len(result.symptoms)}")
                    logger.info(f"      Remedies: {len(result.remedies)}")
            except Exception as e:
                logger.debug(f"   Parallel task {future_name} error: {e}")

        processing_time = (time.time() - processing_start) * 1000
        logger.debug(f"   ⚡ Parallel processing completed in {processing_time:.1f}ms")

        transcript_metadata = metadata or {}
        if audio_data is not None:
            transcript_metadata["has_audio"] = True
        if confidence is not None:
            transcript_metadata["confidence"] = confidence

        return self.queue_request(
            content=transcript,
            request_type=RequestType.VOICE_TRANSCRIPT,
            priority=0,  # Same priority as text
            metadata=transcript_metadata
        )

    def start_processing(self):
        """Start processing queue"""
        if self.processing:
            return

        self.processing = True
        self.stopped = False
        self.paused = False

        self.processing_thread = threading.Thread(
            target=self._process_queue,
            daemon=True,
            name="VoiceTranscriptQueueProcessor"
        )
        self.processing_thread.start()

        logger.info("   🚀 Queue processing started")

    def stop_processing(self):
        """Stop processing queue with parallel cleanup"""
        shutdown_start = time.time()
        self.stopped = True
        self.processing = False

        # Parallel cleanup tasks
        cleanup_futures = []

        # Wait for current request to finish (if any)
        def wait_for_current_request():
            if self.current_request:
                max_wait = 5.0  # Max 5 seconds
                wait_start = time.time()
                while self.current_request and (time.time() - wait_start) < max_wait:
                    time.sleep(0.1)

        cleanup_futures.append(self._executor.submit(wait_for_current_request))

        # Wait for processing thread to finish
        def wait_for_thread():
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=2.0)

        cleanup_futures.append(self._executor.submit(wait_for_thread))

        # Wait for all cleanup tasks
        for future in as_completed(cleanup_futures, timeout=5.0):
            try:
                future.result()
            except Exception as e:
                logger.debug(f"   Cleanup task error: {e}")

        # Shutdown executor gracefully
        def shutdown_executor():
            self._executor.shutdown(wait=True, timeout=2.0)

        shutdown_executor()

        shutdown_time = (time.time() - shutdown_start) * 1000
        self.stats["shutdown_time_ms"] = shutdown_time
        logger.info("   🛑 Queue processing stopped (shutdown: %.1fms)", shutdown_time)

    def pause_processing(self):
        """Pause processing (but keep queue)"""
        self.paused = True
        logger.info("   ⏸️  Queue processing paused")

    def resume_processing(self):
        """Resume processing"""
        self.paused = False
        logger.info("   ▶️  Queue processing resumed")

    def cancel_request(self, request_id: str) -> bool:
        """Cancel a specific request (if not yet processed)"""
        # Note: Queue doesn't support removal, so we mark it for skipping
        if self.current_request and self.current_request.request_id == request_id:
            self.current_request = None
            self.stats["cancelled"] += 1
            logger.info("   🛑 Cancelled request: %s", request_id)
            return True
        # Can't cancel queued items easily, but we can skip them during processing
        return False

    def clear_queue(self):
        """Clear all queued requests"""
        # Drain the queue
        while not self.request_queue.empty():
            try:
                self.request_queue.get_nowait()
            except Empty:
                break
        self.stats["cancelled"] += self.request_queue.qsize()
        logger.info("   🗑️  Queue cleared")

    def _process_queue(self):
        """Process queue (runs in background thread)"""
        logger.info("   🔄 Queue processor started")

        while self.processing and not self.stopped:
            try:
                # Check if paused
                if self.paused:
                    time.sleep(0.5)
                    continue

                # Get next request (with timeout to check stop flag)
                try:
                    request = self.request_queue.get(timeout=1.0)
                except Empty:
                    continue

                # Check if stopped while waiting
                if self.stopped:
                    # Put request back
                    self.request_queue.put(request)
                    break

                self.current_request = request

                logger.info(
                    "   📤 Processing %s request (ID: %s): %s",
                    request.request_type.value,
                    request.request_id,
                    request.content[:50] + "..." if len(request.content) > 50 else request.content
                )

                # Process request
                try:
                    self._handle_request(request)
                    self.stats["total_processed"] += 1
                except (AttributeError, TypeError, ValueError, KeyError) as e:
                    self.stats["errors"] += 1
                    logger.error("   ❌ Error processing request %s: %s", request.request_id, e)

                self.current_request = None
                self.request_queue.task_done()

                # Small delay between requests
                time.sleep(0.1)

            except (AttributeError, TypeError, ValueError) as e:
                logger.error("   ❌ Error in queue processor: %s", e)
                time.sleep(1.0)

        self.processing = False
        logger.info("   ⏹️  Queue processor stopped")

    def _handle_request(self, request: QueuedRequest):
        """
        Handle a queued request

        This is where the request is actually sent/processed.
        Types the text into Cursor IDE chat input and sends it.

        CRITICAL: Voice transcripts are filtered BEFORE sending to prevent
        TV bleed-through, wife/Glenda voice, and other unwanted audio.
        """
        content = request.content.strip()
        if not content:
            logger.warning("   ⚠️  Empty request content - skipping")
            return

        if request.request_type == RequestType.VOICE_TRANSCRIPT:
            logger.info(
                "   🎤 Processing voice transcript: %s",
                content[:100] + "..." if len(content) > 100 else content
            )

            # CRITICAL: Filter voice transcripts BEFORE sending
            # This prevents TV bleed-through, wife/Glenda voice, etc.
            should_filter = self._filter_voice_transcript(
                transcript=content,
                audio_data=request.metadata.get("audio_data") if request.metadata else None,
                confidence=request.metadata.get("confidence") if request.metadata else None
            )

            if should_filter:
                logger.info("   🚫 Voice transcript FILTERED - not sending (TV/wife/tertiary audio)")
                # Mark speech end even if filtered (transcription completed)
                try:
                    from cursor_auto_send_monitor import get_auto_send_monitor
                    monitor = get_auto_send_monitor()
                    if monitor:
                        monitor.mark_speech_end()
                        logger.debug("   ✅ Speech end marked (filtered transcript)")
                except Exception as e:
                    logger.debug(f"   Could not mark speech end: {e}")
                return  # Don't send filtered transcripts

            logger.info("   ✅ Voice transcript passed filter - processing with Grammarly (AI-driven)...")

            # STEP 1: Grammarly processing (must happen first, before other operations)
            processing_start = time.time()
            try:
                from grammarly_ai_driven_cli import process_transcript
                logger.info("   🔍 Processing transcript through Grammarly CLI/API...")
                corrected_content = process_transcript(content)  # Auto-accept is default
                if corrected_content != content:
                    logger.info("   ✅ Grammarly corrections auto-accepted")
                    logger.info(f"   📝 Original: {content[:50]}...")
                    logger.info(f"   ✅ Corrected: {corrected_content[:50]}...")
                    content = corrected_content  # Use corrected version
                else:
                    logger.info("   ✅ No Grammarly corrections needed")
            except ImportError as e:
                logger.warning(f"   ⚠️  Grammarly CLI/API not available: {e}")
                logger.warning("   📝 Continuing with original transcript (no Grammarly)")
            except Exception as e:
                logger.warning(f"   ⚠️  Grammarly processing failed: {e}")
                logger.warning("   📝 Continuing with original transcript (Grammarly error)")

            # STEP 2: PARALLEL PROCESSING - Run independent operations concurrently
            # These can all run in parallel after Grammarly correction
            parallel_futures = {}

            # Task 1: SYNC CONFIRMATION (independent)
            def process_sync_confirmation():
                try:
                    from ai_operator_sync_confirmation_system import \
                        get_sync_system
                    sync_system = get_sync_system()
                    sync_system.process_request(content, source="voice")
                    return True
                except ImportError:
                    return None
                except Exception as e:
                    logger.debug(f"   Sync confirmation error: {e}")
                    return None

            parallel_futures['sync'] = self._executor.submit(process_sync_confirmation)

            # Task 2: UNIFIED INTEGRATION (independent)
            def process_unified_integration():
                try:
                    from lumina_unified_integration import \
                        get_unified_integration
                    unified = get_unified_integration()
                    workflow_state = unified.process_unified_request(
                        input_text=content,
                        source="voice",
                        context={"system_state": "processing_voice"}
                    )
                    return workflow_state
                except ImportError:
                    # Fallback to individual systems
                    try:
                        from cursor_archive_workflow_integration import \
                            get_archive_workflow
                        content_lower = content.lower()
                        if "#troubleshot" in content_lower or "#decisioned" in content_lower:
                            archive_workflow = get_archive_workflow()
                            session_id = f"voice_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                            if "#troubleshot" in content_lower:
                                archive_workflow.mark_troubleshot(
                                    session_id=session_id,
                                    issue_description=content[:200]
                                )
                            if "#decisioned" in content_lower:
                                archive_workflow.mark_decisioned(
                                    session_id=session_id,
                                    decision=content[:200]
                                )
                            return "archive_workflow"
                    except ImportError:
                        pass
                except Exception as e:
                    logger.debug(f"   Unified integration error: {e}")
                return None

            parallel_futures['unified'] = self._executor.submit(process_unified_integration)

            # Task 3: PREDICTIVE ACTIONS (independent)
            def process_predictive_actions():
                try:
                    from predictive_actions_framework import (
                        Action, ActionType, get_predictive_actions_framework)
                    framework = get_predictive_actions_framework()
                    action = Action(
                        action_id=f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
                        action_type=ActionType.COMMUNICATE,
                        target="voice_transcript",
                        description=f"Voice input: {content[:50]}...",
                        context={
                            "source": "voice",
                            "active_files": [],
                            "system_state": "listening"
                        },
                        source="voice",
                        intent_summary=content[:100]
                    )
                    framework.record_action(action)
                    current_context = {
                        "source": "voice",
                        "system_state": "processing_voice",
                        "recent_commands": [content[:50]]
                    }
                    suggestions = framework.suggest_actions(current_context, max_suggestions=3)
                    return suggestions
                except ImportError:
                    return None
                except Exception as e:
                    logger.debug(f"   Predictive actions error: {e}")
                    return None

            parallel_futures['predictive'] = self._executor.submit(process_predictive_actions)

            # Wait for all parallel tasks and process results
            for future_name, future in parallel_futures.items():
                try:
                    result = future.result(timeout=3.0)  # 3 second timeout per task

                    if future_name == 'sync' and result:
                        logger.info("   ⏸️  SYNC CONFIRMATION REQUIRED - Execution paused")
                        logger.info("   📋 Reformulated request presented to operator")
                        logger.info("   ⏳ Waiting for operator confirmation...")
                        logger.info("   🔄 WORKFLOW: Analyze Intent → Reformulate (AI Speak + Grammarly)")
                        logger.info("   🔄 WORKFLOW: Present to Operator → Wait for Confirmation")
                        logger.info("   🔄 WORKFLOW: Execute only after sync confirmed")
                    elif future_name == 'sync' and result is None:
                        logger.debug("   Sync confirmation system not available - proceeding without confirmation")

                    elif future_name == 'unified' and result:
                        if hasattr(result, 'workflow_id'):
                            logger.info("   🌟 Unified LUMINA workflow processed")
                            logger.info(f"   📋 Workflow ID: {result.workflow_id}")
                            logger.info(f"   🧩 Intent: {result.intent}")
                            logger.info(f"   🔮 Actions Predicted: {len(result.actions_predicted)}")
                            logger.info(f"   📦 Archive Ready: {result.archive_ready}")
                            logger.info(f"   🔄 Synced: {result.synced}")
                        elif result == "archive_workflow":
                            logger.info("   🔧 Archive workflow processed (fallback)")
                    elif future_name == 'unified' and result is None:
                        logger.debug("   Unified integration not available - using individual systems")

                    elif future_name == 'predictive' and result:
                        logger.info("   🔮 PREDICTIVE ACTIONS - Suggested next actions:")
                        for i, suggestion in enumerate(result, 1):
                            pred = suggestion.predicted_action
                            logger.info(
                                f"      {i}. {pred.action_type.value} -> "
                                f"{pred.target} ({pred.confidence.value}, "
                                f"{pred.confidence_score:.0%})"
                            )
                            logger.info(f"         Reasoning: {pred.reasoning}")
                    elif future_name == 'predictive' and result is None:
                        logger.debug("   Predictive actions framework not available")
                except Exception as e:
                    logger.debug(f"   Parallel task {future_name} error: {e}")

            processing_time = (time.time() - processing_start) * 1000
            logger.debug(f"   ⚡ Parallel request processing completed in {processing_time:.1f}ms")

            logger.info("   🎤 Voice input will be sent to active/pinned agent after pause")

            # CRITICAL: Type transcript into chat field FIRST (before marking speech end)
            # This ensures text is in chat field when auto-send monitor triggers
            # ENHANCED: Works even when agent is actively working/pinned
            try:
                # Focus chat field and type transcript (but DON'T send yet)
                # This will work even if an agent is currently processing
                self._type_to_chat_field(content)
                logger.debug("   ✅ Transcript typed into chat field")
                logger.info("   📝 Voice input queued - active agent will receive it after pause")
            except Exception as e:
                logger.error(f"   ❌ Failed to type transcript: {e}")
                logger.warning("   ⚠️  Retrying with immediate send (fallback for active agent)")
                # Fallback: try full send if typing fails
                # This ensures voice input gets through even if focus fails
                try:
                    self._send_to_cursor_ide(content)
                    logger.info("   ✅ Message sent to Cursor IDE (fallback - immediate send)")
                    logger.info("   🎤 Voice input delivered to active agent")
                    # Mark speech end even in fallback
                    try:
                        from cursor_auto_send_monitor import \
                            get_auto_send_monitor
                        monitor = get_auto_send_monitor()
                        if monitor:
                            monitor.mark_speech_end()
                    except Exception:
                        pass
                    return
                except Exception as e2:
                    logger.error("   ❌ Failed to send message: %s", e2)
                    logger.error("   ❌ Voice input could not be delivered to active agent")
                return

            # CRITICAL: Mark speech end AFTER typing (transcription complete, text in chat)
            # This triggers dynamic scaling wait timer in auto-send monitor
            # The auto-send monitor will handle sending after pause threshold
            try:
                from cursor_auto_send_monitor import get_auto_send_monitor
                monitor = get_auto_send_monitor()
                if monitor:
                    # CRITICAL: Ensure monitor is running
                    if not monitor.running:
                        logger.warning("   ⚠️  Auto-send monitor not running - starting...")
                        monitor.start()

                    # CRITICAL: Set pending transcript FIRST so monitor knows what to send
                    monitor.pending_transcript = content
                    logger.debug("   ✅ Pending transcript set for auto-send")

                    # Mark speech end - this starts the pause detection timer
                    monitor.mark_speech_end()
                    logger.debug("   ✅ Speech end marked - dynamic wait timer started")
                    logger.info("   ⏸️  Waiting for auto-send monitor to send after pause...")
                    logger.info(f"   ⏱️  Pause threshold: {monitor.pause_threshold:.1f}s")
                else:
                    logger.warning("   ⚠️  Auto-send monitor not available")
                    raise RuntimeError("Auto-send monitor not available")
            except Exception as e:
                logger.error(f"   ❌ Could not mark speech end: {e}")
                # Fallback: send immediately if auto-send monitor not available
                try:
                    import keyboard
                    keyboard.press_and_release('enter')
                    logger.info("   ✅ Message sent to Cursor IDE (fallback - no auto-send)")
                except Exception as e2:
                    logger.error("   ❌ Failed to send message: %s", e2)
                return

            # DON'T send immediately - let auto-send monitor handle it after pause
            # Text is now in chat field, monitor will send after pause threshold
            logger.info("   ✅ Voice transcript queued - auto-send will trigger after pause")
            return  # Exit - auto-send monitor will handle sending

        elif request.request_type == RequestType.TEXT:
            logger.info(
                "   📝 Processing text request: %s",
                content[:100] + "..." if len(content) > 100 else content
            )
            # Text requests can be sent immediately (not voice, so no pause needed)
            try:
                self._send_to_cursor_ide(content)
                logger.info("   ✅ Message sent to Cursor IDE")
            except Exception as e:
                logger.error("   ❌ Failed to send message to Cursor IDE: %s", e)
                raise

    def _filter_voice_transcript(
        self,
        transcript: str,
        audio_data: Optional[Any] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Filter voice transcript using voice filter system

        Returns True if transcript should be filtered (not sent),
        False if it should be sent.

        This prevents TV bleed-through, wife/Glenda voice, and other
        unwanted audio from being sent to Cursor IDE.

        CRITICAL: Wake word commands always bypass filtering to ensure
        user can always trigger JARVIS.
        """
        # CRITICAL BYPASS: Wake word commands always allowed through
        # This ensures user can always trigger JARVIS, even if voice
        # is not recognized as primary speaker
        if transcript:
            transcript_lower = transcript.lower().strip()
            wake_words = [
                "hey jarvis",
                "jarvis",
                "hey jarvis,",
                "hey jarvis.",
                "hey jarvis!",
                "hey jarvis test",
                "jarvis test"
            ]

            # Check if transcript starts with or contains wake word
            if any(transcript_lower.startswith(wake) or wake in transcript_lower[:50]
                   for wake in wake_words):
                logger.info("   ✅ WAKE WORD DETECTED - bypassing filter (user trigger)")

                # Mark as primary speaker in filter system to prevent future filtering
                try:
                    from voice_filter_system import VoiceFilterSystem
                    if hasattr(self, '_voice_filter_system') and self._voice_filter_system:
                        filter_system = self._voice_filter_system
                        if filter_system and filter_system.enabled:
                            # Force primary speaker active
                            filter_system.primary_speaker_active = True
                            filter_system.last_primary_activity = datetime.now()
                            logger.debug("   ✅ Primary speaker marked as active (wake word)")
                except Exception as e:
                    logger.debug(f"   Could not mark primary speaker: {e}")

                return False  # Don't filter - allow wake word through

        try:
            from voice_filter_system import VoiceFilterSystem

            # Create filter system instance (or reuse if cached)
            if not hasattr(self, '_voice_filter_system') or self._voice_filter_system is None:
                self._voice_filter_system = VoiceFilterSystem(
                    project_root=self.project_root
                )

            filter_system = self._voice_filter_system

            if not filter_system or not filter_system.enabled:
                # Filter system not available - allow through
                logger.debug("   Voice filter not available - allowing through")
                return False

            # Extract audio features if audio_data provided
            audio_features = None
            if audio_data:
                audio_features = filter_system.extract_audio_features(audio_data)

            # Check if should filter
            # This will automatically detect greetings and invite wife/third parties
            filter_result = filter_system.should_filter(
                audio_data=audio_data,
                audio_features=audio_features,
                transcription_text=transcript
            )

            # If greeting was detected and profile was auto-invited, log it
            if (transcript and filter_result and
                hasattr(filter_system, 'greeting_detection_enabled') and
                filter_system.greeting_detection_enabled):
                # Check if a greeting was just processed (would be in invited_profiles now)
                # This is handled automatically by should_filter() above
                pass

            if filter_result.should_filter:
                logger.info(
                    "   🚫 FILTERED: %s (confidence: %.2f, reason: %s)",
                    transcript[:50] + "..." if len(transcript) > 50 else transcript,
                    filter_result.confidence,
                    filter_result.reason
                )
                return True  # Filter it - don't send

            # Not filtered - allow through
            logger.debug(
                "   ✅ ALLOWED: %s (confidence: %.2f)",
                transcript[:50] + "..." if len(transcript) > 50 else transcript,
                filter_result.confidence
            )
            return False  # Don't filter - send it

        except ImportError:
            logger.debug("   Voice filter system not available - allowing through")
            return False  # Allow through if filter not available
        except (AttributeError, TypeError, ValueError) as e:
            logger.debug("   Voice filter check failed: %s - allowing through", e)
            return False  # Allow through on error (fail open)

    def _type_to_chat_field(self, text: str):
        """
        Type text into Cursor IDE chat input field (but DON'T send)

        This types the text into the chat field and leaves it there
        for the auto-send monitor to send after pause detection.

        ENHANCED: Works even when agent is actively working/pinned.
        Uses multiple focus attempts to ensure chat field is accessible.
        """
        try:
            import time

            import keyboard

            # FIXED: Use Tab to navigate to chat field (safer than Ctrl+L)
            # This avoids layout switching while still focusing the chat
            try:
                # Try using Tab to navigate to chat (if it's the next focusable element)
                # This is safer than Ctrl+L which switches layouts
                keyboard.press_and_release('tab')
                time.sleep(0.1)
            except Exception:
                pass  # If Tab navigation fails, continue anyway

            # Clear any existing text in chat field (Ctrl+A, then Delete)
            # This ensures we're starting fresh, especially if agent is typing
            try:
                keyboard.press_and_release('ctrl+a')
                time.sleep(0.1)
                keyboard.press_and_release('delete')
                time.sleep(0.1)
            except Exception:
                pass  # If clearing fails, continue anyway

            # Type the text (this will type into the chat input field)
            keyboard.write(text, delay=0.01)  # Fast typing

            logger.debug("   ✅ Typed transcript into chat field (waiting for auto-send)")
            logger.info("   🎤 Voice input queued - will send to active agent after pause")

        except ImportError:
            logger.warning("keyboard not available for typing")
            raise
        except Exception as e:
            logger.error(f"   ❌ Failed to type transcript: {e}")
            raise

    def _send_to_cursor_ide(self, text: str):
        """
        Send text to Cursor IDE chat input by typing it and pressing Enter

        This actively types the text into the chat input field and sends it immediately.
        Used for text requests or fallback scenarios.

        ENHANCED: Works even when agent is actively working/pinned.
        Uses multiple focus attempts and ensures message gets through.
        """
        try:
            import keyboard

            # FIXED: Use Tab to navigate to chat field (safer than Ctrl+L)
            # This avoids layout switching while still focusing the chat
            try:
                # Try using Tab to navigate to chat (if it's the next focusable element)
                # This is safer than Ctrl+L which switches layouts
                keyboard.press_and_release('tab')
                time.sleep(0.1)
            except Exception:
                pass  # If Tab navigation fails, continue anyway

            # Clear any existing text in chat field (Ctrl+A, then Delete)
            # This ensures we're starting fresh, especially if agent is typing
            try:
                keyboard.press_and_release('ctrl+a')
                time.sleep(0.1)
                keyboard.press_and_release('delete')
                time.sleep(0.1)
            except Exception:
                pass  # If clearing fails, continue anyway

            # Type the text (this will type into the chat input field)
            keyboard.write(text, delay=0.01)  # Fast typing

            # Small delay before sending
            time.sleep(0.1)

            # Press Enter to send
            keyboard.press_and_release('enter')

            logger.debug("   ✅ Typed and sent message to Cursor IDE")
            logger.info("   🎤 Voice input sent to active agent")

        except ImportError:
            # Fallback to Windows API if keyboard/pyautogui not available
            try:
                import win32api
                import win32clipboard
                import win32con

                # Copy text to clipboard
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardText(text)
                win32clipboard.CloseClipboard()

                # Paste (Ctrl+V)
                win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)
                win32api.keybd_event(ord('V'), 0, 0, 0)
                win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)
                win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)

                time.sleep(0.1)

                # Press Enter to send
                win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
                win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)

                logger.debug("   ✅ Pasted and sent message to Cursor IDE (Windows API)")

            except ImportError as exc:
                logger.error("   ❌ No keyboard automation library available")
                logger.error("   Install: pip install keyboard pyautogui pywin32")
                raise RuntimeError(
                    "Cannot send message - no keyboard automation available"
                ) from exc
        except (RuntimeError, OSError, ValueError) as e:
            logger.error("   ❌ Error sending message: %s", e)
            raise

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics with performance metrics"""
        stats = self.stats.copy()
        stats["queue_size"] = self.request_queue.qsize()
        stats["processing"] = self.processing
        stats["paused"] = self.paused
        stats["current_request"] = (
            self.current_request.request_id if self.current_request else None
        )

        # Performance metrics
        if stats.get("startup_time_ms", 0) > 0:
            stats["startup_time_seconds"] = stats["startup_time_ms"] / 1000.0
        if stats.get("shutdown_time_ms", 0) > 0:
            stats["shutdown_time_seconds"] = stats["shutdown_time_ms"] / 1000.0

        # CRITICAL: Ensure processing is ALWAYS active (full-time listening)
        if not self.processing and not self.stopped:
            self.start_processing()
            stats["processing"] = True
            stats["auto_restarted"] = True
            logger.info("   🔄 Auto-restarted queue processing (full-time listening)")
        # Health check: verify processing thread is alive
        if self.processing_thread and not self.processing_thread.is_alive():
            logger.warning("   ⚠️  Processing thread died - restarting")
            self.start_processing()
            stats["processing"] = True
            stats["thread_restarted"] = True

        # Add storage info if NAS storage available
        if hasattr(self, 'nas_storage') and self.nas_storage:
            stats["storage"] = self.nas_storage.get_storage_info()

        return stats

    def is_active(self) -> bool:
        """Check if queue is actively listening and processing"""
        return self.processing and not self.stopped and not self.paused

    def ensure_active(self):
        """Ensure queue is active and processing - call this to verify listening status (FULL-TIME)"""
        if not self.processing:
            self.start_processing()
            logger.info("   ✅ Queue activated - FULL-TIME LISTENING ACTIVE")
        elif self.paused:
            self.resume_processing()
            logger.info("   ✅ Queue resumed - FULL-TIME LISTENING ACTIVE")
        elif self.stopped:
            self.start_processing()
            logger.info("   ✅ Queue restarted - FULL-TIME LISTENING ACTIVE")
        # Health check: verify thread is alive
        if self.processing_thread and not self.processing_thread.is_alive():
            logger.warning("   ⚠️  Processing thread not alive - restarting for full-time listening")
            self.start_processing()


# Global instance
_queue_instance = None


def get_voice_transcript_queue() -> VoiceTranscriptQueue:
    """Get or create global queue instance - always active and ready (FULL-TIME LISTENING)"""
    global _queue_instance
    if _queue_instance is None:
        _queue_instance = VoiceTranscriptQueue()
        # Auto-start processing so queue is always active and listening
        _queue_instance.start_processing()
        logger.info("✅ Voice transcript queue initialized and ACTIVE - FULL-TIME LISTENING")
        # Auto-start full-time monitoring service (@mdv)
        _start_full_time_monitoring()
    else:
        # Health check: ensure it's still active (full-time monitoring)
        _queue_instance.ensure_active()
        # Verify processing thread is alive
        if _queue_instance.processing_thread and not _queue_instance.processing_thread.is_alive():
            logger.warning("   ⚠️  Queue processing thread died - restarting for full-time listening")
            _queue_instance.start_processing()
    return _queue_instance


def _start_full_time_monitoring():
    """Start full-time monitoring service (@mdv) - ensures continuous operation"""
    try:
        from full_time_monitoring_service import \
            get_full_time_monitoring_service
        get_full_time_monitoring_service()  # Auto-starts
        logger.debug("   ✅ Full-time monitoring service (@mdv) active")
    except ImportError:
        logger.debug("   Full-time monitoring service not available")
    except (AttributeError, TypeError, ValueError) as e:
        logger.debug("   Could not start full-time monitoring: %s", e)


def queue_voice_transcript(
    transcript: str,
    audio_data: Optional[Any] = None,
    confidence: Optional[float] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Queue a voice transcript - ensures queue is active and listening"""
    queue = get_voice_transcript_queue()
    queue.ensure_active()  # Ensure queue is actively listening
    return queue.queue_voice_transcript(
        transcript=transcript,
        audio_data=audio_data,
        confidence=confidence,
        metadata=metadata
    )


def queue_text_request(
    text: str,
    priority: int = 0,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Queue a text request - ensures queue is active and listening"""
    queue = get_voice_transcript_queue()
    queue.ensure_active()  # Ensure queue is actively listening
    return queue.queue_request(
        content=text,
        request_type=RequestType.TEXT,
        priority=priority,
        metadata=metadata
    )


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Transcript Queue")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--test", action="store_true", help="Test queue with sample requests")
    parser.add_argument("--reboot", action="store_true", help="Reboot queue to test startup/shutdown optimizations")

    args = parser.parse_args()

    if args.reboot:
        print("\n🔄 Rebooting Voice Transcript Queue...")
        print("=" * 60)

        # Get current instance and stop it
        global _queue_instance
        if _queue_instance is not None:
            print("\n⏹️  Stopping current instance...")
            _queue_instance.stop_processing()
            time.sleep(0.5)
            shutdown_time = _queue_instance.stats.get("shutdown_time_ms", 0)
            if shutdown_time > 0:
                print(f"   ✅ Shutdown completed in {shutdown_time:.1f}ms")

        # Clear instance to force fresh initialization
        _queue_instance = None

        # Create new instance (this will show startup time)
        print("\n🚀 Starting fresh instance...")
        start_time = time.time()
        queue = get_voice_transcript_queue()
        startup_time = (time.time() - start_time) * 1000

        # Get stats including timing
        stats = queue.get_stats()

        print("\n📊 Reboot Statistics:")
        print("=" * 60)
        print(f"   ⚡ Startup time: {stats.get('startup_time_ms', startup_time):.1f}ms")
        if stats.get('shutdown_time_ms', 0) > 0:
            print(f"   ⏹️  Shutdown time: {stats['shutdown_time_ms']:.1f}ms")
        print(f"   📦 Total queued: {stats['total_queued']}")
        print(f"   ✅ Total processed: {stats['total_processed']}")
        print(f"   📝 Text requests: {stats['text_requests']}")
        print(f"   🎤 Voice transcripts: {stats['voice_transcripts']}")
        print(f"   🛑 Cancelled: {stats['cancelled']}")
        print(f"   ❌ Errors: {stats['errors']}")
        print(f"   📊 Queue size: {stats['queue_size']}")
        print(f"   🔄 Processing: {stats['processing']}")
        print(f"   ⏸️  Paused: {stats['paused']}")
        print("=" * 60)
        print("✅ Reboot complete!")
        return 0

    queue = get_voice_transcript_queue()

    if args.stats:
        stats = queue.get_stats()
        print("\n📊 Queue Statistics:")
        print(f"   Total queued: {stats['total_queued']}")
        print(f"   Total processed: {stats['total_processed']}")
        print(f"   Text requests: {stats['text_requests']}")
        print(f"   Voice transcripts: {stats['voice_transcripts']}")
        print(f"   Cancelled: {stats['cancelled']}")
        print(f"   Errors: {stats['errors']}")
        print(f"   Queue size: {stats['queue_size']}")
        print(f"   Processing: {stats['processing']}")
        print(f"   Paused: {stats['paused']}")
        if stats.get('startup_time_ms', 0) > 0:
            print(f"   ⚡ Startup time: {stats['startup_time_ms']:.1f}ms")
        if stats.get('shutdown_time_ms', 0) > 0:
            print(f"   ⏹️  Shutdown time: {stats['shutdown_time_ms']:.1f}ms")

    if args.test:
        print("\n🧪 Testing queue...")
        queue.start_processing()

        # Queue some test requests
        queue_text_request("Test text request 1")
        queue_voice_transcript("Test voice transcript 1")
        queue_text_request("Test text request 2")

        # Wait a bit
        time.sleep(2)

        # Show stats
        stats = queue.get_stats()
        print(f"\n✅ Test complete. Processed: {stats['total_processed']}")

    return 0


if __name__ == "__main__":


    sys.exit(main())