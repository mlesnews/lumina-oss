#!/usr/bin/env python3
"""Quick R5 aggregation using current workspace"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts/python to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Auto-detect project root (go up from scripts/python)
project_root = script_dir.parent

try:
    from r5_living_context_matrix import R5LivingContextMatrix

    # Initialize R5
    r5 = R5LivingContextMatrix(project_root)

    # Create session data
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

**Status**: ✅ Fully implemented, now registered in lumina_extensions_integration.json

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

## Actions Completed

1. ✅ SYPHON registered in lumina_extensions_integration.json
2. ✅ Codebase scavenged for existing patterns
3. ✅ Findings aggregated to R5
        """,
        "metadata": {
            "source": "codebase_scavenge",
            "findings": {
                "syphon_system": {
                    "found": True,
                    "location": "scripts/python/syphon/",
                    "status": "fully_implemented_and_registered"
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
    session_id = r5.ingest_session(session_data)
    print(f"✅ Codebase scavenge findings aggregated to R5: {session_id}")

    # Also save to file
    output_file = project_root / "data" / "r5_living_matrix" / "sessions" / f"{session_id}.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Session saved to: {output_file.relative_to(project_root)}")
    print("\n✅ All tasks complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

