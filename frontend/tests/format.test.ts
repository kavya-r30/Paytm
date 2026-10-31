import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { describe, expect, it } from 'vitest';
import {
  formatDate,
  formatMoney,
  INTL_LOCALE,
  isLocale,
  LAKH_CRORE,
  LOCALES,
  LocaleError,
  NATIVE_ZERO,
  toNativeDigits,
  type Locale,
} from '../lib/format';

type MoneyCase = { paise: number; locale: Locale; compact?: boolean; native?: boolean; expected: string };
type DateCase = { date: string; locale: Locale; expected: string };
type LocaleSpec = {
  lakh: string;
  crore: string;
  nativeZero: number | null;
  babel: string;
  intl: string;
};
const cases = JSON.parse(
  readFileSync(
    fileURLToPath(new URL('../../contracts/fixtures/format_cases.json', import.meta.url)),
    'utf-8',
  ),
) as { locales: Record<Locale, LocaleSpec>; money: MoneyCase[]; dates: DateCase[] };

const SPEC = cases.locales;
const NON_LATIN = LOCALES.filter((l) => SPEC[l].nativeZero !== null);
const day = new Date('2026-10-29T12:00:00+05:30');

describe('formatMoney matches the shared fixture', () => {
  it.each(cases.money)('$locale $paise compact=$compact native=$native → $expected', (c) => {
    expect(formatMoney(c.paise, c.locale, { compact: c.compact, native: c.native })).toBe(c.expected);
  });
});

describe('formatDate matches the shared fixture', () => {
  it.each(cases.dates)('$locale $date → $expected', (c) => {
    expect(formatDate(new Date(`${c.date}T12:00:00+05:30`), c.locale)).toBe(c.expected);
  });
});

describe('dates in every locale (structure only; names may differ from Babel)', () => {
  it.each([...LOCALES])('%s has weekday, day 29 and month', (locale) => {
    const [weekday, rest] = formatDate(day, locale).split(/, (.*)/s);
    expect(weekday).toBeTruthy();
    expect(rest.startsWith('29 ')).toBe(true);
    expect(rest.slice(3).trim()).not.toBe('');
  });
  it.each(NON_LATIN)('%s native date uses native digits', (locale) => {
    expect(formatDate(day, locale, { native: true })).toContain(toNativeDigits('29', locale));
  });
});

describe('fixture coverage', () => {
  it.each([...LOCALES])('%s has plain, lakh, crore (and native) cases', (locale) => {
    const mine = cases.money.filter((c) => c.locale === locale);
    const { lakh, crore } = SPEC[locale];
    expect(mine.some((c) => !c.compact && !c.native)).toBe(true);
    expect(mine.some((c) => c.compact && c.expected.endsWith(` ${lakh}`))).toBe(true);
    expect(mine.some((c) => c.compact && c.expected.endsWith(` ${crore}`))).toBe(true);
    if (NON_LATIN.includes(locale)) expect(mine.some((c) => c.native)).toBe(true);
  });
});

describe('code tables equal the fixture locales section', () => {
  it('lists the same locales in the same order', () => {
    expect([...LOCALES]).toEqual(Object.keys(SPEC));
  });
  it.each(Object.keys(SPEC) as Locale[])('%s', (locale) => {
    const row = SPEC[locale];
    expect(LAKH_CRORE[locale]).toEqual([row.lakh, row.crore]);
    expect(NATIVE_ZERO[locale] ?? null).toBe(row.nativeZero);
    expect(INTL_LOCALE[locale]).toBe(row.intl);
  });
});

describe('dates: day edges', () => {
  it('does not pad a single-digit day', () => {
    expect(formatDate(new Date('2026-11-05T12:00:00+05:30'), 'en')).toBe('Thu, 5 Nov');
  });
  it('uses the IST calendar day for a late-evening instant', () => {
    expect(formatDate(new Date('2026-10-29T23:30:00+05:30'), 'en')).toBe('Thu, 29 Oct');
  });
});

describe('guards', () => {
  it('isLocale narrows known locales only', () => {
    expect(isLocale('hi-Latn')).toBe(true);
    expect(isLocale('fr')).toBe(false);
    expect(isLocale('toString')).toBe(false);
  });
  it('rejects unknown locales everywhere', () => {
    const bad = 'fr' as Locale;
    expect(() => formatMoney(100, bad)).toThrow(LocaleError);
    expect(() => formatMoney(100, bad)).toThrow("unsupported locale 'fr'");
    expect(() => formatMoney(10_000_000, bad, { compact: true })).toThrow(LocaleError);
    expect(() => formatDate(day, bad)).toThrow(LocaleError);
    expect(() => toNativeDigits('29', bad)).toThrow(LocaleError);
    expect(() => formatMoney(100, 'toString' as Locale)).toThrow(LocaleError);
  });
  it.each([1.5, Number.NaN, Number.POSITIVE_INFINITY, 2 ** 53])('rejects non-safe-integer paise %s', (n) => {
    expect(() => formatMoney(n, 'en')).toThrow(RangeError);
    expect(() => formatMoney(n, 'en')).toThrow('paise must be a safe integer');
  });
});
