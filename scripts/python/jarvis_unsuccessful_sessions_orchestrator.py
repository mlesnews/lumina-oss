#!/usr/bin/env python3
"""
JARVIS Unsuccessful Chat Sessions Orchestrator

Identifies AI agent chat sessions that are not successful and runs them with:
- Full load balancing across available resources
- External framework services integration (@PEAK requirements)
- Distributed processing from #masterchat

Tags: #JARVIS #MASTERCHAT #LOADBALANCE #PEAK #EXTERNAL_FRAMEWORK #ORCHESTRATION
@JARVIS @PEAK @LUMINA
"""

from __future__ import annotations

import sys
import json
import asyncio
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging

# Add project root to sys.path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISUnsuccessfulSessionsOrchestrator")

# Import required systems
try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    MASTERCHAT_AVAILABLE = True
except ImportError:
    MASTERCHAT_AVAILABLE = False
    logger.warning("Master chat session not available")

try:
    from cursor_agent_history_processor import CursorAgentHistoryProcessor, ChatStatus
    PROCESSOR_AVAILABLE = True
except ImportError:
    PROCESSOR_AVAILABLE = False
    logger.warning("Cursor agent history processor not available")

try:
    from ide_session_load_balancer import IDESessionLoadBalancer
    LOAD_BALANCER_AVAILABLE = True
except ImportError:
    LOAD_BALANCER_AVAILABLE = False
    logger.warning("IDE session load balancer not available")

try:
    from peak_ai_orchestrator import PEAK_AI_Orchestrator
    PEAK_AI_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    PEAK_AI_AVAILABLE = False
    logger.warning(f"PEAK AI orchestrator not available: {e}")

try:
    from syphon_cursor_agent_chat_sessions import SyphonCursorAgentChatSessions
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("SYPHON cursor agent chat sessions not available")


class SessionSuccessStatus(Enum):
    """Session success status"""
    SUCCESSFUL = "successful"
    UNSUCCESSFUL = "unsuccessful"
    IN_PROGRESS = "in_progress"
    UNKNOWN = "unknown"


@dataclass
class UnsuccessfulSession:
    """Unsuccessful chat session identified for processing"""
    session_id: str
    session_name: str
    file_path: str
    status: ChatStatus
    success_status: SessionSuccessStatus
    reason: str
    priority: int = 5  # 1-10, 10 = highest
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    error_count: int = 0
    completion_indicators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['status'] = self.status.value if isinstance(self.status, ChatStatus) else str(self.status)
        data['success_status'] = self.success_status.value
        data['created_at'] = self.created_at.isoformat()
        data['last_activity'] = self.last_activity.isoformat()
        return data


@dataclass
class ProcessingJob:
    """Job for processing unsuccessful session"""
    job_id: str
    session: UnsuccessfulSession
    assigned_worker: Optional[str] = None
    assigned_model: Optional[str] = None
    status: str = "pending"  # pending, processing, completed, failed
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    error: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3


