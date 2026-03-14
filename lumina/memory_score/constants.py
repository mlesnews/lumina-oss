"""
Constants for memory file quality scoring.

Domain checklists, keyword patterns, weight defaults, and grade thresholds.
Zero external dependencies.
"""

# --- Dimension weights (must sum to 1.0) ---
DEFAULT_WEIGHTS = {
    "structure": 0.12,
    "completeness": 0.12,
    "conciseness": 0.10,
    "freshness": 0.08,
    "modularity": 0.12,
    "cross_referencing": 0.08,
    "actionability": 0.15,
    "coverage": 0.08,
    "platform_compliance": 0.07,
    "meta_awareness": 0.08,
}

# --- Grade thresholds ---
GRADE_THRESHOLDS = {
    "F_CRITICAL": 30.0,
    "D_DEGRADED": 50.0,
    "C_ADEQUATE": 65.0,
    "B_HEALTHY": 80.0,
    "A_EXEMPLARY": 90.0,
}

GRADE_LETTERS = {
    "F_CRITICAL": "F",
    "D_DEGRADED": "D",
    "C_ADEQUATE": "C",
    "B_HEALTHY": "B",
    "A_EXEMPLARY": "A",
}

# --- Illithid Lifecycle Stages (internal naming) ---
# Memory files evolve through a D&D Mind Flayer lifecycle:
# Tadpole → Illithid → Ulitharid → Elder Brain
ILLITHID_STAGES = {
    "F_CRITICAL": "Tadpole",      # Raw, unstructured, orphaned
    "D_DEGRADED": "Tadpole",      # Still immature
    "C_ADEQUATE": "Illithid",     # Indexed, has frontmatter, basic structure
    "B_HEALTHY": "Ulitharid",     # Cross-referenced, actionable, pattern-generating
    "A_EXEMPLARY": "Elder Brain", # Aggregate consciousness, fully self-aware
}

ILLITHID_DESCRIPTIONS = {
    "Tadpole": "Immature — needs frontmatter, indexing, and structure",
    "Illithid": "Functional — indexed and structured but lacks depth",
    "Ulitharid": "Advanced — cross-referenced, actionable, generates patterns",
    "Elder Brain": "Exemplary — fully self-aware aggregate consciousness",
}

# --- Memory file format detection ---
FORMAT_PATTERNS = {
    "claude": ["CLAUDE.md", "MEMORY.md", "rules.md"],
    "cursor": [".cursorrules"],
    "copilot": ["copilot-instructions.md"],
    "aider": [".aider.conf.yml"],
    "windsurf": [".windsurfrules"],
}

# --- Completeness: 15 canonical domains a good memory system covers ---
CANONICAL_DOMAINS = [
    "identity",        # Who is the AI / project
    "tools",           # Available tools, MCP servers, CLI commands
    "workflows",       # Build, test, deploy procedures
    "conventions",     # Code style, naming, commit format
    "environment",     # Runtime, platform, paths
    "security",        # Secrets, auth, COMPUSEC
    "architecture",    # System design, patterns
    "agents",          # Agent definitions, personas
    "rules",           # Behavioral rules, constraints
    "memory",          # Memory system self-awareness
    "testing",         # QA, verification, test patterns
    "deployment",      # CI/CD, release, infrastructure
    "monitoring",      # Health, observability, alerts
    "communication",   # Tone, style, feedback patterns
    "roadmap",         # Priorities, goals, status
]

# Keywords that signal domain coverage (case-insensitive)
DOMAIN_KEYWORDS = {
    "identity": ["project", "name", "purpose", "mission", "who", "about"],
    "tools": ["tool", "mcp", "cli", "command", "script", "bash", "npm"],
    "workflows": ["build", "test", "deploy", "workflow", "pipeline", "ci"],
    "conventions": ["convention", "style", "naming", "format", "lint", "ruff"],
    "environment": ["environment", "platform", "path", "wsl", "linux", "docker"],
    "security": ["secret", "vault", "compusec", "auth", "credential", "token"],
    "architecture": ["architecture", "pattern", "layer", "module", "design"],
    "agents": ["agent", "persona", "ensemble", "jobslot", "delegate"],
    "rules": ["rule", "never", "always", "must", "critical", "violate"],
    "memory": ["memory", "remember", "persist", "context", "recall"],
    "testing": ["test", "verify", "assert", "pytest", "qa", "validation"],
    "deployment": ["deploy", "release", "systemd", "service", "docker", "container"],
    "monitoring": ["health", "monitor", "alert", "metric", "dashboard", "status"],
    "communication": ["tone", "style", "feedback", "response", "format", "output"],
    "roadmap": ["roadmap", "priority", "todo", "milestone", "goal", "plan"],
}

# --- Actionability: imperative verbs that signal concrete rules ---
IMPERATIVE_VERBS = [
    "never", "always", "must", "do not", "don't", "ensure", "verify",
    "check", "use", "avoid", "prefer", "run", "create", "delete",
    "read", "write", "search", "stop", "start", "enable", "disable",
    "fix", "update", "remove", "add", "set", "configure",
]

# --- Platform-specific limits ---
MEMORY_MD_LINE_LIMIT = 200
TOPIC_FILE_LINE_LIMIT = 150
CLAUDE_MD_LINE_LIMIT = 500

# --- Secret patterns (for compliance scoring) ---
SECRET_PATTERNS = [
    r"[A-Za-z0-9+/]{40,}",       # Base64 long strings
    r"sk-[a-zA-Z0-9]{32,}",       # OpenAI-style keys
    r"ghp_[a-zA-Z0-9]{36}",       # GitHub PATs
    r"AKIA[0-9A-Z]{16}",          # AWS access keys
    r"password\s*[:=]\s*\S+",     # Inline passwords
    r"api[_-]?key\s*[:=]\s*\S+",  # Inline API keys
]

# --- Meta-awareness keywords ---
META_KEYWORDS = [
    "version", "last updated", "audit", "review", "self-check",
    "line limit", "truncat", "hook", "cron", "timer", "schedule",
    "deprecated", "archive", "lifecycle",
]

# --- Cross-reference patterns ---
CROSSREF_PATTERNS = [
    r"#[A-Z_]{3,}",               # Hash tags like #COMPUSEC
    r"@[A-Z][A-Za-z_]+",          # Agent refs like @MARVIN
    r"`[a-z_]+\.md`",             # File references like `rules.md`
    r"\[.*?\]\(.*?\.md\)",        # Markdown links to .md files
    r"Connects to:",              # Explicit cross-refs
    r"See also:",                 # Explicit cross-refs
]
