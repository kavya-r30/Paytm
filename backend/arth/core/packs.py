"""Vertical packs (spec Part D). The core never branches on vertical; it asks this registry.

A pack can only TIGHTEN core policies. A pack that loosens one fails at boot.
"""

from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Literal, NamedTuple

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from arth.core.config import Policies


class PackPolicyError(ValueError):
    """Any invalid pack (bad manifest, YAML, or a policy that loosens/is malformed)."""


class UnknownPack(KeyError):
    """No pack with that name is installed."""


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CatalogSpec(_Strict):
    schema_: Literal["sku", "menu", "medicine", "service"] = Field(alias="schema")
    fields: list[str]
    units: list[str]
    loose_sale: bool = False
    starter_catalog: str | None = None


class StockSpec(_Strict):
    batches: Literal["required", "optional", "off"]
    expiry: Literal["required", "optional", "off"]
    bom: bool = False


class CounterSpec(_Strict):
    modes: list[str]
    tickets: bool = False
    appointments: bool = False


class KhataSpec(_Strict):
    enabled: bool


class PackManifest(_Strict):
    pack: str
    version: int
    names: dict[str, str]
    catalog: CatalogSpec
    stock: StockSpec
    counter: CounterSpec
    khata: KhataSpec
    levers: dict[str, dict[str, Any]]
    calendar: list[str]
    charts: list[int]
    policies: dict[str, Any] = Field(default_factory=dict)
    templates: str
    generator: str
    peer_cohort: str
    scenarios: list[str]


class Rule(NamedTuple):
    path: tuple[str, ...]  # location inside Policies
    kind: Literal["floor", "cap"]  # floor: pack value must be >= core; cap: must be <= core


_SCALAR_RULES: dict[str, Rule] = {
    # Higher margin floor = fewer thin-margin offers.
    "margin_floor": Rule(("growth", "margin_floor"), "floor"),
    # Larger holdout share = more control group, i.e. more measurement and less exposure.
    "holdout_share": Rule(("growth", "holdout_share"), "floor"),
    # Lower contact cap = fewer marketing messages per patron.
    "marketing_per_patron_per_week": Rule(("contact_caps", "marketing_per_patron_per_week"), "cap"),
    # Higher expiry window = earlier alerts before stock expires.
    "expiry_alert_days": Rule(("expiry_alert_days", "default"), "floor"),
}
_LIST_ADD_ONLY = {"forbid_offers_on_flags"}


def _get(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    node: Any = data
    for key in path:
        node = node[key]
    return node


def _set(data: dict[str, Any], path: tuple[str, ...], value: Any) -> None:
    node: Any = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value


def merge_policies(core: Policies, manifest: PackManifest) -> Policies:
    name = manifest.pack
    merged = core.model_dump()
    for key, value in manifest.policies.items():
        if key in _SCALAR_RULES:
            rule = _SCALAR_RULES[key]
            if not (isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)):
                raise PackPolicyError(f"pack {name!r}: {key} must be a number, got {value!r}")
            current = _get(merged, rule.path)
            loosens = value < current if rule.kind == "floor" else value > current
            if loosens:
                raise PackPolicyError(
                    f"pack {name!r} loosens {key}: {value} vs core {current} "
                    f"(packs may only tighten policies)"
                )
            _set(merged, rule.path, value)
        elif key in _LIST_ADD_ONLY:
            if not (isinstance(value, list) and all(isinstance(v, str) and v for v in value)):
                raise PackPolicyError(
                    f"pack {name!r}: {key} must be a list of non-empty strings, got {value!r}"
                )
            merged[key] = sorted(set(merged[key]) | set(value))
        else:
            raise PackPolicyError(f"pack {name!r} sets unknown policy key {key!r}")
    try:
        return Policies.model_validate(merged)
    except ValidationError as exc:
        raise PackPolicyError(f"pack {name!r}: merged policies invalid: {exc}") from exc


class PackRegistry:
    def __init__(self, manifests: dict[str, PackManifest], policies: dict[str, Policies]) -> None:
        self._manifests = manifests
        self._policies = policies

    @classmethod
    def load(cls, packs_dir: Path, core: Policies) -> PackRegistry:
        manifests: dict[str, PackManifest] = {}
        policies: dict[str, Policies] = {}
        for path in sorted(packs_dir.glob("*/manifest.yaml")):
            try:
                manifest = PackManifest.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
            except yaml.YAMLError as exc:
                raise PackPolicyError(f"{path.parent.name}/manifest.yaml: invalid YAML: {exc}") from exc
            except ValidationError as exc:
                raise PackPolicyError(f"{path.parent.name}/manifest.yaml: {exc}") from exc
            if manifest.pack != path.parent.name:
                raise PackPolicyError(f"{path}: 'pack: {manifest.pack}' must match its folder name")
            manifests[manifest.pack] = manifest
            policies[manifest.pack] = merge_policies(core, manifest)
        return cls(manifests, policies)

    @property
    def names(self) -> list[str]:
        return sorted(self._manifests)

    def get(self, pack: str) -> PackManifest:
        try:
            return self._manifests[pack]
        except KeyError:
            raise UnknownPack(pack) from None

    def lever(self, pack: str, name: str) -> dict[str, Any] | None:
        return self.get(pack).levers.get(name)

    def policies_for(self, pack: str) -> Policies:
        self.get(pack)
        return self._policies[pack]
