"""Shared logging helpers for Python patch builders and local services."""

from __future__ import annotations

import logging
import os


DEFAULT_LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def configure_logging(default_level: str = "INFO") -> None:
    """Configure root logging once for local development and debugging."""

    level_name = os.getenv("PATCH_SERVICE_LOG_LEVEL", default_level).upper()
    level = getattr(logging, level_name, logging.INFO)

    if logging.getLogger().handlers:
        logging.getLogger().setLevel(level)
        return

    logging.basicConfig(
        level=level,
        format=DEFAULT_LOG_FORMAT,
    )


def get_logger(name: str) -> logging.Logger:
    """Return a module logger with the shared project namespace."""

    return logging.getLogger(f"agent_patch_builders.{name}")
