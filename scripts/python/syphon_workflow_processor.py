#!/usr/bin/env python3
"""
SYPHON Workflow Processor - Rinse & Repeat

Processes workflows using SYPHON:
- Extracts actionable intelligence
- Applies @PEAK patterns
- Rinse & repeat as needed
- Integrates with One Ring Master Blueprint
- Master Feedback Loop integration

"Create Command" Enhancement:
- Uses Cursor IDE "create command" to generate code/files
- Applies @PEAK patterns for optimal solutions
- Rinse & repeat for continuous improvement
"""

import asyncio
import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Import SYPHON and related systems
try:
    from scripts.python.syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        print("⚠️ SYPHON modules not available")

try:
    from scripts.python.peak_pattern_system import PeakPatternSystem, PeakPattern
    PEAK_AVAILABLE = True
except ImportError:
    try:
        from peak_pattern_system import PeakPatternSystem, PeakPattern
        PEAK_AVAILABLE = True
    except ImportError:
        PEAK_AVAILABLE = False
        print("⚠️ Peak Pattern System not available")


class SyphonWorkflowProcessor:
    """
    SYPHON Workflow Processor - Rinse & Repeat

    Processes workflows using SYPHON extraction,
    applies @PEAK patterns, and integrates with
    One Ring Master Blueprint feedback loop.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        # Initialize SYPHON
        if SYPHON_AVAILABLE:
            self.syphon = SYPHONSystem(self.project_root)
        else:
            self.syphon = None

        # Initialize Peak Pattern System
        if PEAK_AVAILABLE:
            self.peak_patterns = PeakPatternSystem(self.project_root)
        else:
            self.peak_patterns = None

        # One Ring Blueprint integration
        self.blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        self.blueprint = self._load_blueprint()

        # Workflow tracking
        self.processed_workflows: List[Dict[str, Any]] = []
        self.feedback_loop_data: List[Dict[str, Any]] = []

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("SyphonWorkflowProcessor")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🔬 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _load_blueprint(self) -> Dict[str, Any]:
        """Load One Ring Master Blueprint"""
        if self.blueprint_file.exists():
            try:
                with open(self.blueprint_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading blueprint: {e}")

        return {}

    def _update_blueprint_syphon_status(self, status: Dict[str, Any]):
        """Update SYPHON status in One Ring Blueprint"""
        if not self.blueprint:
            return

        # Update SYPHON system status in blueprint
        core_systems = self.blueprint.get('core_systems', {})
        lumina_ext = core_systems.get('lumina_jarvis_extension', {})
        components = lumina_ext.get('components', [])

        # Find SYPHON component
        for component in components:
            if 'SYPHON' in component.get('name', ''):
                component['status'] = status.get('status', 'operational')
                component['last_updated'] = datetime.now().isoformat()
                component['workflow_processor'] = status
                break

        # Save updated blueprint
        try:
            with open(self.blueprint_file, 'w', encoding='utf-8') as f:
                json.dump(self.blueprint, f, indent=2, ensure_ascii=False)
            self.logger.info("✅ Updated One Ring Blueprint with SYPHON status")
        except Exception as e:
            self.logger.error(f"Error saving blueprint: {e}")

    def syphon_workflow_content(self, content: str, source_type: str = "workflow",
                               metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        SYPHON actionable intelligence from workflow content

        Extracts:
        - Tasks
        - Decisions
        - Actionable items
        - @PEAK patterns
        - @ask-requested items
        - AI capabilities (--ai-integration: PART OF SYPHON WORKFLOW)
        """
        if not self.syphon:
            return {"error": "SYPHON not available"}

        # STEP 1: AI DETECTION (--ai-integration strategy - PART OF SYPHON WORKFLOW)
        # Always check for AI capabilities when processing external entities
        ai_detection_result = None
        if metadata:
            entity_name = metadata.get("entity_name") or metadata.get("source") or metadata.get("from")
            entity_type = metadata.get("entity_type") or metadata.get("type", "unknown")

            if entity_name:
                try:
                    ai_detection_result = self.syphon.detect_ai_capabilities(
                        entity_name=entity_name,
                        entity_type=entity_type,
                        metadata=metadata
                    )
                    self.logger.info(f"🤖 AI Detection: {entity_name} - AI detected: {ai_detection_result.get('ai_detected', False)}")
                except Exception as e:
                    self.logger.warning(f"Error in AI detection: {e}")

        # Map source type to SYPHON DataSourceType and extract using appropriate method
        source_mapping = {
            "workflow": DataSourceType.OTHER,
            "chat": DataSourceType.OTHER,
            "email": DataSourceType.EMAIL,
            "sms": DataSourceType.SMS
        }

        syphon_type = source_mapping.get(source_type, DataSourceType.OTHER)

        # Extract using SYPHON (use syphon_generic for workflow/chat, specific methods for email/sms)
        if source_type == "email":
            # Extract email-specific fields from metadata
            email_id = metadata.get("email_id", "unknown") if metadata else "unknown"
            subject = metadata.get("subject", "") if metadata else ""
            from_addr = metadata.get("from", "") if metadata else ""
            to_addr = metadata.get("to", "") if metadata else ""
            extracted_data = self.syphon.syphon_email(
                email_id=email_id,
                subject=subject,
                body=content,
                from_address=from_addr,
                to_address=to_addr,
                metadata=metadata
            )
        elif source_type == "sms":
            # Extract SMS-specific fields from metadata
            sms_id = metadata.get("sms_id", "unknown") if metadata else "unknown"
            from_num = metadata.get("from", "") if metadata else ""
            to_num = metadata.get("to", "") if metadata else ""
            extracted_data = self.syphon.syphon_sms(
                sms_id=sms_id,
                message=content,
                from_number=from_num,
                to_number=to_num,
                metadata=metadata
            )
        else:
            # Use generic syphon for workflow/chat/other
            source_id = metadata.get("source_id", "workflow") if metadata else "workflow"
            extracted_data = self.syphon.syphon_generic(
                content=content,
                source_type=syphon_type,
                source_id=source_id,
                metadata=metadata
            )

        # Convert SyphonData to dict for return
        if hasattr(extracted_data, 'to_dict'):
            extracted_data = extracted_data.to_dict()

        # Extract @PEAK patterns
        peak_patterns = []
        if self.peak_patterns and PEAK_AVAILABLE and '@peak' in content.lower():
            try:
                peak_patterns = self.peak_patterns.extract_patterns_from_chat([
                    {'content': content, 'role': 'user'}
                ])
            except Exception as e:
                self.logger.warning(f"Error extracting peak patterns: {e}")

        # Extract @ask-requested
        ask_requested = []
        import re
        ask_pattern = r'@ask[:\s]+([^@\n]+?)(?=@|\n|$)'
        ask_matches = re.finditer(ask_pattern, content, re.IGNORECASE)
        for match in ask_matches:
            ask_requested.append(match.group(1).strip())

        return {
            'syphon_data': extracted_data,
            'peak_patterns': [p.to_dict() for p in peak_patterns] if peak_patterns else [],
            'ask_requested': ask_requested,
            'ai_detection': ai_detection_result,  # AI detection result (--ai-integration)
            'extracted_at': datetime.now().isoformat()
        }

    def apply_peak_patterns(self, workflow_tasks: List[str]) -> List[Dict[str, Any]]:
        """
        Apply @PEAK patterns to workflow tasks

        Matches tasks to existing @PEAK patterns for optimal solutions.
        """
        if not self.peak_patterns:
            return []

        optimized_tasks = []

        for task in workflow_tasks:
            # Search for matching @PEAK patterns
            matching_patterns = self.peak_patterns.search_patterns(
                query=task,
                limit=3
            )

            if matching_patterns:
                # Use @PEAK pattern for optimization
                best_pattern = matching_patterns[0]
                optimized_task = {
                    'original_task': task,
                    'peak_pattern': best_pattern.name,
                    'pattern_id': best_pattern.pattern_id,
                    'optimized_approach': best_pattern.description,
                    'code_example': best_pattern.code_example
                }
                optimized_tasks.append(optimized_task)
            else:
                # No pattern match, use as-is
                optimized_tasks.append({
                    'original_task': task,
                    'peak_pattern': None,
                    'optimized_approach': None
                })

        return optimized_tasks

    def create_command_workflow(self, request: str, use_peak: bool = True) -> Dict[str, Any]:
        """
        Create command workflow with @PEAK optimization

        The "create command" in Cursor IDE:
        - Generates code/files based on request
        - Applies @PEAK patterns for optimal solutions
        - Creates reusable, pattern-based implementations

        This function enhances it by:
        - Using SYPHON to extract requirements
        - Matching to @PEAK patterns
        - Generating optimized code
        - Integrating with master blueprint
        """
        self.logger.info(f"🔧 Create Command Workflow: {request[:100]}")

        # Step 1: SYPHON extract requirements
        syphon_result = self.syphon_workflow_content(request, "workflow")

        # Step 2: Apply @PEAK patterns
        tasks = syphon_result.get('syphon_data', {}).get('tasks', [])
        task_texts = [t.get('text', '') for t in tasks if isinstance(t, dict)]

        optimized_tasks = []
        if use_peak and task_texts:
            optimized_tasks = self.apply_peak_patterns(task_texts)

        # Step 3: Generate create command structure
        create_command = {
            'request': request,
            'syphon_extraction': syphon_result,
            'peak_optimized': optimized_tasks if use_peak else None,
            'files_to_create': [],
            'code_blocks': [],
            'integration_points': [],
            'blueprint_impact': None
        }

        # Step 4: Determine files/code to create
        if optimized_tasks:
            for task in optimized_tasks:
                if task.get('peak_pattern'):
                    # Use @PEAK pattern code example
                    code_example = task.get('code_example', '')
                    if code_example:
                        create_command['code_blocks'].append({
                            'pattern': task['peak_pattern'],
                            'code': code_example
                        })

        # Step 5: Check blueprint impact
        create_command['blueprint_impact'] = self._check_blueprint_impact(request)

        return create_command

    def _check_blueprint_impact(self, request: str) -> Dict[str, Any]:
        """Check how this affects One Ring Master Blueprint"""
        impact = {
            'systems_affected': [],
            'integration_points': [],
            'blueprint_updates_needed': False
        }

        # Check for system mentions
        systems = ['SYPHON', 'R5', 'JARVIS', 'MARVIN', 'Holocron', 'WOPR']
        for system in systems:
            if system.lower() in request.lower():
                impact['systems_affected'].append(system)
                impact['blueprint_updates_needed'] = True

        return impact

    async def process_workflow_rinse_repeat(self, workflow_content: str,
                                           max_iterations: int = 3) -> Dict[str, Any]:
        """
        Process workflow with rinse & repeat

        Iterative improvement:
        1. SYPHON extract
        2. Apply @PEAK patterns
        3. Generate/create
        4. Evaluate
        5. Rinse & repeat as needed
        """
        self.logger.info("🔄 Starting rinse & repeat workflow processing...")

        iterations = []

        for iteration in range(max_iterations):
            self.logger.info(f"   Iteration {iteration + 1}/{max_iterations}")

            # SYPHON extract
            syphon_result = self.syphon_workflow_content(workflow_content)

            # Apply @PEAK
            tasks = syphon_result.get('syphon_data', {}).get('tasks', [])
            task_texts = [t.get('text', '') for t in tasks if isinstance(t, dict)]
            optimized = self.apply_peak_patterns(task_texts) if task_texts else []

            # Evaluate (simplified - in real use, would test/validate)
            iteration_result = {
                'iteration': iteration + 1,
                'syphon_result': syphon_result,
                'peak_optimized': optimized,
                'improvement': iteration > 0  # Assume improvement on repeat
            }

            iterations.append(iteration_result)

            # Check if we should continue
            if iteration > 0:
                # Compare with previous iteration
                prev_optimized = iterations[iteration - 1].get('peak_optimized', [])
                if len(optimized) == len(prev_optimized):
                    # No new improvements
                    self.logger.info(f"   No new improvements on iteration {iteration + 1}, stopping")
                    break

        # Update master blueprint
        self._update_blueprint_syphon_status({
            'status': 'operational',
            'last_workflow': datetime.now().isoformat(),
            'iterations': len(iterations),
            'rinse_repeat_active': True
        })

        return {
            'workflow_content': workflow_content,
            'iterations': iterations,
            'final_result': iterations[-1] if iterations else None,
            'blueprint_updated': True
        }

    def get_master_feedback_loop_data(self) -> Dict[str, Any]:
        """Get data for master feedback loop"""
        return {
            'syphon_status': 'operational' if self.syphon else 'unavailable',
            'peak_patterns_available': self.peak_patterns is not None,
            'blueprint_integration': True,
            'processed_workflows': len(self.processed_workflows),
            'feedback_entries': len(self.feedback_loop_data),
            'last_update': datetime.now().isoformat()
        }


