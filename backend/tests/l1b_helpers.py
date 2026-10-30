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
