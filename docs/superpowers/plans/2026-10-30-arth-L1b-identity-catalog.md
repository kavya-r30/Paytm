# Arth L1b Identity and Catalog Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans and superpowers:test-driven-development inline. No git or subagents. Each task ends in a Checkpoint; review spec compliance before quality. Checkbox steps record progress.

**Goal:** Implement T1.7–T1.10 on the L1a governance foundation: independent merchant languages and onboarding, PIN-bound staff sessions/shifts, pack-aware catalog storage, and deterministic resolution.

**Architecture:** All domain mutations run through the Command Bus and scoped Repository. Trusted provisioning creates the first merchant/owner/device; HTTP PIN login creates a persistent signed session, with PIN material passed only in an ephemeral execution context. Catalog payload contracts validate common and pack-schema details; SQLite trigram FTS remains merchant scoped; deterministic resolution exposes ambiguity rather than choosing a tied item.

**Tech Stack:** Existing Python/FastAPI/SQLAlchemy/Alembic/Pydantic/JSON Schema; standard-library scrypt, HMAC, Unicode and difflib. Existing frontend generators/Ajv. No additional dependencies; embeddings are an injected L3 hook.

**Spec:** v6 C1–C6, D1, E2 ONB-1/2/5, STF-1/2/3, I18N-2, TAX-1; E3 CAFE-1/2, PHAR-1, SAL-1 (catalog fields only); F2.2; J7/J9; K2 T1.7–T1.10. v5.1 CAT-1…4, D2/D3, AIQ-1. Appointments, billing, stock consumption, suppliers, OCR and all-screen views belong to their later tasks.

## Global Constraints

- No git commands, no subagents, never inspect backend/.env. Use Settings for runtime secrets.
- Use `python dev.py` and `python -m uv`; generated files are changed only by `python dev.py gen`.
- Merchant identity derives from trusted sessions; actors and current role are verified server-side. SimClock is the sole business time source.
- Money is integer paise, quantities milli-units; JSON text has json_valid checks; new schema requires frozen migration 0003 and drift verification.
- PINs and bearer tokens must not enter command payloads/results, audit or outbox. All domain writes use the bus; auth proof material exists only during R1 execution.
- Preserve CRLF in plan documents and sync fenced source snapshots after review fixes.

## Review Focus

- Restart, logout, role changes and expired sessions must not preserve authorization (Task 2).
- Helpers cannot change settings, create owners or change another staff member's shift (Tasks 1/2).
- Aliases/barcodes/FTS cannot disclose another tenant's items, and collisions fail atomically (Tasks 3/4).
- Bulk price changes require Console step-up; single price changes require R2 confirmation (Task 3).
- Near ties and unknown input return candidates/clarification, never an invented item (Task 4).

## File structure

```text
backend/arth/domains/tables.py               devices, progress, credentials, sessions, shifts, catalog tables
backend/arth/domains/merchants.py            settings/onboarding and trusted initial provisioning
backend/arth/domains/staff.py                PIN verification, session signing, staff and shift commands
backend/arth/domains/catalog.py              catalog commands, import, pack validation and pricing
backend/arth/domains/resolution.py           normalization, transliteration, fuzzy pipeline, embedding hook
backend/arth/api/commerce.py                 domain/session routes and relevant views
backend/migrations/versions/0003_identity_catalog.py
backend/tests/test_l1b_*.py                  task and API acceptance tests
contracts/commands/*.schema.json            per-command payloads (unique stems)
contracts/*view*.schema.json                read contracts
contracts/fixtures/catalog_resolution.json  150 hand-authored utterance expectations
backend/packs/kirana/catalog_starter.csv    synthetic starter records
```

## Batch B1: four related tasks

### Task 1: Merchant settings and onboarding (T1.7)

**Files:** domains/tables.py, merchants.py, migration 0003; tests/test_l1b_merchants.py; merchant/onboarding payload and view schemas/examples; policies.yaml tiers; main registration and language-envelope integration.

**Interfaces:** `register_merchants(bus, packs)` registers `merchant.update_settings` and `onboarding.complete_step`; `provision_shop(bus, name, pack, owner_name, pin, device_id)` is trusted startup provisioning, generates merchant/actor IDs internally, and submits `merchant.bootstrap`. `settings_view(repo)` and `onboarding_view(repo)` return typed read models. Three independent keys: screen_lang, speech_lang, customer_lang; tax profile and shop/quiet hours persist independently. Repository gains trusted execution metadata; payloads never supply it.

- [x] Add strict draft-07 schemas and realistic examples; regenerate with `python dev.py gen`.
- [x] Write tests for independent languages, foreign tenant rejection, helper denial, ordered onboarding, no implicit marketing consent, and bootstrap replay. Run targeted pytest and capture RED.
- [x] Implement minimal tables/migration and merchant handlers; private bootstrap PIN material never enters persisted command data. Apply settings language to command/approval envelopes.
- [x] Run targeted tests and migration drift; expected PASS. Review ONB-1/5, I18N-2, TAX-1, C1; then defaults, validation and transaction boundaries.
- [x] Checkpoint: record task tests and fixes in execution ledger below.

### Task 2: Staff sessions and shifts (T1.8)

**Files:** staff.py, api/commerce.py, auth session dependency, tests/test_l1b_staff.py, login/staff/shift contracts; tables/migration additions; main registration.

**Interfaces:** `StaffService.login(merchant_id, staff_id, pin, device_id, channel, key)` verifies PIN against a tenant-scoped credential; public route binds merchant through a registered device ID, never a body merchant_id. Mint signed bearer outside bus persistence; `resolve(token)` verifies signature, database expiry/revocation, current role and device. Session IDs persist; raw tokens do not. All login/logout/staff/shift writes execute R1 handlers through bus with trusted actor metadata.

- [x] Contracts first and regenerate. Write PIN failure/lockout, secret leakage, session restart/expiry/revocation, helper approval rejection, owner-only staff management and shift variance tests. Capture RED.
- [x] Implement salted scrypt PINs, bounded login failures, persistent signed sessions (12h), device binding, self-shift ownership, float/count/variance. HTTP may not assert role, owner_ptt or step-up.
- [x] Run task tests; expected PASS. Review STF-1/2/3 and AIQ-1; then credentials, replay and races.
- [x] Checkpoint: record results. Voice PTT establishment and R4 step-up UI remain their own layers; this login cannot grant either from a client flag.

### Task 3: Pack-aware catalog (T1.9)

**Files:** catalog.py, catalog tables/migration, starter CSV, catalog contracts and tests/test_l1b_catalog.py; domain read/view routes.

**Interfaces:** `register_catalog(bus, packs)` registers `catalog.add_item`, `catalog.import_items`, `catalog.change_price` (R2), `catalog.bulk_price` (R4); read helpers return scoped public rows. Catalog owns items, aliases, barcodes, append-only prices, tax, modifier groups/options, recipes and service definitions. Pack catalog schema and units drive validation, without branching on pack name.

- [x] Contracts/examples first and regenerate. Write pack field validation, owner-reviewed import, barcode collision rollback, price history/R2/R4, modifier price arithmetic and tenant-scoped FTS tests. Capture RED.
- [x] Implement schema validation and records with integer pricing; seed synthetic kirana CSV through confirmed import. Frozen migration creates trigram FTS5 with tenant column and synchronized data. Stock consumption and appointment scheduling remain later tasks.
- [x] Run task tests; expected PASS and top-5 search <50ms on fixture catalog. Review CAT-1/4, TAX-1, CAFE-1/2, PHAR-1, SAL-1 storage; then integrity and query scoping.
- [x] Checkpoint: record results.

### Task 4: Deterministic resolution and CP-1b (T1.10)

**Files:** resolution.py, 150-utterance fixture, tests/test_l1b_resolution.py, API integration tests and contracts; main view invalidation registration.

**Interfaces:** `normalize(text)`, `transliterate(text)`, `resolve(repo, text, embedding_hook=None)` return stage, candidates (max five), selected item or disambiguation. Stages are normalize/exact → alias → transliteration → fuzzy → injected embedding hook, followed by deterministic frequency reranking. Ties below 0.08 confidence margin request clarification. Unknown input has no selected item.

- [x] Define resolution/search view schemas and examples; regenerate. Write independent 150-case fixture, ambiguity/unknown/script/tenant tests and real API login→settings→import→search→R2 price confirmation tests. Capture RED.
- [x] Implement deterministic stages and explicit embedding seam, using scoped catalog candidates and stable ID tie-breaks. Add relevant language/onboarding/staff/shift/item view routes with invalidate_on topics.
- [x] Run 150-case eval: deterministic line F1 ≥0.92, without counting ambiguous cases as arbitrary successes; test top-5 latency. Review CAT-2/3 and tenant boundaries; then complexity and fallback behavior.
- [x] Self-review every task against its IDs, then quality. Fix findings with RED/GREEN evidence and sync source snapshots.
- [x] Run `python dev.py check`; expected exit 0 before marking CP-1b or advancing to T1.11.
- [x] Record real gate output, acceptance mapping and rulings; update index. Check plan CRLF and source-block equality.

## Execution ledger

**CP-1b complete, 30 Oct 2026.** Final `python dev.py check` exited 0 after the startup recovery fix: **557 pytest passed, 1 existing Starlette/httpx deprecation warning; 158 Vitest passed (4 files)**. Generated artifacts current: 45 Python files and 90 frontend files. Ruff/Prettier/mypy/tsc clean. Startup recovery regression: RED then 1 passed; final whole suite green. Every task reviewed against spec IDs, then code quality, inline by the author; no independent reviewer per no-subagents instruction. No deferred minors identified.

| Acceptance | Evidence |
|---|---|
| T1.7 ONB-1/5, I18N-2, TAX-1 | test_l1b_merchants; test_l1b_api; merchant quiet-hour review regression |
| T1.8 STF-1/2/3, AIQ-1 | test_l1b_staff; test_l1b_review (PIN replay, private signing key, owner voice binding, revoked queue) |
| T1.9 CAT-1/4, TAX-1, pack catalog storage | test_l1b_catalog (confirmed import/collision rollback, history/R2/R4, FTS latency, modifier totals and schema probes); test_migrations |
| T1.10 CAT-2/3 | test_l1b_resolution (150-case deterministic line >=0.92, ambiguity, unknowns, scoped embedding hook); test_l1b_api |
| Startup consumer recovery | test_l1b_recovery without a new merchant request |
| Contracts/views/events/auth | pytest/Vitest shared schema examples and round-trips; test_openapi_contract; live onboarding event checks; full API flow and restart |

User authorized continuing directly into L1c after this checkpoint. Keep the same no-git/no-secret-inspection/no-subagents rules and batch gates. Next plan must be grounded in current dependencies starting with T1.11.

Task 1 RED: 2 missing-domain failures. GREEN: 4 tests including migration drift. Task 2 RED: 2 missing StaffService failures. GREEN: staff/session and merchant tests 4 passed. Task 3 RED: 3 missing-catalog failures. GREEN: catalog plus migration tests 5 passed. Task 4 RED: 2 missing-resolver failures. GREEN: 150-case line and ambiguity/unknown/embedding-scoping tests 2 passed.

API integration RED: merchant.bootstrap unregistered in main; GREEN: 2 tests including documented route equality. Full flow exercises login, three languages, confirmed import, catalog reads, onboarding, R2 price approval, audit and restart.

Review RED→GREEN fixes: reused successful login key must still count wrong PINs; tenant quiet hours must apply and cannot loosen core; separate server signing key prevents surface-token session forgery; trusted owner device PTT turn must validate without granting PTT over HTTP; live onboarding event must use a prefixed device ULID. Latest combined identity/API/review run: 10 passed, one existing Starlette/httpx deprecation warning. Catalog/resolution runs green; full gate still pending.

Baseline note: the optional fresh baseline check overlapped creation of new contract examples, invalidating its frontend inventory check. Its backend result was 447 passed, one existing warning; the authoritative pre-change full baseline is the previous CP-1a gate. Do not treat that overlapping run as a completed gate. All later generators and gate runs must be sequential with mutations.

Implementation status: domains tables, frozen 0003 including trigram FTS/triggers, merchants, PIN security/session service, catalog, resolver, commerce API, main registration and session dependency are implemented. Pending before CP-1b: finish replacing inline internal schemas with their newly generated contract files; update contract inventory assertions; final per-task spec/quality review; full gate; source snapshot synchronization (L1a changed blocks and this plan), CRLF, index.

Review completion before batch gate: internal command schemas now reference contracts; registries enumerate the expanded contract inventory; generator acronym mismatch corrected by naming i18n.changed's exported type LanguageChanged. `python dev.py gen` exited 0 (90 frontend files). Required shop name/VPA/address before onboarding details now has RED→GREEN coverage (initial fixture idempotency collision corrected before capturing the true RED). Relevant merchant/API run: 4 passed. Entire targeted task set plus drift: 17 passed before the final details regression; final full gate running.

Task 1 spec review: ONB-1/5, I18N-2, TAX-1 — independent language persistence/envelopes, explicit pack at trusted provisioning, required details, ordered five steps, catalog-presence check, defaults never grant consent. Quality: tenant/owner boundaries, private bootstrap credential context, canonical IDs, strict shared schemas and quiet-hour tightening.

Task 2 spec review: STF-1/2/3, AIQ-1 — current-role PIN sessions, owner-only staff creation, helper restrictions, device and trusted owner-PTT binding, self-owned shift float/count/variance. Quality: salted scrypt, five-attempt lockout, separate private signing key, expiry/revocation/restart and queued-command session validation, no raw PIN/token persistence.

Task 3 spec review: CAT-1/4, TAX-1, CAFE-1/2, PHAR-1, SAL-1 storage — catalog/aliases/barcodes/history/tax/modifiers/BOM/services; pack schema/unit validation; confirmed CSV import, atomic collisions, R2 single and R4 bulk prices, required modifier arithmetic. Quality: scoped SQL/FTS parameters, frozen migration and explicit exclusion of FTS-managed shadow tables from model drift (behavior is tested), no direct stock/appointment implementation in this task.

Task 4 spec review: CAT-2/3 — 150 independent query/expected-SKU cases across 25 synthetic starter items, normalization/alias/transliteration/fuzzy stages, explicit ambiguity, unknown input and scoped embedding hook. Quality: deterministic frequency/ID ordering, bounded five candidates, finite hook scores and foreign-ID exclusion. The line tests the deterministic fixture; it is not a production speech-quality claim. No embedding model is loaded until L3.

First full batch gate: exit 0; 556 pytest passed (one existing warning), 158 Vitest passed; 45 Python generated files and 90 frontend generated files current; lint and types clean. Final lifecycle regression then demonstrated that startup did not activate persisted merchants for outbox consumers without a new command. Added a startup-only tenant-ID directory read in Repository and seeded the dispatcher's merchant inventory before its loop. Regression RED captured; final verification pending.

Ruling: startup orchestration may enumerate the root merchant directory (IDs only; id must equal merchant_id) to recover durable consumers. This is control-plane inventory, never a client business-data read; all business-data repository operations still inject the session's merchant_id predicate, and no endpoint exposes the directory. Cost: the API process learns registered tenant IDs at startup; without this inventory durable work would wait for another request.

Ruling: merchant quiet hours can tighten core quiet hours but cannot remove the core protected interval. Cost: owners cannot configure a shorter protected interval than the default without an explicit policy change.

Ruling: failed authentication attempts receive server-generated attempt keys so replaying a successful client key cannot bypass lockout; successful login replays remain stored-result replays after PIN verification. Cost: repeated failed HTTP requests each count toward the five-attempt lockout.

Ruling: a private session signing key is loaded from ARTH_SESSION_SIGNING_KEY or generated once under the server data directory as session-signing.key. Surface bearer tokens are never signing keys. Cost: operators must retain that server key across restarts or intentionally invalidate sessions by rotating it; changing it invalidates signed device credentials too.

Plan self-review: T1.7–T1.10 covered; shared interfaces align with L1a. L1a source snapshots are historical; when shared L1a code changes, sync those snapshots too. Frozen migration 0002 remains unchanged.

Pre-flight: merchant bootstrap precedes staff login; catalog import completes onboarding step four; staff execution metadata supplies actor ownership to shifts; catalog candidates feed resolver. Domain-event causation uses the executing command ID. Private credential context is R1-only and never survives an approval gate.

Ruling: first-shop provisioning remains trusted startup/operator code because account/device enrollment authority is unspecified; the public login API uses an already registered device. Cost: fresh installation needs the provisioning entry point before device onboarding.

Ruling: L1b is T1.7–T1.10 (one four-task batch). Stock/billing and the remaining T1.11–T1.23 follow after this gate. Cost: they are intentionally unavailable at CP-1b.


## Implemented source snapshots

These fenced blocks equal the authored files on disk. Generated files are regenerated, never hand-edited.

### backend/arth/domains/__init__.py

```python
"""Merchant-scoped commerce modules."""
```

### backend/arth/domains/tables.py

```python
"""L1b identity and catalog tables (all domain queries are merchant scoped)."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata
from arth.governance.tables import tenant

devices = Table(
    "devices",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("edition", String, nullable=False),
    Column("capabilities", Text, nullable=False, server_default="{}"),
    CheckConstraint("json_valid(capabilities)"),
)
onboarding_progress = Table(
    "onboarding_progress",
    metadata,
    tenant(),
    Column("step", String, nullable=False),
    Column("completed_at", String, nullable=False),
    UniqueConstraint("merchant_id", "step"),
)
staff_credentials = Table(
    "staff_credentials",
    metadata,
    Column("staff_id", String, primary_key=True),
    tenant(),
    Column("pin_hash", Text, nullable=False),
    Column("failed", Integer, nullable=False, server_default="0"),
    Column("locked_until", String),
)
staff_sessions = Table(
    "staff_sessions",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("revoked", Integer, nullable=False, server_default="0"),
)
shifts = Table(
    "shifts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("opened_at", String, nullable=False),
    Column("closed_at", String),
    Column("float_paise", Integer, nullable=False),
    Column("expected_paise", Integer, nullable=False),
    Column("counted_paise", Integer),
    Column("variance_paise", Integer),
    CheckConstraint("float_paise >= 0 AND expected_paise >= 0"),
)

items = Table(
    "items",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("sku", String, nullable=False),
    Column("names", Text, nullable=False),
    Column("unit", String, nullable=False),
    Column("category", String, nullable=False),
    Column("mrp_paise", Integer, nullable=False),
    Column("price_paise", Integer, nullable=False),
    Column("cost_paise", Integer, nullable=False),
    Column("details", Text, nullable=False, server_default="{}"),
    Column("search_text", Text, nullable=False),
    Column("frequency", Integer, nullable=False, server_default="0"),
    UniqueConstraint("merchant_id", "sku"),
    CheckConstraint("json_valid(names) AND json_valid(details)"),
    CheckConstraint("mrp_paise >= 0 AND price_paise >= 0 AND cost_paise >= 0"),
)
item_aliases = Table(
    "item_aliases",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("alias", String, nullable=False),
    UniqueConstraint("merchant_id", "item_id", "alias"),
)
item_barcodes = Table(
    "item_barcodes",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("barcode", String, nullable=False),
    UniqueConstraint("merchant_id", "barcode"),
)
item_prices = Table(
    "item_prices",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("price_paise", Integer, nullable=False),
    Column("effective_from", String, nullable=False),
    Column("command_id", String, nullable=False),
    CheckConstraint("price_paise >= 0"),
)
item_tax = Table(
    "item_tax",
    metadata,
    Column("item_id", String, primary_key=True),
    tenant(),
    Column("hsn", String, nullable=False, server_default=""),
    Column("gst_rate_bp", Integer, nullable=False, server_default="0"),
    CheckConstraint("gst_rate_bp >= 0 AND gst_rate_bp <= 10000"),
)
modifier_groups = Table(
    "modifier_groups",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("item_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("required", Integer, nullable=False),
)
modifiers = Table(
    "modifiers",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("group_id", String, nullable=False),
    Column("name", String, nullable=False),
    Column("delta_paise", Integer, nullable=False),
)
recipes = Table(
    "recipes",
    metadata,
    tenant(),
    Column("item_id", String, nullable=False),
    Column("ingredient_id", String, nullable=False),
    Column("qty_milli", Integer, nullable=False),
    UniqueConstraint("merchant_id", "item_id", "ingredient_id"),
    CheckConstraint("qty_milli > 0"),
)
services = Table(
    "services",
    metadata,
    Column("item_id", String, primary_key=True),
    tenant(),
    Column("duration_minutes", Integer, nullable=False),
    Column("required_skill", String, nullable=False),
    CheckConstraint("duration_minutes > 0"),
)
```

### backend/arth/domains/security.py

```python
"""Credential primitives. Nothing here logs or serializes supplied PINs."""

import hashlib
import os
import re
import secrets
from pathlib import Path

from pydantic import SecretStr


def load_signing_key(path: Path) -> SecretStr:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        pass
    else:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(secrets.token_hex(32))
    value = path.read_text(encoding="utf-8")
    if not re.fullmatch("[0-9a-f]{64}", value):
        raise ValueError("auth.invalid_signing_key_file")
    return SecretStr(value)


def hash_pin(pin: str) -> str:
    if not pin.isascii() or not pin.isdigit() or not 4 <= len(pin) <= 8:
        raise ValueError("staff.invalid_pin")
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(pin.encode(), salt=salt, n=16384, r=8, p=1).hex()
    return f"scrypt${salt.hex()}${digest}"


def verify_pin(pin: str, encoded: str) -> bool:
    try:
        algorithm, salt, digest = encoded.split("$")
        if algorithm != "scrypt" or not pin.isascii() or not pin.isdigit() or not 4 <= len(pin) <= 8:
            return False
        actual = hashlib.scrypt(pin.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1).hex()
        return secrets.compare_digest(actual, digest)
    except (ValueError, TypeError):
        return False
```

### backend/arth/domains/merchants.py

