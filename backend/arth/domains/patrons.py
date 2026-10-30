"""PII-safe patron requests, verified customer instructions and reward callbacks."""

import hashlib
import hmac
from datetime import timedelta
from difflib import SequenceMatcher
from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.core.schemas import schema, validator
from arth.domains.merchants import domain_event, owner_only, stable_id
from arth.domains.patron_identity import (
    PURPOSES,
    canonical_patron,
    has_consent,
    identity_value,
    patron_row,
    related_ids,
    resolve_identity,
)
from arth.domains.patron_rewards import earn_visit, redeem_reward, reward_view
from arth.domains.patron_tables import (
    consents,
    household_members,
    households,
    merge_proposals,
    patron_contacts,
    patron_identities,
    patron_links,
    patrons,
    reward_programs,
)
from arth.governance.audit import canonical
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import PolicyContext, Session
from arth.governance.repository import Repository

__all__ = [
    "PatronService",
    "resolve_identity",
    "has_consent",
    "outbound_context",
    "patron_view",
    "reward_view",
]


async def outbound_context(
    repo: Repository, clock: SimClock, patron_id: str, purpose: str, *, message_class: str | None = None
) -> PolicyContext:
    ids = await related_ids(repo, patron_id)
    rows = await repo.select(
        patron_contacts,
        patron_contacts.c.patron_id.in_(ids),
        patron_contacts.c.purpose == purpose,
        patron_contacts.c.occurred_at > iso_utc(clock.now() - timedelta(days=7)),
        patron_contacts.c.status != "cancelled",
    )
    return PolicyContext(
        purpose=purpose,
        consent=await has_consent(repo, patron_id, purpose),
        weekly_contacts=len(rows),
        message_class=message_class,
    )


async def patron_view(repo: Repository, patron_id: str) -> dict[str, Any]:
    root = await canonical_patron(repo, patron_id)
    row = await patron_row(repo, root)
    members = await repo.select(
        household_members,
        household_members.c.patron_id.in_(await related_ids(repo, root)),
        household_members.c.active == 1,
    )
    return {
        "patron_id": root,
        "display_name": row["display_name"],
        "lang": row["lang"],
        "consent": {purpose: await has_consent(repo, root, purpose) for purpose in PURPOSES},
        "household_members": [{"id": r["id"], "display_name": r["display_name"]} for r in members],
        "rewards": await reward_view(repo, root),
        "invalidate_on": [
            "patron.changed",
            "patron.consent_changed",
            "patron.merged",
            "patron.reward_changed",
        ],
    }


