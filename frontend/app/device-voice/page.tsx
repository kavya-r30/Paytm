'use client';

// Voice edition (I7 VOX): a screenless device with one light bar and one button. Hold to talk; tap reads
// "kya pending hai"; double tap approves what was just read back; long press cancels or stops speaking.
// Pointer, the Space key and a USB button (sends Space/Enter) all drive the same gestures.
import { Mic } from 'lucide-react';
import { useCallback, useEffect, useRef, useState } from 'react';
import { cx } from '@/components/ui/kit';
import { useDecide } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import { useI18n } from '@/lib/i18n/react';
import { useTurnSubmit } from '@/components/shell/device';

type Light = 'idle' | 'listening' | 'thinking' | 'needs_you' | 'done' | 'alert';

const BAR: Record<Light, string> = {
  idle: 'bg-line',
  listening: 'bg-paytm-blue',
  thinking: 'bg-line',
  needs_you: 'bg-amber',
  done: 'bg-green-fill',
  alert: 'bg-red',
};

const HOLD_MS = 300;
const LONG_MS = 1200;
const DOUBLE_MS = 320;

function LightBar({ state }: { state: Light }) {
  return (
    <div className="relative h-3 w-full overflow-hidden rounded-chip bg-line">
      {state === 'thinking' ? (
        <span className="segment absolute top-0 h-full w-1/4 rounded-chip bg-paytm-blue" />
      ) : (
        <span
          className={cx(
            'absolute inset-y-0 left-0 rounded-chip',
            BAR[state],
            state === 'needs_you' ? 'w-1/2' : 'w-full',
          )}
        />
      )}
    </div>
  );
}

function speak(text: string, lang = 'hi-IN', onEnd?: () => void) {
  if (typeof window === 'undefined' || !('speechSynthesis' in window)) {
    onEnd?.();
    return;
  }
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang;
  u.onend = () => onEnd?.();
  window.speechSynthesis.speak(u);
}

