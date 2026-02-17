#!/usr/bin/env python3
"""
Defense Architecture - Transaction Logging
Comprehensive transaction logging for all system operations

All critical operations MUST be logged for audit and security.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from enum import Enum
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DefenseTransactionLog")


class TransactionType(Enum):
    """Transaction types"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"
    AUTHENTICATE = "authenticate"
    AUTHORIZE = "authorize"
    KILLSWITCH = "killswitch"
    AIRGAP = "airgap"
    PRIVILEGE = "privilege"
    SECRET_ACCESS = "secret_access"
    SYSTEM_CHANGE = "system_change"


@dataclass
class TransactionLog:
    """Transaction log entry"""
    transaction_id: str
    timestamp: datetime
    system_name: str
    transaction_type: TransactionType
    resource: str
    action: str
    user: Optional[str] = None
    result: str = "success"
    details: Dict[str, Any] = field(default_factory=dict)
    ip_address: Optional[str] = None
    session_id: Optional[str] = None


class TransactionLogger:
    """Comprehensive transaction logger"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.log_dir = self.project_root / "data" / "defense" / "transaction_logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / f"transactions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        self.logger = get_logger("TransactionLogger")

    def log_transaction(
        self,
        system_name: str,
        transaction_type: TransactionType,
        resource: str,
        action: str,
        user: Optional[str] = None,
        result: str = "success",
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> str:
        """Log a transaction"""
        import uuid

        transaction_id = str(uuid.uuid4())
        log_entry = TransactionLog(
            transaction_id=transaction_id,
            timestamp=datetime.now(),
            system_name=system_name,
            transaction_type=transaction_type,
            resource=resource,
            action=action,
            user=user,
            result=result,
            details=details or {},
            ip_address=ip_address,
            session_id=session_id
        )

        # Write to JSONL file
        log_data = {
            "transaction_id": log_entry.transaction_id,
            "timestamp": log_entry.timestamp.isoformat(),
            "system_name": log_entry.system_name,
            "transaction_type": log_entry.transaction_type.value,
            "resource": log_entry.resource,
            "action": log_entry.action,
            "user": log_entry.user,
            "result": log_entry.result,
            "details": log_entry.details,
            "ip_address": log_entry.ip_address,
            "session_id": log_entry.session_id
        }

        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_data) + '\n')

        # Also log to standard logger
        self.logger.info(
            f"Transaction: {transaction_type.value} - {system_name} - {action} {resource} - {result}"
        )

        return transaction_id

    def query_transactions(
        self,
        system_name: Optional[str] = None,
        transaction_type: Optional[TransactionType] = None,
        resource: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query transaction logs"""
        results = []

        # Read all log files in date range
        if start_time:
            start_date = start_time.strftime('%Y%m%d')
        else:
            start_date = None

        if end_time:
            end_date = end_time.strftime('%Y%m%d')
        else:
            end_date = datetime.now().strftime('%Y%m%d')

        # For simplicity, read current day's log
        log_file = self.log_dir / f"transactions_{datetime.now().strftime('%Y%m%d')}.jsonl"

        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line)

                        # Apply filters
                        if system_name and entry.get("system_name") != system_name:
                            continue
                        if transaction_type and entry.get("transaction_type") != transaction_type.value:
                            continue
                        if resource and entry.get("resource") != resource:
                            continue
                        if start_time and datetime.fromisoformat(entry["timestamp"]) < start_time:
                            continue
                        if end_time and datetime.fromisoformat(entry["timestamp"]) > end_time:
                            continue

                        results.append(entry)
                        if len(results) >= limit:
                            break
                    except Exception as e:
                        self.logger.warning(f"Error parsing log entry: {e}")

        return results


def get_transaction_logger(project_root: Optional[Path] = None) -> TransactionLogger:
    try:
        """Get global transaction logger"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        return TransactionLogger(project_root)


    except Exception as e:
        logger.error(f"Error in get_transaction_logger: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    from dataclasses import dataclass, field

    # Test transaction logging
    project_root = Path(__file__).parent.parent.parent
    tx_logger = get_transaction_logger(project_root)

    print("=" * 60)
    print("Defense Architecture - Transaction Logging")
    print("=" * 60)

    # Log some test transactions
    tx_logger.log_transaction(
        system_name="test-system",
        transaction_type=TransactionType.READ,
        resource="test-resource",
        action="read",
        result="success"
    )

    print("\nTransaction logged successfully")
    print("=" * 60)
