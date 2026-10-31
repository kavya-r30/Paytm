from l1b_helpers import make_bus

from arth.domains.wiring import register_commerce
from arth.governance.events import Dispatcher
from arth.sim.hub import Simulators

KEY = "synthetic-l2-signing-key"


def make_world_bus(db):
    bus = make_bus(db)
    services = register_commerce(bus, bus.packs, KEY)
    dispatcher = Dispatcher(db, bus.clock)
    sim = Simulators(bus, dispatcher, KEY)
    return bus, services, dispatcher, sim


async def build_world(db, pack="kirana", days=3, seed=1, patrons=12, size="micro"):
    from arth.sim.world import WorldBuilder, WorldSpec

    bus, services, dispatcher, sim = make_world_bus(db)
    builder = WorldBuilder(
        sim, services.patrons, WorldSpec(pack=pack, days=days, seed=seed, patrons=patrons, size=size)
    )
    manifest = await builder.build()
    await dispatcher.dispatch(manifest["merchant_id"])
    return bus, sim, dispatcher, manifest
