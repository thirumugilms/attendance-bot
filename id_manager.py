from pathlib import Path
from config import CONFIG_DIR
from logger import safe_read_json, safe_write_json
from models import TestID
from typing import List

IDS_PATH = CONFIG_DIR / "ids.json"

def get_all_ids() -> List[TestID]:
    """Retrieve all IDs from config."""
    data = safe_read_json(IDS_PATH, default=[])
    return [TestID(id=item["id"], enabled=item["enabled"]) for item in data]

def get_enabled_ids() -> List[TestID]:
    """Retrieve only enabled IDs."""
    return [item for item in get_all_ids() if item.enabled]

def add_id(student_id: str, enabled: bool = True) -> bool:
    """Add a new ID if it doesn't exist."""
    ids = get_all_ids()
    if any(item.id == student_id for item in ids):
        return False
    data = safe_read_json(IDS_PATH, default=[])
    data.append({"id": student_id, "enabled": enabled})
    safe_write_json(data, IDS_PATH)
    return True

def edit_id(student_id: str, new_id: str, enabled: bool) -> bool:
    """Edit an existing ID."""
    data = safe_read_json(IDS_PATH, default=[])
    for item in data:
        if item["id"] == student_id:
            item["id"] = new_id
            item["enabled"] = enabled
            safe_write_json(data, IDS_PATH)
            return True
    return False

def delete_id(student_id: str) -> bool:
    """Delete an ID by its string."""
    data = safe_read_json(IDS_PATH, default=[])
    initial_len = len(data)
    data = [item for item in data if item["id"] != student_id]
    if len(data) < initial_len:
        safe_write_json(data, IDS_PATH)
        return True
    return False

def set_id_enabled(student_id: str, enabled: bool) -> bool:
    """Enable or disable an ID."""
    data = safe_read_json(IDS_PATH, default=[])
    for item in data:
        if item["id"] == student_id:
            item["enabled"] = enabled
            safe_write_json(data, IDS_PATH)
            return True
    return False
