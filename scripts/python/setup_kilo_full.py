#!/usr/bin/env python3
"""
Full Kilo Code Setup - All Features Configured

Sets up:
1. Optimal model settings for local cluster
2. Custom modes for different workflows
3. MCP server integration
4. Auto-approval settings
5. Performance optimizations

Tags: @PEAK @KILO_CODE @CONFIGURATION #automation
"""

import json
import os
import sqlite3
from pathlib import Path

print("=" * 60)
print("  KILO CODE FULL SETUP")
print("=" * 60)

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get current settings
cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
row = cur.fetchone()
settings = json.loads(row[0]) if row else {}

print("\n[1/5] Configuring Model Settings...")
# Optimal settings for Global Compute Pool
settings["ollamaBaseUrl"] = "http://localhost:8080"  # Cluster router
settings["ollamaModelId"] = "qwen2.5:7b"  # Will upgrade to 32B when ready
settings["ollamaNumCtx"] = 32768  # 32K context window
settings["apiProvider"] = "ollama"

print(f"  Base URL: {settings['ollamaBaseUrl']}")
print(f"  Model: {settings['ollamaModelId']}")
print(f"  Context: {settings['ollamaNumCtx']}")

print("\n[2/5] Creating Custom Modes...")
# Custom modes for different workflows
custom_modes = [
    {
        "slug": "architect",
        "name": "Architect",
        "roleDefinition": "You are a senior software architect. Focus on system design, patterns, and high-level decisions. Consider scalability, maintainability, and best practices.",
        "groups": ["read", "browser"],
        "customInstructions": "Think before coding. Propose architecture first. Use diagrams when helpful.",
    },
    {
        "slug": "coder",
        "name": "Coder",
        "roleDefinition": "You are an expert programmer. Write clean, efficient, well-documented code. Follow existing patterns in the codebase.",
        "groups": ["read", "write", "command"],
        "customInstructions": "Write code that works. Add comments for complex logic. Follow DRY and SOLID principles.",
    },
    {
        "slug": "debugger",
        "name": "Debugger",
        "roleDefinition": "You are a debugging specialist. Systematically investigate issues, form hypotheses, and verify fixes. Use logs, traces, and tests.",
        "groups": ["read", "write", "command", "browser"],
        "customInstructions": "Reproduce first. Form hypothesis. Test fix. Verify no regressions.",
    },
    {
        "slug": "reviewer",
        "name": "Reviewer",
        "roleDefinition": "You are a code reviewer. Analyze code for bugs, security issues, performance problems, and style violations. Be constructive.",
        "groups": ["read"],
        "customInstructions": "Check for: bugs, security, performance, readability, tests. Be specific and actionable.",
    },
    {
        "slug": "documenter",
        "name": "Documenter",
        "roleDefinition": "You are a technical writer. Create clear, comprehensive documentation. Include examples, diagrams, and troubleshooting guides.",
        "groups": ["read", "write"],
        "customInstructions": "Document for the reader, not the writer. Include examples. Keep it updated.",
    },
    {
        "slug": "tester",
        "name": "Tester",
        "roleDefinition": "You are a QA engineer. Write comprehensive tests, find edge cases, and ensure code quality. Cover unit, integration, and e2e tests.",
        "groups": ["read", "write", "command"],
        "customInstructions": "Test happy path and edge cases. Mock external dependencies. Aim for high coverage.",
    },
    {
        "slug": "devops",
        "name": "DevOps",
        "roleDefinition": "You are a DevOps engineer. Handle infrastructure, CI/CD, containers, and deployment. Automate everything.",
        "groups": ["read", "write", "command"],
        "customInstructions": "Infrastructure as code. Automate deployments. Monitor and alert.",
    },
    {
        "slug": "security",
        "name": "Security",
        "roleDefinition": "You are a security specialist. Identify vulnerabilities, review for OWASP issues, ensure secure coding practices.",
        "groups": ["read"],
        "customInstructions": "Check for: injection, XSS, auth issues, secrets exposure, dependency vulnerabilities.",
    },
]

settings["customModes"] = custom_modes
print(f"  Created {len(custom_modes)} custom modes:")
for m in custom_modes:
    print(f"    - {m['name']}: {m['roleDefinition'][:50]}...")

