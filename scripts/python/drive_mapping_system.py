#!/usr/bin/env python3
"""
Drive Mapping System

Maps and manages network drives for organized storage:
- M: Models
- P: Pictures
- U: Public/Shared
- V: Video/Media (NAS)
- D: Downloads
- Avoids confusion with backups

Tags: #DRIVE_MAPPING #NAS #STORAGE #ORGANIZATION @JARVIS @LUMINA
"""

import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

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

logger = get_logger("DriveMapping")


@dataclass
class DriveMapping:
    """Drive mapping configuration"""
    drive_letter: str
    network_path: str
    local_path: Optional[str] = None
    purpose: str = ""
    description: str = ""
    enabled: bool = True
    mapped: bool = False
    last_mapped: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class DriveMappingSystem:
    """
    Drive Mapping System

    Manages network drive mappings for organized storage:
    - M: Models
    - P: Pictures
    - U: Public/Shared
    - V: Video/Media (NAS)
    - D: Downloads
    """

    def __init__(self):
        """Initialize drive mapping system"""
        self.drive_mappings: Dict[str, DriveMapping] = {}
        self.config_file = project_root / "config" / "drive_mappings.json"
        self.config_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize default mappings
        self._initialize_default_mappings()

        # Load saved mappings
        self._load_mappings()

        logger.info("=" * 80)
        logger.info("💾 DRIVE MAPPING SYSTEM")
        logger.info("=" * 80)

    def _initialize_default_mappings(self):
        """Initialize default drive mappings"""
        default_mappings = [
            DriveMapping(
                drive_letter="M",
                network_path="\\\\NAS\\models",
                purpose="models",
                description="AI Models and Model Storage"
            ),
            DriveMapping(
                drive_letter="P",
                network_path="\\\\NAS\\pictures",
                purpose="pictures",
                description="Pictures and Images"
            ),
            DriveMapping(
                drive_letter="U",
                network_path="\\\\NAS\\public",
                purpose="public",
                description="Public/Shared Drive"
            ),
            DriveMapping(
                drive_letter="V",
                network_path="\\\\NAS\\video",
                purpose="video",
                description="Video/Media Storage (NAS)"
            ),
            DriveMapping(
                drive_letter="D",
                network_path="\\\\NAS\\downloads",
                purpose="downloads",
                description="Downloads Directory"
            ),
        ]

        for mapping in default_mappings:
            self.drive_mappings[mapping.drive_letter] = mapping

    def _load_mappings(self):
        """Load drive mappings from config file"""
        if not self.config_file.exists():
            return

        try:
            with open(self.config_file, encoding='utf-8') as f:
                data = json.load(f)

            for drive_letter, mapping_data in data.get("mappings", {}).items():
                if drive_letter in self.drive_mappings:
                    # Update existing mapping
                    for key, value in mapping_data.items():
                        if hasattr(self.drive_mappings[drive_letter], key):
                            setattr(self.drive_mappings[drive_letter], key, value)
                else:
                    # Create new mapping
                    self.drive_mappings[drive_letter] = DriveMapping(**mapping_data)

            logger.info(f"📂 Loaded drive mappings from {self.config_file}")
        except Exception as e:
            logger.warning(f"Error loading drive mappings: {e}")

    def _save_mappings(self):
        try:
            """Save drive mappings to config file"""
            data = {
                "mappings": {
                    letter: mapping.to_dict()
                    for letter, mapping in self.drive_mappings.items()
                },
                "last_updated": datetime.now().isoformat()
            }

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

            logger.info(f"💾 Saved drive mappings to {self.config_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_mappings: {e}", exc_info=True)
            raise
    def add_mapping(self, drive_letter: str, network_path: str,
                   purpose: str = "", description: str = "") -> DriveMapping:
        """Add or update drive mapping"""
        mapping = DriveMapping(
            drive_letter=drive_letter.upper(),
            network_path=network_path,
            purpose=purpose,
            description=description
        )

        self.drive_mappings[drive_letter.upper()] = mapping
        self._save_mappings()

        logger.info(f"📌 Added drive mapping: {drive_letter}: -> {network_path}")
        return mapping

    def map_drive(self, drive_letter: str, persistent: bool = True) -> bool:
        """Map network drive using Windows net use command"""
        if drive_letter.upper() not in self.drive_mappings:
            logger.warning(f"Drive mapping {drive_letter} not found")
            return False

        mapping = self.drive_mappings[drive_letter.upper()]

        if not mapping.enabled:
            logger.info(f"Drive {drive_letter} is disabled")
            return False

        # Check if already mapped
        drive_path = Path(f"{drive_letter}:\\")
        if drive_path.exists():
            try:
                # Test if it's accessible
                list(drive_path.iterdir())
                logger.info(f"Drive {drive_letter}: already mapped")
                mapping.mapped = True
                return True
            except Exception:
                # Drive letter exists but not accessible, try to disconnect first
                self.unmap_drive(drive_letter)

        # Map the drive
        try:
            # Use net use command for Windows
            persistent_flag = "/PERSISTENT:YES" if persistent else "/PERSISTENT:NO"
            cmd = [
                "net", "use",
                f"{drive_letter}:",
                mapping.network_path,
                persistent_flag
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                mapping.mapped = True
                mapping.last_mapped = datetime.now().isoformat()
                self._save_mappings()
                logger.info(f"✅ Mapped {drive_letter}: -> {mapping.network_path}")
                return True
            else:
                logger.warning(f"Failed to map {drive_letter}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error mapping drive {drive_letter}: {e}")
            return False

    def unmap_drive(self, drive_letter: str) -> bool:
        """Unmap network drive"""
        try:
            cmd = ["net", "use", f"{drive_letter}:", "/DELETE", "/Y"]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                if drive_letter.upper() in self.drive_mappings:
                    self.drive_mappings[drive_letter.upper()].mapped = False
                    self._save_mappings()
                logger.info(f"✅ Unmapped drive {drive_letter}:")
                return True
            else:
                logger.warning(f"Failed to unmap {drive_letter}: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"Error unmapping drive {drive_letter}: {e}")
            return False

    def map_all_drives(self, persistent: bool = True) -> Dict[str, bool]:
        """Map all enabled drives"""
        results = {}

        for drive_letter, mapping in self.drive_mappings.items():
            if mapping.enabled:
                results[drive_letter] = self.map_drive(drive_letter, persistent)

        return results

    def get_drive_status(self) -> Dict[str, Any]:
        """Get status of all drive mappings"""
        status = {
            "mappings": {},
            "mapped_count": 0,
            "total_count": len(self.drive_mappings)
        }

        for drive_letter, mapping in self.drive_mappings.items():
            # Check if actually mapped
            drive_path = Path(f"{drive_letter}:\\")
            is_mapped = drive_path.exists()

            if is_mapped:
                try:
                    list(drive_path.iterdir())
                    mapping.mapped = True
                    status["mapped_count"] += 1
                except Exception:
                    mapping.mapped = False

            status["mappings"][drive_letter] = {
                "mapped": mapping.mapped,
                "network_path": mapping.network_path,
                "purpose": mapping.purpose,
                "description": mapping.description,
                "enabled": mapping.enabled
            }

        return status

    def get_video_storage_path(self) -> Path:
        """Get path for video storage (V: drive / NAS)"""
        # Check if V: drive is mapped
        v_drive = Path("V:\\")
        if v_drive.exists():
            try:
                list(v_drive.iterdir())
                return v_drive / "video" / "va_recordings"
            except Exception:
                pass

        # Fallback to network path
        if "V" in self.drive_mappings:
            mapping = self.drive_mappings["V"]
            # Try to map it
            if self.map_drive("V"):
                return Path("V:\\video\\va_recordings")
            else:
                # Use network path directly
                return Path(mapping.network_path) / "va_recordings"

        # Final fallback - MUST use NAS, no local storage
        # Try network path directly
        nas_path = Path("\\\\NAS\\video\\va_recordings")
        try:
            nas_path.mkdir(parents=True, exist_ok=True)
            return nas_path
        except Exception:
            # If NAS is not accessible, raise error - cannot use local storage
            raise RuntimeError("CRITICAL: NAS storage (\\\\NAS\\video) is not accessible. Local storage is at CRITICAL utilization - NAS access required!")

    def get_picture_storage_path(self) -> Path:
        """Get path for picture/screenshot storage (P: drive / NAS)"""
        # Check if P: drive is mapped
        p_drive = Path("P:\\")
        if p_drive.exists():
            try:
                list(p_drive.iterdir())
                return p_drive / "screenshots" / "manus_rdp_captures"
            except Exception:
                pass

        # Fallback to network path
        if "P" in self.drive_mappings:
            mapping = self.drive_mappings["P"]
            # Try to map it
            if self.map_drive("P"):
                return Path("P:\\screenshots\\manus_rdp_captures")
            else:
                # Use network path directly
                return Path(mapping.network_path) / "screenshots" / "manus_rdp_captures"

        # Final fallback - MUST use NAS, no local storage
        # Try network path directly
        nas_path = Path("\\\\NAS\\pictures\\screenshots\\manus_rdp_captures")
        try:
            nas_path.mkdir(parents=True, exist_ok=True)
            return nas_path
        except Exception:
            # If NAS is not accessible, raise error - cannot use local storage
            raise RuntimeError("CRITICAL: NAS storage (\\\\NAS\\pictures) is not accessible. Local storage is at CRITICAL utilization - NAS access required!")


def main():
    """Main function"""
    print("=" * 80)
    print("💾 DRIVE MAPPING SYSTEM")
    print("=" * 80)
    print()

    system = DriveMappingSystem()

    # Show current mappings
    print("Drive Mappings:")
    for letter, mapping in system.drive_mappings.items():
        status = "✅ MAPPED" if mapping.mapped else "❌ NOT MAPPED"
        print(f"  {letter}: {mapping.network_path}")
        print(f"    Purpose: {mapping.purpose}")
        print(f"    Description: {mapping.description}")
        print(f"    Status: {status}")
        print()

    # Get status
    status = system.get_drive_status()
    print(f"Mapped: {status['mapped_count']}/{status['total_count']}")
    print()

    # Video storage path
    video_path = system.get_video_storage_path()
    print(f"Video Storage Path: {video_path}")
    print()

    print("=" * 80)
    print("✅ DRIVE MAPPING SYSTEM READY")
    print("=" * 80)

    return 0


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()