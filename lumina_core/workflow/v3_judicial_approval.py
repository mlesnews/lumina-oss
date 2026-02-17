"""
@v3 Judicial Approval Framework - Verification, Validation, and Third-Party Verification

Implements the highest quality standard for verification, validation, and third-party verification.
Integrates neutral cloud-based AI model with #decisioning process to provide judicial approval
required for all change control tickets and associated tasks.

Tags: #V3 #VERIFICATION #VALIDATION #THIRD_PARTY_VERIFICATION #JUDICIAL_APPROVAL 
      #CHANGE_CONTROL #AI_VERIFICATION #DECISIONING #QUALITY_STANDARDS #COMPLIANCE 
      #SECURITY @JARVIS @LUMINA
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

try:
    from lumina_core.logging import get_logger
    logger = get_logger("V3JudicialApproval")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3JudicialApproval")

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISIONING_AVAILABLE = True
except ImportError:
    logger.warning("universal_decision_tree not available, decisioning integration disabled")
    DECISIONING_AVAILABLE = False


class ApprovalStatus(Enum):
    """Judicial approval status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"
    ESCALATED = "escalated"


class VerificationTier(Enum):
    """Verification tier levels"""
    VERIFICATION = "verification"  # Tier 1: Code quality, syntax, structure
    VALIDATION = "validation"  # Tier 2: Functional correctness, business logic
    THIRD_PARTY = "third_party"  # Tier 3: Security, compliance, risk


class Environment(Enum):
    """Deployment environments"""
    DEV = "dev"
    TEST = "test"
    QA = "qa"
    STAGING = "staging"
    UAT = "uat"
    PRE_PROD = "pre_prod"
    PROD = "prod"


@dataclass
class VerificationResult:
    """Result of a verification tier"""
    tier: VerificationTier
    passed: bool
    score: float  # 0.0 to 1.0
    findings: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class ChangeControlTicket:
    """Change control ticket information"""
    ticket_id: str
    ticket_type: str  # bug_fix, feature, infrastructure, security, compliance
    priority: str  # critical, high, medium, low
    environment: Environment
    requester: str
    target_date: Optional[str] = None

    # Change details
    description: str = ""
    rationale: str = ""
    code_changes: Optional[Dict[str, Any]] = None
    config_changes: Optional[Dict[str, Any]] = None
    infrastructure_changes: Optional[Dict[str, Any]] = None

    # Impact analysis
    affected_systems: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    user_impact: str = ""
    performance_impact: str = ""
    data_impact: str = ""

    # Risk assessment
    security_risks: List[str] = field(default_factory=list)
    performance_risks: List[str] = field(default_factory=list)
    compliance_risks: List[str] = field(default_factory=list)
    business_risks: List[str] = field(default_factory=list)
    mitigation_plan: str = ""

    # Testing evidence
    unit_tests: Optional[Dict[str, Any]] = None
    integration_tests: Optional[Dict[str, Any]] = None
    qa_approval: bool = False
    performance_tests: Optional[Dict[str, Any]] = None
    security_tests: Optional[Dict[str, Any]] = None

    # Documentation
    change_documentation: Optional[str] = None
    runbooks: Optional[str] = None
    rollback_plan: Optional[str] = None
    communication_plan: Optional[str] = None


@dataclass
class JudicialApprovalDecision:
    """Judicial approval decision"""
    ticket_id: str
    status: ApprovalStatus
    approver: str = "Problem & Change Management Initial Approver (Level 1)"
    decision_timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    # Verification results
    verification_results: List[VerificationResult] = field(default_factory=list)

    # Decision rationale
    rationale: str = ""
    conditions: List[str] = field(default_factory=list)
    escalation_reason: Optional[str] = None

    # Audit trail
    decision_context: Dict[str, Any] = field(default_factory=dict)
    ai_verification_report: Optional[Dict[str, Any]] = None
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class V3VerificationConfig:
    """V3 verification configuration"""
    enabled: bool = True
    ai_provider: str = "openai"  # openai, anthropic, google
    ai_model: str = "gpt-4"  # gpt-4, claude-3, gemini-pro
    ai_api_key: Optional[str] = None
    ai_api_key_vault_path: Optional[str] = None

    verification_levels: Dict[str, List[str]] = field(default_factory=lambda: {
        "dev": ["verification"],
        "test": ["verification", "validation"],
        "staging": ["verification", "validation", "third_party"],
        "pre_prod": ["verification", "validation", "third_party"],
        "prod": ["verification", "validation", "third_party", "audit"]
    })

    approval_required: Dict[str, bool] = field(default_factory=lambda: {
        "dev": False,
        "test": True,
        "staging": True,
        "pre_prod": True,
        "prod": True
    })

    fail_on_error: bool = True
    log_verification: bool = True
    verification_log_path: Optional[Path] = None
    project_root: Optional[Path] = None


