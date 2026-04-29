"""Risk summary builders for common warning-review flows."""

from __future__ import annotations

from typing import Dict, List


def build_risk_summary(level: str, summary: str, details: List[str]) -> Dict[str, object]:
    return {
        "level": level,
        "summary": summary,
        "details": details,
    }