class PatronService:
    def __init__(self, bus: CommandBus, proof_key: str) -> None:
        self.bus, self._key = bus, proof_key.encode()
        self._register()

    def _proof(self, data: dict[str, Any]) -> str:
        return hmac.new(self._key, ("patron-proof:" + canonical(data)).encode(), hashlib.sha256).hexdigest()

    async def submit(self, actor: Session, kind: str, payload: dict[str, Any], key: str) -> dict[str, Any]:
        if kind not in {"patrons.add", "patrons.update_profile"} or not validator(
            kind.replace(".", "_")
        ).is_valid(payload):
            raise CommandError("patron.invalid_payload")
        if kind == "patrons.add":
            public = {
                "patron_id": stable_id("pat", actor.merchant_id + ":" + key),
                "lang": payload["lang"],
                "proof_hash": self._proof(payload),
            }
        else:
            async with self.bus.db.read() as conn:
                row = await patron_row(Repository(conn, actor.merchant_id), payload["patron_id"])
            public = {
                "patron_id": payload["patron_id"],
                "lang": payload.get("lang", row["lang"]),
                "proof_hash": self._proof(payload),
            }
        return await self.bus.submit(actor, kind, public, key, private={"profile": payload})

    def _system(self, merchant_id: str) -> Session:
        return Session(merchant_id, new_id("system"), "system", actor_kind="system")

    async def record_customer_instruction(
        self, merchant_id: str, patron_id: str, purpose: str, granted: bool, source_ref: str
    ) -> dict[str, Any]:
        return await self.bus.submit(
            self._system(merchant_id),
            "consent.grant" if granted else "consent.withdraw",
            {"patron_id": patron_id, "purpose": purpose, "source_ref": source_ref},
            "instruction:" + source_ref + ":" + purpose,
            private={"customer_verified": True},
        )

    async def stop(self, merchant_id: str, patron_id: str, source_ref: str) -> dict[str, Any]:
        return await self.bus.submit(
            self._system(merchant_id),
            "consent.stop",
            {"patron_id": patron_id, "source_ref": source_ref},
            "stop:" + source_ref,
            private={"customer_verified": True},
        )

    async def add_member(self, actor: Session, patron_id: str, display_name: str, key: str) -> dict[str, Any]:
        public = {
            "patron_id": patron_id,
            "member_id": stable_id("member", actor.merchant_id + ":" + key),
            "proof_hash": self._proof({"name": display_name}),
        }
        return await self.bus.submit(
            actor, "patrons.add_household_member", public, key, private={"display_name": display_name}
        )

    async def record_visit(self, merchant_id: str, patron_id: str, payment_ref: str) -> dict[str, Any]:
        return await self.bus.submit(
            self._system(merchant_id),
            "rewards.record_visit",
            {"patron_id": patron_id, "payment_ref": payment_ref},
            "visit:" + payment_ref,
            private={"payment_verified": True},
        )

    def _register(self) -> None:
        bus = self.bus

        async def add(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            profile = repo.private.get("profile")
            if not profile:
                raise CommandError("patron.private_profile_required")
            await repo.insert(
                patrons,
                {
                    "id": payload["patron_id"],
                    "display_name": profile["display_name"],
                    "lang": payload["lang"],
                    "created_at": iso_utc(bus.clock.now()),
                },
            )
            for identity in profile.get("identities", []):
                kind, value = identity_value(repo.merchant_id, identity["kind"], identity["value"])
                if not await repo.select(
                    patron_identities,
                    patron_identities.c.patron_id == payload["patron_id"],
                    patron_identities.c.kind == kind,
                    patron_identities.c.value == value,
                ):
                    await repo.insert(
                        patron_identities,
                        {
                            "id": new_id("identity"),
                            "patron_id": payload["patron_id"],
                            "kind": kind,
                            "value": value,
                        },
                    )
            await domain_event(bus, repo, "patron.changed", {"patron_id": payload["patron_id"]})
            return {"patron_id": payload["patron_id"]}

        async def update(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            profile = repo.private.get("profile")
            if not profile:
                raise CommandError("patron.private_profile_required")
            await patron_row(repo, payload["patron_id"])
            values = {"lang": payload["lang"]}
            if "display_name" in profile:
                values["display_name"] = profile["display_name"]
            await repo.update(patrons, values, patrons.c.id == payload["patron_id"])
            await domain_event(bus, repo, "patron.changed", {"patron_id": payload["patron_id"]})
            return {"patron_id": payload["patron_id"]}

        async def consent_change(repo: Repository, payload: dict[str, Any], granted: bool) -> dict[str, Any]:
            if granted and not repo.private.get("customer_verified"):
                raise CommandError("consent.customer_instruction_required")
            if not granted and not repo.private.get("customer_verified"):
                owner_only(repo)
            await patron_row(repo, payload["patron_id"])
            await repo.insert(
                consents,
                {
                    "id": new_id("consent"),
                    "patron_id": payload["patron_id"],
                    "purpose": payload["purpose"],
                    "granted": int(granted),
                    "source_ref": payload["source_ref"],
                    "occurred_at": iso_utc(bus.clock.now()),
                },
            )
            if not granted:
                await repo.update(
                    patron_contacts,
                    {"status": "cancelled"},
                    patron_contacts.c.patron_id == payload["patron_id"],
                    patron_contacts.c.purpose == payload["purpose"],
                    patron_contacts.c.status == "reserved",
                )
            await domain_event(bus, repo, "patron.consent_changed", {"patron_id": payload["patron_id"]})
            return {"patron_id": payload["patron_id"], "purpose": payload["purpose"], "granted": granted}

        async def grant(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            return await consent_change(repo, payload, True)

        async def withdraw(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            return await consent_change(repo, payload, False)

        async def stop(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if not repo.private.get("customer_verified"):
                raise CommandError("consent.customer_instruction_required")
            for purpose in PURPOSES:
                await consent_change(repo, {**payload, "purpose": purpose}, False)
            return {"patron_id": payload["patron_id"], "stopped": True}

        async def merge(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            source = await canonical_patron(repo, payload["source_id"])
            target = await canonical_patron(repo, payload["target_id"])
            if source != target:
                await repo.insert(
                    patron_links,
                    {
                        "id": new_id("merge"),
                        "source_id": source,
                        "target_id": target,
                        "occurred_at": iso_utc(bus.clock.now()),
                    },
                )
                await domain_event(bus, repo, "patron.merged", {"patron_id": target})
            return {"patron_id": target, "source_id": source}

        async def propose(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            source = await patron_row(repo, payload["source_id"])
            target = await patron_row(repo, payload["target_id"])
            left = await repo.select(patron_identities, patron_identities.c.patron_id == source["id"])
            right = await repo.select(patron_identities, patron_identities.c.patron_id == target["id"])
            strong = any(
                a["kind"] == "vpa_hash" and a["kind"] == b["kind"] and a["value"] == b["value"]
                for a in left
                for b in right
            )
            confidence = (
                9500
                if strong
                else min(
                    8900,
                    int(
                        SequenceMatcher(
                            None, source["display_name"].casefold(), target["display_name"].casefold()
                        ).ratio()
                        * 10000
                    ),
                )
            )
            identity = new_id("proposal")
            status = "merged" if confidence > 9000 else "needs_review" if confidence >= 6000 else "rejected"
            await repo.insert(
                merge_proposals, {"id": identity, **payload, "confidence_bp": confidence, "status": status}
            )
            if status == "merged":
                await merge(repo, payload)
            return {"proposal_id": identity, "confidence_bp": confidence, "status": status}

        async def member(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            await patron_row(repo, payload["patron_id"])
            if not repo.private.get("display_name"):
                raise CommandError("patron.private_profile_required")
            if not await repo.select(households, households.c.patron_id == payload["patron_id"]):
                await repo.insert(households, {"id": new_id("household"), "patron_id": payload["patron_id"]})
            await repo.insert(
                household_members,
                {
                    "id": payload["member_id"],
                    "patron_id": payload["patron_id"],
                    "display_name": repo.private["display_name"],
                },
            )
            await domain_event(bus, repo, "patron.changed", {"patron_id": payload["patron_id"]})
            return {"member_id": payload["member_id"]}

        async def configure(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            await repo.update(reward_programs, {"status": "inactive"}, reward_programs.c.status == "active")
            identity = new_id("rewardprog")
            await repo.insert(
                reward_programs,
                {"id": identity, **payload, "status": "active", "occurred_at": iso_utc(bus.clock.now())},
            )
            return {"program_id": identity}

        async def budget(repo: Repository, payload: dict[str, Any]) -> PolicyContext:
            return PolicyContext(spend_paise=payload["budget_paise"])

        async def visit(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if not repo.private.get("payment_verified"):
                raise CommandError("reward.verified_payment_required")
            result = await earn_visit(repo, bus.clock, payload["patron_id"], payload["payment_ref"])
            await domain_event(bus, repo, "patron.reward_changed", {"patron_id": payload["patron_id"]})
            return result

        async def redeem(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if not repo.private.get("counter_verified"):
                raise CommandError("reward.verified_counter_required")
            result = await redeem_reward(
                repo, bus.clock, payload["patron_id"], payload["bill_id"], repo.private["bill_total_paise"]
            )
            await domain_event(bus, repo, "patron.reward_changed", {"patron_id": payload["patron_id"]})
            return result

        for kind, contract, handler in [
            ("patrons.add", "patrons_add_command", add),
            ("patrons.update_profile", "patrons_update_command", update),
            ("consent.grant", "consent_grant", grant),
            ("consent.withdraw", "consent_withdraw", withdraw),
            ("consent.stop", "consent_stop", stop),
            ("patrons.merge", "patrons_merge", merge),
            ("patrons.propose_merge", "patrons_propose_merge", propose),
            ("patrons.add_household_member", "patrons_add_household_member", member),
            ("rewards.record_visit", "rewards_record_visit", visit),
            ("rewards.redeem", "rewards_redeem", redeem),
        ]:
            bus.register(kind, schema(contract), handler)
        bus.register("rewards.configure", schema("rewards_configure"), configure, budget)