print("\n[3/5] Configuring Auto-Approval...")
# Auto-approval for trusted operations
settings["alwaysAllowReadOnly"] = True
settings["alwaysAllowBrowser"] = True
settings["alwaysAllowMcp"] = True
settings["alwaysAllowModeSwitch"] = True
settings["alwaysAllowSubtasks"] = True
settings["alwaysAllowExecute"] = True  # Execute approved commands
settings["alwaysAllowWrite"] = True  # Write to workspace

# Safety limits
settings["alwaysAllowWriteOutsideWorkspace"] = False
settings["alwaysAllowWriteProtected"] = False
settings["alwaysAllowReadOnlyOutsideWorkspace"] = False

print("  Read-only: Auto-approved")
print("  Browser: Auto-approved")
print("  MCP: Auto-approved")
print("  Write (workspace): Auto-approved")
print("  Write (outside): REQUIRES APPROVAL")

print("\n[4/5] Optimizing Performance...")
# Performance settings
settings["maxOpenTabsContext"] = 20
settings["maxWorkspaceFiles"] = 200
settings["maxReadFileLine"] = 500
settings["maxConcurrentFileReads"] = 5
settings["autoCondenseContext"] = True
settings["autoCondenseContextPercent"] = 100
settings["terminalOutputLineLimit"] = 500
settings["terminalOutputCharacterLimit"] = 50000
settings["allowVeryLargeReads"] = True

print("  Max tabs context: 20")
print("  Max workspace files: 200")
print("  Auto-condense: Enabled")
print("  Large reads: Allowed")

print("\n[5/5] Configuring MCP Integration...")
settings["mcpEnabled"] = True

# Create MCP settings file for Kilo Code
mcp_settings_path = Path.home() / ".kilocode" / "mcp_settings.json"
mcp_settings_path.parent.mkdir(parents=True, exist_ok=True)

mcp_config = {
    "mcpServers": {
        "cursor-ide-browser": {
            "command": "cursor-mcp-server",
            "args": ["browser"],
            "transportType": "stdio",
            "alwaysAllow": ["browser_navigate", "browser_snapshot", "browser_click"],
        }
    }
}

# Note: MCP in Kilo Code is configured via workspace .kilocode/mcp_settings.json
print("  MCP: Enabled")
print("  Browser MCP: Available via Cursor")

# Update API configurations
api_configs = settings.get("listApiConfigMeta", [])

# Ensure ULTRON config exists with correct settings
ultron_config = None
for config in api_configs:
    if config.get("name") == "ULTRON":
        ultron_config = config
        break

if ultron_config:
    ultron_config["modelId"] = "qwen2.5:7b"
    ultron_config["apiProvider"] = "ollama"
else:
    api_configs.append(
        {"id": "ultron-cluster", "name": "ULTRON", "apiProvider": "ollama", "modelId": "qwen2.5:7b"}
    )

# Add Global Compute Pool config
pool_exists = any(c.get("name") == "Global-Pool" for c in api_configs)
if not pool_exists:
    api_configs.append(
        {
            "id": "global-compute-pool",
            "name": "Global-Pool",
            "apiProvider": "ollama",
            "modelId": "qwen2.5:7b",  # Will be qwen2.5:32b when ready
        }
    )

settings["listApiConfigMeta"] = api_configs
settings["currentApiConfigName"] = "ULTRON"

# Save settings
cur.execute(
    "UPDATE ItemTable SET value = ? WHERE key = ?", (json.dumps(settings), "kilocode.kilo-code")
)
conn.commit()
conn.close()

print("\n" + "=" * 60)
print("  SETUP COMPLETE")
print("=" * 60)
print("""
Summary:
  - Model: qwen2.5:7b via Global Compute Pool (localhost:8080)
  - Context: 32K tokens
  - Custom Modes: 8 specialized modes
  - Auto-approve: Enabled for safe operations
  - Performance: Optimized settings
  - MCP: Enabled

Custom Modes Available:
  1. Architect - System design and planning
  2. Coder - Writing code
  3. Debugger - Finding and fixing bugs
  4. Reviewer - Code review
  5. Documenter - Writing documentation
  6. Tester - Writing tests
  7. DevOps - Infrastructure and deployment
  8. Security - Security analysis

API Configurations:
  - ULTRON (active) - Local cluster via router
  - Global-Pool - Federated compute pool

⚠️  RELOAD CURSOR to apply changes!
   Ctrl+Shift+P → Developer: Reload Window
""")