```python
"""Merchant settings, trusted initial provisioning and ordered onboarding."""

import hashlib
import json
from typing import Any

from arth.core.clock import iso_utc
from arth.core.packs import PackRegistry
from arth.core.schemas import schema
from arth.domains.security import hash_pin
from arth.domains.tables import devices, onboarding_progress, staff_credentials
from arth.governance.commands import CommandBus, CommandError
from arth.governance.events import emit_event
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import merchant_settings, merchants, staff

DEFAULTS = {
    "screen_lang": "hi-Latn",
    "speech_lang": "hi-IN",
    "customer_lang": "hi",
    "tax_profile": "unregistered",
    "hours": {"start": "08:00", "end": "21:00"},
    "quiet_hours": {"start": "21:30", "end": "08:00"},
    "marketing_consent_default": False,
    "receipts_consent_default": False,
}
STEPS = ("language", "pack", "details", "catalog", "people")


def stable_id(kind: str, key: str) -> str:
    value = int.from_bytes(hashlib.sha256((kind + ":" + key).encode()).digest()[:16])
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    chars = "".join(alphabet[(value >> shift) & 31] for shift in range(125, -1, -5))
    return kind + "_" + chars


def owner_only(repo: Repository) -> None:
    if repo.session is None or repo.session.role != "owner":
        raise CommandError("policy.owner_required")


async def settings_view(repo: Repository) -> dict[str, Any]:
    shops = await repo.select(merchants)
    if not shops:
        raise CommandError("merchant.not_found")
    settings = await repo.select(merchant_settings)
    return {
        **DEFAULTS,
        **(json.loads(settings[0]["settings"]) if settings else {}),
        "name": shops[0]["name"],
        "pack": shops[0]["pack"],
    }


async def onboarding_view(repo: Repository) -> dict[str, Any]:
    await settings_view(repo)
    completed = {row["step"] for row in await repo.select(onboarding_progress)}
    return {
        "steps": list(STEPS),
        "completed": [step for step in STEPS if step in completed],
        "next_step": next((step for step in STEPS if step not in completed), None),
        "invalidate_on": ["onboarding.updated"],
    }


async def domain_event(bus: CommandBus, repo: Repository, topic: str, payload: dict[str, Any]) -> None:
    assert repo.session is not None and repo.command_id is not None
    await emit_event(repo, bus.clock, repo.session, topic, repo.command_id, payload)


def register_merchants(bus: CommandBus, packs: PackRegistry) -> None:
    async def bootstrap(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if not repo.private.get("bootstrap"):
            raise CommandError("merchant.trusted_provisioning_required")
        packs.get(payload["pack"])
        await repo.insert(
            merchants, {"id": repo.merchant_id, "name": payload["name"], "pack": payload["pack"]}
        )
        await repo.insert(merchant_settings, {"settings": json.dumps(DEFAULTS)})
        await repo.insert(staff, {"id": payload["owner_id"], "role": "owner", "name": payload["owner_name"]})
        await repo.insert(
            staff_credentials, {"staff_id": payload["owner_id"], "pin_hash": hash_pin(repo.private["pin"])}
        )
        await repo.insert(devices, {"id": payload["device_id"], "edition": "display", "capabilities": "{}"})
        result = {
            "merchant_id": repo.merchant_id,
            "owner_id": payload["owner_id"],
            "device_id": payload["device_id"],
        }
        await domain_event(bus, repo, "onboarding.started", {"device_id": payload["device_id"]})
        return result

    async def update_settings(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        old = await settings_view(repo)
        settings = {k: v for k, v in {**old, **payload}.items() if k not in {"name", "pack"}}
        if settings.get("tax_profile") == "regular" and not settings.get("gstin"):
            raise CommandError("merchant.gstin_required")
        if "quiet_hours" in payload:

            def minutes(window: dict[str, str]) -> set[int]:
                start, end = (
                    int(h) * 60 + int(m) for h, m in (window["start"].split(":"), window["end"].split(":"))
                )
                return set(range(start, end)) if start < end else set(range(start, 1440)) | set(range(0, end))

            core = bus.policy.policies.quiet_hours.model_dump()
            if not minutes(core) <= minutes(payload["quiet_hours"]):
                raise CommandError("merchant.quiet_hours_cannot_loosen")
        await repo.update(merchant_settings, {"settings": json.dumps(settings)})
        if "name" in payload:
            await repo.update(merchants, {"name": payload["name"]})
        await domain_event(
            bus,
            repo,
            "i18n.changed",
            {
                "screen_lang": settings["screen_lang"],
                "speech_lang": settings["speech_lang"],
                "customer_lang": settings["customer_lang"],
            },
        )
        return await settings_view(repo)

    async def complete(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        view = await onboarding_view(repo)
        step = payload["step"]
        if step in view["completed"]:
            return view
        if step != view["next_step"]:
            raise CommandError("onboarding.step_order")
        if step == "details":
            settings = await settings_view(repo)
            if not all(settings.get(key, "").strip() for key in ("name", "vpa", "address")):
                raise CommandError("onboarding.details_required")
        if step == "catalog":
            from arth.domains.catalog import catalog_rows

            if not await catalog_rows(repo):
                raise CommandError("onboarding.catalog_required")
        await repo.insert(onboarding_progress, {"step": step, "completed_at": iso_utc(bus.clock.now())})
        await domain_event(bus, repo, "onboarding.updated", {"step": step})
        return await onboarding_view(repo)

    bus.register("merchant.bootstrap", schema("merchant_bootstrap"), bootstrap)
    bus.register("merchant.update_settings", schema("merchant_update_settings"), update_settings)
    bus.register("onboarding.complete_step", schema("onboarding_complete_step"), complete)


async def provision_shop(
    bus: CommandBus, name: str, pack: str, owner_name: str, pin: str, device_id: str, *, key: str
) -> dict[str, Any]:
    mid, owner_id = stable_id("merchant", key), stable_id("staff", key)
    device_id = stable_id("device", device_id)
    result = await bus.submit(
        Session(mid, owner_id, "owner", channel="console"),
        "merchant.bootstrap",
        {"name": name, "pack": pack, "owner_id": owner_id, "owner_name": owner_name, "device_id": device_id},
        key,
        private={"bootstrap": True, "pin": pin},
    )
    return result["data"]
```

### backend/arth/domains/staff.py

```python
"""PIN-backed staff sessions and shift ownership. Secrets never enter bus persistence."""

import hashlib
import hmac
from datetime import timedelta
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.domains.security import hash_pin, verify_pin
from arth.domains.tables import devices, shifts, staff_credentials, staff_sessions
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import staff


class StaffService:
    def __init__(self, bus: CommandBus, signing_key: str) -> None:
        self.bus, self._key = bus, signing_key.encode()
        self._register()
        bus.session_validator = self.validate

    def _sign(self, merchant_id: str, identity: str, kind: str) -> str:
        if any("." in value for value in (merchant_id, identity, kind)):
            raise CommandError("auth.bad_identity")
        body = ".".join((merchant_id, identity, kind))
        return body + "." + hmac.new(self._key, body.encode(), hashlib.sha256).hexdigest()

    def _decode(self, token: str, kind: str) -> tuple[str, str]:
        parts = token.split(".")
        if len(parts) != 4 or len(token) > 500 or parts[2] != kind:
            raise CommandError("auth.invalid_session")
        merchant_id, identity, _, signature = parts
        expected = self._sign(merchant_id, identity, kind).rsplit(".", 1)[1]
        if not hmac.compare_digest(signature, expected):
            raise CommandError("auth.invalid_session")
        return merchant_id, identity

    def device_credential(self, merchant_id: str, device_id: str) -> str:
        return self._sign(merchant_id, device_id, "device")

    def device_identity(self, credential: str) -> tuple[str, str]:
        return self._decode(credential, "device")

    async def resolve(self, token: str) -> Session:
        mid, sid = self._decode(token, "session")
        async with self.bus.db.read() as conn:
            repo = Repository(conn, mid)
            rows = await repo.select(staff_sessions, staff_sessions.c.id == sid)
            if not rows:
                raise CommandError("auth.invalid_session")
            row = rows[0]
            actors = await repo.select(staff, staff.c.id == row["staff_id"])
            if not actors:
                raise CommandError("auth.invalid_session")
            session = Session(
                mid,
                row["staff_id"],
                actors[0]["role"],
                channel=row["channel"],
                device_id=row["device_id"],
                session_id=sid,
            )
            await self.validate(repo, session)
            return session

    async def validate(self, repo: Repository, session: Session) -> None:
        if session.session_id is None:
            return  # trusted internal actors and initial provisioning
        rows = await repo.select(staff_sessions, staff_sessions.c.id == session.session_id)
        actors = await repo.select(staff, staff.c.id == session.actor_id)
        registered = await repo.select(devices, devices.c.id == session.device_id)
        if not rows or not actors or not registered:
            raise CommandError("auth.invalid_session")
        row = rows[0]
        valid_channel = row["channel"] == session.channel or (
            row["channel"] == "device"
            and session.channel == "voice"
            and session.role == "owner"
            and session.owner_ptt
        )
        if (
            row["revoked"]
            or row["expires_at"] <= iso_utc(self.bus.clock.now())
            or row["staff_id"] != session.actor_id
            or not valid_channel
            or row["device_id"] != session.device_id
            or actors[0]["role"] != session.role
        ):
            raise CommandError("auth.expired_session")

    async def login(
        self, device_credential: str, staff_id: str, pin: str, channel: str, key: str
    ) -> dict[str, Any]:
        if channel not in {"device", "console"}:
            raise CommandError("auth.invalid_channel")
        mid, device_id = self._decode(device_credential, "device")
        async with self.bus.db.read() as conn:
            repo = Repository(conn, mid)
            actors = await repo.select(staff, staff.c.id == staff_id)
            credentials = await repo.select(staff_credentials, staff_credentials.c.staff_id == staff_id)
            if not actors or not credentials or not await repo.select(devices, devices.c.id == device_id):
                raise CommandError("staff.invalid_login")
            valid = verify_pin(pin, credentials[0]["pin_hash"])
        result = await self.bus.submit(
            Session(mid, staff_id, actors[0]["role"], channel=channel, device_id=device_id),
            "staff.login",
            {"staff_id": staff_id, "device_id": device_id, "channel": channel},
            key if valid else new_id("attempt"),
            private={"pin": pin},
        )
        if not valid or not result["data"]["authenticated"]:
            raise CommandError(result["data"].get("code", "staff.invalid_login"))
        token = self._sign(mid, result["data"]["session_id"], "session")
        await self.resolve(token)  # replay cannot revive an expired/revoked session
        return {"token": token, "staff_id": staff_id, "expires_at": result["data"]["expires_at"]}

    async def add(self, actor: Session, name: str, role: str, pin: str, key: str) -> dict[str, Any]:
        return await self.bus.submit(
            actor, "staff.add", {"name": name, "role": role}, key, private={"pin": pin}
        )

    def _register(self) -> None:
        bus = self.bus

        async def add(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            if "pin" not in repo.private:
                raise CommandError("staff.pin_required")
            identity = new_id("staff")
            await repo.insert(staff, {"id": identity, **payload})
            await repo.insert(
                staff_credentials, {"staff_id": identity, "pin_hash": hash_pin(repo.private["pin"])}
            )
            await domain_event(bus, repo, "staff.added", {"staff_id": identity, "role": payload["role"]})
            return {"staff_id": identity, "name": payload["name"], "role": payload["role"]}

        async def login(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if (
                repo.session is None
                or repo.session.actor_id != payload["staff_id"]
                or "pin" not in repo.private
            ):
                raise CommandError("staff.invalid_login")
            rows = await repo.select(staff_credentials, staff_credentials.c.staff_id == payload["staff_id"])
            if not rows:
                raise CommandError("staff.invalid_login")
            row = rows[0]
            now = iso_utc(bus.clock.now())
            if row["locked_until"] and row["locked_until"] > now:
                return {"authenticated": False, "code": "staff.locked"}
            if not verify_pin(repo.private["pin"], row["pin_hash"]):
                failed = (row["failed"] if not row["locked_until"] or row["locked_until"] > now else 0) + 1
                await repo.update(
                    staff_credentials,
                    {
                        "failed": failed,
                        "locked_until": iso_utc(bus.clock.now() + timedelta(minutes=5))
                        if failed >= 5
                        else None,
                    },
                    staff_credentials.c.staff_id == payload["staff_id"],
                )
                return {"authenticated": False, "code": "staff.invalid_login"}
            await repo.update(
                staff_credentials,
                {"failed": 0, "locked_until": None},
                staff_credentials.c.staff_id == payload["staff_id"],
            )
            sid = new_id("session")
            expires = iso_utc(bus.clock.now() + timedelta(hours=12))
            await repo.insert(
                staff_sessions,
                {
                    "id": sid,
                    "staff_id": payload["staff_id"],
                    "device_id": payload["device_id"],
                    "channel": payload["channel"],
                    "expires_at": expires,
                },
            )
            await domain_event(
                bus, repo, "staff.logged_in", {"staff_id": payload["staff_id"], "session_id": sid}
            )
            return {"authenticated": True, "session_id": sid, "expires_at": expires}

        async def logout(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if repo.session is None or repo.session.session_id is None:
                raise CommandError("auth.invalid_session")
            await repo.update(staff_sessions, {"revoked": 1}, staff_sessions.c.id == repo.session.session_id)
            return {"logged_out": True}

        async def open_shift(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            assert repo.session is not None
            if await repo.select(
                shifts, shifts.c.staff_id == repo.session.actor_id, shifts.c.closed_at.is_(None)
            ):
                raise CommandError("shift.already_open")
            identity = new_id("shift")
            await repo.insert(
                shifts,
                {
                    "id": identity,
                    "staff_id": repo.session.actor_id,
                    "opened_at": iso_utc(bus.clock.now()),
                    "float_paise": payload["float_paise"],
                    "expected_paise": payload["float_paise"],
                },
            )
            await domain_event(
                bus, repo, "staff.shift_opened", {"shift_id": identity, "staff_id": repo.session.actor_id}
            )
            return {"shift_id": identity, "staff_id": repo.session.actor_id}

        async def close_shift(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            assert repo.session is not None
            rows = await repo.select(
                shifts,
                shifts.c.id == payload["shift_id"],
                shifts.c.staff_id == repo.session.actor_id,
                shifts.c.closed_at.is_(None),
            )
            if not rows:
                raise CommandError("shift.not_open")
            variance = payload["counted_paise"] - rows[0]["expected_paise"]
            await repo.update(
                shifts,
                {
                    "closed_at": iso_utc(bus.clock.now()),
                    "counted_paise": payload["counted_paise"],
                    "variance_paise": variance,
                },
                shifts.c.id == payload["shift_id"],
            )
            await domain_event(
                bus, repo, "staff.shift_closed", {"shift_id": payload["shift_id"], "variance_paise": variance}
            )
            return {
                "shift_id": payload["shift_id"],
                "staff_id": repo.session.actor_id,
                "variance_paise": variance,
            }

        bus.register("staff.add", schema("staff_add_command"), add)
        bus.register("staff.login", schema("staff_login_command"), login)
        bus.register("staff.logout", schema("staff_logout"), logout)
        bus.register("shift.open", schema("shift_open"), open_shift)
        bus.register("shift.close", schema("shift_close"), close_shift)
```

### backend/arth/domains/catalog.py

```python
"""Pack-schema catalog, append-only prices and deterministic modifier arithmetic."""

import csv
import json
from pathlib import Path
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.packs import PackManifest, PackRegistry
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.domains.tables import (
    item_aliases,
    item_barcodes,
    item_prices,
    item_tax,
    items,
    modifier_groups,
    modifiers,
    recipes,
    services,
)
from arth.governance.commands import CommandBus, CommandError
from arth.governance.repository import Repository
from arth.governance.tables import merchants


def validate_pack_item(payload: dict[str, Any], pack: PackManifest) -> None:
    if payload["unit"] not in pack.catalog.units:
        raise CommandError("catalog.invalid_unit")
    details = payload.get("details", {})
    if pack.catalog.schema_ == "medicine" and not all(
        key in details for key in ("salt", "strength", "form", "pack_size", "schedule", "rx_required")
    ):
        raise CommandError("catalog.medicine_fields_required")
    if pack.catalog.schema_ == "service" and not all(
        key in details for key in ("duration_minutes", "required_skill")
    ):
        raise CommandError("catalog.service_fields_required")
    if pack.catalog.schema_ != "menu" and payload.get("modifier_groups"):
        raise CommandError("catalog.modifiers_not_supported")
    if not pack.stock.bom and payload.get("recipe"):
        raise CommandError("catalog.recipe_not_supported")


def public_item(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: json.loads(value) if key in {"names", "details"} else value
        for key, value in row.items()
        if key not in {"merchant_id", "search_text"}
    }


async def catalog_rows(repo: Repository) -> list[dict[str, Any]]:
    return [public_item(row) for row in await repo.select(items)]


async def get_item(repo: Repository, identity: str) -> dict[str, Any]:
    rows = await repo.select(items, items.c.id == identity)
    if not rows:
        raise CommandError("catalog.item_not_found")
    row = public_item(rows[0])
    row["aliases"] = [r["alias"] for r in await repo.select(item_aliases, item_aliases.c.item_id == identity)]
    row["barcodes"] = [
        r["barcode"] for r in await repo.select(item_barcodes, item_barcodes.c.item_id == identity)
    ]
    tax = await repo.select(item_tax, item_tax.c.item_id == identity)
    row.update({key: tax[0][key] for key in ("hsn", "gst_rate_bp")})
    groups = []
    for group in await repo.select(modifier_groups, modifier_groups.c.item_id == identity):
        options = await repo.select(modifiers, modifiers.c.group_id == group["id"])
        groups.append(
            {
                "id": group["id"],
                "name": group["name"],
                "required": bool(group["required"]),
                "options": [{k: r[k] for k in ("id", "name", "delta_paise")} for r in options],
            }
        )
    row["modifier_groups"] = groups
    row["recipe"] = [
        {"item_id": r["ingredient_id"], "qty_milli": r["qty_milli"]}
        for r in await repo.select(recipes, recipes.c.item_id == identity)
    ]
    return row


async def modifier_total(repo: Repository, identity: str, selections: dict[str, list[str]]) -> int:
    row = await get_item(repo, identity)
    groups = {group["id"]: group for group in row["modifier_groups"]}
    if set(selections) - set(groups):
        raise CommandError("catalog.invalid_modifier")
    total = row["price_paise"]
    for gid, group in groups.items():
        chosen = selections.get(gid, [])
        options = {option["id"]: option for option in group["options"]}
        if (
            (group["required"] and not chosen)
            or len(chosen) != len(set(chosen))
            or set(chosen) - set(options)
        ):
            raise CommandError("catalog.invalid_modifier")
        total += sum(options[identity]["delta_paise"] for identity in chosen)
    if total < 0:
        raise CommandError("catalog.invalid_modifier_total")
    return total


def read_starter(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return [
            {
                "sku": r["sku"],
                "names": {"en": r["en"], "hi": r["hi"], "hi-Latn": r["hi_latn"]},
                "unit": r["unit"],
                "mrp_paise": int(r["mrp_paise"]),
                "price_paise": int(r["price_paise"]),
                "cost_paise": int(r["cost_paise"]),
                "category": r["category"],
                "aliases": r["aliases"].split("|") if r["aliases"] else [],
                "barcodes": [],
            }
            for r in csv.DictReader(handle)
        ]


def register_catalog(bus: CommandBus, packs: PackRegistry) -> None:
    async def add(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        shop = (await repo.select(merchants))[0]
        pack = packs.get(shop["pack"])
        validate_pack_item(payload, pack)
        if await repo.select(items, items.c.sku == payload["sku"]):
            raise CommandError("catalog.duplicate_sku")
        for barcode in payload.get("barcodes", []):
            if await repo.select(item_barcodes, item_barcodes.c.barcode == barcode):
                raise CommandError("catalog.duplicate_barcode")
        for ingredient in payload.get("recipe", []):
            if not await repo.select(items, items.c.id == ingredient["item_id"]):
                raise CommandError("catalog.ingredient_not_found")
        identity = new_id("item")
        search_text = " ".join(
            [*payload["names"].values(), *payload.get("aliases", []), payload["sku"]]
        ).lower()
        await repo.insert(
            items,
            {
                "id": identity,
                **{
                    key: payload[key]
                    for key in ("sku", "unit", "category", "mrp_paise", "price_paise", "cost_paise")
                },
                "names": json.dumps(payload["names"], ensure_ascii=False),
                "details": json.dumps(payload.get("details", {}), ensure_ascii=False),
                "search_text": search_text,
            },
        )
        for alias in payload.get("aliases", []):
            await repo.insert(item_aliases, {"id": new_id("alias"), "item_id": identity, "alias": alias})
        for barcode in payload.get("barcodes", []):
            await repo.insert(
                item_barcodes, {"id": new_id("barcode"), "item_id": identity, "barcode": barcode}
            )
        await repo.insert(
            item_prices,
            {
                "item_id": identity,
                "price_paise": payload["price_paise"],
                "effective_from": iso_utc(bus.clock.now()),
                "command_id": repo.command_id,
            },
        )
        await repo.insert(
            item_tax,
            {
                "item_id": identity,
                "hsn": payload.get("hsn", ""),
                "gst_rate_bp": payload.get("gst_rate_bp", 0),
            },
        )
        for group in payload.get("modifier_groups", []):
            gid = new_id("modgroup")
            await repo.insert(
                modifier_groups,
                {"id": gid, "item_id": identity, "name": group["name"], "required": int(group["required"])},
            )
            for option in group["options"]:
                await repo.insert(modifiers, {"id": new_id("modifier"), "group_id": gid, **option})
        for ingredient in payload.get("recipe", []):
            await repo.insert(
                recipes,
                {
                    "item_id": identity,
                    "ingredient_id": ingredient["item_id"],
                    "qty_milli": ingredient["qty_milli"],
                },
            )
        if pack.catalog.schema_ == "service":
            await repo.insert(
                services,
                {
                    "item_id": identity,
                    **{key: payload["details"][key] for key in ("duration_minutes", "required_skill")},
                },
            )
        await domain_event(bus, repo, "catalog.item_added", {"item_id": identity})
        return {"item_id": identity}

    async def import_items(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        return {"item_ids": [(await add(repo, entry))["item_id"] for entry in payload["items"]]}

    async def change_price(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        if repo.session is None or repo.session.role not in {"owner", "manager"}:
            raise CommandError("policy.role")
        await get_item(repo, payload["item_id"])
        await repo.insert(
            item_prices,
            {
                "item_id": payload["item_id"],
                "price_paise": payload["price_paise"],
                "effective_from": iso_utc(bus.clock.now()),
                "command_id": repo.command_id,
            },
        )
        await repo.update(items, {"price_paise": payload["price_paise"]}, items.c.id == payload["item_id"])
        await domain_event(bus, repo, "catalog.price_changed", payload)
        return payload

    async def bulk(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
        owner_only(repo)
        if len({row["item_id"] for row in payload["prices"]}) != len(payload["prices"]):
            raise CommandError("catalog.duplicate_item")
        return {"prices": [await change_price(repo, row) for row in payload["prices"]]}

    for kind, handler in [
        ("catalog.add_item", add),
        ("catalog.import_items", import_items),
        ("catalog.change_price", change_price),
        ("catalog.bulk_price", bulk),
    ]:
        bus.register(kind, schema(kind.replace(".", "_")), handler)
```

