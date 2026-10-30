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
from datetime import timedelta
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from arth.agents.commands import register_agent_commands
from arth.agents.playbooks import install as install_playbooks
from arth.agents.runtime import Runtime
from arth.agents.views import load_helpers
from arth.ai.conductor import Conductor
from arth.ai.router import ProviderRouter
from arth.api import (
    agents,
    commerce,
    commerce_core,
    director,
    governance,
    growth,
    health,
    intel,
    sim,
    stream,
    turns,
    views,
)
from arth.api.problems import install_problem_handlers
from arth.core.calendar import CalendarIndex, load_calendar
from arth.core.clock import SimClock, iso_utc
from arth.core.config import (
    Settings,
    check_auth_tokens,
    check_provider_keys,
    load_policies,
    load_providers,
)
from arth.core.db import Database
from arth.core.ids import new_id
from arth.core.migrate import upgrade
from arth.core.packs import PackRegistry
from arth.core.scheduler import Scheduler, tick_loop
from arth.core.spans import SpanBus
from arth.core.tables import jobs
from arth.domains.merchants import register_merchants
from arth.domains.security import load_signing_key
from arth.domains.wiring import register_commerce
from arth.governance.commands import CommandBus
from arth.governance.events import Dispatcher
from arth.governance.policy import PolicyEngine, Session
from arth.governance.repository import Repository
from arth.intel.commands import register_intel
from arth.sim import peers
from arth.sim.hub import Simulators
from arth.sim.personas import PersonaEngine


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
        app.state.commands.spans = spans
        app.state.commands.packs = app.state.packs
        register_merchants(app.state.commands, app.state.packs)
        signing_key = settings.session_signing_key or load_signing_key(
            settings.data_dir / "session-signing.key"
        )
        services = register_commerce(app.state.commands, app.state.packs, signing_key.get_secret_value())
        app.state.staff, app.state.patrons = services.staff, services.patrons
        async with db.read() as conn:
            app.state.commands.merchant_ids = await Repository.merchant_directory(conn)
        app.state.events = Dispatcher(db, clock)
        app.state.sim = Simulators(app.state.commands, app.state.events, signing_key.get_secret_value())
        app.state.personas = PersonaEngine()
        register_intel(app.state.commands, app.state.calendar)
        app.state.router = ProviderRouter(settings, app.state.providers, spans)
        app.state.conductor = Conductor(app.state.commands, app.state.router, app.state.calendar)
        app.state.runtime = Runtime(app.state.commands, app.state.events)
        install_playbooks(app.state.runtime, app.state.events)
        register_agent_commands(app.state.commands, app.state.runtime)
        app.state.helpers = load_helpers()
        growth.install_guardrails(app.state.events, clock)

        async def night_shift(job: Any) -> None:
            stamp = clock.now_ist().date().isoformat()
            for merchant_id in sorted(app.state.commands.merchant_ids):
                await app.state.runtime.start(merchant_id, "night_shift", stamp)

        scheduler.on("agents.night_shift", night_shift)
        async with db.read() as conn:
            pending = await conn.execute(
                select(jobs.c.id).where(jobs.c.name == "agents.night_shift", jobs.c.status == "pending")
            )
            if not pending.first():
                await scheduler.schedule_daily("agents.night_shift", "22:00")

        async def hourly_alerts(job: Any) -> None:
            stamp = iso_utc(clock.now())[:13]
            for merchant_id in sorted(app.state.commands.merchant_ids):
                actor = Session(merchant_id, new_id("system"), "system", actor_kind="system")
                await app.state.commands.submit(actor, "alerts.scan", {}, f"alerts-{stamp}")

        scheduler.on("intel.hourly", hourly_alerts)
        async with db.read() as conn:
            pending = await conn.execute(
                select(jobs.c.id).where(jobs.c.name == "intel.hourly", jobs.c.status == "pending")
            )
            if not pending.first():
                await scheduler.schedule("intel.hourly", clock.now() + timedelta(hours=1), every_seconds=3600)
        async with db.write() as conn:
            await peers.generate(conn)
        app.state.events.declare_view("trust", {"command.executed", "approval.decided"})
        app.state.events.declare_view("gates", {"approval.requested", "approval.decided"})
        for name, topics in {
            "settings/language": {"i18n.changed"},
            "onboarding": {"onboarding.started", "onboarding.updated"},
            "settings/staff": {"staff.added"},
            "staff/login": {"staff.added"},
            "shift": {"staff.shift_opened", "staff.shift_closed"},
            "catalog": {"catalog.item_added", "catalog.price_changed"},
            "stock": {"stock.changed", "batch.recalled"},
            "expiry": {"stock.changed", "batch.recalled", "clock.day"},
            "customers/search": {"patron.changed", "patron.merged"},
            "patron": {"patron.changed", "patron.consent_changed", "patron.merged", "patron.reward_changed"},
            "khata": {"credit.changed", "credit.reminder_requested", "patron.merged"},
            "statement": {"credit.changed", "credit.reminder_requested", "patron.merged"},
            "promises": {"credit.changed"},
            "payables": {"credit.payable_changed"},
            **views.VIEW_TOPICS,
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
                        await app.state.runtime.tick(merchant_id)
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
    app.include_router(commerce_core.router)
    app.include_router(views.router)
    app.include_router(sim.router)
    app.include_router(intel.router)
    app.include_router(turns.router)
    app.include_router(agents.router)
    app.include_router(growth.router)
    return app


app = create_app()
