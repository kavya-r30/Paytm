// HTTP client for the Arth API (spec C2, I5). Reads GET /v1/views/*, writes POST /v1/commands with an
// Idempotency-Key, and maps RFC 9457 problem JSON to a typed error the UI localises by message_key.
import type { Problem } from '../contracts';

export const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000';

/** Surface bearer tokens (dev defaults match backend Settings); they only gate login and the director. */
export const SURFACE_TOKEN = {
  device: process.env.NEXT_PUBLIC_DEVICE_TOKEN ?? 'dev-device',
  console: process.env.NEXT_PUBLIC_CONSOLE_TOKEN ?? 'dev-console',
  director: process.env.NEXT_PUBLIC_DIRECTOR_TOKEN ?? 'dev-director',
} as const;

/** The Console logs in on its own channel, so it keeps its own session; every other surface uses the device's. */
function sessionKey(): string {
  if (typeof window !== 'undefined' && window.location.pathname.startsWith('/console'))
    return 'arth.session.console';
  return 'arth.session';
}

export type DataMode = 'live' | 'fixture';

/**
 * The session bearer token, from `?session=` (stored for later), localStorage or NEXT_PUBLIC_ARTH_SESSION.
 * `?fixtures=1` forces fixture mode. Without a token every surface renders the Gupta fixtures.
 */
export function sessionToken(): string | null {
  if (typeof window === 'undefined') return process.env.NEXT_PUBLIC_ARTH_SESSION ?? null;
  try {
    const params = new URLSearchParams(window.location.search);
    if (params.get('fixtures') === '1') return null;
    const fromUrl = params.get('session');
    if (fromUrl) {
      window.localStorage.setItem(sessionKey(), fromUrl);
      return fromUrl;
    }
    return window.localStorage.getItem(sessionKey()) ?? process.env.NEXT_PUBLIC_ARTH_SESSION ?? null;
  } catch {
    return process.env.NEXT_PUBLIC_ARTH_SESSION ?? null;
  }
}

export function setSessionToken(token: string | null, key: string = sessionKey()) {
  try {
    if (token) window.localStorage.setItem(key, token);
    else window.localStorage.removeItem(key);
  } catch {
    // storage blocked: the token lives in the URL only
  }
}

export const DEVICE_CREDENTIAL_KEY = 'arth.device_credential';

export function deviceCredential(): string | null {
  try {
    return window.localStorage.getItem(DEVICE_CREDENTIAL_KEY);
  } catch {
    return null;
  }
}

/**
 * POST /v1/staff/login (STF-2) with the registered device credential (printed by `python dev.py seed`), a staff
 * PIN and the surface bearer token. Stores the session for that channel and returns it.
 */
export async function login(
  credential: string,
  staffId: string,
  pin: string,
  channel: 'device' | 'console',
): Promise<string> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}/v1/staff/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${SURFACE_TOKEN[channel]}`,
        'Idempotency-Key': newIdempotencyKey(),
      },
      body: JSON.stringify({ device_credential: credential, staff_id: staffId, pin, channel }),
    });
  } catch (e) {
    throw new NetworkError(e);
  }
  const body = (await parse(res)) as { token: string };
  setSessionToken(body.token, channel === 'console' ? 'arth.session.console' : 'arth.session');
  try {
    window.localStorage.setItem(DEVICE_CREDENTIAL_KEY, credential);
  } catch {
    // the credential is only needed for the next login
  }
  return body.token;
}

/** Director-only calls (sim controls, world, clock) authenticate with the director surface token. */
export async function directorPost(path: string, body: unknown): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${SURFACE_TOKEN.director}` },
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new NetworkError(e);
  }
  return parse(res);
}

export async function directorGet(path: string): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { Authorization: `Bearer ${SURFACE_TOKEN.director}` },
    });
  } catch (e) {
    throw new NetworkError(e);
  }
  return parse(res);
}

export function dataMode(): DataMode {
  return sessionToken() ? 'live' : 'fixture';
}

export class ApiProblem extends Error {
  constructor(
    readonly status: number,
    readonly problem: Partial<Problem> & { code?: string; message_key?: string },
  ) {
    super(problem.title ?? problem.code ?? `HTTP ${status}`);
    this.name = 'ApiProblem';
  }
  get messageKey(): string {
    return this.problem.message_key ?? 'error.generic';
  }
}

/** True when the request never reached the server (offline, API down): the journal may take it. */
export class NetworkError extends Error {
  constructor(cause: unknown) {
    super(`network: ${String(cause)}`);
    this.name = 'NetworkError';
  }
}

function headers(extra: Record<string, string> = {}): Record<string, string> {
  const token = sessionToken();
  return {
    Accept: 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  };
}

async function parse(res: Response): Promise<unknown> {
  const text = await res.text();
  const body: unknown = text ? JSON.parse(text) : null;
  if (!res.ok) throw new ApiProblem(res.status, (body ?? {}) as ApiProblem['problem']);
  return body;
}

export async function apiGet(path: string, init: RequestInit = {}): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, { ...init, headers: headers() });
  } catch (e) {
    throw new NetworkError(e);
  }
  return parse(res);
}

export async function apiPost(path: string, body: unknown, idempotencyKey?: string): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: headers({
        'Content-Type': 'application/json',
        ...(idempotencyKey ? { 'Idempotency-Key': idempotencyKey } : {}),
      }),
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new NetworkError(e);
  }
  return parse(res);
}

/** PII-safe profile routes (PATCH /v1/patrons): identifying fields never become bus payloads. */
export async function apiPatch(path: string, body: unknown): Promise<unknown> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method: 'PATCH',
      headers: headers({ 'Content-Type': 'application/json', 'Idempotency-Key': newIdempotencyKey() }),
      body: JSON.stringify(body),
    });
  } catch (e) {
    throw new NetworkError(e);
  }
  return parse(res);
}

export function newIdempotencyKey(): string {
  return typeof crypto !== 'undefined' && 'randomUUID' in crypto
    ? crypto.randomUUID()
    : `k-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}