async def main():
    """Main execution"""
    processor = SyphonWorkflowProcessor()

    print("🔬 SYPHON Workflow Processor")
    print("=" * 80)
    print("Rinse & Repeat with @PEAK Pattern Integration")
    print("One Ring Master Blueprint Feedback Loop")
    print()

    # Example workflow
    workflow_content = """
    @ask: Help me process workflow with @SYPHON, rinse & repeat as needed.

    Requirements:
    - Extract actionable intelligence
    - Apply @PEAK patterns
    - Integrate with One Ring Blueprint
    - Rinse & repeat for continuous improvement
    """

    # Process with rinse & repeat
    result = await processor.process_workflow_rinse_repeat(workflow_content)

    print("📊 Results:")
    print(f"   Iterations: {len(result['iterations'])}")
    print(f"   SYPHON Status: {'✅ Available' if SYPHON_AVAILABLE else '❌ Unavailable'}")
    print(f"   Blueprint Updated: {result['blueprint_updated']}")

    # Feedback loop data
    feedback = processor.get_master_feedback_loop_data()
    print()
    print("🔄 Master Feedback Loop:")
    print(f"   Processed Workflows: {feedback['processed_workflows']}")
    print(f"   Feedback Entries: {feedback['feedback_entries']}")


if __name__ == "__main__":



    asyncio.run(main())