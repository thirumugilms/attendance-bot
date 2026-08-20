import pytest
from pathlib import Path

# Create a temporary config dir for tests before importing id_manager
import os
import shutil

TEST_CONFIG_DIR = Path("tests/temp_config")

@pytest.fixture(autouse=True)
def setup_teardown():
    # Setup
    TEST_CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    import id_manager
    id_manager.IDS_PATH = TEST_CONFIG_DIR / "ids.json"
    
    yield
    
    # Teardown
    shutil.rmtree(TEST_CONFIG_DIR)

def test_add_and_get_ids():
    from id_manager import add_id, get_all_ids, get_enabled_ids
    
    add_id("TEST001", enabled=True)
    add_id("TEST002", enabled=False)
    
    ids = get_all_ids()
    assert len(ids) == 2
    assert ids[0].id == "TEST001"
    
    enabled = get_enabled_ids()
    assert len(enabled) == 1
    assert enabled[0].id == "TEST001"

def test_delete_id():
    from id_manager import add_id, delete_id, get_all_ids
    add_id("DELETE_ME")
    assert len(get_all_ids()) == 1
    delete_id("DELETE_ME")
    assert len(get_all_ids()) == 0
