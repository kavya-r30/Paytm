// Turn store (I5): the latest envelope drives the orb, the live-voice strip, cards, chips and nav.
import { create } from 'zustand';
import type { Envelope, Followup } from '../contracts/envelope';

export type Presence = Envelope['presence']['state'];

export type Toast = {
  id: string;
  textKey: string;
  params?: Record<string, string | number>;
  until: number | null;
  commandId?: string;
  undo?: { type: string; payload: Record<string, unknown> };
  tone: 'done' | 'info' | 'error' | 'amber';
};

type TurnState = {
  presence: Presence;
  envelope: Envelope | null;
  live: { active: boolean; heard: string; action: string | null };
  followups: Followup[];
  toasts: Toast[];
  setPresence: (p: Presence) => void;
  applyEnvelope: (e: Envelope) => void;
  startVoice: () => void;
  partial: (heard: string) => void;
  stopVoice: () => void;
  toast: (t: Omit<Toast, 'id'>) => string;
  dismiss: (id: string) => void;
};

let seq = 0;

export const useTurn = create<TurnState>((set) => ({
  presence: 'idle',
  envelope: null,
  live: { active: false, heard: '', action: null },
  followups: [],
  toasts: [],
  setPresence: (presence) => set({ presence }),
  applyEnvelope: (envelope) =>
    set((s) => ({
      envelope,
      presence: envelope.presence.state,
      followups: envelope.followups,
      live: { ...s.live, heard: envelope.caption?.heard ?? s.live.heard },
    })),
  startVoice: () => set({ presence: 'listening', live: { active: true, heard: '', action: null } }),
  partial: (heard) => set((s) => ({ live: { ...s.live, heard } })),
  stopVoice: () => set((s) => ({ presence: 'idle', live: { ...s.live, active: false } })),
  toast: (t) => {
    const id = `t${++seq}`;
    set((s) => ({ toasts: [...s.toasts.slice(-2), { ...t, id }] }));
    return id;
  },
  dismiss: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}));

/** Stream store: recent domain events and spans for the stage's evidence tabs. */
export type StreamItem = { kind: 'event' | 'span'; type: string; at: string; data: Record<string, unknown> };

type StreamState = {
  connected: boolean;
  items: StreamItem[];
  setConnected: (c: boolean) => void;
  push: (i: StreamItem) => void;
};

export const useStream = create<StreamState>((set) => ({
  connected: false,
  items: [],
  setConnected: (connected) => set({ connected }),
  push: (i) => set((s) => ({ items: [i, ...s.items].slice(0, 300) })),
}));
