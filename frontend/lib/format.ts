// Keep in lockstep with backend/arth/core/i18n.py via contracts/fixtures/format_cases.json.
// Contract: money is byte-identical on both sides. Dates are rendered by whichever side shows them
// (frontend for screens, backend for messages/PDFs) and are only required to be byte-identical for
// `en` and `hi-Latn`: Node ICU and Babel ship different CLDR versions, so non-Latin month/weekday
// names may differ. Other locales are tested per side for structure (weekday, day, month) only.
export const LOCALES = ['hi', 'en', 'hi-Latn', 'mr', 'ta', 'bn', 'gu', 'te'] as const;
export type Locale = (typeof LOCALES)[number];

export const INTL_LOCALE: Readonly<Record<Locale, string>> = Object.freeze({
  hi: 'hi-IN',
  en: 'en-IN',
  'hi-Latn': 'en-IN',
  mr: 'mr-IN',
  ta: 'ta-IN',
  bn: 'bn-IN',
  gu: 'gu-IN',
  te: 'te-IN',
});
export const NATIVE_ZERO: Readonly<Partial<Record<Locale, number>>> = Object.freeze({
  hi: 0x0966,
  mr: 0x0966,
  bn: 0x09e6,
  ta: 0x0be6,
  gu: 0x0ae6,
  te: 0x0c66,
});
export const LAKH_CRORE: Readonly<Record<Locale, readonly [string, string]>> = Object.freeze({
  en: ['lakh', 'crore'],
  'hi-Latn': ['lakh', 'crore'],
  hi: ['लाख', 'करोड़'],
  mr: ['लाख', 'कोटी'],
  ta: ['லட்சம்', 'கோடி'],
  bn: ['লাখ', 'কোটি'],
  gu: ['લાખ', 'કરોડ'],
  te: ['లక్ష', 'కోటి'],
});
const LAKH = 100_000;
const CRORE = 10_000_000;

export class LocaleError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'LocaleError';
  }
}

export function isLocale(x: string): x is Locale {
  return (LOCALES as readonly string[]).includes(x);
}

function assertLocale(locale: string): asserts locale is Locale {
  if (!isLocale(locale)) {
    throw new LocaleError(`unsupported locale '${locale}'; use one of ${LOCALES.join(', ')}`);
  }
}

// Round whole rupees (>= 1 lakh) half-up to one decimal of lakh or crore. Returns [tenths, unit].
// Compact output deliberately drops paise: at lakh scale they are noise.
// 99.95+ lakh would print as "100 lakh", so it is promoted to crore instead.
function compactRound(rupees: number): [number, number] {
  let unit = rupees >= CRORE ? CRORE : LAKH;
  let tenths = Math.floor((rupees * 10 + Math.floor(unit / 2)) / unit);
  if (unit === LAKH && tenths >= 1000) {
    unit = CRORE;
    tenths = Math.floor((rupees * 10 + Math.floor(unit / 2)) / unit);
  }
  return [tenths, unit];
}

export function groupIndian(n: number): string {
  const digits = String(n);
  if (digits.length <= 3) return digits;
  let head = digits.slice(0, -3);
  const tail = digits.slice(-3);
  const pairs: string[] = [];
  while (head.length > 2) {
    pairs.unshift(head.slice(-2));
    head = head.slice(0, -2);
  }
  if (head) pairs.unshift(head);
  return `${pairs.join(',')},${tail}`;
}

export function toNativeDigits(text: string, locale: Locale): string {
  assertLocale(locale);
  const zero = NATIVE_ZERO[locale];
  if (zero === undefined) return text;
  return text.replace(/[0-9]/g, (d) => String.fromCodePoint(zero + Number(d)));
}

export function formatMoney(
  paise: number,
  locale: Locale,
  opts: { compact?: boolean; native?: boolean } = {},
): string {
  assertLocale(locale);
  if (!Number.isSafeInteger(paise)) throw new RangeError('paise must be a safe integer');
  const sign = paise < 0 ? '-' : '';
  const abs = Math.abs(paise);
  const rupees = Math.floor(abs / 100);
  const rest = abs % 100;
  let text: string;
  let suffix = '';
  if (opts.compact && rupees >= LAKH) {
    const [tenths, unit] = compactRound(rupees);
    const word = LAKH_CRORE[locale][unit === CRORE ? 1 : 0];
    const frac = tenths % 10;
    text = groupIndian(Math.floor(tenths / 10)) + (frac ? `.${frac}` : '');
    suffix = ` ${word}`;
  } else {
    text = groupIndian(rupees) + (rest ? `.${String(rest).padStart(2, '0')}` : '');
  }
  if (opts.native) text = toNativeDigits(text, locale);
  return `${sign}₹${text}${suffix}`;
}

const dateFormats = new Map<Locale, Intl.DateTimeFormat>();

function dateFormat(locale: Locale): Intl.DateTimeFormat {
  let fmt = dateFormats.get(locale);
  if (!fmt) {
    fmt = new Intl.DateTimeFormat(INTL_LOCALE[locale], {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      timeZone: 'Asia/Kolkata',
      numberingSystem: 'latn',
    });
    dateFormats.set(locale, fmt);
  }
  return fmt;
}

export function formatDate(value: Date, locale: Locale, opts: { native?: boolean } = {}): string {
  assertLocale(locale);
  const parts = dateFormat(locale).formatToParts(value);
  const get = (type: Intl.DateTimeFormatPartTypes) => parts.find((p) => p.type === type)?.value ?? '';
  const text = `${get('weekday')}, ${get('day')} ${get('month')}`;
  return opts.native ? toNativeDigits(text, locale) : text;
}
