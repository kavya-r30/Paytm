"""Simulator, webhook and director endpoints (spec C2: Webhooks, Director, Simulators /sim/*)."""

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Header, Request
from pydantic import BaseModel, Field

from arth.api.auth import require_token
from arth.api.commerce import Actor
from arth.api.problems import ProblemError
from arth.core.clock import iso_utc, parse_iso
from arth.governance.commands import CommandError
from arth.governance.repository import Repository
from arth.sim.forge import screenshot
from arth.sim.hub import SignatureError
from arth.sim.peers import peers_view
from arth.sim.tables import local_events

router = APIRouter()
director = [Depends(require_token("director"))]


def refused(exc: Exception, status: int = 409) -> ProblemError:
    return ProblemError(status, str(exc), "error." + str(exc), title="Simulator refused")


@router.post("/webhooks/rails")
async def rails_webhook(request: Request, x_sim_signature: Annotated[str, Header()]) -> dict[str, Any]:
    try:
        return await request.app.state.sim.ingest_rails(await request.body(), x_sim_signature)
    except SignatureError as exc:
        raise refused(exc, 401) from exc
    except CommandError as exc:
        raise refused(exc) from exc


@router.post("/webhooks/messages")
async def messages_webhook(request: Request, x_sim_signature: Annotated[str, Header()]) -> dict[str, Any]:
    try:
        return await request.app.state.sim.ingest_message(await request.body(), x_sim_signature)
    except SignatureError as exc:
        raise refused(exc, 401) from exc
    except CommandError as exc:
        raise refused(exc) from exc


class QrBody(BaseModel):
    merchant_id: str
    order_ref: str
    amount_paise: int = Field(gt=0)


class PayBody(BaseModel):
    payer_vpa: str = "customer@okbank"
    payer_name: str = ""
    outcome: str = Field("success", pattern="^(success|pending|failed)$")


class StaticPayBody(PayBody):
    merchant_id: str
    amount_paise: int = Field(gt=0)
    link_id: str | None = None


class CompleteBody(BaseModel):
    merchant_id: str
    utr: str
    outcome: str = Field(pattern="^(success|failed)$")


class FaultBody(BaseModel):
    merchant_id: str
    kind: str = Field(pattern="^(duplicate|drop|delay|wrong_amount)$")
    times: int = Field(1, ge=1, le=10)
    arg: int = 0


class SettleBody(BaseModel):
    merchant_id: str
    date: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")


class InboundBody(BaseModel):
    merchant_id: str
    persona_id: str
    text: str = Field(min_length=1, max_length=2000)
    kind: str = "text"


class LenderBody(BaseModel):
    merchant_id: str
    need_paise: int = Field(gt=0)
    purpose_ref: str | None = None


class ScreenshotBody(BaseModel):
    amount_paise: int = Field(gt=0)
    utr: str
    payee: str
    paid_at: str
    edited: bool = False
    edit: str = Field("amount", pattern="^(amount|utr)$")


class ClockBody(BaseModel):
    advance_minutes: int | None = Field(None, ge=0, le=60 * 24 * 120)
    to: str | None = None


class WorldBody(BaseModel):
    pack: str = "kirana"
    days: int = Field(30, ge=1, le=120)
    seed: int = 1
    size: str = Field("small", pattern="^(micro|small|medium)$")
    patrons: int = Field(30, ge=4, le=200)
    name: str | None = None
    key: str | None = None


@router.post("/sim/rails/qr", dependencies=director)
async def qr(request: Request, body: QrBody) -> dict[str, Any]:
    return await request.app.state.sim.create_qr(body.merchant_id, body.order_ref, body.amount_paise)


@router.get("/sim/pay/{token}")
async def pay_page(request: Request, token: str) -> dict[str, Any]:
    """Backs the simulated UPI app page `/pay/:token` (T2.2): payee and amount only, nothing personal."""
    try:
        merchant_id, order = await request.app.state.sim.order_for_token(token)
    except CommandError as exc:
        raise refused(exc, 404) from exc
    async with request.app.state.db.read() as conn:
        from arth.domains.merchants import settings_view

        settings = await settings_view(Repository(conn, merchant_id))
    return {
        "token": token,
        "payee_name": settings["name"],
        "payee_vpa": settings.get("vpa"),
        "amount_paise": order["amount_paise"],
        "status": order["status"],
        "expires_at": order["expires_at"],
    }


