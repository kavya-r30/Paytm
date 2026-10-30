import copy
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from jsonschema import Draft7Validator

from arth.core.paths import CONTRACTS_DIR
from arth.core.schemas import ContractError, discover_schemas, load_schemas, schema, validator

EXAMPLES = sorted((CONTRACTS_DIR / "examples").glob("*.example.json"))
SCHEMAS = discover_schemas()


def load(rel: str) -> dict[str, Any]:
    return json.loads((CONTRACTS_DIR / rel).read_text(encoding="utf-8"))


def example(name: str) -> dict[str, Any]:
    return load(f"examples/{name}.example.json")


def errors(name: str, instance: object) -> list[str]:
    return [e.message for e in validator(name).iter_errors(instance)]


def test_discovery_finds_every_contract() -> None:
    assert set(SCHEMAS) == {
        "approval",
        "approval_decided",
        "approval_requested",
        "audit_verification",
        "audit_verified",
        "batch_recalled",
        "catalog_add_item",
        "catalog_bulk_price",
        "catalog_change_price",
        "catalog_import_items",
        "catalog_item_added",
        "catalog_item_view",
        "catalog_price_changed",
        "catalog_search_view",
        "command",
        "command_executed",
        "command_result",
        "common",
        "consent_grant",
        "consent_stop",
        "consent_withdraw",
        "credit_changed",
        "credit_payable_changed",
        "credit_receipt_requested",
        "credit_reminder_requested",
        "credit_statement_requested",
        "customer_search_view",
        "envelope",
        "event",
        "expiry_view",
        "i18n_changed",
        "khata_account_view",
        "khata_view",
        "ledger_acknowledge_entry",
        "ledger_add_entry",
        "ledger_add_payable",
        "ledger_apply_advance",
        "ledger_apply_verified_payment",
        "ledger_dispute_entry",
        "ledger_open_account",
        "ledger_pay_payable",
        "ledger_record_deposit",
        "ledger_record_payment",
        "ledger_record_promise",
        "ledger_resolve_dispute",
        "ledger_reverse_entry",
        "ledger_send_reminder",
        "ledger_send_statement",
        "ledger_set_limit",
        "ledger_statement_view",
        "merchant_bootstrap",
        "merchant_update_settings",
        "onboarding_complete_step",
        "onboarding_started",
        "onboarding_updated",
        "onboarding_view",
        "patron_changed",
        "patron_consent_changed",
        "patron_merged",
        "patron_reward_changed",
        "patron_view",
        "patrons_add",
        "patrons_add_command",
        "patrons_add_household_member",
        "patrons_merge",
        "patrons_propose_merge",
        "patrons_update_command",
        "patrons_update_profile",
        "payables_view",
        "problem",
        "promises_view",
        "resolution_view",
        "rewards_configure",
        "rewards_record_visit",
        "rewards_redeem",
        "session_result",
        "settings_view",
        "shift_close",
        "shift_open",
        "shift_view",
        "staff_add",
        "staff_add_command",
        "staff_added",
        "staff_logged_in",
        "staff_login",
        "staff_login_command",
        "staff_logout",
        "staff_shift_closed",
        "staff_shift_opened",
        "staff_view",
        "stock_adjust",
        "stock_changed",
        "stock_count",
        "stock_demand_logged",
        "stock_log_unmet_demand",
        "stock_override_recorded",
        "stock_recall_batch",
        "stock_receive",
        "stock_view",
        "view_invalidate",
    }
    assert SCHEMAS["event"] == CONTRACTS_DIR / "events" / "event.schema.json"


@pytest.mark.parametrize("name", sorted(SCHEMAS))
def test_schema_is_valid_draft7_with_title_and_id(name: str) -> None:
    Draft7Validator.check_schema(schema(name))  # load_schemas() already enforced title and $id


def test_every_example_has_a_schema() -> None:
    assert EXAMPLES, "contracts/examples/ is empty"
    for path in EXAMPLES:
        assert path.name.removesuffix(".example.json") in SCHEMAS, f"{path.name} has no matching schema"


@pytest.mark.parametrize("path", EXAMPLES, ids=lambda p: p.name)
def test_example_validates_against_its_schema(path: Path) -> None:
    name = path.name.removesuffix(".example.json")
    validator(name).validate(json.loads(path.read_text(encoding="utf-8")))


def test_format_checker_is_active() -> None:
    bad = example("envelope")
    bad["undo"]["until"] = "yesterday"
    assert errors("envelope", bad), "date-time format must be enforced"
    bad_problem = example("problem")
    bad_problem["type"] = "not a uri"
    assert errors("problem", bad_problem), "uri-reference format must be enforced"


def _set(path: str, value: object) -> Callable[[dict[str, Any]], None]:
    def mutate(doc: dict[str, Any]) -> None:
        *parents, last = path.split(".")
        target: Any = doc
        for key in parents:
            target = target[int(key)] if isinstance(target, list) else target[key]
        if isinstance(target, list):
            target[int(last)] = value
        else:
            target[last] = value

    return mutate


