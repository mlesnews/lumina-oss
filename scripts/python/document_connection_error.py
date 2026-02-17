#!/usr/bin/env python3
"""
Document Connection Error - ECONNRESET
Tracks and documents connection errors for #AIMLSEA analysis
"""

import sys
from pathlib import Path
from datetime import datetime
import json

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

print("=" * 70)
print("Connection Error Documentation")
print("Request ID: 5dc5f5d5-693b-46e7-ad1c-bf7a57d532e6")
print("=" * 70)
print()

error_info = {
    "request_id": "5dc5f5d5-693b-46e7-ad1c-bf7a57d532e6",
    "error_type": "ConnectError",
    "error_message": "[aborted] read ECONNRESET",
    "timestamp": datetime.now().isoformat(),
    "source": "Cursor IDE AI Streaming Connection",
    "component": "streamAiConnect",
    "severity": "HIGH",
    "impact": "AI model connection aborted/reset",
    "likely_cause": "Connection to ULTRON (localhost:11434) or KAIJU (<NAS_PRIMARY_IP>:11434) was reset",
    "retry_mechanism": "Should trigger retry manager",
    "tags": ["#AIMLSEA", "#CONNECTION_ERROR", "#RETRY_MANAGER", "@JARVIS", "@v3"]
}

print("ERROR DETAILS:")
print("-" * 70)
print(f"Request ID: {error_info['request_id']}")
print(f"Error Type: {error_info['error_type']}")
print(f"Error Message: {error_info['error_message']}")
print(f"Timestamp: {error_info['timestamp']}")
print(f"Source: {error_info['source']}")
print(f"Component: {error_info['component']}")
print(f"Severity: {error_info['severity']}")
print()

print("ANALYSIS:")
print("-" * 70)
print("ECONNRESET indicates:")
print("  • Connection was established but then reset/aborted")
print("  • Could be network issue, timeout, or server-side abort")
print("  • Common with streaming connections (AI model responses)")
print()

print("LIKELY CAUSES:")
print("-" * 70)
print("  1. ULTRON (localhost:11434) connection reset")
print("     - Ollama instance may have restarted")
print("     - Model loading timeout")
print("     - Resource exhaustion")
print()
print("  2. KAIJU (<NAS_PRIMARY_IP>:11434) connection reset")
print("     - NAS network issue")
print("     - NAS Ollama instance restart")
print("     - Network timeout")
print()
print("  3. Cursor IDE streaming timeout")
print("     - Response too slow")
print("     - Connection idle timeout")
print("     - Client-side abort")
print()

print("RECOMMENDED ACTIONS:")
print("-" * 70)
print("  1. Check ULTRON status:")
print("     - Verify Ollama is running: curl http://localhost:11434/api/tags")
print("     - Check model availability")
print("     - Verify resources (CPU, RAM)")
print()
print("  2. Check KAIJU status:")
print("     - Verify NAS connectivity: ping <NAS_PRIMARY_IP>")
print("     - Check NAS Ollama instance")
print("     - Verify network stability")
print()
print("  3. Retry mechanism:")
print("     - Should trigger cursor_chat_retry_manager")
print("     - Exponential backoff recommended")
print("     - Circuit breaker pattern for repeated failures")
print()

print("=" * 70)
print("#AIMLSEA RESPONSIBILITY")
print("=" * 70)
print()
print("This error falls under #AIMLSEA responsibilities:")
print("  • Design retry mechanisms (exponential, linear, fibonacci)")
print("  • Implement circuit breaker patterns")
print("  • Request ID correlation for distributed tracing")
print("  • Network resilience and error recovery")
print("  • Observability and monitoring")
print()

# Save error documentation
error_log_dir = project_root / "data" / "connection_errors"
error_log_dir.mkdir(parents=True, exist_ok=True)
error_log_file = error_log_dir / f"error_{error_info['request_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

with open(error_log_file, 'w') as f:
    json.dump(error_info, f, indent=2)

print(f"✅ Error documented: {error_log_file}")
print()
print("=" * 70)
