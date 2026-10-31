"""RFC 9457 problem responses with a stable code and an i18n message key (spec Part C1)."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from arth.governance.commands import CommandError

ParamValue = str | int | float | bool


class ProblemError(Exception):
    def __init__(
        self,
        status: int,
        code: str,
        message_key: str,
        *,
        title: str,
        detail: str | None = None,
        params: dict[str, ParamValue] | None = None,
    ) -> None:
        super().__init__(f"{status} {code}")
        self.status, self.code, self.message_key = status, code, message_key
        self.title, self.detail, self.params = title, detail, params or {}


def install_problem_handlers(app: FastAPI) -> None:
    @app.exception_handler(CommandError)
    async def _command_error(_request: Request, exc: CommandError) -> JSONResponse:
        code = str(exc)
        return JSONResponse(
            {
                "type": "https://arth.local/problems/" + code,
                "title": "Command refused",
                "status": 409,
                "code": code,
                "message_key": "error." + code,
            },
            status_code=409,
            media_type="application/problem+json",
        )

    @app.exception_handler(ProblemError)
    async def _handle(_request: Request, exc: ProblemError) -> JSONResponse:
        body: dict[str, object] = {
            "type": f"https://arth.local/problems/{exc.code}",
            "title": exc.title,
            "status": exc.status,
            "code": exc.code,
            "message_key": exc.message_key,
        }
        if exc.detail:
            body["detail"] = exc.detail
        if exc.params:
            body["params"] = exc.params
        return JSONResponse(body, status_code=exc.status, media_type="application/problem+json")