class NeutralAIVerifier:
    """Neutral cloud-based AI model for third-party verification"""

    def __init__(self, config: V3VerificationConfig):
        self.config = config
        self.api_key = self._get_api_key()

    def _get_api_key(self) -> Optional[str]:
        """Get API key from vault or config.

        Resolution order:
        1. Direct config value (ai_api_key)
        2. Environment variable named by ai_api_key_vault_path
        3. Azure Key Vault secret named by ai_api_key_vault_path
        """
        if self.config.ai_api_key:
            return self.config.ai_api_key

        if self.config.ai_api_key_vault_path:
            import os

            # Try environment variable first
            env_val = os.getenv(self.config.ai_api_key_vault_path)
            if env_val:
                return env_val

            # Try Azure Key Vault
            try:
                import subprocess
                result = subprocess.run(
                    [
                        "az", "keyvault", "secret", "show",
                        "--vault-name", "jarvis-lumina",
                        "--name", self.config.ai_api_key_vault_path,
                        "--query", "value",
                        "-o", "tsv",
                    ],
                    capture_output=True, text=True, timeout=15,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip().rstrip("\r")
                else:
                    logger.warning(
                        f"Azure Key Vault lookup failed for "
                        f"'{self.config.ai_api_key_vault_path}': {result.stderr.strip()}"
                    )
            except FileNotFoundError:
                logger.warning("Azure CLI (az) not installed, cannot fetch vault secrets")
            except subprocess.TimeoutExpired:
                logger.warning("Azure Key Vault lookup timed out")
            except Exception as e:
                logger.warning(f"Azure Key Vault error: {e}")

        return None

    def _call_openai(self, prompt: str) -> Dict[str, Any]:
        """Call OpenAI API"""
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)

            response = client.chat.completions.create(
                model=self.config.ai_model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a neutral third-party verification system for change control tickets. Provide objective, unbiased verification of code quality, security, compliance, and risk assessment."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,  # Lower temperature for more consistent verification
                max_tokens=2000
            )

            content = response.choices[0].message.content
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "raw_response": True}
        except ImportError:
            logger.warning("OpenAI library not installed. Install with: pip install openai")
            return {"error": "OpenAI library not available"}
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            return {"error": str(e)}

    def _call_anthropic(self, prompt: str) -> Dict[str, Any]:
        """Call Anthropic Claude API"""
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)

            message = client.messages.create(
                model=self.config.ai_model,
                max_tokens=2000,
                temperature=0.3,
                system="You are a neutral third-party verification system for change control tickets. Provide objective, unbiased verification of code quality, security, compliance, and risk assessment.",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = message.content[0].text
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "raw_response": True}
        except ImportError:
            logger.warning("Anthropic library not installed. Install with: pip install anthropic")
            return {"error": "Anthropic library not available"}
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            return {"error": str(e)}

    def _call_google(self, prompt: str) -> Dict[str, Any]:
        """Call Google Cloud AI API"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)

            model = genai.GenerativeModel(self.config.ai_model)

            full_prompt = f"""You are a neutral third-party verification system for change control tickets. Provide objective, unbiased verification of code quality, security, compliance, and risk assessment.

{prompt}

