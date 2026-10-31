# Arth L1a Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans inline. Steps use checkbox syntax. No git or subagents; tasks end with a Checkpoint.

**Goal:** Establish merchant isolation and the command, policy, approval, audit and event-delivery foundation for later commerce modules.

**Architecture:** SQLAlchemy Core repositories inject merchant scope on every query. The single-writer transaction owns command execution, hash-chained audit and durable outbox insertion. Approval scopes bind canonical payloads and conditions; consumers commit their effects and offsets together.

**Tech Stack:** Existing Python 3.12/FastAPI, SQLite, Alembic, Pydantic/JSON Schema and generated TypeScript; no new dependencies.

**Spec:** `docs/specs/2026-10-30-arth-v6-merged-design.md` C1–C6, D1, F2.1, K2 T1.1–T1.6, L2; `docs/reference/Arth_Spec_v5.1.md` D2–D5, D11, E4, GOV-1/2, WFL-3/4, AIQ-1. `docs/HANDOFF-L1.md` narrows T1.1 to foundation tables.

## Global Constraints

- No git. Never inspect backend/.env. Settings alone loads secrets.
- Use SimClock, integer paise/milli-units and prefixed IDs. Merchant identity comes from a trusted session, never request bodies.
- Contracts first; run `python dev.py gen`; never edit generated files.
- TDD with recorded RED/GREEN output. Review every task against spec IDs, then quality, before each batch gate.
- Preserve CRLF in this plan. Use `python -m uv`; full gate is `python dev.py check`.

## Review Focus

- Cross-merchant IDs and update payloads cannot escape repository scope (Task 1).
- Unknown types, untrusted role assertions and R4 voice requests fail closed (Tasks 2, 4).
- Approval expiry, changed payloads and helper/customer voice replies cannot authorize execution (Task 5).
- Rollback leaves no domain effect, audit row or outbox row; concurrent replays execute once (Task 4).
- Consumer failure preserves its offset; restart/replay does not duplicate durable effects (Task 6).

## File structure

```text
backend/arth/governance/tables.py       eight foundation tables
backend/arth/governance/repository.py   scoped SQL operations
backend/arth/governance/policy.py       roles and contextual policy decisions
backend/arth/governance/audit.py        canonical JSON and chain verification
backend/arth/governance/commands.py     registry and transactional execution
backend/arth/governance/approvals.py    scope-bound durable gates
backend/arth/governance/events.py       outbox consumers and live broadcaster
backend/arth/api/governance.py          authenticated foundation endpoints
backend/migrations/versions/0002_l1a_foundation.py
backend/tests/test_governance_*.py      real SQLite tests and API acceptance
contracts/*, contracts/events/*        command, approval, audit and event schemas
```

## Batch A: governance primitives (three tasks)

### Task 1: Data model and tenancy (T1.1; v5.1 D2/D3, C1)

**Files:** Create governance package, tables, repository, migration 0002 and `test_governance_repository.py`; modify migrations/env.py.

**Interfaces:** `Repository(conn, merchant_id)` exposes select/insert/update with injected tenant predicates; all foundation tables have merchant_id. Commands have unique (merchant_id, idempotency_key); audit/outbox sequence keys; offsets unique per merchant/consumer.

- [x] Write isolation, tenant-override and migration-drift tests; inspect JSON checks and tenant/key uniqueness in the model and frozen migration.
- [x] Run `cd backend; python -m uv run pytest tests/test_governance_repository.py -q`; expected RED for missing package.
- [x] Implement tables, explicit migration and scoped repository. Reject raw SQL and foreign tenant values.
- [x] Run targeted tests; expected PASS. Review D2/D3/C1, then SQL constraints and repository API.
- [x] Checkpoint: targeted tests green; retain RED output in execution record.

### Task 2: Policy Engine (T1.3; GOV-1, STF-1, PAT-3, LED-4/6, D11, D1)

**Files:** Create policy.py and test_governance_policy.py.

**Interfaces:** immutable `Session` contains merchant, actor, role, channel, device, owner PTT and verified step-up facts. `PolicyContext` contains trusted consent/contact/budget/margin facts supplied by handlers, never by HTTP payload. `PolicyEngine.evaluate(type, tier, session, context)` returns stable policy codes (including quiet-hours deferral reasons) and discreet decisions.

- [x] Write role/tier, R4 channel/step-up, consent, quiet boundary, weekly cap, discreet, R1 class and tightened pack tests.
- [x] Run `cd backend; python -m uv run pytest tests/test_governance_policy.py -q`; expected RED.
- [x] Implement deterministic policy checks using pack-merged Policies and SimClock.
- [x] Run targeted tests; expected PASS. Review D11/AIQ-1 and fail-closed behavior, then quality.
- [x] Checkpoint: targeted tests green.

### Task 3: Audit Ledger (T1.5; GOV-2)

**Files:** Create audit.py and test_governance_audit.py.

**Interfaces:** `append_audit(repo, clock, command_id, action, data)` writes canonical row and SHA256(prev_hash + canonical row); `verify_audit(repo)` returns validity, checked count and first bad sequence.

- [x] Write multi-tenant chain and tamper tests; inspect strict canonical ordering and verify rollback in the integrated Command Bus tests.
- [x] Run `cd backend; python -m uv run pytest tests/test_governance_audit.py -q`; expected RED.
- [x] Implement strict canonical JSON (no NaN), append and verifier including sequence/predecessor checks.
- [x] Run targeted tests; expected PASS. Review GOV-2 then mutation and error paths.
- [x] Batch A gate: self-review each task; `python dev.py check`; expected exit 0 before Batch B.

## Batch B: command flow and delivery (three tasks)

### Task 4: Typed Command Bus (T1.2; GOV-1/2, C1/C6)

**Files:** Create command schemas/examples, commands.py and test_governance_commands.py; regenerate contracts.

**Interfaces:** `CommandBus.register(type, schema, handler, context)` registers strict payload validation and trusted policy facts. `submit(session, type, payload, key, conditions)` returns persisted command result/envelope, gate or send-queue state. Handlers receive only the scoped repository and validated payload.

- [x] Add contracts first, examples, then run `python dev.py gen`.
- [x] Write invalid schema, unknown tier, replay/conflict, concurrency and transactional rollback tests; run targeted pytest and capture RED.
- [x] Implement registration, strict validation, policy/approval hooks, atomic domain+audit+outbox+result. Unknown commands are refused; later domain modules register their handlers.
- [x] Run targeted tests; expected PASS. Review GOV-1/2 and C1/C6 then transaction ownership and error handling.
- [x] Checkpoint: targeted tests green.

### Task 5: Approval Service (T1.4; WFL-3/4, AIQ-1, D11/E4)

**Files:** Create approval contracts/examples, approvals.py and test_governance_approvals.py; regenerate contracts.

**Interfaces:** `scope_hash(type, payload, conditions)`; gates persist actor-bound scopes, 12h R3 expiry, single/batch/series/plan metadata. Decisions are approve/snooze/edit with per-gate partial choices (maximum five). Reuse requires exact declared scope plus evaluated trusted conditions; changed scope creates a fresh gate. R3 approval produces a durable due_at 30 seconds later and policy is checked again before dispatch.

