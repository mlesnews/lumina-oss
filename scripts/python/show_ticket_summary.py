#!/usr/bin/env python3
"""
Show Ticket Summary
Quick summary of ticket counts and status.

Tags: #HELPDESK #TICKETS #SUMMARY
"""

import json
import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_ticket_resolution_processor import JARVISTicketResolutionProcessor
except ImportError:
    print("❌ Could not import ticket processor")
    sys.exit(1)

project_root = script_dir.parent.parent
processor = JARVISTicketResolutionProcessor(project_root)

status = processor.get_queue_status()

print("="*80)
print("📊 TICKET QUEUE SUMMARY")
print("="*80)
print()
print(f"Total Tickets: {status['total']}")
print(f"Active Queue: {status['active_queue']} (open: {status['open']}, assigned: {status['assigned']}, in_progress: {status['in_progress']})")
print(f"Resolved: {status['resolved']}")
print(f"Closed: {status['closed']}")
print()
print("By Status:")
print(f"  Open: {status['open']}")
print(f"  Assigned: {status['assigned']}")
print(f"  In Progress: {status['in_progress']}")
print(f"  Resolved: {status['resolved']}")
print()
print("By Priority:")
for priority, count in status['by_priority'].items():
    print(f"  {priority}: {count}")
print()
print("By Team:")
for team, count in status['by_team'].items():
    print(f"  {team}: {count}")
print()
print("="*80)
print()
print("💡 Note: The 2,100 IDE problems are grouped into ONE ticket (HELPDESK-0011)")
print("   We did NOT create 2,000 individual tickets - we grouped them efficiently.")