### backend/arth/domains/resolution.py

```python
"""Deterministic item resolution; ambiguity is data, never an arbitrary choice."""

import math
import re
import unicodedata
from collections.abc import Awaitable, Callable
from difflib import SequenceMatcher
from typing import Any

from arth.domains.catalog import public_item
from arth.domains.tables import item_aliases, items
from arth.governance.repository import Repository

EmbeddingHook = Callable[[str, list[dict[str, Any]]], Awaitable[dict[str, float]]]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).casefold()
    return " ".join("".join(char if unicodedata.category(char)[0] in "LNM" else " " for char in text).split())


CONSONANTS = dict(
    zip(
        "कखगघङचछजझञटठडढणतथदधनपफबभमयरलवशषसह",
        [
            "k",
            "kh",
            "g",
            "gh",
            "ng",
            "ch",
            "chh",
            "j",
            "jh",
            "ny",
            "t",
            "th",
            "d",
            "dh",
            "n",
            "t",
            "th",
            "d",
            "dh",
            "n",
            "p",
            "ph",
            "b",
            "bh",
            "m",
            "y",
            "r",
            "l",
            "v",
            "sh",
            "sh",
            "s",
            "h",
        ],
        strict=True,
    )
)
VOWELS = dict(zip("अआइईउऊऋएऐओऔ", ["a", "aa", "i", "ii", "u", "uu", "ri", "e", "ai", "o", "au"], strict=True))
SIGNS = dict(zip("ािीुूृेैोौ", ["aa", "i", "ii", "u", "uu", "ri", "e", "ai", "o", "au"], strict=True))


def transliterate(text: str) -> str:
    words = []
    for word in normalize(text).split():
        out = ""
        devanagari = False
        for char in word:
            if char in CONSONANTS:
                out += CONSONANTS[char] + "a"
                devanagari = True
            elif char in SIGNS:
                out = out.removesuffix("a") + SIGNS[char]
            elif char == "्":
                out = out.removesuffix("a")
            elif char in VOWELS:
                out += VOWELS[char]
                devanagari = True
            elif char in "ंँ":
                out += "n"
            elif char != "़":
                out += char
        if devanagari:
            out = out.removesuffix("a")
        words.append(re.sub(r"([aeiou])\1+", r"\1", out).replace("ee", "i").replace("oo", "u"))
    return " ".join(words)


async def resolve(repo: Repository, text: str, embedding_hook: EmbeddingHook | None = None) -> dict[str, Any]:
    query = normalize(text)
    rows = await repo.select(items)
    aliases: dict[str, list[str]] = {row["id"]: [] for row in rows}
    for alias in await repo.select(item_aliases):
        if alias["item_id"] in aliases:
            aliases[alias["item_id"]].append(alias["alias"])
    candidates = [public_item(row) for row in rows]

    def response(stage: str, scores: dict[str, float]) -> dict[str, Any]:
        ranked = sorted(
            (
                dict(row, confidence=round(scores[row["id"]], 4))
                for row in candidates
                if scores.get(row["id"], 0) >= 0.72
            ),
            key=lambda r: (-r["confidence"], -r["frequency"], r["id"]),
        )[:5]
        ambiguous = len(ranked) > 1 and ranked[0]["confidence"] - ranked[1]["confidence"] < 0.08
        return {
            "stage": stage,
            "candidates": ranked,
            "selected": ranked[0] if ranked and not ambiguous else None,
            "needs_clarification": ambiguous,
            "invalidate_on": ["catalog.item_added", "catalog.price_changed"],
        }

    if not query or not rows:
        return response("none", {})
    names = {row["id"]: [*row["names"].values(), row["sku"]] for row in candidates}
    exact = {
        identity: 1.0 for identity, values in names.items() if query in [normalize(value) for value in values]
    }
    if exact:
        return response("normalize", exact)
    exact = {
        identity: 1.0
        for identity, values in aliases.items()
        if query in [normalize(value) for value in values]
    }
    if exact:
        return response("alias", exact)
    keys = {
        identity: [transliterate(value) for value in names[identity] + aliases[identity]]
        for identity in names
    }
    roman = transliterate(text)
    exact = {identity: 0.98 for identity, values in keys.items() if roman in values}
    if exact:
        return response("transliteration", exact)
    fuzzy = {
        identity: max(SequenceMatcher(None, roman, value).ratio() for value in values)
        for identity, values in keys.items()
    }
    result = response("fuzzy", fuzzy)
    if result["candidates"]:
        return result
    if embedding_hook:
        scores = await embedding_hook(text, candidates)
        safe = {
            identity: float(score)
            for identity, score in scores.items()
            if identity in names and type(score) in (int, float) and math.isfinite(score) and 0 <= score <= 1
        }
        return response("embedding", safe)
    return response("none", {})
```

### backend/arth/api/commerce.py

```python
"""L1b authentication, scoped catalog reads and screen read models."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Query, Request

from arth.api.auth import require_token
from arth.api.governance import require_session
from arth.api.problems import ProblemError
from arth.contracts.staff_add import StaffAdd
from arth.contracts.staff_login import StaffLogin
from arth.domains.catalog import get_item, public_item
from arth.domains.merchants import onboarding_view, settings_view
from arth.domains.resolution import resolve
from arth.domains.tables import devices, shifts
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import staff

router = APIRouter()
Actor = Annotated[Session, Depends(require_session)]
Key = Annotated[str, Header(min_length=1, max_length=200)]
CATALOG_EVENTS = ["catalog.item_added", "catalog.price_changed"]


@router.post("/v1/staff/login")
async def login(request: Request, body: StaffLogin, idempotency_key: Key) -> dict[str, Any]:
    await require_token(body.channel.value)(request)
    try:
        return await request.app.state.staff.login(
            body.device_credential, body.staff_id, body.pin, body.channel.value, idempotency_key
        )
    except CommandError as exc:
        raise ProblemError(401, str(exc), "error." + str(exc), title="Login refused") from exc


@router.post("/v1/staff")
async def add_staff(request: Request, body: StaffAdd, session: Actor, idempotency_key: Key) -> dict[str, Any]:
    return await request.app.state.staff.add(session, body.name, body.role.value, body.pin, idempotency_key)


@router.get("/v1/catalog/search")
async def search(
    request: Request, session: Actor, q: Annotated[str, Query(min_length=1, max_length=200)]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).search_catalog(q)
        return {"items": [public_item(row) for row in rows], "invalidate_on": CATALOG_EVENTS}


@router.get("/v1/catalog/resolve")
async def resolution(
    request: Request, session: Actor, q: Annotated[str, Query(min_length=1, max_length=200)]
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await resolve(Repository(conn, session.merchant_id), q)


@router.get("/v1/views/settings/language")
async def language(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return {
            **await settings_view(Repository(conn, session.merchant_id)),
            "invalidate_on": ["i18n.changed"],
        }


@router.get("/v1/views/onboarding")
async def onboarding(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await onboarding_view(Repository(conn, session.merchant_id))


@router.get("/v1/views/settings/staff")
async def staff_settings(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(staff)
        return {
            "staff": [{k: r[k] for k in ("id", "name", "role")} for r in rows],
            "invalidate_on": ["staff.added"],
        }


@router.get("/v1/views/staff/login")
async def staff_login_view(request: Request, x_device_credential: Annotated[str, Header()]) -> dict[str, Any]:
    await require_token("device")(request)
    try:
        mid, device_id = request.app.state.staff.device_identity(x_device_credential)
    except CommandError as exc:
        raise ProblemError(401, str(exc), "error." + str(exc), title="Invalid device") from exc
    async with request.app.state.db.read() as conn:
        repo = Repository(conn, mid)
        if not await repo.select(devices, devices.c.id == device_id):
            raise ProblemError(
                401, "auth.invalid_device", "error.auth.invalid_device", title="Invalid device"
            )
        return {
            "staff": [{k: r[k] for k in ("id", "name", "role")} for r in await repo.select(staff)],
            "invalidate_on": ["staff.added"],
        }


@router.get("/v1/views/shift")
async def shift(request: Request, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(
            shifts, shifts.c.staff_id == session.actor_id, shifts.c.closed_at.is_(None)
        )
        return {
            "current": {k: v for k, v in rows[0].items() if k != "merchant_id"} if rows else None,
            "invalidate_on": ["staff.shift_opened", "staff.shift_closed"],
        }


@router.get("/v1/views/item/{item_id}")
async def item_view(request: Request, item_id: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return {
            **await get_item(Repository(conn, session.merchant_id), item_id),
            "invalidate_on": CATALOG_EVENTS,
        }
```

### backend/arth/api/governance.py

```python
"""Foundation endpoints; merchant and actor identity come from provisioned server sessions."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Request

from arth.api.problems import ProblemError
from arth.contracts.approval import ApprovalRequest
from arth.contracts.command import CommandRequest
from arth.governance.audit import verify_audit
from arth.governance.commands import CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository

router = APIRouter()


async def require_session(request: Request) -> Session:
    authorization = request.headers.get("authorization", "")
    session = (
        request.app.state.sessions.get(authorization.removeprefix("Bearer "))
        if authorization.startswith("Bearer ")
        else None
    )
    if session is None and authorization.startswith("Bearer ") and hasattr(request.app.state, "staff"):
        try:
            session = await request.app.state.staff.resolve(authorization.removeprefix("Bearer "))
        except CommandError:
            session = None
    if session is None:
        raise ProblemError(401, "auth.missing_session", "error.auth.missing_session", title="Unauthorized")
    return session


def problem(exc: CommandError) -> ProblemError:
    return ProblemError(409, str(exc), "error." + str(exc), title="Command refused")


@router.post("/v1/commands")
async def submit_command(
    request: Request,
    body: CommandRequest,
    session: Annotated[Session, Depends(require_session)],
    idempotency_key: Annotated[str, Header(min_length=1, max_length=200)],
) -> dict[str, Any]:
    try:
        return await request.app.state.commands.submit(session, body.type, body.payload, idempotency_key)
    except CommandError as exc:
        raise problem(exc) from exc


@router.post("/v1/approvals/{thread_id}")
async def decide_approval(
    request: Request,
    thread_id: str,
    body: ApprovalRequest,
    session: Annotated[Session, Depends(require_session)],
    idempotency_key: Annotated[str, Header(min_length=1, max_length=200)],
) -> dict[str, Any]:
    try:
        return await request.app.state.commands.decide(
            session,
            thread_id,
            body.decision.value,
            idempotency_key,
            decisions={key: value.value for key, value in (body.decisions or {}).items()},
            edits=body.edits,
        )
    except CommandError as exc:
        raise problem(exc) from exc


@router.get("/v1/audit/verify")
async def verify(request: Request, session: Annotated[Session, Depends(require_session)]) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await verify_audit(Repository(conn, session.merchant_id))
```

### backend/arth/api/problems.py

```python
"""RFC 9457 problem responses with a stable code and an i18n message key (spec Part C1)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from arth.governance.commands import CommandError

ParamValue = str | int | float | bool


class ProblemError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message_key: str,
        *,
        title: str,
        detail: str | None = None,
        params: dict[str, ParamValue] | None = None,
    ) -> None:
        super().__init__(f"{status} {code}")
        self.status, self.code, self.message_key = status, code, message_key
        self.title, self.detail, self.params = title, detail, params or {}


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(CommandError)
    async def _command_error(_request: Request, exc: CommandError) -> JSONResponse:
        code = str(exc)
        return JSONResponse(
            {
                "type": "https://arth.local/problems/" + code,
                "title": "Command refused",
                "status": 409,
                "code": code,
                "message_key": "error." + code,
            },
            status_code=409,
            media_type="application/problem+json",
        )

    @app.exception_handler(ProblemError)
    async def _handle(_request: Request, exc: ProblemError) -> JSONResponse:
        body: dict[str, object] = {
            "type": f"https://arth.local/problems/{exc.code}",
            "title": exc.title,
            "status": exc.status,
            "code": exc.code,
            "message_key": exc.message_key,
        }
        if exc.detail:
            body["detail"] = exc.detail
        if exc.params:
            body["params"] = exc.params
        return JSONResponse(body, status_code=exc.status, media_type="application/problem+json")
```

### backend/arth/main.py

```python
"""App factory: validates config, migrates the DB, wires clock, scheduler and spans, mounts routers.

Startup order: config checks -> migrate -> open DB -> scheduler.recover() (re-queue jobs a crash left
`running`) -> start the span persister -> tick loop. Shutdown runs in reverse: stop the tick loop,
flush and stop the span persister (outside any db.write()), close the DB.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from arth.api import commerce, director, governance, health, stream
from arth.api.problems import install_problem_handlers
from arth.core.calendar import CalendarIndex, load_calendar
from arth.core.clock import SimClock
from arth.core.config import (
    Settings,
    check_auth_tokens,
    check_provider_keys,
    load_policies,
    load_providers,
)
from arth.core.db import Database
from arth.core.migrate import upgrade
from arth.core.packs import PackRegistry
from arth.core.scheduler import Scheduler, tick_loop
from arth.core.spans import SpanBus
from arth.domains.catalog import register_catalog
from arth.domains.merchants import register_merchants
from arth.domains.security import load_signing_key
from arth.domains.staff import StaffService
from arth.governance.commands import CommandBus
from arth.governance.events import Dispatcher
from arth.governance.policy import PolicyEngine
from arth.governance.repository import Repository


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        check_auth_tokens(settings)  # prod refuses the dev-* default tokens
        policies = load_policies(settings.config_dir / "policies.yaml")
        app.state.providers = load_providers(settings.config_dir / "providers.yaml")
        check_provider_keys(settings, app.state.providers)
        app.state.calendar = CalendarIndex(load_calendar(settings.config_dir / "calendar"))
        app.state.packs = PackRegistry.load(settings.packs_dir, policies)
        app.state.policies = policies
        upgrade(settings.db_path)
        db = Database(settings.db_path)
        await db.open()
        clock = SimClock(settings.clock_start)
        app.state.db, app.state.clock = db, clock
        scheduler = Scheduler(db, clock)
        await scheduler.recover()
        app.state.scheduler = scheduler
        spans = SpanBus(clock, db)
        await spans.start()
        app.state.spans = spans
        app.state.commands = CommandBus(db, clock, PolicyEngine(policies, clock))
        app.state.commands.packs = app.state.packs
        register_merchants(app.state.commands, app.state.packs)
        signing_key = settings.session_signing_key or load_signing_key(
            settings.data_dir / "session-signing.key"
        )
        app.state.staff = StaffService(app.state.commands, signing_key.get_secret_value())
        register_catalog(app.state.commands, app.state.packs)
        async with db.read() as conn:
            app.state.commands.merchant_ids = await Repository.merchant_directory(conn)
        app.state.events = Dispatcher(db, clock)
        app.state.events.declare_view("trust", {"command.executed", "approval.decided"})
        app.state.events.declare_view("gates", {"approval.requested", "approval.decided"})
        for name, topics in {
            "settings/language": {"i18n.changed"},
            "onboarding": {"onboarding.started", "onboarding.updated"},
            "settings/staff": {"staff.added"},
            "staff/login": {"staff.added"},
            "shift": {"staff.shift_opened", "staff.shift_closed"},
            "catalog": {"catalog.item_added", "catalog.price_changed"},
        }.items():
            app.state.events.declare_view(name, topics)
        stop = asyncio.Event()
        ticker = asyncio.create_task(tick_loop(scheduler, stop, settings.tick_interval_s))

        async def dispatch_loop() -> None:
            while not stop.is_set():
                for merchant_id in {
                    s.merchant_id for s in app.state.sessions.values()
                } | app.state.commands.merchant_ids:
                    try:
                        await app.state.commands.run_due(merchant_id)
                        await app.state.events.dispatch(merchant_id)
                    except Exception:
                        logging.getLogger(__name__).exception("governance delivery failed; retrying")
                try:
                    await asyncio.wait_for(stop.wait(), min(settings.tick_interval_s, 0.05))
                except TimeoutError:
                    pass

        dispatcher_task = asyncio.create_task(dispatch_loop())
        try:
            yield
        finally:
            stop.set()
            await ticker
            await dispatcher_task
            await spans.aclose()
            await db.close()

    app = FastAPI(title="Arth API", version="0.1.0", lifespan=lifespan)
    app.state.settings = settings
    # Provisioned by the trusted session service (staff login arrives in T1.8).
    app.state.sessions = {}
    app.add_middleware(
        CORSMiddleware, allow_origins=settings.cors_origins, allow_methods=["*"], allow_headers=["*"]
    )
    install_problem_handlers(app)
    app.include_router(health.router)
    app.include_router(stream.router)
    app.include_router(director.router)
    app.include_router(governance.router)
    app.include_router(commerce.router)
    return app


app = create_app()
```

### backend/arth/core/config.py

```python
"""Settings and secrets from the environment, plus validated YAML config: policies, providers, calendar.

An invalid config file stops the app at boot with the file name in the error. API keys are read only here,
as SecretStr, from backend/.env; they never reach the web app, logs, spans or prompts (spec Part G0).
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from arth.core.clock import IST
from arth.core.paths import BACKEND_DIR, CONFIG_DIR, DATA_DIR, PACKS_DIR
from arth.core.yamlconf import ConfigError, Strict, validate

Tier = Literal["R0", "R1", "R2", "R3", "R4"]
Mode = Literal["dev", "test", "demo", "prod"]
HHMM = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
TOKEN_ENVS = {
    "ARTH_DIRECTOR_TOKEN": "director_token",
    "ARTH_DEVICE_TOKEN": "device_token",
    "ARTH_CONSOLE_TOKEN": "console_token",
}
KEY_ENVS = ("MISTRAL_API_KEY", "GROQ_API_KEY", "SARVAM_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY")


# ---- settings and secrets ------------------------------------------------------------------


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="ARTH_", env_file=BACKEND_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    mode: Mode = "dev"
    data_dir: Path = DATA_DIR
    config_dir: Path = CONFIG_DIR
    packs_dir: Path = PACKS_DIR
    clock_start: datetime = datetime(2026, 10, 29, 7, 45, tzinfo=IST)
    director_token: SecretStr = SecretStr("dev-director")
    device_token: SecretStr = SecretStr("dev-device")
    console_token: SecretStr = SecretStr("dev-console")
    session_signing_key: SecretStr | None = None
    cors_origins: list[str] = ["http://localhost:3000"]
    tick_interval_s: float = 1.0

    mistral_api_key: SecretStr | None = Field(default=None, validation_alias="MISTRAL_API_KEY")
    groq_api_key: SecretStr | None = Field(default=None, validation_alias="GROQ_API_KEY")
    sarvam_api_key: SecretStr | None = Field(default=None, validation_alias="SARVAM_API_KEY")
    langfuse_public_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: SecretStr | None = Field(default=None, validation_alias="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", validation_alias="LANGFUSE_HOST")

    @field_validator(
        "mistral_api_key",
        "groq_api_key",
        "sarvam_api_key",
        "langfuse_public_key",
        "langfuse_secret_key",
        mode="before",
    )
    @classmethod
    def _blank_is_unset(cls, value: object) -> object:
        return None if isinstance(value, str) and not value.strip() else value

    @property
    def db_path(self) -> Path:
        return self.data_dir / "arth.db"

    def secret(self, env_name: str) -> SecretStr | None:
        secrets = {
            "MISTRAL_API_KEY": self.mistral_api_key,
            "GROQ_API_KEY": self.groq_api_key,
            "SARVAM_API_KEY": self.sarvam_api_key,
            "LANGFUSE_PUBLIC_KEY": self.langfuse_public_key,
            "LANGFUSE_SECRET_KEY": self.langfuse_secret_key,
        }
        if env_name not in secrets:
            raise ConfigError(f"unknown secret {env_name!r}")
        return secrets[env_name]


def check_auth_tokens(settings: Settings) -> None:
    """In prod the dev-* default surface tokens are refused. Messages name env vars, never values."""
    weak = sorted(
        env
        for env, attr in TOKEN_ENVS.items()
        if getattr(settings, attr).get_secret_value().startswith("dev-")
    )
    if weak and settings.mode == "prod":
        raise ConfigError(f"prod refuses the default dev-* auth tokens; set {', '.join(weak)}")


# ---- policies.yaml -------------------------------------------------------------------------


class Role(Strict):
    max_tier: Tier
    approve: list[Tier] = []
    allow: list[str] = []


class QuietHours(Strict):
    start: str
    end: str

    @field_validator("start", "end")
    @classmethod
    def _hhmm(cls, value: str) -> str:
        if not HHMM.match(value):
            raise ValueError(f"time {value!r} must be HH:MM, 24-hour (e.g. '21:30')")
        return value


class ContactCaps(Strict):
    marketing_per_patron_per_week: int = Field(ge=0)


class Reminders(Strict):
    per_patron_per_week: int = Field(ge=0)
    cadence_days: list[int]


class Growth(Strict):
    holdout_share: float = Field(ge=0, le=1)
    holdout_min: int = Field(ge=0)
    margin_floor: float = Field(ge=0, le=1)
    monthly_incentive_budget_paise: int = Field(ge=0)


class DiscreetMode(Strict):
    busy_hours: list[str]


class Attention(Strict):
    proactive_per_day: int = Field(ge=0)
    urgent_interrupts_per_day: int = Field(ge=0)


class Policies(Strict):
    tiers: dict[str, Tier]
    roles: dict[str, Role]
    quiet_hours: QuietHours
    contact_caps: ContactCaps
    reminders: Reminders
    growth: Growth
    expiry_alert_days: dict[str, int]
    discreet_mode: DiscreetMode
    attention: Attention
    forbid_offers_on_flags: list[str] = []

    @model_validator(mode="after")
    def _owner_is_top(self) -> Policies:
        owner = self.roles.get("owner")
        if owner is None or owner.max_tier != "R4":
            raise ValueError("an 'owner' role with max_tier R4 is required")
        return self


# ---- providers.yaml ------------------------------------------------------------------------

DataTag = Literal["merchant_ok_if_paid_plan", "synthetic_only", "synthetic_only_on_free_tier"]
REQUIRED_ROLES = {"llm.fast", "llm.large", "vision", "ocr", "stt", "tts", "translate", "guard", "persona"}


class Hop(Strict):
    provider: str
    model: str | None = None
    timeout_ms: int | None = Field(default=None, gt=0)
    json_mode: bool = Field(default=False, alias="json")
    langs: list[str] | None = None


class RoleChain(Strict):
    chain: list[Hop] = Field(min_length=1)


class Provider(Strict):
    api_key_env: str
    data_tag: DataTag
    rate: dict[str, int] = {}

    @field_validator("api_key_env")
    @classmethod
    def _known_env(cls, value: str) -> str:
        if value not in KEY_ENVS:
            raise ValueError(f"api_key_env {value!r} is not one of {', '.join(KEY_ENVS)}")
        return value


class Providers(Strict):
    roles: dict[str, RoleChain]
    providers: dict[str, Provider]

    @model_validator(mode="after")
    def _chains_are_resolvable(self) -> Providers:
        missing = REQUIRED_ROLES - self.roles.keys()
        if missing:
            raise ValueError(f"missing roles: {sorted(missing)}")
        for role, chain in self.roles.items():
            for hop in chain.chain:
                if hop.provider != "cassette" and hop.provider not in self.providers:
                    raise ValueError(f"role {role!r} uses unknown provider {hop.provider!r}")
                if hop.provider != "cassette" and not hop.model:
                    raise ValueError(f"role {role!r}: provider {hop.provider!r} needs a model id")
        return self

    def used(self) -> set[str]:
        return {
            hop.provider for chain in self.roles.values() for hop in chain.chain if hop.provider != "cassette"
        }


def provider_status(settings: Settings, providers: Providers) -> dict[str, bool]:
    """Which providers have a key configured. Values are booleans only, never the key."""
    return {
        name: settings.secret(p.api_key_env) is not None for name, p in sorted(providers.providers.items())
    }


def check_provider_keys(settings: Settings, providers: Providers) -> None:
    missing = sorted(
        providers.providers[name].api_key_env
        for name in providers.used()
        if settings.secret(providers.providers[name].api_key_env) is None
    )
    if missing and settings.mode == "prod":
        raise ConfigError(f"missing API keys in .env for prod: {', '.join(missing)}")


# ---- loaders -------------------------------------------------------------------------------


def load_policies(path: Path) -> Policies:
    return validate(Policies, path)


def load_providers(path: Path) -> Providers:
    return validate(Providers, path)
```