@router.post("/sim/pay/{token}")
async def pay(request: Request, token: str, body: PayBody) -> dict[str, Any]:
    try:
        merchant_id, _ = await request.app.state.sim.order_for_token(token)
        return await request.app.state.sim.pay(
            merchant_id,
            token=token,
            payer_vpa=body.payer_vpa,
            payer_name=body.payer_name,
            outcome=body.outcome,
        )
    except CommandError as exc:
        raise refused(exc) from exc


@router.post("/sim/rails/static-pay", dependencies=director)
async def static_pay(request: Request, body: StaticPayBody) -> dict[str, Any]:
    try:
        return await request.app.state.sim.pay(
            body.merchant_id,
            payer_vpa=body.payer_vpa,
            payer_name=body.payer_name,
            amount_paise=body.amount_paise,
            outcome=body.outcome,
            link_id=body.link_id,
        )
    except CommandError as exc:
        raise refused(exc) from exc


@router.post("/sim/rails/complete", dependencies=director)
async def complete(request: Request, body: CompleteBody) -> dict[str, Any]:
    try:
        return await request.app.state.sim.complete(body.merchant_id, body.utr, body.outcome)
    except CommandError as exc:
        raise refused(exc) from exc


@router.post("/sim/rails/faults", dependencies=director)
async def faults(request: Request, body: FaultBody) -> dict[str, Any]:
    await request.app.state.sim.add_fault(body.merchant_id, body.kind, body.times, body.arg)
    return {"ok": True}


@router.post("/sim/rails/settle", dependencies=director)
async def settle(request: Request, body: SettleBody) -> dict[str, Any]:
    try:
        return await request.app.state.sim.settle(body.merchant_id, body.date)
    except CommandError as exc:
        raise refused(exc) from exc


@router.get("/sim/messages/threads", dependencies=director)
async def threads(request: Request, merchant_id: str) -> dict[str, Any]:
    return {"threads": await request.app.state.sim.threads(merchant_id)}


@router.post("/sim/messages/inbound", dependencies=director)
async def inbound(request: Request, body: InboundBody) -> dict[str, Any]:
    try:
        return await request.app.state.sim.inbound(body.merchant_id, body.persona_id, body.text, body.kind)
    except (CommandError, IndexError) as exc:
        raise refused(CommandError("sim.unknown_persona") if isinstance(exc, IndexError) else exc) from exc


@router.post("/sim/lender/offers", dependencies=director)
async def lender(request: Request, body: LenderBody) -> dict[str, Any]:
    return {
        "offer_ids": await request.app.state.sim.lender_offers(
            body.merchant_id, body.need_paise, body.purpose_ref
        )
    }


@router.post("/sim/tools/screenshot", dependencies=director)
async def forge(body: ScreenshotBody) -> dict[str, Any]:
    return screenshot(
        body.amount_paise, body.utr, body.payee, body.paid_at, edited=body.edited, edit=body.edit
    )


@router.get("/sim/personas", dependencies=director)
async def personas(request: Request) -> dict[str, Any]:
    return {"personas": list(request.app.state.personas.cards.values())}


@router.post("/v1/director/clock", dependencies=director)
async def clock(request: Request, body: ClockBody) -> dict[str, Any]:
    sim_clock = request.app.state.clock
    try:
        if body.to:
            sim_clock.set(parse_iso(body.to))
        elif body.advance_minutes is not None:
            await request.app.state.scheduler.advance_to(
                sim_clock.now() + timedelta(minutes=body.advance_minutes)
            )
    except ValueError as exc:
        raise refused(exc, 422) from exc
    return {"clock": iso_utc(sim_clock.now())}


