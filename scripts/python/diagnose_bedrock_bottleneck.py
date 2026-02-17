#!/usr/bin/env python3
"""
Diagnose Bedrock Model Selection Bottleneck

Identifies why agent chat session resumption is failing with:
"Selected model is not supported by bedrock, please use a different model"

Tags: #DIAGNOSTIC #BEDROCK #MODEL_SELECTION #BOTTLENECK #TROUBLESHOOTING
@JARVIS @MARVIN
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BedrockBottleneckDiagnostic")


class BedrockBottleneckDiagnostic:
    """
    Diagnose Bedrock model selection bottleneck in agent chat sessions
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.agent_sessions_dir = self.data_dir / "agent_chat_sessions"
        self.config_dir = self.project_root / "config"

        logger.info("✅ Bedrock Bottleneck Diagnostic initialized")

    def diagnose(self) -> Dict[str, Any]:
        try:
            """
            Run full diagnostic on Bedrock model selection bottleneck
            """
            logger.info("=" * 80)
            logger.info("🔍 BEDROCK MODEL SELECTION BOTTLENECK DIAGNOSTIC")
            logger.info("=" * 80)
            logger.info("")

            result = {
                "timestamp": datetime.now().isoformat(),
                "request_id": "a2448884-9307-4c86-b132-7a6881cb5102",
                "error": "Selected model is not supported by bedrock, please use a different model",
                "diagnostics": {},
                "findings": [],
                "recommendations": [],
                "severity": "high"
            }

            # Diagnostic 1: Check agent chat sessions
            logger.info("DIAGNOSTIC 1: Checking agent chat sessions...")
            session_diagnostic = self._diagnose_sessions()
            result["diagnostics"]["sessions"] = session_diagnostic
            logger.info(f"   ✅ Found {len(session_diagnostic.get('sessions', []))} sessions")
            logger.info("")

            # Diagnostic 2: Check model configuration
            logger.info("DIAGNOSTIC 2: Checking model configuration...")
            model_diagnostic = self._diagnose_models()
            result["diagnostics"]["models"] = model_diagnostic
            logger.info(f"   ✅ Model issues: {len(model_diagnostic.get('issues', []))}")
            logger.info("")

            # Diagnostic 3: Check Bedrock configuration
            logger.info("DIAGNOSTIC 3: Checking Bedrock configuration...")
            bedrock_diagnostic = self._diagnose_bedrock()
            result["diagnostics"]["bedrock"] = bedrock_diagnostic
            logger.info(f"   ✅ Bedrock status: {bedrock_diagnostic.get('status', 'unknown')}")
            logger.info("")

            # Diagnostic 4: Check provider selection
            logger.info("DIAGNOSTIC 4: Checking provider selection...")
            provider_diagnostic = self._diagnose_provider_selection()
            result["diagnostics"]["provider_selection"] = provider_diagnostic
            logger.info(f"   ✅ Provider issues: {len(provider_diagnostic.get('issues', []))}")
            logger.info("")

            # Diagnostic 5: Check session resumption code
            logger.info("DIAGNOSTIC 5: Checking session resumption code...")
            resumption_diagnostic = self._diagnose_resumption_code()
            result["diagnostics"]["resumption_code"] = resumption_diagnostic
            logger.info(f"   ✅ Code issues: {len(resumption_diagnostic.get('issues', []))}")
            logger.info("")

            # Analyze findings
            logger.info("ANALYZING FINDINGS...")
            findings = self._analyze_findings(result["diagnostics"])
            result["findings"] = findings
            logger.info(f"   ✅ Found {len(findings)} critical findings")
            logger.info("")

            # Generate recommendations
            logger.info("GENERATING RECOMMENDATIONS...")
            recommendations = self._generate_recommendations(findings, result["diagnostics"])
            result["recommendations"] = recommendations
            logger.info(f"   ✅ Generated {len(recommendations)} recommendations")
            logger.info("")

            # Save diagnostic report
            output_dir = self.data_dir / "diagnostics"
            output_dir.mkdir(parents=True, exist_ok=True)
            report_file = output_dir / f"bedrock_bottleneck_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info("=" * 80)
            logger.info("✅ DIAGNOSTIC COMPLETE")
            logger.info("=" * 80)
            logger.info(f"📄 Report saved: {report_file.name}")
            logger.info("")

            # Print summary
            self._print_summary(result)

            return result

        except Exception as e:
            self.logger.error(f"Error in diagnose: {e}", exc_info=True)
            raise
    def _diagnose_sessions(self) -> Dict[str, Any]:
        """Diagnose agent chat sessions"""
        diagnostic = {
            "sessions": [],
            "issues": [],
            "model_usage": {}
        }

        if not self.agent_sessions_dir.exists():
            diagnostic["issues"].append("Agent sessions directory does not exist")
            return diagnostic

        for session_file in sorted(self.agent_sessions_dir.glob("*.json")):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                session_id = session_data.get("session_id") or session_file.stem
                model = session_data.get("model", "unknown")
                provider = session_data.get("provider", "unknown")

                session_info = {
                    "session_id": session_id,
                    "file": session_file.name,
                    "model": model,
                    "provider": provider,
                    "has_provider": "provider" in session_data,
                    "issues": []
                }

                # Check for issues
                if model == "ULTRON" and provider != "ollama":
                    session_info["issues"].append(
                        f"Model is ULTRON (Ollama) but provider is '{provider}' - will fail if Bedrock is selected"
                    )
                    diagnostic["issues"].append(
                        f"Session {session_id}: ULTRON model without Ollama provider"
                    )

                if model == "ULTRON" and not provider:
                    session_info["issues"].append(
                        "Model is ULTRON but no provider specified - Cursor may default to Bedrock"
                    )
                    diagnostic["issues"].append(
                        f"Session {session_id}: ULTRON model without provider"
                    )

                # Track model usage
                if model not in diagnostic["model_usage"]:
                    diagnostic["model_usage"][model] = 0
                diagnostic["model_usage"][model] += 1

                diagnostic["sessions"].append(session_info)

            except Exception as e:
                diagnostic["issues"].append(f"Error reading {session_file.name}: {e}")

        return diagnostic

    def _diagnose_models(self) -> Dict[str, Any]:
        """Diagnose model configuration"""
        diagnostic = {
            "ollama_models": {
                "ULTRON": "qwen2.5:72b",
                "KAIJU": "llama3"
            },
            "bedrock_models": {},
            "issues": []
        }

        # Check Bedrock config
        bedrock_config_file = self.config_dir / "aws_bedrock_config.json"
        if bedrock_config_file.exists():
            try:
                with open(bedrock_config_file, 'r', encoding='utf-8') as f:
                    bedrock_config = json.load(f)

                models = bedrock_config.get("aws_bedrock", {}).get("models", {})
                for model_name, model_info in models.items():
                    diagnostic["bedrock_models"][model_name] = model_info.get("model_id", "unknown")

                # Check if ULTRON is in Bedrock models (it shouldn't be)
                if "ULTRON" in diagnostic["bedrock_models"]:
                    diagnostic["issues"].append(
                        "ULTRON is configured as a Bedrock model, but it's an Ollama model"
                    )

            except Exception as e:
                diagnostic["issues"].append(f"Error reading Bedrock config: {e}")
        else:
            diagnostic["issues"].append("Bedrock config file not found")

        # Check if ULTRON is being sent to Bedrock
        if "ULTRON" in diagnostic["bedrock_models"]:
            diagnostic["issues"].append(
                "CRITICAL: ULTRON (Ollama model) is being sent to Bedrock - this will fail"
            )

        return diagnostic

    def _diagnose_bedrock(self) -> Dict[str, Any]:
        """Diagnose Bedrock configuration"""
        diagnostic = {
            "status": "unknown",
            "enabled": False,
            "configured": False,
            "credentials_available": False,
            "issues": []
        }

        bedrock_config_file = self.config_dir / "aws_bedrock_config.json"
        if bedrock_config_file.exists():
            try:
                with open(bedrock_config_file, 'r', encoding='utf-8') as f:
                    bedrock_config = json.load(f)

                diagnostic["enabled"] = bedrock_config.get("enabled", False)
                diagnostic["configured"] = True

                # Check cursor integration
                cursor_integration = bedrock_config.get("cursor_integration", {})
                if cursor_integration.get("enabled", False):
                    diagnostic["status"] = "enabled_in_cursor"
                    diagnostic["issues"].append(
                        "Bedrock is enabled in Cursor - sessions with ULTRON will fail if routed to Bedrock"
                    )
                else:
                    diagnostic["status"] = "configured_but_not_enabled"

            except Exception as e:
                diagnostic["issues"].append(f"Error reading Bedrock config: {e}")
        else:
            diagnostic["status"] = "not_configured"
            diagnostic["issues"].append("Bedrock config file not found")

        # Check for AWS credentials (basic check)
        import os
        if os.getenv("AWS_ACCESS_KEY_ID") or os.getenv("AWS_SECRET_ACCESS_KEY"):
            diagnostic["credentials_available"] = True
        else:
            diagnostic["issues"].append(
                "AWS credentials not found in environment - Bedrock may not be properly configured"
            )

        return diagnostic

    def _diagnose_provider_selection(self) -> Dict[str, Any]:
        """Diagnose provider selection logic"""
        diagnostic = {
            "issues": [],
            "provider_mapping": {
                "ULTRON": "ollama",
                "KAIJU": "ollama"
            },
            "missing_providers": []
        }

        # Check if sessions specify providers
        if self.agent_sessions_dir.exists():
            for session_file in self.agent_sessions_dir.glob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)

                    model = session_data.get("model", "")
                    provider = session_data.get("provider", "")

                    if model in diagnostic["provider_mapping"]:
                        expected_provider = diagnostic["provider_mapping"][model]
                        if not provider:
                            diagnostic["missing_providers"].append({
                                "session": session_file.stem,
                                "model": model,
                                "expected_provider": expected_provider
                            })
                            diagnostic["issues"].append(
                                f"Session {session_file.stem}: Model {model} missing provider (should be {expected_provider})"
                            )
                        elif provider != expected_provider:
                            diagnostic["issues"].append(
                                f"Session {session_file.stem}: Model {model} has wrong provider '{provider}' (should be {expected_provider})"
                            )

                except Exception:
                    pass

        return diagnostic

    def _diagnose_resumption_code(self) -> Dict[str, Any]:
        """Diagnose session resumption code"""
        diagnostic = {
            "issues": [],
            "code_locations": []
        }

        # Check jarvis_resume_all_sessions.py
        resumption_file = self.project_root / "scripts" / "python" / "jarvis_resume_all_sessions.py"
        if resumption_file.exists():
            try:
                content = resumption_file.read_text(encoding='utf-8')

                # Check if provider is set
                if 'provider' not in content.lower():
                    diagnostic["issues"].append(
                        "jarvis_resume_all_sessions.py does not set 'provider' field - Cursor may default to Bedrock"
                    )
                    diagnostic["code_locations"].append({
                        "file": "jarvis_resume_all_sessions.py",
                        "issue": "Missing provider specification",
                        "line": "ensure_model_config method"
                    })

                # Check if ULTRON is hardcoded
                if 'ULTRON' in content and 'ollama' not in content.lower():
                    diagnostic["issues"].append(
                        "jarvis_resume_all_sessions.py sets model to ULTRON but doesn't specify Ollama provider"
                    )
                    diagnostic["code_locations"].append({
                        "file": "jarvis_resume_all_sessions.py",
                        "issue": "ULTRON model without Ollama provider",
                        "line": "ensure_model_config method"
                    })

            except Exception as e:
                diagnostic["issues"].append(f"Error reading resumption code: {e}")

        return diagnostic

    def _analyze_findings(self, diagnostics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze diagnostic results to identify root causes"""
        findings = []

        # Finding 1: ULTRON model without provider
        sessions_diag = diagnostics.get("sessions", {})
        if sessions_diag.get("issues"):
            findings.append({
                "severity": "critical",
                "title": "ULTRON Model Without Provider Specification",
                "description": "Agent chat sessions use ULTRON model (Ollama) but don't specify provider. Cursor may route to Bedrock, causing 'model not supported' error.",
                "affected_sessions": len([s for s in sessions_diag.get("sessions", []) if s.get("model") == "ULTRON" and not s.get("provider")]),
                "impact": "Session resumption fails with Bedrock error"
            })

        # Finding 2: Bedrock enabled but ULTRON used
        bedrock_diag = diagnostics.get("bedrock", {})
        if bedrock_diag.get("enabled") and sessions_diag.get("model_usage", {}).get("ULTRON"):
            findings.append({
                "severity": "critical",
                "title": "Bedrock Enabled But ULTRON Model Used",
                "description": "Bedrock is enabled in Cursor, but sessions use ULTRON (Ollama model). Cursor tries to route ULTRON through Bedrock, which doesn't support it.",
                "impact": "All ULTRON sessions fail when resuming"
            })

        # Finding 3: Missing provider in resumption code
        resumption_diag = diagnostics.get("resumption_code", {})
        if resumption_diag.get("issues"):
            findings.append({
                "severity": "high",
                "title": "Resumption Code Doesn't Set Provider",
                "description": "Session resumption code sets model to ULTRON but doesn't specify provider, allowing Cursor to default to Bedrock.",
                "impact": "New sessions will have same issue"
            })

        return findings

    def _generate_recommendations(self, findings: List[Dict[str, Any]], diagnostics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings"""
        recommendations = []

        # Recommendation 1: Add provider to sessions
        if any(f.get("title", "").startswith("ULTRON Model Without Provider") for f in findings):
            recommendations.append({
                "priority": "critical",
                "action": "Add provider field to all agent chat sessions",
                "description": "Update jarvis_resume_all_sessions.py to set provider='ollama' when model='ULTRON'",
                "file": "scripts/python/jarvis_resume_all_sessions.py",
                "method": "ensure_model_config"
            })

        # Recommendation 2: Update resumption code
        if any(f.get("title", "").startswith("Resumption Code") for f in findings):
            recommendations.append({
                "priority": "high",
                "action": "Update session resumption to specify provider",
                "description": "Modify ensure_model_config() to set provider based on model (ULTRON/KAIJU → ollama)",
                "file": "scripts/python/jarvis_resume_all_sessions.py"
            })

        # Recommendation 3: Add error handling
        recommendations.append({
            "priority": "medium",
            "action": "Add Bedrock error handling and fallback",
            "description": "Add try-catch for Bedrock errors and fallback to Ollama if model is ULTRON/KAIJU",
            "file": "scripts/python/jarvis_resume_all_sessions.py"
        })

        # Recommendation 4: Disable Bedrock if not needed
        bedrock_diag = diagnostics.get("bedrock", {})
        if bedrock_diag.get("enabled") and not bedrock_diag.get("credentials_available"):
            recommendations.append({
                "priority": "medium",
                "action": "Disable Bedrock in Cursor if not using it",
                "description": "If you're only using Ollama models (ULTRON, KAIJU), disable Bedrock in Cursor settings to prevent routing issues",
                "file": "Cursor Settings → Personal Configuration → AWS Bedrock"
            })

        return recommendations

    def _print_summary(self, result: Dict[str, Any]):
        """Print diagnostic summary"""
        print("\n" + "=" * 80)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 80)
        print(f"Request ID: {result['request_id']}")
        print(f"Error: {result['error']}")
        print()

        print("🔍 FINDINGS:")
        for i, finding in enumerate(result["findings"], 1):
            print(f"  {i}. [{finding['severity'].upper()}] {finding['title']}")
            print(f"     {finding['description']}")
            print()

        print("💡 RECOMMENDATIONS:")
        for i, rec in enumerate(result["recommendations"], 1):
            print(f"  {i}. [{rec['priority'].upper()}] {rec['action']}")
            print(f"     {rec['description']}")
            print()

        print("=" * 80)


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Diagnose Bedrock Model Selection Bottleneck")
        parser.add_argument("--project-root", help="Project root directory")

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        diagnostic = BedrockBottleneckDiagnostic(project_root=project_root)
        result = diagnostic.diagnose()

        return result


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()