"""Shared helpers for loading environment files."""

from __future__ import annotations

import importlib.util
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def load_env_file(env_path: Path) -> None:
    """Load a .env file if present without overriding existing env vars."""
    if not env_path.exists():
        logger.debug(
            "No .env file found at %s; relying on environment variables (e.g., Docker --env-file).",
            env_path,
        )
        return

    if importlib.util.find_spec("dotenv") is not None:
        from dotenv import load_dotenv

        load_dotenv(env_path, override=False)
        return

    for raw_line in env_path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, raw_value = line.split("=", 1)
        key = key.strip()
        value = raw_value.split("#", 1)[0].strip()
        if value.startswith(("'", '"')) and value.endswith(("'", '"')):
            value = value[1:-1]
        os.environ.setdefault(key, value)
