#!/usr/bin/env python3
"""
Aggregate Codebase Scavenge Findings to R5

Uses local R5 integration patterns to aggregate findings.
"""

import json
from pathlib import Path
from datetime import datetime

# Auto-detect project root
script_path = Path(__file__).resolve()
# Go up from scripts/python/ to project root
project_root = script_path.parent.parent

try:
    from scripts.python.r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    print("Warning: R5 not available")


def aggregate_findings_to_r5():
    """Aggregate codebase scavenge findings to R5"""

    if not R5_AVAILABLE:
        print("R5 not available, skipping aggregation")
        return

    # Initialize R5
    r5 = R5LivingContextMatrix(project_root)

    # Create session data from scavenge findings
    session_data = {
        "session_id": f"codebase_scavenge_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "session_type": "codebase_scavenge",
        "timestamp": datetime.now().isoformat(),
        "content": """
# Codebase Scavenge Findings - R5 Aggregation

## SYPHON System Found ✅
**Location**: `scripts/python/syphon/`

**Components**:
- `core.py` - Main SYPHON system with modular extractors
- `models.py` - Data models (SyphonData, ExtractionResult, HealthStatus)
- `extractors.py` - Base extractor and implementations (Email, SMS, Banking)
- `storage.py` - Storage backend
- `health.py` - Health monitoring and self-healing
- `integration/n8n.py` - n8n integration

**Key Patterns**:
- Modular extractor architecture
- Self-healing with health checks
- Subscription tiers (basic, premium, enterprise)
- Banking extraction with feature gating
- Standardized interfaces

**Status**: ✅ Fully implemented, needs registration completion

---

## Local Azure Vault Pattern (#azvault) Found ✅
**Location**: `scripts/python/watcher_uatu_jarvis_integration.py`

**Pattern**:
- Local file-based vault storage (`data/azvault/`)
- `protect_in_azvault()` method
- Vault entry structure with metadata
- Categories: secrets, sparks, ideas

**Migration Needed**: ⚠️ Must migrate to Azure Key Vault

---

## Azure Service Bus Integration Found ✅
**Location**: `scripts/python/azure_service_bus_integration.py`

**Components**:
- `AzureServiceBusClient` - Service Bus client
- `AzureKeyVaultClient` - Key Vault client
- `ServiceBusMessage` - Message structure
- Topic/Queue publishing and subscription methods

**Status**: ✅ Architecture defined, needs implementation

---

## @PEAK Patterns Extracted

1. **Modular Extractor Pattern** - SYPHON's extractor architecture
2. **Local Vault Pattern** - File-based secret storage (to be migrated)
3. **Health Monitoring Pattern** - SYPHON's self-healing approach
4. **Subscription Tier Pattern** - Feature gating by tier

---

## @WHATIF Scenarios

1. **What if** all secrets are in Azure Key Vault? → Centralized, secure, rotatable
2. **What if** all communication is async via Service Bus? → Scalable, decoupled
3. **What if** SYPHON integrates with Lumina? → Unified intelligence extraction

---

## Next Actions

1. ✅ Complete SYPHON registration
2. ⚠️ Run secret audit
3. ⚠️ Migrate local vault to Azure Key Vault
4. ⚠️ Implement Azure Service Bus integration
        """,
        "metadata": {
            "source": "codebase_scavenge",
            "findings": {
                "syphon_system": {
                    "found": True,
                    "location": "scripts/python/syphon/",
                    "status": "fully_implemented"
                },
                "local_vault": {
                    "found": True,
                    "location": "scripts/python/watcher_uatu_jarvis_integration.py",
                    "migration_needed": True
                },
                "azure_integration": {
                    "found": True,
                    "location": "scripts/python/azure_service_bus_integration.py",
                    "status": "architecture_defined"
                }
            },
            "aggregated_to_r5": True,
            "timestamp": datetime.now().isoformat()
        }
    }

    # Ingest to R5
    r5.ingest_session(session_data)
    print("✅ Codebase scavenge findings aggregated to R5")

    # Also save to file for reference
    output_file = project_root / "data" / "r5_living_matrix" / "sessions" / f"{session_data['session_id']}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Session saved to: {output_file.relative_to(project_root)}")


if __name__ == "__main__":
    print("=" * 60)
    print("Aggregating Codebase Scavenge Findings to R5")
    print("=" * 60)
    print(f"Project Root: {project_root}\n")

    aggregate_findings_to_r5()

    print("\n" + "=" * 60)
    print("Aggregation Complete")
    print("=" * 60)

