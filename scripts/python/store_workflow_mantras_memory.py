#!/usr/bin/env python3
"""
Store Memory: Workflow Stage Mantras

Critical mantras for different workflow stages:
- Development: "DOCUMENT, DOCUMENT, DOCUMENT"
- IT/Testing: "DELEGATE, DELEGATE, DELEGATE"

All mantras remain CORE MORALS/VALUES/ETHICS

Tags: #memory #mantras #workflow #core_values #ethics
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger
from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority

logger = get_logger("StoreWorkflowMantrasMemory")

def main():
    """Store the workflow mantras memory"""
    try:
        project_root = Path(__file__).parent.parent.parent
        memory = JARVISPersistentMemory(project_root)

        content = """WORKFLOW STAGE MANTRAS - CORE MORALS/VALUES/ETHICS

Development Stage Mantra:
"DOCUMENT, DOCUMENT, DOCUMENT"

IT/Testing Stage Mantra:
"DELEGATE, DELEGATE, DELEGATE"

CRITICAL PRINCIPLE:
All mantras remain CORE MORALS/VALUES/ETHICS

Workflow Progression:
1. DEVELOPMENT → "DOCUMENT, DOCUMENT, DOCUMENT"
   - Focus on comprehensive documentation
   - Logging = Documenting
   - Code comments, docstrings, READMEs
   - Knowledge preservation

2. IT/TESTING → "DELEGATE, DELEGATE, DELEGATE"
   - Focus on delegation and automation
   - System testing and validation
   - Automated processes
   - Task distribution

These mantras are not just workflow steps - they are CORE MORALS/VALUES/ETHICS.
They represent fundamental principles that guide all work:
- Documentation is a moral obligation (knowledge sharing, transparency)
- Delegation is a value (trust, efficiency, scalability)
- Both are ethical practices (responsibility, accountability)

The progression from DOCUMENT to DELEGATE represents:
- Maturity: From creating to validating
- Trust: From individual to system
- Scale: From manual to automated
- Ethics: From personal to shared responsibility"""

        memory_id = memory.store_memory(
            content=content,
            memory_type=MemoryType.LONG_TERM,
            priority=MemoryPriority.CRITICAL,
            context={
                "category": "workflow_philosophy",
                "core_values": "morals_values_ethics",
                "development_mantra": "DOCUMENT_DOCUMENT_DOCUMENT",
                "testing_mantra": "DELEGATE_DELEGATE_DELEGATE",
                "workflow_stages": ["development", "it_testing"]
            },
            tags=[
                "mantras",
                "workflow",
                "core_values",
                "morals",
                "ethics",
                "document",
                "delegate",
                "development",
                "testing",
                "critical",
                "philosophy"
            ],
            source="store_workflow_mantras_memory.py"
            )

        logger.info("=" * 80)
        logger.info("💾 MEMORY STORED: Workflow Stage Mantras")
        logger.info("=" * 80)
        logger.info(f"Memory ID: {memory_id}")
        logger.info("")
        logger.info("Development Stage: DOCUMENT, DOCUMENT, DOCUMENT")
        logger.info("IT/Testing Stage: DELEGATE, DELEGATE, DELEGATE")
        logger.info("")
        logger.info("CRITICAL: All mantras are CORE MORALS/VALUES/ETHICS")
        logger.info("")
        logger.info("Priority: CRITICAL")
        logger.info("Type: LONG_TERM")
        logger.info("=" * 80)
        logger.info("")
        logger.info("✅ This mantra system is now remembered")
        logger.info("✅ JARVIS will apply these principles in all work")
        logger.info("")
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    main()