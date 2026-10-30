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
