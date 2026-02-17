#!/usr/bin/env python3
"""
JARVIS Complete Launcher
Unified entry point to start all JARVIS components

Starts:
- AutoHotkey scripts (RAlt, F23 hotkeys)
- ElevenLabs TTS system
- Voice listening system
- Health monitoring
- All background services

Tags: #JARVIS #LAUNCHER #STARTUP #DOIT @JARVIS @LUMINA
"""

import sys
import os
import time
import subprocess
import signal
from pathlib import Path
from typing import Dict, List, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLauncher")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class JARVISLauncher:
    """Complete JARVIS launcher"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize launcher"""
        if project_root is None:
            project_root = PROJECT_ROOT

        self.project_root = Path(project_root)
        self.processes: List[subprocess.Popen] = []
        self.running = True

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("=" * 80)
        logger.info("🤖 JARVIS COMPLETE LAUNCHER")
        logger.info("=" * 80)
        logger.info("")

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info("")
        logger.info("🛑 Shutdown signal received...")
        self.shutdown()
        sys.exit(0)

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        logger.info("🔍 Checking prerequisites...")
        logger.info("")

        checks = {
            "AutoHotkey": self._check_autohotkey(),
            "Python Modules": self._check_python_modules(),
            "ElevenLabs Config": self._check_elevenlabs_config(),
            "Data Directories": self._check_data_directories(),
        }

        all_passed = all(checks.values())

        logger.info("")
        if all_passed:
            logger.info("✅ All prerequisites met!")
        else:
            logger.warning("⚠️  Some prerequisites missing:")
            for check, passed in checks.items():
                status = "✅" if passed else "❌"
                logger.info(f"   {status} {check}")

        return all_passed

    def _check_autohotkey(self) -> bool:
        """Check if AutoHotkey is installed"""
        try:
            result = subprocess.run(
                ["autohotkey.exe", "/ErrorStdOut"],
                capture_output=True,
                timeout=2
            )
            logger.info("   ✅ AutoHotkey found")
            return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            # Try common installation paths
            common_paths = [
                "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
                "C:\\Program Files (x86)\\AutoHotkey\\AutoHotkey.exe",
            ]
            for path in common_paths:
                if Path(path).exists():
                    logger.info("   ✅ AutoHotkey found (common path)")
                    return True

            logger.warning("   ❌ AutoHotkey not found")
            logger.warning("      Install from: https://www.autohotkey.com/")
            return False

    def _check_python_modules(self) -> bool:
        """Check if required Python modules are available"""
        required_modules = [
            "elevenlabs",
            "azure.keyvault.secrets",
        ]

        missing = []
        for module in required_modules:
            try:
                __import__(module.replace(".", "_"))
            except ImportError:
                missing.append(module)

        if not missing:
            logger.info("   ✅ Python modules available")
            return True
        else:
            logger.warning(f"   ⚠️  Missing modules: {', '.join(missing)}")
            return len(missing) == 0

    def _check_elevenlabs_config(self) -> bool:
        try:
            """Check if ElevenLabs config exists"""
            config_path = self.project_root / "config" / "elevenlabs_config.json"
            if config_path.exists():
                logger.info("   ✅ ElevenLabs config found")
                return True
            else:
                logger.warning("   ⚠️  ElevenLabs config missing (will use defaults)")
                return True  # Not critical

        except Exception as e:
            self.logger.error(f"Error in _check_elevenlabs_config: {e}", exc_info=True)
            raise
    def _check_data_directories(self) -> bool:
        try:
            """Check if data directories exist"""
            data_dir = self.project_root / "data" / "elevenlabs" / "audio"
            if data_dir.exists():
                logger.info("   ✅ Data directories exist")
                return True
            else:
                logger.warning("   ⚠️  Data directories missing (will be created)")
                data_dir.mkdir(parents=True, exist_ok=True)
                return True

        except Exception as e:
            self.logger.error(f"Error in _check_data_directories: {e}", exc_info=True)
            raise
    def start_autohotkey_scripts(self) -> bool:
        """Start AutoHotkey scripts"""
        logger.info("")
        logger.info("⌨️  Starting AutoHotkey scripts...")

        ahk_scripts = [
            "left_alt_doit_TEST.ahk",  # RAlt hotkey
            # Add F23 script when ready
        ]

        ahk_dir = self.project_root / "scripts" / "autohotkey"
        started = []

        for script in ahk_scripts:
            script_path = ahk_dir / script
            if not script_path.exists():
                logger.warning(f"   ⚠️  Script not found: {script}")
                continue

            try:
                # Find autohotkey.exe
                ahk_exe = self._find_autohotkey_exe()
                if not ahk_exe:
                    logger.error("   ❌ AutoHotkey.exe not found")
                    return False

                # Start script
                process = subprocess.Popen(
                    [ahk_exe, str(script_path)],
                    cwd=str(ahk_dir),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )

                self.processes.append(process)
                started.append(script)
                logger.info(f"   ✅ Started: {script}")

            except Exception as e:
                logger.error(f"   ❌ Failed to start {script}: {e}")
                return False

        if started:
            logger.info(f"   ✅ Started {len(started)} AutoHotkey script(s)")
            return True
        else:
            logger.warning("   ⚠️  No AutoHotkey scripts started")
            return True  # Not critical if scripts don't exist

    def _find_autohotkey_exe(self) -> Optional[str]:
        """Find AutoHotkey executable"""
        # Try PATH first
        try:
            subprocess.run(["autohotkey.exe", "/ErrorStdOut"],
                         capture_output=True, timeout=1)
            return "autohotkey.exe"
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        # Try common paths
        common_paths = [
            "C:\\Program Files\\AutoHotkey\\AutoHotkey.exe",
            "C:\\Program Files (x86)\\AutoHotkey\\AutoHotkey.exe",
        ]

        for path in common_paths:
            if Path(path).exists():
                return path

        return None

    def start_tts_system(self) -> bool:
        """Initialize TTS system"""
        logger.info("")
        logger.info("🎤 Initializing TTS system...")

        try:
            from jarvis_elevenlabs_integration import JARVISElevenLabsTTS

            tts = JARVISElevenLabsTTS(project_root=self.project_root)

            if tts.api_key and tts.client:
                logger.info("   ✅ ElevenLabs TTS initialized")
                logger.info(f"   Voice: {tts.current_voice_id}")
                return True
            else:
                logger.warning("   ⚠️  TTS initialized but API key not configured")
                return True  # Not critical - can work without TTS

        except Exception as e:
            logger.warning(f"   ⚠️  TTS initialization failed: {e}")
            return True  # Not critical - can work without TTS

    def start_voice_listening(self) -> bool:
        """Start voice listening system"""
        logger.info("")
        logger.info("🎙️  Starting voice listening...")

        try:
            # Check if voice listening script exists
            voice_script = self.project_root / "scripts" / "python" / "jarvis_voice_trigger.py"
            if not voice_script.exists():
                logger.warning("   ⚠️  Voice listening script not found")
                return True  # Not critical

            # Start voice listening in background
            process = subprocess.Popen(
                [sys.executable, str(voice_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.processes.append(process)
            logger.info("   ✅ Voice listening started")
            return True

        except Exception as e:
            logger.warning(f"   ⚠️  Voice listening failed: {e}")
            return True  # Not critical

    def start_all(self) -> bool:
        """Start all JARVIS components"""
        logger.info("")
        logger.info("🚀 Starting JARVIS...")
        logger.info("")

        # Check prerequisites
        if not self.check_prerequisites():
            logger.warning("⚠️  Some prerequisites missing, continuing anyway...")
            logger.info("")

        # Start components
        results = {
            "AutoHotkey": self.start_autohotkey_scripts(),
            "TTS": self.start_tts_system(),
            "Voice": self.start_voice_listening(),
        }

        # Summary
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 STARTUP SUMMARY")
        logger.info("=" * 80)
        logger.info("")

        for component, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"   {status} {component}")

        all_started = all(results.values())

        if all_started:
            logger.info("")
            logger.info("🎉 JARVIS is ready!")
            logger.info("")
            logger.info("Available commands:")
            logger.info("   • RAlt (short) → @doit + Enter")
            logger.info("   • RAlt (long) → Keep All")
            logger.info("   • F23 (short) → Voice Input")
            logger.info("   • Say 'Hey Jarvis' → Voice activation")
            logger.info("")
            logger.info("Press Ctrl+C to shutdown")
            logger.info("")
        else:
            logger.warning("")
            logger.warning("⚠️  Some components failed to start")
            logger.warning("")

        return all_started

    def shutdown(self):
        """Shutdown all components"""
        logger.info("")
        logger.info("🛑 Shutting down JARVIS...")

        # Stop all processes
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.warning(f"   ⚠️  Error stopping process: {e}")

        logger.info("   ✅ All components stopped")
        logger.info("")
        logger.info("👋 JARVIS shutdown complete")

    def run(self):
        """Main run loop"""
        if not self.start_all():
            logger.error("❌ Failed to start JARVIS")
            return False

        # Keep running until shutdown
        try:
            while self.running:
                time.sleep(1)

                # Check if processes are still running
                for i, process in enumerate(self.processes):
                    if process.poll() is not None:
                        logger.warning(f"   ⚠️  Process {i} exited unexpectedly")
                        # Could restart here if needed

        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Keyboard interrupt received...")
        finally:
            self.shutdown()

        return True


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Complete Launcher")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--check-only', action='store_true', help='Only check prerequisites')

    args = parser.parse_args()

    launcher = JARVISLauncher(project_root=args.project_root)

    if args.check_only:
        launcher.check_prerequisites()
        return 0

    success = launcher.run()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())