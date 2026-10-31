"""Provider Router (T4.1): roles → provider chains with timeouts, token buckets, data tags, cassettes, spans.

Live adapters call Azure OpenAI, Mistral, Groq and Sarvam over HTTPS (one pooled client) with keys from
`Settings` (SecretStr, never logged).
When a hop fails (no key, timeout, HTTP error, network blocked) the next hop runs; the `cassette` hop replays
a recorded response keyed by a hash of the request. Live successes are recorded in dev/demo for exact replay.
Data tags (AIQ-3): a request tagged `merchant` never goes to a provider tagged `synthetic_only_*`.
"""

import asyncio
import base64
import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import httpx

from arth.core.config import Providers, Settings
from arth.core.paths import BACKEND_DIR
from arth.core.spans import SpanBus

CASSETTES = BACKEND_DIR / "cassettes"
ENDPOINTS = {
    "mistral": "https://api.mistral.ai/v1",
    "groq": "https://api.groq.com/openai/v1",
    "sarvam": "https://api.sarvam.ai",
}
PRICE_PAISE_PER_1K_TOKENS = {"azure": 25, "mistral": 20, "groq": 5, "sarvam": 10}


class ProviderUnavailable(RuntimeError):
    pass


@dataclass
class Bucket:
    rpm: int
    tokens: float = 0.0
    stamp: float = field(default_factory=time.monotonic)

    def take(self) -> bool:
        now = time.monotonic()
        self.tokens = min(self.rpm, self.tokens + (now - self.stamp) * self.rpm / 60)
        self.stamp = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


@dataclass
class Result:
    role: str
    provider: str
    model: str
    mode: str  # live | replay
    text: str = ""
    data: Any = None
    latency_ms: int = 0
    cost_paise: int = 0


def request_key(role: str, request: dict[str, Any]) -> str:
    return hashlib.sha256(
        (role + json.dumps(request, sort_keys=True, ensure_ascii=False)).encode()
    ).hexdigest()[:24]


