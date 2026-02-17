#!/usr/bin/env python3
"""
System Health Check - Post-Restart Validation

Checks all systems to ensure everything is working after restart.

Tags: #HEALTH_CHECK #VALIDATION #POST_RESTART @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any

from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
project_root = script_dir.parent.parent
from lumina_core.paths import setup_paths
setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from screen_capture_system import ScreenCaptureSystem, SCREEN_CAPTURE_AVAILABLE
    from visual_monitoring_system import VisualMonitoringSystem
    from drive_mapping_system import DriveMappingSystem
    from vlm_integration import VLMIntegration
    from lumina_core.logging import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("SystemHealthCheck")


class SystemHealthChecker:
    """Comprehensive system health checker"""

    def __init__(self):
        """Initialize health checker"""
        self.results: Dict[str, Any] = {}
        logger.info("=" * 80)
        logger.info("🏥 SYSTEM HEALTH CHECK")
        logger.info("=" * 80)

    def check_dependencies(self) -> bool:
        """Check if all dependencies are installed"""
        print("=" * 80)
        print("CHECK 1: Dependencies")
        print("=" * 80)
        print()

        dependencies = {
            "mss": False,
            "opencv-python": False,
            "transformers": False,
            "torch": False,
            "pillow": False,
            "pytesseract": False,
        }

        try:
            import mss
            dependencies["mss"] = True
            print("✅ mss - Installed")
        except ImportError:
            print("❌ mss - Not installed")

        try:
            import cv2
            dependencies["opencv-python"] = True
            print("✅ opencv-python - Installed")
        except ImportError:
            print("❌ opencv-python - Not installed")

        try:
            import transformers
            dependencies["transformers"] = True
            print(f"✅ transformers - Installed ({transformers.__version__})")
        except ImportError:
            print("❌ transformers - Not installed")

        try:
            import torch
            dependencies["torch"] = True
            cuda_available = torch.cuda.is_available()
            print(f"✅ torch - Installed ({torch.__version__})")
            print(f"   CUDA available: {cuda_available}")
        except ImportError:
            print("❌ torch - Not installed")

        try:
            from PIL import Image
            dependencies["pillow"] = True
            print("✅ pillow - Installed")
        except ImportError:
            print("❌ pillow - Not installed")

        try:
            import pytesseract
            dependencies["pytesseract"] = True
            print("✅ pytesseract - Installed")
        except ImportError:
            print("❌ pytesseract - Not installed")

        print()
        all_installed = all(dependencies.values())
        self.results["dependencies"] = {
            "status": "✅ PASS" if all_installed else "⚠️  PARTIAL",
            "details": dependencies
        }

        return all_installed

    def check_screen_capture(self) -> bool:
        """Check screen capture system"""
        print("=" * 80)
        print("CHECK 2: Screen Capture System")
        print("=" * 80)
        print()

        try:
            capture = ScreenCaptureSystem()
            print(f"✅ Screen capture system initialized")
            print(f"   Available: {SCREEN_CAPTURE_AVAILABLE}")
            print(f"   Storage: {capture.video_storage_path}")

            # Test screenshot
            screenshot_path = capture.capture_screenshot("health_check_test.png")
            if screenshot_path.exists():
                file_size = screenshot_path.stat().st_size
                print(f"✅ Screenshot test passed ({file_size} bytes)")
                self.results["screen_capture"] = {
                    "status": "✅ PASS",
                    "screenshot_size": file_size,
                    "storage_path": str(capture.video_storage_path)
                }
                return True
            else:
                print("❌ Screenshot test failed")
                self.results["screen_capture"] = {"status": "❌ FAIL"}
                return False
        except Exception as e:
            print(f"❌ Screen capture check failed: {e}")
            self.results["screen_capture"] = {"status": "❌ FAIL", "error": str(e)}
            return False

    def check_visual_monitoring(self) -> bool:
        """Check visual monitoring system"""
        print("=" * 80)
        print("CHECK 3: Visual Monitoring System")
        print("=" * 80)
        print()

        try:
            monitoring = VisualMonitoringSystem()
            print(f"✅ Visual monitoring initialized")
            print(f"   VLM enabled: {monitoring.use_vlm}")
            print(f"   OCR available: {hasattr(monitoring, 'extract_text_from_screen')}")
            print(f"   CV available: {hasattr(monitoring, 'analyze_screen_with_cv')}")

            status = monitoring.get_monitoring_status()
            print(f"   Monitoring: {status['monitoring']}")
            print(f"   Recording: {status['recording']}")

            self.results["visual_monitoring"] = {
                "status": "✅ PASS",
                "vlm_enabled": monitoring.use_vlm,
                "ocr_available": hasattr(monitoring, 'extract_text_from_screen'),
                "cv_available": hasattr(monitoring, 'analyze_screen_with_cv')
            }
            return True
        except Exception as e:
            print(f"❌ Visual monitoring check failed: {e}")
            self.results["visual_monitoring"] = {"status": "❌ FAIL", "error": str(e)}
            return False

    def check_local_vlm(self) -> bool:
        """Check local VLM"""
        print("=" * 80)
        print("CHECK 4: Local VLM")
        print("=" * 80)
        print()

        try:
            vlm = VLMIntegration(provider="local")
            print(f"✅ VLM integration initialized")
            print(f"   Provider: {vlm.provider}")
            print(f"   Device: {vlm.device}")
            print(f"   Transformers available: {vlm.transformers_available}")

            if vlm.local_model:
                print(f"   Model loaded: {vlm.model}")
                self.results["local_vlm"] = {
                    "status": "✅ PASS",
                    "model": vlm.model,
                    "device": vlm.device
                }
                return True
            else:
                print("⚠️  Model not loaded (will load on first use)")
                self.results["local_vlm"] = {
                    "status": "⚠️  READY",
                    "note": "Model will load on first use"
                }
                return True  # Still counts as ready
        except Exception as e:
            print(f"❌ Local VLM check failed: {e}")
            self.results["local_vlm"] = {"status": "❌ FAIL", "error": str(e)}
            return False

    def check_drive_mappings(self) -> bool:
        """Check drive mappings"""
        print("=" * 80)
        print("CHECK 5: Drive Mappings")
        print("=" * 80)
        print()

        try:
            drive_system = DriveMappingSystem()
            status = drive_system.get_drive_status()

            print(f"Total drives configured: {status['total_count']}")
            print(f"Drives mapped: {status['mapped_count']}")
            print()

            for letter, info in status["mappings"].items():
                status_icon = "✅" if info["mapped"] else "❌"
                print(f"{status_icon} {letter}: {info['network_path']} - {info['purpose']}")

            print()
            video_path = drive_system.get_video_storage_path()
            print(f"Video storage: {video_path}")

            self.results["drive_mappings"] = {
                "status": "✅ PASS" if status['mapped_count'] > 0 else "⚠️  PARTIAL",
                "mapped": status['mapped_count'],
                "total": status['total_count'],
                "video_storage": str(video_path)
            }
            return True
        except Exception as e:
            print(f"❌ Drive mapping check failed: {e}")
            self.results["drive_mappings"] = {"status": "❌ FAIL", "error": str(e)}
            return False

    def check_cursor_settings(self) -> bool:
        """Check Cursor IDE settings"""
        print("=" * 80)
        print("CHECK 6: Cursor IDE Settings")
        print("=" * 80)
        print()

        settings_file = project_root / ".vscode" / "settings.json"

        if settings_file.exists():
            try:
                import json
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                setting_count = len(settings)
                print(f"✅ Settings file exists")
                print(f"   Settings configured: {setting_count}")
                print(f"   Location: {settings_file}")

                # Check key settings
                key_settings = [
                    "editor.fontSize",
                    "cursor.ai.enabled",
                    "git.enabled",
                    "python.defaultInterpreterPath"
                ]

                found = []
                for key in key_settings:
                    if key in settings:
                        found.append(key)
                        print(f"   ✅ {key}: {settings[key]}")

                self.results["cursor_settings"] = {
                    "status": "✅ PASS",
                    "settings_count": setting_count,
                    "key_settings_found": len(found)
                }
                return True
            except Exception as e:
                print(f"❌ Error reading settings: {e}")
                self.results["cursor_settings"] = {"status": "❌ FAIL", "error": str(e)}
                return False
        else:
            print("⚠️  Settings file not found")
            self.results["cursor_settings"] = {"status": "⚠️  NOT FOUND"}
            return False

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        print("=" * 80)
        print("🏥 COMPREHENSIVE SYSTEM HEALTH CHECK")
        print("=" * 80)
        print()
        print("Checking all systems after restart...")
        print()

        checks = [
            ("Dependencies", self.check_dependencies),
            ("Screen Capture", self.check_screen_capture),
            ("Visual Monitoring", self.check_visual_monitoring),
            ("Local VLM", self.check_local_vlm),
            ("Drive Mappings", self.check_drive_mappings),
            ("Cursor Settings", self.check_cursor_settings),
        ]

        results_summary = []
        for name, check_func in checks:
            try:
                result = check_func()
                results_summary.append((name, result))
                print()
            except Exception as e:
                print(f"❌ {name} check crashed: {e}")
                results_summary.append((name, False))
                print()

        # Summary
        print("=" * 80)
        print("📊 HEALTH CHECK SUMMARY")
        print("=" * 80)
        print()

        passed = 0
        total = len(results_summary)

        for name, result in results_summary:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{status} - {name}")
            if result:
                passed += 1

        print()
        print(f"Results: {passed}/{total} checks passed")
        print()

        if passed == total:
            print("✅ ALL SYSTEMS OPERATIONAL")
        elif passed >= total * 0.8:
            print("⚠️  MOST SYSTEMS OPERATIONAL (some issues)")
        else:
            print("❌ MULTIPLE SYSTEMS HAVE ISSUES")

        print()

        self.results["summary"] = {
            "passed": passed,
            "total": total,
            "percentage": (passed / total * 100) if total > 0 else 0
        }

        return self.results


def main():
    """Main function"""
    checker = SystemHealthChecker()
    results = checker.run_all_checks()

    return 0 if results["summary"]["passed"] == results["summary"]["total"] else 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()