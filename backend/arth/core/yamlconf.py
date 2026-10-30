"""Shared YAML-config pieces: error type, strict base model, one load-and-validate helper."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, ValidationError


class ConfigError(ValueError):
    """A config file or secret is missing or invalid."""


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


def load_yaml(path: Path) -> object:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ConfigError(f"{path.name}: file not found at {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigError(f"{path.name}: invalid YAML: {exc}") from exc


def validate[M: BaseModel](model: type[M], path: Path) -> M:
    """Load `path` and validate it as `model`; every failure is a ConfigError naming the file."""
    try:
        return model.model_validate(load_yaml(path))
    except ValidationError as exc:
        raise ConfigError(f"{path.name}: {exc}") from exc