- [x] Write owner/helper/PTT, scope mismatch, expiry, partial batch, series/plan and conditional threshold tests; run targeted pytest and capture RED.
- [x] Implement gate creation/decision/reuse with atomic audit/outbox and persisted results; reject stale or foreign gates.
- [x] Run targeted tests; expected PASS. Review WFL-3/4 and AIQ-1 then authorization and race paths.
- [x] Checkpoint: targeted tests green.

### Task 6: Outbox, dispatcher, routes and CP-1a (T1.6; D5, C2/C5)

**Files:** Create events.py, api/governance.py, event contracts/examples and integration tests; modify stream.py, main.py and openapi.yaml; keep the L0 token stub and add the session dependency in api/governance.py.

**Interfaces:** durable consumer callback `(Repository, event) -> None`, offset committed with effects; broadcaster publishes tenant-filtered domain events alongside existing spans. View dependencies derive view.invalidate without recursion. HTTP routes POST /v1/commands, POST /v1/approvals/{thread_id}, GET /v1/audit/verify resolve only trusted sessions; full staff/PIN login remains T1.8.

- [x] Update OpenAPI/event contracts, regenerate, write failure/restart/deduplication/invalidation/SSE/auth and real API tests; capture RED.
- [x] Implement dispatcher lifecycle, tenant-filtered SSE and routes; queue execution uses SimClock and rechecks policy.
- [x] Run targeted tests; expected PASS. Review D5/C2/C5 then cancellation, offsets and stream cleanup.
- [x] Batch B gate: review every task spec-first then quality; fix with regression RED/GREEN; run `python dev.py check`.
- [x] CP-1a: record tests proving GOV-1 tier enforcement, GOV-2 tamper detection, WFL-3 scope, WFL-4 partial batch data, AIQ-1 owner binding, idempotency, tenancy and event replay. Update plan index only after gate passes.

## Execution record

**CP-1a complete, 30 Oct 2026.** Final `python dev.py check` exit 0: generators current (14 Python files, 28 frontend files), Ruff/Prettier/mypy/tsc clean, **447 pytest passed, 1 existing Starlette/httpx deprecation warning; 127 Vitest passed (4 files)**. Batch A gate passed before Batch B began. Every task received spec-first and code-quality self-review. No git commands or subagents were used; backend/.env was never inspected.

Task 1: complete — merchant isolation/override and migration tests plus scoped-query AST guard. Task 2: complete — roles, consent, quiet boundaries, caps, discreet, R1 classes and pack enforcement. Task 3: complete — full-row audit hash, payload/sequence tamper and transactional rollback. Task 4: complete — strict typed registry, concurrent stored-result replay and atomic execution. Task 5: complete — owner voice binding, tap permissions, scope/conditions, explicit batch/series/plan manifests, edits, expiry and cancellable send queue. Task 6: complete — durable consumer offsets/restart, API contracts and merchant-filtered SSE/view invalidation.

Final deferred minors: none identified. Implementation remains the foundation scope described in the rulings below; complete staff login, domain commands and screen views remain in T1.7–T1.23.

Baseline: `python dev.py check` exited 0: 388 pytest passed (one existing Starlette/httpx deprecation warning), 118 Vitest passed. Initial sandbox attempt failed on uv cache permissions and Corepack DNS; authorized elevated retry passed.

Ruling: the handoff narrows T1.1 to foundation tables; remaining F2.2 tables belong to L1b+. Cost if wrong: later domain modules require their own migrations, as intended by just-in-time layer planning.

Ruling: use the existing checkout and manual non-git checkpoint record; git-dependent skill scripts and all reviewer subagents are excluded by user instruction. Cost: author self-review provides no independent reviewer.

Batch A RED: four failures, all ModuleNotFoundError for missing arth.governance. Initial focused GREEN: 6 passed (including migration drift). Full gate then caught Ruff B008/E731; corrected defaults and named helper. After freezing migration definitions, the full suite caught four unnamed unique constraints; copied the L0 naming convention into frozen migration metadata. Gate rerun pending.

Batch A gate: exit 0; 392 pytest passed (one existing warning), 118 Vitest passed. Spec-first self-review: T1.1 D2/D3/C1 scoped table operations and JSON constraints; T1.3 D11 role/consent/quiet/cap/discreet policy; T1.5 GOV-2 chained audit. Quality review fixed migration independence and naming parity. Later integrated review added the complete-row sequence hash regression.

Batch B RED: five failures for missing commands/events modules. Initial GREEN: replay/concurrency/rollback and event-offset tests; approval fixture was corrected to include the owner's device identity. Scope/envelope RED: four failures (missing batch API, trusted facts and envelope language); GREEN: 8 passed. API/SSE RED: two failures (missing session wiring and invalid derived event ID); GREEN: 11 passed including documented route equality.

Review fix record: stale conditional-gate replay RED then GREEN; discreet envelope, queued-send cancellation, manager tap versus voice, and pack policy wiring all RED then GREEN (8 focused tests). Sequence-column tampering RED then GREEN (2 audit tests). Approval scope/envelope presentation RED then GREEN. Queued-scope mutation RED then GREEN (16 scope/safety tests). Existing schema-discovery and codegen-error tests updated for the expanded contract inventory after the full gate exposed L0-only assumptions.

Ruling: keep server-provisioned sessions as the L1a authentication seam; do not add staff/PIN login ahead of T1.8 or infer merchant/owner identity from surface tokens. Cost if wrong: live use of foundation routes needs trusted session provisioning until L1b adds login.

Ruling: series and plan scopes are bounded manifests of explicit command gates (up to five), not open-ended permissions. Each command's canonical payload and conditions remain independently bound; newly proposed actions get fresh gates. Cost if wrong: larger/dynamic plans require another approval batch or a later explicit scope extension.

Ruling: result-envelope language defaults to hi-Latn/hi-IN until merchant language settings are implemented in T1.7. Cost if wrong: other locales require that settings integration before live UI use.

## CP-1a acceptance evidence

| Acceptance | Tests |
|---|---|
| T1.1 tenancy and migration drift | test_governance_repository; test_governance_safety::test_domain_sql_execution_is_centralized_in_scoped_repository; test_migrations |
| GOV-1 schema/tier/policy enforcement | test_governance_commands; test_governance_policy; test_governance_review; quiet-hour and R1-class parameter tables in test_governance_safety |
| Idempotency, concurrent replay, atomic rollback | test_governance_commands::test_command_replay_concurrency_conflict_and_atomic_rollback |
| GOV-2 full-row hash and tamper | test_governance_audit (payload and sequence tamper) |
| WFL-3 conditions and exact scope | test_governance_scopes; fresh-conditional-gate replay test in test_governance_safety |
| WFL-4 partial batch data | test_governance_scopes::test_partial_batch_and_plan_scope_are_explicit |
| AIQ-1 owner PTT and staff permissions | test_governance_approvals; test_governance_review::test_manager_can_tap_r2_but_cannot_voice_approve |
| 30-second durable send queue and cancellation | test_governance_approvals; test_governance_review::test_queue_can_be_cancelled_before_send |
| T1.6 consumer offsets, rollback and restart | test_governance_events::test_consumer_failure_retries_without_duplicate_effect |
| Contracts, API sessions, SSE invalidation and tenant filtering | test_governance_api; test_openapi_contract; shared example round-trips in pytest/Vitest |

