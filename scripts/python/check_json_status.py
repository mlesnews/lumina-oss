#!/usr/bin/env python3
"""Check JSON file status"""

import json
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def check_json():
    syphon_file = Path('data/syphon/extracted_data.json')
    print(f'Checking SYPHON file: {syphon_file.exists()}')

    if syphon_file.exists():
        try:
            with open(syphon_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f'✅ SYPHON file is valid JSON with {len(data)} entries')

            # Check for video content
            video_count = 0
            for entry in data:
                content = entry.get('content', '').lower()
                if any(keyword in content for keyword in ['elon', 'musk', 'video', 'psychosis', 'llm']):
                    video_count += 1

            print(f'🎥 Video-related entries: {video_count}')

        except json.JSONDecodeError as e:
            print(f'❌ SYPHON JSON error: {e}')
        except Exception as e:
            print(f'❌ Other error: {e}')
    else:
        print('❌ SYPHON file does not exist')

if __name__ == "__main__":
    check_json()
