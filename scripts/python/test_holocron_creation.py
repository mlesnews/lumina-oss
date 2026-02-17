#!/usr/bin/env python3
"""Quick test to create a sample Holocron notebook"""

import sys
from pathlib import Path
import json

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ultron_to_lumina_docuseries_pipeline import ULTRONToLuminaPipeline

# Create pipeline
pipeline = ULTRONToLuminaPipeline()

# Test channel info
test_channel = {
    "name": "Dave's Garage",
    "handle": "@DavesGarage",
    "url": "https://www.youtube.com/@DavesGarage"
}

# Create a sample Holocron notebook structure
sample_transcript = """
This is a sample transcript from a video about technology and coding.
The video discusses various topics including Python programming,
system design, and best practices for software development.
"""

sample_intelligence = {
    "actionable_items": [
        "Learn Python best practices",
        "Study system design patterns",
        "Practice coding regularly"
    ],
    "key_insights": [
        "Python is versatile for many applications",
        "System design is crucial for scalability",
        "Continuous learning is essential"
    ]
}

# Create Holocron notebook
holocron = pipeline._create_holocron_notebook(
    video_id="TEST001",
    video_url="https://www.youtube.com/watch?v=TEST001",
    channel_info=test_channel,
    transcript=sample_transcript,
    intelligence=sample_intelligence,
    timestamp="20251231_190000"
)

# Save to file
notebook_path = pipeline.jupyter_dir / "holocron_TEST001_20251231_190000.ipynb"
with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(holocron, f, indent=2, ensure_ascii=False)

print(f"✅ Sample Holocron created: {notebook_path}")
print(f"   Location: {pipeline.jupyter_dir}")
print(f"   NAS Jupyter: http://<NAS_PRIMARY_IP>:8888")
print(f"\n📚 Holocron contains:")
print(f"   - Title and metadata")
print(f"   - Intelligence summary")
print(f"   - Transcript")
print(f"   - Analysis code cells")
print(f"   - Data export cells")
