// Deterministic prefixed ULIDs for fixtures: fid('bill', 3) → bill_01JBQ0Z7Y8K3M4N5P6Q7R8S903.
const BASE = '01JBQ0Z7Y8K3M4N5P6Q7R8S9';
const CROCKFORD = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

export function fid(kind: string, n: number): string {
  const hi = CROCKFORD[Math.floor(n / 32) % 32]!;
  const lo = CROCKFORD[n % 32]!;
  return `${kind}_${BASE}${hi}${lo}`;
}

/** Fixture "now": Thu 29 Oct 2026, 2:10 pm IST (the Gupta scenario's midday beat). */
export const NOW = '2026-10-29T08:40:00Z';

export function minutesAgo(m: number): string {
  return new Date(Date.parse(NOW) - m * 60_000).toISOString().replace(/\.\d{3}Z$/, 'Z');
}

export function minutesAhead(m: number): string {
  return minutesAgo(-m);
}