class ProviderRouter:
    def __init__(
        self,
        settings: Settings,
        providers: Providers,
        spans: SpanBus | None = None,
        cassettes: Path = CASSETTES,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.settings, self.providers, self.spans, self.cassettes = settings, providers, spans, cassettes
        self.transport = transport
        self.buckets = {
            name: Bucket(p.rate.get("rpm", 120), p.rate.get("rpm", 120))
            for name, p in providers.providers.items()
        }
        self.record = settings.mode in {"dev", "demo"}
        self.status: dict[str, str] = {name: "unknown" for name in providers.providers}
        self.spend_paise = 0
        self.offline = False  # Director fault: every live hop fails, cassettes and templates take over
        self.last_errors: dict[str, list[str]] = {}  # role → per-hop failures of the last call (diagnostics)
        self._client: httpx.AsyncClient | None = None  # pooled: a TLS handshake per call ate the LLM timeout

    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(transport=self.transport, timeout=20)
        return self._client

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()

    # public API -------------------------------------------------------------------------------
    async def chat(
        self,
        role: str,
        messages: list[dict[str, Any]],
        *,
        json_mode: bool = False,
        data_tag: str = "merchant",
        tools: list[dict[str, Any]] | None = None,
    ) -> Result:
        request = {"messages": messages, "json": json_mode, "tools": tools or []}
        return await self._run(role, request, data_tag)

    async def speech_to_text(self, audio: bytes, lang: str = "hi-IN") -> Result:
        request = {"audio_sha": hashlib.sha256(audio).hexdigest(), "lang": lang}
        return await self._run("stt", request, "merchant", payload={"audio": audio})

    async def text_to_speech(self, text: str, lang: str = "hi-IN", speaker: str = "anushka") -> Result:
        return await self._run("tts", {"text": text, "lang": lang, "speaker": speaker}, "merchant")

    async def translate(self, text: str, source: str, target: str) -> Result:
        return await self._run("translate", {"text": text, "source": source, "target": target}, "merchant")

    async def ocr(self, image: bytes, mime: str = "image/png") -> Result:
        request = {"image_sha": hashlib.sha256(image).hexdigest(), "mime": mime}
        return await self._run("ocr", request, "merchant", payload={"image": image})

    # chain --------------------------------------------------------------------------------------
    async def _run(
        self, role: str, request: dict[str, Any], data_tag: str, payload: dict[str, Any] | None = None
    ) -> Result:
        chain = self.providers.roles[role].chain
        errors: list[str] = []
        for hop in chain:
            started = time.monotonic()
            try:
                if hop.provider == "cassette":
                    result = self._replay(role, request)
                elif self.offline:
                    raise ProviderUnavailable("offline")
                else:
                    tag = self.providers.providers[hop.provider].data_tag
                    if data_tag == "merchant" and tag.startswith("synthetic_only"):
                        raise ProviderUnavailable("data_tag")  # AIQ-3: no merchant data to this provider
                    key = self.settings.secret(self.providers.providers[hop.provider].api_key_env)
                    if key is None:
                        raise ProviderUnavailable("no_key")
                    if not self.buckets[hop.provider].take():
                        raise ProviderUnavailable("rate_limited")
                    result = await asyncio.wait_for(
                        self._live(
                            hop.provider,
                            hop.model or "",
                            role,
                            request,
                            payload or {},
                            key.get_secret_value(),
                            hop.speaker,
                        ),
                        timeout=hop.timeout_ms / 1000 if hop.timeout_ms else 10,
                    )
                    self.status[hop.provider] = "live"
                    if self.record:
                        self._store(role, request, result)
                self.last_errors[role] = errors
                result.latency_ms = int((time.monotonic() - started) * 1000)
                self.spend_paise += result.cost_paise
                await self._span(role, result, ok=True)
                return result
            except (TimeoutError, ProviderUnavailable, httpx.HTTPError, KeyError, ValueError) as exc:
                if hop.provider != "cassette":
                    self.status[hop.provider] = "fallback"
                detail = ""
                if isinstance(exc, httpx.HTTPStatusError):
                    detail = " " + exc.response.text[:200].replace(
                        "\n", " "
                    )  # provider error body, never the key
                errors.append(f"{hop.provider}/{hop.model}:{type(exc).__name__}:{exc}{detail}")
        self.last_errors[role] = errors
        raise ProviderUnavailable("; ".join(errors))

    async def _span(self, role: str, result: Result, ok: bool) -> None:
        if self.spans is None:
            return
        async with self.spans.span(
            "llm", role, mode="replay" if result.mode == "replay" else "live"
        ) as trace:
            trace["provider"], trace["model"] = result.provider, result.model
            trace["latency_ms"], trace["cost_paise"] = result.latency_ms, result.cost_paise

    def _path(self, role: str, request: dict[str, Any]) -> Path:
        return self.cassettes / role / f"{request_key(role, request)}.json"

    def _replay(self, role: str, request: dict[str, Any]) -> Result:
        path = self._path(role, request)
        if not path.exists():
            raise ProviderUnavailable("no_cassette")
        data = json.loads(path.read_text(encoding="utf-8"))
        return Result(role, data["provider"], data["model"], "replay", data.get("text", ""), data.get("data"))

    def _store(self, role: str, request: dict[str, Any], result: Result) -> None:
        path = self._path(role, request)
        path.parent.mkdir(parents=True, exist_ok=True)
        data = result.data if not isinstance(result.data, bytes) else base64.b64encode(result.data).decode()
        path.write_text(
            json.dumps(
                {"provider": result.provider, "model": result.model, "text": result.text, "data": data},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    # adapters ---------------------------------------------------------------------------------
    def _chat_target(self, provider: str, model: str, key: str) -> tuple[str, dict[str, str]]:
        """OpenAI-compatible chat URL and auth header; Azure puts the deployment (= model) in the path."""
        if provider == "azure":
            base = (self.settings.azure_openai_endpoint or "").rstrip("/")
            version = self.settings.azure_openai_api_version
            url = f"{base}/openai/deployments/{model}/chat/completions?api-version={version}"
            return url, {"api-key": key}
        return f"{ENDPOINTS[provider]}/chat/completions", {"Authorization": f"Bearer {key}"}

    async def _live(
        self,
        provider: str,
        model: str,
        role: str,
        request: dict[str, Any],
        payload: dict[str, Any],
        key: str,
        speaker: str | None = None,
    ) -> Result:
        client = self.client()
        if provider in {"azure", "mistral", "groq"} and role not in {"ocr", "stt"}:
            body: dict[str, Any] = {"messages": request["messages"], "temperature": 0.2}
            if provider != "azure":
                body["model"] = model
            if request.get("json"):
                body["response_format"] = {"type": "json_object"}
            if request.get("tools"):
                body["tools"] = request["tools"]
            url, auth = self._chat_target(provider, model, key)
            response = await client.post(url, json=body, headers=auth)
            response.raise_for_status()
            data = response.json()
            message = data["choices"][0]["message"]
            tokens = data.get("usage", {}).get("total_tokens", 0)
            return Result(
                role,
                provider,
                model,
                "live",
                message.get("content") or "",
                {"tool_calls": message.get("tool_calls") or []},
                cost_paise=tokens * PRICE_PAISE_PER_1K_TOKENS[provider] // 1000,
            )
        if provider == "mistral" and role == "ocr":
            image = base64.b64encode(payload["image"]).decode()
            response = await client.post(
                f"{ENDPOINTS['mistral']}/ocr",
                headers={"Authorization": f"Bearer {key}"},
                json={
                    "model": model,
                    "document": {
                        "type": "image_url",
                        "image_url": f"data:{request['mime']};base64,{image}",
                    },
                },
            )
            response.raise_for_status()
            pages = response.json().get("pages", [])
            return Result(role, provider, model, "live", "\n".join(p.get("markdown", "") for p in pages))
        if provider == "groq" and role == "stt":
            files = {"file": ("audio.wav", payload["audio"], "audio/wav")}
            response = await client.post(
                f"{ENDPOINTS['groq']}/audio/transcriptions",
                files=files,
                data={"model": model},
                headers={"Authorization": f"Bearer {key}"},
            )
            response.raise_for_status()
            return Result(role, provider, model, "live", response.json().get("text", ""))
        if provider == "sarvam":
            headers = {"api-subscription-key": key}
            if role == "stt":
                files = {"file": ("audio.wav", payload["audio"], "audio/wav")}
                response = await client.post(
                    f"{ENDPOINTS['sarvam']}/speech-to-text",
                    files=files,
                    data={"model": model, "language_code": request["lang"]},
                    headers=headers,
                )
                response.raise_for_status()
                return Result(role, provider, model, "live", response.json().get("transcript", ""))
            if role == "tts":
                response = await client.post(
                    f"{ENDPOINTS['sarvam']}/text-to-speech",
                    headers=headers,
                    json={
                        "text": request["text"],
                        "target_language_code": request["lang"],
                        "speaker": speaker or request["speaker"],
                        "model": model,
                    },
                )
                response.raise_for_status()
                return Result(role, provider, model, "live", data=response.json().get("audios", [""])[0])
            if role == "translate":
                response = await client.post(
                    f"{ENDPOINTS['sarvam']}/translate",
                    headers=headers,
                    json={
                        "input": request["text"],
                        "source_language_code": request["source"],
                        "target_language_code": request["target"],
                    },
                )
                response.raise_for_status()
                return Result(role, provider, model, "live", response.json().get("translated_text", ""))
        raise ProviderUnavailable(f"{provider} cannot serve {role}")

    def health(self) -> dict[str, Any]:
        return {"providers": dict(self.status), "spend_paise": self.spend_paise}
