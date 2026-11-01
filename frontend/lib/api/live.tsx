'use client';

import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import { create } from 'zustand';
import { useEffect, useState, type ReactNode } from 'react';
import { useI18n } from '../i18n/react';
import { useStream, useTurn } from '../store/turn';
import { API_BASE, sessionToken, setSessionToken } from './client';
import { flushJournal } from './journal';
import { presenterSessions } from './sim';
import { SseParser, invalidatedViews } from './stream';

/** Opens the surface's SSE connection and refetches the views each `view.invalidate` names. */
function StreamConnector() {
  const client = useQueryClient();
  useEffect(() => {
    const token = sessionToken();
    if (!token) return;
    const abort = new AbortController();
    const { setConnected, push } = useStream.getState();
    let retry = 1000;

    async function connect() {
      while (!abort.signal.aborted) {
        try {
          const res = await fetch(`${API_BASE}/v1/stream`, {
            headers: { Authorization: `Bearer ${token}`, Accept: 'text/event-stream' },
            signal: abort.signal,
          });
          if (!res.ok || !res.body) throw new Error(`stream ${res.status}`);
          setConnected(true);
          retry = 1000;
          void flushJournal();
          const reader = res.body.pipeThrough(new TextDecoderStream()).getReader();
          const parser = new SseParser();
          for (;;) {
            const { value, done } = await reader.read();
            if (done) break;
            for (const msg of parser.feed(value)) {
              let data: Record<string, unknown> = {};
              try {
                data = JSON.parse(msg.data) as Record<string, unknown>;
              } catch {
                continue;
              }
              if (msg.event === 'view.invalidate') {
                for (const view of invalidatedViews(data)) {
                  void client.invalidateQueries({ queryKey: ['view', view] });
                }
              }
              // A device answers its own turns from the POST response; the shop-wide broadcast (other
              // devices, phones, WhatsApp) would otherwise overwrite this device's answer with someone else's.
              if (msg.event === 'envelope' && !window.location.pathname.startsWith('/device/')) {
                useTurn.getState().applyEnvelope(data as never);
              }
              push({
                kind: msg.event === 'span' ? 'span' : 'event',
                type: msg.event === 'span' ? String(data.name ?? 'span') : msg.event,
                at: String(data.occurred_at ?? data.start ?? new Date().toISOString()),
                data,
              });
            }
          }
        } catch {
          if (abort.signal.aborted) return;
        }
        setConnected(false);
        await new Promise((r) => setTimeout(r, retry));
        retry = Math.min(retry * 2, 15000);
      }
    }
    void connect();
    return () => abort.abort();
  }, [client]);
  return null;
}

/**
 * Normal (dev) mode is live: a surface without a working session asks the API for the seeded shop's owner
 * session (the Director's presenter route), so every component reads and writes real data. A stored token the
 * API no longer accepts (DB reset, expiry) is replaced the same way. `?fixtures=1` keeps the fixture shop;
 * outside `mode: dev` the API refuses the dev director token and the surface stays on its PIN login.
 */
let connecting = false;

/** Whether the surface may take a turn yet: false while it is still connecting itself to the backend (a query
 * typed then would be answered by the fixture shop, or lost in the reload that switches to live data). */
export const useLink = create<{ ready: boolean }>(() => ({ ready: false }));
const ready = () => useLink.setState({ ready: true });

function LiveBootstrap() {
  const { t } = useI18n();
  const [problem, setProblem] = useState<'unreachable' | 'no_shop' | null>(null);
  useEffect(() => {
    if (new URLSearchParams(window.location.search).get('fixtures') === '1') return ready();
    if (window.self !== window.top) return ready(); // the stage hands its iframes their sessions in the URL
    void (async () => {
      const health = (await fetch(`${API_BASE}/healthz`)
        .then((r) => r.json())
        .catch(() => null)) as { mode?: string } | null;
      if (!health) {
        setProblem('unreachable'); // API down, wrong URL, or this page's origin is not allowed (CORS)
        return ready();
      }
      const token = sessionToken();
      if (token) {
        const res = await fetch(`${API_BASE}/v1/views/home`, {
          headers: { Authorization: `Bearer ${token}` },
        }).catch(() => null);
        if (!res) {
          setProblem('unreachable');
          return ready();
        }
        if (res.status !== 401) return ready(); // a working live session: turns go straight to Arth
        setSessionToken(null, 'arth.session');
        setSessionToken(null, 'arth.session.console');
      }
      if (health.mode !== 'dev') return ready(); // outside dev the PIN screen logs in
      if (connecting) return; // React runs effects twice in dev: one session request per page load
      connecting = true;
      try {
        await presenterSessions();
      } catch {
        setProblem('no_shop'); // no shop yet (or several): the Director builds or picks one
        return ready();
      }
      window.location.reload();
    })();
  }, []);
  if (!problem) return null;
  return (
    <div
      role="alert"
      className="fixed inset-x-0 top-0 z-50 bg-red px-4 py-2 text-center text-body font-semibold text-white"
    >
      {t(problem === 'unreachable' ? 'status.backend_down' : 'status.no_shop', { api: API_BASE })}
    </div>
  );
}

export function DataProvider({ children }: { children: ReactNode }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: { queries: { staleTime: 15_000, retry: 1, refetchOnWindowFocus: false } },
      }),
  );
  useEffect(() => {
    const online = () => void flushJournal();
    window.addEventListener('online', online);
    return () => window.removeEventListener('online', online);
  }, []);
  return (
    <QueryClientProvider client={client}>
      <LiveBootstrap />
      <StreamConnector />
      {children}
    </QueryClientProvider>
  );
}
