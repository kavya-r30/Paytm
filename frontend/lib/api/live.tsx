'use client';

import { QueryClient, QueryClientProvider, useQueryClient } from '@tanstack/react-query';
import { useEffect, useState, type ReactNode } from 'react';
import { useStream, useTurn } from '../store/turn';
import { API_BASE, sessionToken } from './client';
import { flushJournal } from './journal';
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
              if (msg.event === 'envelope') {
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
      <StreamConnector />
      {children}
    </QueryClientProvider>
  );
}