NEGATIVE: list[tuple[str, str, Callable[[dict[str, Any]], None]]] = [
    ("envelope", "bad ULID turn_id", _set("turn_id", "turn_01JBQ0Z7Y8K3M4N5P6Q7R8S9TI")),
    ("envelope", "four followups", _set("followups", [{"label_key": "chip.a_b", "turn_text": "x"}] * 4)),
    ("envelope", "unknown presence state", _set("presence.state", "dancing")),
    ("envelope", "unknown card type", _set("cards", [{"type": "banner"}])),
    ("envelope", "extra top-level property", _set("mood", "happy")),
    ("envelope", "hi-Latn as speech locale", _set("lang.speech", "hi-Latn")),
    ("envelope", "unknown audience", _set("audience", "everyone")),
    ("envelope", "empty speech text", _set("speech.text", "")),
    ("envelope", "unprefixed card id", _set("cards.0.id", "01JBQ0Z7Y8K3M4N5P6Q7R8S9T1")),
    ("envelope", "unprefixed undo command_id", _set("undo.command_id", "cmd-1")),
    ("envelope", "label_key without a dot", _set("followups.0.label_key", "chip")),
    ("problem", "status 200", _set("status", 200)),
    ("problem", "empty title", _set("title", "")),
    ("problem", "empty message_key", _set("message_key", "")),
    ("event", "event type without a dot", _set("type", "ticked")),
    ("event", "empty merchant_id", _set("merchant_id", "")),
]


@pytest.mark.parametrize(("name", "case", "mutate"), NEGATIVE, ids=[c for _, c, _ in NEGATIVE])
def test_contract_rejects(name: str, case: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    bad = copy.deepcopy(example(name))
    mutate(bad)
    assert errors(name, bad), f"{name} should reject: {case}"


@pytest.mark.parametrize("key", schema("envelope")["required"])
def test_envelope_rejects_missing_required_key(key: str) -> None:
    bad = example("envelope")
    del bad[key]
    assert errors("envelope", bad), f"envelope without {key!r} must be rejected"


def test_card_type_list_matches_spec_c4() -> None:
    card_types = schema("envelope")["definitions"]["Card"]["properties"]["type"]["enum"]
    assert set(card_types) == {
        "bill",
        "hint",
        "approval",
        "batch",
        "verdict",
        "chart",
        "forecast",
        "brief",
        "offer",
        "plan",
        "campaign",
        "patron",
        "stock",
        "po",
        "quote_compare",
        "claim",
        "memory",
        "draft",
        "capital",
        "nudge",
        "pipeline",
        "receipt",
        "health",
    }


def test_shared_definitions_live_only_in_common() -> None:
    shared = set(schema("common")["definitions"])
    for name, doc in load_schemas().items():
        if name != "common":
            assert not shared & set(doc.get("definitions", {})), f"{name} duplicates a common definition"


def test_nullable_fields_use_any_of() -> None:
    assert '"oneOf"' not in json.dumps(load_schemas()), "use anyOf [ref, {type: null}] for nullable fields"


def test_no_union_type_arrays() -> None:
    """Ajv strict mode rejects `type: [a, b]`; spell unions and nullables with anyOf."""
    text = json.dumps(load_schemas())
    assert '"type": [' not in text


def test_event_requires_causation_fields() -> None:
    assert set(schema("event")["required"]) == {
        "event_id",
        "type",
        "merchant_id",
        "occurred_at",
        "actor",
        "causation_id",
        "payload",
    }


def test_event_missing_causation_id_is_rejected() -> None:
    event = example("event")
    del event["causation_id"]
    assert errors("event", event), "causation_id is required (null for root events)"


def test_root_event_with_null_causation_id_validates() -> None:
    event = example("event")
    event["causation_id"] = None
    event["actor"] = {"kind": "system", "id": None}
    validator("event").validate(event)


def _write(root: Path, rel: str, title: str | None = "T") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    doc: dict[str, Any] = {"$id": f"https://arth.local/contracts/{rel}"}
    if title:
        doc["title"] = title
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_discovery_skips_examples_and_fixtures(tmp_path: Path) -> None:
    _write(tmp_path, "a.schema.json")
    _write(tmp_path, "events/b.schema.json")
    _write(tmp_path, "examples/c.schema.json")
    _write(tmp_path, "fixtures/d.schema.json")
    assert list(discover_schemas(tmp_path)) == ["a", "b"]


def test_discovery_rejects_duplicate_names(tmp_path: Path) -> None:
    _write(tmp_path, "thing.schema.json")
    _write(tmp_path, "events/thing.schema.json")
    with pytest.raises(ContractError, match="duplicate contract name 'thing'"):
        discover_schemas(tmp_path)


def test_loading_requires_title_and_matching_id(tmp_path: Path) -> None:
    _write(tmp_path, "untitled.schema.json", title=None)
    with pytest.raises(ContractError, match="title"):
        load_schemas(tmp_path)
    (tmp_path / "untitled.schema.json").unlink()
    (tmp_path / "moved.schema.json").write_text(
        json.dumps({"title": "M", "$id": "https://arth.local/contracts/other.schema.json"}), encoding="utf-8"
    )
    with pytest.raises(ContractError, match=r"\$id"):
        load_schemas(tmp_path)
