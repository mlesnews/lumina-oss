#!/usr/bin/env python3
"""
Lumina Security Audit: Service Binding & Perimeter Defense
Part of PROJECT IRON CURTAIN.

This script scans for:
1. Services binding to 0.0.0.0 (Global access) instead of 127.0.0.1 (Local loopback).
2. The presence of known risky ports (e.g., 18789 - Moltbot/Clawdbot).
3. Publicly exposed Lumina internal gateways.

Tags: #SECURITY #AUDIT #IRON_CURTAIN @LUMINA
"""

import socket
import os
import sys
import psutil
from pathlib import Path
from datetime import datetime

# Black-hole list from Clawdbot analysis
RISKY_PORTS = [18789]

def audit_bindings():
    print(f"🔒 LUMINA SERVICE BINDING AUDIT - {datetime.now().isoformat()}")
    print("=" * 60)
    
    findings = []
    
    # 1. Scan for listening ports
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            laddr = conn.laddr
            port = laddr.port
            ip = laddr.ip
            
            # Check for 0.0.0.0 / All Interfaces
            if ip == '0.0.0.0' or ip == '::':
                finding = f"⚠️  UNRESTRICTED BINDING: Port {port} is listening on ALL interfaces ({ip})"
                findings.append(finding)
                print(finding)
            
            # Check for Black-hole ports
            if port in RISKY_PORTS:
                finding = f"🚨 BLACK-HOLE PORT DETECTED: Port {port} (Known AI-agent risk vector) is ACTIVE."
                findings.append(finding)
                print(finding)

    print("-" * 60)
    if not findings:
        print("✅ No critical service binding issues detected.")
    else:
        print(f"❌ {len(findings)} findings requiring attention.")
    
    # 2. Store audit log
    audit_log = Path("data/security/audit_binding_results.json")
    audit_log.parent.mkdir(parents=True, exist_ok=True)
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "findings": findings,
        "status": "NEEDS_ATTENTION" if findings else "HEALTHY"
    }
    
    import json
    with open(audit_log, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Audit results saved to: {audit_log}")

if __name__ == "__main__":
    audit_bindings()
