"""Screenshot forge (T2.5): genuine and edited "payment successful" screenshots for Sentinel tests.

Images are SVG (no image dependencies). The returned fields are what perception (L4) would extract;
`phash` and `ela_score_bp` stand in for the image-forensics signals Sentinel lists but never decides on.
"""

import hashlib
from html import escape
from typing import Any


def screenshot(
    amount_paise: int, utr: str, payee: str, paid_at: str, *, edited: bool = False, edit: str = "amount"
) -> dict[str, Any]:
    shown_amount, shown_utr = amount_paise, utr
    if edited and edit == "amount":
        shown_amount = amount_paise * 10
    if edited and edit == "utr":
        shown_utr = utr[:-4] + "0000"
    rupees = f"₹{shown_amount // 100:,}.{shown_amount % 100:02d}"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="360" height="640" viewBox="0 0 360 640">'
        '<rect width="360" height="640" fill="#f4f7fb"/><circle cx="180" cy="150" r="48" fill="#1fa463"/>'
        '<text x="180" y="165" font-size="48" text-anchor="middle" fill="#fff">✓</text>'
        f'<text x="180" y="250" font-size="20" text-anchor="middle">Payment successful</text>'
        f'<text x="180" y="300" font-size="34" text-anchor="middle" font-weight="700">{escape(rupees)}</text>'
        f'<text x="180" y="350" font-size="14" text-anchor="middle">To {escape(payee)}</text>'
        f'<text x="180" y="380" font-size="13" text-anchor="middle">UTR {escape(shown_utr)}</text>'
        f'<text x="180" y="405" font-size="13" text-anchor="middle">{escape(paid_at)}</text></svg>'
    )
    base = hashlib.sha256(f"{amount_paise}|{utr}|{payee}".encode()).hexdigest()[:16]
    return {
        "svg": svg,
        "fields": {"amount_paise": shown_amount, "utr": shown_utr, "paid_at": paid_at},
        "phash": base,
        "ela_score_bp": 8200 if edited else 900,
        "edited": edited,
    }
