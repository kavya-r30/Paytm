import json
import sys
from pathlib import Path

import pytest

from arth.tools import gen_contracts as gen


def _schema(root: Path, rel: str, body: dict[str, object]) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = {"$id": f"https://arth.local/contracts/{rel}", "title": Path(rel).name.split(".")[0].title()} | body
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_stage_flattens_files_and_rewrites_cross_file_refs(tmp_path: Path) -> None:
    src, stage = tmp_path / "contracts", tmp_path / "stage"
    _schema(src, "common.schema.json", {"definitions": {"X": {"type": "string"}}})
    ref = {"$ref": "../common.schema.json#/definitions/X"}
    _schema(src, "events/ev.schema.json", {"properties": {"x": ref}})
    gen.stage(src, stage)
    assert sorted(p.name for p in stage.iterdir()) == ["common.json", "ev.json"]
    staged = json.loads((stage / "ev.json").read_text(encoding="utf-8"))
    assert staged["properties"]["x"]["$ref"] == "common.json#/definitions/X"


def test_stage_rejects_refs_to_files_that_are_not_contracts(tmp_path: Path) -> None:
    src = tmp_path / "contracts"
    _schema(src, "a.schema.json", {"properties": {"x": {"$ref": "nowhere.schema.json#/definitions/X"}}})
    with pytest.raises(gen.GenError, match=r"a\.schema\.json.*nowhere\.schema\.json"):
        gen.stage(src, tmp_path / "stage")


def test_stale_lists_changed_missing_and_extra_files(tmp_path: Path) -> None:
    (tmp_path / "same.py").write_bytes(b"x\n")
    (tmp_path / "changed.py").write_bytes(b"old\n")
    (tmp_path / "extra.py").write_bytes(b"gone\n")
    expected = {"same.py": b"x\n", "changed.py": b"new\n", "missing.py": b"m\n"}
    assert gen.stale(expected, tmp_path) == ["changed.py", "extra.py", "missing.py"]


def test_codegen_failure_names_the_contracts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(gen, "CODEGEN", [sys.executable, "-c", "import sys; sys.exit('boom')"])
    expected = r"(?s)datamodel-codegen failed for contracts .*\bcommon\b.*\benvelope\b.*boom"
    with pytest.raises(gen.GenError, match=expected):
        gen.render()


def test_check_mode_reports_stale_files(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "leftover.py").write_bytes(b"# old\n")
    monkeypatch.setattr(gen, "OUT", tmp_path)
    monkeypatch.setattr(gen, "render", lambda: {"__init__.py": b"# h\n", "thing.py": b"# h\nx = 1\n"})
    assert gen.main(["--check"]) == 1
    assert (tmp_path / "leftover.py").exists(), "--check must never write or delete"
    assert gen.main([]) == 0
    assert not (tmp_path / "leftover.py").exists(), "gen removes modules that no longer match a contract"
    assert gen.main(["--check"]) == 0


def test_committed_models_are_fresh() -> None:
    assert gen.stale(gen.render(), gen.OUT) == [], "contracts are stale: run `python dev.py gen`"
