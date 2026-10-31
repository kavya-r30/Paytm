# Generated from contracts. Do not edit; run `python dev.py gen`.

from __future__ import annotations

from enum import Enum

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field, conint, constr


class Status(Enum):
    open = 'open'
    parked = 'parked'
    closed = 'closed'
    voided = 'voided'


class Payment(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    mode: constr(min_length=1, max_length=200)
    amount_paise: conint(ge=1)
    change_paise: conint(ge=0) | None
    ref_id: constr(min_length=1, max_length=200) | None


class Status6(Enum):
    new = 'new'
    preparing = 'preparing'
    ready = 'ready'
    served = 'served'


class Status7(Enum):
    waiting = 'waiting'
    pending = 'pending'
    paid = 'paid'
    failed = 'failed'
    expired = 'expired'


class Upi(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    order_ref: constr(min_length=1)
    amount_paise: conint(ge=1)
    status: Status7
    expires_at: AwareDatetime


class Alternative(Enum):
    cash = 'cash'
    khata = 'khata'
    regenerate = 'regenerate'


class Line(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    item_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    name: constr(min_length=1, max_length=200)
    qty_milli: conint(ge=1)
    unit_price_paise: conint(ge=0)
    amount_paise: conint(ge=0)
    added_via: constr(min_length=1, max_length=200)
    modifier_ids: list[constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$')]
    price_override: bool
    batch_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None


class Ticket(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    token: conint(ge=1)
    status: Status6


class Patron(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    display_name: str
    lang: str
    khata_balance_paise: int | None
    reward_stamps: int


class Bill(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') = Field(
        ...,
        description='A ULID prefixed by its kind, e.g. bill_01JBQ0Z7Y8K3M4N5P6Q7R8S9T1 (spec Part C1).',
    )
    status: Status
    patron_id: constr(pattern=r'^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$') | None
    staff_id: constr(min_length=1, max_length=200)
    opened_at: AwareDatetime
    closed_at: AwareDatetime | None
    total_paise: conint(ge=0)
    paid_paise: conint(ge=0)
    khata_paise: conint(ge=0)
    due_paise: conint(ge=0)
    lines: list[Line]
    payments: list[Payment]
    ticket: Ticket | None
    upi: Upi | None
    patron: Patron | None


class BillPayView(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    bill: Bill
    payee_vpa: constr(min_length=1, max_length=200) | None
    alternatives: list[Alternative]
    exception: constr(min_length=1, max_length=200) | None
    invalidate_on: list[constr(min_length=1, max_length=200)]
    pay_token: constr(pattern=r'^[0-9a-z]{26}$') | None = Field(
        ...,
        description="Rails-simulator token of the current dynamic QR: the customer's UPI app opens /pay/<token> (null before a QR is requested).",
    )
