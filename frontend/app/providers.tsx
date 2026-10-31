'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { DataProvider } from '@/lib/api/live';
import { I18nProvider } from '@/lib/i18n/react';

/**
 * The surfaces render on the client only: the data mode (live session vs fixture shop) lives in the URL and
 * localStorage, so a server render would show the fixture shop first and effects would act on it (a "new bill"
 * opened the fixture bill in live mode).
 */
export function Providers({ children }: { children: ReactNode }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);
  if (!mounted) return null;
  return (
    <I18nProvider>
      <DataProvider>{children}</DataProvider>
    </I18nProvider>
  );
}
