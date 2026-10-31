import Link from 'next/link';
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
  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-title text-midnight">Arth · dev index</h1>
      <div className="mt-4 rounded-card bg-white p-6 shadow-1">
        <HealthBadge />
        <p className="mt-2 text-meta text-ink-3">
          No session: surfaces show the Gupta fixture shop. For live data run <code>python dev.py seed</code>,
          then use the Director (Connect) or the PIN screen.
        </p>
      </div>
      <ul className="mt-6 space-y-2 text-body text-ink-2">
        {SURFACES.map(([label, href]) => (
          <li key={href}>
            <Link href={href} className="font-semibold text-cyan-text hover:underline">
              {label}
            </Link>{' '}
            <span className="text-meta text-ink-3">{href}</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
