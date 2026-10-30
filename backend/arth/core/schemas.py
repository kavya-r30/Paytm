"""Contract JSON Schemas: discovery, a `referencing` registry and validators (spec Part C).

Every `*.schema.json` under contracts/ (outside examples/ and fixtures/) is a contract. Its name is
the file stem before `.schema.json` (`events/event.schema.json` -> `event`), names are unique across
the tree, every schema has a `title` (the generated class/type name) and an `$id` equal to
`https://arth.local/contracts/<path>`, so relative `$ref`s between files resolve by `$id`.
"""

from __future__ import annotations

import json
from functools import cache
from pathlib import Path
from typing import Any

from jsonschema import Draft7Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT7

from arth.core.paths import CONTRACTS_DIR

ID_BASE = "https://arth.local/contracts/"
SUFFIX = ".schema.json"
EXCLUDED_DIRS = frozenset({"examples", "fixtures"})


class ContractError(ValueError):
    """The contracts tree is malformed (duplicate names, missing title or wrong $id)."""


def schema_name(path: Path) -> str:
    return path.name.removesuffix(SUFFIX)


def discover_schemas(root: Path = CONTRACTS_DIR) -> dict[str, Path]:
    """Map each contract name to its file, sorted by name. Raises ContractError on duplicate names."""
    found: dict[str, Path] = {}
    for path in sorted(root.rglob(f"*{SUFFIX}")):
        if EXCLUDED_DIRS.intersection(path.relative_to(root).parts[:-1]):
            continue
        name = schema_name(path)
        if name in found:
            raise ContractError(
                f"duplicate contract name {name!r}: {found[name].relative_to(root).as_posix()} and "
                f"{path.relative_to(root).as_posix()} (names are file stems and must be unique)"
            )
        found[name] = path
    return dict(sorted(found.items()))


def load_schema(path: Path, root: Path = CONTRACTS_DIR) -> dict[str, Any]:
    rel = path.relative_to(root).as_posix()
    schema: dict[str, Any] = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(schema.get("title"), str) or not schema["title"]:
        raise ContractError(f"{rel}: a contract schema needs a non-empty 'title' (the generated type name)")
    if schema.get("$id") != ID_BASE + rel:
        raise ContractError(f"{rel}: '$id' must be {ID_BASE + rel!r}, got {schema.get('$id')!r}")
    return schema


def load_schemas(root: Path = CONTRACTS_DIR) -> dict[str, dict[str, Any]]:
    return {name: load_schema(path, root) for name, path in discover_schemas(root).items()}


@cache
def _contracts() -> tuple[dict[str, dict[str, Any]], Registry[Any]]:
    schemas = load_schemas()
    registry: Registry[Any] = Registry().with_resources(
        (schema["$id"], Resource.from_contents(schema, default_specification=DRAFT7))
        for schema in schemas.values()
    )
    return schemas, registry


def schema(name: str) -> dict[str, Any]:
    schemas, _ = _contracts()
    if name not in schemas:
        raise KeyError(f"no contract named {name!r}; known: {', '.join(schemas)}")
    return schemas[name]


@cache
def validator(name: str) -> Draft7Validator:
    """A draft-07 validator for one contract, with cross-file refs and format checking."""
    _, registry = _contracts()
    return Draft7Validator(schema(name), registry=registry, format_checker=Draft7Validator.FORMAT_CHECKER)
