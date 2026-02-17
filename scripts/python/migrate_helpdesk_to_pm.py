#!/usr/bin/env python3
"""
Migrate HELPDESK- tickets to PM syntax (9 digits).
Updates files, mappings, and triggers re-migration to Holocron & DB.
"""

import os
import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("migrate_helpdesk_to_pm")


def migrate_tickets():
    try:
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / "data" / "pr_tickets"
        ticket_dir = data_dir / "tickets"
        map_file = data_dir / "pr_ticket_map.json"
        counter_file = data_dir / "ticket_counter.json"

        print(f"🚀 Starting ticket migration to PM syntax...")

        # 1. Load map
        if map_file.exists():
            with open(map_file, 'r', encoding='utf-8') as f:
                ticket_map = json.load(f)
        else:
            ticket_map = {"pr_to_ticket": {}, "ticket_to_pr": {}, "entries": []}

        # 2. Iterate HELPDESK tickets
        new_ticket_to_pr = {}
        new_entries = []

        # Old to new mapping
        id_map = {}

        for ticket_file in sorted(ticket_dir.glob("HELPDESK-*.json")):
            old_id = ticket_file.stem
            num = int(old_id.replace("HELPDESK-", ""))
            new_id = f"PM{num:09d}"
            id_map[old_id] = new_id

            print(f"   Renaming {old_id} → {new_id}")

            # Load and update content
            with open(ticket_file, 'r', encoding='utf-8') as f:
                content = json.load(f)

            content["ticket_number"] = new_id

            # Write new file
            new_file = ticket_dir / f"{new_id}.json"
            with open(new_file, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2)

            # Delete old file
            ticket_file.unlink()

        # 3. Update map
        # Update ticket_to_pr keys
        for old_id, pr_id in ticket_map["ticket_to_pr"].items():
            if old_id in id_map:
                new_ticket_to_pr[id_map[old_id]] = pr_id
            else:
                new_ticket_to_pr[old_id] = pr_id

        # Update pr_to_ticket values
        for pr_id, old_id in ticket_map["pr_to_ticket"].items():
            if old_id in id_map:
                ticket_map["pr_to_ticket"][pr_id] = id_map[old_id]

        # Update entries
        for entry in ticket_map["entries"]:
            if entry["ticket_number"] in id_map:
                entry["ticket_number"] = id_map[entry["ticket_number"]]
            new_entries.append(entry)

        ticket_map["ticket_to_pr"] = new_ticket_to_pr
        ticket_map["entries"] = new_entries

        with open(map_file, 'w', encoding='utf-8') as f:
            json.dump(ticket_map, f, indent=2)

        # 4. Update counter file to 10 (since we have 9 tickets)
        with open(counter_file, 'w', encoding='utf-8') as f:
            json.dump({"counter": 10, "last_updated": datetime.now().isoformat()}, f, indent=2)

        print(f"✅ Renamed files and updated mappings.")

        # 5. Clean up Holocron tickets directory
        holocron_ticket_dir = project_root / "data" / "holocron" / "tickets"
        if holocron_ticket_dir.exists():
            for f in holocron_ticket_dir.glob("HELPDESK-*"):
                f.unlink()

        # 6. Re-run migration script
        print(f"🔄 Re-migrating to Holocron & Database...")
        os.system(f"python {project_root}/scripts/python/jarvis_tickets_to_holocron_db.py --all")

        print(f"🎉 Migration complete!")

    except Exception as e:
        logger.error(f"Error in migrate_tickets: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    migrate_tickets()