### backend/arth/governance/commands.py

```python
"""Typed command pipeline with durable replay and transactional side effects."""

import json
from collections.abc import Awaitable, Callable
from dataclasses import asdict
from datetime import timedelta
from typing import Any

from jsonschema import Draft7Validator

from arth.core.clock import SimClock, iso_utc
from arth.core.config import QuietHours, Tier
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.packs import PackRegistry
from arth.core.schemas import validator as contract_validator
from arth.governance.approvals import can_approve, create_gate, envelope, scope_hash
from arth.governance.audit import append_audit, canonical
from arth.governance.events import emit_event
from arth.governance.policy import Decision, PolicyContext, PolicyEngine, Session
from arth.governance.repository import Repository
from arth.governance.tables import approvals, commands, merchant_settings, merchants

Handler = Callable[[Repository, dict[str, Any]], Awaitable[dict[str, Any]]]
Context = Callable[[Repository, dict[str, Any]], Awaitable[PolicyContext]]


class CommandError(ValueError):
    pass


class CommandBus:
    def __init__(self, db: Database, clock: SimClock, policy: PolicyEngine) -> None:
        self.db, self.clock, self.policy = db, clock, policy
        self.packs: PackRegistry | None = None
        self.session_validator: Callable[[Repository, Session], Awaitable[None]] | None = None
        self.registry: dict[str, tuple[Draft7Validator, Handler, Context | None]] = {}
        self.merchant_ids: set[str] = set()

    def register(
        self, kind: str, schema: dict[str, Any], handler: Handler, context: Context | None = None
    ) -> None:
        Draft7Validator.check_schema(schema)
        contract_id = schema.get("$id", "")
        compiled = (
            contract_validator(contract_id.rsplit("/", 1)[1].removesuffix(".schema.json"))
            if contract_id.startswith("https://arth.local/contracts/")
            else Draft7Validator(schema)
        )
        self.registry[kind] = (compiled, handler, context)

    def _validate(self, kind: str, payload: dict[str, Any]) -> Tier:
        if kind not in self.registry or kind not in self.policy.policies.tiers:
            raise CommandError("command.unknown_type")
        if "merchant_id" in payload:
            raise CommandError("command.tenant_in_body")
        canonical(payload)
        if not self.registry[kind][0].is_valid(payload):
            raise CommandError("command.invalid_payload")
        return self.policy.policies.tiers[kind]

    async def _check(
        self, repo: Repository, session: Session, kind: str, tier: Tier, payload: dict[str, Any]
    ) -> Decision:
        if self.session_validator is not None:
            await self.session_validator(repo, session)
        provider = self.registry[kind][2]
        context = await provider(repo, payload) if provider else PolicyContext()
        policy = self.policy
        if self.packs is not None:
            shops = await repo.select(merchants)
            if not shops and not (kind == "merchant.bootstrap" and repo.private.get("bootstrap")):
                raise CommandError("command.merchant_not_found")
            if shops:
                policy = PolicyEngine(self.packs.policies_for(shops[0]["pack"]), self.clock)
        settings = await repo.select(merchant_settings)
        if settings:
            quiet = json.loads(settings[0]["settings"]).get("quiet_hours")
            if quiet:
                merged = policy.policies.model_copy(update={"quiet_hours": QuietHours.model_validate(quiet)})
                policy = PolicyEngine(merged, self.clock)
        decision = policy.evaluate(kind, tier, session, context)
        if decision.code != "allow":
            raise CommandError(decision.code)
        return decision

    async def submit(
        self,
        session: Session,
        kind: str,
        payload: dict[str, Any],
        key: str,
        conditions: dict[str, Any] | None = None,
        *,
        private: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        tier = self._validate(kind, payload)
        self.merchant_ids.add(session.merchant_id)
        if not key or len(key) > 200:
            raise CommandError("command.idempotency_key")
        conditions = conditions or {}
        hashed = scope_hash(kind, payload, conditions)
        async with self.db.write() as conn:
            repo = Repository(conn, session.merchant_id, session=session, private=private)
            previous = await repo.select(commands, commands.c.idempotency_key == key)
            if previous:
                if previous[0]["scope_hash"] != hashed:
                    raise CommandError("command.idempotency_conflict")
                return json.loads(previous[0]["result"])
            await self._check(repo, session, kind, tier, payload)
            command_id = new_id("cmd")
            await repo.insert(
                commands,
                {
                    "id": command_id,
                    "idempotency_key": key,
                    "type": kind,
                    "scope_hash": hashed,
                    "tier": tier,
                    "status": "pending",
                    "payload": canonical(payload),
                },
            )
            if tier in {"R2", "R3"}:
                if private:
                    raise CommandError("command.private_context_requires_r1")
                result = await create_gate(
                    repo,
                    self.clock,
                    command_id,
                    tier,
                    {"session": asdict(session), "type": kind, "payload": payload},
                    conditions,
                    hashed,
                )
                settings = await repo.select(merchant_settings)
                if settings:
                    languages = json.loads(settings[0]["settings"])
                    result["envelope"]["lang"] = {
                        "screen": languages.get("screen_lang", "hi-Latn"),
                        "speech": languages.get("speech_lang", "hi-IN"),
                    }
                await append_audit(repo, self.clock, command_id, "approval.requested", result)
                await emit_event(repo, self.clock, session, "approval.requested", command_id, result)
                await self._store(repo, command_id, result)
                return result
            return await self._execute(repo, session, command_id, kind, payload, tier)

    async def _store(self, repo: Repository, command_id: str, result: dict[str, Any]) -> None:
        await repo.update(
            commands, {"status": result["status"], "result": canonical(result)}, commands.c.id == command_id
        )

    async def _execute(
        self,
        repo: Repository,
        session: Session,
        command_id: str,
        kind: str,
        payload: dict[str, Any],
        tier: Tier,
    ) -> dict[str, Any]:
        self._validate(kind, payload)
        repo.session, repo.command_id = session, command_id
        decision = await self._check(repo, session, kind, tier, payload)
        data = await self.registry[kind][1](repo, payload)
        result: dict[str, Any] = {
            "command_id": command_id,
            "status": "executed",
            "tier": tier,
            "data": data,
            "envelope": {
                "turn_id": new_id("turn"),
                "cards": [],
                "tier": tier,
                "lang": {"screen": "hi-Latn", "speech": "hi-IN"},
                "audience": "owner",
                "followups": [],
                "provenance": [],
                "presence": {"state": "done"},
                "sensitivity": "discreet" if decision.discreet else "normal",
            },
        }
        settings = await repo.select(merchant_settings)
        if settings:
            languages = json.loads(settings[0]["settings"])
            result["envelope"]["lang"] = {
                "screen": languages.get("screen_lang", "hi-Latn"),
                "speech": languages.get("speech_lang", "hi-IN"),
            }
        await append_audit(
            repo, self.clock, command_id, "command.executed", {"result": result, "session": asdict(session)}
        )
        await emit_event(repo, self.clock, session, "command.executed", command_id, result)
        await self._store(repo, command_id, result)
        return result

    async def batch(self, session: Session, gate_ids: list[str], *, mode: str = "batch") -> str:
        if (
            mode not in {"batch", "series", "plan"}
            or not 1 <= len(gate_ids) <= 5
            or len(set(gate_ids)) != len(gate_ids)
        ):
            raise CommandError("approval.invalid_batch")
        thread_id = new_id("thread")
        async with self.db.write() as conn:
            repo = Repository(conn, session.merchant_id)
            for gate_id in gate_ids:
                rows = await repo.select(
                    approvals, approvals.c.id == gate_id, approvals.c.status == "pending"
                )
                if not rows:
                    raise CommandError("approval.not_found")
                scope = json.loads(rows[0]["scope"])
                scope["mode"] = mode
                await repo.update(
                    approvals, {"thread_id": thread_id, "scope": canonical(scope)}, approvals.c.id == gate_id
                )
        return thread_id

    async def decide(
        self,
        session: Session,
        thread_id: str,
        decision: str,
        key: str,
        *,
        decisions: dict[str, str] | None = None,
        edits: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if decision not in {"approve", "snooze", "edit"} or not key:
            raise CommandError("approval.invalid_decision")
        async with self.db.write() as conn:
            repo = Repository(conn, session.merchant_id)
            gates = await repo.select(approvals, approvals.c.thread_id == thread_id)
            if not gates:
                raise CommandError("approval.not_found")
            if decisions and set(decisions) - {g["id"] for g in gates}:
                raise CommandError("approval.invalid_partial")
            if edits is not None and len(gates) != 1:
                raise CommandError("approval.edit_single_gate")
            results = []
            for gate in gates:
                results.append(
                    await self._decide_gate(
                        repo, session, gate, (decisions or {}).get(gate["id"], decision), key, edits
                    )
                )
            return results[0] if len(results) == 1 else {"items": results}

    async def _decide_gate(
        self,
        repo: Repository,
        session: Session,
        gate: dict[str, Any],
        decision: str,
        key: str,
        edits: dict[str, Any] | None,
    ) -> dict[str, Any]:
        role = self.policy.policies.roles.get(session.role)
        if self.session_validator is not None:
            await self.session_validator(repo, session)
        if role is None or not can_approve(session, gate["tier"], list(role.approve)):
            raise CommandError("approval.cannot_approve")
        scope = json.loads(gate["scope"])
        history = scope.setdefault("decisions", {})
        fingerprint = canonical({"decision": decision, "edits": edits})
        if key in history:
            if history[key]["fingerprint"] != fingerprint:
                raise CommandError("approval.idempotency_conflict")
            return history[key]["result"]
        if gate["expires_at"] <= iso_utc(self.clock.now()):
            raise CommandError("approval.expired")
        if gate["status"] not in {"pending", "snoozed"} and not (
            gate["status"] == "queued" and decision == "snooze"
        ):
            raise CommandError("approval.already_decided")
        conditions = json.loads(gate["conditions"])
        if gate["scope_hash"] != scope_hash(scope["type"], scope["payload"], conditions):
            raise CommandError("approval.scope_mismatch")
        due = iso_utc(self.clock.now() + timedelta(seconds=30))
        if decision == "edit":
            if edits is None:
                raise CommandError("approval.edits_required")
            payload = {**scope["payload"], **edits}
            self._validate(scope["type"], payload)
            scope = {**scope, "payload": payload, "decisions": {}}
            hashed = scope_hash(scope["type"], payload, conditions)
            result = await create_gate(
                repo, self.clock, gate["command_id"], gate["tier"], scope, conditions, hashed
            )
            await repo.update(
                commands,
                {"payload": canonical(payload), "scope_hash": hashed},
                commands.c.id == gate["command_id"],
            )
            status = "superseded"
        elif decision == "snooze":
            result = {"command_id": gate["command_id"], "status": "snoozed"}
            status = "snoozed"
        elif decision == "approve":
            if gate["tier"] == "R3":
                result = {"command_id": gate["command_id"], "status": "queued", "due_at": due}
            else:
                if not await self._conditions(repo, scope, conditions):
                    raise CommandError("approval.conditions_failed")
                result = await self._execute(
                    repo, session, gate["command_id"], scope["type"], scope["payload"], gate["tier"]
                )
            status = result["status"]
        else:
            raise CommandError("approval.invalid_decision")
        result.setdefault("envelope", envelope(gate["tier"]))
        history[key] = {"fingerprint": fingerprint, "result": result}
        scope["decisions"] = history
        await repo.update(
            approvals,
            {
                "status": status,
                "approved_by": session.actor_id,
                "due_at": due if status == "queued" else None,
                "scope": canonical(scope),
            },
            approvals.c.id == gate["id"],
        )
        await self._store(repo, gate["command_id"], result)
        await append_audit(repo, self.clock, gate["command_id"], "approval.decided", result)
        await emit_event(repo, self.clock, session, "approval.decided", gate["command_id"], result)
        return result

    async def _conditions(self, repo: Repository, scope: dict[str, Any], conditions: dict[str, Any]) -> bool:
        if not conditions:
            return True
        provider = self.registry[scope["type"]][2]
        if provider is None:
            return False
        facts = (await provider(repo, scope["payload"])).facts
        for field, comparison in conditions.items():
            if field not in facts or not isinstance(comparison, dict) or not comparison:
                return False
            for operator, bound in comparison.items():
                value = facts[field]
                if operator == "eq":
                    if type(value) is not type(bound) or value != bound:
                        return False
                elif operator == "lte":
                    if type(value) is not int or type(bound) is not int or value > bound:
                        return False
                else:
                    return False
        return True

    async def run_due(self, merchant_id: str) -> int:
        count = 0
        async with self.db.write() as conn:
            repo = Repository(conn, merchant_id)
            for gate in await repo.select(
                approvals, approvals.c.status == "queued", approvals.c.due_at <= iso_utc(self.clock.now())
            ):
                scope = json.loads(gate["scope"])
                conditions = json.loads(gate["conditions"])
                session = Session(**scope["session"])
                if gate["scope_hash"] != scope_hash(
                    scope["type"], scope["payload"], conditions
                ) or not await self._conditions(repo, scope, conditions):
                    # Fresh scope records the changed trusted facts; the old consent is never stretched.
                    provider = self.registry[scope["type"]][2]
                    facts = (await provider(repo, scope["payload"])).facts if provider else {}
                    fresh_conditions = {
                        field: {"eq": facts[field]} if field in facts else comparison
                        for field, comparison in conditions.items()
                    }
                    result = await create_gate(
                        repo,
                        self.clock,
                        gate["command_id"],
                        gate["tier"],
                        scope,
                        fresh_conditions,
                        scope_hash(scope["type"], scope["payload"], fresh_conditions),
                    )
                    await repo.update(approvals, {"status": "superseded"}, approvals.c.id == gate["id"])
                    await self._store(repo, gate["command_id"], result)
                    await append_audit(repo, self.clock, gate["command_id"], "approval.scope_changed", result)
                    await emit_event(
                        repo, self.clock, session, "approval.requested", gate["command_id"], result
                    )
                    continue
                await self._execute(
                    repo, session, gate["command_id"], scope["type"], scope["payload"], gate["tier"]
                )
                await repo.update(approvals, {"status": "executed"}, approvals.c.id == gate["id"])
                count += 1
        return count
```

### backend/arth/governance/repository.py

```python
"""Only scoped table operations are exposed to domain handlers."""

from typing import Any

from sqlalchemy import Table, insert, select, text, update
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.sql.elements import ColumnElement

from arth.governance.policy import Session
from arth.governance.tables import merchants


class Repository:
    @staticmethod
    async def merchant_directory(conn: AsyncConnection) -> set[str]:
        """Startup control-plane inventory: tenant IDs only, never business rows or an HTTP API."""
        rows = await conn.execute(
            select(merchants.c.merchant_id).where(merchants.c.id == merchants.c.merchant_id)
        )
        return {str(identity) for identity in rows.scalars()}

    def __init__(
        self,
        conn: AsyncConnection,
        merchant_id: str,
        *,
        session: Session | None = None,
        private: dict[str, Any] | None = None,
    ) -> None:
        if not merchant_id:
            raise ValueError("merchant_id required")
        self.conn, self.merchant_id = conn, merchant_id
        self.session, self.private = session, private or {}
        self.command_id: str | None = None

    def _scope(self, table: Table) -> ColumnElement[bool]:
        if "merchant_id" not in table.c:
            raise ValueError("unscoped table")
        return table.c.merchant_id == self.merchant_id

    def _values(self, values: dict[str, Any]) -> dict[str, Any]:
        if "merchant_id" in values and values["merchant_id"] != self.merchant_id:
            raise ValueError("tenant override")
        return {**values, "merchant_id": self.merchant_id}

    async def select(self, table: Table, *where: ColumnElement[bool]) -> list[dict[str, Any]]:
        rows = await self.conn.execute(select(table).where(self._scope(table), *where))
        return [dict(row) for row in rows.mappings()]

    async def insert(self, table: Table, values: dict[str, Any]) -> None:
        self._scope(table)
        await self.conn.execute(insert(table).values(**self._values(values)))

    async def update(self, table: Table, values: dict[str, Any], *where: ColumnElement[bool]) -> int:
        result = await self.conn.execute(
            update(table).where(self._scope(table), *where).values(**self._values(values))
        )
        return result.rowcount

    async def search_catalog(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        query = query.strip().lower()
        if not query:
            return []
        limit = min(max(limit, 1), 5)
        if len(query) >= 3:
            statement = text(
                "SELECT i.* FROM items AS i JOIN items_fts AS f "
                "ON i.id=f.id AND i.merchant_id=f.merchant_id "
                "WHERE i.merchant_id=:merchant_id AND f.merchant_id=:merchant_id "
                "AND items_fts MATCH :query ORDER BY rank, i.frequency DESC, i.id LIMIT :limit"
            )
            query = '"' + query.replace('"', '""') + '"'
        else:
            statement = text(
                "SELECT * FROM items WHERE merchant_id=:merchant_id "
                "AND instr(lower(search_text),:query)>0 ORDER BY frequency DESC,id LIMIT :limit"
            )
        rows = await self.conn.execute(
            statement, {"merchant_id": self.merchant_id, "query": query, "limit": limit}
        )
        return [dict(row) for row in rows.mappings()]
```

### backend/arth/governance/policy.py

```python
"""Deterministic governance on trusted session and domain facts."""

from dataclasses import dataclass, field

from arth.core.clock import SimClock
from arth.core.config import Policies, Tier


@dataclass(frozen=True)
class Session:
    merchant_id: str
    actor_id: str
    role: str
    channel: str = "device"
    device_id: str | None = None
    owner_ptt: bool = False
    step_up: bool = False
    session_id: str | None = None


@dataclass(frozen=True)
class PolicyContext:
    facts: dict[str, int | str | bool] = field(default_factory=dict)
    purpose: str | None = None
    consent: bool = False
    weekly_contacts: int = 0
    sensitive: bool = False
    message_class: str | None = None
    reply_age_seconds: int | None = None
    known_supplier: bool = False
    approved_template: bool = False
    margin: float | None = None
    spend_paise: int = 0
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    code: str = "allow"
    discreet: bool = False


class PolicyEngine:
    def __init__(self, policies: Policies, clock: SimClock) -> None:
        self.policies, self.clock = policies, clock

    def evaluate(
        self, kind: str, tier: Tier, session: Session, context: PolicyContext | None = None
    ) -> Decision:
        context = context or PolicyContext()
        role = self.policies.roles.get(session.role)
        if role is None or (tier > role.max_tier and kind not in role.allow):
            return Decision("policy.role")
        if tier == "R3" and session.role != "owner":
            return Decision("policy.owner_required")
        if tier == "R4" and (session.channel != "console" or not session.step_up):
            return Decision("policy.console_required")
        now = self.clock.now_ist().strftime("%H:%M")
        quiet = self.policies.quiet_hours

        def in_window(start: str, end: str) -> bool:
            return start <= now < end if start < end else now >= start or now < end

        if context.purpose:
            if not context.consent:
                return Decision("policy.consent")
            if in_window(quiet.start, quiet.end):
                return Decision("policy.quiet_hours")
            cap = (
                self.policies.contact_caps.marketing_per_patron_per_week
                if context.purpose == "marketing"
                else self.policies.reminders.per_patron_per_week
                if context.purpose == "reminders"
                else None
            )
            if cap is not None and context.weekly_contacts >= cap:
                return Decision("policy.contact_cap")
            if tier == "R1":
                valid = (
                    context.message_class in {"receipt", "offer_terms"}
                    or context.message_class == "reply"
                    and context.reply_age_seconds is not None
                    and 0 <= context.reply_age_seconds <= 600
                    or context.message_class == "rfq"
                    and context.known_supplier
                    and context.approved_template
                )
                if not valid:
                    return Decision("policy.message_class")
        if context.margin is not None and context.margin < self.policies.growth.margin_floor:
            return Decision("policy.margin_floor")
        if context.spend_paise > self.policies.growth.monthly_incentive_budget_paise:
            return Decision("policy.budget")
        if set(context.flags) & set(self.policies.forbid_offers_on_flags):
            return Decision("policy.pack")
        discreet = context.sensitive and any(
            in_window(*window.split("-")) for window in self.policies.discreet_mode.busy_hours
        )
        return Decision(discreet=discreet)
```

