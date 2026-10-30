import json
import re

from arth.core.paths import CONTRACTS_DIR, DESIGN_DIR

C2_TO_TOKEN = {
    "MID": "midnight",
    "CYAN": "paytm-blue",
    "SKY": "sky",
    "GROUND": "ground",
    "LINE": "line",
    "INK": "ink",
    "INK2": "ink-2",
    "INK3": "ink-3",
    "CYT": "cyan-text",
    "RED": "red",
    "REDT": "red-tint",
    "GRN": "green",
    "GRNF": "green-fill",
    "GRNT": "green-tint",
    "AMB": "amber",
    "AMBT": "amber-text",
    "AMBTINT": "amber-tint",
}


def c2_constants() -> dict[str, str]:
    text = (DESIGN_DIR / "generator" / "c2.py").read_text(encoding="utf-8")
    return dict(re.findall(r"\b([A-Z][A-Z0-9]*) = '([^']*)'", text))


def tokens() -> dict:
    return json.loads((CONTRACTS_DIR / "tokens.json").read_text(encoding="utf-8"))


def test_colours_match_design_source() -> None:
    consts, colour = c2_constants(), tokens()["color"]
    for c2_name, token in C2_TO_TOKEN.items():
        assert colour[token].upper() == consts[c2_name].upper(), token


def test_shadows_match_design_source() -> None:
    consts, shadow = c2_constants(), tokens()["shadow"]
    assert shadow["1"] == consts["SH"]
    assert shadow["2"] == consts["SH2"]


def test_device_canvas_is_4_by_3() -> None:
    device = tokens()["device"]
    assert (device["width"], device["height"]) == (960, 720)
    assert device["width"] * 3 == device["height"] * 4
