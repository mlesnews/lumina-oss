#!/usr/bin/env python3
"""
Complete M Drive Setup with IDM Integration
Maps NAS drives to M drive, moves all AI models, and configures IDM for downloads

Tags: #M_DRIVE #IDM #MODELS #NAS @JARVIS @LUMINA @DOIT
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from jarvis_ollama_idm_pull import OllamaIDMPuller
    IDM_AVAILABLE = True
except ImportError:
    IDM_AVAILABLE = False
    print("⚠️  IDM integration not available - will use fallback")


class MDriveModelManager:
    """
    Complete M Drive Model Management with IDM Integration
    - Maps NAS drives to M drive
    - Moves all AI models to M drive
    - Configures IDM for all downloads
    - Sets up Ollama to use M drive
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.nas_ip = "<NAS_PRIMARY_IP>"
        self.nas_paths = [
            f"\\\\{self.nas_ip}\\volume1\\Jarvis\\Ollama\\Models",
            f"\\\\{self.nas_ip}\\homes\\mlesn\\Ollama\\models",
            f"\\\\{self.nas_ip}\\models",
            f"\\\\DS2118PLUS\\AI-Models",
        ]
        self.m_drive_letter = "M:"
        self.m_drive_path = Path("M:/Ollama/models")

        # Initialize IDM puller if available
        self.idm_puller = None
        if IDM_AVAILABLE:
            try:
                self.idm_puller = OllamaIDMPuller(project_root)
                print("✅ IDM integration available")
            except Exception as e:
                print(f"⚠️  IDM initialization failed: {e}")

    def map_m_drive(self) -> bool:
        """Map NAS to M drive using multiple methods"""
        print("\n" + "=" * 80)
        print("🗺️  MAPPING NAS TO M DRIVE")
        print("=" * 80)

        # Check if M drive already mapped
        if Path(self.m_drive_letter).exists():
            print(f"✅ M drive already mapped: {Path(self.m_drive_letter)}")
            return True

        # Try each NAS path
        for nas_path in self.nas_paths:
            print(f"\n🔍 Trying to map M: to {nas_path}...")

            # Method 1: net use command
            try:
                result = subprocess.run(
                    ["net", "use", self.m_drive_letter, nas_path, "/persistent:yes"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"✅ Successfully mapped M: to {nas_path}")
                    # Verify
                    if Path(self.m_drive_letter).exists():
                        return True
            except Exception as e:
                print(f"   ⚠️  net use failed: {e}")

            # Method 2: PowerShell New-PSDrive
            try:
                ps_cmd = f'New-PSDrive -Name "M" -PSProvider FileSystem -Root "{nas_path}" -Persist -ErrorAction Stop'
                result = subprocess.run(
                    ["powershell", "-Command", ps_cmd],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"✅ Successfully mapped M: via PowerShell to {nas_path}")
                    if Path(self.m_drive_letter).exists():
                        return True
            except Exception as e:
                print(f"   ⚠️  PowerShell mapping failed: {e}")

        # If direct mapping failed, try UNC path
        print("\n⚠️  Direct mapping failed. Using UNC path...")
        for nas_path in self.nas_paths:
            if os.path.exists(nas_path):
                print(f"✅ NAS accessible at: {nas_path}")
                # Create M drive directory structure
                self.m_drive_path = Path(nas_path) / "Ollama" / "models"
                self.m_drive_path.mkdir(parents=True, exist_ok=True)
                print(f"✅ Using UNC path: {self.m_drive_path}")
                return True

        print("❌ Could not map M drive. Please map manually:")
        print(f"   net use M: {self.nas_paths[0]} /persistent:yes")
        return False

    def find_all_ai_models(self) -> Dict[str, List[Path]]:
        """Find all AI models in common locations"""
        print("\n" + "=" * 80)
        print("🔍 FINDING ALL AI MODELS")
        print("=" * 80)

        model_locations = {
            "ollama": [],
            "huggingface": [],
            "gguf": [],
            "other": []
        }

        # Common model locations
        search_paths = [
            Path.home() / ".ollama" / "models",
            Path.home() / ".cache" / "huggingface",
            Path("C:/Users/Public/.ollama/models"),
            Path("D:/Ollama/models"),
            Path("E:/models"),
            Path("C:/models"),
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            print(f"\n📁 Searching: {search_path}")

            # Find Ollama models (blobs, manifests)
            for pattern in ["blobs", "manifests", "models"]:
                path = search_path / pattern
                if path.exists():
                    model_locations["ollama"].append(path)
                    print(f"   ✅ Found Ollama {pattern}: {path}")

            # Find GGUF files
            try:
                for gguf_file in search_path.rglob("*.gguf"):
                    model_locations["gguf"].append(gguf_file)
                    if len(model_locations["gguf"]) <= 5:  # Show first 5
                        print(f"   ✅ Found GGUF: {gguf_file.name}")
            except Exception as e:
                pass

            # Find HuggingFace models
            hf_path = search_path / "hub"
            if hf_path.exists():
                model_locations["huggingface"].append(hf_path)
                print(f"   ✅ Found HuggingFace cache: {hf_path}")

        print(f"\n📊 Summary:")
        print(f"   Ollama models: {len(model_locations['ollama'])} locations")
        print(f"   GGUF files: {len(model_locations['gguf'])} files")
        print(f"   HuggingFace: {len(model_locations['huggingface'])} locations")

        return model_locations

    def move_models_to_m_drive(self, model_locations: Dict[str, List[Path]]) -> bool:
        """Move all models to M drive using robocopy for reliability"""
        print("\n" + "=" * 80)
        print("📦 MOVING MODELS TO M DRIVE")
        print("=" * 80)

        # Ensure M drive directory exists
        self.m_drive_path.mkdir(parents=True, exist_ok=True)
        print(f"📁 M drive models path: {self.m_drive_path}")

        success_count = 0
        total_count = 0

        # Move Ollama models
        for ollama_path in model_locations["ollama"]:
            if not ollama_path.exists():
                continue

            total_count += 1
            dest_path = self.m_drive_path / ollama_path.name

            print(f"\n📦 Moving Ollama {ollama_path.name}...")
            print(f"   From: {ollama_path}")
            print(f"   To: {dest_path}")

            # Use robocopy for network transfers (more reliable)
            try:
                result = subprocess.run(
                    [
                        "robocopy",
                        str(ollama_path.parent),
                        str(self.m_drive_path),
                        ollama_path.name,
                        "/E",  # Copy subdirectories
                        "/R:3",  # Retry 3 times
                        "/W:5",  # Wait 5 seconds between retries
                        "/MT:4",  # Multi-threaded (4 threads)
                        "/NP",  # No progress (cleaner output)
                    ],
                    capture_output=True,
                    text=True,
                    timeout=3600  # 1 hour timeout
                )

                # robocopy returns 0-7 for success, 8+ for errors
                if result.returncode < 8:
                    print(f"   ✅ Successfully moved")
                    success_count += 1
                else:
                    print(f"   ⚠️  robocopy returned code: {result.returncode}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

        # Move GGUF files
        for gguf_file in model_locations["gguf"]:
            total_count += 1
            dest_file = self.m_drive_path / "gguf" / gguf_file.name

            print(f"\n📦 Moving GGUF: {gguf_file.name}...")
            print(f"   From: {gguf_file}")
            print(f"   To: {dest_file}")

            try:
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(gguf_file, dest_file)
                print(f"   ✅ Successfully copied")
                success_count += 1
            except Exception as e:
                print(f"   ❌ Error: {e}")

        print(f"\n📊 Moved {success_count}/{total_count} model locations")
        return success_count > 0

    def configure_ollama_for_m_drive(self):
        """Configure Ollama to use M drive"""
        print("\n" + "=" * 80)
        print("⚙️  CONFIGURING OLLAMA FOR M DRIVE")
        print("=" * 80)

        # Set environment variable
        try:
            subprocess.run(
                ["setx", "OLLAMA_MODELS", str(self.m_drive_path)],
                check=True
            )
            print(f"✅ Set OLLAMA_MODELS={self.m_drive_path}")
        except Exception as e:
            print(f"⚠️  Could not set environment variable: {e}")
            print(f"   Please manually set: OLLAMA_MODELS={self.m_drive_path}")

        # Create symlink if possible (requires admin)
        local_ollama = Path.home() / ".ollama" / "models"
        if local_ollama.exists() and not local_ollama.is_symlink():
            try:
                # Backup existing
                backup = local_ollama.with_suffix('.backup')
                if backup.exists():
                    shutil.rmtree(backup)
                shutil.move(str(local_ollama), str(backup))

                # Create symlink
                subprocess.run(
                    ["mklink", "/D", str(local_ollama), str(self.m_drive_path)],
                    shell=True,
                    check=True
                )
                print(f"✅ Created symlink: {local_ollama} -> {self.m_drive_path}")
            except Exception as e:
                print(f"⚠️  Could not create symlink (may need admin): {e}")
                # Restore backup
                if backup.exists():
                    shutil.move(str(backup), str(local_ollama))

    def download_models_with_idm(self, model_list: List[str]) -> Dict[str, Any]:
        """Download models using IDM ONLY (mandatory)"""
        print("\n" + "=" * 80)
        print("📥 DOWNLOADING MODELS WITH IDM (REQUIRED)")
        print("=" * 80)

        if not self.idm_puller:
            print("❌ IDM not available - downloads aborted")
            print("   Internet Download Manager is required for all downloads")
            return self._fallback_download(model_list)

        if not self.idm_puller.idm or not self.idm_puller.idm.is_available():
            print("❌ IDM not available - downloads aborted")
            print("   Please ensure Internet Download Manager is installed and running")
            return self._fallback_download(model_list)

        results = {}
        for model_name in model_list:
            print(f"\n📥 Downloading {model_name}...")
            result = self.idm_puller.pull_model_with_idm(
                model_name,
                endpoint="http://localhost:11434",
                destination=self.m_drive_path
            )
            results[model_name] = result

            if result.get("success"):
                print(f"   ✅ {model_name}: {result.get('action', 'downloaded')}")
            else:
                print(f"   ❌ {model_name}: {result.get('error', 'failed')}")

        return results

    def _fallback_download(self, model_list: List[str]) -> Dict[str, Any]:
        """IDM is required - no fallback available"""
        print("\n❌ IDM is required for all downloads - no Ollama fallback")
        print("   Please ensure Internet Download Manager is installed and running")
        results = {}
        for model_name in model_list:
            results[model_name] = {
                "success": False,
                "error": "IDM required - no Ollama fallback available"
            }
        return results

    def run_complete_setup(self, download_models: bool = False, model_list: Optional[List[str]] = None):
        try:
            """Run complete M drive setup"""
            print("=" * 80)
            print("🚀 COMPLETE M DRIVE SETUP WITH IDM INTEGRATION")
            print("=" * 80)
            print(f"Timestamp: {datetime.now().isoformat()}")

            results = {
                "timestamp": datetime.now().isoformat(),
                "m_drive_mapped": False,
                "models_found": {},
                "models_moved": False,
                "ollama_configured": False,
                "downloads": {}
            }

            # Step 1: Map M drive
            results["m_drive_mapped"] = self.map_m_drive()

            if not results["m_drive_mapped"]:
                print("\n❌ M drive mapping failed. Cannot continue.")
                return results

            # Step 2: Find all models
            model_locations = self.find_all_ai_models()
            results["models_found"] = {
                k: [str(p) for p in v] for k, v in model_locations.items()
            }

            # Step 3: Move models to M drive
            results["models_moved"] = self.move_models_to_m_drive(model_locations)

            # Step 4: Configure Ollama
            self.configure_ollama_for_m_drive()
            results["ollama_configured"] = True

            # Step 5: Download models if requested
            if download_models and model_list:
                results["downloads"] = self.download_models_with_idm(model_list)

            # Save results
            results_file = self.project_root / "M_DRIVE_SETUP_RESULTS.json"
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)

            print("\n" + "=" * 80)
            print("✅ SETUP COMPLETE")
            print("=" * 80)
            print(f"\n📄 Results saved to: {results_file}")
            print(f"\n💡 Next steps:")
            print("   1. Restart Ollama service")
            print("   2. Verify models: ollama list")
            print("   3. Test model: ollama run qwen2.5:32b")

            return results


        except Exception as e:
            self.logger.error(f"Error in run_complete_setup: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Complete M Drive Setup with IDM Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Complete setup (map drive, move models, configure)
  python setup_m_drive_models_with_idm.py --setup

  # Setup and download peak models with IDM
  python setup_m_drive_models_with_idm.py --setup --download qwen2.5:72b qwen2.5:32b

  # Just map M drive
  python setup_m_drive_models_with_idm.py --map-only
        """
    )
    parser.add_argument("--setup", action="store_true", help="Run complete setup")
    parser.add_argument("--map-only", action="store_true", help="Only map M drive")
    parser.add_argument("--download", nargs="+", help="Download specific models with IDM")
    parser.add_argument("--move-only", action="store_true", help="Only move existing models")

    args = parser.parse_args()

    manager = MDriveModelManager(project_root)

    if args.map_only:
        manager.map_m_drive()
    elif args.move_only:
        model_locations = manager.find_all_ai_models()
        manager.move_models_to_m_drive(model_locations)
    elif args.setup:
        manager.run_complete_setup(
            download_models=bool(args.download),
            model_list=args.download
        )
    else:
        parser.print_help()


if __name__ == "__main__":

    main()