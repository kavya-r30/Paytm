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
