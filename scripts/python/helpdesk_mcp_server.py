#!/usr/bin/env python3
"""
Helpdesk MCP Server — Ticket management for Lumina ecosystem.

This MCP server provides tools for:
- Creating helpdesk tickets
- Querying ticket status
- Updating tickets
- Listing open tickets

Tags: #mcp #helpdesk @JARVIS
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Lumina root
LUMINA_ROOT = Path(__file__).parent.parent.parent
TICKETS_DIR = LUMINA_ROOT / "data" / "helpdesk" / "tickets"
TICKETS_DIR.mkdir(parents=True, exist_ok=True)
COUNTER_FILE = LUMINA_ROOT / "data" / "helpdesk" / "ticket_counter.json"


def get_next_ticket_id() -> str:
    """Get next ticket ID."""
    if COUNTER_FILE.exists():
        with open(COUNTER_FILE) as f:
            data = json.load(f)
            counter = data.get("counter", 3000)
    else:
        counter = 3000
    
    next_id = counter + 1
    with open(COUNTER_FILE, "w") as f:
        json.dump({"counter": next_id}, f)
    
    return f"PM{next_id:09d}"


def create_ticket(title: str, description: str, priority: str = "medium", category: str = "general") -> dict:
    """Create a new helpdesk ticket."""
    ticket_id = get_next_ticket_id()
    ticket = {
        "id": ticket_id,
        "title": title,
        "description": description,
        "priority": priority,
        "category": category,
        "status": "open",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    
    ticket_file = TICKETS_DIR / f"{ticket_id}.json"
    with open(ticket_file, "w") as f:
        json.dump(ticket, f, indent=2)
    
    return ticket


def get_ticket(ticket_id: str) -> dict | None:
    """Get a ticket by ID."""
    ticket_file = TICKETS_DIR / f"{ticket_id}.json"
    if ticket_file.exists():
        with open(ticket_file) as f:
            return json.load(f)
    return None


def list_tickets(status: str = None) -> list:
    """List all tickets, optionally filtered by status."""
    tickets = []
    for ticket_file in TICKETS_DIR.glob("*.json"):
        with open(ticket_file) as f:
            ticket = json.load(f)
            if status is None or ticket.get("status") == status:
                tickets.append(ticket)
    return sorted(tickets, key=lambda t: t.get("created_at", ""), reverse=True)


def update_ticket(ticket_id: str, updates: dict) -> dict | None:
    """Update a ticket."""
    ticket = get_ticket(ticket_id)
    if ticket:
        ticket.update(updates)
        ticket["updated_at"] = datetime.now().isoformat()
        
        ticket_file = TICKETS_DIR / f"{ticket_id}.json"
        with open(ticket_file, "w") as f:
            json.dump(ticket, f, indent=2)
        return ticket
    return None


# MCP Server Protocol
def handle_request(request: dict) -> dict:
    """Handle MCP request."""
    method = request.get("method", "")
    params = request.get("params", {})
    
    if method == "initialize":
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {
                "name": "lumina-helpdesk",
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
                    "name": "create_ticket",
                    "description": "Create a new helpdesk ticket",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "Ticket title"},
                            "description": {"type": "string", "description": "Ticket description"},
                            "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]},
                            "category": {"type": "string"}
                        },
                        "required": ["title", "description"]
                    }
                },
                {
                    "name": "get_ticket",
                    "description": "Get a ticket by ID",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string", "description": "Ticket ID (e.g., PM000003001)"}
                        },
                        "required": ["ticket_id"]
                    }
                },
                {
                    "name": "list_tickets",
                    "description": "List helpdesk tickets",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "status": {"type": "string", "enum": ["open", "in_progress", "resolved", "closed"]}
                        }
                    }
                },
                {
                    "name": "update_ticket",
                    "description": "Update a ticket",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "ticket_id": {"type": "string"},
                            "status": {"type": "string"},
                            "notes": {"type": "string"}
                        },
                        "required": ["ticket_id"]
                    }
                }
            ]
        }
    
    elif method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})
        
        if tool_name == "create_ticket":
            result = create_ticket(
                title=args.get("title", "Untitled"),
                description=args.get("description", ""),
                priority=args.get("priority", "medium"),
                category=args.get("category", "general")
            )
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "get_ticket":
            result = get_ticket(args.get("ticket_id", ""))
            if result:
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            return {"content": [{"type": "text", "text": "Ticket not found"}], "isError": True}
        
        elif tool_name == "list_tickets":
            result = list_tickets(args.get("status"))
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        
        elif tool_name == "update_ticket":
            result = update_ticket(args.get("ticket_id", ""), args)
            if result:
                return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
            return {"content": [{"type": "text", "text": "Ticket not found"}], "isError": True}
    
    return {"error": {"code": -32601, "message": f"Unknown method: {method}"}}


def main():
    """Main MCP server loop."""
    # Read JSON-RPC messages from stdin
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