### backend/migrations/env.py

```python
from alembic import context
from sqlalchemy import engine_from_config, pool

# Every new table module must be imported here so its tables register on metadata;
# otherwise autogenerate and the schema-drift test will not see them.
import arth.core.tables  # noqa: F401  (registers L0 tables on metadata)
import arth.governance.tables  # noqa: F401
import arth.domains.tables  # noqa: F401
from arth.core.db import metadata

config = context.config
target_metadata = metadata


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}), prefix="sqlalchemy.", poolclass=pool.NullPool
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True, compare_type=True
        )
        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
```

### backend/migrations/versions/0003_identity_catalog.py

```python
"""L1b identity and catalog tables (all domain queries are merchant scoped)."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from sqlalchemy import MetaData
metadata = MetaData(naming_convention={
 'ix':'ix_%(table_name)s_%(column_0_name)s', 'uq':'uq_%(table_name)s_%(column_0_name)s',
 'fk':'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s', 'pk':'pk_%(table_name)s'})
def tenant():
    return Column('merchant_id',String,nullable=False,index=True)

devices = Table(
    "devices",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("edition", String, nullable=False),
    Column("capabilities", Text, nullable=False, server_default="{}"),
    CheckConstraint("json_valid(capabilities)"),
)
onboarding_progress = Table(
    "onboarding_progress",
    metadata,
    tenant(),
    Column("step", String, nullable=False),
    Column("completed_at", String, nullable=False),
    UniqueConstraint("merchant_id", "step"),
)
staff_credentials = Table(
    "staff_credentials",
    metadata,
    Column("staff_id", String, primary_key=True),
    tenant(),
    Column("pin_hash", Text, nullable=False),
    Column("failed", Integer, nullable=False, server_default="0"),
    Column("locked_until", String),
)
staff_sessions = Table(
    "staff_sessions",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("device_id", String, nullable=False),
    Column("channel", String, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("revoked", Integer, nullable=False, server_default="0"),
)
shifts = Table(
    "shifts",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("staff_id", String, nullable=False),
    Column("opened_at", String, nullable=False),
    Column("closed_at", String),
    Column("float_paise", Integer, nullable=False),
    Column("expected_paise", Integer, nullable=False),
    Column("counted_paise", Integer),
    Column("variance_paise", Integer),
    CheckConstraint("float_paise >= 0 AND expected_paise >= 0"),
)

items = Table('items',metadata,Column('id',String,primary_key=True),tenant(),Column('sku',String,nullable=False),
    Column('names',Text,nullable=False),Column('unit',String,nullable=False),Column('category',String,nullable=False),
    Column('mrp_paise',Integer,nullable=False),Column('price_paise',Integer,nullable=False),Column('cost_paise',Integer,nullable=False),
    Column('details',Text,nullable=False,server_default='{}'),Column('search_text',Text,nullable=False),
    Column('frequency',Integer,nullable=False,server_default='0'),UniqueConstraint('merchant_id','sku'),
    CheckConstraint('json_valid(names) AND json_valid(details)'),
    CheckConstraint('mrp_paise >= 0 AND price_paise >= 0 AND cost_paise >= 0'))
item_aliases=Table('item_aliases',metadata,Column('id',String,primary_key=True),tenant(),
    Column('item_id',String,nullable=False),Column('alias',String,nullable=False),UniqueConstraint('merchant_id','item_id','alias'))
item_barcodes=Table('item_barcodes',metadata,Column('id',String,primary_key=True),tenant(),
    Column('item_id',String,nullable=False),Column('barcode',String,nullable=False),UniqueConstraint('merchant_id','barcode'))
item_prices=Table('item_prices',metadata,Column('seq',Integer,primary_key=True),tenant(),
    Column('item_id',String,nullable=False),Column('price_paise',Integer,nullable=False),Column('effective_from',String,nullable=False),
    Column('command_id',String,nullable=False),CheckConstraint('price_paise >= 0'))
item_tax=Table('item_tax',metadata,Column('item_id',String,primary_key=True),tenant(),
    Column('hsn',String,nullable=False,server_default=''),Column('gst_rate_bp',Integer,nullable=False,server_default='0'),
    CheckConstraint('gst_rate_bp >= 0 AND gst_rate_bp <= 10000'))
modifier_groups=Table('modifier_groups',metadata,Column('id',String,primary_key=True),tenant(),Column('item_id',String,nullable=False),
    Column('name',String,nullable=False),Column('required',Integer,nullable=False))
modifiers=Table('modifiers',metadata,Column('id',String,primary_key=True),tenant(),Column('group_id',String,nullable=False),
    Column('name',String,nullable=False),Column('delta_paise',Integer,nullable=False))
recipes=Table('recipes',metadata,tenant(),Column('item_id',String,nullable=False),Column('ingredient_id',String,nullable=False),
    Column('qty_milli',Integer,nullable=False),UniqueConstraint('merchant_id','item_id','ingredient_id'),CheckConstraint('qty_milli > 0'))
services=Table('services',metadata,Column('item_id',String,primary_key=True),tenant(),
    Column('duration_minutes',Integer,nullable=False),Column('required_skill',String,nullable=False),CheckConstraint('duration_minutes > 0'))


from alembic import op
revision='0003'
down_revision='0002'
branch_labels=None
depends_on=None

def upgrade():
    metadata.create_all(op.get_bind())
    op.execute("CREATE VIRTUAL TABLE items_fts USING fts5(id UNINDEXED, merchant_id UNINDEXED, search_text, tokenize='trigram')")
    op.execute("CREATE TRIGGER items_fts_insert AFTER INSERT ON items BEGIN INSERT INTO items_fts(id,merchant_id,search_text) VALUES(new.id,new.merchant_id,new.search_text); END")
    op.execute("CREATE TRIGGER items_fts_update AFTER UPDATE OF search_text ON items BEGIN DELETE FROM items_fts WHERE id=old.id AND merchant_id=old.merchant_id; INSERT INTO items_fts(id,merchant_id,search_text) VALUES(new.id,new.merchant_id,new.search_text); END")
    op.execute("CREATE TRIGGER items_fts_delete AFTER DELETE ON items BEGIN DELETE FROM items_fts WHERE id=old.id AND merchant_id=old.merchant_id; END")

def downgrade():
    for name in ('items_fts_insert','items_fts_update','items_fts_delete'):
        op.execute('DROP TRIGGER '+name)
    op.execute('DROP TABLE items_fts')
    metadata.drop_all(op.get_bind())
```

### backend/config/policies.yaml

```yaml
tiers:
  merchant.bootstrap: R1
  merchant.update_settings: R1
  onboarding.complete_step: R1
  staff.add: R1
  staff.login: R1
  staff.logout: R1
  shift.open: R1
  shift.close: R1
  catalog.add_item: R1
  catalog.import_items: R1
  catalog.change_price: R2
  catalog.bulk_price: R4
  counter.add_lines: R1
  ledger.add_entry: R2
  supply.place_po: R3
  outreach.send_campaign: R3
  offers.create_program: R3
  treasury.refund: R4
  capital.apply: R4
  privacy.erase_patron: R4
roles:
  owner: { max_tier: R4, approve: [R2, R3] }
  manager: { max_tier: R2, approve: [R2] }
  cashier: { max_tier: R1, allow: [treasury.cash_payment] }
  helper: { max_tier: R1 }
quiet_hours: { start: '21:30', end: '08:00' }
contact_caps: { marketing_per_patron_per_week: 1 }
reminders: { per_patron_per_week: 1, cadence_days: [0, 7, 14] }
growth: { holdout_share: 0.2, holdout_min: 1, margin_floor: 0.15, monthly_incentive_budget_paise: 0 }
expiry_alert_days: { default: 30 }
discreet_mode: { busy_hours: ['09:00-11:00', '17:30-21:00'] }
attention: { proactive_per_day: 1, urgent_interrupts_per_day: 3 }
forbid_offers_on_flags: []
```

### backend/tests/l1b_helpers.py

```python
from arth.core.clock import SimClock
from arth.core.config import Settings, load_policies
from arth.core.packs import PackRegistry
from arth.core.paths import CONFIG_DIR, PACKS_DIR
from arth.governance.commands import CommandBus
from arth.governance.policy import PolicyEngine


def make_bus(db):
    from arth.domains.merchants import register_merchants

    policies = load_policies(CONFIG_DIR / "policies.yaml")
    clock = SimClock(Settings(_env_file=None).clock_start)
    packs = PackRegistry.load(PACKS_DIR, policies)
    bus = CommandBus(db, clock, PolicyEngine(policies, clock))
    bus.packs = packs
    register_merchants(bus, packs)
    return bus
```

### backend/tests/test_l1b_merchants.py

```python
import json

import pytest
from l1b_helpers import make_bus


async def test_independent_languages_owner_permissions_and_tenancy(db):
    from arth.domains.merchants import provision_shop, settings_view
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    bus = make_bus(db)
    shop = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="setup-a")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    result = await bus.submit(
        owner,
        "merchant.update_settings",
        {"screen_lang": "ta", "speech_lang": "hi-IN", "customer_lang": "en"},
        "languages",
    )
    assert result["envelope"]["lang"] == {"screen": "ta", "speech": "hi-IN"}
    async with db.read() as conn:
        settings = await settings_view(Repository(conn, owner.merchant_id))
        assert settings["customer_lang"] == "en"
        assert settings["marketing_consent_default"] is False
        with pytest.raises(CommandError):
            await settings_view(Repository(conn, "other"))
    with pytest.raises(CommandError):
        await bus.submit(
            Session(owner.merchant_id, "helper", "helper"),
            "merchant.update_settings",
            {"screen_lang": "en"},
            "bad",
        )
    with pytest.raises(CommandError):
        await bus.submit(owner, "merchant.update_settings", {"merchant_id": "other"}, "tenant")


async def test_ordered_onboarding_and_bootstrap_no_secret_persistence(db):
    from arth.domains.merchants import onboarding_view, provision_shop
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, outbox

    bus = make_bus(db)
    shop = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="same")
    replay = await provision_shop(bus, "A", "kirana", "Owner", "4826", "device-a", key="same")
    assert replay == shop
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner")
    with pytest.raises(CommandError, match="step_order"):
        await bus.submit(owner, "onboarding.complete_step", {"step": "details"}, "wrong")
    await bus.submit(owner, "onboarding.complete_step", {"step": "language"}, "first")
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert (await onboarding_view(repo))["completed"] == ["language"]
        dumped = json.dumps([await repo.select(t) for t in (commands, audit_log, outbox)])
        assert '"4826"' not in dumped and "scrypt$" not in dumped
        from arth.core.schemas import validator

        for row in await repo.select(outbox):
            event = json.loads(row["payload"])
            validator(event["type"].replace(".", "_")).validate(event)


async def test_details_step_requires_shop_payment_and_address_details(db):
    from arth.domains.merchants import provision_shop
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = make_bus(db)
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="details")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner")
    await bus.submit(owner, "onboarding.complete_step", {"step": "language"}, "language")
    await bus.submit(owner, "onboarding.complete_step", {"step": "pack"}, "pack")
    with pytest.raises(CommandError, match="details_required"):
        await bus.submit(owner, "onboarding.complete_step", {"step": "details"}, "complete-details")
```

### backend/tests/test_l1b_staff.py

```python
import json
from datetime import timedelta

import pytest
from l1b_helpers import make_bus


async def setup_staff(db):
    from arth.domains.merchants import provision_shop
    from arth.domains.staff import StaffService
    from arth.governance.policy import Session

    bus = make_bus(db)
    service = StaffService(bus, "synthetic-test-signing-key")
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="shop")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    credential = service.device_credential(shop["merchant_id"], shop["device_id"])
    return bus, service, shop, owner, credential


async def test_pin_session_restart_logout_and_no_credential_leak(db):
    from arth.domains.staff import StaffService
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, outbox

    bus, service, shop, owner, device = await setup_staff(db)
    result = await service.login(device, shop["owner_id"], "4826", "console", "login")
    session = await service.resolve(result["token"])
    assert session.role == "owner" and not session.owner_ptt and not session.step_up
    restarted = StaffService(bus, "synthetic-test-signing-key")
    assert (await restarted.resolve(result["token"])).actor_id == owner.actor_id
    with pytest.raises(CommandError):
        await service.login(device, shop["owner_id"], "1111", "console", "login")
    with pytest.raises(CommandError):
        await service.resolve(result["token"] + "x")
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        history = json.dumps([await repo.select(t) for t in (commands, audit_log, outbox)])
        assert '"4826"' not in history and result["token"] not in history and "scrypt$" not in history
    await bus.submit(session, "staff.logout", {}, "logout")
    with pytest.raises(CommandError, match="session"):
        await restarted.resolve(result["token"])


async def test_lockout_expiry_helper_and_shift_variance(db):
    from arth.governance.commands import CommandError

    bus, service, shop, owner, device = await setup_staff(db)
    helper = (await service.add(owner, "Helper", "helper", "6194", "new-helper"))["data"]["staff_id"]
    for n in range(5):
        with pytest.raises(CommandError):
            await service.login(device, helper, "1111", "device", f"bad{n}")
    with pytest.raises(CommandError, match="locked"):
        await service.login(device, helper, "6194", "device", "locked")
    bus.clock.set(bus.clock.now() + timedelta(minutes=5))
    token = (await service.login(device, helper, "6194", "device", "helper-login"))["token"]
    session = await service.resolve(token)
    with pytest.raises(CommandError):
        await service.add(session, "Evil owner", "owner", "4826", "escalate")
    opened = await bus.submit(session, "shift.open", {"float_paise": 200000}, "open")
    shift_id = opened["data"]["shift_id"]
    with pytest.raises(CommandError, match="shift"):
        await bus.submit(owner, "shift.close", {"shift_id": shift_id, "counted_paise": 195000}, "other-close")
    closed = await bus.submit(
        session, "shift.close", {"shift_id": shift_id, "counted_paise": 195000}, "close"
    )
    assert closed["data"]["variance_paise"] == -5000
    assert closed["data"]["staff_id"] == helper
    bus.clock.set(bus.clock.now() + timedelta(hours=12))
    with pytest.raises(CommandError, match="session"):
        await service.resolve(token)
```

### backend/tests/test_l1b_catalog.py

```python
import json
from time import perf_counter

import pytest
from l1b_helpers import make_bus

from arth.core.paths import CONTRACTS_DIR


def item():
    return json.loads((CONTRACTS_DIR / "examples/catalog_add_item.example.json").read_text(encoding="utf-8"))


async def setup_catalog(db):
    from arth.domains.catalog import register_catalog
    from arth.domains.merchants import provision_shop
    from arth.governance.policy import Session

    bus = make_bus(db)
    register_catalog(bus, bus.packs)
    shop = await provision_shop(bus, "Shop", "kirana", "Owner", "4826", "device-a", key="catalog-shop")
    owner = Session(shop["merchant_id"], shop["owner_id"], "owner", channel="console")
    return bus, owner


async def test_catalog_import_is_confirmed_atomic_and_search_is_scoped(db):
    from arth.domains.catalog import catalog_rows
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    with pytest.raises(CommandError):
        await bus.submit(owner, "catalog.import_items", {"confirmed": False, "items": [item()]}, "unreviewed")
    added = await bus.submit(owner, "catalog.add_item", item(), "add")
    identity = added["data"]["item_id"]
    bad = {**item(), "sku": "OTHER-SALT"}
    with pytest.raises(CommandError, match="barcode"):
        await bus.submit(
            owner,
            "catalog.import_items",
            {"confirmed": True, "items": [{**item(), "sku": "NEW", "barcodes": []}, bad]},
            "collision",
        )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert len(await catalog_rows(repo)) == 1
        start = perf_counter()
        results = await repo.search_catalog("टाटा")
        assert perf_counter() - start < 0.05
        assert [r["id"] for r in results] == [identity]
        assert await Repository(conn, "other").search_catalog("टाटा") == []


async def test_price_history_r2_and_r4_are_enforced(db):
    from arth.domains.catalog import catalog_rows
    from arth.domains.tables import item_prices
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    identity = (await bus.submit(owner, "catalog.add_item", item(), "add"))["data"]["item_id"]
    gate = await bus.submit(
        owner, "catalog.change_price", {"item_id": identity, "price_paise": 2600}, "price"
    )
    assert gate["status"] == "needs_approval"
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    with pytest.raises(CommandError, match="console"):
        await bus.submit(
            owner, "catalog.bulk_price", {"prices": [{"item_id": identity, "price_paise": 2500}]}, "bulk"
        )
    stepped = Session(owner.merchant_id, owner.actor_id, "owner", channel="console", step_up=True)
    await bus.submit(
        stepped, "catalog.bulk_price", {"prices": [{"item_id": identity, "price_paise": 2500}]}, "bulk"
    )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        assert (await catalog_rows(repo))[0]["price_paise"] == 2500
        assert [r["price_paise"] for r in await repo.select(item_prices)] == [2700, 2600, 2500]


async def test_pack_fields_and_modifier_prices(db):
    from arth.domains.catalog import get_item, modifier_total, validate_pack_item
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    manifest = bus.packs.get("kirana")
    medicine = manifest.model_copy(deep=True)
    medicine.catalog.schema_ = "medicine"
    with pytest.raises(CommandError, match="medicine"):
        validate_pack_item(item(), medicine)
    service = manifest.model_copy(deep=True)
    service.catalog.schema_ = "service"
    with pytest.raises(CommandError, match="service"):
        validate_pack_item(item(), service)
    coffee = {
        **item(),
        "sku": "COFFEE",
        "barcodes": [],
        "modifier_groups": [
            {"name": "Size", "required": True, "options": [{"name": "Large", "delta_paise": 1500}]}
        ],
    }
    # Modifier groups are accepted only by the menu schema, not by a kirana SKU schema.
    menu = manifest.model_copy(deep=True)
    menu.catalog.schema_ = "menu"
    bus.packs._manifests["kirana"] = menu
    identity = (await bus.submit(owner, "catalog.add_item", coffee, "coffee"))["data"]["item_id"]
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        row = await get_item(repo, identity)
        group = row["modifier_groups"][0]
        with pytest.raises(CommandError, match="modifier"):
            await modifier_total(repo, identity, {})
        assert await modifier_total(repo, identity, {group["id"]: [group["options"][0]["id"]]}) == 4200
```

### backend/tests/test_l1b_resolution.py

```python
import json

from test_l1b_catalog import item, setup_catalog

from arth.core.paths import CONTRACTS_DIR, PACKS_DIR


async def test_150_utterance_deterministic_line(db):
    from arth.domains.catalog import read_starter
    from arth.domains.resolution import resolve
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    seeds = read_starter(PACKS_DIR / "kirana/catalog_starter.csv")
    await bus.submit(owner, "catalog.import_items", {"confirmed": True, "items": seeds}, "seed")
    cases = json.loads((CONTRACTS_DIR / "fixtures/catalog_resolution.json").read_text(encoding="utf-8"))
    assert len(cases) == 150
    correct = 0
    misses = []
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        for case in cases:
            result = await resolve(repo, case["query"])
            if result["selected"] and result["selected"]["sku"] == case["sku"]:
                correct += 1
            else:
                misses.append((case["query"], result))
    assert correct / 150 >= 0.92, misses


async def test_ambiguity_unknown_and_embedding_hook_are_scoped(db):
    from arth.domains.resolution import resolve
    from arth.governance.repository import Repository

    bus, owner = await setup_catalog(db)
    await bus.submit(owner, "catalog.add_item", item(), "one")
    await bus.submit(
        owner,
        "catalog.add_item",
        {**item(), "sku": "OTHER", "names": {"en": "Aashirvaad Salt"}, "barcodes": []},
        "two",
    )
    async with db.read() as conn:
        repo = Repository(conn, owner.merchant_id)
        result = await resolve(repo, "namak")
        assert result["needs_clarification"] and result["selected"] is None
        assert len(result["candidates"]) == 2
        assert (await resolve(repo, "wireless headphones"))["selected"] is None
        assert (await resolve(Repository(conn, "other"), "Tata Salt"))["candidates"] == []

        async def embeddings(query, candidates):
            return {"foreign_item": 1.0, candidates[0]["id"]: 0.95}

        result = await resolve(repo, "unknown semantic item", embedding_hook=embeddings)
        assert result["stage"] == "embedding" and result["selected"]["id"] != "foreign_item"
```

### backend/tests/test_l1b_api.py

```python
import json

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.core.paths import CONTRACTS_DIR
from arth.core.schemas import validator
from arth.main import create_app


def test_login_settings_import_search_price_gate_and_restart(tmp_path):
    from arth.domains.merchants import provision_shop

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.05))
    with TestClient(app) as client:

        async def seed():
            return await provision_shop(
                app.state.commands, "Shop", "kirana", "Owner", "4826", "device-api", key="api-shop"
            )

        shop = client.portal.call(seed)
        credential = app.state.staff.device_credential(shop["merchant_id"], shop["device_id"])
        login_body = {
            "device_credential": credential,
            "staff_id": shop["owner_id"],
            "pin": "4826",
            "channel": "console",
        }
        login = client.post(
            "/v1/staff/login",
            json=login_body,
            headers={"Authorization": "Bearer dev-console", "Idempotency-Key": "login"},
        )
        assert login.status_code == 200, login.text
        validator("session_result").validate(login.json())
        token = login.json()["token"]
        import hashlib
        import hmac

        signed_body = token.rsplit(".", 1)[0]
        forged = signed_body + "." + hmac.new(b"dev-device", signed_body.encode(), hashlib.sha256).hexdigest()
        assert (
            client.get(
                "/v1/views/settings/language", headers={"Authorization": "Bearer " + forged}
            ).status_code
            == 401
        )
        auth = {"Authorization": "Bearer " + token}

        def command(kind, payload, key):
            response = client.post(
                "/v1/commands",
                json={"type": kind, "payload": payload},
                headers={**auth, "Idempotency-Key": key},
            )
            assert response.status_code == 200, response.text
            return response.json()

        command(
            "merchant.update_settings",
            {
                "screen_lang": "ta",
                "speech_lang": "hi-IN",
                "customer_lang": "en",
                "vpa": "example@paytm",
                "address": "Example Market",
            },
            "lang",
        )
        settings = client.get("/v1/views/settings/language", headers=auth).json()
        validator("settings_view").validate(settings)
        assert (settings["screen_lang"], settings["speech_lang"], settings["customer_lang"]) == (
            "ta",
            "hi-IN",
            "en",
        )
        item = json.loads(
            (CONTRACTS_DIR / "examples/catalog_add_item.example.json").read_text(encoding="utf-8")
        )
        identity = command("catalog.import_items", {"confirmed": True, "items": [item]}, "import")["data"][
            "item_ids"
        ][0]
        for path, name in [
            ("/v1/catalog/search?q=namak", "catalog_search_view"),
            ("/v1/catalog/resolve?q=Tata%20Salt", "resolution_view"),
            ("/v1/views/item/" + identity, "catalog_item_view"),
            ("/v1/views/onboarding", "onboarding_view"),
            ("/v1/views/settings/staff", "staff_view"),
            ("/v1/views/shift", "shift_view"),
        ]:
            response = client.get(path, headers=auth)
            assert response.status_code == 200, response.text
            validator(name).validate(response.json())
        for step in ["language", "pack", "details", "catalog", "people"]:
            command("onboarding.complete_step", {"step": step}, "step-" + step)
        assert client.get("/v1/views/onboarding", headers=auth).json()["next_step"] is None
        gate = command("catalog.change_price", {"item_id": identity, "price_paise": 2600}, "change")
        assert gate["status"] == "needs_approval"
        assert gate["envelope"]["lang"]["screen"] == "ta"
        approval = client.post(
            "/v1/approvals/" + gate["thread_id"],
            json={"decision": "approve"},
            headers={**auth, "Idempotency-Key": "approve"},
        )
        assert approval.status_code == 200, approval.text
        assert client.get("/v1/views/item/" + identity, headers=auth).json()["price_paise"] == 2600
        assert client.get("/v1/audit/verify", headers=auth).json()["valid"]
        assert (
            client.post(
                "/v1/staff/login",
                json={**login_body, "role": "owner", "owner_ptt": True},
                headers={"Authorization": "Bearer dev-console", "Idempotency-Key": "spoof"},
            ).status_code
            == 422
        )
    with TestClient(create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))) as restarted:
        assert restarted.get("/v1/views/item/" + identity, headers=auth).status_code == 200
```

