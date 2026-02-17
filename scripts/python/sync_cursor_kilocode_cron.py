#!/usr/bin/env python3
"""
Sync Cursor and Kilo Code Configurations

Keeps Cursor and Kilo Code in sync:
- Rules: .cursor/rules/*.mdc -> .kilocode/rules/*.md
- Skills -> Custom Modes: .cursor/skills/*/SKILL.md -> custom_modes.yaml
- Workflows: docs/workflow/*.md referenced in modes

Schedule: Run hourly or on-demand

Tags: #CRON #SYNC #CURSOR #KILOCODE @JARVIS
"""

import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path

import yaml

# Paths
LUMINA_ROOT = Path(__file__).parent.parent.parent
CURSOR_RULES_DIR = LUMINA_ROOT / ".cursor" / "rules"
CURSOR_SKILLS_DIR = LUMINA_ROOT / ".cursor" / "skills"
KILO_RULES_DIR = LUMINA_ROOT / ".kilocode" / "rules"
KILO_MODES_FILE = (
    Path(os.environ.get("APPDATA", ""))
    / "Cursor"
    / "User"
    / "globalStorage"
    / "kilocode.kilo-code"
    / "settings"
    / "custom_modes.yaml"
)
WORKFLOW_DOCS_DIR = LUMINA_ROOT / "docs" / "workflow"
SYNC_LOG_FILE = LUMINA_ROOT / "data" / "sync" / "cursor_kilocode_sync.jsonl"

# Ensure directories exist
KILO_RULES_DIR.mkdir(parents=True, exist_ok=True)
SYNC_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)


def sync_rules() -> dict:
    """Sync Cursor rules (.mdc) to Kilo Code rules (.md)"""
    result = {"synced": [], "skipped": [], "errors": []}

    if not CURSOR_RULES_DIR.exists():
        result["errors"].append(f"Cursor rules directory not found: {CURSOR_RULES_DIR}")
        return result

    for cursor_rule in CURSOR_RULES_DIR.glob("*.mdc"):
        try:
            # Convert .mdc to .md (same content, different extension)
            kilo_rule = KILO_RULES_DIR / (cursor_rule.stem + ".md")

            # Check if sync needed (file changed or doesn't exist)
            needs_sync = False
            if not kilo_rule.exists():
                needs_sync = True
            else:
                # Compare modification times
                if cursor_rule.stat().st_mtime > kilo_rule.stat().st_mtime:
                    needs_sync = True

            if needs_sync:
                shutil.copy2(cursor_rule, kilo_rule)
                result["synced"].append(cursor_rule.stem)
            else:
                result["skipped"].append(cursor_rule.stem)

        except Exception as e:
            result["errors"].append(f"{cursor_rule.stem}: {str(e)}")

    return result


def parse_skill_md(skill_path: Path) -> dict:
    """Parse a Cursor SKILL.md file into structured data"""
    content = skill_path.read_text(encoding="utf-8")

    skill_data = {
        "name": "",
        "description": "",
        "when_to_use": "",
        "required_behavior": "",
        "references": [],
    }

    # Parse YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1])
                skill_data["name"] = frontmatter.get("name", "")
                skill_data["description"] = frontmatter.get("description", "")
            except Exception:
                pass
            content = parts[2]

    # Extract sections
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)
    for section in sections:
        lines = section.strip().split("\n", 1)
        if len(lines) < 2:
            continue
        header = lines[0].lower().strip()
        body = lines[1].strip() if len(lines) > 1 else ""

        if "when to use" in header:
            skill_data["when_to_use"] = body
        elif "required behavior" in header:
            skill_data["required_behavior"] = body
        elif "reference" in header:
            skill_data["references"] = [
                line.strip("- ").strip()
                for line in body.split("\n")
                if line.strip().startswith("-")
            ]

    return skill_data


def skill_to_kilo_mode(skill_data: dict, slug: str) -> dict:
    """Convert Cursor skill data to Kilo Code custom mode format"""
    # Create role definition from description
    role_def = f"You are an AI assistant specialized in {skill_data['description']}. "
    role_def += "Follow project conventions and best practices."

    # Build custom instructions from required behavior
    instructions = skill_data.get("required_behavior", "")
    if skill_data.get("references"):
        instructions += "\n\nReferences:\n" + "\n".join(
            f"- {ref}" for ref in skill_data["references"]
        )

    return {
        "slug": slug,
        "name": skill_data.get("name", slug).replace("--", "").replace("-", " ").title(),
        "description": skill_data.get("description", f"Mode for {slug}"),
        "roleDefinition": role_def,
        "whenToUse": skill_data.get("when_to_use", ""),
        "customInstructions": instructions,
        "groups": ["read", "edit", "browser", "command", "mcp"],
    }


