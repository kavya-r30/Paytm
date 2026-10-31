// Message catalogues (spec I6): ICU MessageFormat, a per-locale fallback chain and the xx-LONG pseudo-locale.
// Pure module (no React) so it is testable in node and usable from server components.
import { IntlMessageFormat } from 'intl-messageformat';
import { INTL_LOCALE, LOCALES, formatMoney, type Locale } from '../format';
import en from '../../i18n/en.json';
import hi from '../../i18n/hi.json';
import hiLatn from '../../i18n/hi-Latn.json';
import mr from '../../i18n/mr.json';
import ta from '../../i18n/ta.json';
import bn from '../../i18n/bn.json';
import gu from '../../i18n/gu.json';
import te from '../../i18n/te.json';

export const PSEUDO = 'xx-LONG' as const;
export type UiLocale = Locale | typeof PSEUDO;
export const UI_LOCALES: readonly UiLocale[] = [...LOCALES, PSEUDO];

type Catalogue = Record<string, string>;
export const CATALOGUES: Readonly<Record<Locale, Catalogue>> = {
  en,
  hi,
  'hi-Latn': hiLatn,
  mr,
  ta,
  bn,
  gu,
  te,
};

/** Where a missing key is looked up next. Marathi reads Hindi before English; Hinglish is the demo default. */
export const FALLBACK: Readonly<Record<Locale, readonly Locale[]>> = {
  en: [],
  'hi-Latn': ['en'],
  hi: ['hi-Latn', 'en'],
  mr: ['hi', 'en'],
  ta: ['en'],
  bn: ['en'],
  gu: ['en'],
  te: ['en'],
};

/** Native names for the language picker and the rail pill. */
export const NATIVE_NAME: Readonly<Record<UiLocale, string>> = {
  hi: 'हिंदी',
  en: 'English',
  'hi-Latn': 'Hinglish',
  mr: 'मराठी',
  ta: 'தமிழ்',
  bn: 'বাংলা',
  gu: 'ગુજરાતી',
  te: 'తెలుగు',
  'xx-LONG': 'Ƥšéûðö',
};
export const SHORT_NAME: Readonly<Record<UiLocale, string>> = {
  hi: 'हि',
  en: 'En',
  'hi-Latn': 'Hi',
  mr: 'म',
  ta: 'த',
  bn: 'বা',
  gu: 'ગુ',
  te: 'తె',
  'xx-LONG': 'Xx',
};

/** Noto family for each script; Inter covers Latin. Loaded only for the active locale (I3). */
export const SCRIPT_FONT: Readonly<Partial<Record<UiLocale, string>>> = {
  hi: 'Noto Sans Devanagari',
  mr: 'Noto Sans Devanagari',
  ta: 'Noto Sans Tamil',
  bn: 'Noto Sans Bengali',
  gu: 'Noto Sans Gujarati',
  te: 'Noto Sans Telugu',
};

export function isUiLocale(x: string): x is UiLocale {
  return (UI_LOCALES as readonly string[]).includes(x);
}

/** The data locale behind a UI locale: the pseudo-locale formats numbers as English. */
export function dataLocale(locale: UiLocale): Locale {
  return locale === PSEUDO ? 'en' : locale;
}

const ACCENTS: Record<string, string> = {
  a: 'à',
  e: 'é',
  i: 'î',
  o: 'ö',
  u: 'û',
  c: 'ç',
  n: 'ñ',
  s: 'š',
  y: 'ý',
  A: 'Å',
  E: 'É',
  I: 'Î',
  O: 'Ö',
  U: 'Ü',
  S: 'Š',
};

/** +40% length and accented, leaving ICU placeholders untouched, to catch overflow (I6). */
export function pseudoize(text: string): string {
  let depth = 0;
  let out = '';
  for (const ch of text) {
    if (ch === '{') depth += 1;
    if (ch === '}') depth -= 1;
    out += depth === 0 && ch !== '}' ? (ACCENTS[ch] ?? ch) : ch;
  }
  const pad = '~'.repeat(Math.ceil(text.length * 0.4));
  return `[${out}${pad}]`;
}

