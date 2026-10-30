from pathlib import Path

import yaml

from arth.core.config import Settings
from arth.core.paths import CONTRACTS_DIR
from arth.main import create_app

HTTP_METHODS = {"get", "post", "put", "patch", "delete"}


def operations(paths: dict[str, dict[str, object]]) -> set[tuple[str, str]]:
    return {(method.upper(), path) for path, ops in paths.items() for method in ops if method in HTTP_METHODS}


def test_served_routes_equal_documented_routes(tmp_path: Path) -> None:
    # FastAPI >= 0.16x nests included routers instead of flattening app.routes, so read the served
    # operations from FastAPI's own generated OpenAPI document (excludes /docs, /redoc, /openapi.json).
    documented = operations(
        yaml.safe_load((CONTRACTS_DIR / "openapi.yaml").read_text(encoding="utf-8"))["paths"]
    )
    served = operations(
        create_app(Settings(_env_file=None, mode="test", data_dir=tmp_path)).openapi()["paths"]
    )
    assert served == documented, f"undocumented: {served - documented}; unserved: {documented - served}"