@router.post("/v1/director/world", dependencies=director)
async def world(request: Request, body: WorldBody) -> dict[str, Any]:
    from arth.sim.world import WorldBuilder, WorldSpec

    state = request.app.state
    spec = WorldSpec(
        pack=body.pack,
        days=body.days,
        seed=body.seed,
        size=body.size,
        patrons=body.patrons,
        name=body.name,
        key=body.key,
    )
    try:
        manifest = await WorldBuilder(state.sim, state.patrons, spec).build()
    except CommandError as exc:
        raise refused(exc) from exc
    state.commands.merchant_ids.add(manifest["merchant_id"])
    manifest["device_credential"] = state.staff.device_credential(
        manifest["merchant_id"], manifest["device_id"]
    )
    return manifest


class SessionBody(BaseModel):
    merchant_id: str | None = None
    surface: str = Field("device", pattern="^(device|console)$")
    role: str = Field("owner", pattern="^(owner|manager|cashier|helper)$")


@router.post("/v1/director/session", dependencies=director)
async def presenter_session(request: Request, body: SessionBody) -> dict[str, Any]:
    """A real staff session for a seeded shop, so the stage can pass `?session=` to each surface."""
    from arth.domains.tables import devices
    from arth.governance.tables import staff

    state = request.app.state
    merchants = sorted(state.commands.merchant_ids)
    merchant_id = body.merchant_id or (merchants[-1] if len(merchants) == 1 else None)
    if merchant_id is None or merchant_id not in state.commands.merchant_ids:
        raise refused(CommandError("director.merchant_required"), 422)
    async with state.db.read() as conn:
        repo = Repository(conn, merchant_id)
        people = await repo.select(staff, staff.c.role == body.role)
        device = await repo.select(devices)
    if not people or not device:
        raise refused(CommandError("director.no_such_staff"), 404)
    try:
        return await state.staff.issue(
            merchant_id,
            people[0]["id"],
            device[0]["id"],
            body.surface,
            f"presenter-{merchant_id}-{body.surface}-{body.role}-{iso_utc(state.clock.now())}",
        )
    except CommandError as exc:
        raise refused(exc) from exc


class SnapshotBody(BaseModel):
    name: str = Field(pattern=r"^[a-z0-9_.-]{1,80}$")


def _snapshot_path(request: Request, name: str) -> Any:
    from pathlib import Path

    return Path(request.app.state.settings.data_dir) / "snapshots" / f"{name}.db"


