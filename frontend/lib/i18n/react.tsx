'use client';

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import {
  SCRIPT_FONT,
  day,
  isUiLocale,
  money,
  shortDate,
  time,
  translate,
  type Params,
  type UiLocale,
} from './core';

const STORAGE_KEY = 'arth.locale';
const DEFAULT_LOCALE: UiLocale = 'hi-Latn';

type I18n = {
  locale: UiLocale;
  setLocale: (l: UiLocale) => void;
  t: (key: string, params?: Params) => string;
  money: (paise: number, compact?: boolean) => string;
  time: (iso: string) => string;
  day: (iso: string) => string;
  date: (iso: string) => string;
};

const Ctx = createContext<I18n | null>(null);

function readStored(): UiLocale | null {
  try {
    const fromUrl = new URLSearchParams(window.location.search).get('lang');
    if (fromUrl && isUiLocale(fromUrl)) return fromUrl;
    const stored = window.localStorage.getItem(STORAGE_KEY);
    return stored && isUiLocale(stored) ? stored : null;
  } catch {
    return null;
  }
}

/** Loads Inter plus the Noto family of the active script only (I3: fonts per script). */
function useScriptFont(locale: UiLocale) {
  useEffect(() => {
    const family = SCRIPT_FONT[locale];
    const families = [
      'Inter:wght@400;500;600;700;800',
      ...(family ? [`${family}:wght@400;500;600;700`] : []),
    ];
    const href = `https://fonts.googleapis.com/css2?${families
      .map((f) => `family=${f.replace(/ /g, '+')}`)
      .join('&')}&display=swap`;
    const id = 'arth-font';
    let link = document.getElementById(id) as HTMLLinkElement | null;
    if (!link) {
      link = document.createElement('link');
      link.id = id;
      link.rel = 'stylesheet';
      document.head.appendChild(link);
    }
    if (link.href !== href) link.href = href;
    document.documentElement.lang = locale === 'xx-LONG' ? 'en' : locale;
  }, [locale]);
}

export function I18nProvider({ children, initial }: { children: ReactNode; initial?: UiLocale }) {
  const [locale, setLocaleState] = useState<UiLocale>(initial ?? DEFAULT_LOCALE);
  useEffect(() => {
    if (initial) return;
    const stored = readStored();
    if (stored) setLocaleState(stored);
  }, [initial]);
  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === STORAGE_KEY && e.newValue && isUiLocale(e.newValue)) setLocaleState(e.newValue);
    };
    window.addEventListener('storage', onStorage);
    return () => window.removeEventListener('storage', onStorage);
  }, []);
  useScriptFont(locale);
  const setLocale = useCallback((l: UiLocale) => {
    setLocaleState(l);
    try {
      window.localStorage.setItem(STORAGE_KEY, l);
    } catch {
      // private mode: the choice lasts for this page only
    }
  }, []);
  const value = useMemo<I18n>(
    () => ({
      locale,
      setLocale,
      t: (key, params) => translate(locale, key, params),
      money: (paise, compact) => money(locale, paise, compact),
      time: (iso) => time(locale, iso),
      day: (iso) => day(locale, iso),
      date: (iso) => shortDate(locale, iso),
    }),
    [locale, setLocale],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n(): I18n {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useI18n outside I18nProvider');
  return ctx;
}

export function useT() {
  return useI18n().t;
}
