#!/usr/bin/env python3
"""
Analyze Quantum Mechanics Integration in Lumina
                    -LUM THE MODERN

Comprehensive analysis of how much quantum mechanics is incorporated into Lumina's logic.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("QuantumAnalysis")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("QuantumAnalysis")

def analyze_quantum_documents():
    """Analyze quantum mechanics documents"""
    quantum_docs = [
        "docs/QUANTUM_CONTEXT_SCORING.md",
        "docs/philosophy/QUANTUM_ENTANGLEMENT_MULTIVERSE.md",
        "docs/system/LUMINA_QUANTUM_ENTANGLEMENT_SIMULATIONS.md",
        "docs/system/LUMINA_QUANTUM_ENTANGLEMENT_COMPLETE.md",
        "docs/system/LUMINA_QUANTUM_ENTANGLEMENT_SUMMARY.md",
        "docs/system/QUANTUM_ENTANGLEMENT_10000_YEARS.md",
        "docs/lumina_quantum_validation_integration.md",
        "docs/quantum_validation_lattice_system.md",
        "quantum_enhanced_lumina_complete.md"
    ]

    quantum_concepts = defaultdict(int)
    quantum_files = []

    for doc_path in quantum_docs:
        full_path = project_root / doc_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                quantum_files.append({
                    "path": doc_path,
                    "size": len(content),
                    "lines": len(content.split('\n'))
                })

                # Count quantum concepts
                concepts = {
                    "superposition": content.lower().count("superposition"),
                    "entanglement": content.lower().count("entanglement"),
                    "quantum": content.lower().count("quantum"),
                    "qubit": content.lower().count("qubit"),
                    "quantum_state": content.lower().count("quantum state"),
                    "quantum_computing": content.lower().count("quantum computing"),
                    "quantum_logic": content.lower().count("quantum logic"),
                    "quantum_algorithm": content.lower().count("quantum algorithm"),
                    "wave_function": content.lower().count("wave function"),
                    "quantum_mechanics": content.lower().count("quantum mechanics"),
                    "quantum_entanglement": content.lower().count("quantum entanglement"),
                    "quantum_superposition": content.lower().count("quantum superposition")
                }

                for concept, count in concepts.items():
                    quantum_concepts[concept] += count

            except Exception as e:
                logger.warning(f"Could not read {doc_path}: {e}")

    return {
        "files": quantum_files,
        "concepts": dict(quantum_concepts),
        "total_files": len(quantum_files)
    }

def analyze_quantum_in_code():
    """Analyze quantum mechanics usage in code"""
    quantum_keywords = [
        "quantum", "qubit", "superposition", "entanglement",
        "quantum_state", "quantum_computing", "quantum_logic",
        "wave_function", "quantum_algorithm"
    ]

    code_files = []
    total_matches = 0

    # Search in Python scripts
    scripts_dir = project_root / "scripts" / "python"
    if scripts_dir.exists():
        for py_file in scripts_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding='utf-8')
                matches = {}
                for keyword in quantum_keywords:
                    count = content.lower().count(keyword)
                    if count > 0:
                        matches[keyword] = count
                        total_matches += count

                if matches:
                    code_files.append({
                        "file": str(py_file.relative_to(project_root)),
                        "matches": matches,
                        "total_matches": sum(matches.values())
                    })
            except Exception as e:
                pass

    return {
        "code_files": code_files,
        "total_matches": total_matches,
        "files_with_quantum": len(code_files)
    }

def analyze_quantum_in_config():
    """Analyze quantum mechanics in configuration files"""
    config_files = []

    # Check specific config files
    config_paths = [
        "config/physics_simulation_config.yaml",
        "config/one_ring_blueprint.json",
        "config/r5/@r5d4_astro-mythical-mech.hero.jsn"
    ]

    for config_path in config_paths:
        full_path = project_root / config_path
        if full_path.exists():
            try:
                content = full_path.read_text(encoding='utf-8')
                quantum_count = content.lower().count("quantum")
                if quantum_count > 0:
                    config_files.append({
                        "file": config_path,
                        "quantum_references": quantum_count
                    })
            except Exception as e:
                pass

    return {"config_files": config_files}

def generate_quantum_integration_report():
    try:
        """Generate comprehensive quantum mechanics integration report"""
        logger.info("=" * 80)
        logger.info("🔬 QUANTUM MECHANICS INTEGRATION ANALYSIS")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)

        # Analyze documents
        logger.info("\n📚 Analyzing Quantum Mechanics Documents...")
        doc_analysis = analyze_quantum_documents()

        logger.info(f"\n   Total Quantum Documents: {doc_analysis['total_files']}")
        logger.info(f"   Quantum Concepts Found:")
        for concept, count in sorted(doc_analysis['concepts'].items(), key=lambda x: x[1], reverse=True):
            if count > 0:
                logger.info(f"      - {concept}: {count} references")

        # Analyze code
        logger.info("\n💻 Analyzing Quantum Mechanics in Code...")
        code_analysis = analyze_quantum_in_code()

        logger.info(f"\n   Files with Quantum References: {code_analysis['files_with_quantum']}")
        logger.info(f"   Total Quantum References: {code_analysis['total_matches']}")

        if code_analysis['code_files']:
            logger.info(f"\n   Top Files:")
            for code_file in sorted(code_analysis['code_files'], key=lambda x: x['total_matches'], reverse=True)[:5]:
                logger.info(f"      - {code_file['file']}: {code_file['total_matches']} references")

        # Analyze config
        logger.info("\n⚙️  Analyzing Quantum Mechanics in Configuration...")
        config_analysis = analyze_quantum_in_config()

        logger.info(f"\n   Config Files with Quantum: {len(config_analysis['config_files'])}")
        for config_file in config_analysis['config_files']:
            logger.info(f"      - {config_file['file']}: {config_file['quantum_references']} references")

        # Calculate integration percentage
        total_quantum_refs = (
            sum(doc_analysis['concepts'].values()) +
            code_analysis['total_matches'] +
            sum(c['quantum_references'] for c in config_analysis['config_files'])
        )

        logger.info("\n" + "=" * 80)
        logger.info("📊 QUANTUM INTEGRATION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Total Quantum References: {total_quantum_refs}")
        logger.info(f"   Quantum Documents: {doc_analysis['total_files']}")
        logger.info(f"   Code Files with Quantum: {code_analysis['files_with_quantum']}")
        logger.info(f"   Config Files with Quantum: {len(config_analysis['config_files'])}")
        logger.info("=" * 80)

        # Generate report
        report = {
            "analysis_date": str(Path(__file__).stat().st_mtime),
            "document_analysis": doc_analysis,
            "code_analysis": code_analysis,
            "config_analysis": config_analysis,
            "total_quantum_references": total_quantum_refs,
            "integration_level": "comprehensive" if total_quantum_refs > 100 else "moderate" if total_quantum_refs > 50 else "basic"
        }

        report_path = project_root / "data" / "quantum_integration_analysis.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        logger.info(f"\n💾 Report saved: {report_path}")
        logger.info("=" * 80)

        return report

    except Exception as e:
        logger.error(f"Error in generate_quantum_integration_report: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    report = generate_quantum_integration_report()
