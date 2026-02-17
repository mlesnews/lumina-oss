#!/usr/bin/env python3
"""
Extract Cursor Chat/Agent History from All Workspaces
Aggregates chat history across all Cursor workspaces including workgroup folders

IMPORTANT: When using workgroup folders, each folder has its own workspaceStorage entry.
This script finds ALL workspaces and extracts chat history from each.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("extract_cursor_chat_history")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from r5_living_context_matrix import R5LivingContextMatrix
    from syphon.extractors import IDEExtractor

    syphon = SYPHONSystem(SYPHONConfig(project_root=project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(project_root)

    # Register IDE extractor for chat history
    if DataSourceType.IDE not in syphon.extractors:
        syphon.register_extractor(DataSourceType.IDE, IDEExtractor(syphon.config))


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

    def find_cursor_chat_history_files() -> List[Dict[str, Any]]:
        try:
            """Find Cursor chat history files from History directory and workspaceStorage"""
            chat_files = []
            appdata = Path(os.getenv("APPDATA", ""))

            # Primary location: User/History (contains chat/conversation JSON files)
            history_dir = appdata / "Cursor" / "User" / "History"

            if history_dir.exists():
                print(f"🔍 Scanning Cursor History directory: {history_dir}")
                for history_file in history_dir.rglob("*.json"):
                    if not history_file.is_file():
                        continue

                    file_size = history_file.stat().st_size
                    file_name = history_file.name.lower()

                    # Skip entries.json files (these are file edit history, not chat)
                    if file_name == "entries.json":
                        continue

                    # Include files that are:
                    # 1. Large enough to contain actual conversations (>5KB)
                    # 2. OR have chat-related names and are >1KB
                    is_chat_related = any(kw in file_name for kw in ["chat", "conversation", "session", "agent", "message"])
                    min_size = 5000 if not is_chat_related else 1000

                    if file_size > min_size:
                        chat_files.append({
                            "path": history_file,
                            "size": file_size,
                            "modified": datetime.fromtimestamp(history_file.stat().st_mtime).isoformat(),
                            "source": "cursor_history_directory"
                        })

                print(f"   Found {len(chat_files)} chat conversation files (filtered from file edit history)")

            return chat_files

        except Exception as e:
            logger.error(f"Error in find_cursor_chat_history_files: {e}", exc_info=True)
            raise
    def find_cursor_workspaces() -> List[Dict[str, Any]]:
        """Find all Cursor workspace directories for workgroup tracking"""
        workspaces = []
        appdata = Path(os.getenv("APPDATA", ""))
        workspace_storage = appdata / "Cursor" / "User" / "workspaceStorage"

        if not workspace_storage.exists():
            print("⚠️  Cursor workspaceStorage not found")
            return workspaces

        print(f"🔍 Scanning Cursor workspaceStorage for workgroup info: {workspace_storage}")

        for workspace_dir in workspace_storage.iterdir():
            if not workspace_dir.is_dir():
                continue

            workspace_info = {
                "id": workspace_dir.name,
                "path": workspace_dir,
                "workspace_json": workspace_dir / "workspace.json",
                "folders": [],
                "chat_files": [],
                "conversation_files": []
            }

            # Read workspace.json to get folder paths
            workspace_json_path = workspace_dir / "workspace.json"
            if workspace_json_path.exists():
                try:
                    with open(workspace_json_path, 'r', encoding='utf-8') as f:
                        ws_data = json.load(f)
                        if "folders" in ws_data:
                            workspace_info["folders"] = [f.get("path", "") for f in ws_data["folders"]]
                except Exception as e:
                    print(f"  ⚠️  Error reading workspace.json: {e}")

            # Find chat/conversation files
            for file_path in workspace_dir.rglob("*"):
                if not file_path.is_file():
                    continue

                file_name_lower = file_path.name.lower()

                # Look for chat/conversation/session files
                if any(keyword in file_name_lower for keyword in [
                    "chat", "conversation", "session", "history", "agent", 
                    "message", "thread", "dialogue"
                ]):
                    # Only include JSON or database files of reasonable size
                    if file_path.suffix in [".json", ".db", ".sqlite", ".sqlite3"]:
                        if file_path.stat().st_size > 100:  # Skip tiny files
                            workspace_info["chat_files"].append({
                                "path": file_path,
                                "size": file_path.stat().st_size,
                                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                            })

            if workspace_info["chat_files"] or workspace_info["folders"]:
                workspaces.append(workspace_info)

        return workspaces

    def extract_chat_from_json(file_path: Path) -> Optional[str]:
        """Extract chat content from JSON file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

                # Try various JSON structures
                if isinstance(data, list):
                    # Array of messages/conversations
                    messages = []
                    for item in data:
                        if isinstance(item, dict):
                            # Extract message-like fields
                            content = ""
                            if "content" in item:
                                content = item["content"]
                            elif "message" in item:
                                content = item["message"]
                            elif "text" in item:
                                content = item["text"]

                            role = item.get("role", item.get("sender", item.get("from", "unknown")))
                            timestamp = item.get("timestamp", item.get("time", item.get("date", "")))

                            if content:
                                messages.append(f"[{role}] {timestamp}: {content}")

                    return "\n".join(messages) if messages else None

                elif isinstance(data, dict):
                    # Object with messages/conversations
                    messages = []

                    # Check common chat structures
                    for key in ["messages", "conversations", "history", "chats", "threads", "sessions"]:
                        if key in data and isinstance(data[key], list):
                            for item in data[key]:
                                if isinstance(item, dict):
                                    content = item.get("content") or item.get("message") or item.get("text")
                                    role = item.get("role") or item.get("sender") or "unknown"
                                    if content:
                                        messages.append(f"[{role}]: {content}")

                    # If no structured messages, try to extract any text content
                    if not messages:
                        content_str = json.dumps(data, indent=2)
                        if len(content_str) < 100000:  # Only if not too large
                            return content_str

                    return "\n".join(messages) if messages else None
        except Exception as e:
            print(f"  ⚠️  Error reading {file_path.name}: {e}")

        return None

    def extract_chat_from_db(file_path: Path) -> Optional[str]:
        """Extract chat content from SQLite database"""
        try:
            conn = sqlite3.connect(str(file_path))
            cursor = conn.cursor()

            # Get all table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            messages = []
            for table_name in tables:
                table = table_name[0]
                try:
                    # Get column names
                    cursor.execute(f"PRAGMA table_info({table})")
                    columns = [row[1] for row in cursor.fetchall()]

                    # Try to find message-like columns
                    content_cols = [c for c in columns if any(k in c.lower() for k in ["content", "message", "text", "body"])]
                    role_cols = [c for c in columns if any(k in c.lower() for k in ["role", "sender", "from", "user", "type"])]

                    if content_cols:
                        # Build query
                        select_cols = content_cols
                        if role_cols:
                            select_cols = role_cols + select_cols

                        query = f"SELECT {', '.join(select_cols)} FROM {table} LIMIT 1000"
                        rows = cursor.fetchall()

                        for row in rows:
                            if role_cols and content_cols:
                                role = row[0] if row[0] else "unknown"
                                content = row[1] if len(row) > 1 else str(row[0])
                            else:
                                role = "unknown"
                                content = str(row[0]) if row[0] else ""

                            if content:
                                messages.append(f"[{role}]: {content}")
                except Exception as e:
                    continue  # Skip tables we can't read

            conn.close()
            return "\n".join(messages) if messages else None

        except Exception as e:
            print(f"  ⚠️  Error reading database {file_path.name}: {e}")

        return None

    def process_workspace_chat_history(workspace_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process chat history from a single workspace"""
        extracted = []

        print(f"\n📂 Processing workspace: {workspace_info['id']}")
        if workspace_info["folders"]:
            print(f"   Folders: {len(workspace_info['folders'])}")
            for folder in workspace_info["folders"]:
                print(f"     - {folder}")

        for chat_file in workspace_info["chat_files"]:
            file_path = chat_file["path"]
            print(f"   📄 {file_path.name} ({chat_file['size']} bytes)")

            # Extract content based on file type
            content = None
            if file_path.suffix == ".json":
                content = extract_chat_from_json(file_path)
            elif file_path.suffix in [".db", ".sqlite", ".sqlite3"]:
                content = extract_chat_from_db(file_path)

            if content and len(content) > 50:  # Only if we got meaningful content
                extracted.append({
                    "workspace_id": workspace_info["id"],
                    "workspace_folders": workspace_info["folders"],
                    "file_path": str(file_path),
                    "file_name": file_path.name,
                    "content": content,
                    "size": chat_file["size"],
                    "modified": chat_file["modified"]
                })
                print(f"     ✅ Extracted {len(content)} characters")

        return extracted

    def main():
        """Main extraction function"""
        print("=" * 70)
        print("CURSOR CHAT HISTORY EXTRACTION - ALL WORKSPACES")
        print("=" * 70)

        # Find chat history files from History directory
        chat_files = find_cursor_chat_history_files()

        # Find workspaces for workgroup tracking
        workspaces = find_cursor_workspaces()

        if not chat_files and not workspaces:
            print("\n❌ No Cursor chat history or workspaces found")
            return

        print(f"\n✅ Found {len(chat_files)} chat history file(s)")
        if workspaces:
            print(f"✅ Found {len(workspaces)} workspace(s) (for workgroup tracking)")

        # Process chat history files
        all_chat_history = []
        for chat_file in chat_files:
            try:
                # Read chat file content
                with open(chat_file["path"], 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                if len(content) > 50:
                    all_chat_history.append({
                        "workspace_id": "history_directory",
                        "workspace_folders": [],
                        "file_path": str(chat_file["path"]),
                        "file_name": chat_file["path"].name,
                        "content": content,
                        "size": chat_file["size"],
                        "modified": chat_file["modified"],
                        "source": chat_file.get("source", "cursor_history")
                    })
                    print(f"  ✅ Extracted: {chat_file['path'].name} ({len(content)} chars)")
            except Exception as e:
                print(f"  ⚠️  Error reading {chat_file['path'].name}: {e}")

        # Also process workspace-specific files
        for workspace in workspaces:
            extracted = process_workspace_chat_history(workspace)
            all_chat_history.extend(extracted)

        print(f"\n📊 Total chat files extracted: {len(all_chat_history)}")

        if not all_chat_history:
            print("\n⚠️  No chat history found in workspace files")
            print("   Note: Cursor may store chat history in a different format or location")
            return

        # Process through SYPHON and ingest to R5
        processed_count = 0
        for chat_data in all_chat_history:
            try:
                # Create metadata
                metadata = {
                    "workspace_id": chat_data["workspace_id"],
                    "workspace_folders": chat_data["workspace_folders"],
                    "file_path": chat_data["file_path"],
                    "file_name": chat_data["file_name"],
                    "source_type": "cursor_chat_history",
                    "extraction_type": "cursor_workspace_chat"
                }

                # Extract with SYPHON
                result = syphon.extract(
                    DataSourceType.IDE,
                    {"notifications": [{"message": chat_data["content"][:5000], "severity": "info"}]},
                    metadata
                )

                if result.success and result.data:
                    # Ingest to R5
                    session_data = {
                        "session_id": f"cursor_chat_{chat_data['workspace_id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                        "session_type": "cursor_chat_history",
                        "timestamp": chat_data["modified"],
                        "content": chat_data["content"],
                        "metadata": {
                            **metadata,
                            "actionable_items": result.data.actionable_items,
                            "tasks": result.data.tasks,
                            "intelligence": result.data.intelligence
                        }
                    }

                    r5.ingest_session(session_data)
                    processed_count += 1
                    print(f"  ✅ Processed: {chat_data['file_name']}")
            except Exception as e:
                print(f"  ❌ Error processing {chat_data['file_name']}: {e}")

        print(f"\n✅ Complete! Processed {processed_count}/{len(all_chat_history)} chat files")
        print(f"   All history ingested to R5 Living Context Matrix")

    if __name__ == "__main__":

        main()
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