### backend/tests/test_l1b_review.py

```python
from datetime import timedelta

import pytest
from test_l1b_staff import setup_staff


def test_private_signing_key_persists_and_rejects_corruption(tmp_path):
    from arth.domains.security import load_signing_key

    path = tmp_path / "session-signing.key"
    first = load_signing_key(path)
    assert len(first.get_secret_value()) == 64
    assert load_signing_key(path).get_secret_value() == first.get_secret_value()
    assert first.get_secret_value() not in repr(first)
    path.write_text("invalid", encoding="utf-8")
    with pytest.raises(ValueError):
        load_signing_key(path)


async def test_wrong_pin_reusing_success_key_still_locks_out(db):
    from arth.governance.commands import CommandError

    bus, service, shop, owner, device = await setup_staff(db)
    await service.login(device, owner.actor_id, "4826", "device", "known-success")
    for _ in range(5):
        with pytest.raises(CommandError):
            await service.login(device, owner.actor_id, "1111", "device", "known-success")
    with pytest.raises(CommandError, match="locked"):
        await service.login(device, owner.actor_id, "4826", "device", "correct-new-key")


async def test_merchant_quiet_hours_apply_and_cannot_loosen_guardrails(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import PolicyContext

    bus, service, shop, owner, device = await setup_staff(db)
    await bus.submit(
        owner, "merchant.update_settings", {"quiet_hours": {"start": "20:00", "end": "09:00"}}, "quiet"
    )
    bus.clock.set(bus.clock.now() + timedelta(hours=12, minutes=30))

    async def handler(repo, payload):
        return {"draft": True}

    async def context(repo, payload):
        return PolicyContext(purpose="marketing", consent=True)

    bus.register(
        "outreach.send_campaign", {"type": "object", "additionalProperties": False}, handler, context
    )
    with pytest.raises(CommandError, match="quiet_hours"):
        await bus.submit(owner, "outreach.send_campaign", {}, "send")
    with pytest.raises(CommandError, match="quiet_hours"):
        await bus.submit(
            owner, "merchant.update_settings", {"quiet_hours": {"start": "22:00", "end": "07:00"}}, "loosen"
        )


async def test_queued_approval_rechecks_revoked_session(db):
    from arth.domains.tables import staff_sessions
    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, service, shop, owner, device = await setup_staff(db)
    token = (await service.login(device, owner.actor_id, "4826", "console", "owner-login"))["token"]
    session = await service.resolve(token)

    async def handler(repo, payload):
        return {"saved": True}

    bus.register("supply.place_po", {"type": "object", "additionalProperties": False}, handler)
    gate = await bus.submit(session, "supply.place_po", {}, "po")
    await bus.decide(session, gate["thread_id"], "approve", "approve")
    async with db.write() as conn:
        await Repository(conn, owner.merchant_id).update(staff_sessions, {"revoked": 1})
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    with pytest.raises(CommandError, match="session"):
        await bus.run_due(owner.merchant_id)


async def test_authenticated_owner_device_can_bind_a_trusted_voice_turn(db):
    from dataclasses import replace

    from arth.governance.commands import CommandError
    from arth.governance.repository import Repository

    bus, service, shop, owner, device = await setup_staff(db)
    token = (await service.login(device, owner.actor_id, "4826", "device", "owner-device"))["token"]
    signed = await service.resolve(token)
    voice = replace(signed, channel="voice", owner_ptt=True)
    async with db.read() as conn:
        await service.validate(Repository(conn, owner.merchant_id), voice)
        with pytest.raises(CommandError):
            await service.validate(Repository(conn, owner.merchant_id), replace(voice, owner_ptt=False))
```

### backend/tests/test_l1b_recovery.py

```python
import asyncio

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.main import create_app


def test_startup_recovers_outbox_consumers_without_a_new_request(tmp_path):
    from arth.domains.merchants import provision_shop
    from arth.domains.tables import onboarding_progress
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    settings = Settings(_env_file=None, mode="test", data_dir=tmp_path, tick_interval_s=0.02)
    first = create_app(settings)
    with TestClient(first) as client:

        async def seed():
            shop = await provision_shop(
                first.state.commands, "Shop", "kirana", "Owner", "4826", "device", key="recovery"
            )
            await first.state.commands.submit(
                Session(shop["merchant_id"], shop["owner_id"], "owner"),
                "onboarding.complete_step",
                {"step": "language"},
                "language",
            )
            return shop

        shop = client.portal.call(seed)
    restarted = create_app(settings)
    with TestClient(restarted) as client:

        async def consume(repo, event):
            if event["type"] == "onboarding.updated":
                await repo.insert(
                    onboarding_progress, {"step": "recovery_probe", "completed_at": event["occurred_at"]}
                )

        restarted.state.events.on("recovery-probe", consume)

        async def observed():
            for _ in range(25):
                async with restarted.state.db.read() as conn:
                    rows = await Repository(conn, shop["merchant_id"]).select(
                        onboarding_progress, onboarding_progress.c.step == "recovery_probe"
                    )
                if rows:
                    return True
                await asyncio.sleep(0.02)
            return False

        assert client.portal.call(observed)
```

### backend/tests/test_migrations.py

```python
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import create_engine

import arth.core.tables  # noqa: F401  (registers tables on metadata)
from arth.core.db import metadata
from arth.core.migrate import upgrade


def test_migrations_match_models(tmp_path: Path) -> None:
    path = tmp_path / "drift.db"
    upgrade(path)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        with engine.connect() as conn:
            ctx = MigrationContext.configure(
                conn,
                opts={
                    "compare_type": True,
                    "include_object": lambda obj, name, type_, reflected, compare_to: (
                        not (name == "items_fts" or name.startswith("items_fts_"))
                    ),
                },
            )
            assert compare_metadata(ctx, metadata) == []
    finally:
        engine.dispose()


def test_upgrade_handles_percent_in_path(tmp_path: Path) -> None:
    path = tmp_path / "a%20b" / "arth.db"
    upgrade(path)
    assert path.is_file()
```

### backend/tests/test_contract_schemas.py

```python
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
        "envelope",
        "event",
        "i18n_changed",
        "merchant_bootstrap",
        "merchant_update_settings",
        "onboarding_complete_step",
        "onboarding_started",
        "onboarding_updated",
        "onboarding_view",
        "problem",
        "resolution_view",
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
```

### frontend/tests/contracts.test.ts

```typescript
import { readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import { SCHEMAS, type SchemaName } from '../lib/contracts';
import { parseEnvelope, validate, validateEnvelope, validateEvent, validateProblem } from '../lib/validate';

const EXAMPLES_DIR = fileURLToPath(new URL('../../contracts/examples/', import.meta.url));
const examples = readdirSync(EXAMPLES_DIR)
  .filter((f) => f.endsWith('.example.json'))
  .sort()
  .map(
    (f) => [f.replace(/\.example\.json$/, ''), JSON.parse(readFileSync(EXAMPLES_DIR + f, 'utf-8'))] as const,
  );
const example = (name: string) => structuredClone(examples.find(([n]) => n === name)![1]);
const contractNames = [
  'approval',
  'approval_decided',
  'approval_requested',
  'audit_verification',
  'audit_verified',
  'catalog_add_item',
  'catalog_bulk_price',
  'catalog_change_price',
  'catalog_import_items',
  'catalog_item_added',
  'catalog_item_view',
  'catalog_price_changed',
  'catalog_search_view',
  'command',
  'command_executed',
  'command_result',
  'common',
  'envelope',
  'event',
  'i18n_changed',
  'merchant_bootstrap',
  'merchant_update_settings',
  'onboarding_complete_step',
  'onboarding_started',
  'onboarding_updated',
  'onboarding_view',
  'problem',
  'resolution_view',
  'session_result',
  'settings_view',
  'shift_close',
  'shift_open',
  'shift_view',
  'staff_add',
  'staff_add_command',
  'staff_added',
  'staff_logged_in',
  'staff_login',
  'staff_login_command',
  'staff_logout',
  'staff_shift_closed',
  'staff_shift_opened',
  'staff_view',
  'view_invalidate',
];

describe('contract registry', () => {
  it('lists every contract', () => {
    expect(SCHEMAS.map((s) => s.name).sort()).toEqual(contractNames);
  });

  it('has an example for each top-level contract', () => {
    expect(examples.map(([n]) => n)).toEqual(contractNames.filter((name) => name !== 'common'));
  });
});

describe.each(examples)('%s example', (name, data) => {
  it('validates against its schema', () => {
    expect(validate(name as SchemaName, data)).toBe(true);
  });
});

describe('envelope contract', () => {
  it('accepts the spec example via the named validator', () => {
    expect(validateEnvelope(example('envelope'))).toBe(true);
  });

  it('rejects an unknown audience', () => {
    expect(validateEnvelope({ ...example('envelope'), audience: 'everyone' })).toBe(false);
  });

  it('rejects an unknown card type', () => {
    expect(validateEnvelope({ ...example('envelope'), cards: [{ type: 'banner' }] })).toBe(false);
  });

  it('rejects hi-Latn as a speech locale (resolved through common.schema.json)', () => {
    expect(validateEnvelope({ ...example('envelope'), lang: { screen: 'hi-Latn', speech: 'hi-Latn' } })).toBe(
      false,
    );
  });

  it('rejects a bad undo date-time (formats are on)', () => {
    const bad = example('envelope');
    bad.undo.until = 'yesterday';
    expect(validateEnvelope(bad)).toBe(false);
  });

  it('parseEnvelope returns the typed envelope or throws with the errors', () => {
    expect(parseEnvelope(example('envelope')).turn_id).toMatch(/^turn_/);
    expect(() => parseEnvelope({ ...example('envelope'), presence: { state: 'dancing' } })).toThrow(
      /invalid envelope: .*presence\/state/,
    );
  });
});

describe('event and problem contracts', () => {
  it('rejects an event type without a dot', () => {
    expect(validateEvent({ ...example('event'), type: 'ticked' })).toBe(false);
  });

  it('accepts a root event with a null causation_id', () => {
    expect(validateEvent({ ...example('event'), causation_id: null })).toBe(true);
  });

  it('rejects a problem with a 2xx status', () => {
    expect(validateProblem({ ...example('problem'), status: 200 })).toBe(false);
  });

  it('throws for an unknown contract name', () => {
    expect(() => validate('nope' as SchemaName, {})).toThrow(/no contract named "nope"/);
  });
});
```

### backend/packs/kirana/catalog_starter.csv

```csv
sku,en,hi,hi_latn,unit,mrp_paise,price_paise,cost_paise,category,aliases
TATA-SALT,Tata Salt,टाटा नमक,Tata namak,pcs,10000,9000,7000,grocery,tata salt packet
ASH-SALT,Aashirvaad Salt,आशीर्वाद नमक,Aashirvaad namak,pcs,10000,9000,7000,grocery,ashirvad salt
ASH-ATTA,Aashirvaad Atta,आशीर्वाद आटा,Aashirvaad atta,pcs,10000,9000,7000,grocery,ashirvad flour
FORT-ATTA,Fortune Atta,फॉर्च्यून आटा,Fortune atta,pcs,10000,9000,7000,grocery,fortune wheat
SUGAR,White Sugar,सफेद चीनी,Safed cheeni,pcs,10000,9000,7000,grocery,chini packet
TATA-TEA,Tata Tea Gold,टाटा चाय गोल्ड,Tata chai gold,pcs,10000,9000,7000,grocery,tata gold chai
BROOKE-TEA,Brooke Bond Red Label,ब्रुक बॉन्ड रेड लेबल,Brooke bond lal chai,pcs,10000,9000,7000,grocery,red label tea
AMUL-MILK,Amul Taaza Milk,अमूल ताजा दूध,Amul taaza doodh,pcs,10000,9000,7000,grocery,amul milk packet
MOTHER-MILK,Mother Dairy Milk,मदर डेयरी दूध,Mother dairy doodh,pcs,10000,9000,7000,grocery,mother dairy packet
PARLE,Parle G Biscuit,पारले जी बिस्कुट,Parle ji biscuit,pcs,10000,9000,7000,grocery,parleg packet
MAGGI,Maggi Noodles,मैगी नूडल्स,Maggi noodles,pcs,10000,9000,7000,grocery,maggi packet
BRIT-BREAD,Britannia Bread,ब्रिटानिया ब्रेड,Britannia bread,pcs,10000,9000,7000,grocery,britannia loaf
FORT-OIL,Fortune Sunflower Oil,फॉर्च्यून सूरजमुखी तेल,Fortune surajmukhi tel,pcs,10000,9000,7000,grocery,fortune sunflower
DALDA,Dalda Vanaspati,डालडा वनस्पति,Dalda vanaspati,pcs,10000,9000,7000,grocery,dalda ghee
INDIA-RICE,India Gate Basmati Rice,इंडिया गेट बासमती चावल,India gate basmati chawal,pcs,10000,9000,7000,grocery,india gate rice
DAAWAT,Daawat Basmati Rice,दावत बासमती चावल,Daawat basmati chawal,pcs,10000,9000,7000,grocery,daawat rice
TOOR,Toor Dal,तूर दाल,Toor dal,pcs,10000,9000,7000,grocery,arhar dal
MOONG,Moong Dal,मूंग दाल,Moong dal,pcs,10000,9000,7000,grocery,mung lentils
MASOOR,Masoor Dal,मसूर दाल,Masoor dal,pcs,10000,9000,7000,grocery,masur lentils
SURF,Surf Excel Detergent,सर्फ एक्सेल डिटर्जेंट,Surf excel detergent,pcs,10000,9000,7000,grocery,surf powder
RIN,Rin Detergent Bar,रिन डिटर्जेंट बार,Rin sabun,pcs,10000,9000,7000,grocery,rin washing bar
LUX,Lux Soap,लक्स साबुन,Lux sabun,pcs,10000,9000,7000,grocery,lux bath soap
COLGATE,Colgate Toothpaste,कोलगेट टूथपेस्ट,Colgate toothpaste,pcs,10000,9000,7000,grocery,colgate paste
CLINIC,Clinic Plus Shampoo,क्लिनिक प्लस शैम्पू,Clinic plus shampoo,pcs,10000,9000,7000,grocery,clinic shampoo
HALDIRAM,Haldiram Aloo Bhujia,हल्दीराम आलू भुजिया,Haldiram aloo bhujia,pcs,10000,9000,7000,grocery,haldiram namkeen
```

### contracts/fixtures/catalog_resolution.json

```json
[
  {
    "query": "Tata Salt",
    "sku": "TATA-SALT"
  },
  {
    "query": "टाटा नमक",
    "sku": "TATA-SALT"
  },
  {
    "query": "Tata namak",
    "sku": "TATA-SALT"
  },
  {
    "query": "tata salt packet",
    "sku": "TATA-SALT"
  },
  {
    "query": "tata saltt",
    "sku": "TATA-SALT"
  },
  {
    "query": "TATA—SALT",
    "sku": "TATA-SALT"
  },
  {
    "query": "Aashirvaad Salt",
    "sku": "ASH-SALT"
  },
  {
    "query": "आशीर्वाद नमक",
    "sku": "ASH-SALT"
  },
  {
    "query": "Aashirvaad namak",
    "sku": "ASH-SALT"
  },
  {
    "query": "ashirvad salt",
    "sku": "ASH-SALT"
  },
  {
    "query": "aashirvad saltt",
    "sku": "ASH-SALT"
  },
  {
    "query": "AASHIRVAAD SALT",
    "sku": "ASH-SALT"
  },
  {
    "query": "Aashirvaad Atta",
    "sku": "ASH-ATTA"
  },
  {
    "query": "आशीर्वाद आटा",
    "sku": "ASH-ATTA"
  },
  {
    "query": "Aashirvaad atta",
    "sku": "ASH-ATTA"
  },
  {
    "query": "ashirvad flour",
    "sku": "ASH-ATTA"
  },
  {
    "query": "aashirvaad ataa",
    "sku": "ASH-ATTA"
  },
  {
    "query": "AASHIRVAAD-ATTA",
    "sku": "ASH-ATTA"
  },
  {
    "query": "Fortune Atta",
    "sku": "FORT-ATTA"
  },
  {
    "query": "फॉर्च्यून आटा",
    "sku": "FORT-ATTA"
  },
  {
    "query": "Fortune atta",
    "sku": "FORT-ATTA"
  },
  {
    "query": "fortune wheat",
    "sku": "FORT-ATTA"
  },
  {
    "query": "fortun atta",
    "sku": "FORT-ATTA"
  },
  {
    "query": "FORTUNE ATTA",
    "sku": "FORT-ATTA"
  },
  {
    "query": "White Sugar",
    "sku": "SUGAR"
  },
  {
    "query": "सफेद चीनी",
    "sku": "SUGAR"
  },
  {
    "query": "Safed cheeni",
    "sku": "SUGAR"
  },
  {
    "query": "chini packet",
    "sku": "SUGAR"
  },
  {
    "query": "white sugarr",
    "sku": "SUGAR"
  },
  {
    "query": "WHITE-SUGAR",
    "sku": "SUGAR"
  },
  {
    "query": "Tata Tea Gold",
    "sku": "TATA-TEA"
  },
  {
    "query": "टाटा चाय गोल्ड",
    "sku": "TATA-TEA"
  },
  {
    "query": "Tata chai gold",
    "sku": "TATA-TEA"
  },
  {
    "query": "tata gold chai",
    "sku": "TATA-TEA"
  },
  {
    "query": "tata tea goldd",
    "sku": "TATA-TEA"
  },
  {
    "query": "TATA TEA GOLD",
    "sku": "TATA-TEA"
  },
  {
    "query": "Brooke Bond Red Label",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "ब्रुक बॉन्ड रेड लेबल",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "Brooke bond lal chai",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "red label tea",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "brooke bond red lable",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "BROOKE BOND RED LABEL",
    "sku": "BROOKE-TEA"
  },
  {
    "query": "Amul Taaza Milk",
    "sku": "AMUL-MILK"
  },
  {
    "query": "अमूल ताजा दूध",
    "sku": "AMUL-MILK"
  },
  {
    "query": "Amul taaza doodh",
    "sku": "AMUL-MILK"
  },
  {
    "query": "amul milk packet",
    "sku": "AMUL-MILK"
  },
  {
    "query": "amul taza milk",
    "sku": "AMUL-MILK"
  },
  {
    "query": "AMUL TAAZA MILK",
    "sku": "AMUL-MILK"
  },
  {
    "query": "Mother Dairy Milk",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "मदर डेयरी दूध",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "Mother dairy doodh",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "mother dairy packet",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "mother diary milk",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "MOTHER DAIRY MILK",
    "sku": "MOTHER-MILK"
  },
  {
    "query": "Parle G Biscuit",
    "sku": "PARLE"
  },
  {
    "query": "पारले जी बिस्कुट",
    "sku": "PARLE"
  },
  {
    "query": "Parle ji biscuit",
    "sku": "PARLE"
  },
  {
    "query": "parleg packet",
    "sku": "PARLE"
  },
  {
    "query": "parle g biscut",
    "sku": "PARLE"
  },
  {
    "query": "PARLE-G BISCUIT",
    "sku": "PARLE"
  },
  {
    "query": "Maggi Noodles",
    "sku": "MAGGI"
  },
  {
    "query": "मैगी नूडल्स",
    "sku": "MAGGI"
  },
  {
    "query": "Maggi noodles",
    "sku": "MAGGI"
  },
  {
    "query": "maggi packet",
    "sku": "MAGGI"
  },
  {
    "query": "maggi noodls",
    "sku": "MAGGI"
  },
  {
    "query": "MAGGI NOODLES",
    "sku": "MAGGI"
  },
  {
    "query": "Britannia Bread",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "ब्रिटानिया ब्रेड",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "Britannia bread",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "britannia loaf",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "britania bread",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "BRITANNIA BREAD",
    "sku": "BRIT-BREAD"
  },
  {
    "query": "Fortune Sunflower Oil",
    "sku": "FORT-OIL"
  },
  {
    "query": "फॉर्च्यून सूरजमुखी तेल",
    "sku": "FORT-OIL"
  },
  {
    "query": "Fortune surajmukhi tel",
    "sku": "FORT-OIL"
  },
  {
    "query": "fortune sunflower",
    "sku": "FORT-OIL"
  },
  {
    "query": "fortune sunflwer oil",
    "sku": "FORT-OIL"
  },
  {
    "query": "FORTUNE SUNFLOWER OIL",
    "sku": "FORT-OIL"
  },
  {
    "query": "Dalda Vanaspati",
    "sku": "DALDA"
  },
  {
    "query": "डालडा वनस्पति",
    "sku": "DALDA"
  },
  {
    "query": "Dalda vanaspati",
    "sku": "DALDA"
  },
  {
    "query": "dalda ghee",
    "sku": "DALDA"
  },
  {
    "query": "dalda vanaspti",
    "sku": "DALDA"
  },
  {
    "query": "DALDA VANASPATI",
    "sku": "DALDA"
  },
  {
    "query": "India Gate Basmati Rice",
    "sku": "INDIA-RICE"
  },
  {
    "query": "इंडिया गेट बासमती चावल",
    "sku": "INDIA-RICE"
  },
  {
    "query": "India gate basmati chawal",
    "sku": "INDIA-RICE"
  },
  {
    "query": "india gate rice",
    "sku": "INDIA-RICE"
  },
  {
    "query": "india gate basmati rce",
    "sku": "INDIA-RICE"
  },
  {
    "query": "INDIA GATE BASMATI RICE",
    "sku": "INDIA-RICE"
  },
  {
    "query": "Daawat Basmati Rice",
    "sku": "DAAWAT"
  },
  {
    "query": "दावत बासमती चावल",
    "sku": "DAAWAT"
  },
  {
    "query": "Daawat basmati chawal",
    "sku": "DAAWAT"
  },
  {
    "query": "daawat rice",
    "sku": "DAAWAT"
  },
  {
    "query": "dawat basmati rice",
    "sku": "DAAWAT"
  },
  {
    "query": "DAAWAT BASMATI RICE",
    "sku": "DAAWAT"
  },
  {
    "query": "Toor Dal",
    "sku": "TOOR"
  },
  {
    "query": "तूर दाल",
    "sku": "TOOR"
  },
  {
    "query": "Toor dal",
    "sku": "TOOR"
  },
  {
    "query": "arhar dal",
    "sku": "TOOR"
  },
  {
    "query": "toor daal",
    "sku": "TOOR"
  },
  {
    "query": "TOOR-DAL",
    "sku": "TOOR"
  },
  {
    "query": "Moong Dal",
    "sku": "MOONG"
  },
  {
    "query": "मूंग दाल",
    "sku": "MOONG"
  },
  {
    "query": "Moong dal",
    "sku": "MOONG"
  },
  {
    "query": "mung lentils",
    "sku": "MOONG"
  },
  {
    "query": "moong daal",
    "sku": "MOONG"
  },
  {
    "query": "MOONG-DAL",
    "sku": "MOONG"
  },
  {
    "query": "Masoor Dal",
    "sku": "MASOOR"
  },
  {
    "query": "मसूर दाल",
    "sku": "MASOOR"
  },
  {
    "query": "Masoor dal",
    "sku": "MASOOR"
  },
  {
    "query": "masur lentils",
    "sku": "MASOOR"
  },
  {
    "query": "masoor daal",
    "sku": "MASOOR"
  },
  {
    "query": "MASOOR-DAL",
    "sku": "MASOOR"
  },
  {
    "query": "Surf Excel Detergent",
    "sku": "SURF"
  },
  {
    "query": "सर्फ एक्सेल डिटर्जेंट",
    "sku": "SURF"
  },
  {
    "query": "Surf excel detergent",
    "sku": "SURF"
  },
  {
    "query": "surf powder",
    "sku": "SURF"
  },
  {
    "query": "surf excel detergnt",
    "sku": "SURF"
  },
  {
    "query": "SURF EXCEL DETERGENT",
    "sku": "SURF"
  },
  {
    "query": "Rin Detergent Bar",
    "sku": "RIN"
  },
  {
    "query": "रिन डिटर्जेंट बार",
    "sku": "RIN"
  },
  {
    "query": "Rin sabun",
    "sku": "RIN"
  },
  {
    "query": "rin washing bar",
    "sku": "RIN"
  },
  {
    "query": "rin detergent barr",
    "sku": "RIN"
  },
  {
    "query": "RIN DETERGENT BAR",
    "sku": "RIN"
  },
  {
    "query": "Lux Soap",
    "sku": "LUX"
  },
  {
    "query": "लक्स साबुन",
    "sku": "LUX"
  },
  {
    "query": "Lux sabun",
    "sku": "LUX"
  },
  {
    "query": "lux bath soap",
    "sku": "LUX"
  },
  {
    "query": "lux soapp",
    "sku": "LUX"
  },
  {
    "query": "LUX-SOAP",
    "sku": "LUX"
  },
  {
    "query": "Colgate Toothpaste",
    "sku": "COLGATE"
  },
  {
    "query": "कोलगेट टूथपेस्ट",
    "sku": "COLGATE"
  },
  {
    "query": "Colgate toothpaste",
    "sku": "COLGATE"
  },
  {
    "query": "colgate paste",
    "sku": "COLGATE"
  },
  {
    "query": "colgate toothpste",
    "sku": "COLGATE"
  },
  {
    "query": "COLGATE TOOTHPASTE",
    "sku": "COLGATE"
  },
  {
    "query": "Clinic Plus Shampoo",
    "sku": "CLINIC"
  },
  {
    "query": "क्लिनिक प्लस शैम्पू",
    "sku": "CLINIC"
  },
  {
    "query": "Clinic plus shampoo",
    "sku": "CLINIC"
  },
  {
    "query": "clinic shampoo",
    "sku": "CLINIC"
  },
  {
    "query": "clinic plus shampo",
    "sku": "CLINIC"
  },
  {
    "query": "CLINIC PLUS SHAMPOO",
    "sku": "CLINIC"
  },
  {
    "query": "Haldiram Aloo Bhujia",
    "sku": "HALDIRAM"
  },
  {
    "query": "हल्दीराम आलू भुजिया",
    "sku": "HALDIRAM"
  },
  {
    "query": "Haldiram aloo bhujia",
    "sku": "HALDIRAM"
  },
  {
    "query": "haldiram namkeen",
    "sku": "HALDIRAM"
  },
  {
    "query": "haldiram aloo bhujiya",
    "sku": "HALDIRAM"
  },
  {
    "query": "HALDIRAM ALOO BHUJIA",
    "sku": "HALDIRAM"
  }
]
```

