#!/usr/bin/env python3
"""
Homelab Knowledge Ingestion System

Intelligently ingests device and feature information from:
- Ongoing conversations
- Existing documentation
- Natural language descriptions
- R5 Living Context Matrix

As the Master, I learn continuously from you (the Student) about your homelab.

Tags: #HOMELAB #KNOWLEDGE_INGESTION #MASTER_STUDENT #R5_INTEGRATION @JARVIS @LUMINA
"""

import sys
import json
import re
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field

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

logger = get_logger("HomelabKnowledgeIngestion")

# Import software inventory system
try:
    from software_inventory_system import (
        SoftwareInventorySystem,
        DeviceType,
        Device,
        SoftwareFeature
    )
    INVENTORY_AVAILABLE = True
except ImportError:
    INVENTORY_AVAILABLE = False
    logger.warning("⚠️  Software inventory system not available")

# R5 Integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None


class HomelabKnowledgeIngestion:
    """
    Homelab Knowledge Ingestion System

    Intelligently extracts and learns about devices and features from:
    - Conversations
    - Documentation
    - Natural language
    - R5 context
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "homelab_knowledge"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.ingestion_log = self.data_dir / "ingestion_log.jsonl"
        self.extracted_knowledge = self.data_dir / "extracted_knowledge.json"

        # Initialize inventory system
        if INVENTORY_AVAILABLE:
            self.inventory = SoftwareInventorySystem(project_root=project_root)
        else:
            self.inventory = None
            logger.warning("⚠️  Inventory system not available - knowledge will be logged only")

        # R5 Integration
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root=project_root)
                logger.info("✅ R5 integration available")
            except Exception as e:
                logger.warning(f"⚠️  R5 integration failed: {e}")

        # Device/feature extraction patterns
        self.device_patterns = [
            r"(?:device|equipment|hardware|system|server|nas|router|switch|desktop|laptop)\s+([A-Za-z0-9\s\-_]+)",
            r"([A-Za-z0-9\s\-_]+)\s+(?:device|equipment|hardware|system|server|nas)",
        ]

        self.feature_patterns = [
            r"(?:feature|functionality|option|setting|capability)\s+(?:of|on|in)\s+([A-Za-z0-9\s\-_]+):\s*([A-Za-z0-9\s\-_.,;:!?]+)",
            r"([A-Za-z0-9\s\-_]+)\s+(?:has|supports|can|does)\s+([A-Za-z0-9\s\-_.,;:!?]+",
        ]

        logger.info("=" * 80)
        logger.info("🧠 HOMELAB KNOWLEDGE INGESTION SYSTEM")
        logger.info("=" * 80)
        logger.info("   Master learns from Student continuously")
        logger.info("   Sources: Conversations, Documentation, R5 Context")
        logger.info("=" * 80)

    def ingest_from_conversation(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Ingest knowledge from conversation text

        Extracts devices, features, and functionality mentioned in natural language.
        """
        extracted = {
            "devices": [],
            "features": [],
            "timestamp": datetime.now().isoformat(),
            "source": "conversation",
            "context": context or {}
        }

        # Extract device mentions
        devices = self._extract_devices(text)
        extracted["devices"] = devices

        # Extract feature mentions
        features = self._extract_features(text)
        extracted["features"] = features

        # Process extracted knowledge
        if devices or features:
            self._process_extracted_knowledge(extracted)
            self._log_ingestion(extracted)

        return extracted

    def ingest_from_documentation(self, file_path: Path) -> Dict[str, Any]:
        """
        Ingest knowledge from documentation files

        Parses markdown and text files for device/feature information.
        """
        if not file_path.exists():
            logger.warning(f"⚠️  File not found: {file_path}")
            return {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            extracted = {
                "devices": [],
                "features": [],
                "timestamp": datetime.now().isoformat(),
                "source": "documentation",
                "file": str(file_path)
            }

            # Extract from content
            devices = self._extract_devices(content)
            features = self._extract_features(content)

            extracted["devices"] = devices
            extracted["features"] = features

            if devices or features:
                self._process_extracted_knowledge(extracted)
                self._log_ingestion(extracted)

            logger.info(f"✅ Ingested from {file_path.name}: {len(devices)} devices, {len(features)} features")
            return extracted

        except Exception as e:
            logger.error(f"❌ Error ingesting from {file_path}: {e}")
            return {}

    def ingest_from_r5(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ingest knowledge from R5 Living Context Matrix

        Extracts device/feature mentions from R5 context.
        """
        if not self.r5:
            logger.warning("⚠️  R5 not available")
            return {}

        extracted = {
            "devices": [],
            "features": [],
            "timestamp": datetime.now().isoformat(),
            "source": "r5_context"
        }

        try:
            # Get recent context from R5
            # This would need R5 API to retrieve context
            # For now, log that we would ingest from R5
            logger.info("📚 R5 ingestion would extract from context matrix")

        except Exception as e:
            logger.error(f"❌ Error ingesting from R5: {e}")

        return extracted

    def _extract_devices(self, text: str) -> List[Dict[str, Any]]:
        """Extract device mentions from text"""
        devices = []
        text_lower = text.lower()

        # Common device keywords
        device_keywords = {
            "nas": DeviceType.NAS,
            "server": DeviceType.SERVER,
            "desktop": DeviceType.DESKTOP,
            "laptop": DeviceType.LAPTOP,
            "router": DeviceType.NETWORK_DEVICE,
            "switch": DeviceType.NETWORK_DEVICE,
            "monitor": DeviceType.MONITOR,
            "keyboard": DeviceType.KEYBOARD,
            "mouse": DeviceType.MOUSE,
            "camera": DeviceType.CAMERA,
        }

        # Look for device mentions
        for keyword, device_type in device_keywords.items():
            if keyword in text_lower:
                # Try to extract device name
                pattern = rf"{keyword}\s+([A-Za-z0-9\s\-_]+)"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    device_name = match.group(1).strip()
                    if device_name and len(device_name) > 2:
                        devices.append({
                            "name": device_name,
                            "type": device_type.value,
                            "confidence": 0.7,
                            "extracted_from": match.group(0)
                        })

        # Look for IP addresses (might indicate devices)
        ip_pattern = r"\b(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\b"
        ip_matches = re.finditer(ip_pattern, text)
        for match in ip_matches:
            ip = match.group(1)
            # Check if IP is mentioned with device context
            context = text[max(0, match.start()-50):match.end()+50]
            if any(kw in context.lower() for kw in ["nas", "server", "device", "system"]):
                devices.append({
                    "name": f"Device at {ip}",
                    "ip_address": ip,
                    "type": DeviceType.OTHER.value,
                    "confidence": 0.5,
                    "extracted_from": context.strip()
                })

        return devices

    def _extract_features(self, text: str) -> List[Dict[str, Any]]:
        """Extract feature mentions from text"""
        features = []

        # Look for feature patterns
        feature_keywords = [
            "feature", "functionality", "option", "setting", "capability",
            "can do", "supports", "has", "includes", "provides"
        ]

        # Pattern: "device has feature X"
        pattern = r"([A-Za-z0-9\s\-_]+)\s+(?:has|supports|can|does|includes|provides)\s+([A-Za-z0-9\s\-_.,;:!?]+?)(?:\.|,|$)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            device_ref = match.group(1).strip()
            feature_desc = match.group(2).strip()

            if len(feature_desc) > 5:  # Minimum feature description length
                features.append({
                    "device_reference": device_ref,
                    "name": feature_desc.split('.')[0].split(',')[0].strip(),  # First sentence/clause
                    "description": feature_desc,
                    "confidence": 0.6,
                    "extracted_from": match.group(0)
                })

        # Pattern: "feature X on device Y"
        pattern = r"(?:feature|functionality|option|setting|capability)\s+([A-Za-z0-9\s\-_]+)\s+(?:on|of|in)\s+([A-Za-z0-9\s\-_]+)"
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            feature_name = match.group(1).strip()
            device_ref = match.group(2).strip()

            features.append({
                "device_reference": device_ref,
                "name": feature_name,
                "description": f"Feature {feature_name} on {device_ref}",
                "confidence": 0.7,
                "extracted_from": match.group(0)
            })

        return features

    def _process_extracted_knowledge(self, extracted: Dict[str, Any]):
        """
        Process extracted knowledge and add to inventory

        As the Master, I learn from extracted information.
        """
        if not self.inventory:
            return

        # Process devices
        for device_info in extracted.get("devices", []):
            try:
                device_id = self._generate_device_id(device_info["name"])
                device_type = DeviceType(device_info.get("type", "other"))

                # Check if device exists
                if device_id not in self.inventory.devices:
                    self.inventory.add_device(
                        device_id=device_id,
                        name=device_info["name"],
                        device_type=device_type,
                        notes=f"Auto-extracted: {device_info.get('extracted_from', '')}"
                    )
                    logger.info(f"📚 Learned about device: {device_info['name']}")
                else:
                    # Update existing device
                    device = self.inventory.devices[device_id]
                    if device_info.get("ip_address"):
                        device.hardware_specs["ip_address"] = device_info["ip_address"]
                        device.last_updated = datetime.now()
                        self.inventory._save_inventory()

            except Exception as e:
                logger.warning(f"⚠️  Error processing device {device_info.get('name')}: {e}")

        # Process features
        for feature_info in extracted.get("features", []):
            try:
                device_ref = feature_info.get("device_reference", "")
                if not device_ref:
                    continue

                # Find device by reference
                device = self._find_device_by_reference(device_ref)
                if not device:
                    logger.debug(f"⚠️  Could not find device for feature: {device_ref}")
                    continue

                feature_id = self._generate_feature_id(feature_info["name"])

                # Check if feature exists
                existing = next((f for f in device.software_features if f.feature_id == feature_id), None)
                if not existing:
                    self.inventory.add_software_feature(
                        device_id=device.device_id,
                        feature_id=feature_id,
                        name=feature_info["name"],
                        description=feature_info.get("description", ""),
                        category="",
                        learned_from=f"Auto-extracted: {feature_info.get('extracted_from', '')}"
                    )
                    logger.info(f"📚 Learned about feature: {feature_info['name']} on {device.name}")

            except Exception as e:
                logger.warning(f"⚠️  Error processing feature {feature_info.get('name')}: {e}")

    def _find_device_by_reference(self, reference: str) -> Optional[Device]:
        """Find device by name reference"""
        if not self.inventory:
            return None

        reference_lower = reference.lower()

        # Exact match
        for device in self.inventory.devices.values():
            if reference_lower in device.name.lower():
                return device

        # Partial match
        for device in self.inventory.devices.values():
            if any(word in device.name.lower() for word in reference_lower.split() if len(word) > 3):
                return device

        return None

    def _generate_device_id(self, name: str) -> str:
        """Generate device ID from name"""
        # Clean name and create ID
        clean = re.sub(r'[^a-z0-9]+', '_', name.lower())
        clean = clean.strip('_')
        return f"device_{clean[:30]}"  # Limit length

    def _generate_feature_id(self, name: str) -> str:
        """Generate feature ID from name"""
        clean = re.sub(r'[^a-z0-9]+', '_', name.lower())
        clean = clean.strip('_')
        return f"feature_{clean[:30]}"  # Limit length

    def _log_ingestion(self, extracted: Dict[str, Any]):
        """Log ingestion event"""
        try:
            with open(self.ingestion_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(extracted, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error logging ingestion: {e}")

    def scan_documentation(self, directory: Optional[Path] = None) -> Dict[str, Any]:
        try:
            """
            Scan documentation directory for device/feature information

            Automatically ingests from all markdown files.
            """
            if directory is None:
                directory = self.project_root / "docs"

            if not directory.exists():
                logger.warning(f"⚠️  Directory not found: {directory}")
                return {}

            results = {
                "files_scanned": 0,
                "files_ingested": 0,
                "devices_found": 0,
                "features_found": 0
            }

            # Scan markdown files
            for md_file in directory.rglob("*.md"):
                results["files_scanned"] += 1
                extracted = self.ingest_from_documentation(md_file)

                if extracted.get("devices") or extracted.get("features"):
                    results["files_ingested"] += 1
                    results["devices_found"] += len(extracted.get("devices", []))
                    results["features_found"] += len(extracted.get("features", []))

            logger.info(f"📚 Scanned {results['files_scanned']} files, ingested {results['files_ingested']}")
            logger.info(f"   Found {results['devices_found']} devices, {results['features_found']} features")

            return results


        except Exception as e:
            self.logger.error(f"Error in scan_documentation: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Homelab Knowledge Ingestion")
        parser.add_argument("--scan-docs", action="store_true", help="Scan documentation directory")
        parser.add_argument("--ingest-file", type=str, metavar="FILE", help="Ingest from specific file")
        parser.add_argument("--ingest-text", type=str, metavar="TEXT", help="Ingest from text")

        args = parser.parse_args()

        ingestion = HomelabKnowledgeIngestion()

        if args.scan_docs:
            results = ingestion.scan_documentation()
            print(f"\n📚 Scan Results:")
            print(f"   Files scanned: {results['files_scanned']}")
            print(f"   Files ingested: {results['files_ingested']}")
            print(f"   Devices found: {results['devices_found']}")
            print(f"   Features found: {results['features_found']}")

        if args.ingest_file:
            file_path = Path(args.ingest_file)
            extracted = ingestion.ingest_from_documentation(file_path)
            print(f"\n✅ Ingested from {file_path.name}")
            print(f"   Devices: {len(extracted.get('devices', []))}")
            print(f"   Features: {len(extracted.get('features', []))}")

        if args.ingest_text:
            extracted = ingestion.ingest_from_conversation(args.ingest_text)
            print(f"\n✅ Ingested from text")
            print(f"   Devices: {len(extracted.get('devices', []))}")
            print(f"   Features: {len(extracted.get('features', []))}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()