Provide your analysis in JSON format with the following structure:
{{
    "tier1_verification": {{"code_quality_score": 0.0-1.0, "syntax_check": "passed/failed", "findings": []}},
    "tier2_validation": {{"functional_correctness": 0.0-1.0, "findings": []}},
    "tier3_third_party": {{"security_assessment": 0.0-1.0, "compliance_check": "passed/failed", "findings": []}},
    "overall_recommendation": "approve/conditional/reject",
    "confidence_score": 0.0-1.0
}}"""

            response = model.generate_content(full_prompt)
            content = response.text

            # Try to parse as JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "raw_response": True}
        except ImportError:
            logger.warning("Google Generative AI library not installed. Install with: pip install google-generativeai")
            return {"error": "Google AI library not available"}
        except Exception as e:
            logger.error(f"Google AI API call failed: {e}")
            return {"error": str(e)}

    def verify_ticket(self, ticket: ChangeControlTicket) -> Dict[str, Any]:
        """
        Request verification from neutral cloud-based AI model

        Args:
            ticket: Change control ticket to verify

        Returns:
            AI verification report
        """
        if not self.api_key:
            logger.warning("AI API key not available, skipping AI verification")
            return {
                "available": False,
                "message": "AI API key not configured"
            }

        # Prepare verification prompt
        prompt = f"""Analyze the following change control ticket for verification, validation, and third-party verification:

TICKET INFORMATION:
- Ticket ID: {ticket.ticket_id}
- Type: {ticket.ticket_type}
- Priority: {ticket.priority}
- Environment: {ticket.environment.value}
- Description: {ticket.description}
- Rationale: {ticket.rationale}

RISK ASSESSMENT:
- Security Risks: {', '.join(ticket.security_risks) if ticket.security_risks else 'None identified'}
- Compliance Risks: {', '.join(ticket.compliance_risks) if ticket.compliance_risks else 'None identified'}
- Performance Risks: {', '.join(ticket.performance_risks) if ticket.performance_risks else 'None identified'}

TESTING EVIDENCE:
- QA Approval: {'Yes' if ticket.qa_approval else 'No'}
- Unit Tests: {'Provided' if ticket.unit_tests else 'Not provided'}
- Integration Tests: {'Provided' if ticket.integration_tests else 'Not provided'}
- Security Tests: {'Provided' if ticket.security_tests else 'Not provided'}

CODE CHANGES:
{json.dumps(ticket.code_changes, indent=2) if ticket.code_changes else 'No code changes provided'}

Please provide a comprehensive verification analysis covering:
1. Tier 1 (Verification): Code quality, syntax, structure, best practices
2. Tier 2 (Validation): Functional correctness, business logic, integration points
3. Tier 3 (Third-Party Verification): Security assessment, compliance checking, risk analysis

