"""Consistent message payload builders."""

from __future__ import annotations

from typing import Dict


def build_message(
    *,
    message_id: str,
    role: str,
    title: str,
    body: str,
    timestamp: str,
    tone: str = "info",
) -> Dict[str, str]:
    return {
        "id": message_id,
        "role": role,
        "title": title,
        "body": body,
        "tone": tone,
        "timestamp": timestamp,
    }
