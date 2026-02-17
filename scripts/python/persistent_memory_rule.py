#!/usr/bin/env python3
"""
Persistent Memory Rule - Auto-Process Workflows
Rule: No constant explanations - auto-digest to Holocrons/DB/YouTube
Importance scoring: 5+ star system (+, ++, +++, ++++, +++++)
"""

# RULE: Auto-process workflows without constant explanations
# Back half: Data digested into Holocrons, DB, YouTube content
# Persistent memory with importance scoring (5+ star system)

AUTO_PROCESS = True
MINIMAL_EXPLANATION = True
AUTO_STORE_HOLOCRON = True
AUTO_STORE_DB = True
AUTO_GENERATE_CONTENT = True

IMPORTANCE_LEVELS = {
    1: (0, 20, "+"),
    2: (21, 40, "++"),
    3: (41, 60, "+++"),
    4: (61, 80, "++++"),
    5: (81, 100, "+++++")
}

def should_explain(importance_score: int) -> bool:
    """Rule: Only explain if importance is 5+ (+++++)"""
    return importance_score >= 81

def get_importance_symbol(score: int) -> str:
    """Get importance symbol based on score"""
    for level, (min_score, max_score, symbol) in IMPORTANCE_LEVELS.items():
        if min_score <= score <= max_score:
            return symbol
    return "+"
