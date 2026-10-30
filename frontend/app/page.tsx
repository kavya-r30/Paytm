import { HealthBadge } from './health-badge';

// Developer index. The product surfaces (and the no-literal-strings lint) arrive in L7.
const SURFACES: [string, string][] = [
  ['Device · Display (4:3)', '/device'],
  ['Device · Voice', '/device-voice'],
  ['Customer display', '/customer-display'],
  ['Phones', '/phone/owner'],
  ['Console', '/console'],
  ['Stage', '/stage'],
  ['Director', '/director'],
];

export default function DevIndex() {
  return (
    <main className="mx-auto max-w-2xl p-8">
      <h1 className="text-title text-midnight">Arth · dev index</h1>
      <div className="mt-4 rounded-card bg-white p-6 shadow-1">
        <HealthBadge />
      </div>
      <ul className="mt-6 space-y-2 text-body text-ink-2">
        {SURFACES.map(([label, href]) => (
          <li key={href}>
            {label} <span className="text-meta text-ink-3">({href}, arrives in L7)</span>
          </li>
        ))}
      </ul>
    </main>
  );
}
