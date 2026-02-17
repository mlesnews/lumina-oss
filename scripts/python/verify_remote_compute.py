#!/usr/bin/env python3
"""Verify remote compute deployment"""
from jarvis_remote_renderer import HybridRenderer

r = HybridRenderer()
print("✅ Remote renderer initialized")
print(f"   Remote enabled: {r.use_remote}")
print(f"   Render endpoint: {r.remote_service.render_endpoint or 'Not configured'}")