### contracts/openapi.yaml

```yaml
openapi: 3.1.0
info:
  title: Arth API
  version: 0.1.0
  description: Spec Part C2. L0 exposes health, the SSE stream and a director ping; later layers add their families.
paths:
  /v1/staff/login:
    post:
      operationId: staffLogin
      security: [{device: []}, {console: []}]
      parameters:
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: './commands/staff_login.schema.json'}
      responses:
        '200':
          description: staffLogin result
          content:
            application/json:
              schema: {$ref: './session_result.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/staff:
    post:
      operationId: addStaff
      security: [{device: []}, {console: []}]
      parameters:
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: './commands/staff_add.schema.json'}
      responses:
        '200':
          description: addStaff result
          content:
            application/json:
              schema: {$ref: './command_result.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/catalog/search:
    get:
      operationId: searchCatalog
      security: [{device: []}, {console: []}]
      parameters:
        - {in: query, name: q, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      responses:
        '200':
          description: searchCatalog result
          content:
            application/json:
              schema: {$ref: './catalog_search_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/catalog/resolve:
    get:
      operationId: resolveCatalog
      security: [{device: []}, {console: []}]
      parameters:
        - {in: query, name: q, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      responses:
        '200':
          description: resolveCatalog result
          content:
            application/json:
              schema: {$ref: './resolution_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/settings/language:
    get:
      operationId: languageSettings
      security: [{device: []}, {console: []}]
      responses:
        '200':
          description: languageSettings result
          content:
            application/json:
              schema: {$ref: './settings_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/onboarding:
    get:
      operationId: onboardingView
      security: [{device: []}, {console: []}]
      responses:
        '200':
          description: onboardingView result
          content:
            application/json:
              schema: {$ref: './onboarding_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/settings/staff:
    get:
      operationId: staffSettings
      security: [{device: []}, {console: []}]
      responses:
        '200':
          description: staffSettings result
          content:
            application/json:
              schema: {$ref: './staff_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/staff/login:
    get:
      operationId: staffLoginView
      security: [{device: []}, {console: []}]
      parameters:
        - {in: header, name: X-Device-Credential, required: true, schema: {type: string}}
      responses:
        '200':
          description: staffLoginView result
          content:
            application/json:
              schema: {$ref: './staff_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/shift:
    get:
      operationId: shiftView
      security: [{device: []}, {console: []}]
      responses:
        '200':
          description: shiftView result
          content:
            application/json:
              schema: {$ref: './shift_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/views/item/{item_id}:
    get:
      operationId: itemView
      security: [{device: []}, {console: []}]
      parameters:
        - {in: path, name: item_id, required: true, schema: {type: string}}
      responses:
        '200':
          description: itemView result
          content:
            application/json:
              schema: {$ref: './catalog_item_view.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/commands:
    post:
      operationId: submitCommand
      security: [{device: []}, {console: []}]
      parameters:
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: './command.schema.json'}
      responses:
        '200':
          description: Stored command result or approval gate
          content:
            application/json:
              schema: {$ref: './command_result.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/approvals/{thread_id}:
    post:
      operationId: decideApproval
      security: [{device: []}, {console: []}]
      parameters:
        - {in: path, name: thread_id, required: true, schema: {type: string}}
        - {in: header, name: Idempotency-Key, required: true, schema: {type: string, minLength: 1, maxLength: 200}}
      requestBody:
        required: true
        content:
          application/json:
            schema: {$ref: './approval.schema.json'}
      responses:
        '200':
          description: Decision results, one per gate for a batch
          content:
            application/json:
              schema:
                anyOf:
                  - {$ref: './command_result.schema.json'}
                  - {type: object, properties: {items: {type: array, items: {$ref: './command_result.schema.json'}}}, required: [items], additionalProperties: false}
        '401': {$ref: '#/components/responses/Problem'}
        '409': {$ref: '#/components/responses/Problem'}
  /v1/audit/verify:
    get:
      operationId: verifyAudit
      security: [{device: []}, {console: []}]
      responses:
        '200':
          description: Merchant audit integrity
          content:
            application/json:
              schema: {$ref: './audit_verification.schema.json'}
        '401': {$ref: '#/components/responses/Problem'}
  /healthz:
    get:
      operationId: getHealth
      security: []
      responses:
        '200':
          description: Service health
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Health' }
  /v1/stream:
    get:
      operationId: getStream
      security: [{device: []}, {console: []}]
      description: >-
        Server-sent events. L0 streams spans; L1 adds domain events, envelopes and view invalidations.
        Requires a server-provisioned merchant session. Domain events and spans are merchant filtered.
      responses:
        '401': {$ref: '#/components/responses/Problem'}
        '200':
          description: SSE stream
          content:
            text/event-stream:
              schema: { type: string }
  /v1/director/ping:
    get:
      operationId: directorPing
      security:
        - director: []
      responses:
        '200':
          description: Director token accepted
          content:
            application/json:
              schema: { $ref: '#/components/schemas/Ok' }
        '401':
          $ref: '#/components/responses/Problem'
components:
  securitySchemes:
    director:
      type: http
      scheme: bearer
      description: Presenter token for /v1/director/* (L0).
    device:
      type: http
      scheme: bearer
      description: Reserved for L1 device sessions (STF-2); no L0 route uses it yet.
    console:
      type: http
      scheme: bearer
      description: Reserved for L1 Console sessions (STF-2); no L0 route uses it yet.
  responses:
    Problem:
      description: RFC 9457 problem details (spec Part C1)
      content:
        application/problem+json:
          schema: { $ref: '#/components/schemas/Problem' }
  schemas:
    Problem:
      $ref: './problem.schema.json'
    Health:
      type: object
      required: [status, mode, clock, packs, providers]
      properties:
        status: { type: string, enum: [ok] }
        mode: { type: string, enum: [dev, test, demo, prod] }
        clock: { type: string, format: date-time }
        packs: { type: array, items: { type: string } }
        providers:
          type: object
          description: Whether each AI provider has an API key configured (booleans only, never the key)
          additionalProperties: { type: boolean }
    Ok:
      type: object
      required: [ok]
      properties:
        ok: { type: boolean }
```

### contracts/README.md

```markdown
# Contracts

The single source of truth between `backend/` and `frontend/` (spec Part C). Both sides are **generated** from these files; never edit generated code.

## Layout
| Path | What |
|---|---|
| `common.schema.json` | Shared definitions: `Locale`, `SpeechLocale`, `Audience`, `Tier`, `Ulid`, `PrefixedId`, `DottedCode`, `MessageKey`, `NonEmptyString` |
| `envelope.schema.json` | Response envelope v2 + base `Card` (C3, C4) |
| `events/event.schema.json` | `DomainEvent` base shape for the Event Spine (C5) |
| `problem.schema.json` | RFC 9457 problem details (C1) |
| `openapi.yaml` | HTTP API (C2); `Problem` is exposed as `components/schemas/Problem` and `components/responses/Problem` |
| `examples/<name>.example.json` | One realistic example per contract. Every example is validated and round-tripped on both sides automatically |
| `fixtures/` | Shared test fixtures (e.g. `format_cases.json` for money/date formatting parity). Not contracts |
| `tokens.json` | Design tokens (→ `frontend/app/tokens.css`). Not a contract |

## Rules
1. **Dialect:** JSON Schema **draft-07** with `definitions` (not `$defs`). All three toolchains (jsonschema, datamodel-code-generator, json-schema-to-typescript/Ajv) handle it identically.
2. **Discovery:** every `*.schema.json` outside `examples/` and `fixtures/` is a contract. Its name is the file stem (`events/event.schema.json` → `event`); names must be unique across the tree.
3. **Identity:** each schema has a `title` (the generated class/type name) and `$id` = `https://arth.local/contracts/<path>`. Cross-file refs are relative: `common.schema.json#/definitions/Tier` (or `../common.schema.json#/...` from a subfolder).
4. **Nullable fields:** `anyOf: [{$ref: ...}, {type: "null"}]`, never `oneOf` (a ref that also accepts null would match both branches) and never union `type` arrays (Ajv strict mode rejects them).
5. **Numbers:** when a value may be a whole number, list `integer` before `number` so Pydantic keeps it an `int` (paise must never become `200000.0`).
6. **Strictness:** objects use `additionalProperties: false`, except the open base `Card` (see below).

## Workflow
- After any change here: `python dev.py gen` (Pydantic → `backend/arth/contracts/`, TS + copied schemas + `index.ts` → `frontend/lib/contracts/`, OpenAPI types → `frontend/lib/contracts/api.ts`).
- `python dev.py check` runs `gen-check` first and **fails if generated code is stale**.
- Add an example for every new contract; the tests pick it up by name.

## L1a foundation

`command.schema.json` is the strict transport envelope; each domain registers its own strict payload schema
with the Command Bus when implemented in L1b+. `command_result`, `approval` and `audit_verification` define
foundation responses and decisions. Per-topic schemas cover `command.executed`, `approval.requested`,
`approval.decided`, `audit.verified` and `view.invalidate`. All have shared Python/TypeScript examples.

The foundation endpoints and SSE require a merchant session. L1b adds persisted PIN sessions; surface tokens
alone cannot select a merchant or assert an owner role. `app.state.sessions` remains a trusted fixture seam.

## L1b identity and catalog

`commands/` contains strict per-command schemas. `staff_login` and `staff_add` are credential-bearing HTTP
requests; their `_command` counterparts are the public bus payloads with PINs removed. PIN material is passed
only through ephemeral R1 execution context, never command history, audit or outbox. Session bearer tokens are
minted outside persisted command results. Domain-event schemas cover i18n, onboarding, staff and catalog changes.

Trusted startup code calls `arth.domains.merchants.provision_shop` with the app's Command Bus and a stable
provisioning key. The returned merchant/owner/device IDs are canonical prefixed ULIDs. Obtain the registered
device credential through `app.state.staff.device_credential(shop['merchant_id'], shop['device_id'])` and hand
it to that device. `POST /v1/staff/login` requires that credential, a staff PIN, the appropriate surface bearer
token and an Idempotency-Key. Authenticated requests then use the returned session bearer token.

The server signing key is separate from surface tokens: set `ARTH_SESSION_SIGNING_KEY` or retain the generated
`session-signing.key` under the server data directory. It is a server secret; it must never be shipped to a
device, browser, prompt or log. Rotating it invalidates both session and device credentials. First-merchant
enrollment remains trusted provisioning; a public enrollment authority is not specified yet.

L1b registers merchant, onboarding, staff, shift and catalog commands at boot. Settings, onboarding, staff,
shift, item, search and resolution read models declare invalidation topics. The synthetic kirana starter CSV
requires a confirmed import command. Resolution's 150-case fixture tests deterministic retrieval; embeddings
are an injected L3 hook. Stock consumption, appointments and the remaining commerce modules follow later.

## Planned extension patterns (L1+)
**Per-card-type schemas.** One file per type at `cards/<type>.schema.json`, each with `properties.type: {const: "<type>"}`, its own required fields and `additionalProperties: false` (repeat the shared `id`/`audience`/`note` fields, or `allOf` the base, which then must stay open). The envelope's `cards.items` becomes a `oneOf` of `$ref`s to those files (the `const` makes branches mutually exclusive, and both generators emit a tagged union). Then delete the base `type` enum so the list lives in one place, and point the card-type test at the `cards/` directory listing. The current envelope example's `hint` card is the first fixture to make strict.

**Per-topic event payloads.** Same pattern: `events/<topic>.schema.json` with `type: {const: "<topic>"}` and a typed `payload`; `DomainEvent` stays the base shape.
```

### contracts/staff_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/staff_view.schema.json",
  "title": "StaffView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "staff": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "name": {
            "type": "string"
          },
          "role": {
            "enum": [
              "owner",
              "manager",
              "cashier",
              "helper"
            ]
          }
        },
        "required": [
          "id",
          "name",
          "role"
        ]
      }
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "staff",
    "invalidate_on"
  ]
}
```

### contracts/examples/staff_view.example.json

```json
{
  "staff": [
    {
      "id": "staff_example",
      "name": "Owner",
      "role": "owner"
    }
  ],
  "invalidate_on": [
    "staff.added"
  ]
}
```

### contracts/shift_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/shift_view.schema.json",
  "title": "ShiftView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "current": {
      "anyOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "id": {
              "type": "string",
              "minLength": 1
            },
            "staff_id": {
              "type": "string",
              "minLength": 1
            },
            "opened_at": {
              "type": "string"
            },
            "closed_at": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "null"
                }
              ]
            },
            "float_paise": {
              "type": "integer"
            },
            "expected_paise": {
              "type": "integer"
            },
            "counted_paise": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ]
            },
            "variance_paise": {
              "anyOf": [
                {
                  "type": "integer"
                },
                {
                  "type": "null"
                }
              ]
            }
          },
          "required": [
            "id",
            "staff_id",
            "opened_at",
            "float_paise",
            "expected_paise"
          ]
        },
        {
          "type": "null"
        }
      ]
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "current",
    "invalidate_on"
  ]
}
```

### contracts/examples/shift_view.example.json

```json
{
  "current": null,
  "invalidate_on": [
    "staff.shift_opened",
    "staff.shift_closed"
  ]
}
```

### contracts/settings_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/settings_view.schema.json",
  "title": "SettingsView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "screen_lang": {
      "enum": [
        "hi",
        "en",
        "hi-Latn",
        "mr",
        "ta",
        "bn",
        "gu",
        "te"
      ]
    },
    "speech_lang": {
      "enum": [
        "hi-IN",
        "en-IN",
        "mr-IN",
        "ta-IN",
        "bn-IN",
        "gu-IN",
        "te-IN"
      ]
    },
    "customer_lang": {
      "enum": [
        "hi",
        "en",
        "hi-Latn",
        "mr",
        "ta",
        "bn",
        "gu",
        "te"
      ]
    },
    "name": {
      "type": "string"
    },
    "vpa": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "address": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "gstin": {
      "type": "string",
      "maxLength": 15
    },
    "tax_profile": {
      "enum": [
        "unregistered",
        "composition",
        "regular"
      ]
    },
    "hours": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        },
        "end": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        }
      },
      "required": [
        "start",
        "end"
      ]
    },
    "quiet_hours": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        },
        "end": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        }
      },
      "required": [
        "start",
        "end"
      ]
    },
    "pack": {
      "type": "string"
    },
    "marketing_consent_default": {
      "const": false
    },
    "receipts_consent_default": {
      "const": false
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "name",
    "pack",
    "screen_lang",
    "speech_lang",
    "customer_lang",
    "tax_profile",
    "marketing_consent_default",
    "receipts_consent_default"
  ]
}
```

### contracts/examples/settings_view.example.json

```json
{
  "name": "Example Shop",
  "pack": "kirana",
  "screen_lang": "hi-Latn",
  "speech_lang": "hi-IN",
  "customer_lang": "hi",
  "tax_profile": "unregistered",
  "marketing_consent_default": false,
  "receipts_consent_default": false
}
```

### contracts/session_result.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/session_result.schema.json",
  "title": "SessionResult",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "token": {
      "type": "string"
    },
    "staff_id": {
      "type": "string",
      "minLength": 1
    },
    "expires_at": {
      "type": "string",
      "format": "date-time"
    }
  },
  "required": [
    "token",
    "staff_id",
    "expires_at"
  ]
}
```

### contracts/examples/session_result.example.json

```json
{
  "token": "synthetic-session-example",
  "staff_id": "staff_example",
  "expires_at": "2026-10-30T16:00:00Z"
}
```

### contracts/resolution_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/resolution_view.schema.json",
  "title": "ResolutionView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "stage": {
      "enum": [
        "none",
        "normalize",
        "alias",
        "transliteration",
        "fuzzy",
        "embedding"
      ]
    },
    "candidates": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "sku": {
            "type": "string"
          },
          "names": {
            "type": "object",
            "additionalProperties": {
              "type": "string",
              "minLength": 1
            },
            "minProperties": 1
          },
          "unit": {
            "type": "string"
          },
          "category": {
            "type": "string"
          },
          "mrp_paise": {
            "type": "integer"
          },
          "price_paise": {
            "type": "integer"
          },
          "cost_paise": {
            "type": "integer"
          },
          "details": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "salt": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "strength": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "form": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "pack_size": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "schedule": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "rx_required": {
                "type": "boolean"
              },
              "duration_minutes": {
                "type": "integer",
                "minimum": 1
              },
              "required_skill": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              }
            },
            "required": []
          },
          "frequency": {
            "type": "integer"
          },
          "confidence": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        },
        "required": [
          "id",
          "sku",
          "names",
          "unit",
          "price_paise",
          "frequency"
        ]
      }
    },
    "selected": {
      "anyOf": [
        {
          "type": "object",
          "additionalProperties": false,
          "properties": {
            "id": {
              "type": "string",
              "minLength": 1
            },
            "sku": {
              "type": "string"
            },
            "names": {
              "type": "object",
              "additionalProperties": {
                "type": "string",
                "minLength": 1
              },
              "minProperties": 1
            },
            "unit": {
              "type": "string"
            },
            "category": {
              "type": "string"
            },
            "mrp_paise": {
              "type": "integer"
            },
            "price_paise": {
              "type": "integer"
            },
            "cost_paise": {
              "type": "integer"
            },
            "details": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "salt": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "strength": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "form": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "pack_size": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "schedule": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "rx_required": {
                  "type": "boolean"
                },
                "duration_minutes": {
                  "type": "integer",
                  "minimum": 1
                },
                "required_skill": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                }
              },
              "required": []
            },
            "frequency": {
              "type": "integer"
            },
            "confidence": {
              "type": "number",
              "minimum": 0,
              "maximum": 1
            }
          },
          "required": [
            "id",
            "sku",
            "names",
            "unit",
            "price_paise",
            "frequency"
          ]
        },
        {
          "type": "null"
        }
      ]
    },
    "needs_clarification": {
      "type": "boolean"
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "stage",
    "candidates",
    "selected",
    "needs_clarification",
    "invalidate_on"
  ]
}
```

