'use client';

// Writes (I5): POST /v1/commands with an Idempotency-Key. The server decides the tier; the UI reacts:
// R1 → undo toast (queued, 30 s), R2 → amber read-back until confirmed, R3 → gate card, R4 → Console pointer.
import { useQueryClient } from '@tanstack/react-query';
import { useCallback } from 'react';
import type { CommandResult } from '../contracts';
import { useTurn } from '../store/turn';
import { ApiProblem, NetworkError, apiPost, dataMode, newIdempotencyKey } from './client';
import { journal, offlineAllowed } from './journal';

export type Tier = 'R0' | 'R1' | 'R2' | 'R3' | 'R4';

/** Commands that are R4 by policy: the device never submits them, it points to the Console (CON-R4). */
export const CONSOLE_ONLY = new Set([
  'treasury.refund',
  'capital.apply',
  'catalog.bulk_price',
  'privacy.erase_patron',
]);

export type CommandOutcome =
  | { kind: 'done'; result: CommandResult }
  | { kind: 'queued'; result: CommandResult }
  | { kind: 'gate'; result: CommandResult }
  | { kind: 'console' }
  | { kind: 'offline' }
  | { kind: 'refused'; messageKey: string; params: Record<string, unknown> };

let fixtureSeq = 0;

function fixtureResult(type: string): CommandResult {
  fixtureSeq += 1;
  const n = String(fixtureSeq).padStart(2, '0').slice(-2);
  return {
    command_id: `cmd_01JBQ0Z7Y8K3M4N5P6Q7R8S9${n.replace(/[^0-9]/g, '0')}`,
    status: 'executed',
    tier: 'R1',
    data: { fixture: true, type },
  };
}

export function useCommand() {
  const client = useQueryClient();
  const toast = useTurn((s) => s.toast);

  return useCallback(
    async (
      type: string,
      payload: Record<string, unknown>,
      opts: { label?: string; undo?: { type: string; payload: Record<string, unknown> } } = {},
    ): Promise<CommandOutcome> => {
      const label = opts.label ?? type;
      const undo = opts.undo;
      if (CONSOLE_ONLY.has(type)) {
        toast({ textKey: 'toast.console_only', params: {}, until: null, tone: 'amber' });
        return { kind: 'console' };
      }
      const key = newIdempotencyKey();
      if (dataMode() === 'fixture') {
        const result = fixtureResult(type);
        toast({
          textKey: 'toast.done',
          params: { what: label },
          until: undo ? Date.now() + 30_000 : null,
          tone: 'done',
          commandId: result.command_id,
          undo,
        });
        return { kind: 'done', result };
      }
      try {
        const result = (await apiPost('/v1/commands', { type, payload }, key)) as CommandResult;
        void client.invalidateQueries({ queryKey: ['view'] });
        if (result.envelope) useTurn.getState().applyEnvelope(result.envelope);
        if (result.status === 'needs_approval') {
          toast({
            textKey: 'toast.needs_approval',
            params: { tier: result.tier ?? 'R3' },
            until: null,
            tone: 'amber',
          });
          return { kind: 'gate', result };
        }
        if (result.status === 'queued') {
          const until = result.due_at ? Date.parse(result.due_at) : Date.now() + 30_000;
          toast({
            textKey: 'toast.queued',
            params: { what: label },
            until,
            tone: 'done',
            commandId: result.command_id,
          });
          return { kind: 'queued', result };
        }
        toast({
          textKey: 'toast.done',
          params: { what: label },
          until: undo ? Date.now() + 30_000 : null,
          tone: 'done',
          commandId: result.command_id,
          undo,
        });
        return { kind: 'done', result };
      } catch (err) {
        if (err instanceof NetworkError) {
          if (offlineAllowed(type, payload)) {
            journal({ type, payload, key, at: new Date().toISOString() });
            toast({ textKey: 'toast.offline_saved', until: null, tone: 'info' });
            return { kind: 'offline' };
          }
          toast({ textKey: 'toast.needs_network', until: null, tone: 'error' });
          return { kind: 'refused', messageKey: 'toast.needs_network', params: {} };
        }
        if (err instanceof ApiProblem) {
          const params = (err.problem.params ?? {}) as Record<string, unknown>;
          toast({
            textKey: err.messageKey,
            params: params as Record<string, string>,
            until: null,
            tone: 'error',
          });
          return { kind: 'refused', messageKey: err.messageKey, params };
        }
        throw err;
      }
    },
    [client, toast],
  );
}

/** Approve, decline or snooze a gate: POST /v1/approvals/{thread_id} (scope hash recorded server-side). */
export function useDecide() {
  const client = useQueryClient();
  const toast = useTurn((s) => s.toast);
  return useCallback(
    async (
      threadId: string,
      decision: 'approve' | 'snooze' | 'edit' | 'decline',
      edits?: Record<string, unknown>,
      decisions?: Record<string, 'approve' | 'snooze' | 'decline'>,
    ) => {
      if (dataMode() === 'fixture') {
        toast({ textKey: `toast.decision_${decision}`, until: null, tone: 'done' });
        return true;
      }
      try {
        await apiPost(
          `/v1/approvals/${threadId}`,
          { decision, ...(edits ? { edits } : {}), ...(decisions ? { decisions } : {}) },
          newIdempotencyKey(),
        );
        void client.invalidateQueries({ queryKey: ['view'] });
        toast({ textKey: `toast.decision_${decision}`, until: null, tone: 'done' });
        return true;
      } catch (err) {
        const key = err instanceof ApiProblem ? err.messageKey : 'toast.needs_network';
        toast({ textKey: key, until: null, tone: 'error' });
        return false;
      }
    },
    [client, toast],
  );
}
