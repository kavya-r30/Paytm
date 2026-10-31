"""Narration templates (T4.13): every spoken or shown sentence is a template filled with tool numbers.

Languages: hi-Latn, hi, en fully; mr, ta, bn, gu, te fall back to hi-Latn text with locale-formatted numbers
until their catalogues are reviewed (I18N-5/6). Amounts are formatted by core.i18n (same as the UI).
"""

from typing import Any

from arth.core.i18n import format_money

T: dict[str, dict[str, str]] = {
    "today_sales": {
        "hi-Latn": "Aaj {money} aaya, {bills} bill.",
        "hi": "आज {money} आया, {bills} बिल।",
        "en": "Today {money} came in, {bills} bills.",
    },
    "khata_total": {
        "hi-Latn": "Kul khata baaki {money}, {accounts} grahak.",
        "hi": "कुल खाता बाकी {money}, {accounts} ग्राहक।",
        "en": "Total khata due {money}, {accounts} customers.",
    },
    "pending": {
        "hi-Latn": "{count} kaam aapki haan ka intezaar kar rahe hain.",
        "hi": "{count} काम आपकी हाँ का इंतज़ार कर रहे हैं।",
        "en": "{count} items are waiting for your yes.",
    },
    "forecast": {
        "hi-Latn": "Kal ki bikri sabse sambhav {money}, range {low} se {high}.",
        "hi": "कल की बिक्री सबसे संभव {money}, रेंज {low} से {high}।",
        "en": "Tomorrow's most likely sales {money}, range {low} to {high}.",
    },
    "forecast_unknown": {
        "hi-Latn": "Andaaze ke liye abhi data kam hai.",
        "hi": "अंदाज़े के लिए अभी डेटा कम है।",
        "en": "Not enough data for a forecast yet.",
    },
    "low_stock": {
        "hi-Latn": "{count} cheezein kam hain: {names}.",
        "hi": "{count} चीज़ें कम हैं: {names}।",
        "en": "{count} items are low: {names}.",
    },
    "item_stock": {
        "hi-Latn": "{name}: {qty} {unit} bacha hai.",
        "hi": "{name}: {qty} {unit} बचा है।",
        "en": "{name}: {qty} {unit} in stock.",
    },
    "item_price": {
        "hi-Latn": "{name} ka daam {money} ({unit}).",
        "hi": "{name} का दाम {money} ({unit})।",
        "en": "{name} sells at {money} ({unit}).",
    },
    "item_unknown": {
        "hi-Latn": '"{text}" naam ki cheez catalog mein nahi mili.',
        "hi": '"{text}" नाम की चीज़ कैटलॉग में नहीं मिली।',
        "en": 'No item called "{text}" in the catalog.',
    },
    "patron_khata": {
        "hi-Latn": "{name} ka khata {money} baaki hai.",
        "hi": "{name} का खाता {money} बाकी है।",
        "en": "{name} owes {money} on khata.",
    },
    "patron_unknown": {
        "hi-Latn": '"{text}" naam ka khata nahi mila. Poora naam boliye.',
        "hi": '"{text}" नाम का खाता नहीं मिला। पूरा नाम बोलिए।',
        "en": 'No khata found for "{text}". Please say the full name.',
    },
    "top_items": {
        "hi-Latn": "Is hafte sabse zyada: {names}.",
        "hi": "इस हफ्ते सबसे ज़्यादा: {names}।",
        "en": "Top this week: {names}.",
    },
    "added": {
        "hi-Latn": "{names} joda. Kul {money}.",
        "hi": "{names} जोड़ा। कुल {money}।",
        "en": "Added {names}. Total {money}.",
    },
    "removed": {
        "hi-Latn": "Hata diya. Kul {money}.",
        "hi": "हटा दिया। कुल {money}।",
        "en": "Removed. Total {money}.",
    },
    "gate": {
        "hi-Latn": "Ye aapki haan ke baad hoga.",
        "hi": "यह आपकी हाँ के बाद होगा।",
        "en": "This needs your yes.",
    },
    "done": {"hi-Latn": "Ho gaya.", "hi": "हो गया।", "en": "Done."},
    "nav": {"hi-Latn": "Khol diya.", "hi": "खोल दिया।", "en": "Opened."},
    "not_understood": {
        "hi-Latn": "Maaf kijiye, samjha nahi. Phir se boliye?",
        "hi": "माफ़ कीजिए, समझा नहीं।",
        "en": "Sorry, I didn't get that.",
    },
    "medical": {
        "hi-Latn": "Dawai ki salah doctor ya pharmacist hi denge. Main stock aur bill mein madad kar sakta hoon.",
        "hi": "दवाई की सलाह डॉक्टर या फार्मासिस्ट ही देंगे।",
        "en": "Please ask a doctor or pharmacist.",
    },
    "tax_advice": {
        "hi-Latn": "Main GST ke aankde dikha sakta hoon, filing ke liye CA se confirm karein.",
        "hi": "मैं GST के आंकड़े दिखा सकता हूँ, फाइलिंग के लिए CA से पुष्टि करें।",
        "en": "I can show GST figures; please confirm filing with your CA.",
    },
    "other": {
        "hi-Latn": "Main dukaan ke kaam mein madad karta hoon: bikri, khata, stock, orders.",
        "hi": "मैं दुकान के काम में मदद करता हूँ।",
        "en": "I help with the shop: sales, khata, stock, orders.",
    },
    "blocked": {
        "hi-Latn": "Ye message sirf draft bana sakta hai, main isse koi action nahi lunga.",
        "hi": "यह संदेश केवल ड्राफ्ट बना सकता है।",
        "en": "This message can only create a draft.",
    },
    "discreet": {"hi-Latn": "WhatsApp pe bhej diya.", "hi": "व्हाट्सऐप पर भेज दिया।", "en": "Sent to WhatsApp."},
}


def render(key: str, lang: str, **params: Any) -> str:
    table = T[key]
    template = table.get(lang) or table["hi-Latn"]
    ui = lang if lang in {"hi", "en", "hi-Latn", "mr", "ta", "bn", "gu", "te"} else "hi-Latn"
    filled = {k: format_money(v, ui) if k in {"money", "low", "high"} else v for k, v in params.items()}
    return template.format(**filled)
