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
from arth.core.spans import SpanBus
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
        self.spans: SpanBus | None = None

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
        if self.spans is None:
            return await self._evaluate(repo, session, kind, tier, payload)
        async with self.spans.span("policy", kind) as trace:
            trace["merchant_id"], trace["tier"] = repo.merchant_id, tier
            try:
                decision = await self._evaluate(repo, session, kind, tier, payload)
            except CommandError as exc:
                trace["code"] = str(exc)
                raise
            trace["code"] = decision.code
            return decision

    async def _evaluate(
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
            decision = await self._check(repo, session, kind, tier, payload)
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
                # Trusted domain bounds cannot be weakened by request-supplied conditions.
                effective_conditions = {**conditions, **repo.approval_conditions}
                result = await create_gate(
                    repo,
                    self.clock,
                    command_id,
                    tier,
                    {"session": asdict(session), "type": kind, "payload": payload},
                    effective_conditions,
                    scope_hash(kind, payload, effective_conditions),
                )
                result["envelope"]["sensitivity"] = "discreet" if decision.discreet else "normal"
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
        if decision not in {"approve", "snooze", "edit", "decline"} or not key:
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
        if session.actor_kind == "agent" or session.channel == "agent":
            raise CommandError("approval.cannot_approve")  # agents propose; only people approve (AIQ-1)
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
            gate["status"] == "queued" and decision in {"snooze", "decline"}
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
        elif decision == "decline":
            result = {"command_id": gate["command_id"], "status": "declined"}  # the gated command never runs
            status = "declined"
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
                if gate["expires_at"] <= iso_utc(self.clock.now()):
                    result = {"command_id": gate["command_id"], "status": "expired"}
                    await repo.update(approvals, {"status": "expired"}, approvals.c.id == gate["id"])
                    await self._store(repo, gate["command_id"], result)
                    await append_audit(repo, self.clock, gate["command_id"], "approval.expired", result)
                    continue
                scope = json.loads(gate["scope"])
                conditions = json.loads(gate["conditions"])
                session = Session(**scope["session"])
                repo.session = session  # condition providers check who asked (e.g. owner-only manual reminders)
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
