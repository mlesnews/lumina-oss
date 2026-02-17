#!/usr/bin/env python3
"""
JARVIS Five Senses Explanation

Provides a clear explanation of how JARVIS's five senses correlate with home lab/network infrastructure.

Tags: #JARVIS #FIVE_SENSES #HOMELAB #NETWORK #EXPLANATION
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFiveSenses")


def explain_five_senses():
    """Explain JARVIS's five senses and their home lab correlations"""

    print("")
    print("=" * 80)
    print("🧠 JARVIS FIVE SENSES - HOME LAB/NETWORK CORRELATION")
    print("=" * 80)
    print("")

    # SIGHT
    print("👁️  SIGHT - MDV Live Video & Visual Monitoring")
    print("-" * 80)
    print("What JARVIS Sees:")
    print("  • Desktop/UI monitoring via real-time screen capture")
    print("  • Visual state analysis and problem detection")
    print("  • Can verify operations and detect visual anomalies")
    print("")
    print("🏠 Home Lab Correlation:")
    print("  • Network visualization through monitoring dashboards")
    print("  • Service status dashboards (NAS, pfSense, Docker containers)")
    print("  • Infrastructure monitoring (Grafana, Prometheus, network maps)")
    print("  • Real-time desktop awareness - sees what you see")
    print("")

    # HEARING
    print("👂 HEARING - Voice Transcript Queue & Audio Monitoring")
    print("-" * 80)
    print("What JARVIS Hears:")
    print("  • Voice input from ElevenLabs, Grammarly CLI, voice systems")
    print("  • Operator commands, requests, and feedback")
    print("  • Audio alerts, system notifications, warnings")
    print("")
    print("🏠 Home Lab Correlation:")
    print("  • Network traffic analysis through packet/flow monitoring")
    print("  • Service logs (application, system, health reports)")
    print("  • Alert systems (WOPR, DEFCON, health checks)")
    print("  • Communication channels (chat, notifications, event streams)")
    print("")

    # TOUCH
    print("✋ TOUCH - Input Feedback & System Interaction")
    print("-" * 80)
    print("What JARVIS Feels:")
    print("  • User interactions (mouse, keyboard, drag operations)")
    print("  • System responses and UI feedback")
    print("  • Haptic feedback and interaction patterns")
    print("")
    print("🏠 Home Lab Correlation:")
    print("  • Network latency and responsiveness (ping times, connection quality)")
    print("  • Service response times (how quickly services respond)")
    print("  • System load (CPU, memory, disk I/O pressure)")
    print("  • Infrastructure health (the 'pulse' of your home lab)")
    print("  • VA movement tracking (all drag/move operations show user focus)")
    print("")

    # TASTE
    print("👅 TASTE - Data Quality Analysis")
    print("-" * 80)
    print("What JARVIS Tastes:")
    print("  • Data quality - is it clean, corrupted, incomplete?")
    print("  • Information integrity - detects anomalies, inconsistencies")
    print("  • Data patterns - recognizes trends and quality issues")
    print("")
    print("🏠 Home Lab Correlation:")
    print("  • Database health (PostgreSQL, MySQL data integrity)")
    print("  • Backup quality (completeness and integrity verification)")
    print("  • Configuration validity (configs are valid and consistent)")
    print("  • Data pipeline health (ETL processes, transformations, data flow)")
    print("  • Storage integrity (file system health, RAID status, reliability)")
    print("  • Log quality (analyzes logs for patterns, anomalies, issues)")
    print("")

    # SMELL
    print("👃 SMELL - System Health Monitoring & Problem Detection")
    print("-" * 80)
    print("What JARVIS Smells:")
    print("  • System health - detects 'odors' of problems (errors, warnings)")
    print("  • Problem detection - identifies issues before they become critical")
    print("  • Alert recognition - recognizes patterns indicating system problems")
    print("")
    print("🏠 Home Lab Correlation:")
    print("  • DEFCON monitoring (WOPR status, system alerts, critical errors)")
    print("  • Network health (connectivity problems, bandwidth issues)")
    print("  • Service health (Docker containers, services, application health)")
    print("  • Infrastructure alerts (NAS, pfSense, routers, switches)")
    print("  • Security threats (unauthorized access, anomalies)")
    print("  • Resource exhaustion (CPU, memory, disk, network problems)")
    print("  • Hardware issues (failures, temperature, fan problems)")
    print("")

    # Integration
    print("=" * 80)
    print("🔗 HOW SENSES WORK TOGETHER")
    print("=" * 80)
    print("")
    print("1. SIGHT sees visual state → SMELL detects if something looks wrong")
    print("2. HEARING receives alerts → SMELL analyzes severity → SIGHT verifies visually")
    print("3. TOUCH feels slow responses → TASTE checks data quality → SMELL identifies root cause")
    print("4. SMELL detects problem → SIGHT visualizes it → HEARING alerts operator")
    print("5. TASTE finds bad data → SMELL raises alert → TOUCH verifies system response")
    print("")
    print("=" * 80)
    print("📚 For detailed documentation, see:")
    print("   docs/system/JARVIS_FIVE_SENSES_HOMELAB_MAPPING.md")
    print("=" * 80)
    print("")


if __name__ == "__main__":
    explain_five_senses()
