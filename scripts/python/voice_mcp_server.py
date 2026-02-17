#!/usr/bin/env python3
"""
Voice MCP Server — Text-to-speech and voice synthesis for Lumina.

This MCP server provides tools for:
- Text-to-speech synthesis (via ElevenLabs or local engines)
- Voice status and configuration
- Audio file generation

Tags: #mcp #voice #tts @JARVIS
"""

import json
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Any

# Lumina root
LUMINA_ROOT = Path(__file__).parent.parent.parent
AUDIO_DIR = LUMINA_ROOT / "data" / "voice" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)


def get_voice_status() -> dict:
    """Get current voice/TTS engine status."""
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    return {
        "elevenlabs_configured": bool(elevenlabs_key),
        "audio_output_dir": str(AUDIO_DIR),
        "timestamp": datetime.now().isoformat()
    }


def speak_text(text: str, voice_id: str = "default", output_file: str = None) -> dict:
    """
    Synthesize speech from text.
    
    Currently returns a stub - integration with ElevenLabs Docker MCP 
    or local TTS engine can be added.
    """
    # Check if ElevenLabs is configured
    elevenlabs_key = os.environ.get("ELEVENLABS_API_KEY")
    
    if not elevenlabs_key:
        return {
            "status": "not_configured",
            "message": "ElevenLabs API key not set. Set ELEVENLABS_API_KEY environment variable or use Docker MCP ElevenLabs server.",
            "text": text[:100] + "..." if len(text) > 100 else text
        }
    
    # Placeholder for actual TTS implementation
    # The ElevenLabs MCP server in Docker handles actual synthesis
    return {
        "status": "delegated",
        "message": "Use the ElevenLabs MCP server (via Docker MCP Toolkit) for actual voice synthesis",
        "text": text[:100] + "..." if len(text) > 100 else text,
        "voice_id": voice_id
    }


def list_voices() -> list:
    """List available voices."""
    # Placeholder - would integrate with ElevenLabs API
    return [
        {"id": "default", "name": "Default System Voice", "provider": "system"},
        {"id": "elevenlabs", "name": "ElevenLabs (via Docker MCP)", "provider": "elevenlabs", "requires_api_key": True}
    ]


# MCP Server Protocol
def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "lumina-voice",
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
                    "name": "get_voice_status",
                    "description": "Get current voice/TTS engine configuration status",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                },
                {
                    "name": "speak",
                    "description": "Synthesize speech from text (requires ElevenLabs API key or Docker MCP)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "text": {"type": "string", "description": "Text to speak"},
                            "voice_id": {"type": "string", "description": "Voice ID to use"},
                            "output_file": {"type": "string", "description": "Optional output file path"}
                        },
                        "required": ["text"]
                    }
                },
                {
                    "name": "list_voices",
                    "description": "List available voice options",
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
        
        if tool_name == "get_voice_status":
            result = get_voice_status()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "speak":
            result = speak_text(
                text=args.get("text", ""),
                voice_id=args.get("voice_id", "default"),
                output_file=args.get("output_file")
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "list_voices":
            result = list_voices()
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
