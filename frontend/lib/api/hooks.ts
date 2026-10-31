'use client';

import { useQuery } from '@tanstack/react-query';
import { useEffect, useState } from 'react';
import type { LayerPendingView } from '../contracts';
import { validate } from '../validate';
import { apiGet, dataMode, type DataMode } from './client';
import { isPending, type ViewSpec } from './views';

export type ViewState<T> = {
  data: T | undefined;
  pending: LayerPendingView | null;
  loading: boolean;
  error: Error | null;
  mode: DataMode;
  refetch: () => void;
};

/** Mode is resolved on the client after mount, so server and first client render agree (fixture). */
export function useDataMode(): DataMode {
  const [mode, setMode] = useState<DataMode>('fixture');
  useEffect(() => setMode(dataMode()), []);
  return mode;
}

/**
 * One TanStack query per view (I5). Live responses are validated against the view's contract (Ajv); a
 * response that fails validation still renders, with the reason logged, so a schema drift is visible
 * without blanking the device mid-demo.
 */
export function useView<T>(spec: ViewSpec<T>, opts: { enabled?: boolean } = {}): ViewState<T> {
  const mode = useDataMode();
  const query = useQuery({
    queryKey: ['view', ...spec.key, mode],
    enabled: opts.enabled ?? true,
    queryFn: async () => {
      if (mode === 'fixture') return spec.fixture();
      const body = await apiGet(spec.path);
      if (isPending(body)) return body;
      if (spec.schema && !validate(spec.schema, body)) {
        console.warn(`[arth] ${spec.path} does not match ${spec.schema}`);
      }
      return body as T;
    },
  });
  const raw = query.data;
  const pending = isPending(raw) ? raw : null;
  return {
    data: pending ? undefined : (raw as T | undefined),
    pending,
    loading: query.isLoading,
    error: query.error,
    mode,
    refetch: () => void query.refetch(),
  };
}
