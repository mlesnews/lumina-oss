#!/usr/bin/env python3
"""Process session summary through SYPHON"""
import json
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from jarvis_syphon_current_chat_session import JarvisSyphonCurrentChatSession

# Read session summary
summary_file = project_root / "data" / "syphon" / "current_chat_sessions" / "session_summary_20260110.md"
content = summary_file.read_text(encoding='utf-8')

# Process through SYPHON
syphon = JarvisSyphonCurrentChatSession(project_root)
intelligence = syphon.syphon_current_session(content)

print("\n✅ JARVIS @SYPHON: Session summary processed successfully!")
print(f"   Intelligence extracted and saved")
