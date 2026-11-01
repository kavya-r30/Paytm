// Simulator and director calls (L2): persona threads, inbound messages, the UPI pay page, world/clock/faults.
// These are presenter tools, authenticated with the director surface token (never shipped to a real device).
import type { Scenario } from '../contracts/scenario';
import { API_BASE, directorGet, directorPost, sessionToken, setSessionToken } from './client';

/** Session tokens are `merchant.session.kind.signature`; the merchant id is the first segment. */
export function merchantId(token: string | null = sessionToken()): string | null {
  const first = token?.split('.')[0];
  return first && /^[a-z][a-z0-9]{1,9}_[0-9A-HJKMNP-TV-Z]{26}$/.test(first) ? first : null;
}

export type ThreadMessage = {
  id: string;
  direction: 'in' | 'out';
  category: string;
  kind: string;
  created_at: string;
  body: {
    text?: string;
    template_key?: string;
    params?: Record<string, unknown>;
    url?: string;
    [k: string]: unknown;
  };
};

export type Thread = {
  id: string;
  persona_id: string;
  name: string;
  role: string;
  lang: string;
  patron_id?: string | null;
  supplier_id?: string | null;
  messages: ThreadMessage[];
};

export async function threads(merchant: string): Promise<Thread[]> {
  const body = (await directorGet(`/sim/messages/threads?merchant_id=${encodeURIComponent(merchant)}`)) as {
    threads: Thread[];
  };
  return body.threads;
}

export function inbound(merchant: string, personaId: string, text: string) {
  return directorPost('/sim/messages/inbound', {
    merchant_id: merchant,
    persona_id: personaId,
    text,
    kind: 'text',
  });
}

export type PayPage = {
  token: string;
  payee_name: string;
  payee_vpa: string | null;
  amount_paise: number;
  status: string;
  expires_at: string;
};

export async function payPage(token: string): Promise<PayPage> {
  const res = await fetch(`${API_BASE}/sim/pay/${encodeURIComponent(token)}`);
  if (!res.ok) throw new Error(`pay page ${res.status}`);
  return (await res.json()) as PayPage;
}

export async function payNow(token: string, outcome: 'success' | 'pending' | 'failed') {
  const res = await fetch(`${API_BASE}/sim/pay/${encodeURIComponent(token)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ outcome, payer_vpa: 'customer@okbank' }),
  });
  if (!res.ok) throw new Error(`pay ${res.status}`);
  return res.json() as Promise<Record<string, unknown>>;
}

export type WorldManifest = {
  merchant_id: string;
  device_id: string;
  owner_id: string;
  device_credential: string;
  [k: string]: unknown;
};

export function buildWorld(pack: string, days: number) {
  return directorPost('/v1/director/world', { pack, days, seed: 1, size: 'small' }) as Promise<WorldManifest>;
}

/** A real staff session for the seeded shop, stored for this browser's device and console surfaces. */
export async function presenterSessions(merchant?: string) {
  const device = (await directorPost('/v1/director/session', {
    merchant_id: merchant,
    surface: 'device',
  })) as {
    token: string;
  };
  const console = (await directorPost('/v1/director/session', {
    merchant_id: merchant,
    surface: 'console',
  })) as {
    token: string;
  };
  setSessionToken(device.token, 'arth.session');
  setSessionToken(console.token, 'arth.session.console');
  return { device: device.token, console: console.token };
}

/** STG-DIRECTOR clock control: freeze the shop's clock or let it run at real time. */
export function setClockRunning(running: boolean) {
  return directorPost('/v1/director/clock', { running }) as Promise<{ clock: string; running: boolean }>;
}

export function moveClock(advanceMinutes: number) {
  return directorPost('/v1/director/clock', { advance_minutes: advanceMinutes }) as Promise<{
    clock: string;
  }>;
}

export function injectFault(merchant: string, kind: 'duplicate' | 'drop' | 'delay' | 'wrong_amount') {
  return directorPost('/sim/rails/faults', { merchant_id: merchant, kind, times: 1 });
}

export function staticPay(merchant: string, amountPaise: number) {
  return directorPost('/sim/rails/static-pay', {
    merchant_id: merchant,
    amount_paise: amountPaise,
    payer_vpa: 'priya@okaxis',
    outcome: 'success',
  });
}

/** Stage ↔ director channel: same-browser BroadcastChannel; the director's beat sets the stage's focus. */
export type StageFocus = {
  beat: number;
  scene: string;
  device_screen?: string;
  phone_persona?: string;
  evidence_tab?: string;
  table?: string;
  edition?: 'display' | 'voice';
  paused?: boolean;
  /** Library beats carry their own text; local beats are looked up by index. */
  scenario_title?: string;
  title?: string;
  cue?: string;
  total?: number;
};

/** L8 library and live play: the backend runner plays each beat in the running server. */
export async function scenarioLibrary(): Promise<Scenario[]> {
  return ((await directorGet('/v1/director/scenarios')) as { scenarios: Scenario[] }).scenarios;
}

export function playScenario(scenario: string) {
  return directorPost('/v1/director/play', { scenario }) as Promise<{
    scenario: string;
    merchant_id: string;
    beats: string[];
  }>;
}

/** A scenario already played or restored on the server (`python dev.py demo`): the Director continues it. */
export function currentPlay() {
  return directorGet('/v1/director/play') as Promise<{
    scenario: string | null;
    merchant_id: string | null;
    done?: string[];
  }>;
}

export type BeatResult = { beat_id: string; ok: boolean; ms?: number; error?: string; snapshot: string };

export function playBeat(beatId: string) {
  return directorPost('/v1/director/play/beat', { beat_id: beatId }) as Promise<BeatResult>;
}

/** Recovery button: back to the snapshot taken at the scene's first beat (DB + clock, < 3 s). */
export function restoreSnapshot(name: string) {
  return directorPost('/v1/director/restore', { name }) as Promise<{
    name: string;
    clock: string;
    ms: number;
  }>;
}

export const STAGE_CHANNEL = 'arth-stage';
