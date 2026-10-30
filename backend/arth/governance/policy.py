"""Deterministic governance on trusted session and domain facts."""

from dataclasses import dataclass, field

from arth.core.clock import SimClock
from arth.core.config import Policies, Tier


@dataclass(frozen=True)
class Session:
    merchant_id: str
    actor_id: str
    role: str
    channel: str = "device"
    device_id: str | None = None
    owner_ptt: bool = False
    step_up: bool = False
    session_id: str | None = None
    actor_kind: str | None = None


@dataclass(frozen=True)
class PolicyContext:
    facts: dict[str, int | str | bool] = field(default_factory=dict)
    purpose: str | None = None
    consent: bool = False
    weekly_contacts: int = 0
    sensitive: bool = False
    message_class: str | None = None
    reply_age_seconds: int | None = None
    known_supplier: bool = False
    approved_template: bool = False
    margin: float | None = None
    spend_paise: int = 0
    flags: tuple[str, ...] = ()


@dataclass(frozen=True)
class Decision:
    code: str = "allow"
    discreet: bool = False


class PolicyEngine:
    def __init__(self, policies: Policies, clock: SimClock) -> None:
        self.policies, self.clock = policies, clock

    def evaluate(
        self, kind: str, tier: Tier, session: Session, context: PolicyContext | None = None
    ) -> Decision:
        context = context or PolicyContext()
        role = self.policies.roles.get(session.role)
        if role is None or (tier > role.max_tier and kind not in role.allow):
            return Decision("policy.role")
        if tier == "R3" and session.role != "owner":
            return Decision("policy.owner_required")
        if tier == "R4" and (session.channel != "console" or not session.step_up):
            return Decision("policy.console_required")
        now = self.clock.now_ist().strftime("%H:%M")
        quiet = self.policies.quiet_hours

        def in_window(start: str, end: str) -> bool:
            return start <= now < end if start < end else now >= start or now < end

        if context.purpose:
            if not context.consent:
                return Decision("policy.consent")
            if in_window(quiet.start, quiet.end):
                return Decision("policy.quiet_hours")
            cap = (
                self.policies.contact_caps.marketing_per_patron_per_week
                if context.purpose == "marketing"
                else self.policies.reminders.per_patron_per_week
                if context.purpose == "reminders"
                else None
            )
            if cap is not None and context.weekly_contacts >= cap:
                return Decision("policy.contact_cap")
            if tier == "R1":
                valid = (
                    context.message_class in {"receipt", "offer_terms"}
                    or context.message_class == "reply"
                    and context.reply_age_seconds is not None
                    and 0 <= context.reply_age_seconds <= 600
                    or context.message_class == "rfq"
                    and context.known_supplier
                    and context.approved_template
                )
                if not valid:
                    return Decision("policy.message_class")
        if context.margin is not None and context.margin < self.policies.growth.margin_floor:
            return Decision("policy.margin_floor")
        if context.spend_paise > self.policies.growth.monthly_incentive_budget_paise:
            return Decision("policy.budget")
        if set(context.flags) & set(self.policies.forbid_offers_on_flags):
            return Decision("policy.pack")
        discreet = context.sensitive and any(
            in_window(*window.split("-")) for window in self.policies.discreet_mode.busy_hours
        )
        return Decision(discreet=discreet)
