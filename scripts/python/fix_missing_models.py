#!/usr/bin/env python3
"""
Fix Missing Models - Pull required models to local Ollama
                    -LUM THE MODERN
"""
import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Models needed for ULTRON Local
ultron_models = ["qwen2.5:72b", "llama3.2:3b", "smollm:135m"]

print("=" * 80)
print("🔧 FIXING MISSING MODELS")
print("=" * 80)
print("\n📥 Pulling models to local Ollama...")

for model in ultron_models:
    print(f"\n📥 Pulling {model}...")
    try:
        result = subprocess.run(
            ["ollama", "pull", model],
            capture_output=True,
            text=True,
            timeout=3600  # 1 hour timeout
        )
        if result.returncode == 0:
            print(f"   ✅ {model} pulled successfully")
        else:
            print(f"   ⚠️  {model} pull failed: {result.stderr[:200]}")
    except subprocess.TimeoutExpired:
        print(f"   ⚠️  {model} pull timed out (model may be very large)")
    except Exception as e:
        print(f"   ❌ {model} pull error: {e}")

print("\n✅ Model pull complete!")
print("=" * 80)
