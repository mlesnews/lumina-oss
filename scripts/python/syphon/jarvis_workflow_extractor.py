#!/usr/bin/env python3
"""
SYPHON JARVIS Workflow Extractor
Extracts intelligence from JARVIS workflows, agent coordination, and collaboration patterns

Extracts:
- Workflow execution patterns
- Agent coordination (C-3PO, droids, subagents)
- Collaboration patterns (@COLAB)
- Coordination patterns (@COOR)
- Subagent interactions under JARVIS CTO superagent
- Framework usage (#FRAMEWORKS, #EVENLABS, similar frameworks)
- Docker container/image/configuration usage (#DOCKER)
- @MANUS unified control system usage (@MANUS)

#SYPHON #JARVIS #WORKFLOWS #AGENTS #COORDINATION #COLLABORATION #CTO #FRAMEWORKS #DOCKER #EVENLABS #MANUS
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from syphon.models import SyphonData, DataSourceType, ExtractionResult
from syphon.extractors import BaseExtractor

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SYPHONJARVISWorkflowExtractor")


class JARVISWorkflowExtractor(BaseExtractor):
    """
    SYPHON extractor for JARVIS workflows, agent coordination, and collaboration patterns.

    Extracts intelligence from:
    - Workflow execution logs
    - Agent assignment patterns
    - Droid coordination (C-3PO)
    - Collaboration patterns (@COLAB)
    - Coordination patterns (@COOR)
    - Subagent interactions
    - Framework usage (#FRAMEWORKS, #EVENLABS, similar frameworks)
    - Docker containers, images, configurations (#DOCKER)
    - @MANUS unified control system (@MANUS)
    """

    def __init__(self, config):
        """Initialize JARVIS Workflow Extractor"""
        super().__init__(config)
        self.project_root = config.project_root
        self.data_dir = config.data_dir

        # Paths to JARVIS workflow data
        self.workflow_logs_dir = self.project_root / "data" / "workflow_logs"
        self.jarvis_intelligence_dir = self.project_root / "data" / "jarvis_intelligence"
        self.r5_sessions_dir = self.project_root / "data" / "r5_living_matrix" / "sessions"
        self.telemetry_dir = self.project_root / "data" / "telemetry"

        # Ensure directories exist
        for dir_path in [self.workflow_logs_dir, self.jarvis_intelligence_dir, 
                         self.r5_sessions_dir, self.telemetry_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def extract(self, content: Any, metadata: Dict[str, Any]) -> ExtractionResult:
        """
        Extract intelligence from JARVIS workflow content.

        Args:
            content: Workflow data (dict, JSON string, or file path)
            metadata: Additional metadata (source, timestamp, etc.)

        Returns:
            ExtractionResult with extracted intelligence
        """
        try:
            # Parse content
            if isinstance(content, str):
                # Check if it's a file path
                if Path(content).exists():
                    with open(content, 'r', encoding='utf-8') as f:
                        workflow_data = json.load(f)
                else:
                    # Try to parse as JSON
                    workflow_data = json.loads(content)
            elif isinstance(content, dict):
                workflow_data = content
            else:
                workflow_data = {"raw": str(content)}

            # Extract intelligence
            intelligence = {
                "workflow_patterns": self._extract_workflow_patterns(workflow_data),
                "agent_coordination": self._extract_agent_coordination(workflow_data),
                "collaboration_patterns": self._extract_collaboration_patterns(workflow_data),
                "coordination_patterns": self._extract_coordination_patterns(workflow_data),
                "subagent_interactions": self._extract_subagent_interactions(workflow_data),
                "jarvis_cto_insights": self._extract_jarvis_cto_insights(workflow_data),
                "framework_usage": self._extract_framework_usage(workflow_data),
                "docker_usage": self._extract_docker_usage(workflow_data),
                "manus_control": self._extract_manus_control(workflow_data),
            }

            # Extract actionable items
            actionable_items = self._extract_actionable_items_from_workflow(workflow_data)

            # Extract tasks
            tasks = self._extract_tasks_from_workflow(workflow_data)

            # Extract decisions
            decisions = self._extract_decisions_from_workflow(workflow_data)

            # Create SyphonData
            workflow_id = workflow_data.get("workflow_id", workflow_data.get("id", "unknown"))
            syphon_data = SyphonData(
                data_id=f"jarvis_workflow_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.WORKFLOW,
                source_id=workflow_id,
                content=json.dumps(workflow_data, indent=2),
                actionable_items=actionable_items,
                tasks=tasks,
                decisions=decisions,
                intelligence=[{"type": "workflow_intelligence", "data": intelligence}],
                metadata={
                    "extractor": "JARVISWorkflowExtractor",
                    "extraction_timestamp": datetime.now().isoformat(),
                    **metadata
                }
            )

            return ExtractionResult(
                success=True,
                data=syphon_data,
                metadata={"extracted_count": len(actionable_items) + len(tasks) + len(decisions)}
            )

        except Exception as e:
            logger.error(f"Error extracting JARVIS workflow intelligence: {e}", exc_info=True)
            return ExtractionResult(
                success=False,
                data=None,
                error=str(e),
                extracted_count=0
            )

    def _extract_workflow_patterns(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract workflow execution patterns"""
        patterns = {
            "workflow_name": workflow_data.get("workflow_name", "unknown"),
            "workflow_id": workflow_data.get("workflow_id", workflow_data.get("id", "unknown")),
            "execution_id": workflow_data.get("execution_id", "unknown"),
            "domain": workflow_data.get("domain", workflow_data.get("context", {}).get("domain", "unknown")),
            "complexity": workflow_data.get("complexity", workflow_data.get("context", {}).get("complexity", "unknown")),
            "status": workflow_data.get("status", "unknown"),
            "timestamp": workflow_data.get("timestamp", workflow_data.get("created_at", datetime.now().isoformat())),
            "execution_time": workflow_data.get("execution_time", workflow_data.get("duration", None)),
            "success": workflow_data.get("success", workflow_data.get("verified", False)),
            "steps": workflow_data.get("steps", []),
            "metrics": workflow_data.get("metrics", {}),
        }

        return patterns

    def _extract_agent_coordination(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract agent coordination patterns (C-3PO, droids, subagents)"""
        coordination = {
            "coordinator": "C-3PO",
            "assigned_droid": workflow_data.get("assigned_droid", workflow_data.get("droid_id", None)),
            "droid_assignment": workflow_data.get("droid_assignment", {}),
            "c3po_coordination": workflow_data.get("c3po_coordination", {}),
            "escalation_path": workflow_data.get("escalation_path", "C-3PO → JARVIS"),
            "escalated": workflow_data.get("escalated", False),
            "escalation_reason": workflow_data.get("escalation_reason", None),
            "verification_tasks": workflow_data.get("verification_tasks", []),
            "verification_status": workflow_data.get("verification_status", "unknown"),
        }

        # Extract droid-specific coordination
        if "droid_assignment" in workflow_data:
            droid_assignment = workflow_data["droid_assignment"]
            coordination.update({
                "droid_id": droid_assignment.get("droid_id"),
                "droid_name": droid_assignment.get("droid_name"),
                "confidence_score": droid_assignment.get("confidence_score"),
                "coordination_method": droid_assignment.get("coordination_method", "C-3PO assignment"),
            })

        return coordination

    def _extract_collaboration_patterns(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Extract collaboration patterns (@COLAB)"""
            collaboration = {
                "collaboration_detected": False,
                "collaborating_agents": [],
                "collaboration_type": None,
                "shared_resources": [],
                "communication_channels": [],
            }

            # Check for @COLAB tags
            content_str = json.dumps(workflow_data)
            if "@COLAB" in content_str or "collaboration" in content_str.lower():
                collaboration["collaboration_detected"] = True

            # Extract collaborating agents
            if "collaborating_agents" in workflow_data:
                collaboration["collaborating_agents"] = workflow_data["collaborating_agents"]

            # Extract collaboration metadata
            if "collaboration" in workflow_data:
                collab_data = workflow_data["collaboration"]
                collaboration.update({
                    "collaboration_type": collab_data.get("type", "unknown"),
                    "shared_resources": collab_data.get("shared_resources", []),
                    "communication_channels": collab_data.get("communication_channels", []),
                })

            return collaboration

        except Exception as e:
            self.logger.error(f"Error in _extract_collaboration_patterns: {e}", exc_info=True)
            raise
    def _extract_coordination_patterns(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Extract coordination patterns (@COOR)"""
            coordination = {
                "coordination_detected": False,
                "coordinating_agent": None,
                "coordinated_agents": [],
                "coordination_method": None,
                "coordination_timeline": [],
            }

            # Check for @COOR tags
            content_str = json.dumps(workflow_data)
            if "@COOR" in content_str or "coordination" in content_str.lower():
                coordination["coordination_detected"] = True

            # Extract coordination metadata
            if "coordination" in workflow_data:
                coord_data = workflow_data["coordination"]
                coordination.update({
                    "coordinating_agent": coord_data.get("coordinator", "C-3PO"),
                    "coordinated_agents": coord_data.get("agents", []),
                    "coordination_method": coord_data.get("method", "protocol-based"),
                    "coordination_timeline": coord_data.get("timeline", []),
                })

            # Extract from droid coordination
            if "droid_coordination" in workflow_data:
                droid_coord = workflow_data["droid_coordination"]
                coordination.update({
                    "coordinating_agent": droid_coord.get("primary_consultant", "C-3PO"),
                    "coordinated_agents": [
                        droid_coord.get("primary_consultant"),
                        droid_coord.get("technical_implementation"),
                        droid_coord.get("protocol_validation"),
                    ],
                })

            return coordination

        except Exception as e:
            self.logger.error(f"Error in _extract_coordination_patterns: {e}", exc_info=True)
            raise
    def _extract_subagent_interactions(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract subagent interactions under JARVIS CTO"""
        subagents = {
            "subagents_detected": [],
            "subagent_hierarchy": {},
            "interaction_patterns": [],
            "jarvis_supervision": False,
        }

        # Extract subagent information
        if "subagents" in workflow_data:
            subagents["subagents_detected"] = workflow_data["subagents"]

        # Extract from droid assignments (droids are subagents of C-3PO, who reports to JARVIS)
        if "droid_assignment" in workflow_data:
            droid_id = workflow_data["droid_assignment"].get("droid_id")
            if droid_id:
                subagents["subagents_detected"].append(droid_id)
                subagents["subagent_hierarchy"][droid_id] = {
                    "parent": "C-3PO",
                    "grandparent": "JARVIS",
                    "role": "droid_agent",
                }

        # Check for JARVIS supervision
        if "jarvis_escalation" in workflow_data or "escalated" in workflow_data:
            subagents["jarvis_supervision"] = True

        # Extract interaction patterns
        if "interactions" in workflow_data:
            subagents["interaction_patterns"] = workflow_data["interactions"]

        return subagents

    def _extract_jarvis_cto_insights(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Extract JARVIS CTO superagent insights"""
            insights = {
                "jarvis_involvement": False,
                "cto_decision_points": [],
                "strategic_insights": [],
                "escalation_insights": {},
            }

            # Check for JARVIS involvement
            content_str = json.dumps(workflow_data)
            if "JARVIS" in content_str or "jarvis" in content_str.lower():
                insights["jarvis_involvement"] = True

            # Extract escalation insights
            if "escalated" in workflow_data and workflow_data.get("escalated"):
                insights["escalation_insights"] = {
                    "escalated": True,
                    "reason": workflow_data.get("escalation_reason"),
                    "escalation_path": workflow_data.get("escalation_path", "C-3PO → JARVIS"),
                    "jarvis_response": workflow_data.get("jarvis_response"),
                }

            # Extract decision points
            if "decisions" in workflow_data:
                insights["cto_decision_points"] = workflow_data["decisions"]

            # Extract strategic insights
            if "insights" in workflow_data:
                insights["strategic_insights"] = workflow_data["insights"]

            return insights

        except Exception as e:
            self.logger.error(f"Error in _extract_jarvis_cto_insights: {e}", exc_info=True)
            raise
    def _extract_actionable_items_from_workflow(self, workflow_data: Dict[str, Any]) -> List[str]:
        try:
            """Extract actionable items from workflow"""
            actionable_items = []

            # Extract from workflow steps
            steps = workflow_data.get("steps", [])
            for step in steps:
                if isinstance(step, dict):
                    action = step.get("action", step.get("description", ""))
                    if action:
                        actionable_items.append(action)
                elif isinstance(step, str):
                    actionable_items.append(step)

            # Extract from verification tasks
            verification_tasks = workflow_data.get("verification_tasks", [])
            actionable_items.extend(verification_tasks)

            # Extract from escalation reasons
            if workflow_data.get("escalated"):
                escalation_reason = workflow_data.get("escalation_reason")
                if escalation_reason:
                    actionable_items.append(f"Escalation: {escalation_reason}")

            # Use base class method for text extraction
            content_str = json.dumps(workflow_data)
            base_actionable = self._extract_actionable_items(content_str, use_regex_tools=True)
            actionable_items.extend(base_actionable)

            return list(set(actionable_items))  # Remove duplicates

        except Exception as e:
            self.logger.error(f"Error in _extract_actionable_items_from_workflow: {e}", exc_info=True)
            raise
    def _extract_tasks_from_workflow(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tasks from workflow"""
        tasks = []

        # Extract from workflow steps
        steps = workflow_data.get("steps", [])
        for i, step in enumerate(steps):
            task = {
                "task_id": f"workflow_step_{i}",
                "description": step.get("action", step.get("description", str(step))),
                "status": step.get("status", "pending"),
                "assigned_to": step.get("assigned_droid", workflow_data.get("assigned_droid")),
            }
            tasks.append(task)

        # Extract from verification tasks
        verification_tasks = workflow_data.get("verification_tasks", [])
        for i, vtask in enumerate(verification_tasks):
            task = {
                "task_id": f"verification_task_{i}",
                "description": vtask if isinstance(vtask, str) else vtask.get("description", str(vtask)),
                "status": "pending",
                "assigned_to": workflow_data.get("assigned_droid"),
            }
            tasks.append(task)

        return tasks

    def _extract_decisions_from_workflow(self, workflow_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decisions from workflow"""
        decisions = []

        # Extract droid assignment decision
        if "droid_assignment" in workflow_data:
            droid_assignment = workflow_data["droid_assignment"]
            decision = {
                "decision_type": "droid_assignment",
                "decision": f"Assigned {droid_assignment.get('droid_name', 'unknown')} to workflow",
                "confidence": droid_assignment.get("confidence_score"),
                "decision_maker": "C-3PO",
            }
            decisions.append(decision)

        # Extract escalation decision
        if workflow_data.get("escalated"):
            decision = {
                "decision_type": "escalation",
                "decision": "Escalated to JARVIS",
                "reason": workflow_data.get("escalation_reason"),
                "decision_maker": "C-3PO",
            }
            decisions.append(decision)

        # Extract verification decision
        if "verification_status" in workflow_data:
            decision = {
                "decision_type": "verification",
                "decision": f"Verification {workflow_data.get('verification_status')}",
                "decision_maker": workflow_data.get("assigned_droid", "unknown"),
            }
            decisions.append(decision)

        return decisions

    def _extract_framework_usage(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract framework usage (#FRAMEWORKS, #EVENLABS, similar frameworks)"""
        frameworks = {
            "frameworks_detected": [],
            "evenlabs_usage": {},
            "similar_frameworks": [],
            "framework_details": {},
        }

        content_str = json.dumps(workflow_data, default=str).lower()
        content_full = json.dumps(workflow_data, default=str)

        # Detect EvenLabs/ElevenLabs (#EVENLABS)
        evenlabs_patterns = ["evenlabs", "elevenlabs", "eleven labs", "#evenlabs", "elevenlabs_", "elevenlabs."]
        if any(pattern in content_str for pattern in evenlabs_patterns):
            frameworks["frameworks_detected"].append("EvenLabs")
            frameworks["evenlabs_usage"] = {
                "detected": True,
                "tts_usage": "tts" in content_str or "text-to-speech" in content_str,
                "voice_synthesis": "voice" in content_str and ("synthesis" in content_str or "tts" in content_str),
                "api_integration": "api" in content_str and ("elevenlabs" in content_str or "evenlabs" in content_str),
                "jarvis_integration": "jarvis_elevenlabs" in content_str or "jarvis_evenlabs" in content_str,
            }

        # Find similar frameworks to EvenLabs (TTS, voice, AI frameworks)
        similar_keywords = ["openai", "anthropic", "cohere", "huggingface", "whisper", "tiktoken", "tts", "voice"]
        for keyword in similar_keywords:
            if keyword in content_str:
                frameworks["similar_frameworks"].append(keyword)

        # Extract framework metadata
        if "frameworks" in workflow_data:
            frameworks["framework_details"].update(workflow_data["frameworks"])

        return frameworks

    def _extract_docker_usage(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract Docker container/image/configuration usage (#DOCKER)"""
        docker_info = {
            "docker_detected": False,
            "containers": [],
            "images": [],
            "compose_files": [],
            "dockerfiles": [],
            "docker_config": {},
        }

        content_str = json.dumps(workflow_data, default=str)
        content_lower = content_str.lower()

        # Detect Docker usage
        docker_keywords = ["docker", "container", "dockerfile", "docker-compose", "#docker"]
        if any(keyword in content_lower for keyword in docker_keywords):
            docker_info["docker_detected"] = True

        # Extract container information
        if "containers" in workflow_data:
            docker_info["containers"] = workflow_data["containers"]
        elif "docker_containers" in workflow_data:
            docker_info["containers"] = workflow_data["docker_containers"]

        # Extract image information
        if "images" in workflow_data:
            docker_info["images"] = workflow_data["images"]
        elif "docker_images" in workflow_data:
            docker_info["images"] = workflow_data["docker_images"]

        # Extract compose file references
        compose_patterns = [
            r'docker-compose\.yml',
            r'docker-compose\.yaml',
            r'compose\.yml',
            r'compose\.yaml',
        ]
        for pattern in compose_patterns:
            matches = re.finditer(pattern, content_str, re.IGNORECASE)
            for match in matches:
                compose_file = match.group(0)
                if compose_file not in docker_info["compose_files"]:
                    docker_info["compose_files"].append(compose_file)

        # Extract Dockerfile references
        dockerfile_patterns = [
            r'Dockerfile',
            r'Dockerfile\.[\w-]+',
        ]
        for pattern in dockerfile_patterns:
            matches = re.finditer(pattern, content_str, re.IGNORECASE)
            for match in matches:
                dockerfile = match.group(0)
                if dockerfile not in docker_info["dockerfiles"]:
                    docker_info["dockerfiles"].append(dockerfile)

        # Extract Docker configuration
        if "docker_config" in workflow_data:
            docker_info["docker_config"] = workflow_data["docker_config"]
        elif "docker" in workflow_data:
            docker_info["docker_config"] = workflow_data["docker"]

        # Extract from execution results
        if "execution_result" in workflow_data:
            exec_result = workflow_data["execution_result"]
            if "docker" in exec_result:
                docker_info["docker_config"].update(exec_result["docker"])

        return docker_info

    def _extract_manus_control(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract @MANUS unified control system usage (@MANUS)"""
        manus_info = {
            "manus_detected": False,
            "control_areas": [],
            "operations": [],
            "control_results": [],
            "manus_config": {},
        }

        content_str = json.dumps(workflow_data, default=str)
        content_lower = content_str.lower()

        # Detect MANUS usage
        manus_keywords = ["@manus", "manus", "unified control", "manusunifiedcontrol", "manus_unified_control"]
        if any(keyword in content_lower for keyword in manus_keywords):
            manus_info["manus_detected"] = True

        # Extract control areas
        control_areas = [
            "ide_control",
            "workstation_control",
            "home_lab_infrastructure",
            "project_lumina_management",
            "automation_control",
            "data_management",
            "security_control",
            "rdp_capture",
        ]

        for area in control_areas:
            if area in content_lower or area.replace("_", " ") in content_lower:
                manus_info["control_areas"].append(area)

        # Extract MANUS operations
        if "manus_operations" in workflow_data:
            manus_info["operations"] = workflow_data["manus_operations"]
        elif "operations" in workflow_data:
            operations = workflow_data["operations"]
            if isinstance(operations, list):
                for op in operations:
                    if isinstance(op, dict) and ("manus" in str(op).lower() or "control" in str(op).lower()):
                        manus_info["operations"].append(op)

        # Extract control results
        if "manus_results" in workflow_data:
            manus_info["control_results"] = workflow_data["manus_results"]
        elif "control_results" in workflow_data:
            manus_info["control_results"] = workflow_data["control_results"]

        # Extract MANUS configuration
        if "manus_config" in workflow_data:
            manus_info["manus_config"] = workflow_data["manus_config"]
        elif "manus" in workflow_data:
            manus_info["manus_config"] = workflow_data["manus"]

        # Extract from execution results
        if "execution_result" in workflow_data:
            exec_result = workflow_data["execution_result"]
            if "manus" in exec_result:
                manus_info["manus_config"].update(exec_result["manus"])
            if "control_result" in exec_result:
                manus_info["control_results"].append(exec_result["control_result"])

        # Extract from verification results
        if "verification_results" in workflow_data:
            verify_results = workflow_data["verification_results"]
            if "manus" in verify_results:
                manus_info["manus_config"].update(verify_results["manus"])

        return manus_info
