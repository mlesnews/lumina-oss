#!/usr/bin/env python3
"""
Correct Ticket Numbering to match PM 3000+ standard.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("correct_ticket_numbering")


def correct_numbering():
    try:
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data" / "pr_tickets"
        ticket_dir = data_dir / "tickets"
        map_file = data_dir / "pr_ticket_map.json"
        counter_file = data_dir / "ticket_counter.json"

        # Starting at 3050 as requested (since we were around 50)
        NEW_START = 3050

        print(f"🚀 Correcting ticket numbering to start at {NEW_START}...")

        # 1. Update counter
        with open(counter_file, 'w', encoding='utf-8') as f:
            json.dump({"counter": NEW_START, "last_updated": datetime.now().isoformat()}, f, indent=2)

        # 2. Migrate existing PM000000001... to PM000003001...
        if map_file.exists():
            with open(map_file, 'r', encoding='utf-8') as f:
                ticket_map = json.load(f)
        else:
            ticket_map = {"pr_to_ticket": {}, "ticket_to_pr": {}, "entries": []}

        id_map = {}
        for ticket_file in sorted(ticket_dir.glob("PM000000*.json")):
            old_id = ticket_file.stem
            num = int(old_id.replace("PM", ""))
            new_id = f"PM{3000 + num:09d}"
            id_map[old_id] = new_id

            print(f"   Re-indexing {old_id} → {new_id}")

            with open(ticket_file, 'r', encoding='utf-8') as f:
                content = json.load(f)
            content["ticket_number"] = new_id

            new_file = ticket_dir / f"{new_id}.json"
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)
            ticket_file.unlink()

        # Update map
        new_ticket_to_pr = {}
        for old_id, pr_id in ticket_map["ticket_to_pr"].items():
            if old_id in id_map:
                new_ticket_to_pr[id_map[old_id]] = pr_id
            else:
                new_ticket_to_pr[old_id] = pr_id

        for pr_id, old_id in ticket_map["pr_to_ticket"].items():
            if old_id in id_map:
                ticket_map["pr_to_ticket"][pr_id] = id_map[old_id]

        for entry in ticket_map["entries"]:
            if entry["ticket_number"] in id_map:
                entry["ticket_number"] = id_map[entry["ticket_number"]]

        ticket_map["ticket_to_pr"] = new_ticket_to_pr
        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(ticket_map, f, indent=2)

        # Clean up Holocron
        holocron_ticket_dir = project_root / "data" / "holocron" / "tickets"
        if holocron_ticket_dir.exists():
            for f in holocron_ticket_dir.glob("PM000000*"):
                f.unlink()

        # Re-migrate
        print(f"🔄 Re-migrating to Holocron & Database...")
        os.system(f"python {project_root}/scripts/python/jarvis_tickets_to_holocron_db.py --all")

        print(f"✅ Corrected ticket numbering and re-indexed existing tickets.")

    except Exception as e:
        logger.error(f"Error in correct_numbering: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    correct_numbering()