### contracts/examples/resolution_view.example.json

```json
{
  "stage": "none",
  "candidates": [],
  "selected": null,
  "needs_clarification": false,
  "invalidate_on": [
    "catalog.item_added",
    "catalog.price_changed"
  ]
}
```

### contracts/onboarding_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/onboarding_view.schema.json",
  "title": "OnboardingView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "steps": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "completed": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "next_step": {
      "anyOf": [
        {
          "type": "string"
        },
        {
          "type": "null"
        }
      ]
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "steps",
    "completed",
    "next_step",
    "invalidate_on"
  ]
}
```

### contracts/examples/onboarding_view.example.json

```json
{
  "steps": [
    "language",
    "pack",
    "details",
    "catalog",
    "people"
  ],
  "completed": [],
  "next_step": "language",
  "invalidate_on": [
    "onboarding.updated"
  ]
}
```

### contracts/catalog_search_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/catalog_search_view.schema.json",
  "title": "CatalogSearchView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "items": {
      "type": "array",
      "maxItems": 5,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "id": {
            "type": "string",
            "minLength": 1
          },
          "sku": {
            "type": "string"
          },
          "names": {
            "type": "object",
            "additionalProperties": {
              "type": "string",
              "minLength": 1
            },
            "minProperties": 1
          },
          "unit": {
            "type": "string"
          },
          "category": {
            "type": "string"
          },
          "mrp_paise": {
            "type": "integer"
          },
          "price_paise": {
            "type": "integer"
          },
          "cost_paise": {
            "type": "integer"
          },
          "details": {
            "type": "object",
            "additionalProperties": false,
            "properties": {
              "salt": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "strength": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "form": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "pack_size": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "schedule": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              },
              "rx_required": {
                "type": "boolean"
              },
              "duration_minutes": {
                "type": "integer",
                "minimum": 1
              },
              "required_skill": {
                "type": "string",
                "minLength": 1,
                "maxLength": 200
              }
            },
            "required": []
          },
          "frequency": {
            "type": "integer"
          }
        },
        "required": [
          "id",
          "sku",
          "names",
          "price_paise"
        ]
      }
    },
    "invalidate_on": {
      "type": "array",
      "items": {
        "type": "string"
      }
    }
  },
  "required": [
    "items",
    "invalidate_on"
  ]
}
```

### contracts/examples/catalog_search_view.example.json

```json
{
  "items": [],
  "invalidate_on": [
    "catalog.item_added",
    "catalog.price_changed"
  ]
}
```

### contracts/catalog_item_view.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/catalog_item_view.schema.json",
  "title": "CatalogItemView",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "invalidate_on": {"type":"array","items":{"type":"string"}},
    "id": {
      "type": "string",
      "minLength": 1
    },
    "sku": {
      "type": "string"
    },
    "names": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "minLength": 1
      },
      "minProperties": 1
    },
    "unit": {
      "type": "string"
    },
    "category": {
      "type": "string"
    },
    "mrp_paise": {
      "type": "integer"
    },
    "price_paise": {
      "type": "integer"
    },
    "cost_paise": {
      "type": "integer"
    },
    "details": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "salt": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "strength": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "form": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "pack_size": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "schedule": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "rx_required": {
          "type": "boolean"
        },
        "duration_minutes": {
          "type": "integer",
          "minimum": 1
        },
        "required_skill": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        }
      },
      "required": []
    },
    "frequency": {
      "type": "integer"
    },
    "aliases": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "barcodes": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "hsn": {
      "type": "string"
    },
    "gst_rate_bp": {
      "type": "integer"
    },
    "modifier_groups": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
          },
          "required": {
            "type": "boolean"
          },
          "options": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "name": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "delta_paise": {
                  "type": "integer"
                },
                "id": {
                  "type": "string",
                  "minLength": 1
                }
              },
              "required": [
                "name",
                "delta_paise",
                "id"
              ]
            }
          },
          "id": {
            "type": "string",
            "minLength": 1
          }
        },
        "required": [
          "name",
          "required",
          "options",
          "id"
        ]
      }
    },
    "recipe": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "item_id": {
            "type": "string",
            "minLength": 1
          },
          "qty_milli": {
            "type": "integer",
            "minimum": 1
          }
        },
        "required": [
          "item_id",
          "qty_milli"
        ]
      }
    }
  },
  "required": [
    "id",
    "sku",
    "names",
    "unit",
    "price_paise",
    "modifier_groups",
    "recipe"
  ]
}
```

### contracts/examples/catalog_item_view.example.json

```json
{
  "invalidate_on": ["catalog.item_added", "catalog.price_changed"],
  "id": "item_example",
  "sku": "SALT",
  "names": {
    "en": "Salt"
  },
  "unit": "pcs",
  "price_paise": 2700,
  "modifier_groups": [],
  "recipe": []
}
```

### contracts/commands/staff_logout.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/staff_logout.schema.json",
  "title": "StaffLogout",
  "type": "object",
  "additionalProperties": false,
  "properties": {},
  "required": []
}
```

### contracts/examples/staff_logout.example.json

```json
{}
```

### contracts/commands/staff_login_command.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/staff_login_command.schema.json",
  "title": "StaffLoginCommand",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "staff_id": {
      "type": "string",
      "minLength": 1
    },
    "device_id": {
      "type": "string",
      "minLength": 1
    },
    "channel": {
      "enum": [
        "device",
        "console"
      ]
    }
  },
  "required": [
    "staff_id",
    "device_id",
    "channel"
  ]
}
```

### contracts/examples/staff_login_command.example.json

```json
{
  "staff_id": "staff_example",
  "device_id": "device_example",
  "channel": "device"
}
```

### contracts/commands/staff_login.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/staff_login.schema.json",
  "title": "StaffLogin",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "device_credential": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "staff_id": {
      "type": "string",
      "minLength": 1
    },
    "pin": {
      "type": "string",
      "pattern": "^[0-9]{4,8}$"
    },
    "channel": {
      "enum": [
        "device",
        "console"
      ]
    }
  },
  "required": [
    "device_credential",
    "staff_id",
    "pin",
    "channel"
  ]
}
```

### contracts/examples/staff_login.example.json

```json
{
  "device_credential": "signed-device-example",
  "staff_id": "staff_example",
  "pin": "4826",
  "channel": "device"
}
```

### contracts/commands/staff_add_command.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/staff_add_command.schema.json",
  "title": "StaffAddCommand",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "role": {
      "enum": [
        "owner",
        "manager",
        "cashier",
        "helper"
      ]
    }
  },
  "required": [
    "name",
    "role"
  ]
}
```

### contracts/examples/staff_add_command.example.json

```json
{
  "name": "Asha",
  "role": "cashier"
}
```

### contracts/commands/staff_add.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/staff_add.schema.json",
  "title": "StaffAdd",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "role": {
      "enum": [
        "owner",
        "manager",
        "cashier",
        "helper"
      ]
    },
    "pin": {
      "type": "string",
      "pattern": "^[0-9]{4,8}$"
    }
  },
  "required": [
    "name",
    "role",
    "pin"
  ]
}
```

### contracts/examples/staff_add.example.json

```json
{
  "name": "Asha",
  "role": "cashier",
  "pin": "6194"
}
```

### contracts/commands/shift_open.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/shift_open.schema.json",
  "title": "ShiftOpen",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "float_paise": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": [
    "float_paise"
  ]
}
```

### contracts/examples/shift_open.example.json

```json
{
  "float_paise": 200000
}
```

### contracts/commands/shift_close.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/shift_close.schema.json",
  "title": "ShiftClose",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "shift_id": {
      "type": "string",
      "minLength": 1
    },
    "counted_paise": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": [
    "shift_id",
    "counted_paise"
  ]
}
```

### contracts/examples/shift_close.example.json

```json
{
  "shift_id": "shift_example",
  "counted_paise": 195000
}
```

### contracts/commands/onboarding_complete_step.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/onboarding_complete_step.schema.json",
  "title": "OnboardingCompleteStep",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "step": {
      "enum": [
        "language",
        "pack",
        "details",
        "catalog",
        "people"
      ]
    }
  },
  "required": [
    "step"
  ]
}
```

### contracts/examples/onboarding_complete_step.example.json

```json
{
  "step": "language"
}
```

### contracts/commands/merchant_update_settings.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/merchant_update_settings.schema.json",
  "title": "MerchantUpdateSettings",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "screen_lang": {
      "enum": [
        "hi",
        "en",
        "hi-Latn",
        "mr",
        "ta",
        "bn",
        "gu",
        "te"
      ]
    },
    "speech_lang": {
      "enum": [
        "hi-IN",
        "en-IN",
        "mr-IN",
        "ta-IN",
        "bn-IN",
        "gu-IN",
        "te-IN"
      ]
    },
    "customer_lang": {
      "enum": [
        "hi",
        "en",
        "hi-Latn",
        "mr",
        "ta",
        "bn",
        "gu",
        "te"
      ]
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "vpa": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "address": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "gstin": {
      "type": "string",
      "maxLength": 15
    },
    "tax_profile": {
      "enum": [
        "unregistered",
        "composition",
        "regular"
      ]
    },
    "hours": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        },
        "end": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        }
      },
      "required": [
        "start",
        "end"
      ]
    },
    "quiet_hours": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "start": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        },
        "end": {
          "type": "string",
          "pattern": "^([01][0-9]|2[0-3]):[0-5][0-9]$"
        }
      },
      "required": [
        "start",
        "end"
      ]
    }
  },
  "required": [],
  "minProperties": 1
}
```

### contracts/examples/merchant_update_settings.example.json

```json
{
  "screen_lang": "ta",
  "speech_lang": "hi-IN",
  "customer_lang": "en"
}
```

### contracts/commands/merchant_bootstrap.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/merchant_bootstrap.schema.json",
  "title": "MerchantBootstrap",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1
    },
    "pack": {
      "type": "string",
      "minLength": 1
    },
    "owner_id": {
      "type": "string",
      "minLength": 1
    },
    "owner_name": {
      "type": "string",
      "minLength": 1
    },
    "device_id": {
      "type": "string",
      "minLength": 1
    }
  },
  "required": [
    "name",
    "pack",
    "owner_id",
    "owner_name",
    "device_id"
  ]
}
```

### contracts/examples/merchant_bootstrap.example.json

```json
{
  "name": "Example Shop",
  "pack": "kirana",
  "owner_id": "staff_example",
  "owner_name": "Owner",
  "device_id": "device_example"
}
```

### contracts/commands/catalog_import_items.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/catalog_import_items.schema.json",
  "title": "CatalogImportItems",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "confirmed": {
      "const": true
    },
    "items": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "$ref": "catalog_add_item.schema.json"
      }
    }
  },
  "required": [
    "confirmed",
    "items"
  ]
}
```

### contracts/examples/catalog_import_items.example.json

```json
{
  "confirmed": true,
  "items": [
    {
      "sku": "TATA-SALT-1KG",
      "names": {
        "en": "Tata Salt",
        "hi": "टाटा नमक",
        "hi-Latn": "Tata namak"
      },
      "unit": "pcs",
      "mrp_paise": 2800,
      "price_paise": 2700,
      "cost_paise": 2300,
      "category": "staples",
      "aliases": [
        "namak"
      ],
      "barcodes": [
        "8901000000001"
      ],
      "hsn": "2501",
      "gst_rate_bp": 0
    }
  ]
}
```

### contracts/commands/catalog_change_price.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/catalog_change_price.schema.json",
  "title": "CatalogChangePrice",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "item_id": {
      "type": "string",
      "minLength": 1
    },
    "price_paise": {
      "type": "integer",
      "minimum": 0
    }
  },
  "required": [
    "item_id",
    "price_paise"
  ]
}
```

### contracts/examples/catalog_change_price.example.json

```json
{
  "item_id": "item_example",
  "price_paise": 2900
}
```

### contracts/commands/catalog_bulk_price.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/catalog_bulk_price.schema.json",
  "title": "CatalogBulkPrice",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "prices": {
      "type": "array",
      "minItems": 1,
      "maxItems": 500,
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "item_id": {
            "type": "string",
            "minLength": 1
          },
          "price_paise": {
            "type": "integer",
            "minimum": 0
          }
        },
        "required": [
          "item_id",
          "price_paise"
        ]
      }
    }
  },
  "required": [
    "prices"
  ]
}
```

### contracts/examples/catalog_bulk_price.example.json

```json
{
  "prices": [
    {
      "item_id": "item_example",
      "price_paise": 2900
    }
  ]
}
```

### contracts/commands/catalog_add_item.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/commands/catalog_add_item.schema.json",
  "title": "CatalogAddItem",
  "type": "object",
  "additionalProperties": false,
  "properties": {
    "sku": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "names": {
      "type": "object",
      "additionalProperties": {
        "type": "string",
        "minLength": 1
      },
      "minProperties": 1
    },
    "unit": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "mrp_paise": {
      "type": "integer",
      "minimum": 0
    },
    "price_paise": {
      "type": "integer",
      "minimum": 0
    },
    "cost_paise": {
      "type": "integer",
      "minimum": 0
    },
    "category": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "aliases": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "maxLength": 200
      },
      "uniqueItems": true
    },
    "barcodes": {
      "type": "array",
      "items": {
        "type": "string",
        "pattern": "^[0-9]{8,14}$"
      },
      "uniqueItems": true
    },
    "hsn": {
      "type": "string",
      "pattern": "^[0-9]{4,8}$"
    },
    "gst_rate_bp": {
      "type": "integer",
      "minimum": 0,
      "maximum": 10000
    },
    "details": {
      "type": "object",
      "additionalProperties": false,
      "properties": {
        "salt": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "strength": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "form": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "pack_size": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "schedule": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        },
        "rx_required": {
          "type": "boolean"
        },
        "duration_minutes": {
          "type": "integer",
          "minimum": 1
        },
        "required_skill": {
          "type": "string",
          "minLength": 1,
          "maxLength": 200
        }
      },
      "required": []
    },
    "modifier_groups": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "name": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
          },
          "required": {
            "type": "boolean"
          },
          "options": {
            "type": "array",
            "minItems": 1,
            "items": {
              "type": "object",
              "additionalProperties": false,
              "properties": {
                "name": {
                  "type": "string",
                  "minLength": 1,
                  "maxLength": 200
                },
                "delta_paise": {
                  "type": "integer"
                }
              },
              "required": [
                "name",
                "delta_paise"
              ]
            }
          }
        },
        "required": [
          "name",
          "required",
          "options"
        ]
      }
    },
    "recipe": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "item_id": {
            "type": "string",
            "minLength": 1
          },
          "qty_milli": {
            "type": "integer",
            "minimum": 1
          }
        },
        "required": [
          "item_id",
          "qty_milli"
        ]
      }
    }
  },
  "required": [
    "sku",
    "names",
    "unit",
    "price_paise",
    "cost_paise",
    "mrp_paise",
    "category"
  ]
}
```

### contracts/examples/catalog_add_item.example.json

```json
{
  "sku": "TATA-SALT-1KG",
  "names": {
    "en": "Tata Salt",
    "hi": "टाटा नमक",
    "hi-Latn": "Tata namak"
  },
  "unit": "pcs",
  "mrp_paise": 2800,
  "price_paise": 2700,
  "cost_paise": 2300,
  "category": "staples",
  "aliases": [
    "namak"
  ],
  "barcodes": [
    "8901000000001"
  ],
  "hsn": "2501",
  "gst_rate_bp": 0
}
```

### contracts/events/staff_shift_opened.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/staff_shift_opened.schema.json",
  "title": "StaffShiftOpened",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "staff.shift_opened"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "shift_id",
        "staff_id"
      ],
      "properties": {
        "shift_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        "staff_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/staff_shift_opened.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "staff.shift_opened",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "shift_id": "shift_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
    "staff_id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  }
}
```

### contracts/events/staff_shift_closed.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/staff_shift_closed.schema.json",
  "title": "StaffShiftClosed",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "staff.shift_closed"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "shift_id",
        "variance_paise"
      ],
      "properties": {
        "shift_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        "variance_paise": {
          "type": "integer"
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/staff_shift_closed.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "staff.shift_closed",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "shift_id": "shift_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
    "variance_paise": -5000
  }
}
```

### contracts/events/staff_logged_in.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/staff_logged_in.schema.json",
  "title": "StaffLoggedIn",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "staff.logged_in"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "staff_id",
        "session_id"
      ],
      "properties": {
        "staff_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        "session_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/staff_logged_in.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "staff.logged_in",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "staff_id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
    "session_id": "session_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  }
}
```

### contracts/events/staff_added.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/staff_added.schema.json",
  "title": "StaffAdded",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "staff.added"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "staff_id",
        "role"
      ],
      "properties": {
        "staff_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        "role": {
          "enum": [
            "owner",
            "manager",
            "cashier",
            "helper"
          ]
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/staff_added.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "staff.added",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "staff_id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
    "role": "helper"
  }
}
```

### contracts/events/onboarding_updated.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/onboarding_updated.schema.json",
  "title": "OnboardingUpdated",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "onboarding.updated"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "step"
      ],
      "properties": {
        "step": {
          "enum": [
            "language",
            "pack",
            "details",
            "catalog",
            "people"
          ]
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/onboarding_updated.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "onboarding.updated",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "step": "language"
  }
}
```

### contracts/events/onboarding_started.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/onboarding_started.schema.json",
  "title": "OnboardingStarted",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "onboarding.started"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "device_id"
      ],
      "properties": {
        "device_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/onboarding_started.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "onboarding.started",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "device_id": "device_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  }
}
```

### contracts/events/i18n_changed.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/i18n_changed.schema.json",
  "title": "LanguageChanged",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "i18n.changed"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "screen_lang",
        "speech_lang",
        "customer_lang"
      ],
      "properties": {
        "screen_lang": {
          "enum": [
            "hi",
            "en",
            "hi-Latn",
            "mr",
            "ta",
            "bn",
            "gu",
            "te"
          ]
        },
        "speech_lang": {
          "enum": [
            "hi-IN",
            "en-IN",
            "mr-IN",
            "ta-IN",
            "bn-IN",
            "gu-IN",
            "te-IN"
          ]
        },
        "customer_lang": {
          "enum": [
            "hi",
            "en",
            "hi-Latn",
            "mr",
            "ta",
            "bn",
            "gu",
            "te"
          ]
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/i18n_changed.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "i18n.changed",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "screen_lang": "ta",
    "speech_lang": "hi-IN",
    "customer_lang": "en"
  }
}
```

### contracts/events/catalog_price_changed.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/catalog_price_changed.schema.json",
  "title": "CatalogPriceChanged",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "catalog.price_changed"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "item_id",
        "price_paise"
      ],
      "properties": {
        "item_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        "price_paise": {
          "type": "integer",
          "minimum": 0
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/catalog_price_changed.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "catalog.price_changed",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "item_id": "item_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
    "price_paise": 2600
  }
}
```

### contracts/events/catalog_item_added.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/catalog_item_added.schema.json",
  "title": "CatalogItemAdded",
  "description": "Base shape of every Event Spine event (spec Part C5). Per-topic payload schemas arrive with their layer (see contracts/README.md).",
  "type": "object",
  "required": [
    "event_id",
    "type",
    "merchant_id",
    "occurred_at",
    "actor",
    "causation_id",
    "payload"
  ],
  "additionalProperties": false,
  "properties": {
    "event_id": {
      "type": "string",
      "pattern": "^evt_[0-9A-HJKMNP-TV-Z]{26}$"
    },
    "type": {
      "const": "catalog.item_added"
    },
    "merchant_id": {
      "$ref": "../common.schema.json#/definitions/NonEmptyString"
    },
    "occurred_at": {
      "type": "string",
      "format": "date-time"
    },
    "actor": {
      "$ref": "#/definitions/Actor"
    },
    "causation_id": {
      "anyOf": [
        {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        },
        {
          "type": "null"
        }
      ],
      "description": "Id of the command or event that caused this event; null means a root event with no cause (e.g. a clock tick)."
    },
    "payload": {
      "type": "object",
      "additionalProperties": false,
      "required": [
        "item_id"
      ],
      "properties": {
        "item_id": {
          "$ref": "../common.schema.json#/definitions/PrefixedId"
        }
      }
    }
  },
  "definitions": {
    "Actor": {
      "type": "object",
      "required": [
        "kind"
      ],
      "additionalProperties": false,
      "properties": {
        "kind": {
          "type": "string",
          "enum": [
            "owner",
            "staff",
            "customer",
            "supplier",
            "agent",
            "system",
            "simulator"
          ]
        },
        "id": {
          "anyOf": [
            {
              "$ref": "../common.schema.json#/definitions/NonEmptyString"
            },
            {
              "type": "null"
            }
          ]
        }
      }
    }
  }
}
```

### contracts/examples/catalog_item_added.example.json

```json
{
  "event_id": "evt_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "type": "catalog.item_added",
  "merchant_id": "merchant_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "occurred_at": "2026-10-30T04:00:00Z",
  "actor": {
    "kind": "owner",
    "id": "staff_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  },
  "causation_id": "cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0",
  "payload": {
    "item_id": "item_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0"
  }
}
```

