#!/usr/bin/env python3
"""Create Jupyter notebooks for Problem and Change Management"""
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Problem Management Notebook
pm_notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "source": [
                "# Problem Management Notebook\n\n",
                "**Team:** Problem Management Team  \n",
                "**Purpose:** Track problems, root cause analysis, resolution management  \n",
                "**Tags:** #PROBLEMMANAGEMENT #HELPDESK #ROOT_CAUSE_ANALYSIS\n\n",
                "---\n\n",
                "## Data Sources\n\n",
                "- `data/cursor_retry_tracking/` - Retry actions\n",
                "- `data/cross_reference/` - Cross-reference database\n",
                "- `data/notification_tickets/` - Ticket tracking\n",
                "- `data/diagnostics/` - Diagnostic data"
            ]
        },
        {
            "cell_type": "code",
            "source": [
                "import json\n",
                "import pandas as pd\n",
                "from pathlib import Path\n",
                "from datetime import datetime\n",
                "\n",
                "# Project root\n",
                "project_root = Path().resolve().parent.parent\n",
                "data_dir = project_root / 'data'\n",
                "\n",
                "print(f'Project root: {project_root}')"
            ]
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 4
}

# Change Management Notebook
cm_notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "source": [
                "# Change Management Notebook\n\n",
                "**Team:** Change Management Team  \n",
                "**Purpose:** Track changes, impact analysis, deployment coordination  \n",
                "**Tags:** #CHANGEMANAGEMENT #HELPDESK #DEPLOYMENT\n\n",
                "---\n\n",
                "## Data Sources\n\n",
                "- `data/cursor_retry_tracking/` - Change-related retries\n",
                "- `data/cross_reference/` - Cross-reference database\n",
                "- `data/notification_tickets/` - Change tickets\n",
                "- `config/helpdesk/` - Change management team config"
            ]
        },
        {
            "cell_type": "code",
            "source": [
                "import json\n",
                "import pandas as pd\n",
                "from pathlib import Path\n",
                "from datetime import datetime\n",
                "\n",
                "# Project root\n",
                "project_root = Path().resolve().parent.parent\n",
                "data_dir = project_root / 'data'\n",
                "\n",
                "print(f'Project root: {project_root}')"
            ]
        }
    ],
    "metadata": {},
    "nbformat": 4,
    "nbformat_minor": 4
}

# Write notebooks
pm_dir = project_root / "notebooks" / "problem_management"
cm_dir = project_root / "notebooks" / "change_management"

pm_dir.mkdir(parents=True, exist_ok=True)
cm_dir.mkdir(parents=True, exist_ok=True)

with open(pm_dir / "problem_management.ipynb", 'w') as f:
    json.dump(pm_notebook, f, indent=2)

with open(cm_dir / "change_management.ipynb", 'w') as f:
    json.dump(cm_notebook, f, indent=2)

print("✅ Jupyter notebooks created")
