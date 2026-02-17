"""
R5 Living Context Matrix System
Continuously aggregates IDE chat sessions into concentrated knowledge

Features:
- @PEAK pattern extraction
- @WHATIF thought experiments
- Matrix visualization
- Knowledge condensation
- n8n and Jupyter integration
"""

import json
import logging
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add project root to path for unified engine
script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from scripts.python.pattern_unified_engine import PatternUnifiedEngine
    UNIFIED_ENGINE_AVAILABLE = True
except ImportError:
    UNIFIED_ENGINE_AVAILABLE = False
    PatternUnifiedEngine = None

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("R5")
else:
    logger = get_logger("R5")

# Azure Service Bus integration
try:
    from azure_service_bus_integration import (
        AzureServiceBusClient,
        ServiceBusMessage,
        MessageType,
        get_service_bus_client,
        get_key_vault_client
    )
    from r5_service_bus_integration import publish_knowledge_entry
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logger.debug("Azure Service Bus integration not available - using file-based fallback")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ChatSession:
    """Represents a single IDE chat session"""
    session_id: str
    timestamp: datetime
    messages: List[Dict[str, Any]]
    patterns: List[str] = field(default_factory=list)
    whatif_scenarios: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PeakPattern:
    """@PEAK pattern extracted from sessions"""
    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    sessions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class R5Config:
    """R5 system configuration"""
    data_directory: Path
    output_file: Path
    aggregation_interval: int = 3600
    max_sessions: int = 1000
    peak_extraction_enabled: bool = True
    whatif_enabled: bool = True
    matrix_visualization_enabled: bool = True
    n8n_webhook_url: Optional[str] = None
    jupyter_notebook_path: Optional[Path] = None


