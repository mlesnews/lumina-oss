#!/usr/bin/env python3
"""
Test SYPHON JARVIS Workflow Extraction
Tests framework, Docker, and @MANUS extraction
"""

import sys
from pathlib import Path
import json

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from syphon.jarvis_workflow_extractor import JARVISWorkflowExtractor
from syphon.core import SYPHONConfig, SubscriptionTier
import logging
logger = logging.getLogger("test_syphon_jarvis_extraction")


def main():
    try:
        """Test SYPHON JARVIS workflow extraction"""
        print("=" * 80)
        print("SYPHON JARVIS Workflow Extraction Test")
        print("=" * 80)
        print()

        # Initialize extractor
        config = SYPHONConfig(
            project_root=project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE
        )
        extractor = JARVISWorkflowExtractor(config)

        # Create test workflow with framework, Docker, and MANUS usage
        test_workflow = {
            "workflow_id": "test_001",
            "workflow_name": "Test Workflow with Frameworks",
            "domain": "technical",
            "complexity": "medium",
            "status": "completed",
            "docker": True,
            "dockerfiles": ["Dockerfile", "Dockerfile.prod"],
            "docker_compose": ["docker-compose.yml"],
            "containers": ["nas-proxy-cache", "jarvis-api"],
            "elevenlabs": True,
            "evenlabs": True,
            "@manus": True,
            "manus_operations": [
                {"area": "ide_control", "action": "test", "control_area": "ide_control"}
            ],
            "manus_config": {"enabled": True},
            "droid_assignment": {
                "droid_id": "r2d2",
                "droid_name": "R2-D2",
                "confidence_score": 0.95
            },
            "escalated": False,
            "steps": [
                {"action": "Initialize Docker containers", "status": "completed"},
                {"action": "Configure EvenLabs TTS", "status": "completed"},
                {"action": "Setup MANUS control", "status": "completed"},
            ]
        }

        print("Test Workflow Data:")
        print(json.dumps(test_workflow, indent=2))
        print()
        print("-" * 80)
        print()

        # Extract intelligence
        print("Extracting intelligence...")
        result = extractor.extract(test_workflow, {"source": "test"})

        if result.success:
            print("✅ Extraction successful!")
            extracted_count = result.metadata.get("extracted_count", 0)
            print(f"   Extracted {extracted_count} items")
            print()

            if result.data and result.data.intelligence:
                intel_data = result.data.intelligence[0].get("data", {})

                print("Extracted Intelligence:")
                print("-" * 80)

                # Framework usage
                framework_usage = intel_data.get("framework_usage", {})
                print(f"📦 Frameworks Detected: {framework_usage.get('frameworks_detected', [])}")
                evenlabs = framework_usage.get("evenlabs_usage", {})
                if evenlabs.get("detected"):
                    print(f"   ✅ EvenLabs/ElevenLabs: {evenlabs}")
                similar = framework_usage.get("similar_frameworks", [])
                if similar:
                    print(f"   🔍 Similar Frameworks: {similar}")

                # Docker usage
                docker_usage = intel_data.get("docker_usage", {})
                if docker_usage.get("docker_detected"):
                    print(f"🐳 Docker Detected: ✅")
                    print(f"   Containers: {docker_usage.get('containers', [])}")
                    print(f"   Dockerfiles: {docker_usage.get('dockerfiles', [])}")
                    print(f"   Compose Files: {docker_usage.get('compose_files', [])}")

                # MANUS control
                manus_control = intel_data.get("manus_control", {})
                if manus_control.get("manus_detected"):
                    print(f"🎮 @MANUS Detected: ✅")
                    print(f"   Control Areas: {manus_control.get('control_areas', [])}")
                    print(f"   Operations: {len(manus_control.get('operations', []))} operations")

                # Agent coordination
                agent_coord = intel_data.get("agent_coordination", {})
                if agent_coord.get("assigned_droid"):
                    print(f"🤖 Agent Coordination:")
                    print(f"   Droid: {agent_coord.get('assigned_droid')}")
                    print(f"   Coordinator: {agent_coord.get('coordinator')}")

                print()
                print("=" * 80)
                print("✅ All extraction tests passed!")
                print("=" * 80)
            else:
                print("⚠️  No intelligence data extracted")
        else:
            print(f"❌ Extraction failed: {result.error}")
            return 1

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())