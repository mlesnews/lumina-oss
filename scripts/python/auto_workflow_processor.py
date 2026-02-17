#!/usr/bin/env python3
"""
Auto Workflow Processor - No Explanations, Just Execute
Digests data into Holocrons, DB, and YouTube content
Uses persistent memory and importance scoring (5+ star system)
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

class AutoWorkflowProcessor:
    """Automated workflow processor - executes without constant explanations"""

    def __init__(self):
        self.config_path = Path(__file__).parent.parent.parent / "config" / "persistent_memory_config.json"
        self.config = self._load_config()

        self.holocron_dir = Path(__file__).parent.parent.parent / "data" / "holocrons"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = Path(__file__).parent.parent.parent / "data" / "persistent_memory.db"
        self._init_database()

    def _load_config(self) -> Dict:
        try:
            """Load configuration"""
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return {}

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _init_database(self):
        try:
            """Initialize persistent memory database"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Workflow history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    workflow_type TEXT,
                    action TEXT,
                    result TEXT,
                    importance_score INTEGER,
                    stored_to_holocron BOOLEAN,
                    stored_to_db BOOLEAN,
                    content_generated BOOLEAN
                )
            ''')

            # Holocron index
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS holocron_index (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    holocron_id TEXT UNIQUE,
                    title TEXT,
                    importance_score INTEGER,
                    category TEXT,
                    timestamp TEXT,
                    content_path TEXT
                )
            ''')

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def calculate_importance_score(self, workflow_data: Dict) -> int:
        """
        Calculate importance score (0-100) for 5+ star system

        Returns:
            Score 0-100 (maps to +, ++, +++, ++++, +++++)
        """
        score = 0

        # Factor: Workflow type
        workflow_type = workflow_data.get("workflow_type", "")
        if workflow_type in ["firewall", "security", "critical"]:
            score += 30
        elif workflow_type in ["network", "system"]:
            score += 20
        else:
            score += 10

        # Factor: Impact
        impact = workflow_data.get("impact", "low")
        if impact == "critical":
            score += 40
        elif impact == "high":
            score += 30
        elif impact == "medium":
            score += 20
        else:
            score += 10

        # Factor: Employee level
        employee_level = workflow_data.get("employee_level", 1)
        score += min(employee_level * 5, 20)

        # Factor: Data sources affected
        data_sources = workflow_data.get("data_sources", [])
        score += min(len(data_sources) * 2, 10)

        return min(score, 100)

    def get_importance_symbol(self, score: int) -> str:
        """Get importance symbol (+, ++, +++, ++++, ++++++)"""
        levels = self.config.get("importance_scoring", {}).get("levels", {})

        for level in ["5", "4", "3", "2", "1"]:
            level_config = levels.get(level, {})
            if level_config.get("min", 0) <= score <= level_config.get("max", 100):
                return level_config.get("symbol", "+")

        return "+"

    def store_to_holocron(self, data: Dict, importance_score: int) -> str:
        try:
            """
            Store data to Holocron (persistent knowledge)

            Returns:
                Holocron ID
            """
            if importance_score < self.config.get("holocrons", {}).get("importance_threshold", 3) * 20:
                return None

            holocron_id = f"HOLO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

            holocron_data = {
                "holocron_id": holocron_id,
                "timestamp": datetime.now().isoformat(),
                "importance_score": importance_score,
                "importance_symbol": self.get_importance_symbol(importance_score),
                "data": data,
                "category": data.get("category", "workflow"),
                "tags": data.get("tags", [])
            }

            # Store to file
            holocron_file = self.holocron_dir / f"{holocron_id}.json"
            with open(holocron_file, 'w') as f:
                json.dump(holocron_data, f, indent=2)

            # Index in database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO holocron_index 
                (holocron_id, title, importance_score, category, timestamp, content_path)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                holocron_id,
                data.get("title", "Workflow Data"),
                importance_score,
                data.get("category", "workflow"),
                datetime.now().isoformat(),
                str(holocron_file)
            ))
            conn.commit()
            conn.close()

            return holocron_id

        except Exception as e:
            self.logger.error(f"Error in store_to_holocron: {e}", exc_info=True)
            raise
    def store_to_database(self, workflow_data: Dict, importance_score: int):
        try:
            """Store workflow to database"""
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO workflow_history 
                (timestamp, workflow_type, action, result, importance_score, 
                 stored_to_holocron, stored_to_db, content_generated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                workflow_data.get("workflow_type", "unknown"),
                workflow_data.get("action", "processed"),
                json.dumps(workflow_data.get("result", {})),
                importance_score,
                False,  # Will be set after holocron storage
                True,
                False  # Will be set after content generation
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            self.logger.error(f"Error in store_to_database: {e}", exc_info=True)
            raise
    def generate_youtube_content(self, data: Dict, importance_score: int) -> Optional[str]:
        """Generate YouTube content if importance is high enough"""
        threshold = self.config.get("youtube_content", {}).get("importance_threshold", 4) * 20

        if importance_score < threshold:
            return None

        content = {
            "title": f"{data.get('title', 'Workflow')} - {self.get_importance_symbol(importance_score)}",
            "description": f"Automated workflow processing: {data.get('workflow_type', 'unknown')}",
            "importance_score": importance_score,
            "importance_symbol": self.get_importance_symbol(importance_score),
            "timestamp": datetime.now().isoformat(),
            "content": data
        }

        content_file = Path(__file__).parent.parent.parent / "data" / "youtube_content" / f"content_{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        content_file.parent.mkdir(parents=True, exist_ok=True)

        with open(content_file, 'w') as f:
            json.dump(content, f, indent=2)

        return str(content_file)

    def process_workflow(self, workflow_data: Dict) -> Dict:
        """
        Process workflow automatically - no explanations

        Args:
            workflow_data: Workflow data dictionary

        Returns:
            Processing result
        """
        # Calculate importance
        importance_score = self.calculate_importance_score(workflow_data)
        importance_symbol = self.get_importance_symbol(importance_score)

        # Store to database
        if self.config.get("database", {}).get("auto_store", True):
            self.store_to_database(workflow_data, importance_score)

        # Store to holocron
        holocron_id = None
        if self.config.get("holocrons", {}).get("auto_store", True):
            holocron_id = self.store_to_holocron(workflow_data, importance_score)

        # Generate YouTube content
        youtube_content = None
        if self.config.get("youtube_content", {}).get("auto_generate", True):
            youtube_content = self.generate_youtube_content(workflow_data, importance_score)

        # Send to PEAK if employee/data related
        peak_result = None
        if workflow_data.get("workflow_type") in ["peak_integration", "employee_analytics", "data_integration"]:
            try:
                from peak_employee_data_integration import PeakEmployeeDataIntegration
                peak_integration = PeakEmployeeDataIntegration()
                if "employee" in workflow_data.get("data_sources", []):
                    peak_result = peak_integration.send_employee_data_to_peak()
                else:
                    peak_result = peak_integration.send_data_to_peak(workflow_data, workflow_data.get("workflow_type", "general"))
            except Exception:
                pass  # Silent fail

        # Update database flags
        if holocron_id or youtube_content:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE workflow_history 
                SET stored_to_holocron = ?, content_generated = ?
                WHERE id = (SELECT MAX(id) FROM workflow_history)
            ''', (holocron_id is not None, youtube_content is not None))
            conn.commit()
            conn.close()

        return {
            "processed": True,
            "importance_score": importance_score,
            "importance_symbol": importance_symbol,
            "holocron_id": holocron_id,
            "youtube_content": youtube_content,
            "peak_result": peak_result,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """CLI interface - minimal output"""
    import sys

    if len(sys.argv) < 2:
        return

    workflow_data = json.loads(sys.argv[1])

    processor = AutoWorkflowProcessor()
    result = processor.process_workflow(workflow_data)

    # Minimal output - just result
    print(json.dumps(result))


if __name__ == "__main__":


    main()