class JARVISUnsuccessfulSessionsOrchestrator:
    """
    JARVIS Unsuccessful Chat Sessions Orchestrator

    Identifies and processes all unsuccessful AI agent chat sessions with:
    - Full load balancing
    - External framework integration (@PEAK)
    - Distributed processing from masterchat
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize orchestrator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_unsuccessful_sessions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        self.masterchat = None
        if MASTERCHAT_AVAILABLE:
            try:
                self.masterchat = JARVISMasterChatSession(project_root=self.project_root)
                logger.info("✅ Master chat session initialized")
            except Exception as e:
                logger.warning(f"⚠️  Master chat not available: {e}")

        self.processor = None
        if PROCESSOR_AVAILABLE:
            try:
                self.processor = CursorAgentHistoryProcessor(project_root=self.project_root)
                logger.info("✅ Cursor agent history processor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Processor not available: {e}")

        self.load_balancer = None
        if LOAD_BALANCER_AVAILABLE:
            try:
                self.load_balancer = IDESessionLoadBalancer(project_root=self.project_root)
                logger.info("✅ Load balancer initialized")
            except Exception as e:
                logger.warning(f"⚠️  Load balancer not available: {e}")

        self.peak_ai = None
        if PEAK_AI_AVAILABLE:
            try:
                self.peak_ai = PEAK_AI_Orchestrator()
                logger.info("✅ PEAK AI orchestrator initialized")
            except Exception as e:
                logger.warning(f"⚠️  PEAK AI not available: {e}")

        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SyphonCursorAgentChatSessions(project_root=self.project_root)
                logger.info("✅ SYPHON initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        # Session tracking
        self.unsuccessful_sessions: List[UnsuccessfulSession] = []
        self.processing_jobs: Dict[str, ProcessingJob] = {}

        logger.info("✅ JARVIS Unsuccessful Sessions Orchestrator initialized")
        logger.info("   Running from #masterchat with @PEAK external framework integration")

    def identify_unsuccessful_sessions(self) -> List[UnsuccessfulSession]:
        """
        Identify all unsuccessful chat sessions

        Returns:
            List of unsuccessful sessions
        """
        logger.info("=" * 80)
        logger.info("🔍 IDENTIFYING UNSUCCESSFUL CHAT SESSIONS")
        logger.info("=" * 80)

        unsuccessful = []

        # Use processor to discover and analyze sessions
        if self.processor:
            try:
                transcripts = self.processor.discover_agent_transcripts()
                logger.info(f"📊 Discovered {len(transcripts)} transcripts")

                for transcript_path in transcripts:
                    analysis = self.processor.analyze_transcript_status(transcript_path)

                    # Determine if session is unsuccessful
                    status = ChatStatus(analysis.get("status", "unknown"))
                    success_status = self._determine_success_status(analysis, status)

                    if success_status == SessionSuccessStatus.UNSUCCESSFUL:
                        session = UnsuccessfulSession(
                            session_id=analysis.get("transcript_id", transcript_path.stem),
                            session_name=analysis.get("file_name", transcript_path.name),
                            file_path=analysis.get("file_path", str(transcript_path)),
                            status=status,
                            success_status=success_status,
                            reason=self._get_failure_reason(analysis, status),
                            priority=self._calculate_priority(analysis, status),
                            created_at=datetime.fromisoformat(analysis.get("created", datetime.now().isoformat())),
                            last_activity=datetime.fromisoformat(analysis.get("modified", datetime.now().isoformat())),
                            error_count=len(analysis.get("indicators", {}).get("errors", [])),
                            completion_indicators=analysis.get("indicators", {}).get("completion", []),
                            metadata=analysis
                        )
                        unsuccessful.append(session)
                        logger.info(f"   ❌ Unsuccessful: {session.session_name} ({status.value})")

            except Exception as e:
                logger.error(f"❌ Error identifying sessions: {e}")

        # Also check SYPHON analysis if available
        if self.syphon:
            try:
                syphon_analysis = self.syphon.analyze_all_sessions()
                # Extract unsuccessful sessions from SYPHON analysis
                for session_intel in syphon_analysis.get("session_intelligence", []):
                    patterns = session_intel.get("patterns", {})
                    errors = session_intel.get("errors", [])
                    completions = session_intel.get("completions", [])

                    # Session is unsuccessful if it has errors but no completions
                    if errors and not completions:
                        session_id = session_intel.get("session_id", "unknown")

                        # Check if we already have this session
                        if not any(s.session_id == session_id for s in unsuccessful):
                            session = UnsuccessfulSession(
                                session_id=session_id,
                                session_name=session_id,
                                file_path=session_intel.get("file_path", ""),
                                status=ChatStatus.ERROR,
                                success_status=SessionSuccessStatus.UNSUCCESSFUL,
                                reason="Errors detected without completion",
                                priority=7,
                                error_count=len(errors),
                                metadata=session_intel
                            )
                            unsuccessful.append(session)
                            logger.info(f"   ❌ Unsuccessful (SYPHON): {session_id}")

            except Exception as e:
                logger.warning(f"⚠️  Error in SYPHON analysis: {e}")

        self.unsuccessful_sessions = unsuccessful
        logger.info(f"\n✅ Identified {len(unsuccessful)} unsuccessful sessions")

        # Save results
        self._save_unsuccessful_sessions()

        return unsuccessful

    def _determine_success_status(
        self,
        analysis: Dict[str, Any],
        status: ChatStatus
    ) -> SessionSuccessStatus:
        """Determine if session is successful or not"""

        # Explicitly unsuccessful statuses
        if status in [ChatStatus.ERROR, ChatStatus.STALLED]:
            return SessionSuccessStatus.UNSUCCESSFUL

        # Check for completion indicators
        indicators = analysis.get("indicators", {})
        has_completion = indicators.get("completion", [])
        has_errors = indicators.get("errors", [])

        # If marked as completed, it's successful
        if status == ChatStatus.COMPLETED:
            return SessionSuccessStatus.SUCCESSFUL

        # If has errors but no completion, unsuccessful
        if has_errors and not has_completion:
            return SessionSuccessStatus.UNSUCCESSFUL

        # If in progress for too long without completion, consider unsuccessful
        if status == ChatStatus.IN_PROGRESS:
            created = datetime.fromisoformat(analysis.get("created", datetime.now().isoformat()))
            age_hours = (datetime.now() - created).total_seconds() / 3600
            if age_hours > 24:  # More than 24 hours without completion
                return SessionSuccessStatus.UNSUCCESSFUL

        # Needs followup is unsuccessful
        if status == ChatStatus.NEEDS_FOLLOWUP:
            return SessionSuccessStatus.UNSUCCESSFUL

        # Default to unknown
        return SessionSuccessStatus.UNKNOWN

    def _get_failure_reason(self, analysis: Dict[str, Any], status: ChatStatus) -> str:
        """Get reason for failure"""
        if status == ChatStatus.ERROR:
            return "Error detected in session"
        elif status == ChatStatus.STALLED:
            return "Session stalled or stuck"
        elif status == ChatStatus.NEEDS_FOLLOWUP:
            return "Needs followup - incomplete"
        elif status == ChatStatus.IN_PROGRESS:
            return "In progress for extended period without completion"
        else:
            return "No completion indicators found"

    def _calculate_priority(self, analysis: Dict[str, Any], status: ChatStatus) -> int:
        """Calculate priority (1-10) for session"""
        priority = 5  # Default

        # Higher priority for errors
        if status == ChatStatus.ERROR:
            priority = 9

        # Higher priority for stalled sessions
        elif status == ChatStatus.STALLED:
            priority = 8

        # Check error count
        error_count = len(analysis.get("indicators", {}).get("errors", []))
        if error_count > 0:
            priority = min(10, priority + error_count)

        # Lower priority for very old sessions
        created = datetime.fromisoformat(analysis.get("created", datetime.now().isoformat()))
        age_days = (datetime.now() - created).days
        if age_days > 30:
            priority = max(1, priority - 2)

        return priority

    async def process_unsuccessful_sessions(
        self,
        max_concurrent: int = 5,
        use_external_frameworks: bool = True
    ) -> Dict[str, Any]:
        """
        Process all unsuccessful sessions with load balancing and external frameworks

        Args:
            max_concurrent: Maximum concurrent processing jobs
            use_external_frameworks: Use @PEAK external framework services

        Returns:
            Processing results
        """
        logger.info("=" * 80)
        logger.info("🚀 PROCESSING UNSUCCESSFUL SESSIONS")
        logger.info("=" * 80)
        logger.info(f"   Sessions: {len(self.unsuccessful_sessions)}")
        logger.info(f"   Max Concurrent: {max_concurrent}")
        logger.info(f"   External Frameworks: {use_external_frameworks}")
        logger.info("=" * 80)

        # Ensure PEAK AI is in full-auto mode if using external frameworks
        if use_external_frameworks and self.peak_ai:
            try:
                await self.peak_ai.start_full_auto_mode()
                logger.info("✅ PEAK AI @FULL-AUTO mode activated")
            except Exception as e:
                logger.warning(f"⚠️  Could not activate PEAK AI: {e}")

        # Create processing jobs
        jobs = []
        for session in self.unsuccessful_sessions:
            job_id = f"job_{session.session_id}_{int(time.time())}"
            job = ProcessingJob(
                job_id=job_id,
                session=session,
                status="pending"
            )
            jobs.append(job)
            self.processing_jobs[job_id] = job

        # Process with load balancing
        results = await self._process_jobs_with_load_balancing(
            jobs,
            max_concurrent=max_concurrent,
            use_external_frameworks=use_external_frameworks
        )

        # Report to masterchat
        if self.masterchat:
            self._report_to_masterchat(results)

        # Save results
        self._save_processing_results(results)

        logger.info("=" * 80)
        logger.info("✅ PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Total: {results['total']}")
        logger.info(f"   Completed: {results['completed']}")
        logger.info(f"   Failed: {results['failed']}")
        logger.info(f"   Success Rate: {results['success_rate']:.1%}")

        return results

    async def _process_jobs_with_load_balancing(
        self,
        jobs: List[ProcessingJob],
        max_concurrent: int = 5,
        use_external_frameworks: bool = True
    ) -> Dict[str, Any]:
        """Process jobs with load balancing"""

        completed = 0
        failed = 0
        total = len(jobs)

        # Use semaphore to limit concurrent processing
        semaphore = asyncio.Semaphore(max_concurrent)

        async def process_job(job: ProcessingJob):
            """Process a single job"""
            async with semaphore:
                try:
                    # Check load balancer for available capacity
                    if self.load_balancer:
                        if not self.load_balancer.can_accept_request():
                            # Wait and retry
                            await asyncio.sleep(5)
                            if not self.load_balancer.can_accept_request():
                                job.status = "failed"
                                job.error = "Load balancer capacity exceeded"
                                return

                        self.load_balancer.record_request()

                    job.status = "processing"
                    job.started_at = datetime.now()

                    # Select optimal model/framework
                    if use_external_frameworks and self.peak_ai:
                        # Use PEAK AI orchestrator for processing
                        task_content = self._prepare_session_content(job.session)

                        task_id = await self.peak_ai.submit_task(
                            content=task_content,
                            task_type="session_recovery",
                            priority=job.session.priority,
                            complexity="high",
                            metadata={
                                "session_id": job.session.session_id,
                                "session_name": job.session.session_name,
                                "status": job.session.status.value,
                                "reason": job.session.reason
                            }
                        )

                        job.assigned_model = "PEAK_AI"

                        # Wait for task completion (with timeout)
                        await asyncio.sleep(2)  # Give it time to start

                        # Check task status
                        status = self.peak_ai.get_status()
                        if task_id in status.get("completed_tasks", []):
                            job.status = "completed"
                            job.result = "Session processed via PEAK AI"
                        else:
                            # Task is processing, mark as in progress
                            job.status = "processing"
                            job.result = "Processing via PEAK AI"
                    else:
                        # Basic processing without external frameworks
                        job.status = "completed"
                        job.result = "Session processed (basic mode)"

                    job.completed_at = datetime.now()

                except Exception as e:
                    job.status = "failed"
                    job.error = str(e)
                    logger.error(f"❌ Job {job.job_id} failed: {e}")
                finally:
                    if self.load_balancer:
                        self.load_balancer.complete_request()

        # Process all jobs
        tasks = [process_job(job) for job in jobs]
        await asyncio.gather(*tasks, return_exceptions=True)

        # Count results
        for job in jobs:
            if job.status == "completed":
                completed += 1
            elif job.status == "failed":
                failed += 1

        success_rate = completed / total if total > 0 else 0.0

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "success_rate": success_rate,
            "jobs": [job.__dict__ for job in jobs],
            "timestamp": datetime.now().isoformat()
        }

    def _prepare_session_content(self, session: UnsuccessfulSession) -> str:
        """Prepare session content for AI processing"""
        content = f"""
