// Demo scenarios for the director (STG-DIRECTOR) and stage auto-focus (I2). Each beat sets the stage focus,
// optionally drives the simulator, and states what must hold afterwards (same shape as backend scenarios/*.yaml).
import type { StageFocus } from './api/sim';

export type BeatAction =
  | { kind: 'static_pay'; amount_paise: number }
  | { kind: 'inbound'; persona: string; text: string }
  | { kind: 'clock'; advance_minutes: number }
  | { kind: 'fault'; fault: 'duplicate' | 'drop' | 'delay' | 'wrong_amount' };

export type Expect = { view: string; path: string; equals?: unknown; gte?: number };

export type Beat = {
  id: string;
  title_key: string;
  cue_key: string;
  focus: Omit<StageFocus, 'beat' | 'scene'>;
  action?: BeatAction;
  expect?: Expect[];
};

export type Scenario = { id: string; title_key: string; pack: string; beats: Beat[] };

export const SCENARIOS: Scenario[] = [
  {
    id: 'gupta_diwali',
    title_key: 'scenario.gupta',
    pack: 'kirana',
    beats: [
      {
        id: 'morning',
        title_key: 'beat.morning',
        cue_key: 'cue.morning',
        focus: { device_screen: 'home', phone_persona: 'owner', evidence_tab: 'trace', edition: 'display' },
      },
      {
        id: 'bill',
        title_key: 'beat.bill',
        cue_key: 'cue.bill',
        focus: { device_screen: 'bill/new', phone_persona: 'priya', evidence_tab: 'tables', table: 'bills' },
      },
      {
        id: 'pay',
        title_key: 'beat.pay',
        cue_key: 'cue.pay',
        focus: { device_screen: 'home', phone_persona: 'priya', evidence_tab: 'logs' },
        action: { kind: 'static_pay', amount_paise: 9000 },
        expect: [{ view: 'hisaab', path: 'today.sales_paise', gte: 9000 }],
      },
      {
        id: 'order',
        title_key: 'beat.order',
        cue_key: 'cue.order',
        focus: { device_screen: 'orders', phone_persona: 'mehta', evidence_tab: 'tools' },
        action: {
          kind: 'inbound',
          persona: 'mehta',
          text: 'Bhaiya 1 kilo kaju, 2 kilo cheeni, besan ek packet bhej do',
        },
      },
      {
        id: 'stock',
        title_key: 'beat.stock',
        cue_key: 'cue.stock',
        focus: { device_screen: 'stock', phone_persona: 'balaji', evidence_tab: 'playbooks' },
      },
      {
        id: 'khata',
        title_key: 'beat.khata',
        cue_key: 'cue.khata',
        focus: { device_screen: 'khata', phone_persona: 'owner', evidence_tab: 'tables', table: 'khata' },
      },
      {
        id: 'voice',
        title_key: 'beat.voice',
        cue_key: 'cue.voice',
        focus: { device_screen: 'home', phone_persona: 'owner', evidence_tab: 'ai', edition: 'voice' },
      },
      {
        id: 'close',
        title_key: 'beat.close',
        cue_key: 'cue.close',
        focus: {
          device_screen: 'hisaab',
          phone_persona: 'owner',
          evidence_tab: 'health',
          edition: 'display',
        },
        action: { kind: 'clock', advance_minutes: 60 },
        expect: [{ view: 'trust', path: 'audit.ok', equals: true }],
      },
    ],
  },
];

/** Reads a dotted path ("today.sales_paise") from a view body. */
export function at(body: unknown, path: string): unknown {
  return path
    .split('.')
    .reduce<unknown>(
      (v, k) => (v && typeof v === 'object' ? (v as Record<string, unknown>)[k] : undefined),
      body,
    );
}

export function holds(body: unknown, e: Expect): boolean {
  const v = at(body, e.path);
  if (e.gte !== undefined) return typeof v === 'number' && v >= e.gte;
  return v === e.equals;
}
