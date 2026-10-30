"""Well-known repository paths.

Layout: backend/ holds the Python app plus config/, packs/, data/ and .env; contracts/ and design/
sit beside it at the repo root. Per-directory overrides live in Settings (ARTH_DATA_DIR,
ARTH_CONFIG_DIR, ARTH_PACKS_DIR).
"""

from __future__ import annotations

from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]
REPO_ROOT = BACKEND_DIR.parent
CONTRACTS_DIR = REPO_ROOT / "contracts"
CONFIG_DIR = BACKEND_DIR / "config"
PACKS_DIR = BACKEND_DIR / "packs"
DATA_DIR = BACKEND_DIR / "data"
DESIGN_DIR = REPO_ROOT / "design"
