'use client';

import type { ReactNode } from 'react';
import { ErrorState, Loading, PendingState } from '@/components/shell/device';
import type { ViewState } from '@/lib/api/hooks';

export type ScreenProps = { param?: string };

/** Renders the J0 states for a view: loading, error/offline, layer-pending, then the full screen. */
export function ViewGate<T>({
  state,
  children,
  pendingIcon,
}: {
  state: ViewState<T>;
  children: (data: T) => ReactNode;
  pendingIcon?: ReactNode;
}) {
  if (state.pending) return <PendingState pending={state.pending} icon={pendingIcon} />;
  if (state.error) return <ErrorState error={state.error} onRetry={state.refetch} />;
  if (state.loading || state.data === undefined) return <Loading />;
  return <>{children(state.data)}</>;
}

/** Field from an open object (gate scopes, briefs) without trusting its type. */
export function field<T>(obj: unknown, key: string, fallback: T): T {
  if (obj && typeof obj === 'object' && key in obj) {
    const v = (obj as Record<string, unknown>)[key];
    if (v !== undefined && v !== null && typeof v === typeof fallback) return v as T;
  }
  return fallback;
}
