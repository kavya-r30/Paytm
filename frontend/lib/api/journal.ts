// Offline command journal (EDG-1). Cash and static-QR billing keep working offline: their commands are
// journalled with their Idempotency-Key and replayed when the network returns, so sync is idempotent.
// Voice, coupons and anything that messages a customer need the network and are refused instead.
import { apiPost, NetworkError } from './client';

const KEY = 'arth.journal';

export type JournalEntry = { type: string; payload: Record<string, unknown>; key: string; at: string };

/** Commands safe to take offline: counter work and cash settlement only. */
const OFFLINE_OK = new Set([
  'counter.open_bill',
  'counter.add_lines',
  'counter.set_qty',
  'counter.remove_line',
  'counter.attach_patron',
  'counter.park',
  'counter.resume',
  'counter.checkout',
  'stock.count',
]);

export function offlineAllowed(type: string, payload: Record<string, unknown>): boolean {
  if (!OFFLINE_OK.has(type)) return false;
  return type !== 'counter.checkout' || payload.mode === 'cash' || payload.mode === 'static_qr';
}

export function readJournal(): JournalEntry[] {
  try {
    return JSON.parse(window.localStorage.getItem(KEY) ?? '[]') as JournalEntry[];
  } catch {
    return [];
  }
}

function write(entries: JournalEntry[]) {
  try {
    window.localStorage.setItem(KEY, JSON.stringify(entries));
  } catch {
    // storage full or blocked: the entry is lost, and the caller already showed it as queued
  }
}

export function journal(entry: JournalEntry) {
  write([...readJournal(), entry]);
}

let flushing = false;

/** Replays journalled commands in order; stops at the first network failure and keeps the rest. */
export async function flushJournal(): Promise<number> {
  if (flushing || typeof window === 'undefined') return 0;
  flushing = true;
  let sent = 0;
  try {
    const entries = readJournal();
    while (entries.length) {
      const e = entries[0]!;
      try {
        await apiPost('/v1/commands', { type: e.type, payload: e.payload }, e.key);
      } catch (err) {
        if (err instanceof NetworkError) break;
        // a refusal is final: the server already decided (same key), drop it
      }
      entries.shift();
      write(entries);
      sent += 1;
    }
  } finally {
    flushing = false;
  }
  return sent;
}
