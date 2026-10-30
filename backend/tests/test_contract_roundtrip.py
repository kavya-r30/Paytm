import importlib
import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel

from arth.core.paths import BACKEND_DIR, CONTRACTS_DIR
from arth.core.schemas import discover_schemas, schema

EXAMPLES = sorted((CONTRACTS_DIR / "examples").glob("*.example.json"))
GENERATED = BACKEND_DIR / "arth" / "contracts"
HEADER = "# Generated from contracts. Do not edit; run `python dev.py gen`."


def model_for(name: str) -> type[BaseModel]:
    """The generated model for a contract: module = contract name, class = schema title."""
    model = getattr(importlib.import_module(f"arth.contracts.{name}"), schema(name)["title"])
    assert issubclass(model, BaseModel)
    return model


def round_trip(name: str, raw: dict[str, Any]) -> dict[str, Any]:
    # exclude_unset keeps explicit nulls (a dropped null would fail the exact comparison below)
    dumped: dict[str, Any] = model_for(name).model_validate(raw).model_dump(mode="json", exclude_unset=True)
    return dumped


def canonical(value: Any) -> str:
    # JSON text, not Python equality: 200000 == 200000.0 in Python, but they are different JSON.
    return json.dumps(value, sort_keys=True, ensure_ascii=False)


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_round_trips_exactly(path: Path) -> None:
    raw = json.loads(path.read_text(encoding="utf-8"))
    assert canonical(round_trip(path.name.removesuffix(".example.json"), raw)) == canonical(raw)


def test_explicit_nulls_survive_the_round_trip() -> None:
    raw = json.loads((CONTRACTS_DIR / "examples" / "envelope.example.json").read_text(encoding="utf-8"))
    raw |= {"speech": None, "nav": None, "tier": None, "led": None}
    assert round_trip("envelope", raw) == raw

    event = json.loads((CONTRACTS_DIR / "examples" / "event.example.json").read_text(encoding="utf-8"))
    event |= {"causation_id": None, "actor": {"kind": "system", "id": None}}
    assert round_trip("event", event) == event


def test_documented_imports_work() -> None:
    from arth.contracts.envelope import Envelope
    from arth.contracts.event import DomainEvent
    from arth.contracts.problem import Problem

    names = {Envelope.__name__, DomainEvent.__name__, Problem.__name__}
    assert names == {"Envelope", "DomainEvent", "Problem"}


def test_one_generated_module_per_contract() -> None:
    modules = {p.stem for p in GENERATED.glob("*.py")} - {"__init__"}
    assert modules == set(discover_schemas())


def test_generated_files_carry_do_not_edit_header() -> None:
    for path in GENERATED.glob("*.py"):
        assert path.read_text(encoding="utf-8").startswith(HEADER), path.name
