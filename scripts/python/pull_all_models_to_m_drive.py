#!/usr/bin/env python3
"""
Pull All AI Models to M Drive
Downloads all peak models directly to M drive and configures Ollama to use them

Tags: #M_DRIVE #MODELS #OLLAMA @JARVIS @LUMINA @DOIT
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Peak models to download
PEAK_MODELS = [
    "qwen2.5:72b",
    "qwen2.5:32b",
    "qwen2.5-coder:32b",
    "qwen2.5:14b",
    "qwen2.5-coder:7b",
    "mixtral:8x7b",
    "llama3.2:3b",
    "codellama:13b",
    "mistral:latest",
]

# Additional coding models
CODING_MODELS = [
    "deepseek-coder:6.7b",
    "codellama:7b",
    "phi3:medium",
]

# Additional general models
GENERAL_MODELS = [
    "llama3.2:latest",
    "gemma2:9b",
    "qwen2.5:7b",
]


def set_ollama_models_env(m_drive_path: Path):
    """Set OLLAMA_MODELS environment variable to M drive"""
    print(f"\n⚙️  Setting OLLAMA_MODELS to M drive...")

    try:
        # Set for current session
        os.environ["OLLAMA_MODELS"] = str(m_drive_path)

        # Set permanently
        subprocess.run(
            ["setx", "OLLAMA_MODELS", str(m_drive_path)],
            check=True
        )
        print(f"✅ Set OLLAMA_MODELS={m_drive_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not set environment variable: {e}")
        print(f"   Please manually set: OLLAMA_MODELS={m_drive_path}")
        return False


def verify_m_drive() -> Path:
    """Verify M drive is accessible and return models path"""
    m_drive = Path("M:/Ollama/models")

    # Try to create directory if it doesn't exist
    try:
        m_drive.mkdir(parents=True, exist_ok=True)
        if m_drive.exists():
            print(f"✅ M drive accessible: {m_drive}")
            return m_drive
    except Exception as e:
        print(f"⚠️  M drive path issue: {e}")

    # Try alternative paths
    alt_paths = [
        Path("M:/models"),
        Path("M:/ollama/models"),
        Path("//<NAS_PRIMARY_IP>/homes/mlesn/Ollama/models"),
    ]

    for alt_path in alt_paths:
        try:
            alt_path.mkdir(parents=True, exist_ok=True)
            if alt_path.exists():
                print(f"✅ Using alternative path: {alt_path}")
                return alt_path
        except:
            pass

    print("❌ M drive not accessible")
    return None


def list_available_models() -> List[str]:
    """List currently available models in Ollama"""
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]  # Skip header
            models = []
            for line in lines:
                if line.strip():
                    model_name = line.split()[0]
                    models.append(model_name)
            return models
    except Exception as e:
        print(f"⚠️  Error listing models: {e}")
    return []


def pull_model_to_m_drive(model_name: str, m_drive_path: Path) -> Dict[str, Any]:
    """Pull a model to M drive using IDM ONLY (no Ollama fallback)"""
    print(f"\n📥 Pulling {model_name}...")

    # IDM is mandatory - no fallback
    try:
        from jarvis_ollama_idm_pull import OllamaIDMPuller
        idm_puller = OllamaIDMPuller(project_root)

        if not idm_puller.idm or not idm_puller.idm.is_available():
            print(f"   ❌ IDM not available - download aborted")
            return {
                "success": False,
                "method": "idm",
                "model": model_name,
                "error": "IDM not available - Internet Download Manager is required"
            }

        print(f"   🚀 Using IDM for download...")
        result = idm_puller.pull_model_with_idm(
            model_name,
            endpoint="http://localhost:11434",
            destination=m_drive_path
        )

        if result.get("success"):
            print(f"   ✅ {model_name} queued in IDM")
            print(f"   📊 Monitor download progress in IDM application")
            return {"success": True, "method": "idm", "model": model_name}
        else:
            print(f"   ❌ {model_name} failed to queue in IDM")
            return {
                "success": False,
                "method": "idm",
                "model": model_name,
                "error": result.get("error", "IDM queue failed")
            }
    except ImportError as e:
        print(f"   ❌ IDM integration not available: {e}")
        return {
            "success": False,
            "method": "idm",
            "model": model_name,
            "error": f"IDM integration not available: {e}"
        }
    except Exception as e:
        print(f"   ❌ Error with IDM: {e}")
        return {
            "success": False,
            "method": "idm",
            "model": model_name,
            "error": str(e)
        }


def verify_idm_available() -> bool:
    """Verify IDM is available before proceeding"""
    try:
        from jarvis_ollama_idm_pull import OllamaIDMPuller
        idm_puller = OllamaIDMPuller(project_root)
        if idm_puller.idm and idm_puller.idm.is_available():
            print("✅ IDM is available and ready")
            return True
        else:
            print("❌ IDM is not available")
            print("   Please ensure Internet Download Manager is installed and running")
            return False
    except Exception as e:
        print(f"❌ IDM integration error: {e}")
        return False


def pull_all_models(
    model_categories: Dict[str, List[str]] = None,
    skip_existing: bool = True
) -> Dict[str, Any]:
    """Pull all models to M drive using IDM ONLY"""
    print("=" * 80)
    print("🚀 PULLING ALL AI MODELS TO M DRIVE (IDM ONLY)")
    print("=" * 80)

    # Verify IDM is available FIRST (mandatory)
    if not verify_idm_available():
        print("\n❌ Internet Download Manager is required for all downloads")
        print("   Please install IDM and ensure it's running, then try again")
        return {"success": False, "error": "IDM not available"}

    # Verify M drive
    m_drive_path = verify_m_drive()
    if not m_drive_path:
        print("\n❌ M drive not accessible. Please run setup first:")
        print("   python scripts\\python\\setup_m_drive_models_with_idm.py --setup")
        return {"success": False, "error": "M drive not accessible"}

    # Set environment variable
    set_ollama_models_env(m_drive_path)

    # Get existing models
    existing_models = list_available_models()
    print(f"\n📦 Currently available: {len(existing_models)} models")

    # Define model categories
    if model_categories is None:
        model_categories = {
            "peak": PEAK_MODELS,
            "coding": CODING_MODELS,
            "general": GENERAL_MODELS,
        }

    # Collect all models to download
    all_models = []
    for category, models in model_categories.items():
        all_models.extend(models)

    # Filter out existing if requested
    if skip_existing:
        models_to_download = []
        for model in all_models:
            base_name = model.split(":")[0]
            if not any(base_name in existing for existing in existing_models):
                models_to_download.append(model)
            else:
                print(f"⏭️  Skipping {model} (already available)")
    else:
        models_to_download = all_models

    print(f"\n📥 Models to download: {len(models_to_download)}")
    print(f"   Total models: {len(all_models)}")
    print(f"   Already available: {len(all_models) - len(models_to_download)}")

    if not models_to_download:
        print("\n✅ All models already available!")
        return {"success": True, "downloaded": 0, "skipped": len(all_models)}

    # Download models
    results = {}
    success_count = 0

    for model_name in models_to_download:
        result = pull_model_to_m_drive(model_name, m_drive_path)
        results[model_name] = result
        if result.get("success"):
            success_count += 1

    # Summary
    print("\n" + "=" * 80)
    print("📊 DOWNLOAD SUMMARY")
    print("=" * 80)
    print(f"✅ Successfully downloaded: {success_count}/{len(models_to_download)}")
    print(f"⏭️  Skipped (already available): {len(all_models) - len(models_to_download)}")
    print(f"📁 Models location: {m_drive_path}")

    # Save results
    results_file = project_root / "M_DRIVE_MODELS_PULL_RESULTS.json"
    summary = {
        "timestamp": datetime.now().isoformat(),
        "m_drive_path": str(m_drive_path),
        "total_models": len(all_models),
        "downloaded": success_count,
        "skipped": len(all_models) - len(models_to_download),
        "failed": len(models_to_download) - success_count,
        "results": results
    }

    with open(results_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)

    print(f"\n📄 Results saved to: {results_file}")
    print(f"\n💡 Next steps:")
    print("   1. Verify models: ollama list")
    print("   2. Test a model: ollama run qwen2.5:32b")
    print("   3. Models are now on M drive and ready to use!")

    return summary


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pull All AI Models to M Drive",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Pull all peak models
  python pull_all_models_to_m_drive.py --all

  # Pull only peak models
  python pull_all_models_to_m_drive.py --peak

  # Pull specific models
  python pull_all_models_to_m_drive.py --models qwen2.5:72b qwen2.5:32b

  # Note: All downloads use IDM only - no Ollama fallback
        """
    )
    parser.add_argument("--all", action="store_true", help="Pull all models (peak + coding + general)")
    parser.add_argument("--peak", action="store_true", help="Pull only peak models")
    parser.add_argument("--coding", action="store_true", help="Pull only coding models")
    parser.add_argument("--general", action="store_true", help="Pull only general models")
    parser.add_argument("--models", nargs="+", help="Pull specific models")
    parser.add_argument("--no-skip", action="store_true", help="Don't skip existing models")

    args = parser.parse_args()

    # Determine which models to pull
    model_categories = {}

    if args.all:
        model_categories = {
            "peak": PEAK_MODELS,
            "coding": CODING_MODELS,
            "general": GENERAL_MODELS,
        }
    elif args.peak:
        model_categories = {"peak": PEAK_MODELS}
    elif args.coding:
        model_categories = {"coding": CODING_MODELS}
    elif args.general:
        model_categories = {"general": GENERAL_MODELS}
    elif args.models:
        model_categories = {"custom": args.models}
    else:
        # Default: peak models only
        model_categories = {"peak": PEAK_MODELS}

    pull_all_models(
        model_categories=model_categories,
        skip_existing=not args.no_skip
    )


if __name__ == "__main__":

    main()