export default function VoiceEdition() {
  const { t, money } = useI18n();
  const notif = useView(views.notifications());
  const decide = useDecide();
  const submit = useTurnSubmit();
  const [light, setLight] = useState<Light>('idle');
  const [caption, setCaption] = useState('');
  const [log, setLog] = useState<string[]>([]);
  const down = useRef<number | null>(null);
  const holdTimer = useRef<number | null>(null);
  const lastTap = useRef(0);
  const tapTimer = useRef<number | null>(null);
  const readBack = useRef<string | null>(null);

  const note = (s: string) => setLog((l) => [s, ...l].slice(0, 6));
  const settle = (state: Light, ms = 2500) => {
    setLight(state);
    window.setTimeout(() => setLight('idle'), ms);
  };

  const readPending = useCallback(() => {
    const gates = notif.data?.needs_you ?? [];
    if (!gates.length) {
      const text = t('voice.nothing_pending');
      setCaption(text);
      speak(text, 'hi-IN', () => settle('done', 800));
      return;
    }
    const g = gates[0]!;
    const amount =
      typeof g.summary_params.amount_paise === 'number' ? money(g.summary_params.amount_paise) : '';
    const text = t('voice.read_gate', {
      n: gates.length,
      what: t(g.title_key, { ...g.summary_params, amount }),
      amount,
    });
    readBack.current = g.thread_id;
    setCaption(text);
    setLight('needs_you');
    speak(text);
  }, [notif.data, t, money]);

  const approve = useCallback(async () => {
    const thread = readBack.current;
    if (!thread) {
      note(t('voice.nothing_to_approve'));
      return;
    }
    readBack.current = null;
    setLight('thinking');
    const ok = await decide(thread, 'approve');
    const text = ok ? t('voice.approved') : t('voice.failed');
    setCaption(text);
    speak(text);
    settle(ok ? 'done' : 'alert');
    note(`${t('voice.gesture_double')} → ${text}`);
  }, [decide, t]);

  const cancel = useCallback(() => {
    window.speechSynthesis?.cancel();
    readBack.current = null;
    setCaption(t('voice.cancelled'));
    settle('idle', 300);
    note(t('voice.gesture_long'));
  }, [t]);

  const press = useCallback(() => {
    down.current = Date.now();
    holdTimer.current = window.setTimeout(() => {
      setLight('listening');
      setCaption(t('voice.listening'));
    }, HOLD_MS);
  }, [t]);

  const release = useCallback(() => {
    if (down.current === null) return;
    const held = Date.now() - down.current;
    down.current = null;
    if (holdTimer.current) window.clearTimeout(holdTimer.current);
    if (held >= LONG_MS && light !== 'listening') return cancel();
    if (held >= HOLD_MS) {
      // Hold to talk: the transcript arrives from speech recognition (L4); the demo routes a canned utterance.
      setLight('thinking');
      const heard = t('voice.demo_utterance');
      setCaption(heard);
      note(`${t('voice.gesture_hold')} → “${heard}”`);
      window.setTimeout(() => {
        submit(heard);
        settle('done');
      }, 700);
      return;
    }
    const now = Date.now();
    if (now - lastTap.current < DOUBLE_MS) {
      lastTap.current = 0;
      if (tapTimer.current) window.clearTimeout(tapTimer.current);
      void approve();
      return;
    }
    lastTap.current = now;
    tapTimer.current = window.setTimeout(() => {
      note(t('voice.gesture_tap'));
      readPending();
    }, DOUBLE_MS);
  }, [approve, cancel, light, readPending, submit, t]);

  useEffect(() => {
    const isButton = (e: KeyboardEvent) => e.code === 'Space' || e.code === 'Enter';
    const kd = (e: KeyboardEvent) => {
      if (!isButton(e) || e.repeat) return;
      e.preventDefault();
      press();
    };
    const ku = (e: KeyboardEvent) => {
      if (!isButton(e)) return;
      e.preventDefault();
      release();
    };
    window.addEventListener('keydown', kd);
    window.addEventListener('keyup', ku);
    return () => {
      window.removeEventListener('keydown', kd);
      window.removeEventListener('keyup', ku);
    };
  }, [press, release]);

  return (
    <main className="flex min-h-screen items-center justify-center gap-12 bg-ground p-8">
      <div className="flex h-[420px] w-[340px] flex-col items-center gap-8 rounded-card bg-white px-10 pt-10 shadow-2">
        <LightBar state={light} />
        <div className="grid grid-cols-10 gap-3" aria-hidden>
          {Array.from({ length: 50 }, (_, i) => (
            <span key={i} className="h-1.5 w-1.5 rounded-chip bg-line" />
          ))}
        </div>
        <button
          type="button"
          onPointerDown={press}
          onPointerUp={release}
          onPointerLeave={() => down.current !== null && release()}
          aria-label={t('voice.button')}
          className={cx(
            'flex h-28 w-28 select-none items-center justify-center rounded-chip bg-midnight text-white shadow-2 transition active:scale-95',
            light === 'listening' && 'orb-breathe',
          )}
        >
          <Mic size={40} />
        </button>
      </div>
      <div className="flex w-[360px] flex-col gap-4">
        <h1 className="text-title text-ink">{t('voice.title')}</h1>
        <p className="text-body text-ink-3">{t('voice.sub')}</p>
        <p className="min-h-[72px] rounded-ground bg-white p-4 text-arth text-ink shadow-1">
          {caption || t(`voice.light_${light}`)}
        </p>
        <ul className="grid grid-cols-2 gap-2 text-meta">
          {(['hold', 'tap', 'double', 'long'] as const).map((g) => (
            <li key={g} className="rounded-ground bg-white p-3 shadow-1">
              <span className="block font-bold text-ink">{t(`voice.gesture_${g}`)}</span>
              <span className="text-ink-3">{t(`voice.gesture_${g}_sub`)}</span>
            </li>
          ))}
        </ul>
        <ul className="text-meta text-ink-3">
          {log.map((l, i) => (
            <li key={i}>{l}</li>
          ))}
        </ul>
        <p className="text-meta text-ink-3">{t('voice.fallback')}</p>
      </div>
    </main>
  );
}
