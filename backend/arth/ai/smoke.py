"""`python dev.py ai-smoke` (T4.2): one live call per role and provider; records cassettes for offline replay.

Run where the providers are reachable (a laptop with backend/.env). Prints only roles, providers and modes.
"""

import asyncio
import sys

from arth.ai.router import ProviderRouter, ProviderUnavailable
from arth.core.config import Settings, load_providers


async def main() -> int:
    settings = Settings()
    router = ProviderRouter(settings, load_providers(settings.config_dir / "providers.yaml"))
    router.record = True
    checks = [
        (
            "llm.fast",
            router.chat(
                "llm.fast",
                [{"role": "user", "content": 'Reply with JSON {"ok": true}'}],
                json_mode=True,
                data_tag="synthetic",
            ),
        ),
        (
            "llm.large",
            router.chat(
                "llm.large", [{"role": "user", "content": "Say namaste in one word."}], data_tag="synthetic"
            ),
        ),
        ("tts", router.text_to_speech("Namaste, Arth hazir hai.", "hi-IN")),
        ("translate", router.translate("Your order is ready.", "en-IN", "hi-IN")),
    ]
    failures = 0
    for name, call in checks:
        try:
            result = await call
            print(f"{name}: {result.provider}/{result.model} {result.mode} {result.latency_ms} ms")
        except ProviderUnavailable as exc:
            failures += 1
            print(f"{name}: UNAVAILABLE {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
