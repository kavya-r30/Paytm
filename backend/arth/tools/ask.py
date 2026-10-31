"""Ask Arth from the terminal, one turn per argument, against the running API (the device's own path).

    python -m arth.tools.ask "hi" "Priya ka bill banao, 2 Parle-G aur ek Maggi" "khate mein daal do"

Turns share one device session and carry the open bill forward, so chained counter talk works as on the
device. Prints what Arth said, the screen it opened, any approval it raised and how long it took.
"""

from __future__ import annotations

import sys
import time
import uuid

import httpx


def main(questions: list[str]) -> int:
    api = httpx.Client(base_url="http://localhost:8000", timeout=120)
    director = {"Authorization": "Bearer dev-director"}
    token = api.post("/v1/director/session", json={"surface": "device"}, headers=director).json()["token"]
    auth = {"Authorization": f"Bearer {token}"}
    bill: str | None = None
    for text in questions:
        started = time.monotonic()
        body: dict[str, object] = {"text": text, "surface": "device", **({"bill_id": bill} if bill else {})}
        res = api.post("/v1/turns", json=body, headers=auth | {"Idempotency-Key": uuid.uuid4().hex})
        ms = int((time.monotonic() - started) * 1000)
        if res.status_code != 200:
            print(f"\n> {text}\n  HTTP {res.status_code} {res.text[:200]}")
            continue
        env = res.json()
        nav = env.get("nav") or {}
        bill = (nav.get("params") or {}).get("bill_id") or bill
        gates = [c for c in env.get("cards") or [] if c.get("type") == "approval"]
        print(f"\n> {text}   [{ms} ms]")
        print(f"  Arth: {env['speech']['text']}")
        if nav:
            print(f"  screen: {nav.get('screen')} {nav.get('params') or ''}")
        for gate in gates:
            print(f"  waiting for owner's yes: {gate['tier']} gate {gate['id']}")
        if env.get("provenance"):
            print(f"  tools: {', '.join(p['kind'] for p in env['provenance'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["Aaj kitna aaya?"]))
