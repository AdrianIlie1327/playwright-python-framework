"""Access to static test data stored under ``test_data/``."""

from __future__ import annotations

import json
from functools import lru_cache
from typing import Any

from framework.config import PROJECT_ROOT

TEST_DATA_DIR = PROJECT_ROOT / "test_data"


@lru_cache
def load_json(name: str) -> dict[str, Any]:
    return json.loads((TEST_DATA_DIR / name).read_text(encoding="utf-8"))
