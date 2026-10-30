"""Static checks on contracts/openapi.yaml (served-vs-documented routes is a separate API test)."""

import json
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from arth.core.paths import CONTRACTS_DIR

OPENAPI_PATH = CONTRACTS_DIR / "openapi.yaml"
HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def _load(path: Path) -> Any:
    text = path.read_text(encoding="utf-8")
    return yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)


def _refs(node: Any) -> Iterator[str]:
    if isinstance(node, dict):
        ref = node.get("$ref")
        if isinstance(ref, str):
            yield ref
        for value in node.values():
            yield from _refs(value)
    elif isinstance(node, list):
        for value in node:
            yield from _refs(value)


def _pointer(doc: Any, fragment: str) -> Any:
    target = doc
    for part in [p for p in fragment.lstrip("/").split("/") if p]:
        target = target[part.replace("~1", "/").replace("~0", "~")]
    return target


def test_openapi_parses_as_3_1() -> None:
    spec = _load(OPENAPI_PATH)
    assert spec["openapi"].startswith("3.1")
    assert spec["paths"], "no paths documented"


def test_operation_ids_are_unique() -> None:
    spec = _load(OPENAPI_PATH)
    ids = [op["operationId"] for ops in spec["paths"].values() for m, op in ops.items() if m in HTTP_METHODS]
    assert all(ids), "every operation needs an operationId"
    assert [i for i, n in Counter(ids).items() if n > 1] == []


def test_every_ref_resolves_across_files() -> None:
    """Follow every $ref from openapi.yaml into sibling schema files, transitively."""
    pending, seen, broken = [OPENAPI_PATH.resolve()], set(), []
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        doc = _load(path)
        for ref in _refs(doc):
            file_part, _, fragment = ref.partition("#")
            target_path = (path.parent / file_part).resolve() if file_part else path
            try:
                _pointer(doc if not file_part else _load(target_path), fragment)
            except (OSError, KeyError, IndexError, TypeError) as exc:
                broken.append(f"{path.name}: {ref} ({type(exc).__name__})")
                continue
            if file_part:
                pending.append(target_path)
    assert not broken, broken


def test_problem_responses_use_the_shared_problem_schema() -> None:
    spec = _load(OPENAPI_PATH)
    assert spec["components"]["schemas"]["Problem"] == {"$ref": "./problem.schema.json"}
    unauthorized = spec["paths"]["/v1/director/ping"]["get"]["responses"]["401"]
    assert unauthorized == {"$ref": "#/components/responses/Problem"}
    assert spec["paths"]["/healthz"]["get"]["security"] == []
