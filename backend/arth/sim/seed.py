"""`python dev.py seed`: generate a demo shop world into the real data DB and print how to log in."""

import argparse
import json

from fastapi.testclient import TestClient

from arth.core.config import Settings
from arth.main import create_app
from arth.sim.world import WorldBuilder, WorldSpec


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed a generated demo shop")
    parser.add_argument("--pack", default="kirana", choices=["kirana", "cafe", "pharmacy", "salon"])
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--size", default="small", choices=["micro", "small", "medium"])
    parser.add_argument("--name", default=None)
    args = parser.parse_args()
    app = create_app(Settings())
    with TestClient(app) as client:
        state = app.state
        spec = WorldSpec(
            pack=args.pack,
            days=args.days,
            seed=args.seed,
            size=args.size,
            name=args.name,
            key=f"demo-{args.pack}-{args.seed}",
        )
        manifest = client.portal.call(WorldBuilder(state.sim, state.patrons, spec).build)  # type: ignore[union-attr]
        manifest["device_credential"] = state.staff.device_credential(
            manifest["merchant_id"], manifest["device_id"]
        )
        print(json.dumps(manifest, indent=2))
        print(
            "\nLog in: POST /v1/staff/login with device_credential, staff_id = owner_id, pin = 4826,"
            " channel device (Bearer dev-device) or console (Bearer dev-console)."
        )


if __name__ == "__main__":
    main()
