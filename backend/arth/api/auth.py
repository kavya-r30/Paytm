"""Bearer-token stubs per surface (device, console, director). Real sessions and PINs arrive in L1 (STF-2)."""

from __future__ import annotations

import secrets
from collections.abc import Awaitable, Callable
from typing import Literal

from fastapi import Request

from arth.api.problems import ProblemError

Surface = Literal["device", "console", "director"]


def require_token(surface: Surface) -> Callable[[Request], Awaitable[None]]:
    async def dependency(request: Request) -> None:
        # The tokens are SecretStr: unwrap only here, and compare in constant time.
        token = getattr(request.app.state.settings, f"{surface}_token")
        expected = f"Bearer {token.get_secret_value()}"
        given = request.headers.get("authorization", "")
        if not secrets.compare_digest(given.encode(), expected.encode()):
            raise ProblemError(
                401,
                "auth.missing_token",
                "error.auth.missing_token",
                title="Unauthorized",
                params={"surface": surface},
            )

    return dependency
