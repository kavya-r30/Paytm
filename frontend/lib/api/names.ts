'use client';

// Display names for IDs that views carry without names (contract-change request #2). Fixture mode reads the
// fixture dictionary; live mode reads the item or patron view once per ID (cached by TanStack Query).
import { useQuery } from '@tanstack/react-query';
import { NAMES } from '../fixtures/gupta';
import { apiGet } from './client';
import { useDataMode } from './hooks';

function kindOf(id: string): string {
  return id.split('_')[0] ?? '';
}

export function shortId(id: string): string {
  return `${kindOf(id)}·${id.slice(-4)}`;
}

export function useName(id: string | null | undefined, locale = 'en'): string {
  const mode = useDataMode();
  const kind = id ? kindOf(id) : '';
  const live = mode === 'live' && !!id && (kind === 'item' || kind === 'pat');
  const q = useQuery({
    queryKey: ['name', id, mode],
    enabled: live,
    staleTime: Infinity,
    queryFn: async () => {
      const body = (await apiGet(kind === 'item' ? `/v1/views/item/${id}` : `/v1/views/patron/${id}`)) as {
        names?: Record<string, string>;
        display_name?: string;
      };
      return body.display_name ?? body.names?.[locale] ?? body.names?.en ?? null;
    },
  });
  if (!id) return '';
  if (mode === 'fixture') return NAMES[id] ?? shortId(id);
  return q.data ?? NAMES[id] ?? shortId(id);
}
