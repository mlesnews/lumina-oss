"""
Ask Retries Fix Plugin

Fixes @ASKS retry and timeout handling.
Consolidates: fix_asks_retries.py
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

script_dir = Path(__file__).parent.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from fixes.fixer import FixPlugin, FixType, FixResult
except ImportError:
    from ..fixer import FixPlugin, FixType, FixResult

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AskRetriesFixPlugin")


class AskRetriesFixPlugin(FixPlugin):
    """Fix @ASKS retry and timeout handling"""

    def __init__(self):
        super().__init__(
            fix_type=FixType.ASK_RETRIES,
            name="Ask Retries Fixer",
            description="Fixes @ASKS stalling and retry/timeout handling issues"
        )

    def can_fix(self, issue: str) -> bool:
        """Check if this plugin can fix the issue"""
        issue_lower = issue.lower()
        return any(keyword in issue_lower for keyword in [
            'ask', 'retry', 'timeout', 'stalling', 'circuit breaker'
        ])

    def detect(self, **kwargs) -> List[str]:
        """Detect ask retry issues"""
        issues = []

        # Check ask database for incomplete asks
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)
        ask_db = project_root / "data" / "ask_database.db"

        if ask_db.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(str(ask_db))
                cursor = conn.cursor()

                # Check for asks that have been retrying too long
                cursor.execute("""
                    SELECT COUNT(*) FROM asks 
                    WHERE status = 'in_progress' 
                    AND created_at < datetime('now', '-1 hour')
                """)
                stale_asks = cursor.fetchone()[0]

                if stale_asks > 0:
                    issues.append(f"{stale_asks} stale ask(s) detected (in progress > 1 hour)")

                conn.close()
            except Exception as e:
                logger.debug(f"Error checking ask database: {e}")

        return issues

    def fix(self, **kwargs) -> FixResult:
        """Fix ask retry issues"""
        project_root = kwargs.get('project_root', Path(__file__).parent.parent.parent.parent)

        try:
            # Import and use the existing fix function
            try:
                from fix_asks_retries import fix_asks_retries
                result = fix_asks_retries(project_root)

                return FixResult(
                    fix_type=self.fix_type,
                    success=result.get('success', False),
                    message=result.get('message', 'Ask retries fixed'),
                    details=result
                )
            except ImportError:
                # Fallback: implement basic retry fix logic
                logger.warning("fix_asks_retries module not available, using fallback")

                # Basic fix: update stale asks
                ask_db = project_root / "data" / "ask_database.db"
                if ask_db.exists():
                    import sqlite3
                    conn = sqlite3.connect(str(ask_db))
                    cursor = conn.cursor()

                    cursor.execute("""
                        UPDATE asks 
                        SET status = 'failed', 
                            error = 'Timeout: Stale ask detected and marked as failed'
                        WHERE status = 'in_progress' 
                        AND created_at < datetime('now', '-1 hour')
                    """)

                    updated = cursor.rowcount
                    conn.commit()
                    conn.close()

                    return FixResult(
                        fix_type=self.fix_type,
                        success=True,
                        message=f"Marked {updated} stale ask(s) as failed",
                        details={"updated": updated}
                    )
                else:
                    return FixResult(
                        fix_type=self.fix_type,
                        success=False,
                        message="Ask database not found",
                        details={"error": "Database not found"}
                    )

        except Exception as e:
            return FixResult(
                fix_type=self.fix_type,
                success=False,
                message=f"Failed to fix ask retries: {e}",
                details={"error": str(e)}
            )
