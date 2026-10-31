"""Visit stamp issuance and redemption share the monetary liability transaction."""

from typing import Any

from arth.core.clock import SimClock, iso_utc
from arth.core.ids import new_id
from arth.domains.patron_identity import patron_row, related_ids
from arth.domains.patron_tables import offer_liability, reward_ledger, reward_programs
from arth.governance.commands import CommandError
from arth.governance.repository import Repository


async def reward_view(repo: Repository, identity: str) -> dict[str, Any]:
    rows = await repo.select(reward_ledger, reward_ledger.c.patron_id.in_(await related_ids(repo, identity)))
    redeemed = {row["issued_ref"] for row in rows if row["kind"] == "redeem"}
    available = [row for row in rows if row["kind"] == "issue" and row["id"] not in redeemed]
    return {
        "stamps": sum(row["delta_stamps"] for row in rows),
        "available_rewards": len(available),
        "available_value_paise": sum(row["value_paise"] for row in available),
    }


async def earn_visit(repo: Repository, clock: SimClock, identity: str, payment_ref: str) -> dict[str, Any]:
    await patron_row(repo, identity)
    old = await repo.select(
        reward_ledger, reward_ledger.c.kind == "visit", reward_ledger.c.source_ref == payment_ref
    )
    if old:
        if old[0]["patron_id"] != identity:
            raise CommandError("reward.payment_conflict")
        return await reward_view(repo, identity)
    programs = await repo.select(reward_programs, reward_programs.c.status == "active")
    program = max(programs, key=lambda row: (row["occurred_at"], row["id"])) if programs else None
    common = {
        "patron_id": identity,
        "program_id": program["id"] if program else None,
        "source_ref": payment_ref,
        "occurred_at": iso_utc(clock.now()),
    }
    await repo.insert(reward_ledger, {"id": new_id("reward"), "kind": "visit", "delta_stamps": 1, **common})
    if program:
        balance = await reward_view(repo, identity)
        spent = sum(
            row["issued_paise"]
            for row in await repo.select(offer_liability, offer_liability.c.program_id == program["id"])
        )
        if (
            balance["stamps"] // program["threshold"] > balance["available_rewards"]
            and spent + program["value_paise"] <= program["budget_paise"]
        ):
            issued = new_id("reward")
            await repo.insert(
                reward_ledger,
                {
                    "id": issued,
                    "kind": "issue",
                    "delta_stamps": 0,
                    "stamps_required": program["threshold"],
                    "value_paise": program["value_paise"],
                    **common,
                },
            )
            await repo.insert(
                offer_liability,
                {
                    "id": new_id("liability"),
                    "program_id": program["id"],
                    "patron_id": identity,
                    "source_ref": issued,
                    "date": clock.now_ist().date().isoformat(),
                    "issued_paise": program["value_paise"],
                },
            )
    return await reward_view(repo, identity)


async def redeem_reward(
    repo: Repository, clock: SimClock, identity: str, bill_id: str, maximum_paise: int
) -> dict[str, Any]:
    rows = await repo.select(reward_ledger, reward_ledger.c.patron_id.in_(await related_ids(repo, identity)))
    previous = [row for row in rows if row["kind"] == "redeem" and row["source_ref"] == bill_id]
    if previous:
        return {"discount_paise": previous[0]["value_paise"]}
    redeemed = {row["issued_ref"] for row in rows if row["kind"] == "redeem"}
    available = sorted(
        (row for row in rows if row["kind"] == "issue" and row["id"] not in redeemed),
        key=lambda row: row["seq"],
    )
    if not available:
        raise CommandError("reward.not_available")
    reward = available[0]
    if reward["value_paise"] > maximum_paise:
        raise CommandError("reward.exceeds_bill")
    await repo.insert(
        reward_ledger,
        {
            "id": new_id("reward"),
            "patron_id": identity,
            "program_id": reward["program_id"],
            "kind": "redeem",
            "source_ref": bill_id,
            "issued_ref": reward["id"],
            "delta_stamps": -reward["stamps_required"],
            "value_paise": reward["value_paise"],
            "occurred_at": iso_utc(clock.now()),
        },
    )
    await repo.insert(
        offer_liability,
        {
            "id": new_id("liability"),
            "program_id": reward["program_id"],
            "patron_id": identity,
            "source_ref": bill_id,
            "date": clock.now_ist().date().isoformat(),
            "redeemed_paise": reward["value_paise"],
        },
    )
    return {"discount_paise": reward["value_paise"]}