@router.post("/v1/director/snapshot", dependencies=director)
async def snapshot(request: Request, body: SnapshotBody) -> dict[str, Any]:
    """T8.2: save the whole world (DB + sim clock) under a name, e.g. one per scene."""
    import json

    path = _snapshot_path(request, body.name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    await request.app.state.db.snapshot(path)
    path.with_suffix(".json").write_text(json.dumps({"clock": iso_utc(request.app.state.clock.now())}))
    return {"name": body.name, "clock": iso_utc(request.app.state.clock.now())}


@router.post("/v1/director/restore", dependencies=director)
async def restore(request: Request, body: SnapshotBody) -> dict[str, Any]:
    """T8.2 recovery button: restore a named snapshot and its clock (< 3 s)."""
    import json
    import time

    from arth.governance.repository import Repository as Repo

    state = request.app.state
    path = _snapshot_path(request, body.name)
    if not path.exists():
        raise refused(CommandError("director.snapshot_not_found"), 404)
    started = time.monotonic()
    await state.db.restore(path)
    clock_file = path.with_suffix(".json")
    if clock_file.exists():
        state.clock.reset(parse_iso(json.loads(clock_file.read_text())["clock"]))
    async with state.db.read() as conn:
        state.commands.merchant_ids = await Repo.merchant_directory(conn)
    return {
        "name": body.name,
        "clock": iso_utc(state.clock.now()),
        "ms": int((time.monotonic() - started) * 1000),
    }


@router.get("/v1/director/scenarios", dependencies=director)
async def scenarios() -> dict[str, Any]:
    """The scenario library (validated YAML) for the Director and the stage's auto-focus."""
    from arth.sim.scenario import SCENARIOS_DIR, load

    return {"scenarios": [load(path) for path in sorted(SCENARIOS_DIR.glob("*/scenario.yaml"))]}


class PlayBody(BaseModel):
    scenario: str = Field(pattern=r"^[a-z0-9_]{1,60}$")


class BeatBody(BaseModel):
    beat_id: str = Field(min_length=1, max_length=20)


@router.post("/v1/director/play", dependencies=director)
async def play(request: Request, body: PlayBody) -> dict[str, Any]:
    """T8.7 live play: build the scenario's world here; the Director then runs it one beat at a time."""
    import anyio.to_thread

    from arth.sim.scenario import SCENARIOS_DIR, LiveClient, ScenarioRunner, load

    path = SCENARIOS_DIR / body.scenario / "scenario.yaml"
    if not path.exists():
        raise refused(CommandError("director.scenario_not_found"), 404)
    scenario = load(path)
    runner = ScenarioRunner(LiveClient(request.app))
    import secrets

    await anyio.to_thread.run_sync(runner.setup, scenario, "-play-" + secrets.token_hex(4))
    request.app.state.director_play = {"scenario": scenario, "runner": runner}
    return {
        "scenario": body.scenario,
        "merchant_id": runner.saved["merchant_id"],
        "beats": [b["id"] for scene in scenario["scenes"] for b in scene["beats"]],
    }


@router.post("/v1/director/play/beat", dependencies=director)
async def play_beat(request: Request, body: BeatBody) -> dict[str, Any]:
    """Run one beat of the playing scenario: snapshot at a scene's first beat (the recovery point), then its
    inputs and expectations. A failed expectation is reported, not raised, so the presenter can recover."""
    import anyio.to_thread

    from arth.sim.scenario import BeatFailed

    playing = getattr(request.app.state, "director_play", None)
    if playing is None:
        raise refused(CommandError("director.not_playing"), 409)
    scenario, runner = playing["scenario"], playing["runner"]
    found = next(
        (
            (scene, i)
            for scene in scenario["scenes"]
            for i, b in enumerate(scene["beats"])
            if b["id"] == body.beat_id
        ),
        None,
    )
    if found is None:
        raise refused(CommandError("director.beat_not_found"), 404)
    scene, index = found
    snapshot = f"{scenario['scenario']}-scene-{scene['id']}"
    if index == 0:
        await anyio.to_thread.run_sync(runner.snapshot, snapshot)
    try:
        ms = await anyio.to_thread.run_sync(runner.play_beat, scene["beats"][index])
    except (BeatFailed, AssertionError, KeyError, TypeError, ValueError) as exc:
        # e.g. a beat replayed out of order (its bill is already closed): report it so the presenter restores
        error = str(exc) if isinstance(exc, AssertionError) else f"{type(exc).__name__}: {exc}"
        return {"beat_id": body.beat_id, "ok": False, "error": error[:500], "snapshot": snapshot}
    return {"beat_id": body.beat_id, "ok": True, "ms": ms, "snapshot": snapshot}


@router.get("/v1/peers/{pack}")
async def peers(request: Request, pack: str, session: Actor) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        return await peers_view(conn, pack)


@router.get("/v1/views/calendar")
async def calendar(request: Request, session: Actor, city: str = "lucknow") -> dict[str, Any]:
    state = request.app.state
    today = state.clock.now_ist().date()
    try:
        upcoming = state.calendar.upcoming(city, today, within_days=60)
    except (KeyError, ValueError) as exc:
        raise refused(CommandError("calendar.unknown_city"), 422) from exc
    async with state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(local_events)
    return {
        "city": city,
        "upcoming": [
            {
                "id": o.id,
                "kind": o.kind,
                "name": o.names.get("en", o.id),
                "start": o.start.isoformat(),
                "end": o.end.isoformat(),
                "days_until": (o.start - today).days,
                "confidence": o.confidence,
                "source": o.source,
            }
            for o in upcoming
        ],
        "local_events": [{k: r[k] for k in ("id", "name", "kind", "start", "end")} for r in rows],
        "tentative_within_60_days": len([o for o in upcoming if o.confidence != "confirmed"]),
        "invalidate_on": ["calendar.local_event_added", "clock.day"],
    }
