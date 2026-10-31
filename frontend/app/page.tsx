'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import { apiGet, dataMode } from '@/lib/api/client';
import { HealthBadge } from './health-badge';

// Developer index (exempt from the no-literal-strings lint): every surface in spec Part I1.
const SURFACES: [string, string][] = [
  ['Device · Display (4:3)', '/device/home'],
  ['Device · Voice edition', '/device-voice'],
  ['Customer display', '/customer-display'],
  ['Phones', '/phone/owner'],
  ['Console', '/console/home'],
  ['UPI pay page', '/pay/demo-token'],
  ['Storefront', '/s/gupta-general-store'],
  ['Stage', '/stage'],
  ['Director', '/director'],
  ['Pseudo-locale (overflow check)', '/device/home?lang=xx-LONG'],
];

export default function DevIndex() {
  // live mode links the session shop's own storefront (its slug comes from the world, not the fixture)
  const [storefront, setStorefront] = useState('/s/gupta-general-store');
  useEffect(() => {
    if (dataMode() !== 'live') return;
    void apiGet('/v1/views/storefront')
      .then((v) => setStorefront((v as { url: string }).url))
      .catch(() => {});
  }, []);
  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-title text-midnight">Arth · dev index</h1>
      <div className="mt-4 rounded-card bg-white p-6 shadow-1">
        <HealthBadge />
        <p className="mt-2 text-meta text-ink-3">
          Normal mode is live: with one shop in the API, every surface connects to it automatically. With no
          shop yet, build one in the Director (or <code>python dev.py seed</code>); <code>?fixtures=1</code>{' '}
          shows the Gupta fixture shop.
        </p>
      </div>
      <ul className="mt-6 space-y-2 text-body text-ink-2">
        {SURFACES.map(([label, fixed]) => [label, fixed.startsWith('/s/') ? storefront : fixed]).map(
          ([label, href]) => (
            <li key={href}>
              <Link href={href} className="font-semibold text-cyan-text hover:underline">
                {label}
              </Link>{' '}
              <span className="text-meta text-ink-3">{href}</span>
            </li>
          ),
        )}
      </ul>
    </main>
  );
}
