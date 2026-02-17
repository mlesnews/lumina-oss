from pathlib import Path
import sys
from datetime import datetime
import json

# Add scripts/python to path
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from jedi_librarian_system import JediLibrarian
    lib = JediLibrarian()
    lib.catalog_notebook(Path('data/holocron/archives/900_History_and_Docuseries/docuseries_ch2_script.md'), {
        'title': 'Docuseries Chapter 2: The Foundation',
        'classification': 'Δ-900.2',
        'tags': ['history', 'docuseries', 'foundation'],
        'chapter_id': 'CH-002'
    })
    print("✅ Cataloged Chapter 2")
except Exception as e:
    print(f"❌ Cataloging failed: {e}")
