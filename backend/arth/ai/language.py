"""Normaliser (T4.5) and TTS number words (T4.4): spoken Hindi/Hinglish/English numerals, units, money and
relative dates become exact integers; amounts are spoken as words, never digit by digit (AIQ-13/14).
"""

import re
from datetime import date, timedelta

UNITS_HI = {
    "ek": 1,
    "do": 2,
    "teen": 3,
    "char": 4,
    "chaar": 4,
    "paanch": 5,
    "panch": 5,
    "chhe": 6,
    "chhah": 6,
    "saat": 7,
    "aath": 8,
    "nau": 9,
    "das": 10,
    "gyarah": 11,
    "barah": 12,
    "pandrah": 15,
    "bees": 20,
    "pachees": 25,
    "tees": 30,
    "chalees": 40,
    "pachaas": 50,
    "pachas": 50,
    "saath": 60,
    "sattar": 70,
    "assi": 80,
    "nabbe": 90,
}
UNITS_EN = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "twelve": 12,
    "fifteen": 15,
    "twenty": 20,
    "thirty": 30,
    "fifty": 50,
}
UNITS_DEVA = {
    "एक": 1,
    "दो": 2,
    "तीन": 3,
    "चार": 4,
    "पांच": 5,
    "पाँच": 5,
    "छह": 6,
    "सात": 7,
    "आठ": 8,
    "नौ": 9,
    "दस": 10,
    "बीस": 20,
    "पचास": 50,
}
FRACTIONS = {
    "aadha": 500,
    "adha": 500,
    "आधा": 500,
    "pav": 250,
    "paav": 250,
    "sawa": 1250,
    "dedh": 1500,
    "डेढ़": 1500,
    "dhai": 2500,
    "ढाई": 2500,
    "half": 500,
}
MULTIPLIERS = {
    "sau": 100,
    "hundred": 100,
    "सौ": 100,
    "hazaar": 1000,
    "hazar": 1000,
    "thousand": 1000,
    "हज़ार": 1000,
    "हजार": 1000,
    "lakh": 100000,
    "लाख": 100000,
}
UNIT_WORDS = {
    "kilo": ("kg", 1000),
    "kg": ("kg", 1000),
    "किलो": ("kg", 1000),
    "gram": ("g", 1),
    "g": ("g", 1),
    "litre": ("l", 1000),
    "liter": ("l", 1000),
    "packet": ("pcs", 1000),
    "pkt": ("pcs", 1000),
    "piece": ("pcs", 1000),
    "dabba": ("pcs", 1000),
    "strip": ("strip", 1000),
    "cup": ("cup", 1000),
}
DAYS = {
    "somvar": 0,
    "mangalvar": 1,
    "budhvar": 2,
    "guruvar": 3,
    "shukravaar": 4,
    "shukravar": 4,
    "shanivar": 5,
    "ravivar": 6,
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def tokens(text: str) -> list[str]:
    return re.findall(r"₹?\d+(?:[.,]\d+)?|[\wऀ-ॿ]+", text.lower())


def number(words: list[str]) -> int | None:
    """Parse a spoken cardinal ('do hazaar paanch sau', 'teen', '₹500', 'dedh') into an integer."""
    total, current, seen = 0, 0, False
    for word in words:
        word = word.lstrip("₹").replace(",", "")
        if word.replace(".", "", 1).isdigit():
            current += int(float(word))
            seen = True
        elif word in UNITS_HI or word in UNITS_EN or word in UNITS_DEVA:
            current += UNITS_HI.get(word) or UNITS_EN.get(word) or UNITS_DEVA[word]
            seen = True
        elif word in MULTIPLIERS:
            current = (current or 1) * MULTIPLIERS[word]
            if MULTIPLIERS[word] >= 1000:
                total, current = total + current, 0
            seen = True
        else:
            break
    return total + current if seen else None


def quantity(text: str) -> tuple[int, str | None] | None:
    """'aadha kilo' → (500, 'kg'); '2 packet' → (2000, 'pcs'); 'teen' → (3000, None) in milli-units."""
    words = tokens(text)
    for i, word in enumerate(words):
        if word in FRACTIONS:
            unit = UNIT_WORDS.get(words[i + 1]) if i + 1 < len(words) else None
            return FRACTIONS[word], unit[0] if unit else None
        value = number(words[i:])
        if value is not None:
            rest = words[i + 1 :]
            unit = UNIT_WORDS.get(rest[0]) if rest else None  # the unit must follow the number directly
            if unit and unit[0] == "g":
                return value, "kg"  # grams as milli-kg
            return value * 1000, unit[0] if unit else None
    return None


def money(text: str) -> int | None:
    """'₹30 ka', '500 rupaye', 'paanch sau' → paise."""
    match = re.search(r"₹\s?(\d+(?:\.\d{1,2})?)", text)
    if match:
        return round(float(match.group(1)) * 100)
    words = tokens(text)
    for i in range(len(words)):
        value = number(words[i:])
        if value is not None:
            return value * 100
    return None


def relative_date(text: str, today: date) -> date | None:
    lowered = text.lower()
    if "parso" in lowered:
        return today + timedelta(days=2)
    if "kal" in lowered or "tomorrow" in lowered:
        return today + timedelta(days=1)
    if "agle hafte" in lowered or "next week" in lowered:
        return today + timedelta(days=7)
    for word, weekday in DAYS.items():
        if word in lowered:
            return today + timedelta(days=(weekday - today.weekday()) % 7 or 7)
    return None


HI_WORDS = [
    "",
    "ek",
    "do",
    "teen",
    "chaar",
    "paanch",
    "chhah",
    "saat",
    "aath",
    "nau",
    "das",
    "gyaarah",
    "baarah",
    "terah",
    "chaudah",
    "pandrah",
    "solah",
    "satrah",
    "athaarah",
    "unnees",
    "bees",
    "ikkees",
    "baaees",
    "teyees",
    "chaubees",
    "pachchees",
    "chhabbees",
    "sattaees",
    "atthaees",
    "untees",
    "tees",
    "ikattees",
    "battees",
    "taintees",
    "chauntees",
    "paintees",
    "chhattees",
    "saintees",
    "adtees",
    "untaalees",
    "chaalees",
    "iktaalees",
    "bayaalees",
    "taintaalees",
    "chavaalees",
    "paintaalees",
    "chhiyaalees",
    "saintaalees",
    "adtaalees",
    "unchaas",
    "pachaas",
    "ikyaavan",
    "baavan",
    "tirpan",
    "chauvan",
    "pachpan",
    "chhappan",
    "sattaavan",
    "atthaavan",
    "unsath",
    "saath",
    "iksath",
    "baasath",
    "tirsath",
    "chausath",
    "painsath",
    "chhiyaasath",
    "sadsath",
    "adsath",
    "unhattar",
    "sattar",
    "ikhattar",
    "bahattar",
    "tihattar",
    "chauhattar",
    "pachhattar",
    "chhihattar",
    "sathattar",
    "athattar",
    "unaasi",
    "assi",
    "ikyaasi",
    "bayaasi",
    "tiraasi",
    "chauraasi",
    "pachaasi",
    "chhiyaasi",
    "sataasi",
    "athaasi",
    "navaasi",
    "nabbe",
    "ikyaanve",
    "baanve",
    "tiraanve",
    "chauraanve",
    "pachaanve",
    "chhiyaanve",
    "sattaanve",
    "attaanve",
    "ninyaanve",
]
EN_SMALL = [
    "",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
EN_TENS = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]


def _en_under_100(n: int) -> str:
    return EN_SMALL[n] if n < 20 else EN_TENS[n // 10] + ("-" + EN_SMALL[n % 10] if n % 10 else "")


def words(n: int, lang: str = "hi") -> str:
    """Indian-system number words (lakh/crore). hi and hi-Latn share the romanised Hindi table."""
    if n == 0:
        return "shunya" if lang.startswith("hi") else "zero"
    parts = []
    for size, hi_name, en_name in (
        (10**7, "crore", "crore"),
        (10**5, "lakh", "lakh"),
        (1000, "hazaar", "thousand"),
        (100, "sau", "hundred"),
    ):
        if n >= size:
            count, n = divmod(n, size)
            spoken = (
                words(count, lang)
                if count >= 100
                else (HI_WORDS[count] if lang.startswith("hi") else _en_under_100(count))
            )
            parts.append(f"{spoken} {hi_name if lang.startswith('hi') else en_name}")
    if n:
        parts.append(HI_WORDS[n] if lang.startswith("hi") else _en_under_100(n))
    return " ".join(parts)


def speak_money(paise: int, lang: str = "hi") -> str:
    rupees, rest = divmod(paise, 100)
    text = f"{words(rupees, lang)} {'rupaye' if lang.startswith('hi') else 'rupees'}"
    if rest:
        text += f" {words(rest, lang)} {'paise' if lang.startswith('hi') else 'paise'}"
    return text


def normalise_for_tts(text: str, lang: str = "hi") -> str:
    """Replace ₹ amounts and bare integers with words so TTS never reads digits one by one."""

    def amount(match: re.Match[str]) -> str:
        value = match.group(1).replace(",", "")
        rupees, _, paise = value.partition(".")
        return speak_money(int(rupees) * 100 + int((paise + "00")[:2] if paise else 0), lang)

    text = re.sub(r"₹\s?([\d,]+(?:\.\d{1,2})?)", amount, text)
    return re.sub(r"\b\d+\b", lambda m: words(int(m.group(0)), lang), text)
