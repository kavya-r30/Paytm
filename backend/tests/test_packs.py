from pathlib import Path

import pytest

from arth.core.config import load_policies
from arth.core.packs import PackPolicyError, PackRegistry, UnknownPack, merge_policies
from arth.core.paths import CONFIG_DIR, PACKS_DIR

POLICIES = load_policies(CONFIG_DIR / "policies.yaml")
KIRANA = (PACKS_DIR / "kirana" / "manifest.yaml").read_text(encoding="utf-8")


def make_pack(root: Path, name: str, policies_line: str) -> None:
    folder = root / name
    folder.mkdir(parents=True)
    text = KIRANA.replace("pack: kirana", f"pack: {name}").replace(
        "policies: { margin_floor: 0.15 }", policies_line
    )
    (folder / "manifest.yaml").write_text(text, encoding="utf-8")


def test_repo_packs_load_and_expose_levers() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    kirana = registry.get("kirana")
    assert kirana.catalog.schema_ == "sku"
    assert registry.lever("kirana", "replenish") == {
        "categories": ["atta", "rice", "oil", "sugar", "dal", "milk", "tea", "detergent"],
        "cv_max": 0.4,
    }
    assert registry.lever("kirana", "slot_fill") is None


def test_unknown_pack_raises() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    with pytest.raises(UnknownPack):
        registry.get("bakery")


def test_tightening_is_merged() -> None:
    registry = PackRegistry.load(PACKS_DIR, POLICIES)
    tighter = registry.get("kirana").model_copy(update={"policies": {"margin_floor": 0.25}})
    merged = merge_policies(POLICIES, tighter)
    assert merged.growth.margin_floor == 0.25
    assert POLICIES.growth.margin_floor == 0.15, "core policies must not be mutated"


def test_loosening_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "loose", "policies: { margin_floor: 0.10 }")
    with pytest.raises(PackPolicyError, match="margin_floor"):
        PackRegistry.load(tmp_path, POLICIES)


def test_raising_contact_cap_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "spammy", "policies: { marketing_per_patron_per_week: 3 }")
    with pytest.raises(PackPolicyError, match="marketing_per_patron_per_week"):
        PackRegistry.load(tmp_path, POLICIES)


def test_unknown_policy_key_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "odd", "policies: { allow_r4_by_voice: true }")
    with pytest.raises(PackPolicyError, match="allow_r4_by_voice"):
        PackRegistry.load(tmp_path, POLICIES)


def test_forbid_offers_flags_are_added(tmp_path: Path) -> None:
    make_pack(tmp_path, "chemist", "policies: { forbid_offers_on_flags: [rx_required] }")
    registry = PackRegistry.load(tmp_path, POLICIES)
    assert registry.policies_for("chemist").forbid_offers_on_flags == ["rx_required"]


def test_merged_policies_out_of_bounds_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "wild", "policies: { margin_floor: 5 }")
    with pytest.raises(PackPolicyError, match=r"wild.*merged policies invalid"):
        PackRegistry.load(tmp_path, POLICIES)


@pytest.mark.parametrize("bad", ["abc", "true", ".nan", ".inf"])
def test_non_numeric_scalar_fails_boot(tmp_path: Path, bad: str) -> None:
    make_pack(tmp_path, "junk", f"policies: {{ margin_floor: {bad} }}")
    with pytest.raises(PackPolicyError, match=r"junk.*margin_floor must be a number"):
        PackRegistry.load(tmp_path, POLICIES)


@pytest.mark.parametrize("bad", ["rx_required", "[1, 2]", "['']", "{a: b}"])
def test_forbid_offers_must_be_list_of_strings(tmp_path: Path, bad: str) -> None:
    make_pack(tmp_path, "badlist", f"policies: {{ forbid_offers_on_flags: {bad} }}")
    with pytest.raises(PackPolicyError, match=r"badlist.*forbid_offers_on_flags"):
        PackRegistry.load(tmp_path, POLICIES)


def test_malformed_yaml_fails_boot(tmp_path: Path) -> None:
    folder = tmp_path / "broken"
    folder.mkdir()
    (folder / "manifest.yaml").write_text("pack: [unclosed\n  : :", encoding="utf-8")
    with pytest.raises(PackPolicyError, match=r"broken.*manifest.yaml"):
        PackRegistry.load(tmp_path, POLICIES)


def test_folder_name_must_match_pack(tmp_path: Path) -> None:
    make_pack(tmp_path, "alpha", "policies: { margin_floor: 0.2 }")
    (tmp_path / "alpha").rename(tmp_path / "beta")
    with pytest.raises(PackPolicyError, match="must match its folder name"):
        PackRegistry.load(tmp_path, POLICIES)


def test_schema_violation_fails_boot(tmp_path: Path) -> None:
    make_pack(tmp_path, "extra", "policies: { margin_floor: 0.2 }\nsurprise: 1")
    with pytest.raises(PackPolicyError, match=r"extra/manifest.yaml"):
        PackRegistry.load(tmp_path, POLICIES)


def test_expiry_alert_days_is_a_floor(tmp_path: Path) -> None:
    core = POLICIES.expiry_alert_days["default"]
    make_pack(tmp_path / "low", "low", f"policies: {{ expiry_alert_days: {core - 1} }}")
    with pytest.raises(PackPolicyError, match="expiry_alert_days"):
        PackRegistry.load(tmp_path / "low", POLICIES)
    make_pack(tmp_path / "high", "high", f"policies: {{ expiry_alert_days: {core + 5} }}")
    registry = PackRegistry.load(tmp_path / "high", POLICIES)
    assert registry.policies_for("high").expiry_alert_days["default"] == core + 5