Provide your recommendation: approve, conditional, or reject.
"""

        logger.info(f"Requesting AI verification for ticket {ticket.ticket_id} using {self.config.ai_provider}")

        # Call appropriate AI provider
        try:
            if self.config.ai_provider == "openai":
                ai_response = self._call_openai(prompt)
            elif self.config.ai_provider == "anthropic":
                ai_response = self._call_anthropic(prompt)
            elif self.config.ai_provider == "google":
                ai_response = self._call_google(prompt)
            else:
                logger.warning(f"Unknown AI provider: {self.config.ai_provider}")
                ai_response = {"error": f"Unknown provider: {self.config.ai_provider}"}

            # Process response
            if "error" in ai_response:
                logger.warning(f"AI verification failed: {ai_response['error']}")
                return {
                    "available": False,
                    "message": f"AI verification failed: {ai_response['error']}"
                }

            # Normalize response format
            if "raw_response" in ai_response:
                # Parse text response (basic parsing)
                analysis_text = ai_response.get("analysis", "")
                return {
                    "available": True,
                    "ticket_id": ticket.ticket_id,
                    "verification_timestamp": datetime.now().isoformat(),
                    "provider": self.config.ai_provider,
                    "model": self.config.ai_model,
                    "raw_analysis": analysis_text,
                    "tier1_verification": {
                        "code_quality_score": 0.75,  # Default if not parsed
                        "syntax_check": "unknown",
                        "findings": []
                    },
                    "tier2_validation": {
                        "functional_correctness": 0.75,
                        "findings": []
                    },
                    "tier3_third_party": {
                        "security_assessment": 0.75,
                        "compliance_check": "unknown",
                        "findings": []
                    },
                    "overall_recommendation": "conditional",
                    "confidence_score": 0.70
                }

            # Structured response
            return {
                "available": True,
                "ticket_id": ticket.ticket_id,
                "verification_timestamp": datetime.now().isoformat(),
                "provider": self.config.ai_provider,
                "model": self.config.ai_model,
                **ai_response
            }

        except Exception as e:
            logger.error(f"AI verification exception: {e}", exc_info=True)
            return {
                "available": False,
                "message": f"AI verification exception: {str(e)}"
            }


class V3JudicialApprovalSystem:
    """
    V3 Judicial Approval System

    Provides judicial approval for all change control tickets through:
    - Three-tier verification (Verification, Validation, Third-Party Verification)
    - Neutral cloud-based AI model integration
    - #Decisioning process integration
    - Environment-specific verification levels
    """

    def __init__(self, config: Optional[V3VerificationConfig] = None):
        self.config = config or V3VerificationConfig()
        self.ai_verifier = NeutralAIVerifier(self.config)
        self.approval_history: List[JudicialApprovalDecision] = []

        if self.config.verification_log_path:
            self.config.verification_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("V3 Judicial Approval System initialized")
        logger.info(f"AI Provider: {self.config.ai_provider}")
        logger.info(f"AI Model: {self.config.ai_model}")
        logger.info(f"Verification enabled: {self.config.enabled}")

    def verify_ticket(self, ticket: ChangeControlTicket) -> JudicialApprovalDecision:
        """
        Verify change control ticket and provide judicial approval

        Args:
            ticket: Change control ticket to verify

        Returns:
            Judicial approval decision
        """
        logger.info("="*80)
        logger.info(f"🔍 V3 JUDICIAL APPROVAL: Ticket {ticket.ticket_id}")
        logger.info("="*80)
        logger.info(f"Type: {ticket.ticket_type}")
        logger.info(f"Priority: {ticket.priority}")
        logger.info(f"Environment: {ticket.environment.value}")
        logger.info("="*80)

        # Step 1: Determine required verification tiers based on environment
        required_tiers = self._get_required_tiers(ticket.environment)
        logger.info(f"Required verification tiers: {', '.join([t.value for t in required_tiers])}")

        # Step 2: Run verification tiers
        verification_results: List[VerificationResult] = []

        if VerificationTier.VERIFICATION in required_tiers:
            result = self._run_tier1_verification(ticket)
            verification_results.append(result)

        if VerificationTier.VALIDATION in required_tiers:
            result = self._run_tier2_validation(ticket)
            verification_results.append(result)

        if VerificationTier.THIRD_PARTY in required_tiers:
            result = self._run_tier3_third_party_verification(ticket)
            verification_results.append(result)

        # Step 3: Request AI verification
        ai_report = self.ai_verifier.verify_ticket(ticket)

        # Step 4: Integrate with #decisioning process
        decision_context = self._create_decision_context(ticket, verification_results, ai_report)
        decisioning_outcome = None
        if DECISIONING_AVAILABLE:
            decisioning_outcome = self._integrate_decisioning(decision_context)

        # Step 5: Judicial review (Level 1 - Initial Approver)
        decision = self._judicial_review(
            ticket=ticket,
            verification_results=verification_results,
            ai_report=ai_report,
            decisioning_outcome=decisioning_outcome
        )

        # Step 6: Record in audit trail
        self.approval_history.append(decision)
        if self.config.log_verification:
            self._log_verification(decision)

        # Step 7: Log summary
        logger.info("="*80)
        logger.info("📊 JUDICIAL APPROVAL DECISION")
        logger.info("="*80)
        logger.info(f"Status: {decision.status.value.upper()}")
        logger.info(f"Approver: {decision.approver}")
        logger.info(f"Decision Time: {decision.decision_timestamp}")
        if decision.rationale:
            logger.info(f"Rationale: {decision.rationale}")
        if decision.conditions:
            logger.info(f"Conditions: {', '.join(decision.conditions)}")
        logger.info("="*80)

        return decision

    def _get_required_tiers(self, environment: Environment) -> List[VerificationTier]:
        """Get required verification tiers for environment"""
        env_key = environment.value
        tier_names = self.config.verification_levels.get(env_key, [])

        tiers = []
        if "verification" in tier_names:
            tiers.append(VerificationTier.VERIFICATION)
        if "validation" in tier_names:
            tiers.append(VerificationTier.VALIDATION)
        if "third_party" in tier_names:
            tiers.append(VerificationTier.THIRD_PARTY)

        return tiers

    def _run_tier1_verification(self, ticket: ChangeControlTicket) -> VerificationResult:
        """Tier 1: Verification - Code quality, syntax, structure"""
        logger.info("🔍 Running Tier 1: Verification...")

        findings = []
        recommendations = []
        score = 1.0

        # Check code quality via AST parsing and basic static analysis
        if ticket.code_changes:
            import ast
            for filepath, change_info in ticket.code_changes.items():
                code_content = change_info if isinstance(change_info, str) else change_info.get("content", "")
                if not code_content or not filepath.endswith(".py"):
                    continue

                # Syntax check via AST parse
                try:
                    tree = ast.parse(code_content)
                except SyntaxError as e:
                    findings.append(f"Syntax error in {filepath}: {e.msg} (line {e.lineno})")
                    score -= 0.3
                    continue

                # Check for bare except clauses
                for node in ast.walk(tree):
                    if isinstance(node, ast.ExceptHandler) and node.type is None:
                        findings.append(f"Bare except clause in {filepath} (line {node.lineno})")
                        score -= 0.05
                        recommendations.append(f"Use specific exception types in {filepath}")

                # Check line length compliance
                long_lines = [
                    i + 1 for i, line in enumerate(code_content.split("\n"))
                    if len(line) > 120
                ]
                if long_lines:
                    findings.append(f"{len(long_lines)} lines exceed 120 chars in {filepath}")
                    score -= 0.05

                # Check for functions without docstrings
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if not (node.body and isinstance(node.body[0], ast.Expr)
                                and isinstance(node.body[0].value, ast.Constant)
                                and isinstance(node.body[0].value.value, str)):
                            recommendations.append(
                                f"Add docstring to {node.name}() in {filepath}"
                            )

        # Validate configuration syntax and structure
        if ticket.config_changes:
            for config_path, config_data in ticket.config_changes.items():
                content = config_data if isinstance(config_data, str) else config_data.get("content", "")
                if not content:
                    continue
                if config_path.endswith(".json"):
                    try:
                        json.loads(content)
                    except json.JSONDecodeError as e:
                        findings.append(f"Invalid JSON in {config_path}: {e}")
                        score -= 0.2
                elif config_path.endswith((".yaml", ".yml")):
                    try:
                        import yaml
                        yaml.safe_load(content)
                    except ImportError:
                        pass  # YAML validation optional
                    except Exception as e:
                        findings.append(f"Invalid YAML in {config_path}: {e}")
                        score -= 0.2

        return VerificationResult(
            tier=VerificationTier.VERIFICATION,
            passed=len(findings) == 0,
            score=score,
            findings=findings,
            recommendations=recommendations,
            details={
                "code_quality_checked": ticket.code_changes is not None,
                "config_quality_checked": ticket.config_changes is not None
            }
        )

    def _run_tier2_validation(self, ticket: ChangeControlTicket) -> VerificationResult:
        """Tier 2: Validation - Functional correctness, business logic"""
        logger.info("🔍 Running Tier 2: Validation...")

        findings = []
        recommendations = []
        score = 1.0

        # Validate functional correctness
        if not ticket.description:
            findings.append("Missing change description")
            score -= 0.1

        if not ticket.rationale:
            findings.append("Missing business rationale")
            score -= 0.1

        # Validate system dependencies
        if ticket.affected_systems:
            known_systems = {
                "trading", "cluster-ui", "syphon", "collider", "rag",
                "health-monitor", "litellm", "ollama", "n8n",
                "jarvis", "aios", "mailplus", "pfsense",
            }
            unknown = [s for s in ticket.affected_systems if s.lower() not in known_systems]
            if unknown:
                findings.append(f"Unknown affected systems: {', '.join(unknown)}")
                score -= 0.05
                recommendations.append(
                    "Verify system names match known infrastructure components"
                )
            if ticket.dependencies:
                missing_deps = [
                    d for d in ticket.dependencies
                    if d not in ticket.affected_systems
                ]
                if missing_deps:
                    findings.append(
                        f"Dependencies not listed in affected systems: {', '.join(missing_deps)}"
                    )
                    score -= 0.05

        # Validate testing evidence
        if not ticket.qa_approval:
            findings.append("QA approval not obtained")
            score -= 0.2
            recommendations.append("Obtain QA approval before deployment")

        if not ticket.unit_tests:
            findings.append("Unit test results not provided")
            score -= 0.1

        return VerificationResult(
            tier=VerificationTier.VALIDATION,
            passed=score >= 0.7,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations,
            details={
                "has_description": bool(ticket.description),
                "has_rationale": bool(ticket.rationale),
                "qa_approval": ticket.qa_approval,
                "has_unit_tests": ticket.unit_tests is not None
            }
        )

    def _run_tier3_third_party_verification(self, ticket: ChangeControlTicket) -> VerificationResult:
        """Tier 3: Third-Party Verification - Security, compliance, risk"""
        logger.info("🔍 Running Tier 3: Third-Party Verification...")

        findings = []
        recommendations = []
        score = 1.0

        # Security assessment
        if ticket.security_risks:
            findings.append(f"Security risks identified: {len(ticket.security_risks)}")
            score -= 0.1 * len(ticket.security_risks)
            if not ticket.mitigation_plan:
                findings.append("Security risks identified but no mitigation plan provided")
                score -= 0.2
                recommendations.append("Provide security risk mitigation plan")

        # Compliance checking
        if ticket.compliance_risks:
            findings.append(f"Compliance risks identified: {len(ticket.compliance_risks)}")
            score -= 0.15 * len(ticket.compliance_risks)
            recommendations.append("Address compliance risks before deployment")

        # Risk analysis
        if ticket.priority == "critical" and not ticket.rollback_plan:
            findings.append("Critical change missing rollback plan")
            score -= 0.3
            recommendations.append("Provide detailed rollback plan for critical changes")

        return VerificationResult(
            tier=VerificationTier.THIRD_PARTY,
            passed=score >= 0.7,
            score=max(0.0, score),
            findings=findings,
            recommendations=recommendations,
            details={
                "security_risks_count": len(ticket.security_risks),
                "compliance_risks_count": len(ticket.compliance_risks),
                "has_rollback_plan": bool(ticket.rollback_plan),
                "has_mitigation_plan": bool(ticket.mitigation_plan)
            }
        )

    def _create_decision_context(
        self,
        ticket: ChangeControlTicket,
        verification_results: List[VerificationResult],
        ai_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create decision context for #decisioning process"""
        all_passed = all(r.passed for r in verification_results)
        avg_score = sum(r.score for r in verification_results) / len(verification_results) if verification_results else 0.0

        return {
            "ticket_id": ticket.ticket_id,
            "ticket_type": ticket.ticket_type,
            "priority": ticket.priority,
            "environment": ticket.environment.value,
            "verification_passed": all_passed,
            "average_score": avg_score,
            "verification_tier_count": len(verification_results),
            "ai_verification_available": ai_report.get("available", False),
            "ai_recommendation": ai_report.get("overall_recommendation", "unknown"),
            "ai_confidence": ai_report.get("confidence_score", 0.0),
            "has_security_risks": len(ticket.security_risks) > 0,
            "has_compliance_risks": len(ticket.compliance_risks) > 0,
            "qa_approval": ticket.qa_approval,
            "has_rollback_plan": bool(ticket.rollback_plan)
        }

    def _integrate_decisioning(self, decision_context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Integrate with #decisioning process"""
        if not DECISIONING_AVAILABLE:
            return None

        try:
            # Create decision context for universal decision tree
            ctx = DecisionContext(
                complexity="high" if decision_context["priority"] in ["critical", "high"] else "medium",
                urgency="high" if decision_context["priority"] == "critical" else "medium",
                cost_sensitive=True,
                local_ai_available=True,
                custom_data=decision_context
            )

            # Use decisioning for approval decision
            result = decide('v3_judicial_approval', ctx)
            logger.info(f"Decisioning outcome: {result.outcome.value} - {result.reasoning}")

            # Extract approval status from metadata (decision tree sets this)
            approval_status = result.metadata.get("approval_status", "")
            if not approval_status:
                # Fallback: map DecisionOutcome to approval status
                outcome_map = {
                    "skip": "approve",  # skip means approved (no blocking issues)
                    "fail": "reject",
                    "escalate": "escalate"
                }
                approval_status = outcome_map.get(result.outcome.value, "conditional")

            guidance = {
                "outcome": approval_status,
                "reasoning": result.reasoning,
                "confidence": result.confidence,
                "metadata": result.metadata
            }

            return guidance
        except Exception as e:
            logger.warning(f"Decisioning integration failed: {e}")
            return None

    def _judicial_review(
        self,
        ticket: ChangeControlTicket,
        verification_results: List[VerificationResult],
        ai_report: Dict[str, Any],
        decisioning_outcome: Optional[Dict[str, Any]]
    ) -> JudicialApprovalDecision:
        """
        Judicial review by Level 1 - Problem & Change Management Initial Approver

        This AI Assistant serves as the Initial Approver
        """
        # Evaluate verification results
        all_passed = all(r.passed for r in verification_results)
        avg_score = sum(r.score for r in verification_results) / len(verification_results) if verification_results else 0.0

        # Evaluate AI verification
        ai_available = ai_report.get("available", False)
        ai_recommendation = ai_report.get("overall_recommendation", "unknown")
        ai_confidence = ai_report.get("confidence_score", 0.0)

        # Collect all findings
        all_findings = []
        for result in verification_results:
            all_findings.extend(result.findings)

        # Collect all recommendations
        all_recommendations = []
        for result in verification_results:
            all_recommendations.extend(result.recommendations)

        # Decision logic
        status = ApprovalStatus.PENDING
        rationale = ""
        conditions = []
        escalation_reason = None

        # Consider decisioning outcome if available
        decisioning_guidance = None
        if decisioning_outcome:
            decisioning_guidance = decisioning_outcome.get("outcome", "").lower()
            logger.info(f"Decisioning guidance: {decisioning_guidance} (confidence: {decisioning_outcome.get('confidence', 0.0)})")

        # Automatic approval criteria
        # Consider decisioning guidance if high confidence
        if decisioning_guidance == "approve" and decisioning_outcome and decisioning_outcome.get("confidence", 0.0) >= 0.9:
            if (all_passed and avg_score >= 0.8 and len(ticket.security_risks) == 0 and 
                len(ticket.compliance_risks) == 0 and ticket.qa_approval):
                status = ApprovalStatus.APPROVED
                rationale = f"Decisioning recommends approval. {decisioning_outcome.get('reasoning', '')} All verification tiers passed. No security or compliance risks. QA approval obtained."

        elif (all_passed and 
            avg_score >= 0.8 and 
            (not ai_available or ai_recommendation == "approve") and
            len(ticket.security_risks) == 0 and
            len(ticket.compliance_risks) == 0 and
            ticket.qa_approval):
            status = ApprovalStatus.APPROVED
            rationale = "All verification tiers passed. No security or compliance risks. QA approval obtained."

        # Conditional approval
        elif (all_passed and 
              avg_score >= 0.7 and
              len(ticket.security_risks) == 0 and
              ticket.qa_approval):
            status = ApprovalStatus.CONDITIONAL
            rationale = "Verification passed with minor issues. Conditions must be met before deployment."
            conditions = all_recommendations[:3]  # Top 3 recommendations as conditions

        # Rejection criteria
        # Consider decisioning guidance for rejection
        elif decisioning_guidance == "reject" and decisioning_outcome and decisioning_outcome.get("confidence", 0.0) >= 0.8:
            status = ApprovalStatus.REJECTED
            rationale = f"Decisioning recommends rejection. {decisioning_outcome.get('reasoning', '')} Verification failed or risks identified. Findings: {len(all_findings)}"
            if all_findings:
                rationale += f" Issues: {', '.join(all_findings[:3])}"

        elif (not all_passed or
              avg_score < 0.7 or
              len(ticket.security_risks) > 0 or
              (ai_available and ai_recommendation == "reject")):
            status = ApprovalStatus.REJECTED
            rationale = f"Verification failed or risks identified. Findings: {len(all_findings)}"
            if all_findings:
                rationale += f" Issues: {', '.join(all_findings[:3])}"

        # Escalation criteria
        # Consider decisioning guidance for escalation
        elif decisioning_guidance == "escalate" and decisioning_outcome and decisioning_outcome.get("confidence", 0.0) >= 0.8:
            status = ApprovalStatus.ESCALATED
            escalation_reason = f"Decisioning recommends escalation. {decisioning_outcome.get('reasoning', '')}"
            rationale = escalation_reason

        elif (ticket.priority == "critical" and 
              ticket.environment == Environment.PROD and
              len(ticket.security_risks) > 0):
            status = ApprovalStatus.ESCALATED
            escalation_reason = "Critical PROD deployment with security risks requires Level 2 (Executive) approval"
            rationale = escalation_reason

        # Default to conditional if unclear
        if status == ApprovalStatus.PENDING:
            status = ApprovalStatus.CONDITIONAL
            rationale = "Requires additional review. Conditions must be met."
            conditions = all_recommendations[:3]

        decision = JudicialApprovalDecision(
            ticket_id=ticket.ticket_id,
            status=status,
            approver="Problem & Change Management Initial Approver (Level 1)",
            verification_results=verification_results,
            rationale=rationale,
            conditions=conditions,
            escalation_reason=escalation_reason,
            decision_context={
                "all_passed": all_passed,
                "average_score": avg_score,
                "ai_available": ai_available,
                "ai_recommendation": ai_recommendation,
                "ai_confidence": ai_confidence,
                "findings_count": len(all_findings),
                "recommendations_count": len(all_recommendations)
            },
            ai_verification_report=ai_report if ai_available else None,
            audit_trail=[
                {
                    "action": "verification_initiated",
                    "timestamp": datetime.now().isoformat(),
                    "tiers": [r.tier.value for r in verification_results]
                },
                {
                    "action": "ai_verification_requested",
                    "timestamp": datetime.now().isoformat(),
                    "available": ai_available
                },
                {
                    "action": "judicial_review_completed",
                    "timestamp": datetime.now().isoformat(),
                    "status": status.value
                }
            ]
        )

        return decision

    def _log_verification(self, decision: JudicialApprovalDecision) -> None:
        """Log verification to file"""
        if not self.config.verification_log_path:
            return

        log_entry = {
            "verification_run": datetime.now().isoformat(),
            "decision": asdict(decision)
        }

        try:
            with open(self.config.verification_log_path, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, indent=2, default=str)
                f.write("\n")
        except Exception as e:
            logger.warning(f"Failed to log verification: {e}")

    def get_approval_history(self) -> List[JudicialApprovalDecision]:
        """Get approval history"""
        return self.approval_history

    def get_approval_summary(self) -> Dict[str, Any]:
        """Get summary of approval decisions"""
        total = len(self.approval_history)
        if total == 0:
            return {
                "total_decisions": 0,
                "by_status": {},
                "by_environment": {}
            }

        by_status = {}
        by_environment = {}

        for decision in self.approval_history:
            status = decision.status.value
            by_status[status] = by_status.get(status, 0) + 1

        return {
            "total_decisions": total,
            "by_status": by_status,
            "by_environment": by_environment
        }


def verify_change_control_ticket(
    ticket: ChangeControlTicket,
    config: Optional[V3VerificationConfig] = None
) -> JudicialApprovalDecision:
    """
    Convenience function to verify a change control ticket

    Args:
        ticket: Change control ticket to verify
        config: Optional V3VerificationConfig

    Returns:
        Judicial approval decision
    """
    system = V3JudicialApprovalSystem(config)
    return system.verify_ticket(ticket)


if __name__ == "__main__":
    # Example usage
    test_ticket = ChangeControlTicket(
        ticket_id="TICKET-001",
        ticket_type="feature",
        priority="medium",
        environment=Environment.STAGING,
        requester="Test User",
        description="Test feature implementation",
        rationale="Testing v3 verification framework",
        qa_approval=True
    )

    config = V3VerificationConfig(
        enabled=True,
        verification_log_path=Path("data/v3_verification/test_verification.jsonl")
    )

    system = V3JudicialApprovalSystem(config)
    decision = system.verify_ticket(test_ticket)

    print(f"\nDecision Status: {decision.status.value}")
    print(f"Rationale: {decision.rationale}")
    if decision.conditions:
        print(f"Conditions: {', '.join(decision.conditions)}")
