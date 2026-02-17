#!/usr/bin/env python3
"""
Show Actual Ollama Model File Names

Displays the actual file names and paths for Ollama models so you can
easily identify LLM model types by their actual file names.
"""

import json
import requests
import sys
import subprocess
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class OllamaModelFileInspector:
    """Inspect actual Ollama model file names and paths"""

    def __init__(self):
        self.endpoints = [
            "http://localhost:11434",
            "http://kaiju_no_8:11437",
            "http://localhost:11437",
            "http://127.0.0.1:11437",
        ]
        self.active_endpoint = None

    def find_active_endpoint(self) -> Optional[str]:
        """Find active Ollama endpoint"""
        for endpoint in self.endpoints:
            try:
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    self.active_endpoint = endpoint
                    return endpoint
            except Exception:
                continue
        return None

    def get_ollama_models_dir(self) -> Optional[Path]:
        """Get Ollama models directory"""
        # Common Ollama storage locations
        possible_paths = [
            Path.home() / ".ollama" / "models",
            Path(os.path.expandvars("%USERPROFILE%")) / ".ollama" / "models",  # Windows
            Path("/root/.ollama/models"),  # Docker/Linux
            Path("/var/lib/ollama/models"),  # System installation
        ]

        for path in possible_paths:
            if path.exists():
                return path

        # Try to get from Ollama process
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(
                    ["wmic", "process", "where", "name='ollama.exe'", "get", "executablepath"],
                    capture_output=True, text=True
                )
            else:
                result = subprocess.run(
                    ["ps", "aux"], capture_output=True, text=True
                )
                # Parse for ollama binary location
        except:
            pass

        return None

    def get_model_files(self, model_name: str) -> Dict[str, Any]:
        """Get actual file information for a model"""
        if not self.active_endpoint:
            return {}

        try:
            # Get model details from API
            response = requests.post(
                f"{self.active_endpoint}/api/show",
                json={"name": model_name},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()

                file_info = {
                    "model_tag": model_name,
                    "digest": data.get("digest", ""),
                    "size_bytes": data.get("size", 0),
                    "size_gb": round(data.get("size", 0) / (1024**3), 2),
                    "modelfile": data.get("modelfile", ""),
                    "parameters": data.get("parameters", ""),
                    "family": data.get("family", ""),
                    "families": data.get("families", []),
                    "format": data.get("format", ""),
                    "parent_model": data.get("parent_model", ""),
                }

                # Parse modelfile for actual file references
                modelfile = data.get("modelfile", "")

                # Extract FROM line (base model)
                for line in modelfile.split("\n"):
                    line = line.strip()
                    if line.startswith("FROM"):
                        file_info["from_model"] = line.replace("FROM", "").strip()

                # Construct actual file paths based on digest
                digest = data.get("digest", "")
                if digest:
                    # Ollama stores models in: ~/.ollama/models/blobs/{digest}
                    models_dir = self.get_ollama_models_dir()
                    if models_dir:
                        blob_path = models_dir / "blobs" / digest
                        file_info["actual_file_path"] = str(blob_path) if blob_path.exists() else None
                        file_info["file_name"] = digest

                    # Also check manifests
                    manifest_path = models_dir / "manifests" / model_name if models_dir else None
                    if manifest_path and manifest_path.exists():
                        file_info["manifest_path"] = str(manifest_path)

                return file_info
        except Exception as e:
            print(f"⚠️  Error getting file info for {model_name}: {e}")
            return {}

    def list_all_models_with_files(self) -> List[Dict[str, Any]]:
        """List all models with their actual file information"""
        if not self.active_endpoint:
            if not self.find_active_endpoint():
                print("❌ No active Ollama endpoint found")
                return []

        try:
            response = requests.get(f"{self.active_endpoint}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                models_info = []

                for model in data.get("models", []):
                    model_name = model.get("name", "")
                    file_info = self.get_model_files(model_name)

                    model_data = {
                        "name": model_name,
                        "tag": model_name,
                        "digest": model.get("digest", ""),
                        "size_bytes": model.get("size", 0),
                        "size_gb": round(model.get("size", 0) / (1024**3), 2),
                        "modified_at": model.get("modified_at", ""),
                        "file_info": file_info,
                    }
                    models_info.append(model_data)

                return models_info
        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []

    def generate_file_report(self) -> str:
        """Generate comprehensive file name report"""
        models = self.list_all_models_with_files()
        models_dir = self.get_ollama_models_dir()

        report = []
        report.append("=" * 100)
        report.append("OLLAMA MODEL ACTUAL FILE NAMES REPORT")
        report.append("=" * 100)
        report.append(f"Endpoint: {self.active_endpoint}")
        report.append(f"Models Directory: {models_dir}")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 100)
        report.append("")

        if not models:
            report.append("❌ No models found on endpoint")
            return "\n".join(report)

        for model in models:
            report.append("─" * 100)
            report.append(f"📦 MODEL: {model['name']}")
            report.append(f"   Tag/Name: {model['tag']}")
            report.append(f"   Size: {model['size_gb']} GB ({model['size_bytes']:,} bytes)")
            report.append(f"   Digest: {model['digest']}")
            report.append(f"   Modified: {model.get('modified_at', 'N/A')}")
            report.append("")

            file_info = model.get("file_info", {})
            if file_info:
                report.append("   📂 FILE INFORMATION:")
                report.append(f"      🔑 Digest: {file_info.get('digest', 'N/A')}")

                if file_info.get("actual_file_path"):
                    report.append(f"      📁 Actual File Path: {file_info['actual_file_path']}")
                    report.append(f"      📄 File Name: {file_info.get('file_name', 'N/A')}")

                if file_info.get("manifest_path"):
                    report.append(f"      📋 Manifest Path: {file_info['manifest_path']}")

                if file_info.get("from_model"):
                    report.append(f"      🔗 Base Model (FROM): {file_info['from_model']}")

                report.append(f"      🏷️  Family: {file_info.get('family', 'N/A')}")
                report.append(f"      📐 Format: {file_info.get('format', 'N/A')}")

                if file_info.get("families"):
                    report.append(f"      🧬 Families: {', '.join(file_info['families'])}")

                report.append("")

                # Show modelfile
                if file_info.get("modelfile"):
                    report.append("   📝 MODELFILE:")
                    for line in file_info["modelfile"].split("\n")[:10]:  # First 10 lines
                        if line.strip():
                            report.append(f"      {line}")
                    report.append("")

        report.append("=" * 100)
        report.append("")
        report.append("💡 HOW TO IDENTIFY MODEL FILES:")
        report.append("   • Ollama stores models in: ~/.ollama/models/blobs/{digest}")
        report.append("   • Model tag/name is stored in: ~/.ollama/models/manifests/{model_name}")
        report.append("   • Digest is the actual unique file identifier")
        report.append("   • Use 'ollama show {model_name}' to see full file details")
        report.append("=" * 100)

        return "\n".join(report)

    def show_model_file_structure(self):
        """Show the actual file system structure of Ollama models"""
        models_dir = self.get_ollama_models_dir()

        if not models_dir:
            print("❌ Could not locate Ollama models directory")
            return

        print(f"\n📂 OLLAMA MODELS DIRECTORY STRUCTURE:")
        print(f"   {models_dir}")
        print()

        # List blobs directory
        blobs_dir = models_dir / "blobs"
        if blobs_dir.exists():
            print(f"📦 BLOBS (Actual Model Files):")
            blob_files = list(blobs_dir.glob("*"))[:20]  # First 20
            for blob_file in blob_files:
                size_mb = blob_file.stat().st_size / (1024**2) if blob_file.is_file() else 0
                print(f"   🔑 {blob_file.name[:16]}... ({size_mb:.1f} MB)")
            if len(list(blobs_dir.glob("*"))) > 20:
                print(f"   ... and {len(list(blobs_dir.glob('*'))) - 20} more files")
            print()

        # List manifests directory
        manifests_dir = models_dir / "manifests"
        if manifests_dir.exists():
            print(f"📋 MANIFESTS (Model Tags/Names):")
            manifest_files = list(manifests_dir.glob("*"))
            for manifest_file in manifest_files:
                if manifest_file.is_file():
                    try:
                        with open(manifest_file, 'r') as f:
                            manifest_data = json.load(f)
                            digest = manifest_data.get("config", {}).get("digest", "unknown")
                            print(f"   🏷️  {manifest_file.name} → {digest[:16]}...")
                    except:
                        print(f"   🏷️  {manifest_file.name}")
            print()


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Show Actual Ollama Model File Names")
    parser.add_argument("action", choices=["list", "report", "files"], 
                       help="Action: list (simple), report (detailed), files (filesystem)")

    args = parser.parse_args()

    inspector = OllamaModelFileInspector()

    if args.action == "list":
        models = inspector.list_all_models_with_files()
        print("\n📦 AVAILABLE MODELS:")
        print("=" * 80)
        for model in models:
            print(f"\n✅ {model['name']}")
            print(f"   Size: {model['size_gb']} GB")
            print(f"   Digest: {model['digest']}")
            file_info = model.get('file_info', {})
            if file_info.get('actual_file_path'):
                print(f"   File: {file_info['actual_file_path']}")

    elif args.action == "report":
        report = inspector.generate_file_report()
        print(report)

    elif args.action == "files":
        inspector.show_model_file_structure()
        inspector.find_active_endpoint()
        if inspector.active_endpoint:
            report = inspector.generate_file_report()
            print(report)


if __name__ == "__main__":


    main()