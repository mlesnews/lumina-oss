#!/usr/bin/env python3
"""PERSONAPLEX Tab Processor - VSCode Tab Management"""
import json, logging
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TabState(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MODIFIED = "modified"

class TabType:
    FILE = "file"
    MARKDOWN_PREVIEW = "markdown_preview"

@dataclass
class TabInfo:
    tab_id: str
    label: str
    file_path: Optional[str] = None
    tab_type: str = TabType.FILE
    state: TabState = TabState.INACTIVE
    is_dirty: bool = False
    language_id: Optional[str] = None
    group_id: Optional[str] = None

class VSCodeTabProcessor:
    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.tabs = {}
        self.active_tab_id = None
        logger.info(f"VSCodeTabProcessor initialized")

    def add_tab(self, tab_id: str, label: str, file_path: Optional[str] = None, language_id: Optional[str] = None) -> TabInfo:
        self.tabs[tab_id] = TabInfo(tab_id=tab_id, label=label, file_path=file_path, language_id=language_id)
        logger.info(f"Tab added: {tab_id}")
        return self.tabs[tab_id]

    def set_active_tab(self, tab_id: str) -> bool:
        if tab_id in self.tabs:
            self.active_tab_id = tab_id
            self.tabs[tab_id].state = TabState.ACTIVE
            return True
        return False

    def get_active_tab(self) -> Optional[TabInfo]:
        if self.active_tab_id:
            return self.tabs.get(self.active_tab_id)
        return None

    def get_statistics(self) -> dict:
        return {"total_tabs": len(self.tabs), "active_tab_id": self.active_tab_id}

def create_tab_processor(workspace_root: Optional[str] = None) -> VSCodeTabProcessor:
    return VSCodeTabProcessor(workspace_root=workspace_root)

if __name__ == "__main__":
    p = create_tab_processor()
    p.add_tab("tab-1", "test.py", "test.py", "python")
    p.set_active_tab("tab-1")
    print(f"Active: {p.get_active_tab().label}")
    print("PERSONAPLEX Tab Processor initialized!")
