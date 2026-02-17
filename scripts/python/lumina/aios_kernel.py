#!/usr/bin/env python3
"""
AIOS Kernel - Core AI Operating System Service

Runs as the main service in Docker containers.
Provides unified API for all AIOS capabilities.

Tags: #KERNEL #AIOS #DOCKER #SERVICE @JARVIS @LUMINA
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import asyncio
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIOSKernel")

# Initialize AIOS
try:
    from lumina.aios import AIOS
    aios = AIOS()
    logger.info("✅ AIOS Kernel initialized")
except Exception as e:
    logger.error(f"❌ Failed to initialize AIOS: {e}")
    aios = None

# Create FastAPI app
app = FastAPI(
    title="AIOS Kernel",
    description="AI Operating System - Core Service",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AIOS Kernel",
        "version": "1.0.0",
        "status": "operational" if aios else "degraded",
        "aios_initialized": aios is not None
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    status = aios.get_status()
    return {
        "healthy": status.get('initialized', False),
        "status": "operational" if status.get('initialized') else "degraded",
        "components": {
            "entry_layer": status.get('entry_layer', {}).get('peak') is not None,
            "knowledge_layer": status.get('knowledge_layer', {}).get('library') is not None,
            "inference_layer": status.get('inference_layer', {}).get('reality') is not None,
            "transformation_layer": status.get('transformation_layer', {}).get('pegl') is not None,
            "aos_core": status.get('aos_core', {}).get('spatial_graph') is not None,
            "foundation": status.get('foundation', {}).get('layer_zero') is not None,
            "ai_connection": status.get('ai_connection', {}).get('available', False),
            "homelab": status.get('homelab', {}).get('available', False),
            "simulators": status.get('simulators', {}).get('available', False),
            "ab_testing": status.get('ab_testing', {}).get('available', False),
            "quantum_entanglement": status.get('quantum_entanglement', {}).get('available', False)
        }
    }


@app.get("/status")
async def status():
    """Get full AIOS status"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    return aios.get_status()


@app.post("/execute")
async def execute(query: dict):
    """Execute query through AIOS"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    try:
        result = aios.execute(
            query.get("query", ""),
            use_flow=query.get("use_flow", True),
            use_pegl=query.get("use_pegl", False)
        )
        return result
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/infer")
async def infer(query: dict):
    """Execute AI inference"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    if not aios.ai_connection:
        raise HTTPException(status_code=503, detail="AI Connection not available")

    try:
        result = aios.infer(
            query.get("query", ""),
            **query.get("kwargs", {})
        )
        return result
    except Exception as e:
        logger.error(f"Inference error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/simulate")
async def simulate(simulation: dict):
    """Run simulation"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    if not aios.simulators:
        raise HTTPException(status_code=503, detail="Simulators not available")

    try:
        result = aios.simulators.simulate(
            simulation.get("type", "wopr"),
            simulation.get("scenario", ""),
            use_flow=simulation.get("use_flow", True)
        )
        return result
    except Exception as e:
        logger.error(f"Simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/quantum")
async def quantum(params: dict):
    """Run quantum entanglement simulation"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    if not aios.quantum_entanglement:
        raise HTTPException(status_code=503, detail="Quantum Entanglement not available")

    try:
        from lumina.quantum_entanglement import EntanglementState

        years = params.get("years", 10000)
        ent_type_str = params.get("entanglement_type", "bell_phi_plus")

        # Map string to enum
        ent_type_map = {
            "bell_phi_plus": EntanglementState.BELL_PHI_PLUS,
            "bell_phi_minus": EntanglementState.BELL_PHI_MINUS,
            "bell_psi_plus": EntanglementState.BELL_PSI_PLUS,
            "bell_psi_minus": EntanglementState.BELL_PSI_MINUS,
            "ghz": EntanglementState.GHZ,
            "w": EntanglementState.W
        }

        ent_type = ent_type_map.get(ent_type_str, EntanglementState.BELL_PHI_PLUS)

        result = aios.quantum_entanglement.simulate_entanglement(
            years=years,
            time_step=params.get("time_step", "year"),
            entanglement_type=ent_type,
            apply_learning=params.get("apply_learning", True)
        )
        return result
    except Exception as e:
        logger.error(f"Quantum simulation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/components")
async def components():
    """List available components"""
    if not aios:
        raise HTTPException(status_code=503, detail="AIOS not initialized")

    status = aios.get_status()

    return {
        "components": {
            "entry_layer": "Lumina Peak",
            "knowledge_layer": "Library, Digest",
            "inference_layer": "Hybrid Reality, Simple Reality, Layer Zero",
            "transformation_layer": "PEGL, Flow",
            "aos_core": "Spatial Graph, Quantum State Machine, HID Layer",
            "foundation": "Reality Layer Zero",
            "infrastructure": "Docker, API Gateway",
            "ai_connection": "ULTRON, KAIJU, Cloud AI",
            "homelab": "ULTRON, KAIJU, NAS",
            "simulators": "WOPR, Matrix, Animatrix",
            "ab_testing": "A/B Testing, Curve Grading",
            "quantum_entanglement": "Quantum Simulations"
        },
        "status": status
    }


def main():
    """Run AIOS Kernel service"""
    port = int(os.getenv("AIOS_PORT", "8080"))
    host = os.getenv("AIOS_HOST", "0.0.0.0")

    logger.info("=" * 80)
    logger.info("🚀 AIOS KERNEL - Starting Service")
    logger.info("=" * 80)
    logger.info(f"   Host: {host}")
    logger.info(f"   Port: {port}")
    logger.info(f"   AIOS Initialized: {aios is not None}")
    logger.info("=" * 80)

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )


if __name__ == "__main__":


    main()