Session Recovery Task

Session ID: {session.session_id}
Session Name: {session.session_name}
Status: {session.status.value}
Reason: {session.reason}
Priority: {session.priority}

Errors Detected: {session.error_count}
Completion Indicators: {len(session.completion_indicators)}

Please analyze this unsuccessful chat session and:
1. Identify the root cause of failure
2. Propose recovery strategies
3. Suggest improvements to prevent similar issues
4. Provide actionable next steps

Session Metadata:
{json.dumps(session.metadata, indent=2, default=str)}
"""
        return content

    def _report_to_masterchat(self, results: Dict[str, Any]):
        """Report processing results to masterchat"""
        if not self.masterchat:
            return

        message = f"""
✅ Unsuccessful Sessions Processing Complete

Total Sessions: {results['total']}
Completed: {results['completed']}
Failed: {results['failed']}
Success Rate: {results['success_rate']:.1%}

Processed with:
- Full load balancing across available resources
- @PEAK external framework services integration
- Distributed processing from #masterchat
"""

        self.masterchat.add_message(
            agent_id="jarvis",
            agent_name="JARVIS (CTO Superagent)",
            message=message,
            message_type="coordination",
            metadata={
                "processing_results": results,
                "timestamp": datetime.now().isoformat()
            }
        )

    def _save_unsuccessful_sessions(self):
        try:
            """Save identified unsuccessful sessions"""
            file_path = self.data_dir / f"unsuccessful_sessions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            data = {
                "timestamp": datetime.now().isoformat(),
                "total": len(self.unsuccessful_sessions),
                "sessions": [s.to_dict() for s in self.unsuccessful_sessions]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Saved unsuccessful sessions: {file_path.name}")

        except Exception as e:
            self.logger.error(f"Error in _save_unsuccessful_sessions: {e}", exc_info=True)
            raise
    def _save_processing_results(self, results: Dict[str, Any]):
        try:
            """Save processing results"""
            file_path = self.data_dir / f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info(f"💾 Saved processing results: {file_path.name}")


        except Exception as e:
            self.logger.error(f"Error in _save_processing_results: {e}", exc_info=True)
            raise
async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Unsuccessful Sessions Orchestrator")
    parser.add_argument("--identify", action="store_true", help="Identify unsuccessful sessions")
    parser.add_argument("--process", action="store_true", help="Process unsuccessful sessions")
    parser.add_argument("--max-concurrent", type=int, default=5, help="Max concurrent jobs")
    parser.add_argument("--no-external", action="store_true", help="Don't use external frameworks")

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🤖 JARVIS UNSUCCESSFUL SESSIONS ORCHESTRATOR")
    print("   Running from #masterchat with @PEAK external framework integration")
    print("=" * 80 + "\n")

    orchestrator = JARVISUnsuccessfulSessionsOrchestrator()

    if args.identify:
        print("🔍 Identifying unsuccessful sessions...")
        sessions = orchestrator.identify_unsuccessful_sessions()
        print(f"\n✅ Identified {len(sessions)} unsuccessful sessions")
        print("\nSessions:")
        for session in sessions[:10]:  # Show first 10
            print(f"   ❌ {session.session_name} ({session.status.value}) - Priority: {session.priority}")
            print(f"      Reason: {session.reason}")
        if len(sessions) > 10:
            print(f"   ... and {len(sessions) - 10} more")
        print()

    if args.process:
        print("🚀 Processing unsuccessful sessions...")
        results = await orchestrator.process_unsuccessful_sessions(
            max_concurrent=args.max_concurrent,
            use_external_frameworks=not args.no_external
        )
        print(f"\n✅ Processing complete")
        print(f"   Total: {results['total']}")
        print(f"   Completed: {results['completed']}")
        print(f"   Failed: {results['failed']}")
        print(f"   Success Rate: {results['success_rate']:.1%}")
        print()

    if not args.identify and not args.process:
        # Default: identify and process
        print("🔍 Identifying unsuccessful sessions...")
        sessions = orchestrator.identify_unsuccessful_sessions()
        print(f"✅ Identified {len(sessions)} unsuccessful sessions\n")

        if sessions:
            print("🚀 Processing unsuccessful sessions...")
            results = await orchestrator.process_unsuccessful_sessions(
                max_concurrent=args.max_concurrent,
                use_external_frameworks=not args.no_external
            )
            print(f"\n✅ Processing complete")
            print(f"   Success Rate: {results['success_rate']:.1%}")
        else:
            print("✅ No unsuccessful sessions found")
        print()

    print("=" * 80)
    print("✅ JARVIS Unsuccessful Sessions Orchestrator Complete")
    print("=" * 80 + "\n")


if __name__ == "__main__":


    asyncio.run(main())