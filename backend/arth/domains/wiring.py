"""One place that registers every commerce domain on a Command Bus (app and tests share it)."""

from dataclasses import dataclass

from arth.core.packs import PackRegistry
from arth.domains.capital import register_capital
from arth.domains.catalog import register_catalog
from arth.domains.counter import register_counter
from arth.domains.inbox import register_inbox
from arth.domains.ledger import register_ledger
from arth.domains.offers import register_offers
from arth.domains.orders import register_orders
from arth.domains.patrons import PatronService
from arth.domains.sentinel import register_sentinel
from arth.domains.staff import StaffService
from arth.domains.stock import register_stock
from arth.domains.supply import register_supply
from arth.domains.tax import register_books
from arth.domains.treasury import register_treasury
from arth.domains.trust import register_trust
from arth.governance.commands import CommandBus
from arth.growth.engine import register_growth


@dataclass(frozen=True)
class Services:
    staff: StaffService
    patrons: PatronService


def register_commerce(bus: CommandBus, packs: PackRegistry, signing_key: str) -> Services:
    staff = StaffService(bus, signing_key)
    register_catalog(bus, packs)
    register_stock(bus, packs)
    patrons = PatronService(bus, signing_key)
    register_ledger(bus)
    register_counter(bus, packs)
    register_treasury(bus)
    register_offers(bus)
    register_books(bus)
    register_orders(bus, packs)
    register_supply(bus, packs)
    register_trust(bus, packs)
    register_capital(bus)
    register_sentinel(bus)
    register_inbox(bus)
    register_growth(bus, packs)
    return Services(staff=staff, patrons=patrons)