def sync_skills_to_modes() -> dict:
    """Sync Cursor skills to Kilo Code custom modes"""
    result = {"synced": [], "skipped": [], "errors": []}

    if not CURSOR_SKILLS_DIR.exists():
        result["errors"].append(f"Cursor skills directory not found: {CURSOR_SKILLS_DIR}")
        return result

    if not KILO_MODES_FILE.parent.exists():
        result["errors"].append(f"Kilo Code settings directory not found: {KILO_MODES_FILE.parent}")
        return result

    # Load existing modes
    existing_modes = {"customModes": []}
    if KILO_MODES_FILE.exists():
        try:
            with open(KILO_MODES_FILE, encoding="utf-8") as f:
                existing_modes = yaml.safe_load(f) or {"customModes": []}
        except Exception as e:
            result["errors"].append(f"Error reading existing modes: {e}")

    # Get existing mode slugs
    existing_slugs = {m.get("slug") for m in existing_modes.get("customModes", [])}

    # Process each skill
    new_modes = []
    for skill_dir in CURSOR_SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue

        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue

        slug = skill_dir.name.lstrip("-")

        try:
            skill_data = parse_skill_md(skill_file)
            mode = skill_to_kilo_mode(skill_data, slug)

            if slug in existing_slugs:
                # Update existing mode
                for i, m in enumerate(existing_modes["customModes"]):
                    if m.get("slug") == slug:
                        existing_modes["customModes"][i] = mode
                        result["synced"].append(slug)
                        break
            else:
                # Add new mode
                new_modes.append(mode)
                result["synced"].append(slug)

        except Exception as e:
            result["errors"].append(f"{slug}: {str(e)}")

    # Add new modes
    existing_modes["customModes"].extend(new_modes)

    # Write updated modes
    if result["synced"]:
        try:
            with open(KILO_MODES_FILE, "w", encoding="utf-8") as f:
                yaml.dump(
                    existing_modes, f, default_flow_style=False, allow_unicode=True, sort_keys=False
                )
        except Exception as e:
            result["errors"].append(f"Error writing modes file: {e}")

    return result


def get_workflow_docs() -> list:
    """Get list of workflow documents for reference"""
    workflows = []
    if WORKFLOW_DOCS_DIR.exists():
        for doc in WORKFLOW_DOCS_DIR.glob("*.md"):
            workflows.append({"name": doc.stem, "path": str(doc.relative_to(LUMINA_ROOT))})
    return workflows


def log_sync(rules_result: dict, modes_result: dict) -> None:
    """Log sync result to JSONL file"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "rules": {
            "synced": len(rules_result.get("synced", [])),
            "skipped": len(rules_result.get("skipped", [])),
            "errors": len(rules_result.get("errors", [])),
        },
        "modes": {
            "synced": len(modes_result.get("synced", [])),
            "skipped": len(modes_result.get("skipped", [])),
            "errors": len(modes_result.get("errors", [])),
        },
        "details": {"rules": rules_result, "modes": modes_result},
    }

    try:
        with open(SYNC_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry) + "\n")
    except Exception as e:
        print(f"Error writing sync log: {e}")


def main():
    """Main sync function"""
    print("=" * 60)
    print("CURSOR <-> KILO CODE SYNC")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    # 1. Sync rules
    print("1. Syncing Rules...")
    print(f"   From: {CURSOR_RULES_DIR}")
    print(f"   To:   {KILO_RULES_DIR}")

    rules_result = sync_rules()

    if rules_result["synced"]:
        print(f"   ✅ Synced {len(rules_result['synced'])} rules:")
        for rule in rules_result["synced"][:5]:
            print(f"      - {rule}")
        if len(rules_result["synced"]) > 5:
            print(f"      ... and {len(rules_result['synced']) - 5} more")

    if rules_result["skipped"]:
        print(f"   ⏭️  Skipped {len(rules_result['skipped'])} rules (unchanged)")

    if rules_result["errors"]:
        print(f"   ❌ Errors: {len(rules_result['errors'])}")
        for error in rules_result["errors"]:
            print(f"      - {error}")

    print()

    # 2. Sync skills to custom modes
    print("2. Syncing Skills → Custom Modes...")
    print(f"   From: {CURSOR_SKILLS_DIR}")
    print(f"   To:   {KILO_MODES_FILE}")

    modes_result = sync_skills_to_modes()

    if modes_result["synced"]:
        print(f"   ✅ Synced {len(modes_result['synced'])} modes:")
        for mode in modes_result["synced"][:5]:
            print(f"      - {mode}")
        if len(modes_result["synced"]) > 5:
            print(f"      ... and {len(modes_result['synced']) - 5} more")

    if modes_result["skipped"]:
        print(f"   ⏭️  Skipped {len(modes_result['skipped'])} modes (unchanged)")

    if modes_result["errors"]:
        print(f"   ❌ Errors: {len(modes_result['errors'])}")
        for error in modes_result["errors"]:
            print(f"      - {error}")

    print()

    # 3. List workflow docs (for reference)
    print("3. Workflow Documents Available...")
    workflows = get_workflow_docs()
    if workflows:
        print(f"   📋 Found {len(workflows)} workflow docs:")
        for wf in workflows[:5]:
            print(f"      - {wf['name']}")
        if len(workflows) > 5:
            print(f"      ... and {len(workflows) - 5} more")
        print("   (Referenced in modes' customInstructions)")
    else:
        print("   ℹ️  No workflow docs found")

    # Log the sync
    log_sync(rules_result, modes_result)

    print()
    print("=" * 60)
    total_synced = len(rules_result["synced"]) + len(modes_result["synced"])
    total_errors = len(rules_result["errors"]) + len(modes_result["errors"])

    if total_errors == 0:
        print(f"✅ Sync complete: {total_synced} items synced")
    else:
        print(f"⚠️ Sync complete with errors: {total_synced} synced, {total_errors} errors")

    print("=" * 60)

    return 0 if total_errors == 0 else 1


if __name__ == "__main__":
    exit(main())
