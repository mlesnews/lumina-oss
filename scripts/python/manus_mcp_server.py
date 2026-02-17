#!/usr/bin/env python3
"""
MANUS MCP Server

MCP (Model Context Protocol) server that exposes MANUS unified control interface
to MCP clients like Claude Desktop, Cursor, and Windsurf.

This allows AI assistants to control MANUS operations across:
- IDE Control (Cursor, VS Code)
- Workstation Control (Windows, services, resources)
- Home Lab Infrastructure (NAS, services, network)
- Project Lumina Management (Git, codebase, deployments)
- Automation Control (n8n, workflows, integrations)
- Data Management (storage, lifecycle, backup)
- Security Control (scanning, access, compliance)

@MANUS @MCP @UNIFIED_CONTROL
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Any, Sequence
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))
sys.path.insert(0, str(project_root))

try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)

from manus_unified_control import (
    MANUSUnifiedControl,
    ControlArea,
    ControlOperation,
    OperationResult
)

# Initialize MANUS controller
manus_controller = None

def get_manus_controller() -> MANUSUnifiedControl:
    """Get or initialize MANUS controller"""
    global manus_controller
    if manus_controller is None:
        manus_controller = MANUSUnifiedControl(project_root)
    return manus_controller


# MCP Server setup
if MCP_AVAILABLE:
    server = Server("manus-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available MANUS tools"""
        return [
            Tool(
                name="manus_execute_operation",
                description="Execute a MANUS control operation across IDE, workstation, infrastructure, Lumina, automation, data, or security areas",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "area": {
                            "type": "string",
                            "enum": [
                                "ide_control",
                                "workstation_control",
                                "home_lab_infrastructure",
                                "project_lumina_management",
                                "automation_control",
                                "data_management",
                                "security_control"
                            ],
                            "description": "Control area for the operation"
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to perform (e.g., 'connect', 'execute_command', 'get_status', 'scan', etc.)"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "additionalProperties": True
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Operation priority (1-10, default: 1)",
                            "minimum": 1,
                            "maximum": 10,
                            "default": 1
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Operation timeout in seconds (default: 300)",
                            "default": 300
                        }
                    },
                    "required": ["area", "action"]
                }
            ),
            Tool(
                name="manus_get_health_status",
                description="Get health status of all MANUS control areas",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="manus_get_operation_history",
                description="Get recent MANUS operation history",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Number of recent operations to return (default: 50)",
                            "minimum": 1,
                            "maximum": 1000,
                            "default": 50
                        }
                    },
                    "required": []
                }
            ),
            Tool(
                name="manus_ide_control",
                description="Control IDE operations (Cursor, VS Code)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["connect", "execute_command", "open_file", "get_status"],
                            "description": "IDE action to perform"
                        },
                        "ide": {
                            "type": "string",
                            "enum": ["cursor", "vscode"],
                            "description": "Target IDE",
                            "default": "cursor"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "additionalProperties": True
                        }
                    },
                    "required": ["action"]
                }
            ),
            Tool(
                name="manus_workstation_control",
                description="Control workstation operations (Windows, services, resources)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["execute_command", "get_status", "manage_service", "check_resources"],
                            "description": "Workstation action to perform"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "additionalProperties": True
                        }
                    },
                    "required": ["action"]
                }
            ),
            Tool(
                name="manus_lumina_control",
                description="Control Project Lumina operations (Git, codebase, deployments)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["git_operation", "deploy", "get_status", "run_script"],
                            "description": "Lumina action to perform"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "additionalProperties": True
                        }
                    },
                    "required": ["action"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
        """Handle tool calls"""
        controller = get_manus_controller()

        try:
            if name == "manus_execute_operation":
                area_str = arguments.get("area")
                action = arguments.get("action")
                parameters = arguments.get("parameters", {})
                priority = arguments.get("priority", 1)
                timeout = arguments.get("timeout", 300)

                # Map string to ControlArea enum
                area_map = {
                    "ide_control": ControlArea.IDE_CONTROL,
                    "workstation_control": ControlArea.WORKSTATION_CONTROL,
                    "home_lab_infrastructure": ControlArea.HOME_LAB_INFRASTRUCTURE,
                    "project_lumina_management": ControlArea.PROJECT_LUMINA_MANAGEMENT,
                    "automation_control": ControlArea.AUTOMATION_CONTROL,
                    "data_management": ControlArea.DATA_MANAGEMENT,
                    "security_control": ControlArea.SECURITY_CONTROL
                }

                area = area_map.get(area_str)
                if not area:
                    return [TextContent(
                        type="text",
                        text=json.dumps({
                            "success": False,
                            "error": f"Unknown area: {area_str}"
                        }, indent=2)
                    )]

                operation = ControlOperation(
                    operation_id=f"mcp_{datetime.now().timestamp()}",
                    area=area,
                    action=action,
                    parameters=parameters,
                    priority=priority,
                    timeout=timeout
                )

                result = controller.execute_operation(operation)

                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": result.success,
                        "message": result.message,
                        "data": result.data,
                        "errors": result.errors,
                        "duration": result.duration,
                        "operation_id": result.operation_id
                    }, indent=2, default=str)
                )]

            elif name == "manus_get_health_status":
                status = controller.get_health_status()
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2, default=str)
                )]

            elif name == "manus_get_operation_history":
                limit = arguments.get("limit", 50)
                history = controller.get_operation_history(limit=limit)
                return [TextContent(
                    type="text",
                    text=json.dumps(history, indent=2, default=str)
                )]

            elif name == "manus_ide_control":
                action = arguments.get("action")
                ide = arguments.get("ide", "cursor")
                parameters = arguments.get("parameters", {})
                parameters["ide"] = ide

                operation = ControlOperation(
                    operation_id=f"mcp_{datetime.now().timestamp()}",
                    area=ControlArea.IDE_CONTROL,
                    action=action,
                    parameters=parameters
                )

                result = controller.execute_operation(operation)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": result.success,
                        "message": result.message,
                        "data": result.data,
                        "errors": result.errors
                    }, indent=2, default=str)
                )]

            elif name == "manus_workstation_control":
                action = arguments.get("action")
                parameters = arguments.get("parameters", {})

                operation = ControlOperation(
                    operation_id=f"mcp_{datetime.now().timestamp()}",
                    area=ControlArea.WORKSTATION_CONTROL,
                    action=action,
                    parameters=parameters
                )

                result = controller.execute_operation(operation)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": result.success,
                        "message": result.message,
                        "data": result.data,
                        "errors": result.errors
                    }, indent=2, default=str)
                )]

            elif name == "manus_lumina_control":
                action = arguments.get("action")
                parameters = arguments.get("parameters", {})

                operation = ControlOperation(
                    operation_id=f"mcp_{datetime.now().timestamp()}",
                    area=ControlArea.PROJECT_LUMINA_MANAGEMENT,
                    action=action,
                    parameters=parameters
                )

                result = controller.execute_operation(operation)
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": result.success,
                        "message": result.message,
                        "data": result.data,
                        "errors": result.errors
                    }, indent=2, default=str)
                )]

            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({
                        "success": False,
                        "error": f"Unknown tool: {name}"
                    }, indent=2)
                )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                }, indent=2)
            )]


async def main():
    """Main entry point for MCP server"""
    if not MCP_AVAILABLE:
        print("Error: MCP SDK not installed. Install with: pip install mcp", file=sys.stderr)
        sys.exit(1)

    # Initialize MANUS controller
    get_manus_controller()

    # Run stdio server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":


    asyncio.run(main())