class R5LivingContextMatrix:
    """
    R5 Living Context Matrix System

    Aggregates and condenses IDE chat sessions into concentrated knowledge.
    Integrates with n8n workflows and Jupyter notebooks for force multiplier effect.
    """

    def __init__(self, project_root: Path, config: Optional[R5Config] = None):
        """
        Initialize R5 system

        Args:
            project_root: Root directory of the project
            config: Optional R5Config instance
        """
        self.project_root = Path(project_root)

        # Load storage policy
        policy_file = self.project_root / "config" / "storage_policy.json"
        storage_policy = {"zero_local_storage_enforced": False}
        if policy_file.exists():
            try:
                with open(policy_file, "r", encoding="utf-8") as f:
                    storage_policy = json.load(f)
            except Exception as e:
                logging.error(f"Error loading storage policy: {e}")

        # Load or create config
        if config:
            self.config = config
        else:
            self.config = self._load_config()

        # Enforce Zero-Local-Storage Policy for R5
        if storage_policy.get("zero_local_storage_enforced"):
            nas_r5_dir = Path(storage_policy["nas_paths"]["r5_matrix"])
            self.config.data_directory = nas_r5_dir
            # Update output file path to be relative to the new data directory
            self.config.output_file = nas_r5_dir / "LIVING_CONTEXT_MATRIX_PROMPT.md"
            logging.info(f"🛡️  Enforcing Zero-Local-Storage Policy for R5. Using NAS: {nas_r5_dir}")

        # Ensure directories exist
        self.config.data_directory.mkdir(parents=True, exist_ok=True)
        (self.config.data_directory / "sessions").mkdir(exist_ok=True)
        (self.config.data_directory / "aggregated").mkdir(exist_ok=True)
        (self.config.data_directory / "visualizations").mkdir(exist_ok=True)

        self.sessions: List[ChatSession] = []
        self.patterns: List[PeakPattern] = []

        # Initialize Azure Service Bus client
        self.service_bus_client = None
        if AZURE_AVAILABLE:
            try:
                kv_client = get_key_vault_client()
                self.service_bus_client = get_service_bus_client(
                    namespace="jarvis-lumina-bus.servicebus.windows.net",
                    key_vault_client=kv_client
                )
                logger.info("Azure Service Bus client initialized for R5")
            except Exception as e:
                logger.warning(f"Service Bus not available, using file-based fallback: {e}")
                self.service_bus_client = None

        logger.info("R5 Living Context Matrix initialized")
        logger.info(f"Data directory: {self.config.data_directory}")
        logger.info(f"Output file: {self.config.output_file}")

    def _load_config(self) -> R5Config:
        try:
            """Load configuration from file"""
            config_path = self.project_root / "config" / "r5" / "r5_config.json"

            if config_path.exists():
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    r5_data = config_data.get("r5_system", {})

                    return R5Config(
                        data_directory=Path(r5_data.get("data_directory", "data/r5_living_matrix")),
                        output_file=Path(r5_data.get("output_file", "data/r5_living_matrix/LIVING_CONTEXT_MATRIX_PROMPT.md")),
                        aggregation_interval=r5_data.get("aggregation_interval", 3600),
                        max_sessions=r5_data.get("max_sessions", 1000),
                        peak_extraction_enabled=r5_data.get("features", {}).get("peak_pattern_extraction", True),
                        whatif_enabled=r5_data.get("features", {}).get("whatif_thought_experiments", True),
                        matrix_visualization_enabled=r5_data.get("features", {}).get("matrix_visualization", True),
                        n8n_webhook_url=r5_data.get("integrations", {}).get("n8n", {}).get("webhook_url"),
                        jupyter_notebook_path=Path(r5_data.get("integrations", {}).get("jupyter", {}).get("notebook_path", "data/jupyter")) if r5_data.get("integrations", {}).get("jupyter", {}).get("notebook_path") else None
                    )
            else:
                # Default config
                return R5Config(
                    data_directory=self.project_root / "data" / "r5_living_matrix",
                    output_file=self.project_root / "data" / "r5_living_matrix" / "LIVING_CONTEXT_MATRIX_PROMPT.md"
                )

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def ingest_session(self, session_data: Dict[str, Any]) -> str:
        try:
            """
            Ingest a new chat session

            Args:
                session_data: Dictionary containing session data
                    - session_id: Optional session ID (auto-generated if not provided)
                    - timestamp: Optional ISO timestamp (defaults to now)
                    - messages: List of message dicts with 'role' and 'content'
                    - content: Optional string content (converted to messages if messages not provided)
                    - metadata: Optional metadata dictionary

            Returns:
                Session ID
            """
            session_id = session_data.get("session_id", f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

            # Handle both 'messages' and 'content' formats
            messages = session_data.get("messages", [])
            if not messages and "content" in session_data:
                # Convert content string to messages format
                content = session_data.get("content", "")
                messages = [
                    {"role": "user", "content": content}
                ]

            session = ChatSession(
                session_id=session_id,
                timestamp=datetime.fromisoformat(session_data.get("timestamp", datetime.now().isoformat())),
                messages=messages,
                metadata=session_data.get("metadata", {})
            )

            # Extract patterns if enabled
            if self.config.peak_extraction_enabled:
                session.patterns = self._extract_peak_patterns(session)

            # Extract @WHATIF scenarios if enabled
            if self.config.whatif_enabled:
                session.whatif_scenarios = self._extract_whatif_scenarios(session)

            # Save session
            session_file = self.config.data_directory / "sessions" / f"{session_id}.json"
            with open(session_file, 'w') as f:
                json.dump({
                    "session_id": session.session_id,
                    "timestamp": session.timestamp.isoformat(),
                    "messages": session.messages,
                    "patterns": session.patterns,
                    "whatif_scenarios": session.whatif_scenarios,
                    "metadata": session.metadata
                }, f, indent=2)

            self.sessions.append(session)

            # Keep only max_sessions
            if len(self.sessions) > self.config.max_sessions:
                self.sessions = self.sessions[-self.config.max_sessions:]

            # Publish to Azure Service Bus for R5 ingestion
            if AZURE_AVAILABLE and self.service_bus_client:
                try:
                    publish_knowledge_entry({
                        "session_id": session_id,
                        "timestamp": session.timestamp.isoformat(),
                        "messages": session.messages,
                        "patterns": session.patterns,
                        "whatif_scenarios": session.whatif_scenarios,
                        "metadata": session.metadata
                    }, extract_patterns=self.config.peak_extraction_enabled, sb_client=self.service_bus_client)
                    logger.debug(f"Published session to Service Bus: {session_id}")
                except Exception as e:
                    logger.warning(f"Failed to publish session to Service Bus: {e}")

            logger.info(f"Ingested session: {session_id} ({len(session.messages)} messages)")

            return session_id

        except Exception as e:
            self.logger.error(f"Error in ingest_session: {e}", exc_info=True)
            raise
    def _extract_peak_patterns(self, session: ChatSession) -> List[str]:
        """Extract @PEAK patterns from session using unified engine"""

        # Use unified engine if available
        if self.unified_engine:
            try:
                # Combine all messages into text
                text = "\n".join([msg.get("content", "") for msg in session.messages])

                # Use unified engine for pattern extraction
                # Pattern: Look for @PEAK mentions
                pattern = r"@PEAK|@peak|#PEAK|#peak"
                result = self.unified_engine.unified_operation("extract", text, pattern)

                if result.extracted:
                    logger.debug(f"   Extracted {len(result.extracted)} patterns using unified engine")
                    return result.extracted
            except Exception as e:
                logger.warning(f"   Unified engine error, falling back: {e}")

        # Fallback to original implementation
        patterns = []

        for message in session.messages:
            content = message.get("content", "")
            if "@PEAK" in content or "@peak" in content:
                # Extract pattern descriptions
                lines = content.split("\n")
                for line in lines:
                    if "@PEAK" in line or "@peak" in line:
                        patterns.append(line.strip())

        return patterns

    def _extract_whatif_scenarios(self, session: ChatSession) -> List[str]:
        """Extract @WHATIF scenarios from session"""
        scenarios = []

        for message in session.messages:
            content = message.get("content", "")
            if "@WHATIF" in content or "@whatif" in content or "what if" in content.lower():
                # Extract scenario descriptions
                lines = content.split("\n")
                for line in lines:
                    if "@WHATIF" in line or "@whatif" in line or "what if" in line.lower():
                        scenarios.append(line.strip())

        return scenarios

    def aggregate_sessions(self) -> Dict[str, Any]:
        """
        Aggregate all sessions into concentrated knowledge

        Returns:
            Dictionary containing aggregated data
        """
        logger.info(f"Aggregating {len(self.sessions)} sessions...")

        # Load all sessions
        session_files = list((self.config.data_directory / "sessions").glob("*.json"))
        all_sessions = []

        for session_file in session_files:
            try:
                with open(session_file, 'r') as f:
                    all_sessions.append(json.load(f))
            except Exception as e:
                logger.warning(f"Failed to load session {session_file}: {e}")

        # Aggregate patterns
        all_patterns = {}
        for session in all_sessions:
            for pattern in session.get("patterns", []):
                if pattern not in all_patterns:
                    all_patterns[pattern] = 0
                all_patterns[pattern] += 1

        # Aggregate @WHATIF scenarios
        all_whatifs = []
        for session in all_sessions:
            all_whatifs.extend(session.get("whatif_scenarios", []))

        # Create aggregated data
        aggregated = {
            "total_sessions": len(all_sessions),
            "total_messages": sum(len(s.get("messages", [])) for s in all_sessions),
            "peak_patterns": sorted(all_patterns.items(), key=lambda x: x[1], reverse=True),
            "whatif_scenarios": list(set(all_whatifs)),
            "last_updated": datetime.now().isoformat(),
            "sessions": all_sessions[-100:]  # Last 100 sessions
        }

        # Save aggregated data
        aggregated_file = self.config.data_directory / "aggregated" / f"aggregated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(aggregated_file, 'w') as f:
            json.dump(aggregated, f, indent=2)

        # Generate living context matrix prompt
        self._generate_living_context_matrix(aggregated)

        logger.info("Aggregation complete")

        return aggregated

    def _generate_living_context_matrix(self, aggregated: Dict[str, Any]) -> None:
        try:
            """Generate the living context matrix prompt markdown file"""
            output = []
            output.append("# R5 Living Context Matrix")
            output.append("")
            output.append("> The most concentrated form of knowledge from all IDE chat sessions")
            output.append("")
            output.append(f"**Last Updated:** {aggregated['last_updated']}")
            output.append(f"**Total Sessions:** {aggregated['total_sessions']}")
            output.append(f"**Total Messages:** {aggregated['total_messages']}")
            output.append("")

            # @PEAK Patterns
            output.append("## @PEAK Patterns")
            output.append("")
            output.append("High-quality, reusable components extracted from sessions:")
            output.append("")
            for pattern, frequency in aggregated['peak_patterns'][:20]:
                output.append(f"- **({frequency}x)** {pattern}")
            output.append("")

            # @WHATIF Scenarios
            if aggregated['whatif_scenarios']:
                output.append("## @WHATIF Thought Experiments")
                output.append("")
                for scenario in aggregated['whatif_scenarios'][:10]:
                    output.append(f"- {scenario}")
                output.append("")

            # Recent Sessions Summary
            output.append("## Recent Sessions Summary")
            output.append("")
            for session in aggregated['sessions'][-10:]:
                output.append(f"### {session.get('session_id', 'Unknown')}")
                output.append(f"**Timestamp:** {session.get('timestamp', 'Unknown')}")
                output.append(f"**Messages:** {len(session.get('messages', []))}")
                if session.get('patterns'):
                    output.append(f"**@PEAK Patterns:** {len(session['patterns'])}")
                output.append("")

            # Write to file
            with open(self.config.output_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(output))

            logger.info(f"Living context matrix generated: {self.config.output_file}")

        except Exception as e:
            self.logger.error(f"Error in _generate_living_context_matrix: {e}", exc_info=True)
            raise
    def export_for_jupyter(self) -> Dict[str, Any]:
        """Export data formatted for Jupyter notebooks"""
        aggregated = self.aggregate_sessions()

        # Format for pandas/analysis
        jupyter_data = {
            "sessions_df": {
                "session_id": [s.get("session_id") for s in aggregated["sessions"]],
                "timestamp": [s.get("timestamp") for s in aggregated["sessions"]],
                "message_count": [len(s.get("messages", [])) for s in aggregated["sessions"]],
                "pattern_count": [len(s.get("patterns", [])) for s in aggregated["sessions"]]
            },
            "patterns_df": {
                "pattern": [p[0] for p in aggregated["peak_patterns"]],
                "frequency": [p[1] for p in aggregated["peak_patterns"]]
            },
            "metadata": {
                "total_sessions": aggregated["total_sessions"],
                "total_messages": aggregated["total_messages"],
                "last_updated": aggregated["last_updated"]
            }
        }

        return jupyter_data


def main():
    try:
        """Main entry point for R5 system"""
        import sys
        from pathlib import Path

        project_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()

        r5 = R5LivingContextMatrix(project_root)

        # Aggregate existing sessions
        r5.aggregate_sessions()

        print(f"R5 Living Context Matrix generated: {r5.config.output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()