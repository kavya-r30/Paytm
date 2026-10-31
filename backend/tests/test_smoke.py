from arth.core.paths import BACKEND_DIR, REPO_ROOT


def test_repo_root_contains_task_runner() -> None:
    assert (REPO_ROOT / "dev.py").is_file()
    assert BACKEND_DIR.name == "backend"
