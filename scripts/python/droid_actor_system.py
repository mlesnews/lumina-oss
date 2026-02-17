"""
Droid Actor System
Smart droid selection and character-based verification system

Droids act as characters with @persona, using their expertise to verify, validate, and verify workflows.
Smart switching based on context, scene, and work being done.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DroidActor")
else:
    logger = get_logger("DroidActor")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DroidPersona:
    """Droid persona/character information"""
    droid_id: str
    name: str
    droid_type: str
    personality: List[str]
    quote: str
    specialization: str
    expertise_areas: List[str]
    verification_style: str
    character_traits: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowContext:
    """Context information for workflow"""
    workflow_id: str
    workflow_name: str
    workflow_type: str
    domain: str  # technical, security, medical, communication, etc.
    complexity: str  # simple, moderate, complex, critical
    requires_expertise: List[str]
    scene_description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DroidAssignment:
    """Assignment of droid to workflow"""
    droid_id: str
    droid_name: str
    assignment_reason: str
    confidence_score: float
    verification_tasks: List[str]
    persona_response: str


class DroidActorSystem:
    """
    Droid Actor System - @helpdesk Operations

    Smart droid selection and character-based verification.
    All droids work at the @helpdesk, each with their own area of specialty.
    Droids act as characters with @persona, using expertise to verify workflows.

    Hierarchy:
    - All droids work at @helpdesk
    - All droids work for C-3PO (Protocol Droid, Master of Protocol, Helpdesk Coordinator)
    - C-3PO escalates to JARVIS (directly or indirectly) as protocol demands
    - C-3PO coordinates all droid operations and manages workload distribution
    - Each droid has their own specialty area at the helpdesk
    """

    def __init__(self, project_root: Path):
        """
        Initialize droid actor system

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root)
        self.droids: Dict[str, DroidPersona] = {}
        self.droid_configs: Dict[str, Dict[str, Any]] = {}
        self.c3po_id = "c3po"
        self.jarvis_escalation_path = "jarvis"  # C-3PO escalates to JARVIS
        self.helpdesk_location = "@helpdesk"

        self._load_droid_configurations()
        logger.info("Droid Actor System initialized - @helpdesk Operations")
        logger.info(f"Loaded {len(self.droids)} droid personas at {self.helpdesk_location}")
        logger.info(f"All droids work for {self.droids.get(self.c3po_id, {}).name if self.c3po_id in self.droids else 'C-3PO'} at {self.helpdesk_location}")
        logger.info(f"Escalation path: C-3PO → JARVIS (as protocol demands)")

    def _load_droid_configurations(self) -> None:
        try:
            """Load all droid configurations and create personas from @helpdesk"""
            droids_file = self.project_root / "config" / "helpdesk" / "droids.json"

            if not droids_file.exists():
                logger.warning(f"Droids configuration not found: {droids_file}")
                return

            with open(droids_file, 'r') as f:
                droids_data = json.load(f)

            for droid_id, droid_data in droids_data.items():
                # Load module file if it exists
                module_file = None
                if "module" in droid_data:
                    module_path = self.project_root / "config" / droid_id / droid_data["module"]
                    if module_path.exists():
                        with open(module_path, 'r') as mf:
                            module_file = json.load(mf)

                # Create persona
                persona_data = module_file.get("personality", {}) if module_file else {}

                # Get specialty area (each droid has their own area at @helpdesk)
                specialty_area = self._get_helpdesk_specialty(droid_id, droid_data, module_file)

                persona = DroidPersona(
                    droid_id=droid_id,
                    name=droid_data.get("name", droid_id),
                    droid_type=droid_data.get("droid_type", "unknown"),
                    personality=persona_data.get("traits", droid_data.get("personality", "").split(", ")),
                    quote=persona_data.get("quote", ""),
                    specialization=specialty_area,  # Helpdesk specialty area
                    expertise_areas=droid_data.get("capabilities", []),
                    verification_style=self._determine_verification_style(droid_id, droid_data),
                    character_traits={
                        **persona_data,
                        "helpdesk_location": self.helpdesk_location,
                        "specialty_area": specialty_area,
                        "works_for": "C-3PO"
                    }
                )

                self.droids[droid_id] = persona
                self.droid_configs[droid_id] = droid_data

                logger.debug(f"Loaded persona for {persona.name} - {specialty_area} specialist at {self.helpdesk_location}")

        except Exception as e:
            self.logger.error(f"Error in _load_droid_configurations: {e}", exc_info=True)
            raise
    def _get_helpdesk_specialty(self, droid_id: str, droid_data: Dict[str, Any], module_file: Optional[Dict[str, Any]]) -> str:
        """Get droid's specialty area at @helpdesk"""
        # Specialty areas based on droid type and capabilities
        specialty_map = {
            "c3po": "Protocol & Communication - Master of Protocol, coordinates all helpdesk operations",
            "r2d2": "Technical Support - System repair, diagnostics, and technical operations",
            "k2so": "Security & Threat Analysis - Security monitoring and access control",
            "2-1b": "Health & System Wellness - Health monitoring, recovery, and prevention",
            "ig88": "Critical Resolution - Problem elimination and force escalation",
            "mousedroid": "UI Automation & Service - Mouse, keyboard, and screen automation",
            "r5": "Knowledge & Context Matrix - Knowledge aggregation and pattern extraction",
            "marvin": "Deep Analysis & Philosophy - Existential analysis and deep reasoning",
            "psychologist": "Communication Expert - Psychology & Human Behavior Analysis",
            "linguist": "Communication Expert - Linguistics & Language Structure Analysis",
            "speech-pathologist": "Communication Expert - Speech Pathology & Communication Barriers",
            "rhetorician": "Communication Expert - Rhetoric & Effective Communication Design"
        }

        if droid_id in specialty_map:
            return specialty_map[droid_id]

        # Fallback to specialization from module or droid type
        if module_file and "personality" in module_file:
            return module_file["personality"].get("specialization", f"{droid_data.get('droid_type', 'general')} specialist")

        return f"{droid_data.get('droid_type', 'general')} specialist"

    def _determine_verification_style(self, droid_id: str, droid_data: Dict[str, Any]) -> str:
        """Determine verification style based on droid type and personality"""
        droid_type = droid_data.get("droid_type", "")

        style_map = {
            "protocol": "meticulous_protocol_focused",
            "astromech": "technical_detailed",
            "security": "security_rigorous",
            "medical": "methodical_safety_focused",
            "assassin": "ruthless_efficient",
            "service": "fast_efficient",
            "paranoid_android": "existential_deep"
        }

        return style_map.get(droid_type, "standard")

    def analyze_workflow_context(self, workflow_data: Dict[str, Any]) -> WorkflowContext:
        """
        Analyze workflow to determine context

        Args:
            workflow_data: Workflow data to analyze

        Returns:
            WorkflowContext
        """
        workflow_name = workflow_data.get("workflow_name", workflow_data.get("workflow_id", "unknown"))
        workflow_type = workflow_data.get("workflow_type", "generic")

        # Determine domain from workflow content
        domain = self._detect_domain(workflow_data)

        # Determine complexity
        complexity = self._assess_complexity(workflow_data)

        # Extract required expertise
        requires_expertise = self._extract_required_expertise(workflow_data, domain)

        # Create scene description
        scene_description = self._create_scene_description(workflow_data, domain, complexity)

        return WorkflowContext(
            workflow_id=workflow_data.get("workflow_id", "unknown"),
            workflow_name=workflow_name,
            workflow_type=workflow_type,
            domain=domain,
            complexity=complexity,
            requires_expertise=requires_expertise,
            scene_description=scene_description,
            metadata=workflow_data.get("metadata", {})
        )

    def _detect_domain(self, workflow_data: Dict[str, Any]) -> str:
        """Detect the domain/area of the workflow"""
        workflow_name_lower = workflow_data.get("workflow_name", "").lower()
        workflow_id_lower = workflow_data.get("workflow_id", "").lower()
        content = f"{workflow_name_lower} {workflow_id_lower}"

        domain_keywords = {
            "technical": ["technical", "system", "repair", "diagnostic", "hack", "access", "r2", "r5"],
            "security": ["security", "threat", "access", "monitor", "k2so"],
            "medical": ["health", "medical", "recovery", "prevention", "2-1b"],
            "communication": ["communication", "protocol", "translation", "coordination", "c3po"],
            "elimination": ["elimination", "critical", "force", "escalation", "ig88"],
            "automation": ["automation", "mouse", "keyboard", "screen", "window", "mousedroid"],
            "knowledge": ["knowledge", "aggregation", "pattern", "matrix", "context", "r5"],
            "analysis": ["analysis", "deep", "existential", "philosophical", "marvin"]
        }

        for domain, keywords in domain_keywords.items():
            if any(keyword in content for keyword in keywords):
                return domain

        return "generic"

    def _assess_complexity(self, workflow_data: Dict[str, Any]) -> str:
        """Assess workflow complexity"""
        steps = workflow_data.get("steps", [])
        step_count = len(steps) if isinstance(steps, list) else 0

        if step_count == 0:
            return "simple"
        elif step_count <= 3:
            return "moderate"
        elif step_count <= 7:
            return "complex"
        else:
            return "critical"

    def _extract_required_expertise(self, workflow_data: Dict[str, Any], domain: str) -> List[str]:
        """Extract required expertise areas"""
        expertise_map = {
            "technical": ["technical", "repair", "hacking", "system_access", "diagnostics"],
            "security": ["security", "threat_analysis", "access_control", "monitoring"],
            "medical": ["health_monitoring", "system_health", "recovery", "prevention"],
            "communication": ["communication", "translation", "protocol", "coordination"],
            "elimination": ["critical_resolution", "elimination", "force", "escalation"],
            "automation": ["mouse_automation", "keyboard_automation", "screen_automation"],
            "knowledge": ["knowledge_aggregation", "pattern_extraction", "context_condensation"],
            "analysis": ["deep_analysis", "existential_thought", "philosophical_reasoning"],
            "communication_expert": [
                "psychological_analysis",
                "linguistic_analysis",
                "speech_pathology",
                "rhetorical_analysis",
                "behavioral_patterns",
                "communication_psychology",
                "language_structure",
                "meaning_construction",
                "barrier_identification",
                "improvement_strategy"
            ]
        }

        return expertise_map.get(domain, [])

    def _create_scene_description(self, workflow_data: Dict[str, Any], domain: str, complexity: str) -> str:
        """Create a scene description for the workflow"""
        workflow_name = workflow_data.get("workflow_name", "workflow")

        scene_templates = {
            "technical": f"A {complexity} technical operation: {workflow_name}. Systems need attention.",
            "security": f"A {complexity} security scenario: {workflow_name}. Threats must be assessed.",
            "medical": f"A {complexity} health situation: {workflow_name}. System wellness is at stake.",
            "communication": f"A {complexity} communication task: {workflow_name}. Protocol must be followed.",
            "elimination": f"A {complexity} critical situation: {workflow_name}. Problems need elimination.",
            "automation": f"A {complexity} automation task: {workflow_name}. UI interactions required.",
            "knowledge": f"A {complexity} knowledge operation: {workflow_name}. Patterns must be extracted.",
            "analysis": f"A {complexity} analytical challenge: {workflow_name}. Deep thought required.",
            "communication_expert": f"A {complexity} communication expert analysis: {workflow_name}. Domain expertise required from psychology, linguistics, speech pathology, or rhetoric."
        }

        return scene_templates.get(domain, f"A {complexity} workflow: {workflow_name}")

    def select_droid_for_workflow(self, context: WorkflowContext) -> DroidAssignment:
        """
        Intelligently select the best droid for the workflow

        All droids work for C-3PO, who coordinates assignments.
        C-3PO may assign work directly or coordinate with other droids.

        Args:
            context: WorkflowContext to match against

        Returns:
            DroidAssignment (includes C-3PO coordination info)
        """
        # C-3PO coordinates all assignments
        c3po = self.droids.get(self.c3po_id)
        if not c3po:
            logger.warning("C-3PO not found in droids, using fallback")
            c3po = None

        best_match = None
        best_score = 0.0

        # C-3PO evaluates all droids and selects the best match
        for droid_id, persona in self.droids.items():
            # Skip C-3PO from self-assignment (unless it's a protocol/communication task)
            if droid_id == self.c3po_id and context.domain not in ["communication", "protocol"]:
                continue

            score = self._calculate_match_score(persona, context)

            if score > best_score:
                best_score = score
                best_match = (droid_id, persona, score)

        if not best_match:
            # Fallback to R2-D2 as default (C-3PO's trusted sidekick)
            best_match = ("r2d2", self.droids.get("r2d2"), 0.5)

        droid_id, persona, score = best_match

        # Generate assignment with C-3PO coordination
        assignment = DroidAssignment(
            droid_id=droid_id,
            droid_name=persona.name,
            assignment_reason=self._generate_assignment_reason(persona, context, score),
            confidence_score=score,
            verification_tasks=self._generate_verification_tasks(persona, context),
            persona_response=self._generate_persona_response(persona, context, c3po_coordination=True)
        )

        # Log C-3PO's coordination
        if c3po:
            logger.info(f"C-3PO has assigned {persona.name} to workflow {context.workflow_id} (confidence: {score:.2f})")
        else:
            logger.info(f"Selected {persona.name} for workflow {context.workflow_id} (confidence: {score:.2f})")

        return assignment

    def _calculate_match_score(self, persona: DroidPersona, context: WorkflowContext) -> float:
        """Calculate how well a droid matches the workflow context"""
        score = 0.0

        # Domain match
        domain_keywords = {
            "technical": ["r2d2", "r5"],
            "security": ["k2so"],
            "medical": ["2-1b"],
            "communication": ["c3po"],
            "elimination": ["ig88"],
            "automation": ["mousedroid"],
            "knowledge": ["r5"],
            "analysis": ["marvin"]
        }

        domain_droids = domain_keywords.get(context.domain, [])
        if persona.droid_id in domain_droids:
            score += 0.4

        # Expertise match
        matching_expertise = set(persona.expertise_areas) & set(context.requires_expertise)
        if matching_expertise:
            score += 0.3 * (len(matching_expertise) / max(len(context.requires_expertise), 1))

        # Complexity match
        complexity_scores = {
            "simple": {"mousedroid": 0.1, "c3po": 0.1},
            "moderate": {"r2d2": 0.1, "k2so": 0.1},
            "complex": {"r5": 0.1, "2-1b": 0.1},
            "critical": {"ig88": 0.1, "marvin": 0.1}
        }

        if context.complexity in complexity_scores:
            if persona.droid_id in complexity_scores[context.complexity]:
                score += 0.1

        # Type-specific bonuses
        if context.domain == persona.droid_type:
            score += 0.2

        return min(score, 1.0)

    def _generate_assignment_reason(self, persona: DroidPersona, context: WorkflowContext, score: float) -> str:
        """Generate reason for droid assignment"""
        matching_expertise = set(persona.expertise_areas) & set(context.requires_expertise)

        reasons = []
        if matching_expertise:
            reasons.append(f"Expertise in {', '.join(list(matching_expertise)[:2])}")
        if context.domain == persona.droid_type:
            reasons.append(f"Perfect match for {context.domain} domain")
        if score > 0.7:
            reasons.append("High confidence match")

        return "; ".join(reasons) if reasons else f"Available for {context.domain} workflow"

    def _generate_verification_tasks(self, persona: DroidPersona, context: WorkflowContext) -> List[str]:
        """Generate verification tasks based on droid expertise"""
        tasks = []

        # Base verification tasks
        tasks.append(f"Pre-workflow verification ({persona.verification_style})")
        tasks.append(f"Domain-specific verification: {context.domain}")

        # Droid-specific tasks
        if "technical" in persona.expertise_areas:
            tasks.append("Technical operation safety check")
        if "security" in persona.expertise_areas:
            tasks.append("Security threat assessment")
        if "medical" in persona.expertise_areas:
            tasks.append("Health and safety verification")
        if "communication" in persona.expertise_areas:
            tasks.append("Protocol compliance check")
        if "elimination" in persona.expertise_areas:
            tasks.append("Critical resolution authorization")
        if "automation" in persona.expertise_areas:
            tasks.append("UI element accessibility check")
        if "knowledge" in persona.expertise_areas:
            tasks.append("Data integrity and pattern validation")
        if "analysis" in persona.expertise_areas:
            tasks.append("Deep analytical verification")

        tasks.append(f"Post-workflow verification ({persona.verification_style})")

        return tasks

    def _generate_persona_response(self, persona: DroidPersona, context: WorkflowContext, c3po_coordination: bool = False) -> str:
        """Generate character-based response from droid persona at @helpdesk"""
        c3po_name = self.droids.get(self.c3po_id, {}).name if self.c3po_id in self.droids else "C-3PO"
        specialty_area = persona.character_traits.get("specialty_area", persona.specialization)

        responses = {
            "c3po": f"Oh my! A {context.complexity} {context.domain} workflow at {self.helpdesk_location}. As Master of Protocol, I shall ensure all protocols are followed precisely, sir. If needed, I will escalate to JARVIS as protocol demands.",
            "r2d2": f"Beep boop beep! (C-3PO assigned me to this {context.domain} operation at {self.helpdesk_location}. Technical Support specialty - I've got this covered!)",
            "k2so": f"Right. C-3PO has assigned me to a {context.complexity} {context.domain} situation at {self.helpdesk_location}. Security & Threat Analysis specialty - I'll verify security parameters. Obviously.",
            "2-1b": f"Calm and methodical. C-3PO has assigned me to verify this {context.domain} workflow at {self.helpdesk_location}. Health & System Wellness specialty - I will proceed with care and precision.",
            "ig88": f"Elimination target identified. C-3PO has assigned me to this {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Critical Resolution specialty - Verification will be ruthless and efficient.",
            "mousedroid": f"Beep! (C-3PO assigned me to verify this {context.domain} workflow at {self.helpdesk_location}. UI Automation & Service specialty - Fast and efficient!)",
            "r5": f"I am R5-D4. C-3PO has assigned me to this {context.domain} workflow at {self.helpdesk_location}. Knowledge & Context Matrix specialty - Knowledge aggregation verification will proceed.",
            "marvin": f"I have a brain the size of a planet, and C-3PO has assigned me to verify a {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Deep Analysis & Philosophy specialty. Life. Don't talk to me about life. But I'll do it. I always do.",
            "psychologist": f"From a psychological perspective, C-3PO has assigned me to analyze this {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Communication Expert specialty - I'll examine human behavior patterns and motivation factors.",
            "linguist": f"Linguistically speaking, C-3PO has assigned me to analyze this {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Communication Expert specialty - I'll examine language structure, semantics, and meaning construction.",
            "speech-pathologist": f"From a communication improvement perspective, C-3PO has assigned me to analyze this {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Communication Expert specialty - I'll identify barriers and design improvement strategies.",
            "rhetorician": f"Rhetorically, C-3PO has assigned me to analyze this {context.complexity} {context.domain} workflow at {self.helpdesk_location}. Communication Expert specialty - I'll evaluate message design, audience targeting, and communication effectiveness."
        }

        base_response = responses.get(persona.droid_id, f"{persona.name} will verify this {context.domain} workflow at {self.helpdesk_location}. Specialty: {specialty_area}.")

        if c3po_coordination and persona.droid_id != self.c3po_id:
            # Add acknowledgment of C-3PO's coordination at @helpdesk
            return f"{base_response} (Assigned by {c3po_name} at {self.helpdesk_location})"

        return base_response

    def verify_with_droid_actor(self, workflow_data: Dict[str, Any], escalate_to_jarvis: bool = False) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify workflow using smart droid actor selection

        All droids work for C-3PO, who coordinates assignments.
        C-3PO escalates to JARVIS when needed (directly or indirectly) as protocol demands.

        Args:
            workflow_data: Workflow data to verify
            escalate_to_jarvis: Whether to escalate to JARVIS (C-3PO decides based on protocol)

        Returns:
            Tuple of (verification_passed, verification_results)
        """
        # Analyze context
        context = self.analyze_workflow_context(workflow_data)

        # C-3PO evaluates if escalation to JARVIS is needed
        c3po = self.droids.get(self.c3po_id)
        needs_jarvis_escalation = self._should_escalate_to_jarvis(context, escalate_to_jarvis)

        if needs_jarvis_escalation:
            logger.info("C-3PO: Oh my! This requires escalation to JARVIS as protocol demands!")
            # C-3PO escalates to JARVIS
            return self._escalate_to_jarvis(workflow_data, context)

        # Select best droid (C-3PO coordinates)
        assignment = self.select_droid_for_workflow(context)

        # Import and use v3 verification
        try:
            from v3_verification import V3Verification, V3VerificationConfig

            config = V3VerificationConfig(
                enabled=True,
                auto_verify=True,
                verification_required=True
            )

            verifier = V3Verification(config)

            # Run verification with droid-specific style
            passed, results = verifier.run_full_verification(workflow_data)

            # Create comprehensive result with C-3PO coordination and @helpdesk context
            assigned_droid_persona = self.droids.get(assignment.droid_id)
            specialty_area = assigned_droid_persona.character_traits.get("specialty_area", "General") if assigned_droid_persona else "General"

            verification_result = {
                "verification_passed": passed,
                "helpdesk": {
                    "location": self.helpdesk_location,
                    "coordinator": c3po.name if c3po else "C-3PO",
                    "assigned_droid": assignment.droid_name,
                    "specialty_area": specialty_area,
                    "escalation_path": "C-3PO → JARVIS (if needed)"
                },
                "hierarchy": {
                    "coordinator": c3po.name if c3po else "C-3PO",
                    "assigned_droid": assignment.droid_name,
                    "droid_specialty": specialty_area,
                    "helpdesk_location": self.helpdesk_location,
                    "escalation_path": "C-3PO → JARVIS (if needed)"
                },
                "droid_assignment": {
                    "droid_id": assignment.droid_id,
                    "droid_name": assignment.droid_name,
                    "specialty_area": specialty_area,
                    "assignment_reason": assignment.assignment_reason,
                    "confidence_score": assignment.confidence_score,
                    "persona_response": assignment.persona_response,
                    "assigned_by": c3po.name if c3po else "C-3PO",
                    "helpdesk_location": self.helpdesk_location
                },
                "workflow_context": {
                    "workflow_id": context.workflow_id,
                    "workflow_name": context.workflow_name,
                    "domain": context.domain,
                    "complexity": context.complexity,
                    "scene_description": context.scene_description
                },
                "verification_tasks": assignment.verification_tasks,
                "verification_results": [
                    {
                        "step": r.step_name,
                        "passed": r.passed,
                        "message": r.message
                    }
                    for r in results
                ],
                "verification_summary": verifier.get_verification_summary()
            }

            logger.info(f"Verification {'PASSED' if passed else 'FAILED'} using {assignment.droid_name} (coordinated by {c3po.name if c3po else 'C-3PO'})")

            return passed, verification_result

        except ImportError:
            logger.error("v3_verification module not found")
            return False, {"error": "v3_verification module not available"}

    def _should_escalate_to_jarvis(self, context: WorkflowContext, force_escalate: bool = False) -> bool:
        """
        Determine if C-3PO should escalate to JARVIS

        C-3PO escalates based on protocol:
        - Critical complexity workflows
        - Multi-domain workflows requiring coordination
        - When explicitly requested
        - When verification fails and requires higher authority

        Args:
            context: WorkflowContext
            force_escalate: Force escalation flag

        Returns:
            bool indicating if escalation is needed
        """
        if force_escalate:
            return True

        # Escalate critical workflows
        if context.complexity == "critical":
            return True

        # Escalate if multiple domains involved
        if len(context.requires_expertise) > 3:
            return True

        # C-3PO decides based on protocol
        # For now, escalate complex+ workflows
        return context.complexity in ["complex", "critical"]

    def _escalate_to_jarvis(self, workflow_data: Dict[str, Any], context: WorkflowContext) -> Tuple[bool, Dict[str, Any]]:
        """
        Escalate workflow to JARVIS (C-3PO protocol escalation)

        Args:
            workflow_data: Workflow data
            context: WorkflowContext

        Returns:
            Tuple of (verification_passed, escalation_results)
        """
        c3po = self.droids.get(self.c3po_id)
        c3po_name = c3po.name if c3po else "C-3PO"

        logger.info(f"{c3po_name}: Escalating to JARVIS as protocol demands...")

        # C-3PO's escalation message
        escalation_message = (
            f"Oh my! This {context.complexity} {context.domain} workflow requires escalation to JARVIS "
            f"as protocol demands. I have coordinated the initial assessment and now require JARVIS's authority."
        )

        # Perform verification first (C-3PO's initial assessment)
        try:
            from v3_verification import V3Verification, V3VerificationConfig

            config = V3VerificationConfig(enabled=True, auto_verify=True, verification_required=True)
            verifier = V3Verification(config)
            passed, results = verifier.run_full_verification(workflow_data)

            escalation_result = {
                "verification_passed": passed,
                "escalated": True,
                "hierarchy": {
                    "coordinator": c3po_name,
                    "escalated_to": "JARVIS",
                    "escalation_path": "C-3PO → JARVIS",
                    "escalation_reason": f"Protocol demands escalation for {context.complexity} {context.domain} workflow"
                },
                "c3po_assessment": {
                    "message": escalation_message,
                    "initial_verification": passed,
                    "workflow_context": {
                        "workflow_id": context.workflow_id,
                        "workflow_name": context.workflow_name,
                        "domain": context.domain,
                        "complexity": context.complexity
                    }
                },
                "verification_results": [
                    {
                        "step": r.step_name,
                        "passed": r.passed,
                        "message": r.message
                    }
                    for r in results
                ],
                "jarvis_handoff": {
                    "status": "pending",
                    "message": "C-3PO has escalated to JARVIS. Awaiting JARVIS response."
                }
            }

            # Send escalation to JARVIS intelligence directory
            try:
                jarvis_dir = self.project_root / "data" / "jarvis_intelligence"
                jarvis_dir.mkdir(parents=True, exist_ok=True)

                message_id = f"jarvis_escalation_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{context.workflow_id}"
                jarvis_message = {
                    "message_id": message_id,
                    "message_type": "escalation",
                    "sender": c3po_name,
                    "recipient": "@jarvis",
                    "priority": "high",
                    "classification": "operational",
                    "timestamp": datetime.now().isoformat(),
                    "escalation": {
                        "escalated_at": datetime.now().isoformat(),
                        "escalated_by": c3po_name,
                        "escalated_to": "JARVIS",
                        "reason": escalation_result["hierarchy"]["escalation_reason"],
                        "workflow_id": context.workflow_id,
                        "workflow_name": context.workflow_name,
                        "workflow_type": context.workflow_type,
                        "complexity": context.complexity,
                        "domain": context.domain
                    },
                    "workflow_data": workflow_data,
                    "verification_results": escalation_result,
                    "status": "pending",
                    "awaiting_response": True
                }

                message_file = jarvis_dir / f"{message_id}.json"
                with open(message_file, 'w', encoding='utf-8') as f:
                    import json
                    json.dump(jarvis_message, f, indent=2, ensure_ascii=False)

                escalation_result["jarvis_handoff"]["message_id"] = message_id
                escalation_result["jarvis_handoff"]["message_file"] = str(message_file)
                escalation_result["jarvis_handoff"]["status"] = "sent"
                escalation_result["jarvis_handoff"]["message"] = f"C-3PO has escalated to JARVIS. Message ID: {message_id}"

                logger.info(f"Escalation sent to JARVIS: {message_id}")
            except Exception as e:
                logger.error(f"Error sending escalation to JARVIS: {e}")
                escalation_result["jarvis_handoff"]["error"] = str(e)

            return passed, escalation_result

        except Exception as e:
            logger.error(f"Error during escalation: {e}")
            return False, {
                "error": str(e),
                "escalated": True,
                "hierarchy": {
                    "coordinator": c3po_name,
                    "escalated_to": "JARVIS"
                }
            }


def verify_workflow_with_droid_actor(workflow_data: Dict[str, Any], project_root: Optional[Path] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Convenience function to verify workflow with smart droid actor selection

    Args:
        workflow_data: Workflow data to verify
        project_root: Optional project root path

    Returns:
        Tuple of (verification_passed, verification_results)
    """
    if project_root is None:
        from pathlib import Path
        project_root = Path.cwd()

    system = DroidActorSystem(project_root)
    return system.verify_with_droid_actor(workflow_data)


if __name__ == "__main__":
    # Example usage
    test_workflow = {
        "workflow_id": "test_technical",
        "workflow_name": "System Repair Workflow",
        "workflow_type": "technical",
        "steps": [
            {"step": 1, "action": "diagnose"},
            {"step": 2, "action": "repair"}
        ]
    }

    from pathlib import Path
    system = DroidActorSystem(Path.cwd())
    passed, results = system.verify_with_droid_actor(test_workflow)

    print(f"Verification {'PASSED' if passed else 'FAILED'}")
    print(f"Droid: {results['droid_assignment']['droid_name']}")
    print(f"Response: {results['droid_assignment']['persona_response']}")

