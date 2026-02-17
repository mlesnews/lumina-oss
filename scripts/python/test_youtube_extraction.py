#!/usr/bin/env python3
"""Test YouTube learnings extraction"""
import json
from pathlib import Path

data = json.load(open('data/lumina_youtube_learning/qPUPmz6Zh4g.json'))

class VideoObj:
    def __init__(self, data):
        for k, v in data.items():
            setattr(self, k, v)

v = VideoObj(data)
print(f'Review type: {type(v.review)}')
print(f'Review is dict: {isinstance(v.review, dict)}')
if isinstance(v.review, dict):
    print(f'Has learnings_for_lumina: {"learnings_for_lumina" in v.review}')
    print(f'Learnings count: {len(v.review.get("learnings_for_lumina", []))}')
    print(f'Learnings: {v.review.get("learnings_for_lumina", [])[:3]}')
