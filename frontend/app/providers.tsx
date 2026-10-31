'use client';

import type { ReactNode } from 'react';
import { DataProvider } from '@/lib/api/live';
import { I18nProvider } from '@/lib/i18n/react';

export function Providers({ children }: { children: ReactNode }) {
  return (
    <I18nProvider>
      <DataProvider>{children}</DataProvider>
    </I18nProvider>
  );
}
