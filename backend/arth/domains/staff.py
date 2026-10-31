"""PIN-backed staff sessions and shift ownership. Secrets never enter bus persistence."""

import hashlib
import hmac
from datetime import timedelta
from typing import Any

from arth.core.clock import iso_utc
from arth.core.ids import new_id
from arth.core.schemas import schema
from arth.domains.merchants import domain_event, owner_only
from arth.domains.security import hash_pin, verify_pin
from arth.domains.tables import devices, shifts, staff_credentials, staff_sessions
from arth.governance.commands import CommandBus, CommandError
from arth.governance.policy import Session
from arth.governance.repository import Repository
from arth.governance.tables import staff


class StaffService:
    def __init__(self, bus: CommandBus, signing_key: str) -> None:
        self.bus, self._key = bus, signing_key.encode()
        self._register()
        bus.session_validator = self.validate

    def _sign(self, merchant_id: str, identity: str, kind: str) -> str:
        if any("." in value for value in (merchant_id, identity, kind)):
            raise CommandError("auth.bad_identity")
        body = ".".join((merchant_id, identity, kind))
        return body + "." + hmac.new(self._key, body.encode(), hashlib.sha256).hexdigest()

    def _decode(self, token: str, kind: str) -> tuple[str, str]:
        parts = token.split(".")
        if len(parts) != 4 or len(token) > 500 or parts[2] != kind:
            raise CommandError("auth.invalid_session")
        merchant_id, identity, _, signature = parts
        expected = self._sign(merchant_id, identity, kind).rsplit(".", 1)[1]
        if not hmac.compare_digest(signature, expected):
            raise CommandError("auth.invalid_session")
        return merchant_id, identity

    def device_credential(self, merchant_id: str, device_id: str) -> str:
        return self._sign(merchant_id, device_id, "device")

    def device_identity(self, credential: str) -> tuple[str, str]:
        return self._decode(credential, "device")

    async def resolve(self, token: str) -> Session:
        mid, sid = self._decode(token, "session")
        async with self.bus.db.read() as conn:
            repo = Repository(conn, mid)
            rows = await repo.select(staff_sessions, staff_sessions.c.id == sid)
            if not rows:
                raise CommandError("auth.invalid_session")
            row = rows[0]
            actors = await repo.select(staff, staff.c.id == row["staff_id"])
            if not actors:
                raise CommandError("auth.invalid_session")
            session = Session(
                mid,
                row["staff_id"],
                actors[0]["role"],
                channel=row["channel"],
                device_id=row["device_id"],
                session_id=sid,
            )
            await self.validate(repo, session)
            return session

    async def validate(self, repo: Repository, session: Session) -> None:
        if session.session_id is None:
            return  # trusted internal actors and initial provisioning
        rows = await repo.select(staff_sessions, staff_sessions.c.id == session.session_id)
        actors = await repo.select(staff, staff.c.id == session.actor_id)
        registered = await repo.select(devices, devices.c.id == session.device_id)
        if not rows or not actors or not registered:
            raise CommandError("auth.invalid_session")
        row = rows[0]
        valid_channel = row["channel"] == session.channel or (
            row["channel"] == "device"
            and session.channel == "voice"
            and session.role == "owner"
            and session.owner_ptt
        )
        if (
            row["revoked"]
            or row["expires_at"] <= iso_utc(self.bus.clock.now())
            or row["staff_id"] != session.actor_id
            or not valid_channel
            or row["device_id"] != session.device_id
            or actors[0]["role"] != session.role
        ):
            raise CommandError("auth.expired_session")

    async def login(
        self, device_credential: str, staff_id: str, pin: str, channel: str, key: str
    ) -> dict[str, Any]:
        if channel not in {"device", "console"}:
            raise CommandError("auth.invalid_channel")
        mid, device_id = self._decode(device_credential, "device")
        async with self.bus.db.read() as conn:
            repo = Repository(conn, mid)
            actors = await repo.select(staff, staff.c.id == staff_id)
            credentials = await repo.select(staff_credentials, staff_credentials.c.staff_id == staff_id)
            if not actors or not credentials or not await repo.select(devices, devices.c.id == device_id):
                raise CommandError("staff.invalid_login")
            valid = verify_pin(pin, credentials[0]["pin_hash"])
        result = await self.bus.submit(
            Session(mid, staff_id, actors[0]["role"], channel=channel, device_id=device_id),
            "staff.login",
            {"staff_id": staff_id, "device_id": device_id, "channel": channel},
            key if valid else new_id("attempt"),
            private={"pin": pin},
        )
        if not valid or not result["data"]["authenticated"]:
            raise CommandError(result["data"].get("code", "staff.invalid_login"))
        token = self._sign(mid, result["data"]["session_id"], "session")
        await self.resolve(token)  # replay cannot revive an expired/revoked session
        return {"token": token, "staff_id": staff_id, "expires_at": result["data"]["expires_at"]}

    async def issue(
        self, merchant_id: str, staff_id: str, device_id: str, channel: str, key: str
    ) -> dict[str, Any]:
        """Presenter-only (director token checked by the API): a real session without a PIN, for the stage."""
        if channel not in {"device", "console"}:
            raise CommandError("auth.invalid_channel")
        async with self.bus.db.read() as conn:
            actors = await Repository(conn, merchant_id).select(staff, staff.c.id == staff_id)
        if not actors:
            raise CommandError("staff.invalid_login")
        result = await self.bus.submit(
            Session(merchant_id, staff_id, actors[0]["role"], channel=channel, device_id=device_id),
            "staff.login",
            {"staff_id": staff_id, "device_id": device_id, "channel": channel},
            key,
            private={"presenter_issued": True},
        )
        token = self._sign(merchant_id, result["data"]["session_id"], "session")
        return {"token": token, "staff_id": staff_id, "expires_at": result["data"]["expires_at"]}

    async def add(self, actor: Session, name: str, role: str, pin: str, key: str) -> dict[str, Any]:
        return await self.bus.submit(
            actor, "staff.add", {"name": name, "role": role}, key, private={"pin": pin}
        )

    def _register(self) -> None:
        bus = self.bus

        async def add(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            owner_only(repo)
            if "pin" not in repo.private:
                raise CommandError("staff.pin_required")
            identity = new_id("staff")
            await repo.insert(staff, {"id": identity, **payload})
            await repo.insert(
                staff_credentials, {"staff_id": identity, "pin_hash": hash_pin(repo.private["pin"])}
            )
            await domain_event(bus, repo, "staff.added", {"staff_id": identity, "role": payload["role"]})
            return {"staff_id": identity, "name": payload["name"], "role": payload["role"]}

        async def login(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if (
                repo.session is None
                or repo.session.actor_id != payload["staff_id"]
                or ("pin" not in repo.private and not repo.private.get("presenter_issued"))
            ):
                raise CommandError("staff.invalid_login")
            rows = await repo.select(staff_credentials, staff_credentials.c.staff_id == payload["staff_id"])
            if not rows:
                raise CommandError("staff.invalid_login")
            row = rows[0]
            now = iso_utc(bus.clock.now())
            if row["locked_until"] and row["locked_until"] > now:
                return {"authenticated": False, "code": "staff.locked"}
            presenter = bool(repo.private.get("presenter_issued"))
            if not presenter and not verify_pin(repo.private["pin"], row["pin_hash"]):
                failed = (row["failed"] if not row["locked_until"] or row["locked_until"] > now else 0) + 1
                await repo.update(
                    staff_credentials,
                    {
                        "failed": failed,
                        "locked_until": iso_utc(bus.clock.now() + timedelta(minutes=5))
                        if failed >= 5
                        else None,
                    },
                    staff_credentials.c.staff_id == payload["staff_id"],
                )
                return {"authenticated": False, "code": "staff.invalid_login"}
            await repo.update(
                staff_credentials,
                {"failed": 0, "locked_until": None},
                staff_credentials.c.staff_id == payload["staff_id"],
            )
            sid = new_id("session")
            expires = iso_utc(bus.clock.now() + timedelta(hours=12))
            await repo.insert(
                staff_sessions,
                {
                    "id": sid,
                    "staff_id": payload["staff_id"],
                    "device_id": payload["device_id"],
                    "channel": payload["channel"],
                    "expires_at": expires,
                },
            )
            await domain_event(
                bus, repo, "staff.logged_in", {"staff_id": payload["staff_id"], "session_id": sid}
            )
            return {"authenticated": True, "session_id": sid, "expires_at": expires}

        async def logout(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            if repo.session is None or repo.session.session_id is None:
                raise CommandError("auth.invalid_session")
            await repo.update(staff_sessions, {"revoked": 1}, staff_sessions.c.id == repo.session.session_id)
            return {"logged_out": True}

        async def open_shift(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            assert repo.session is not None
            if await repo.select(
                shifts, shifts.c.staff_id == repo.session.actor_id, shifts.c.closed_at.is_(None)
            ):
                raise CommandError("shift.already_open")
            identity = new_id("shift")
            await repo.insert(
                shifts,
                {
                    "id": identity,
                    "staff_id": repo.session.actor_id,
                    "opened_at": iso_utc(bus.clock.now()),
                    "float_paise": payload["float_paise"],
                    "expected_paise": payload["float_paise"],
                },
            )
            await domain_event(
                bus, repo, "staff.shift_opened", {"shift_id": identity, "staff_id": repo.session.actor_id}
            )
            return {"shift_id": identity, "staff_id": repo.session.actor_id}

        async def close_shift(repo: Repository, payload: dict[str, Any]) -> dict[str, Any]:
            assert repo.session is not None
            rows = await repo.select(
                shifts,
                shifts.c.id == payload["shift_id"],
                shifts.c.staff_id == repo.session.actor_id,
                shifts.c.closed_at.is_(None),
            )
            if not rows:
                raise CommandError("shift.not_open")
            from arth.domains.treasury import shift_cash

            now = iso_utc(bus.clock.now())
            expected = await shift_cash(repo, rows[0], now)  # STF-3: float + cash in − cash out
            variance = payload["counted_paise"] - expected
            await repo.update(
                shifts,
                {
                    "closed_at": now,
                    "expected_paise": expected,
                    "counted_paise": payload["counted_paise"],
                    "variance_paise": variance,
                },
                shifts.c.id == payload["shift_id"],
            )
            await domain_event(
                bus, repo, "staff.shift_closed", {"shift_id": payload["shift_id"], "variance_paise": variance}
            )
            return {
                "shift_id": payload["shift_id"],
                "staff_id": repo.session.actor_id,
                "expected_paise": expected,
                "variance_paise": variance,
            }

        bus.register("staff.add", schema("staff_add_command"), add)
        bus.register("staff.login", schema("staff_login_command"), login)
        bus.register("staff.logout", schema("staff_logout"), logout)
        bus.register("shift.open", schema("shift_open"), open_shift)
        bus.register("shift.close", schema("shift_close"), close_shift)