Final review: self-review by author, per explicit no-subagents instruction. No independent review. Full gate result will be recorded below before CP-1a is marked complete.

Gate follow-up: backend 447 passed, one existing warning. Vitest first exposed two L0-only inventory assertions (updated); the next full run hit a worker module-fetch timeout before contract test collection. Isolated reproduction passed: 24 contract tests in 1.91s. No implementation/config change was made for the non-reproducing worker timeout; a fresh full gate is running. Source snapshot verification: 36 blocks, zero mismatches.


## Contract and compatibility source snapshot

### contracts/command.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/command.schema.json",
  "type": "object",
  "additionalProperties": false,
  "title": "CommandRequest",
  "required": [
    "type",
    "payload"
  ],
  "properties": {
    "type": {
      "$ref": "common.schema.json#/definitions/DottedCode"
    },
    "payload": {
      "type": "object"
    }
  }
}
```

### contracts/command_result.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/command_result.schema.json",
  "title": "CommandResult",
  "type": "object",
  "additionalProperties": false,
  "required": [
    "command_id",
    "status"
  ],
  "properties": {
    "scope": {
      "type": "object", "additionalProperties": false, "required": ["type", "payload", "conditions"],
      "properties": {"type": {"type": "string"}, "payload": {"type": "object"}, "conditions": {"type": "object"}}
    },
    "expires_at": {"type": "string", "format": "date-time"},
    "command_id": {
      "$ref": "common.schema.json#/definitions/PrefixedId"
    },
    "status": {
      "enum": [
        "executed",
        "needs_approval",
        "queued",
        "snoozed"
      ]
    },
    "tier": {
      "$ref": "common.schema.json#/definitions/Tier"
    },
    "data": {
      "type": "object"
    },
    "envelope": {
      "$ref": "envelope.schema.json"
    },
    "gate_id": {
      "$ref": "common.schema.json#/definitions/PrefixedId"
    },
    "thread_id": {
      "$ref": "common.schema.json#/definitions/PrefixedId"
    },
    "due_at": {
      "type": "string",
      "format": "date-time"
    }
  }
}
```

### contracts/approval.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/approval.schema.json",
  "type": "object",
  "additionalProperties": false,
  "title": "ApprovalRequest",
  "required": [
    "decision"
  ],
  "properties": {
    "decision": {
      "enum": [
        "approve",
        "snooze",
        "edit"
      ]
    },
    "edits": {
      "type": "object"
    },
    "decisions": {
      "type": "object",
      "additionalProperties": {
        "enum": [
          "approve",
          "snooze"
        ]
      }
    }
  }
}
```

### contracts/audit_verification.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/audit_verification.schema.json",
  "type": "object",
  "additionalProperties": false,
  "title": "AuditVerification",
  "required": [
    "valid",
    "checked",
    "bad_seq"
  ],
  "properties": {
    "valid": {
      "type": "boolean"
    },
    "checked": {
      "type": "integer",
      "minimum": 0
    },
    "bad_seq": {
      "anyOf": [
        {
          "type": "integer",
          "minimum": 1
        },
        {
          "type": "null"
        }
      ]
    }
  }
}
```

### contracts/events/command_executed.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/command_executed.schema.json",
  "title": "CommandExecuted",
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
      "const": "command.executed"
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
      "$ref": "../command_result.schema.json"
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

### contracts/events/approval_requested.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/approval_requested.schema.json",
  "title": "ApprovalRequested",
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
      "const": "approval.requested"
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
      "$ref": "../command_result.schema.json"
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

### contracts/events/approval_decided.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/approval_decided.schema.json",
  "title": "ApprovalDecided",
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
      "const": "approval.decided"
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
      "$ref": "../command_result.schema.json"
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

### contracts/events/audit_verified.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/audit_verified.schema.json",
  "title": "AuditVerified",
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
      "const": "audit.verified"
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
      "$ref": "../audit_verification.schema.json"
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

