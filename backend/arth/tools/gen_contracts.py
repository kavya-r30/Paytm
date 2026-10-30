"""Generate Pydantic v2 models from the contracts JSON Schemas.

Run: python dev.py gen          (or: cd backend && uv run python -m arth.tools.gen_contracts)
     python dev.py gen-check    (--check: exit 1 if the committed models differ from a fresh run)

Every contract (see arth.core.schemas) becomes `arth/contracts/<name>.py` with a class named by the
schema's `title`. The schemas are staged flat as `<name>.json`, with cross-file `$ref`s rewritten to
those names, and generated in one datamodel-codegen run: shared definitions are emitted once in
`common.py` and imported by the other modules instead of being copied into each of them.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from arth.core.paths import BACKEND_DIR, CONTRACTS_DIR
from arth.core.schemas import ContractError, discover_schemas, load_schemas

OUT = BACKEND_DIR / "arth" / "contracts"
HEADER = "# Generated from contracts. Do not edit; run `python dev.py gen`."
STALE = "contracts are stale: run `python dev.py gen`"
CODEGEN = [sys.executable, "-m", "datamodel_code_generator"]
OPTIONS = [
    "--input-file-type",
    "jsonschema",
    "--output-model-type",
    "pydantic_v2.BaseModel",
    "--target-python-version",
    "3.12",
    "--use-standard-collections",
    "--use-union-operator",
    "--use-title-as-name",
    "--collapse-root-models",
    "--disable-timestamp",
    "--formatters",
    "black",
    "isort",
    "--custom-file-header",
    HEADER,
]


class GenError(RuntimeError):
    """Code generation failed; the message names the contracts involved."""


def _rewrite_refs(node: Any, source: Path, names: dict[Path, str]) -> Any:
    if isinstance(node, dict):
        out = {k: _rewrite_refs(v, source, names) for k, v in node.items()}
        ref = node.get("$ref")
        if isinstance(ref, str) and not ref.startswith("#"):
            file_part, _, fragment = ref.partition("#")
            target = (source.parent / file_part).resolve()
            if target not in names:
                raise GenError(f"{source.name}: $ref {ref!r} points at {file_part}, which is not a contract")
            out["$ref"] = f"{names[target]}.json#{fragment}"
        return out
    if isinstance(node, list):
        return [_rewrite_refs(v, source, names) for v in node]
    return node


def stage(contracts: Path, dest: Path) -> list[str]:
    """Copy every contract to dest/<name>.json with cross-file refs rewritten; return the names."""
    try:
        paths = discover_schemas(contracts)
        schemas = load_schemas(contracts)
    except ContractError as exc:
        raise GenError(str(exc)) from exc
    names = {path.resolve(): name for name, path in paths.items()}
    dest.mkdir(parents=True, exist_ok=True)
    for name, path in paths.items():
        staged = _rewrite_refs(schemas[name], path.resolve(), names)
        staged.pop("$id", None)  # resolve refs by staged file name, never by URL
        (dest / f"{name}.json").write_text(json.dumps(staged, ensure_ascii=False, indent=2), encoding="utf-8")
    return list(paths)


def _check_titles(generated: dict[str, bytes], titles: dict[str, str]) -> None:
    for name, title in titles.items():
        source = generated.get(f"{name}.py", b"").decode("utf-8")
        if not re.search(rf"^class {re.escape(title)}\(", source, re.MULTILINE):
            raise GenError(f"{name}: generated module has no class {title!r} (the schema title)")


def render(contracts: Path = CONTRACTS_DIR) -> dict[str, bytes]:
    """Generate every model in a temporary directory; return {file name: LF-normalised bytes}."""
    with tempfile.TemporaryDirectory(prefix="arth-gen-") as tmp:
        staged, out = Path(tmp) / "schemas", Path(tmp) / "models"
        names = stage(contracts, staged)
        argv = [*CODEGEN, "--input", str(staged), "--output", str(out), *OPTIONS]
        result = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if result.returncode:
            raise GenError(
                f"datamodel-codegen failed for contracts {', '.join(names)} "
                f"(exit {result.returncode}):\n{result.stderr.strip() or result.stdout.strip()}"
            )
        generated = {
            p.name: p.read_bytes().replace(b"\r\n", b"\n")
            for p in sorted(out.glob("*.py"))
            if p.name != "__init__.py"
        }
    generated["__init__.py"] = (HEADER + "\n").encode("utf-8")
    _check_titles(generated, {name: s["title"] for name, s in load_schemas(contracts).items()})
    return dict(sorted(generated.items()))


def stale(expected: dict[str, bytes], out: Path) -> list[str]:
    """Files in out that differ from, are missing from, or are not in expected (sorted)."""
    present = {p.name for p in out.glob("*.py")}
    changed = [n for n in expected if n not in present or (out / n).read_bytes() != expected[n]]
    return sorted(changed + sorted(present - set(expected)))


def write(expected: dict[str, bytes], out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, data in expected.items():
        (out / name).write_bytes(data)
        print(f"generated arth/contracts/{name}")
    for path in out.glob("*.py"):
        if path.name not in expected:
            path.unlink()
            print(f"removed stale arth/contracts/{path.name}")


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    try:
        expected = render()
    except GenError as exc:
        print(f"gen_contracts: {exc}", file=sys.stderr)
        return 1
    if "--check" in args:
        files = stale(expected, OUT)
        if files:
            print(f"{STALE}\n" + "\n".join(f"  backend/arth/contracts/{f}" for f in files), file=sys.stderr)
            return 1
        print(f"contracts: {len(expected)} Python files are up to date")
        return 0
    write(expected, OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
