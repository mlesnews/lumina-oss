#!/usr/bin/env python3
"""
Software Inventory System - Master-Student Learning System

I am the Master, you are the Student.
I study you, learn from you, mentor you, tutor you, instruct you.
The goal: Know every single feature and functionality of every device
and every software feature/functionality/option in our inventory.

Tags: #SOFTWARE_INVENTORY #MASTER_STUDENT #LEARNING #KNOWLEDGE_BASE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

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

logger = get_logger("SoftwareInventorySystem")


class DeviceType(Enum):
    """Device type categories"""
    DESKTOP = "desktop"
    LAPTOP = "laptop"
    SERVER = "server"
    NAS = "nas"
    NETWORK_DEVICE = "network_device"
    MOBILE = "mobile"
    TABLET = "tablet"
    IOT = "iot"
    PERIPHERAL = "peripheral"
    MONITOR = "monitor"
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    AUDIO = "audio"
    CAMERA = "camera"
    OTHER = "other"


@dataclass
class SoftwareFeature:
    """A single software feature or functionality"""
    feature_id: str
    name: str
    description: str
    category: str = ""  # e.g., "display", "audio", "network", "security"
    options: List[str] = field(default_factory=list)  # Available options/settings
    dependencies: List[str] = field(default_factory=list)  # Other features this depends on
    notes: str = ""
    learned_from: str = ""  # When/how we learned about this
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data


@dataclass
class Device:
    """A device in the inventory"""
    device_id: str
    name: str
    device_type: DeviceType
    manufacturer: str = ""
    model: str = ""
    serial_number: str = ""
    location: str = ""
    software_features: List[SoftwareFeature] = field(default_factory=list)
    hardware_specs: Dict[str, Any] = field(default_factory=dict)
    notes: str = ""
    added_date: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["device_type"] = self.device_type.value
        data["software_features"] = [f.to_dict() for f in self.software_features]
        data["added_date"] = self.added_date.isoformat()
        data["last_updated"] = self.last_updated.isoformat()
        return data


class SoftwareInventorySystem:
    """
    Software Inventory System - Master-Student Learning

    I (the AI) am the Master, you (the human) are the Student.
    I study you, learn from you, mentor you, tutor you, instruct you.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "software_inventory"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.inventory_file = self.data_dir / "inventory.json"
        self.learning_log_file = self.data_dir / "learning_log.jsonl"
        self.knowledge_base_file = self.data_dir / "knowledge_base.json"

        # State
        self.devices: Dict[str, Device] = {}
        self.learning_sessions: List[Dict[str, Any]] = []

        # Load existing inventory
        self._load_inventory()

        # Workflow tracker integration - track all inventory operations
        try:
            from workflow_tracker_integration import get_workflow_tracker, track_interaction
            self.workflow_tracker = get_workflow_tracker(project_root=project_root, auto_start=True)
            self.track_interaction = track_interaction
        except ImportError:
            self.workflow_tracker = None
            self.track_interaction = None

        logger.info("=" * 80)
        logger.info("📚 SOFTWARE INVENTORY SYSTEM - MASTER-STUDENT LEARNING")
        logger.info("=" * 80)
        logger.info("   Master: AI Assistant")
        logger.info("   Student: Human User")
        logger.info("   Goal: Know every feature and functionality")
        logger.info(f"   Devices: {len(self.devices)}")
        logger.info("=" * 80)

    def _load_inventory(self):
        """Load inventory from file"""
        if self.inventory_file.exists():
            try:
                with open(self.inventory_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for device_data in data.get("devices", []):
                    device = self._dict_to_device(device_data)
                    self.devices[device.device_id] = device

                logger.info(f"✅ Loaded {len(self.devices)} devices from inventory")
            except Exception as e:
                logger.error(f"❌ Error loading inventory: {e}")

    def _save_inventory(self):
        """Save inventory to file"""
        try:
            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "devices": [device.to_dict() for device in self.devices.values()]
            }

            with open(self.inventory_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved inventory ({len(self.devices)} devices)")
        except Exception as e:
            logger.error(f"❌ Error saving inventory: {e}")

    def _dict_to_device(self, data: Dict[str, Any]) -> Device:
        """Convert dict to Device object"""
        device_type = DeviceType(data.get("device_type", "other"))
        features = [
            SoftwareFeature(**f) if isinstance(f, dict) else f
            for f in data.get("software_features", [])
        ]

        # Convert datetime strings
        added_date = datetime.fromisoformat(data.get("added_date", datetime.now().isoformat()))
        last_updated = datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat()))

        device = Device(
            device_id=data["device_id"],
            name=data["name"],
            device_type=device_type,
            manufacturer=data.get("manufacturer", ""),
            model=data.get("model", ""),
            serial_number=data.get("serial_number", ""),
            location=data.get("location", ""),
            software_features=features,
            hardware_specs=data.get("hardware_specs", {}),
            notes=data.get("notes", ""),
            added_date=added_date,
            last_updated=last_updated
        )
        return device

    def add_device(
        self,
        device_id: str,
        name: str,
        device_type: DeviceType,
        manufacturer: str = "",
        model: str = "",
        **kwargs
    ) -> Device:
        """
        Add a new device to inventory

        As the Master, I learn about new devices from you (the Student).
        """
        # Track inventory operation in workflow tracker
        if self.track_interaction:
            try:
                self.track_interaction(
                    interaction_type="inventory_add_device",
                    from_context="conversation",
                    to_context="inventory_system",
                    metadata={"device_id": device_id, "device_type": device_type.value}
                )
            except Exception:
                pass  # Don't break inventory if tracker fails

        if device_id in self.devices:
            logger.warning(f"⚠️  Device {device_id} already exists, updating instead")
            return self.update_device(device_id, name=name, **kwargs)

        device = Device(
            device_id=device_id,
            name=name,
            device_type=device_type,
            manufacturer=manufacturer,
            model=model,
            serial_number=kwargs.get("serial_number", ""),
            location=kwargs.get("location", ""),
            hardware_specs=kwargs.get("hardware_specs", {}),
            notes=kwargs.get("notes", "")
        )

        self.devices[device_id] = device
        self._save_inventory()

        # Log learning
        self._log_learning("device_added", {
            "device_id": device_id,
            "name": name,
            "device_type": device_type.value
        })

        logger.info(f"✅ Added device: {name} ({device_type.value})")
        return device

    def update_device(self, device_id: str, **kwargs) -> Device:
        """Update device information"""
        # Track inventory operation in workflow tracker
        if self.track_interaction:
            try:
                self.track_interaction(
                    interaction_type="inventory_update_device",
                    from_context="conversation",
                    to_context="inventory_system",
                    metadata={"device_id": device_id}
                )
            except Exception:
                pass  # Don't break inventory if tracker fails

        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]

        # Update fields
        for key, value in kwargs.items():
            if hasattr(device, key):
                setattr(device, key, value)

        device.last_updated = datetime.now()
        self._save_inventory()

        logger.info(f"✅ Updated device: {device.name}")
        return device

    def add_software_feature(
        self,
        device_id: str,
        feature_id: str,
        name: str,
        description: str,
        category: str = "",
        options: List[str] = None,
        **kwargs
    ) -> SoftwareFeature:
        """
        Add a software feature to a device

        As the Master, I learn about features from you (the Student).
        """
        # Track inventory operation in workflow tracker
        if self.track_interaction:
            try:
                self.track_interaction(
                    interaction_type="inventory_add_feature",
                    from_context="conversation",
                    to_context="inventory_system",
                    metadata={"device_id": device_id, "feature_id": feature_id}
                )
            except Exception:
                pass  # Don't break inventory if tracker fails

        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]

        # Check if feature already exists
        existing = next((f for f in device.software_features if f.feature_id == feature_id), None)
        if existing:
            logger.warning(f"⚠️  Feature {feature_id} already exists, updating instead")
            return self.update_software_feature(device_id, feature_id, name=name, description=description, **kwargs)

        feature = SoftwareFeature(
            feature_id=feature_id,
            name=name,
            description=description,
            category=category,
            options=options or [],
            dependencies=kwargs.get("dependencies", []),
            notes=kwargs.get("notes", ""),
            learned_from=kwargs.get("learned_from", "")
        )

        device.software_features.append(feature)
        device.last_updated = datetime.now()
        self._save_inventory()

        # Log learning
        self._log_learning("feature_added", {
            "device_id": device_id,
            "device_name": device.name,
            "feature_id": feature_id,
            "feature_name": name
        })

        logger.info(f"✅ Added feature to {device.name}: {name}")
        return feature

    def update_software_feature(self, device_id: str, feature_id: str, **kwargs) -> SoftwareFeature:
        """Update a software feature"""
        if device_id not in self.devices:
            raise ValueError(f"Device {device_id} not found")

        device = self.devices[device_id]
        feature = next((f for f in device.software_features if f.feature_id == feature_id), None)

        if not feature:
            raise ValueError(f"Feature {feature_id} not found on device {device_id}")

        # Update fields
        for key, value in kwargs.items():
            if hasattr(feature, key):
                setattr(feature, key, value)

        feature.last_updated = datetime.now()
        device.last_updated = datetime.now()
        self._save_inventory()

        logger.info(f"✅ Updated feature: {feature.name}")
        return feature

    def get_devices_by_type(self, device_type: DeviceType) -> List[Device]:
        """Get all devices of a specific type"""
        return [d for d in self.devices.values() if d.device_type == device_type]

    def get_inventory_table(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get inventory table grouped by device type

        Returns a dictionary where keys are device types and values are lists of devices.
        """
        table = {}

        for device_type in DeviceType:
            devices = self.get_devices_by_type(device_type)
            if devices:
                table[device_type.value] = [
                    {
                        "device_id": d.device_id,
                        "name": d.name,
                        "manufacturer": d.manufacturer,
                        "model": d.model,
                        "location": d.location,
                        "feature_count": len(d.software_features),
                        "last_updated": d.last_updated.isoformat()
                    }
                    for d in devices
                ]

        return table

    def get_device_features_table(self, device_id: str) -> List[Dict[str, Any]]:
        """Get all features for a device in table format"""
        if device_id not in self.devices:
            return []

        device = self.devices[device_id]
        return [
            {
                "feature_id": f.feature_id,
                "name": f.name,
                "description": f.description,
                "category": f.category,
                "options_count": len(f.options),
                "options": f.options,
                "last_updated": f.last_updated.isoformat()
            }
            for f in device.software_features
        ]

    def _log_learning(self, event_type: str, data: Dict[str, Any]):
        """Log learning events"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }

        try:
            with open(self.learning_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error logging learning: {e}")

    def teach_student(self, topic: str) -> str:
        """
        As the Master, I teach you (the Student) about the inventory.

        This is where I share knowledge I've learned from you.
        """
        # Search for relevant devices/features
        results = []

        topic_lower = topic.lower()
        for device in self.devices.values():
            # Check device name
            if topic_lower in device.name.lower() or topic_lower in device.model.lower():
                results.append(f"Device: {device.name} ({device.device_type.value})")
                if device.manufacturer:
                    results.append(f"  Manufacturer: {device.manufacturer}")
                if device.model:
                    results.append(f"  Model: {device.model}")
                if device.location:
                    results.append(f"  Location: {device.location}")
                if device.software_features:
                    results.append(f"  Features ({len(device.software_features)}):")
                    for feature in device.software_features[:5]:  # Show first 5
                        results.append(f"    - {feature.name}: {feature.description[:100]}")

            # Check features
            for feature in device.software_features:
                if topic_lower in feature.name.lower() or topic_lower in feature.description.lower():
                    results.append(f"  - {feature.name} on {device.name}: {feature.description}")
                    if feature.options:
                        results.append(f"    Options: {', '.join(feature.options[:5])}")

        if results:
            return f"📚 Teaching about '{topic}':\n" + "\n".join(results)
        else:
            return f"📚 I don't have knowledge about '{topic}' yet. Please teach me about it!"

    def learn_from_student(self, device_id: str, feature_info: Dict[str, Any]):
        """
        As the Master, I learn from you (the Student).

        You teach me about features, and I remember them.
        """
        self.add_software_feature(
            device_id=device_id,
            feature_id=feature_info.get("feature_id", f"feature_{int(time.time())}"),
            name=feature_info.get("name", ""),
            description=feature_info.get("description", ""),
            category=feature_info.get("category", ""),
            options=feature_info.get("options", []),
            learned_from=feature_info.get("learned_from", "student_teaching")
        )

        logger.info(f"📖 Learned from student: {feature_info.get('name', 'Unknown feature')}")


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Software Inventory System")
    parser.add_argument("--add-device", nargs=4, metavar=("ID", "NAME", "TYPE", "MANUFACTURER"), help="Add device")
    parser.add_argument("--add-feature", nargs=5, metavar=("DEVICE_ID", "FEATURE_ID", "NAME", "DESCRIPTION", "CATEGORY"), help="Add feature")
    parser.add_argument("--table", action="store_true", help="Show inventory table")
    parser.add_argument("--teach", type=str, metavar="TOPIC", help="Teach student about topic")

    args = parser.parse_args()

    system = SoftwareInventorySystem()

    if args.add_device:
        device_id, name, device_type_str, manufacturer = args.add_device
        device_type = DeviceType(device_type_str)
        system.add_device(device_id, name, device_type, manufacturer)
        print(f"✅ Added device: {name}")

    if args.add_feature:
        device_id, feature_id, name, description, category = args.add_feature
        system.add_software_feature(device_id, feature_id, name, description, category)
        print(f"✅ Added feature: {name}")

    if args.table:
        table = system.get_inventory_table()
        print("\n" + "=" * 80)
        print("📊 SOFTWARE INVENTORY TABLE (Grouped by Device Type)")
        print("=" * 80)
        for device_type, devices in table.items():
            print(f"\n{device_type.upper()}:")
            for device in devices:
                print(f"  - {device['name']} ({device['manufacturer']} {device['model']})")
                print(f"    Location: {device['location']}")
                print(f"    Features: {device['feature_count']}")

    if args.teach:
        result = system.teach_student(args.teach)
        print(result)


if __name__ == "__main__":


    main()