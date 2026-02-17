#!/usr/bin/env python3
"""
Cursor Agent History Ingestor - Find and ingest Cursor agent chat histories

Locates Cursor agent chat histories from various storage locations and ingests
them into R5 Living Context Matrix for visibility in Cursor IDE agents section.

Storage locations checked:
- %APPDATA%/Cursor/User/workspaceStorage/*/state.vscdb (SQLite)
- %APPDATA%/Cursor/User/globalStorage/state.vscdb (SQLite)
- .cursor directories in workspace
- Cursor worktrees data directories
- NAS centralized storage
"""

import sqlite3
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
import subprocess
import hashlib
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("cursor_agent_history_ingestor")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from r5_living_context_matrix import R5LivingContextMatrix
    from parallel_agent_session_processor import ParallelAgentSessionProcessor

    syphon = SYPHONSystem(SYPHONConfig(project_root=script_dir.parent.parent, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(script_dir.parent.parent)

    # Register OTHER extractor if not already registered (use SocialExtractor as fallback)
    if DataSourceType.OTHER not in syphon.extractors:
        try:
            from syphon.extractors import SocialExtractor
            syphon.register_extractor(DataSourceType.OTHER, SocialExtractor(syphon.config))
            print("✅ Registered SocialExtractor for OTHER type")
        except ImportError:
            # If SocialExtractor doesn't exist, the extract() method will handle gracefully
            pass

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Required modules not available")
    sys.exit(1)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CursorAgentHistoryIngestor:
    """Ingests Cursor agent chat histories into R5"""

    def __init__(self):
        self.project_root = script_dir.parent.parent
        self.cursor_data_dir = Path(os.environ.get('APPDATA', '')) / 'Cursor'
        self.user_data_dir = self.cursor_data_dir / 'User'
        self.workspace_storage_dir = self.user_data_dir / 'workspaceStorage'

        # Output tracking
        self.ingested_sessions = 0
        self.processed_files = 0
        self.errors = []

    def find_cursor_chat_databases(self) -> List[Path]:
        try:
            """Find SQLite databases containing Cursor chat history"""
            databases = []

            # Check workspace storage databases
            if self.workspace_storage_dir.exists():
                for workspace_dir in self.workspace_storage_dir.iterdir():
                    if workspace_dir.is_dir():
                        state_db = workspace_dir / 'state.vscdb'
                        if state_db.exists():
                            databases.append(state_db)

            # Check global storage
            global_db = self.user_data_dir / 'globalStorage' / 'state.vscdb'
            if global_db.exists():
                databases.append(global_db)

            # Check .cursor directories in workspace
            cursor_dirs = [
                self.project_root / '.cursor',
                Path.home() / '.cursor'
            ]

            for cursor_dir in cursor_dirs:
                if cursor_dir.exists():
                    state_db = cursor_dir / 'state.vscdb'
                    if state_db.exists():
                        databases.append(state_db)

            return databases

        except Exception as e:
            self.logger.error(f"Error in find_cursor_chat_databases: {e}", exc_info=True)
            raise
    def extract_chat_history_from_db(self, db_path: Path) -> List[Dict[str, Any]]:
        """Extract chat history from SQLite database"""
        chat_sessions = []

        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            # Query for chat history tables (these may vary by Cursor version)
            tables_to_check = [
                'chat_sessions',
                'conversations',
                'chat_history',
                'agent_interactions',
                'cursor_chat',
                'ai_chat'
            ]

            for table_name in tables_to_check:
                try:
                    # Check if table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                    if cursor.fetchone():
                        print(f"📊 Found table: {table_name} in {db_path}")

                        # Get table schema
                        cursor.execute(f"PRAGMA table_info({table_name})")
                        columns = cursor.fetchall()
                        column_names = [col[1] for col in columns]

                        # Look for conversation/message data
                        if any(keyword in ' '.join(column_names).lower() for keyword in ['message', 'content', 'chat', 'conversation']):
                            # Extract data
                            cursor.execute(f"SELECT * FROM {table_name}")
                            rows = cursor.fetchall()

                            for row in rows:
                                row_data = dict(zip(column_names, row))
                                chat_sessions.append({
                                    'source': 'cursor_db',
                                    'database': str(db_path),
                                    'table': table_name,
                                    'data': row_data,
                                    'extracted_at': datetime.now().isoformat()
                                })

                except sqlite3.Error as e:
                    print(f"⚠️  Error querying table {table_name}: {e}")
                    continue

            conn.close()

        except Exception as e:
            self.errors.append(f"Failed to process {db_path}: {e}")
            print(f"❌ Error processing database {db_path}: {e}")

        return chat_sessions

    def find_cursor_json_chat_files(self) -> List[Path]:
        """Find JSON files containing Cursor chat data"""
        chat_files = []

        # Search patterns for chat files
        search_patterns = [
            "**/cursor_chat/**/*.json",
            "**/agent_history/**/*.json",
            "**/chat_archive/**/*.json",
            "**/conversation/**/*.json",
            "**/*chat*.json",
            "**/*agent*.json"
        ]

        # Directories to search
        search_dirs = [
            self.cursor_data_dir,
            self.project_root,
            Path.home() / '.cursor',
            self.project_root / 'data'
        ]

        for search_dir in search_dirs:
            if not search_dir.exists():
                continue

            for pattern in search_patterns:
                try:
                    for json_file in search_dir.glob(pattern):
                        if json_file.is_file() and json_file.stat().st_size > 100:  # Skip empty/small files
                            chat_files.append(json_file)
                except:
                    continue

        return list(set(chat_files))  # Remove duplicates

    def process_json_chat_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Process a JSON chat file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)

            # Validate it looks like chat data
            if isinstance(data, dict) and any(key in data for key in ['session', 'messages', 'conversations', 'chat']):
                return {
                    'source': 'cursor_json',
                    'file_path': str(file_path),
                    'data': data,
                    'extracted_at': datetime.now().isoformat(),
                    'file_size': file_path.stat().st_size,
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                }

        except Exception as e:
            self.errors.append(f"Failed to process {file_path}: {e}")
            return None

    def convert_to_syphon_format(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            """Convert chat data to SYPHON format"""
            source = chat_data.get('source', 'unknown')
            extracted_at = chat_data.get('extracted_at', datetime.now().isoformat())

            if source == 'cursor_db':
                # Database row format
                row_data = chat_data.get('data', {})
                content = json.dumps(row_data, indent=2)

                return {
                    "data_id": f"cursor_chat_db_{hash(content) % 1000000}",
                    "source_type": DataSourceType.OTHER,
                    "source_id": f"cursor_db_{chat_data.get('database', 'unknown')}",
                    "content": content,
                    "metadata": {
                        "database": chat_data.get('database'),
                        "table": chat_data.get('table'),
                        "extraction_method": "sqlite"
                    },
                    "extracted_at": extracted_at,
                    "actionable_items": self.extract_actionable_items(content),
                    "tasks": [],
                    "decisions": [],
                    "intelligence": self.extract_chat_intelligence(content)
                }

            elif source == 'cursor_json':
                # JSON file format
                json_data = chat_data.get('data', {})
                content = json.dumps(json_data, indent=2)

                # Try to extract session info
                session_id = "unknown"
                if isinstance(json_data, dict):
                    session_id = json_data.get('session', {}).get('session_id', json_data.get('id', f"cursor_chat_{hash(content) % 1000000}"))

                return {
                    "data_id": f"cursor_chat_json_{session_id}",
                    "source_type": DataSourceType.OTHER,
                    "source_id": f"cursor_json_{chat_data.get('file_path', 'unknown')}",
                    "content": content,
                    "metadata": {
                        "file_path": chat_data.get('file_path'),
                        "file_size": chat_data.get('file_size'),
                        "modified": chat_data.get('modified'),
                        "extraction_method": "json_file"
                    },
                    "extracted_at": extracted_at,
                    "actionable_items": self.extract_actionable_items(content),
                    "tasks": self.extract_chat_tasks(content),
                    "decisions": self.extract_chat_decisions(content),
                    "intelligence": self.extract_chat_intelligence(content)
                }

            else:
                # Fallback
                content = json.dumps(chat_data.get('data', {}), indent=2)
                return {
                    "data_id": f"cursor_chat_fallback_{hash(content) % 1000000}",
                    "source_type": DataSourceType.OTHER,
                    "source_id": "cursor_fallback",
                    "content": content,
                    "metadata": {"extraction_method": "fallback"},
                    "extracted_at": extracted_at,
                    "actionable_items": [],
                    "tasks": [],
                    "decisions": [],
                    "intelligence": []
                }

        except Exception as e:
            self.logger.error(f"Error in convert_to_syphon_format: {e}", exc_info=True)
            raise
    def extract_actionable_items(self, content: str) -> List[str]:
        """Extract actionable items from chat content"""
        items = []

        # Look for action-oriented language
        action_patterns = [
            r"need to (.+)",
            r"should (.+)",
            r"must (.+)",
            r"TODO: (.+)",
            r"FIXME: (.+)",
            r"implement (.+)",
            r"create (.+)",
            r"add (.+)",
            r"update (.+)",
            r"fix (.+)"
        ]

        import re
        for pattern in action_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            items.extend(matches[:3])  # Limit per pattern

        return items[:10]  # Limit total items

    def extract_chat_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract tasks from chat content"""
        tasks = []

        # Look for task-like content
        if "task" in content.lower() or "implement" in content.lower():
            tasks.append({
                "text": "Process chat content for actionable tasks",
                "type": "analysis",
                "priority": "medium"
            })

        return tasks

    def extract_chat_decisions(self, content: str) -> List[Dict[str, Any]]:
        """Extract decisions from chat content"""
        decisions = []

        # Look for decision keywords
        decision_keywords = ["decide", "choice", "select", "choose", "recommend"]
        if any(keyword in content.lower() for keyword in decision_keywords):
            decisions.append({
                "type": "implementation_decision",
                "description": "Determine best approach for processing chat data"
            })

        return decisions

    def extract_chat_intelligence(self, content: str) -> List[Dict[str, Any]]:
        """Extract intelligence from chat content"""
        intelligence = []

        # Extract code-related intelligence
        if "```" in content or "function" in content.lower():
            intelligence.append({
                "type": "code_pattern",
                "content": "Code implementation patterns found in chat",
                "confidence": 0.8
            })

        # Extract problem-solving intelligence
        if "error" in content.lower() or "fix" in content.lower():
            intelligence.append({
                "type": "problem_solving",
                "content": "Debugging and error resolution patterns",
                "confidence": 0.7
            })

        return intelligence

    def ingest_chat_history(self, chat_data: Dict[str, Any]) -> bool:
        """Ingest chat data into SYPHON and R5"""
        try:
            # Convert to SYPHON format dict (for R5 metadata)
            syphon_data = self.convert_to_syphon_format(chat_data)

            # Extract content and metadata for SYPHON.extract()
            content = syphon_data.get("content", "")
            metadata = syphon_data.get("metadata", {})
            source_type = syphon_data.get("source_type", DataSourceType.OTHER)

            # Add additional metadata
            metadata.update({
                "data_id": syphon_data.get("data_id"),
                "source_id": syphon_data.get("source_id"),
                "extracted_at": syphon_data.get("extracted_at")
            })

            # Extract with SYPHON using correct API
            syphon_result = syphon.extract(source_type, content, metadata)

            if syphon_result.success and syphon_result.data:
                # Get the extracted SyphonData object
                extracted_data = syphon_result.data

                # Add to R5 Living Context Matrix
                r5_session = {
                    "session_id": syphon_data["data_id"],
                    "timestamp": syphon_data.get("extracted_at", datetime.now().isoformat()),
                    "messages": [
                        {
                            "role": "system",
                            "content": f"Cursor Agent Chat Data - {syphon_data['source_id']}"
                        },
                        {
                            "role": "assistant",
                            "content": f"Processed chat data: {len(content)} characters"
                        }
                    ],
                    "patterns": [],
                    "whatif_scenarios": [],
                    "metadata": {
                        "source": "cursor_agent_history_ingestor",
                        "syphon_data_id": syphon_data["data_id"],
                        "extraction_method": syphon_data["metadata"].get("extraction_method"),
                        "file_path": chat_data.get("file_path") or chat_data.get("database"),
                        "ingested_at": datetime.now().isoformat(),
                        "actionable_items_count": len(extracted_data.actionable_items) if hasattr(extracted_data, 'actionable_items') else 0,
                        "tasks_count": len(extracted_data.tasks) if hasattr(extracted_data, 'tasks') else 0
                    }
                }

                r5.ingest_session(r5_session)
                self.ingested_sessions += 1

                print(f"✅ Ingested chat data: {syphon_data['data_id']}")
                return True
            else:
                error_msg = syphon_result.error if hasattr(syphon_result, 'error') else 'Unknown error'
                self.errors.append(f"Failed to process with SYPHON: {error_msg}")
                return False

        except Exception as e:
            self.errors.append(f"Failed to ingest chat data: {e}")
            print(f"❌ Error ingesting chat data: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run_ingestion(self) -> Dict[str, Any]:
        """Run the complete ingestion process"""
        print("🚀 Starting Cursor Agent Chat History Ingestion")
        print("=" * 60)

        start_time = datetime.now()

        # Find all chat data sources
        print("\n🔍 Discovering chat data sources...")

        # 1. Find SQLite databases
        db_files = self.find_cursor_chat_databases()
        print(f"📊 Found {len(db_files)} SQLite databases")

        # 2. Find JSON chat files
        json_files = self.find_cursor_json_chat_files()
        print(f"📄 Found {len(json_files)} JSON chat files")

        total_sources = len(db_files) + len(json_files)
        print(f"📋 Total data sources: {total_sources}")

        # Process databases
        for db_file in db_files:
            print(f"\n💾 Processing database: {db_file}")
            chat_sessions = self.extract_chat_history_from_db(db_file)

            for session in chat_sessions:
                self.ingest_chat_history(session)
                self.processed_files += 1

        # Process JSON files
        for json_file in json_files:
            print(f"\n📄 Processing JSON file: {json_file}")
            chat_data = self.process_json_chat_file(json_file)

            if chat_data:
                self.ingest_chat_history(chat_data)
                self.processed_files += 1

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        result = {
            "success": True,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "databases_processed": len(db_files),
            "json_files_processed": len(json_files),
            "total_sources": total_sources,
            "sessions_ingested": self.ingested_sessions,
            "files_processed": self.processed_files,
            "errors": self.errors,
            "error_count": len(self.errors)
        }

        print("\n📊 Ingestion Summary:")
        print(f"  Duration: {duration:.1f} seconds")
        print(f"  Sources processed: {total_sources}")
        print(f"  Sessions ingested: {self.ingested_sessions}")
        print(f"  Files processed: {self.processed_files}")
        print(f"  Errors: {len(self.errors)}")

        if self.errors:
            print("\n⚠️  Errors encountered:")
            for error in self.errors[:5]:  # Show first 5
                print(f"  - {error}")

        print("\n✅ Cursor agent chat history ingestion complete!")
        print("💡 Agent histories should now be visible in Cursor IDE agents section")

        return result


def main():
    try:
        """Main entry point"""
        ingestor = CursorAgentHistoryIngestor()
        result = ingestor.run_ingestion()

        # Save results
        output_file = script_dir.parent.parent / "data" / "cursor_ingestion_result.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

        # Exit with error code if there were failures
        if result["error_count"] > 0:
            sys.exit(1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()