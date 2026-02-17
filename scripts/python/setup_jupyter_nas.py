"""
Jupyter Notebook Server Setup on NAS
Sets up Jupyter Notebook server on NAS with resource-aware system integration

Author: <COMPANY_NAME> LLC
Date: 2025-01-24
"""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JupyterNASSetup")


def setup_jupyter_nas(
    project_root: Path,
    nas_ip: str = "<NAS_PRIMARY_IP>",
    jupyter_port: int = 8888
) -> None:
    """
    Set up Jupyter Notebook server on NAS

    Args:
        project_root: Project root directory (should be D:\\Dropbox\\my_projects)
        nas_ip: NAS IP address
        jupyter_port: Jupyter server port
    """
    project_root = Path(project_root)

    logger.info(f"Setting up Jupyter Notebook Server on NAS")
    logger.info(f"Project Root: {project_root}")
    logger.info(f"NAS IP: {nas_ip}")
    logger.info(f"Jupyter Port: {jupyter_port}")

    # Create necessary directories
    directories = [
        project_root / "data" / "jupyter",
        project_root / "config" / "jupyter"
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created/verified directory: {directory}")

    # Create Jupyter config directory
    jupyter_config_dir = Path.home() / ".jupyter"
    jupyter_config_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Jupyter config directory: {jupyter_config_dir}")

    # Create Jupyter configuration
    project_root_escaped = str(project_root).replace('\\', '\\\\')
    jupyter_config_content = f"""# Jupyter Notebook Server Configuration for NAS
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

c = get_config()

# Server configuration
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = {jupyter_port}
c.ServerApp.open_browser = False
c.ServerApp.allow_root = True
c.ServerApp.token = ''
c.ServerApp.password = ''

# Notebook directory (NAS or local)
c.ServerApp.notebook_dir = r'{project_root_escaped}\\data\\jupyter'

# Enable extensions
c.ServerApp.allow_origin = '*'
c.ServerApp.disable_check_xsrf = True

# Enable file browser
c.ContentsManager.allow_hidden = True

# Enable all kernels
c.MultiKernelManager.default_kernel_name = 'python3'

# Resource-aware system integration
# Add project root to Python path for library access
import sys
import os
project_root = r'{project_root_escaped}'
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    sys.path.insert(0, os.path.join(project_root, 'scripts'))
    sys.path.insert(0, os.path.join(project_root, 'scripts', 'python'))

# Logging
c.Application.log_level = 'INFO'
"""

    jupyter_config_path = jupyter_config_dir / "jupyter_labconfig.py"
    with open(jupyter_config_path, 'w', encoding='utf-8') as f:
        f.write(jupyter_config_content)

    logger.info(f"✓ Jupyter configuration created: {jupyter_config_path}")

    # Create NAS configuration
    nas_config = {
        "nas": {
            "ip": nas_ip,
            "path": f"\\\\{nas_ip}\\backups\\MATT_Backups",
            "jupyter_port": jupyter_port,
            "project_root": str(project_root),
            "notebook_directory": str(project_root / "data" / "jupyter")
        },
        "integration": {
            "memory_manager": True,
            "resource_aware_context": True,
            "holocron_query": True,
            "r5_living_context": True
        },
        "access": {
            "local": f"http://localhost:{jupyter_port}",
            "nas": f"http://{nas_ip}:{jupyter_port}",
            "network": f"http://{nas_ip}:{jupyter_port}"
        },
        "library_paths": [
            str(project_root),
            str(project_root / "scripts"),
            str(project_root / "scripts" / "python")
        ]
    }

    nas_config_path = project_root / "config" / "jupyter" / "nas_config.json"
    with open(nas_config_path, 'w', encoding='utf-8') as f:
        json.dump(nas_config, f, indent=2)

    logger.info(f"✓ NAS configuration created: {nas_config_path}")

    # Create sample notebook
    sample_notebook = create_sample_notebook(project_root)
    notebook_path = project_root / "data" / "jupyter" / "Resource_Aware_System_Integration.ipynb"
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(sample_notebook, f, indent=2)

    logger.info(f"✓ Sample notebook created: {notebook_path}")

    print("\n=== Jupyter Notebook Server Setup Complete ===")
    print(f"Project Root: {project_root}")
    print(f"Jupyter Port: {jupyter_port}")
    print(f"NAS IP: {nas_ip}")
    print(f"Notebook Directory: {project_root / 'data' / 'jupyter'}")
    print("\nTo start Jupyter:")
    print(f"  jupyter lab --config={jupyter_config_path} --port={jupyter_port}")
    print("\nAccess Jupyter:")
    print(f"  Local: http://localhost:{jupyter_port}")
    print(f"  NAS: http://{nas_ip}:{jupyter_port}")


def create_sample_notebook(project_root: Path) -> Dict[str, Any]:
    """Create sample notebook with resource-aware system integration"""
    project_root_str = str(project_root).replace('\\', '\\\\')

    return {
        "cells": [
            {
                "cell_type": "markdown",
                "source": [
                    "# Resource-Aware System Integration\n\n",
                    "This notebook integrates with the resource-aware system for memory, R5, and Holocron access."
                ]
            },
            {
                "cell_type": "code",
                "source": [
                    "import sys\n",
                    "import os\n",
                    "from pathlib import Path\n",
                    "\n",
                    "# Add project root to path\n",
                    f"project_root = Path(r'{project_root_str}')\n",
                    "sys.path.insert(0, str(project_root))\n",
                    "sys.path.insert(0, str(project_root / 'scripts' / 'python'))\n",
                    "\n",
                    "print(f'Project root: {project_root}')\n",
                    "print(f'Python path updated')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "source": [
                    "# Import resource-aware system modules\n",
                    "try:\n",
                    "    from memory_manager import MemoryManager, MemoryType, get_memory_manager\n",
                    "    from resource_aware_context import ResourceAwareContextChecker, should_use_ai\n",
                    "    from holocron_query import HolocronQueryEngine\n",
                    "    from r5_living_context_matrix import R5LivingContextMatrix\n",
                    "    print('✓ Resource-aware system modules loaded')\n",
                    "except ImportError as e:\n",
                    "    print(f'✗ Failed to import modules: {e}')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "source": [
                    "# Example: Query memory\n",
                    "memory_manager = get_memory_manager(project_root)\n",
                    "memories = memory_manager.retrieve('example query', limit=5)\n",
                    "print(f'Found {len(memories)} memories')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "source": [
                    "# Example: Check resource-aware context\n",
                    "checker = ResourceAwareContextChecker(project_root)\n",
                    "result = checker.check_context('example query')\n",
                    "print(f'Should use AI: {result.should_use_ai}')\n",
                    "print(f'Confidence: {result.confidence_score}')\n",
                    "print(f'Tokens saved: {result.tokens_saved}')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "source": [
                    "# Example: Query Holocrons\n",
                    "holocron_engine = HolocronQueryEngine(project_root)\n",
                    "results = holocron_engine.query('Tesla autonomous', limit=5)\n",
                    "for result in results:\n",
                    "    print(f'{result.entry.title}: {result.relevance_score:.2f}')"
                ],
                "execution_count": None,
                "outputs": []
            },
            {
                "cell_type": "code",
                "source": [
                    "# Example: R5 Living Context Matrix\n",
                    "r5 = R5LivingContextMatrix(project_root)\n",
                    "data = r5.export_for_jupyter()\n",
                    "print(f'R5 Sessions: {data[\"metadata\"][\"total_sessions\"]}')\n",
                    "print(f'R5 Messages: {data[\"metadata\"][\"total_messages\"]}')"
                ],
                "execution_count": None,
                "outputs": []
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (Resource-Aware)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python",
                "version": "3.8+"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }


if __name__ == "__main__":
    # Default to D drive Dropbox
    project_root = Path(r"D:\Dropbox\my_projects")

    setup_jupyter_nas(
        project_root=project_root,
        nas_ip="<NAS_PRIMARY_IP>",
        jupyter_port=8888
    )

