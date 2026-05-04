"""Load compiled app configuration artifacts for the Python patch service."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


@lru_cache(maxsize=4)
def load_generated_app_config(
    app_id: str = "warning_review_workbench",
) -> Optional[Dict[str, Any]]:
    path = _repo_root() / "generated" / app_id / "app.normalized.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
