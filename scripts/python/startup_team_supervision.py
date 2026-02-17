#!/usr/bin/env python3
"""
Startup Team Supervision Monitor

Starts active team supervision monitoring on system startup.
Ensures managers are supervised and subordinates report status.

Tags: #MANAGEMENT #SUPERVISION #STARTUP #REQUIRED @PEAK @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("StartupTeamSupervision")

from active_team_supervision_monitor import run_active_supervision


if __name__ == "__main__":
    logger.info("🚀 Starting Active Team Supervision Monitor...")
    logger.info("   @PEAK: Continuous supervision and reporting enabled")
    logger.info("   A) Managers supervised by higher-level AI/agents")
    logger.info("   B) Subordinates report to managers/leads")
    logger.info("")

    # Run active supervision (continuous)
    run_active_supervision(check_interval=300)  # 5 minutes