### contracts/events/view_invalidate.schema.json

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://arth.local/contracts/events/view_invalidate.schema.json",
  "title": "ViewInvalidate",
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
      "const": "view.invalidate"
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
        "views"
      ],
      "properties": {
        "views": {
          "type": "array",
          "items": {
            "type": "string"
          },
          "minItems": 1
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

### backend/tests/test_gen_contracts.py

```python
import json
import sys
from pathlib import Path

import pytest

from arth.tools import gen_contracts as gen


def _schema(root: Path, rel: str, body: dict[str, object]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"$id": f"https://arth.local/contracts/{rel}", "title": Path(rel).name.split(".")[0].title()} | body
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_stage_flattens_files_and_rewrites_cross_file_refs(tmp_path: Path) -> None:
    src, stage = tmp_path / "contracts", tmp_path / "stage"
    _schema(src, "common.schema.json", {"definitions": {"X": {"type": "string"}}})
    ref = {"$ref": "../common.schema.json#/definitions/X"}
    _schema(src, "events/ev.schema.json", {"properties": {"x": ref}})
    gen.stage(src, stage)
    assert sorted(p.name for p in stage.iterdir()) == ["common.json", "ev.json"]
    staged = json.loads((stage / "ev.json").read_text(encoding="utf-8"))
    assert staged["properties"]["x"]["$ref"] == "common.json#/definitions/X"


def test_stage_rejects_refs_to_files_that_are_not_contracts(tmp_path: Path) -> None:
    src = tmp_path / "contracts"
    _schema(src, "a.schema.json", {"properties": {"x": {"$ref": "nowhere.schema.json#/definitions/X"}}})
    with pytest.raises(gen.GenError, match=r"a\.schema\.json.*nowhere\.schema\.json"):
        gen.stage(src, tmp_path / "stage")


def test_stale_lists_changed_missing_and_extra_files(tmp_path: Path) -> None:
    (tmp_path / "same.py").write_bytes(b"x\n")
    (tmp_path / "changed.py").write_bytes(b"old\n")
    (tmp_path / "extra.py").write_bytes(b"gone\n")
    expected = {"same.py": b"x\n", "changed.py": b"new\n", "missing.py": b"m\n"}
    assert gen.stale(expected, tmp_path) == ["changed.py", "extra.py", "missing.py"]


def test_codegen_failure_names_the_contracts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gen, "CODEGEN", [sys.executable, "-c", "import sys; sys.exit('boom')"])
    expected = r"(?s)datamodel-codegen failed for contracts .*common, envelope.*boom"
    with pytest.raises(gen.GenError, match=expected):
        gen.render()


def test_check_mode_reports_stale_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "leftover.py").write_bytes(b"# old\n")
    monkeypatch.setattr(gen, "OUT", tmp_path)
    monkeypatch.setattr(gen, "render", lambda: {"__init__.py": b"# h\n", "thing.py": b"# h\nx = 1\n"})
    assert gen.main(["--check"]) == 1
    assert (tmp_path / "leftover.py").exists(), "--check must never write or delete"
    assert gen.main([]) == 0
    assert not (tmp_path / "leftover.py").exists(), "gen removes modules that no longer match a contract"
    assert gen.main(["--check"]) == 0


def test_committed_models_are_fresh() -> None:
    assert gen.stale(gen.render(), gen.OUT) == [], "contracts are stale: run `python dev.py gen`"
```



## Implemented source snapshot

Shared-file snapshots synchronized after L1b on 30 Oct 2026; the CP-1a test counts above remain historical. L1b adds persisted sessions, domain registration and startup tenant-directory recovery. See its plan for the new interfaces and review rulings.

These fenced blocks equal the authored files on disk at CP-1a. Generated files are deliberately omitted.

### backend/arth/governance/__init__.py

```python
"""Merchant-scoped commerce governance (L1a)."""
```

### backend/arth/governance/tables.py

```python
"""Foundation storage; all domain rows carry explicit merchant ownership."""

from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from arth.core.db import metadata


def tenant() -> Column[str]:
    return Column("merchant_id", String, nullable=False, index=True)


merchants = Table(
    "merchants",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("name", String, nullable=False),
    Column("pack", String, nullable=False),
)
merchant_settings = Table(
    "merchant_settings",
    metadata,
    tenant(),
    Column("settings", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id"),
    CheckConstraint("json_valid(settings)"),
)
staff = Table(
    "staff",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("role", String, nullable=False),
    Column("name", String, nullable=False),
)
commands = Table(
    "commands",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("idempotency_key", String, nullable=False),
    Column("type", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("payload", Text, nullable=False),
    Column("result", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id", "idempotency_key"),
    CheckConstraint("json_valid(payload) AND json_valid(result)"),
)
approvals = Table(
    "approvals",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("thread_id", String, nullable=False),
    Column("command_id", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("conditions", Text, nullable=False),
    Column("scope", Text, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("due_at", String),
    Column("approved_by", String),
    CheckConstraint("json_valid(conditions) AND json_valid(scope)"),
)
audit_log = Table(
    "audit_log",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("command_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("data", Text, nullable=False),
    Column("prev_hash", String, nullable=False),
    Column("hash", String, nullable=False),
    CheckConstraint("json_valid(data)"),
)
outbox = Table(
    "outbox",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("event_id", String, nullable=False, unique=True),
    Column("type", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("payload", Text, nullable=False),
    CheckConstraint("json_valid(payload)"),
)
consumer_offsets = Table(
    "consumer_offsets",
    metadata,
    tenant(),
    Column("consumer", String, nullable=False),
    Column("last_seq", Integer, nullable=False),
    UniqueConstraint("merchant_id", "consumer"),
)
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

### backend/arth/governance/audit.py

```python
"""Canonical tenant-local SHA256 audit chain (GOV-2)."""

import hashlib
import json
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.governance.repository import Repository
from arth.governance.tables import audit_log


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(previous: str, row: dict[str, Any]) -> str:
    return hashlib.sha256((previous + canonical(row)).encode()).hexdigest()


async def append_audit(
    repo: Repository, clock: SimClock, command_id: str, action: str, data: dict[str, Any]
) -> None:
    rows = sorted(await repo.select(audit_log), key=lambda r: r["seq"])
    previous = rows[-1]["hash"] if rows else ""
    row = {
        "merchant_id": repo.merchant_id,
        "command_id": command_id,
        "action": action,
        "occurred_at": iso_utc(clock.now()),
        "data": canonical(data),
        "prev_hash": previous,
    }
    await repo.insert(audit_log, {**row, "hash": ""})
    stored = max(await repo.select(audit_log), key=lambda r: r["seq"])
    await repo.update(
        audit_log, {"hash": digest(previous, {**row, "seq": stored["seq"]})}, audit_log.c.seq == stored["seq"]
    )


async def verify_audit(repo: Repository) -> dict[str, Any]:
    previous = ""
    checked = 0
    for stored in sorted(await repo.select(audit_log), key=lambda r: r["seq"]):
        row = {k: v for k, v in stored.items() if k != "hash"}
        if row["prev_hash"] != previous or digest(previous, row) != stored["hash"]:
            return {"valid": False, "checked": checked, "bad_seq": stored["seq"]}
        previous = stored["hash"]
        checked += 1
    return {"valid": True, "checked": checked, "bad_seq": None}
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

### backend/arth/governance/approvals.py

```python
"""Scope-bound gate primitives; decisions execute inside the command transaction."""

import hashlib
from datetime import timedelta
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.governance.audit import canonical
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import approvals


def scope_hash(kind: str, payload: dict[str, Any], conditions: dict[str, Any]) -> str:
    return hashlib.sha256((kind + canonical(payload) + canonical(conditions)).encode()).hexdigest()


def envelope(tier: str, *, needs_you: bool = False) -> dict[str, Any]:
    return {
        "turn_id": new_id("turn"),
        "lang": {"screen": "hi-Latn", "speech": "hi-IN"},
        "audience": "owner",
        "cards": [],
        "followups": [],
        "provenance": [],
        "presence": {"state": "needs_you" if needs_you else "done"},
        "sensitivity": "normal",
        "tier": tier,
    }


def can_approve(session: Session, tier: str, permissions: list[str]) -> bool:
    if session.channel == "voice" and (
        session.role != "owner" or not session.owner_ptt or not session.device_id
    ):
        return False
    return tier in permissions and (tier != "R3" or session.role == "owner")


async def create_gate(
    repo: Repository,
    clock: SimClock,
    command_id: str,
    tier: str,
    scope: dict[str, Any],
    conditions: dict[str, Any],
    hashed: str,
) -> dict[str, Any]:
    scope = {**scope, "decisions": {}}
    gate_id, thread_id = new_id("gate"), new_id("thread")
    await repo.insert(
        approvals,
        {
            "id": gate_id,
            "thread_id": thread_id,
            "command_id": command_id,
            "scope_hash": hashed,
            "tier": tier,
            "status": "pending",
            "conditions": canonical(conditions),
            "scope": canonical(scope),
            "expires_at": iso_utc(clock.now() + timedelta(hours=12)),
        },
    )
    return {
        "command_id": command_id,
        "status": "needs_approval",
        "gate_id": gate_id,
        "thread_id": thread_id,
        "tier": tier,
        "scope": {"type": scope["type"], "payload": scope["payload"], "conditions": conditions},
        "expires_at": iso_utc(clock.now() + timedelta(hours=12)),
        "envelope": envelope(tier, needs_you=True),
    }
```

### backend/arth/governance/events.py

```python
"""Transactional event delivery: consumer effects and offsets share a transaction."""

import asyncio
import json
from collections.abc import Awaitable, Callable
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.db import Database
from arth.core.ids import new_id
from arth.governance.audit import canonical
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import consumer_offsets, outbox

Consumer = Callable[[Repository, dict[str, Any]], Awaitable[None]]


async def emit_event(
    repo: Repository, clock: SimClock, session: Session, topic: str, cause: str, payload: dict[str, Any]
) -> None:
    event = {
        "event_id": new_id("evt"),
        "type": topic,
        "merchant_id": repo.merchant_id,
        "occurred_at": iso_utc(clock.now()),
        "actor": {"kind": "owner" if session.role == "owner" else "staff", "id": session.actor_id},
        "causation_id": cause,
        "payload": payload,
    }
    await repo.insert(
        outbox,
        {
            "event_id": event["event_id"],
            "type": topic,
            "occurred_at": event["occurred_at"],
            "payload": canonical(event),
        },
    )


class Dispatcher:
    def __init__(self, db: Database, clock: SimClock) -> None:
        self.db, self.clock = db, clock
        self.consumers: dict[str, Consumer] = {}
        self.subscribers: dict[asyncio.Queue[dict[str, Any]], str] = {}
        self.views: dict[str, set[str]] = {}

    def on(self, name: str, handler: Consumer) -> None:
        self.consumers[name] = handler

    def subscribe(self, merchant_id: str) -> asyncio.Queue[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=1000)
        self.subscribers[queue] = merchant_id
        return queue

    def unsubscribe(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self.subscribers.pop(queue, None)

    def declare_view(self, name: str, topics: set[str]) -> None:
        self.views[name] = topics

    async def dispatch(self, merchant_id: str) -> None:
        for name, consumer in list(self.consumers.items()) + [("sse", self._broadcast)]:
            async with self.db.write() as conn:
                repo = Repository(conn, merchant_id)
                offsets = await repo.select(consumer_offsets, consumer_offsets.c.consumer == name)
                last = offsets[0]["last_seq"] if offsets else 0
                rows = sorted(await repo.select(outbox, outbox.c.seq > last), key=lambda r: r["seq"])
                for row in rows:
                    await consumer(repo, json.loads(row["payload"]))
                    last = row["seq"]
                if not offsets:
                    await repo.insert(consumer_offsets, {"consumer": name, "last_seq": last})
                elif rows:
                    await repo.update(
                        consumer_offsets, {"last_seq": last}, consumer_offsets.c.consumer == name
                    )

    async def _broadcast(self, repo: Repository, event: dict[str, Any]) -> None:
        views = sorted(name for name, topics in self.views.items() if event["type"] in topics)
        events = [event]
        if views and event["type"] != "view.invalidate":
            events.append(
                {
                    **event,
                    "event_id": new_id("evt"),
                    "type": "view.invalidate",
                    "causation_id": event["event_id"],
                    "payload": {"views": views},
                }
            )
        for queue, merchant_id in list(self.subscribers.items()):
            if merchant_id == repo.merchant_id:
                for item in events:
                    if queue.full():
                        queue.get_nowait()
                    queue.put_nowait(item)
```

### backend/migrations/versions/0002_l1a_foundation.py

```python
"""Frozen L1a foundation schema."""
from alembic import op
from sqlalchemy import CheckConstraint, Column, Integer, String, Table, Text, UniqueConstraint

from sqlalchemy import MetaData
metadata = MetaData(naming_convention={
    'ix': 'ix_%(table_name)s_%(column_0_name)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s',
})


def tenant() -> Column[str]:
    return Column("merchant_id", String, nullable=False, index=True)


merchants = Table(
    "merchants",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("name", String, nullable=False),
    Column("pack", String, nullable=False),
)
merchant_settings = Table(
    "merchant_settings",
    metadata,
    tenant(),
    Column("settings", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id"),
    CheckConstraint("json_valid(settings)"),
)
staff = Table(
    "staff",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("role", String, nullable=False),
    Column("name", String, nullable=False),
)
commands = Table(
    "commands",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("idempotency_key", String, nullable=False),
    Column("type", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("payload", Text, nullable=False),
    Column("result", Text, nullable=False, server_default="{}"),
    UniqueConstraint("merchant_id", "idempotency_key"),
    CheckConstraint("json_valid(payload) AND json_valid(result)"),
)
approvals = Table(
    "approvals",
    metadata,
    Column("id", String, primary_key=True),
    tenant(),
    Column("thread_id", String, nullable=False),
    Column("command_id", String, nullable=False),
    Column("scope_hash", String, nullable=False),
    Column("tier", String, nullable=False),
    Column("status", String, nullable=False),
    Column("conditions", Text, nullable=False),
    Column("scope", Text, nullable=False),
    Column("expires_at", String, nullable=False),
    Column("due_at", String),
    Column("approved_by", String),
    CheckConstraint("json_valid(conditions) AND json_valid(scope)"),
)
audit_log = Table(
    "audit_log",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("command_id", String, nullable=False),
    Column("action", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("data", Text, nullable=False),
    Column("prev_hash", String, nullable=False),
    Column("hash", String, nullable=False),
    CheckConstraint("json_valid(data)"),
)
outbox = Table(
    "outbox",
    metadata,
    Column("seq", Integer, primary_key=True),
    tenant(),
    Column("event_id", String, nullable=False, unique=True),
    Column("type", String, nullable=False),
    Column("occurred_at", String, nullable=False),
    Column("payload", Text, nullable=False),
    CheckConstraint("json_valid(payload)"),
)
consumer_offsets = Table(
    "consumer_offsets",
    metadata,
    tenant(),
    Column("consumer", String, nullable=False),
    Column("last_seq", Integer, nullable=False),
    UniqueConstraint("merchant_id", "consumer"),
)


revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

def upgrade():
    metadata.create_all(op.get_bind())

def downgrade():
    metadata.drop_all(op.get_bind())
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

### backend/arth/api/stream.py

```python
"""GET /v1/stream: server-sent events. L0 streams spans; L1 adds domain events and view invalidations."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from arth.api.governance import require_session
from arth.core.spans import SpanBus, safe_json
from arth.governance.events import Dispatcher
from arth.governance.policy import Session

router = APIRouter()


async def span_events(bus: SpanBus, *, limit: int | None = None) -> AsyncGenerator[dict[str, str]]:
    queue = bus.subscribe()
    sent = 0
    try:
        while limit is None or sent < limit:
            span = await queue.get()
            yield {"event": "span", "data": safe_json(asdict(span))}
            sent += 1
    finally:
        bus.unsubscribe(queue)


@router.get("/v1/stream")
async def get_stream(request: Request) -> EventSourceResponse:
    session = await require_session(request)
    return EventSourceResponse(domain_events(request.app.state.events, request.app.state.spans, session))


async def domain_events(
    dispatcher: Dispatcher, bus: SpanBus, session: Session
) -> AsyncGenerator[dict[str, str]]:
    domain, spans = dispatcher.subscribe(session.merchant_id), bus.subscribe()
    tasks: dict[asyncio.Task[Any], str] = {
        asyncio.create_task(domain.get()): "domain",
        asyncio.create_task(spans.get()): "span",
    }
    try:
        while True:
            done, _ = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                kind = tasks.pop(task)
                item = task.result()
                queue = domain if kind == "domain" else spans
                tasks[asyncio.create_task(queue.get())] = kind
                if kind == "domain":
                    yield {"event": item["type"], "id": item["event_id"], "data": safe_json(item)}
                elif item.attrs.get("merchant_id") == session.merchant_id:
                    yield {"event": "span", "data": safe_json(asdict(item))}
    finally:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        dispatcher.unsubscribe(domain)
        bus.unsubscribe(spans)
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

### backend/tests/test_governance_repository.py

```python
import pytest
from sqlalchemy import Column, String, Table

from arth.core.db import metadata


async def test_repository_isolates_and_rejects_tenant_override(db):
    from arth.governance.repository import Repository
    from arth.governance.tables import merchants

    async with db.write() as conn:
        a = Repository(conn, "shop-a")
        b = Repository(conn, "shop-b")
        await a.insert(merchants, {"id": "shop-a", "name": "A", "pack": "kirana"})
        await b.insert(merchants, {"id": "shop-b", "name": "B", "pack": "kirana"})
        assert [r["name"] for r in await a.select(merchants)] == ["A"]
        assert await a.update(merchants, {"name": "stolen"}, merchants.c.id == "shop-b") == 0
        with pytest.raises(ValueError):
            await a.insert(merchants, {"merchant_id": "shop-b"})
        with pytest.raises(ValueError):
            await a.update(merchants, {"merchant_id": "shop-b"})


async def test_repository_rejects_unscoped_table(db):
    from arth.governance.repository import Repository

    table = Table("unscoped_probe", metadata, Column("id", String), extend_existing=True)
    try:
        async with db.read() as conn:
            with pytest.raises(ValueError):
                await Repository(conn, "a").select(table)
    finally:
        metadata.remove(table)
```

### backend/tests/test_governance_policy.py

```python
from datetime import datetime

from arth.core.clock import IST, SimClock
from arth.core.config import load_policies
from arth.core.paths import CONFIG_DIR


def test_policy_roles_consent_quiet_caps_and_r4():
    from arth.governance.policy import PolicyContext, PolicyEngine, Session

    clock = SimClock(datetime(2026, 10, 30, 10, tzinfo=IST))
    engine = PolicyEngine(load_policies(CONFIG_DIR / "policies.yaml"), clock)
    owner = Session("a", "owner", "owner")
    helper = Session("a", "helper", "helper")
    assert engine.evaluate("ledger.add_entry", "R2", helper).code == "policy.role"
    assert engine.evaluate("capital.apply", "R4", owner).code == "policy.console_required"
    assert engine.evaluate("send", "R3", owner, PolicyContext(purpose="marketing")).code == "policy.consent"
    assert (
        engine.evaluate(
            "send", "R3", owner, PolicyContext(purpose="marketing", consent=True, weekly_contacts=1)
        ).code
        == "policy.contact_cap"
    )
    assert engine.evaluate("read", "R0", owner, PolicyContext(sensitive=True)).discreet
    clock.set(datetime(2026, 10, 30, 22, tzinfo=IST))
    assert (
        engine.evaluate("send", "R3", owner, PolicyContext(purpose="receipts", consent=True)).code
        == "policy.quiet_hours"
    )
```

### backend/tests/test_governance_audit.py

```python
from arth.core.clock import SimClock
from arth.core.config import Settings


async def test_audit_chain_detects_tamper_and_isolates_tenants(db):
    from arth.governance.audit import append_audit, verify_audit
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log

    clock = SimClock(Settings(_env_file=None).clock_start)
    async with db.write() as conn:
        repo = Repository(conn, "a")
        await append_audit(repo, clock, "cmd_a", "executed", {"amount_paise": 45000})
        await append_audit(repo, clock, "cmd_b", "executed", {})
        assert (await verify_audit(repo))["valid"]
        assert (await verify_audit(Repository(conn, "b")))["checked"] == 0
        await repo.update(audit_log, {"data": "{}"}, audit_log.c.seq == 1)
        assert (await verify_audit(repo)) == {"valid": False, "checked": 0, "bad_seq": 1}


async def test_audit_hash_protects_sequence_number(db):
    from arth.governance.audit import append_audit, verify_audit
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log

    clock = SimClock(Settings(_env_file=None).clock_start)
    async with db.write() as conn:
        repo = Repository(conn, "a")
        await append_audit(repo, clock, "cmd_a", "executed", {})
        await repo.update(audit_log, {"seq": 99})
        assert not (await verify_audit(repo))["valid"]
```

### backend/tests/test_governance_commands.py

```python
import asyncio

import pytest

from arth.core.clock import SimClock
from arth.core.config import Settings, load_policies
from arth.core.paths import CONFIG_DIR


async def make_bus(db, tier="R1"):
    from arth.governance.commands import CommandBus
    from arth.governance.policy import PolicyEngine
    from arth.governance.tables import merchant_settings

    clock = SimClock(Settings(_env_file=None).clock_start)
    policies = load_policies(CONFIG_DIR / "policies.yaml").model_copy(deep=True)
    policies.tiers["test.write"] = tier
    bus = CommandBus(db, clock, PolicyEngine(policies, clock))

    async def handler(repo, payload):
        await repo.insert(merchant_settings, {"settings": '{"changed":true}'})
        if payload.get("fail"):
            raise RuntimeError("abort")
        return {"saved": True}

    bus.register(
        "test.write",
        {"type": "object", "properties": {"fail": {"type": "boolean"}}, "additionalProperties": False},
        handler,
    )
    return bus


async def test_command_replay_concurrency_conflict_and_atomic_rollback(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import audit_log, commands, merchant_settings, outbox

    bus = await make_bus(db)
    session = Session("a", "owner-a", "owner")
    a, b = await asyncio.gather(
        bus.submit(session, "test.write", {}, "same"), bus.submit(session, "test.write", {}, "same")
    )
    assert a == b and a["status"] == "executed"
    from arth.core.schemas import validator

    validator("envelope").validate(a["envelope"])
    with pytest.raises(CommandError, match="idempotency"):
        await bus.submit(session, "test.write", {"fail": False}, "same")
    with pytest.raises(RuntimeError, match="abort"):
        await bus.submit(Session("b", "owner-b", "owner"), "test.write", {"fail": True}, "bad")
    async with db.read() as conn:
        repo = Repository(conn, "a")
        assert len(await repo.select(merchant_settings)) == 1
        assert len(await repo.select(commands)) == 1
        assert len(await repo.select(audit_log)) == 1
        assert len(await repo.select(outbox)) == 1
        assert await Repository(conn, "b").select(commands) == []


async def test_unknown_and_invalid_commands_fail_before_writes(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db)
    for kind, payload in [("unknown.command", {}), ("test.write", {"merchant_id": "b"})]:
        with pytest.raises(CommandError):
            await bus.submit(Session("a", "o", "owner"), kind, payload, "key")
```

### backend/tests/test_governance_approvals.py

```python
from datetime import timedelta

import pytest
from test_governance_commands import make_bus


async def test_owner_binding_scope_change_and_send_queue(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "owner", "owner", channel="voice", device_id="device-a", owner_ptt=True)
    gate = await bus.submit(owner, "test.write", {}, "one")
    assert gate["status"] == "needs_approval"
    from arth.core.schemas import validator

    validator("envelope").validate(gate["envelope"])
    assert gate["scope"] == {"type": "test.write", "payload": {}, "conditions": {}}
    with pytest.raises(CommandError, match="approve"):
        await bus.decide(
            Session("a", "helper", "helper", channel="voice", owner_ptt=True),
            gate["thread_id"],
            "approve",
            "decision1",
        )
    with pytest.raises(CommandError, match="approve"):
        await bus.decide(
            Session("a", "owner", "owner", channel="voice"), gate["thread_id"], "approve", "decision2"
        )
    queued = await bus.decide(owner, gate["thread_id"], "approve", "decision3")
    assert queued["status"] == "queued"
    assert await bus.run_due("a") == 0
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 1
    assert (await bus.submit(owner, "test.write", {}, "one"))["status"] == "executed"
    assert (await bus.submit(owner, "test.write", {"fail": False}, "changed"))["status"] == "needs_approval"


async def test_expired_gate_cannot_be_approved(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R2")
    owner = Session("a", "o", "owner", device_id="device-a", owner_ptt=True)
    gate = await bus.submit(owner, "test.write", {}, "one")
    bus.clock.set(bus.clock.now() + timedelta(hours=12))
    with pytest.raises(CommandError, match="expired"):
        await bus.decide(owner, gate["thread_id"], "approve", "decision")
```

### backend/tests/test_governance_scopes.py

```python
import json
from datetime import timedelta

from test_governance_commands import make_bus


async def test_partial_batch_and_plan_scope_are_explicit(db):
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gates = [await bus.submit(owner, "test.write", {}, str(n)) for n in range(3)]
    thread = await bus.batch(owner, [g["gate_id"] for g in gates], mode="plan")
    results = await bus.decide(owner, thread, "approve", "partial", decisions={gates[1]["gate_id"]: "snooze"})
    assert [r["status"] for r in results["items"]] == ["queued", "snoozed", "queued"]
    async with db.read() as conn:
        rows = await Repository(conn, "a").select(approvals)
        assert all(json.loads(r["scope"])["mode"] == "plan" for r in rows)


async def test_conditional_scope_failure_raises_fresh_gate(db):
    from arth.governance.policy import PolicyContext, Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    actual = {"price_paise": 4500}

    async def facts(repo, payload):
        return PolicyContext(facts=actual)

    schema, handler, _ = bus.registry["test.write"]
    bus.register("test.write", schema.schema, handler, facts)
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one", {"price_paise": {"lte": 4500}})
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    actual["price_paise"] = 4550
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0
    async with db.read() as conn:
        rows = await Repository(conn, "a").select(approvals)
        assert [r["status"] for r in rows] == ["superseded", "pending"]
        assert rows[0]["scope_hash"] != rows[1]["scope_hash"]


async def test_series_scope_and_edit_create_new_gate(db):
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    thread = await bus.batch(owner, [gate["gate_id"]], mode="series")
    result = await bus.decide(owner, thread, "edit", "edit", edits={"fail": False})
    assert result["status"] == "needs_approval"
    assert result["gate_id"] != gate["gate_id"]


async def test_queued_scope_mutation_requires_reapproval(db):
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    async with db.write() as conn:
        repo = Repository(conn, "a")
        row = (await repo.select(approvals))[0]
        scope = json.loads(row["scope"])
        scope["payload"] = {"fail": False}
        await repo.update(approvals, {"scope": json.dumps(scope)})
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0
```

### backend/tests/test_governance_events.py

```python
import pytest


async def test_consumer_failure_retries_without_duplicate_effect(db):
    from arth.core.clock import SimClock
    from arth.core.config import Settings
    from arth.governance.events import Dispatcher, emit_event
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import merchant_settings

    clock = SimClock(Settings(_env_file=None).clock_start)
    dispatcher = Dispatcher(db, clock)
    async with db.write() as conn:
        await emit_event(
            Repository(conn, "a"),
            clock,
            Session("a", "o", "owner"),
            "command.executed",
            "cmd_x",
            {"command_id": "cmd_x"},
        )

    async def broken(repo, event):
        await repo.insert(merchant_settings, {"settings": "{}"})
        raise RuntimeError("retry")

    dispatcher.on("consumer", broken)
    with pytest.raises(RuntimeError):
        await dispatcher.dispatch("a")

    async def working(repo, event):
        await repo.insert(merchant_settings, {"settings": "{}"})

    dispatcher.on("consumer", working)
    await dispatcher.dispatch("a")
    await dispatcher.dispatch("a")
    async with db.read() as conn:
        assert len(await Repository(conn, "a").select(merchant_settings)) == 1
    restarted = Dispatcher(db, clock)
    restarted.on("consumer", working)
    await restarted.dispatch("a")
```

### backend/tests/test_governance_api.py

```python
from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.core.schemas import validator
from arth.main import create_app


def test_api_uses_server_session_not_body_or_headers(tmp_path):
    from arth.governance.policy import Session
    from arth.governance.repository import Repository
    from arth.governance.tables import merchant_settings, merchants

    app = create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path))
    with TestClient(app) as client:
        app.state.sessions["test-owner"] = Session("a", "o", "owner", channel="console")
        bus = app.state.commands

        async def seed():
            async with app.state.db.write() as conn:
                await Repository(conn, "a").insert(merchants, {"id": "a", "name": "A", "pack": "kirana"})

        client.portal.call(seed)
        bus.policy.policies.tiers["test.write"] = "R1"

        async def save(repo, payload):
            await repo.insert(merchant_settings, {"settings": "{}"})
            return {"saved": True}

        bus.register("test.write", {"type": "object", "additionalProperties": False}, save)
        body = {"type": "test.write", "payload": {}}
        assert client.post("/v1/commands", json=body).status_code == 401
        headers = {"Authorization": "Bearer test-owner", "Idempotency-Key": "one", "X-Merchant-Id": "b"}
        response = client.post("/v1/commands", json=body, headers=headers)
        assert response.status_code == 200, response.text
        validator("command_result").validate(response.json())
        assert client.post("/v1/commands", json=body, headers=headers).json() == response.json()
        assert (
            client.post("/v1/commands", json={**body, "merchant_id": "b"}, headers=headers).status_code == 422
        )
        audit = client.get("/v1/audit/verify", headers=headers)
        assert audit.json()["valid"] and audit.json()["checked"] == 1
        app.state.sessions["test-other"] = Session("b", "o2", "owner", channel="console")
        assert (
            client.get("/v1/audit/verify", headers={"Authorization": "Bearer test-other"}).json()["checked"]
            == 0
        )


async def test_sse_domain_events_and_view_invalidation_are_tenant_filtered(db):
    import asyncio

    from arth.core.clock import SimClock
    from arth.governance.events import Dispatcher, emit_event
    from arth.governance.policy import Session
    from arth.governance.repository import Repository

    clock = SimClock(Settings(_env_file=None).clock_start)
    dispatcher = Dispatcher(db, clock)
    dispatcher.declare_view("trust", {"command.executed"})
    a, b = dispatcher.subscribe("a"), dispatcher.subscribe("b")
    async with db.write() as conn:
        from arth.core.ids import new_id

        await emit_event(
            Repository(conn, "a"),
            clock,
            Session("a", "o", "owner"),
            "command.executed",
            new_id("cmd"),
            {"command_id": new_id("cmd"), "status": "executed"},
        )
    await asyncio.wait_for(dispatcher.dispatch("a"), 0.2)
    validator("command_executed").validate(a.get_nowait())
    event = a.get_nowait()
    validator("view_invalidate").validate(event)
    assert event["payload"] == {"views": ["trust"]}
    assert b.empty()
```

### backend/tests/test_governance_safety.py

```python
import ast
from datetime import datetime

import pytest

from arth.core.clock import IST, SimClock
from arth.core.config import load_policies
from arth.core.paths import BACKEND_DIR, CONFIG_DIR


def test_domain_sql_execution_is_centralized_in_scoped_repository():
    violations = []
    for path in (BACKEND_DIR / "arth" / "governance").glob("*.py"):
        if path.name == "repository.py":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        violations += [
            f"{path.name}:{n.lineno}"
            for n in ast.walk(tree)
            if isinstance(n, ast.Call)
            and isinstance(n.func, ast.Attribute)
            and n.func.attr in {"execute", "exec_driver_sql"}
        ]
    assert violations == []


@pytest.mark.parametrize(
    "hour,minute,expected",
    [(8, 0, "allow"), (21, 29, "allow"), (21, 30, "policy.quiet_hours"), (7, 59, "policy.quiet_hours")],
)
def test_quiet_hour_boundaries(hour, minute, expected):
    from arth.governance.policy import PolicyContext, PolicyEngine, Session

    clock = SimClock(datetime(2026, 10, 30, hour, minute, tzinfo=IST))
    policy = PolicyEngine(load_policies(CONFIG_DIR / "policies.yaml"), clock)
    assert (
        policy.evaluate(
            "send", "R3", Session("a", "o", "owner"), PolicyContext(purpose="marketing", consent=True)
        ).code
        == expected
    )


@pytest.mark.parametrize(
    "message_class,age,known,template,allowed",
    [
        ("reply", 600, False, False, True),
        ("reply", 601, False, False, False),
        ("rfq", None, True, True, True),
        ("rfq", None, False, True, False),
        ("receipt", None, False, False, True),
        ("campaign", None, False, False, False),
    ],
)
def test_r1_classes_are_bounded(message_class, age, known, template, allowed):
    from arth.governance.policy import PolicyContext, PolicyEngine, Session

    clock = SimClock(datetime(2026, 10, 30, 12, tzinfo=IST))
    policy = PolicyEngine(load_policies(CONFIG_DIR / "policies.yaml"), clock)
    decision = policy.evaluate(
        "send",
        "R1",
        Session("a", "o", "owner"),
        PolicyContext(
            purpose="receipts",
            consent=True,
            message_class=message_class,
            reply_age_seconds=age,
            known_supplier=known,
            approved_template=template,
        ),
    )
    assert (decision.code == "allow") == allowed


async def test_fresh_conditional_gate_cannot_replay_old_approval(db):
    from datetime import timedelta

    from test_governance_commands import make_bus

    from arth.governance.policy import PolicyContext, Session
    from arth.governance.repository import Repository
    from arth.governance.tables import approvals

    bus = await make_bus(db, "R3")
    actual = {"price": 45}

    async def context(repo, payload):
        return PolicyContext(facts=actual)

    schema, handler, _ = bus.registry["test.write"]
    bus.register("test.write", schema.schema, handler, context)
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one", {"price": {"lte": 45}})
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    actual["price"] = 46
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    await bus.run_due("a")
    async with db.read() as conn:
        pending = (await Repository(conn, "a").select(approvals, approvals.c.status == "pending"))[0]
    result = await bus.decide(owner, pending["thread_id"], "approve", "yes")
    assert result["due_at"] == "2026-10-29T02:16:00.000000Z"
```

### backend/tests/test_governance_review.py

```python
from datetime import timedelta

import pytest
from test_governance_commands import make_bus


async def test_discreet_decision_reaches_envelope(db):
    from arth.governance.policy import PolicyContext, Session

    bus = await make_bus(db)
    bus.clock.set(bus.clock.now() + timedelta(hours=2))
    schema, handler, _ = bus.registry["test.write"]

    async def context(repo, payload):
        return PolicyContext(sensitive=True)

    bus.register("test.write", schema.schema, handler, context)
    result = await bus.submit(Session("a", "o", "owner"), "test.write", {}, "one")
    assert result["envelope"]["sensitivity"] == "discreet"


async def test_queue_can_be_cancelled_before_send(db):
    from arth.governance.policy import Session

    bus = await make_bus(db, "R3")
    owner = Session("a", "o", "owner", channel="console")
    gate = await bus.submit(owner, "test.write", {}, "one")
    await bus.decide(owner, gate["thread_id"], "approve", "yes")
    assert (await bus.decide(owner, gate["thread_id"], "snooze", "cancel"))["status"] == "snoozed"
    bus.clock.set(bus.clock.now() + timedelta(seconds=30))
    assert await bus.run_due("a") == 0


async def test_manager_can_tap_r2_but_cannot_voice_approve(db):
    from arth.governance.commands import CommandError
    from arth.governance.policy import Session

    bus = await make_bus(db, "R2")
    manager = Session("a", "m", "manager", device_id="manager-device")
    gate = await bus.submit(manager, "test.write", {}, "one")
    with pytest.raises(CommandError):
        await bus.decide(
            Session("a", "m", "manager", channel="voice", device_id="manager-device", owner_ptt=True),
            gate["thread_id"],
            "approve",
            "voice",
        )
    assert (await bus.decide(manager, gate["thread_id"], "approve", "tap"))["status"] == "executed"


async def test_pack_policy_is_used_by_bus(db):
    from arth.core.packs import PackRegistry
    from arth.governance.commands import CommandError
    from arth.governance.policy import PolicyContext, Session
    from arth.governance.repository import Repository
    from arth.governance.tables import merchants

    bus = await make_bus(db)
    policies = bus.policy.policies.model_copy(deep=True)
    policies.growth.margin_floor = 0.25
    bus.packs = PackRegistry({}, {"cafe": policies})
    # Registry resolves a real manifest as well as merged policies.
    from arth.core.paths import PACKS_DIR

    base = PackRegistry.load(PACKS_DIR, bus.policy.policies).get("kirana")
    bus.packs = PackRegistry({"cafe": base.model_copy(update={"pack": "cafe"})}, {"cafe": policies})
    async with db.write() as conn:
        await Repository(conn, "a").insert(merchants, {"id": "a", "name": "Cafe", "pack": "cafe"})
    schema, handler, _ = bus.registry["test.write"]

    async def context(repo, payload):
        return PolicyContext(margin=0.2)

    bus.register("test.write", schema.schema, handler, context)
    with pytest.raises(CommandError, match="margin_floor"):
        await bus.submit(Session("a", "o", "owner"), "test.write", {}, "one")
```