export function lookup(locale: UiLocale, key: string): string | undefined {
  if (locale === PSEUDO) {
    const base = CATALOGUES.en[key];
    return base === undefined ? undefined : pseudoize(base);
  }
  const chain = [locale, ...FALLBACK[locale]];
  for (const l of chain) {
    const hit = CATALOGUES[l][key];
    if (hit !== undefined) return hit;
  }
  return undefined;
}

export type Params = Record<string, string | number | boolean | null | undefined>;
const compiled = new Map<string, IntlMessageFormat>();

/** Translate a key. Unknown keys render as the key itself so gaps are visible, never blank. */
export function translate(locale: UiLocale, key: string, params?: Params): string {
  const source = lookup(locale, key);
  if (source === undefined) return key;
  if (!params && !source.includes('{')) return source;
  const cacheKey = `${locale}\u0000${key}`;
  let fmt = compiled.get(cacheKey);
  if (!fmt) {
    fmt = new IntlMessageFormat(source, INTL_LOCALE[dataLocale(locale)], undefined, { ignoreTag: true });
    compiled.set(cacheKey, fmt);
  }
  const clean: Record<string, string | number | boolean> = {};
  for (const [k, v] of Object.entries(params ?? {})) clean[k] = v ?? '';
  try {
    return String(fmt.format(clean));
  } catch {
    // a placeholder without a value (e.g. a gate scope with no patron) renders blank, never crashes a screen
    return source
      .replace(/\{[^}]*\}/g, (m) => String(clean[m.slice(1, -1).split(',')[0]!.trim()] ?? ''))
      .trim();
  }
}

/** Money in the active locale; compact ("₹1.1 lakh") where a slot is tight (I6). */
export function money(locale: UiLocale, paise: number, compact = false): string {
  return formatMoney(paise, dataLocale(locale), { compact });
}

/** Quantity from milli-units: 500 → "0.5", 2000 → "2". */
export function qty(milli: number): string {
  const whole = milli / 1000;
  return Number.isInteger(whole) ? String(whole) : whole.toFixed(3).replace(/0+$/, '');
}

const timeFormats = new Map<string, Intl.DateTimeFormat>();
function fmt(locale: UiLocale, opts: Intl.DateTimeFormatOptions, tag: string): Intl.DateTimeFormat {
  const key = `${locale}:${tag}`;
  let f = timeFormats.get(key);
  if (!f) {
    f = new Intl.DateTimeFormat(INTL_LOCALE[dataLocale(locale)], {
      timeZone: 'Asia/Kolkata',
      numberingSystem: 'latn',
      ...opts,
    });
    timeFormats.set(key, f);
  }
  return f;
}

export function time(locale: UiLocale, iso: string): string {
  return fmt(locale, { hour: 'numeric', minute: '2-digit' }, 't').format(new Date(iso));
}

export function day(locale: UiLocale, iso: string): string {
  return fmt(locale, { weekday: 'short', day: 'numeric', month: 'short' }, 'd').format(new Date(iso));
}

export function shortDate(locale: UiLocale, iso: string): string {
  return fmt(locale, { day: 'numeric', month: 'short' }, 's').format(new Date(iso));
}

/** Text fit (I6): the font size that fits `textWidth` (measured at `max`) into `boxWidth`, clamped to `min`. */
export function fitSize(textWidth: number, boxWidth: number, max: number, min: number): number {
  if (textWidth <= 0 || boxWidth <= 0 || textWidth <= boxWidth) return max;
  return Math.max(min, Math.floor((max * boxWidth) / textWidth));
}

/** Initials for an avatar: "Priya Verma" → "PV". */
export function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  return parts
    .slice(0, 2)
    .map((p) => p[0]!.toUpperCase())
    .join('');
}
