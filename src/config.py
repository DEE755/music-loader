from __future__ import annotations

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Mapping

from pydantic import BaseModel, ValidationError, field_validator

from src.env_loader import load_env_file


class ConfigError(RuntimeError):
    """Raised when required environment configuration is missing or invalid."""


MAX_PIECES=20
SCRAPPING_DELAY=1.0

DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVEL_ENV_VARS: tuple[str, ...] = ( "LOG_LEVEL")
LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
# Resolve project root once so every module looks for the same .env file.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ENV_PATH = PROJECT_ROOT / ".env"


def _normalize_log_level(value: str) -> str:
    """Normalize and validate a log level name."""
    normalized = value.upper()
    if normalized == "WARN":
        normalized = "WARNING"

    mapping = logging.getLevelNamesMapping()
    if normalized not in mapping:
        allowed = ", ".join(sorted(name for name in mapping if name.isalpha()))
        raise ValueError(f"Log level must be one of: {allowed}.")
    return normalized


def resolve_log_level(env: Mapping[str, str] | None = None) -> str:
    """Resolve the desired log level from the environment or fall back to default."""
    source = env or os.environ
    for var in LOG_LEVEL_ENV_VARS:
        value = source.get(var)
        if value:
            return value
    return DEFAULT_LOG_LEVEL


def configure_logging(
    level_name: str | int | None = None, *, log_format: str = LOG_FORMAT
) -> int:
    """Apply a consistent logging format/level across the service."""
    if isinstance(level_name, int):
        level = level_name
    else:
        normalized = _normalize_log_level(level_name or resolve_log_level())
        level = logging.getLevelNamesMapping()[normalized]

    logging.basicConfig(level=level, format=log_format, force=True)
    logging.captureWarnings(True)
    return level


class Settings(BaseModel):
    log_level: str = DEFAULT_LOG_LEVEL
    database_url: str | None = None

    model_config = {"extra": "forbid"}

        
       
    @field_validator("log_level")
    @classmethod
    def _normalize_level(cls, value: str) -> str:
        return _normalize_log_level(value)

    @classmethod
    def from_environment(cls, env_path: Path | None = None) -> "Settings":
        env_file = env_path or DEFAULT_ENV_PATH
        load_env_file(env_file)
        try:
            return cls.model_validate(
                {
                    "log_level": resolve_log_level()
                }
            )
        except ValidationError as exc:  # noqa: TRY003 - we rephrase to avoid leaking values
            # Collect error messages without including raw values
            messages = "; ".join(err["msg"] for err in exc.errors())
            raise ConfigError(messages) from exc


def validate_runtime_env(env_path: Path | None = None) -> Settings:
    """Validate required environment variables and return parsed settings."""
    return Settings.from_environment(env_path)


def get_settings(env_path: Path | None = None) -> Settings:
    """Retrieve validated settings, loading .env from the project root by default."""
    return Settings.from_environment(env_path)
