"""POST /v1/turns (T4.15): voice or text on device, console, voice and WhatsApp; shared session memory."""

import base64
import json
from typing import Annotated, Any

from fastapi import APIRouter, Header, Query, Request

from arth.ai.language import normalise_for_tts
from arth.ai.router import ProviderUnavailable
from arth.ai.tables import turns
from arth.api.commerce import Actor
from arth.api.problems import ProblemError
from arth.contracts.turn_request import TurnRequest
from arth.governance.repository import Repository

router = APIRouter()


@router.post("/v1/turns")
async def turn(
    request: Request,
    body: TurnRequest,
    session: Actor,
    idempotency_key: Annotated[str, Header(min_length=1, max_length=200)],
) -> dict[str, Any]:
    state = request.app.state
    text = body.text
    if body.audio_b64 and not text:
        try:
            heard = await state.router.speech_to_text(base64.b64decode(body.audio_b64))
        except (ProviderUnavailable, ValueError) as exc:
            raise ProblemError(
                503, "speech.unavailable", "error.speech.unavailable", title="Speech unavailable"
            ) from exc
        text = heard.text
    if not text:
        raise ProblemError(422, "turn.empty", "error.turn.empty", title="Nothing heard")
    result: dict[str, Any] = await state.conductor.handle(
        session, text, body.surface.value, bill_id=body.bill_id, key=idempotency_key
    )
    state.events.publish(session.merchant_id, {"type": "envelope", "event_id": result["turn_id"], **result})
    return result


@router.get("/v1/views/ask")
async def ask(
    request: Request, session: Actor, session_ref: Annotated[str | None, Query(alias="session")] = None
) -> dict[str, Any]:
    async with request.app.state.db.read() as conn:
        rows = await Repository(conn, session.merchant_id).select(turns)
    rows = sorted(
        (r for r in rows if not session_ref or r["session_ref"] == session_ref), key=lambda r: r["created_at"]
    )[-20:]
    return {
        "session": session_ref,
        "turns": [
            {
                "id": r["id"],
                "surface": r["surface"],
                "heard": r["heard"],
                "intent": r["intent"],
                "said": json.loads(r["envelope"])["speech"]["text"],
                "created_at": r["created_at"],
            }
            for r in rows
        ],
        "invalidate_on": ["turn.completed"],
    }


@router.get("/v1/tts")
async def tts(
    request: Request,
    session: Actor,
    text: Annotated[str, Query(min_length=1, max_length=500)],
    lang: str = "hi-IN",
) -> dict[str, Any]:
    spoken = normalise_for_tts(text, "en" if lang.startswith("en") else "hi")
    try:
        result = await request.app.state.router.text_to_speech(spoken, lang)
        return {
            "text": text,
            "spoken_text": spoken,
            "lang": lang,
            "audio_b64": result.data,
            "mode": result.mode,
        }
    except ProviderUnavailable:
        return {"text": text, "spoken_text": spoken, "lang": lang, "audio_b64": None, "mode": "unavailable"}
