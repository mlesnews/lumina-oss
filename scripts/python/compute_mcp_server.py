#!/usr/bin/env python3
"""
Compute MCP Server — Task execution and compute resource management for Lumina.

This MCP server provides tools for:
- Running background compute tasks
- Checking system resource usage
- Managing task queues

Tags: #mcp #compute @JARVIS
"""

import json
import sys
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any

# Lumina root
LUMINA_ROOT = Path(__file__).parent.parent.parent
TASKS_DIR = LUMINA_ROOT / "data" / "compute" / "tasks"
TASKS_DIR.mkdir(parents=True, exist_ok=True)


def get_system_info() -> dict:
    """Get current system resource info."""
    try:
        import psutil
        return {
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:\\').percent,
            "timestamp": datetime.now().isoformat()
        }
    except ImportError:
        # Fallback if psutil not available
        return {
            "error": "psutil not installed",
            "timestamp": datetime.now().isoformat()
        }


def run_script(script_path: str, args: list = None) -> dict:
    """Run a script and return its output."""
    args = args or []
    full_path = LUMINA_ROOT / script_path if not Path(script_path).is_absolute() else Path(script_path)
    
    if not full_path.exists():
        return {"error": f"Script not found: {script_path}"}
    
    try:
        result = subprocess.run(
            ["python", str(full_path)] + args,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=str(LUMINA_ROOT)
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "script": script_path
        }
    except subprocess.TimeoutExpired:
        return {"error": "Script timed out after 5 minutes", "script": script_path}
    except Exception as e:
        return {"error": str(e), "script": script_path}


def list_available_scripts() -> list:
    """List available Python scripts that can be executed."""
    scripts_dir = LUMINA_ROOT / "scripts" / "python"
    scripts = []
    if scripts_dir.exists():
        for f in scripts_dir.glob("*.py"):
            if not f.name.startswith("_") and "mcp_server" not in f.name:
                scripts.append(f.name)
    return sorted(scripts)


# MCP Server Protocol
def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "lumina-compute",
                "version": "1.0.0"
            },
            "capabilities": {
                "tools": {}
            }
        }
    
    elif method == "tools/list":
        return {
            "tools": [
                {
                    "name": "get_system_info",
                    "description": "Get current system resource usage (CPU, memory, disk)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "run_script",
                    "description": "Run a Python script from the Lumina scripts directory",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "script_path": {"type": "string", "description": "Path to script (relative to Lumina root or absolute)"},
                            "args": {"type": "array", "items": {"type": "string"}, "description": "Command-line arguments"}
                        },
                        "required": ["script_path"]
                    }
                },
                {
                    "name": "list_scripts",
                    "description": "List available Python scripts that can be executed",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        
        if tool_name == "get_system_info":
            result = get_system_info()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "run_script":
            result = run_script(
                script_path=args.get("script_path", ""),
                args=args.get("args", [])
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "list_scripts":
            result = list_available_scripts()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    
    return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Main MCP server loop."""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            response = handle_request(request)
            response["jsonrpc"] = "2.0"
            response["id"] = request.get("id")
            
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32603, "message": str(e)}
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
