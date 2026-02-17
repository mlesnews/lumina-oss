#!/usr/bin/env python3
"""
DYNO LUMINA JARVIS MCP Server

MCP (Model Context Protocol) server that exposes DYNO LUMINA JARVIS as an AI inference layer
to MCP clients like Cursor IDE, Claude Desktop, and Windsurf.

This allows AI assistants to:
- Access all Lumina framework components
- Use AIOS (AI Operating System) capabilities
- Run simulators (WOPR, Matrix, Animatrix)
- Execute AI inference through ULTRON/KAIJU/Cloud AI
- Access all JARVIS components
- Use all Lumina resources and applications

Tags: #DYNO #LUMINA #JARVIS #MCP #AI_INFERENCE_LAYER @JARVIS @LUMINA
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

from scripts.python.dyno_lumina_jarvis import DYNOLuminaJARVIS
from lumina.ai_connection import AIConnectionManager

# Initialize DYNO LUMINA JARVIS
dyno_instance = None

def get_dyno_instance() -> DYNOLuminaJARVIS:
    """Get or initialize DYNO LUMINA JARVIS instance"""
    global dyno_instance
    if dyno_instance is None:
        dyno_instance = DYNOLuminaJARVIS()
    return dyno_instance


# MCP Server setup
if MCP_AVAILABLE:
    server = Server("dyno-lumina-jarvis-mcp")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available DYNO LUMINA JARVIS tools"""
        return [
            Tool(
                name="dyno_get_status",
                description="Get complete DYNO LUMINA JARVIS system status including all components",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="dyno_activate",
                description="Activate DYNO LUMINA JARVIS system and all components",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="dyno_ai_infer",
                description="Execute AI inference through DYNO LUMINA JARVIS AI connection layer (ULTRON/KAIJU/Cloud AI)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Query or prompt for AI inference"
                        },
                        "prefer_local": {
                            "type": "boolean",
                            "description": "Prefer local AI (ULTRON/KAIJU) over cloud AI",
                            "default": True
                        },
                        "model": {
                            "type": "string",
                            "description": "Specific model to use (optional, defaults to available model)"
                        }
                    },
                    "required": ["query"]
                }
            ),
            Tool(
                name="dyno_ai_status",
                description="Get AI service status and availability (ULTRON, KAIJU, Bedrock, OpenAI, Anthropic)",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="dyno_aios_status",
                description="Get AIOS (AI Operating System) status and layer information",
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            ),
            Tool(
                name="dyno_simulator_run",
                description="Run a simulator (WOPR, Matrix, or Animatrix) with a scenario",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "simulator": {
                            "type": "string",
                            "enum": ["wopr", "matrix", "animatrix"],
                            "description": "Simulator to run"
                        },
                        "scenario": {
                            "type": "string",
                            "description": "Scenario or prompt for the simulator"
                        }
                    },
                    "required": ["simulator", "scenario"]
                }
            ),
            Tool(
                name="dyno_component_access",
                description="Access a specific DYNO LUMINA JARVIS component (aios, ai_validation, performance_model, etc.)",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "component": {
                            "type": "string",
                            "enum": [
                                "aios",
                                "ai_validation",
                                "performance_model",
                                "hallucination_analysis",
                                "live_reality",
                                "marvin_validator"
                            ],
                            "description": "Component to access"
                        },
                        "action": {
                            "type": "string",
                            "description": "Action to perform on the component"
                        },
                        "parameters": {
                            "type": "object",
                            "description": "Action-specific parameters",
                            "additionalProperties": True
                        }
                    },
                    "required": ["component", "action"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
        """Handle tool calls"""
        dyno = get_dyno_instance()

        try:
            if name == "dyno_get_status":
                status = dyno.get_system_status()
                return [TextContent(
                    type="text",
                    text=json.dumps(status, indent=2)
                )]

            elif name == "dyno_activate":
                result = dyno.activate()
                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            elif name == "dyno_ai_infer":
                manager = AIConnectionManager()
                query = arguments.get("query", "")
                prefer_local = arguments.get("prefer_local", True)
                model = arguments.get("model")

                result = manager.infer(
                    query=query,
                    prefer_local=prefer_local,
                    model=model
                )

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            elif name == "dyno_ai_status":
                manager = AIConnectionManager()
                status = manager.get_status()
                available = manager.get_available_services()

                result = {
                    "status": status,
                    "available_services": available,
                    "timestamp": datetime.now().isoformat()
                }

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            elif name == "dyno_aios_status":
                if dyno.aios:
                    status = dyno.aios.get_status()
                    return [TextContent(
                        type="text",
                        text=json.dumps(status, indent=2)
                    )]
                else:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "AIOS not available"}, indent=2)
                    )]

            elif name == "dyno_simulator_run":
                if not dyno.aios or not dyno.aios.simulators:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": "Simulators not available"}, indent=2)
                    )]

                simulator_name = arguments.get("simulator", "").lower()
                scenario = arguments.get("scenario", "")

                # Run simulator based on type
                if simulator_name == "wopr":
                    result = dyno.aios.simulators.run_wopr_simulation(scenario)
                elif simulator_name == "matrix":
                    result = dyno.aios.simulators.run_matrix_simulation(scenario)
                elif simulator_name == "animatrix":
                    result = dyno.aios.simulators.run_animatrix_simulation(scenario)
                else:
                    result = {"error": f"Unknown simulator: {simulator_name}"}

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            elif name == "dyno_component_access":
                component = arguments.get("component", "")
                action = arguments.get("action", "")
                parameters = arguments.get("parameters", {})

                # Access component based on name
                component_obj = None
                if component == "aios":
                    component_obj = dyno.aios
                elif component == "ai_validation":
                    component_obj = dyno.ai_validation
                elif component == "performance_model":
                    component_obj = dyno.performance_model
                elif component == "hallucination_analysis":
                    component_obj = dyno.hallucination_analysis
                elif component == "live_reality":
                    component_obj = dyno.live_reality
                elif component == "marvin_validator":
                    component_obj = dyno.marvin_validator

                if not component_obj:
                    return [TextContent(
                        type="text",
                        text=json.dumps({"error": f"Component {component} not available"}, indent=2)
                    )]

                # Execute action on component
                if hasattr(component_obj, action):
                    method = getattr(component_obj, action)
                    if callable(method):
                        if parameters:
                            result = method(**parameters)
                        else:
                            result = method()
                    else:
                        result = {"error": f"{action} is not callable"}
                else:
                    result = {"error": f"Component {component} does not have action {action}"}

                return [TextContent(
                    type="text",
                    text=json.dumps(result, indent=2)
                )]

            else:
                return [TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2)
                )]

        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({"error": str(e), "tool": name}, indent=2)
            )]

    async def run_server():
        """Run MCP server"""
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    # Export main for use
    def main():
        """Main entry point"""
        asyncio.run(run_server())

    if __name__ == "__main__":
        main()
else:
    # Fallback if MCP not available
    print("MCP SDK not available. Install with: pip install mcp", file=sys.stderr)
    sys.exit(1)
