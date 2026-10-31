'use client';

// Device shell (I3 geometry): 80 px rail, 76 px header, 32 px content padding, the ask dock at the bottom.
import { Boxes, Home, LayoutGrid, Mic, NotebookPen, ReceiptText, Square, TrendingUp, X } from 'lucide-react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { apiPost, dataMode, newIdempotencyKey } from '@/lib/api/client';
import { useCommand } from '@/lib/api/commands';
import { useDataMode } from '@/lib/api/hooks';
import type { Envelope, LayerPendingView } from '@/lib/contracts';
import { SHORT_NAME } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { useTurn } from '@/lib/store/turn';
import { resolveIntent } from '@/lib/voice/intents';
import { MiniOrb, Orb, Waveform } from '../arth/orb';
import { Avatar, Button, Skeleton, cx } from '../ui/kit';

export const DEVICE_BASE = '/device';

const TABS = [
  { id: 'home', icon: Home, href: 'home', match: ['home', 'ask', 'forecast', 'notifications'] },
  {
    id: 'bill',
    icon: ReceiptText,
    href: 'bill/new',
    match: ['bill', 'park', 'orders', 'order', 'return', 'verdict', 'learn'],
  },
  { id: 'khata', icon: NotebookPen, href: 'khata', match: ['khata', 'patron', 'promises'] },
  {
    id: 'stock',
    icon: Boxes,
    href: 'stock',
    match: ['stock', 'item', 'expiry', 'suppliers', 'po', 'grn', 'claim', 'gate'],
  },
  {
    id: 'grow',
    icon: TrendingUp,
    href: 'grow',
    match: [
      'grow',
      'plan',
      'demand',
      'bundle',
      'offers',
      'offer',
      'campaign',
      'ledger',
      'storefront',
      'capital',
    ],
  },
  { id: 'more', icon: LayoutGrid, href: 'menu', match: [] as string[] },
] as const;

export function useDeviceNav() {
  const router = useRouter();
  return useCallback((path: string) => router.push(`${DEVICE_BASE}/${path}`), [router]);
}

function activeTab(pathname: string): string {
  const seg = pathname.replace(`${DEVICE_BASE}/`, '').split('/')[0] ?? 'home';
  return TABS.find((t) => (t.match as readonly string[]).includes(seg))?.id ?? 'more';
}

export function NavRail() {
  const pathname = usePathname() ?? '';
  const { t, locale, setLocale } = useI18n();
  const presence = useTurn((s) => s.presence);
  const active = activeTab(pathname);
  const [other, setOther] = useState<typeof locale>('en');
  const toggle = () => {
    const next = locale === 'en' ? (other === 'en' ? 'hi-Latn' : other) : 'en';
    setOther(locale);
    setLocale(next);
  };
  return (
    <nav className="flex h-full w-20 shrink-0 flex-col items-center border-r border-line bg-white/60 py-4">
      <Link href={`${DEVICE_BASE}/home`} aria-label={t('nav.home')}>
        <Orb state={presence} size={50} />
      </Link>
      <div className="mt-6 flex flex-col gap-2">
        {TABS.map(({ id, icon: Icon, href }) => (
          <Link
            key={id}
            href={`${DEVICE_BASE}/${href}`}
            className={cx(
              'flex h-[58px] w-[60px] flex-col items-center justify-center gap-0.5 rounded-nav text-meta transition',
              active === id ? 'bg-sky font-bold text-midnight' : 'text-ink-3 hover:bg-white',
            )}
          >
            <Icon size={22} strokeWidth={active === id ? 2.4 : 1.8} />
            <span className="max-w-[56px] truncate">{t(`nav.${id}`)}</span>
          </Link>
        ))}
      </div>
      <div className="mt-auto flex flex-col items-center gap-3">
        <button
          type="button"
          onClick={toggle}
          className="rounded-chip border border-line bg-white px-2.5 py-1 text-meta font-bold text-midnight"
        >
          {SHORT_NAME[locale]} · {SHORT_NAME[locale === 'en' ? (other === 'en' ? 'hi-Latn' : other) : 'en']}
        </button>
        <Link href={`${DEVICE_BASE}/pin`} aria-label={t('nav.who')}>
          <Avatar name="Ramesh" size={40} />
        </Link>
      </div>
    </nav>
  );
}

/** "Arth abhi …" status pill: the most recent active run step (I3 rule 3). */
export function StatusPill({ text }: { text?: string }) {
  const { t } = useI18n();
  const presence = useTurn((s) => s.presence);
  const mode = useDataMode();
  return (
    <div className="flex h-11 max-w-[360px] items-center gap-2.5 rounded-chip bg-white py-1 pl-1.5 pr-4 shadow-1">
      <MiniOrb state={presence} />
      <span className="text-meta text-ink-3">{t('status.arth_now')}</span>
      <span className="truncate text-meta font-bold text-ink">{text ?? t(`presence.${presence}`)}</span>
      {mode === 'fixture' && (
        <span
          className="rounded-chip bg-amber-tint px-2 text-meta font-bold text-amber-text"
          title={t('status.fixture_hint')}
        >
          {t('status.fixture')}
        </span>
      )}
    </div>
  );
}

export function Header({ title, sub, right }: { title: string; sub?: string; right?: ReactNode }) {
  return (
    <header className="flex h-[76px] shrink-0 items-center justify-between gap-4 px-8 pt-2">
      <div className="min-w-0">
        <h1 className="truncate text-title text-ink">{title}</h1>
        {sub && <p className="truncate text-body text-ink-3">{sub}</p>}
      </div>
      <div className="flex shrink-0 items-center gap-2">{right ?? <StatusPill />}</div>
    </header>
  );
}

type SpeechRec = {
  lang: string;
  interimResults: boolean;
  onresult: (e: { results: ArrayLike<ArrayLike<{ transcript: string }>> }) => void;
  onend: () => void;
  start: () => void;
  stop: () => void;
};

/** Dispatches an in-screen action (approve_all, show_qr, …) to whichever screen listens. */
export function emitAction(action: string) {
  window.dispatchEvent(new CustomEvent('arth:action', { detail: action }));
}

export function useAction(handler: (action: string) => void) {
  useEffect(() => {
    const on = (e: Event) => handler((e as CustomEvent<string>).detail);
    window.addEventListener('arth:action', on);
    return () => window.removeEventListener('arth:action', on);
  }, [handler]);
}

/** Text or voice turn. L4 owns real turns; until then the intent table routes locally (voice parity). */
export function useTurnSubmit() {
  const nav = useDeviceNav();
  const toast = useTurn((s) => s.toast);
  const setPresence = useTurn((s) => s.setPresence);
  const { locale } = useI18n();
  const client = useQueryClient();

  const local = useCallback(
    (text: string) => {
      const intent = resolveIntent(text);
      setPresence(intent ? 'done' : 'idle');
      if (!intent) {
        toast({ textKey: 'ask.not_understood', params: { text }, until: null, tone: 'info' });
        return;
      }
      if (intent.screen) nav(intent.screen);
      if (intent.action) emitAction(intent.action);
    },
    [nav, setPresence, toast],
  );

  return useCallback(
    async (text: string) => {
      setPresence('thinking');
      // In-screen actions ("QR dikhao", "Teeno haan") act on what is on screen; they never need a round trip.
      const intent = resolveIntent(text);
      if (dataMode() === 'fixture' || (intent?.action && !intent.screen)) {
        window.setTimeout(() => local(text), 400);
        return;
      }
      try {
        const env = (await apiPost(
          '/v1/turns',
          { text, surface: 'device', lang: locale === 'xx-LONG' ? 'en' : locale },
          newIdempotencyKey(),
        )) as Envelope;
        useTurn.getState().applyEnvelope(env);
        void client.invalidateQueries({ queryKey: ['view', 'ask'] });
        if (env.nav) {
          const param = Object.values(env.nav.params ?? {})[0];
          nav(param ? `${env.nav.screen}/${param}` : env.nav.screen);
        } else if (intent?.screen) nav(intent.screen);
        if (env.speech?.text && 'speechSynthesis' in window) {
          const u = new SpeechSynthesisUtterance(env.speech.text);
          u.lang = env.lang.speech;
          u.onend = () => setPresence('idle');
          window.speechSynthesis.speak(u);
        }
      } catch {
        local(text);
      }
    },
    [client, local, locale, nav, setPresence],
  );
}

export function AskDock({ chips = [] }: { chips?: { label: string; text: string }[] }) {
  const { t, locale } = useI18n();
  const live = useTurn((s) => s.live);
  const followups = useTurn((s) => s.followups);
  const { startVoice, stopVoice, partial } = useTurn.getState();
  const submit = useTurnSubmit();
  const [text, setText] = useState('');
  const [rec, setRec] = useState<SpeechRec | null>(null);

  const allChips = [...followups.map((f) => ({ label: t(f.label_key), text: f.turn_text })), ...chips].slice(
    0,
    3,
  );

  const startMic = () => {
    startVoice();
    const W = window as unknown as {
      SpeechRecognition?: new () => SpeechRec;
      webkitSpeechRecognition?: new () => SpeechRec;
    };
    const Ctor = W.SpeechRecognition ?? W.webkitSpeechRecognition;
    if (!Ctor) return;
    const r = new Ctor();
    r.lang = locale === 'en' ? 'en-IN' : 'hi-IN';
    r.interimResults = true;
    let heard = '';
    r.onresult = (e) => {
      heard = Array.from(e.results)
        .map((res) => res[0]?.transcript ?? '')
        .join(' ');
      partial(heard);
    };
    r.onend = () => {
      stopVoice();
      if (heard) submit(heard);
    };
    r.start();
    setRec(r);
  };
  const stopMic = () => {
    rec?.stop();
    stopVoice();
    if (!rec && live.heard) submit(live.heard);
    setRec(null);
  };

  if (live.active) {
    return (
      <div className="mx-8 mb-5 flex h-[68px] items-center gap-4 rounded-dock bg-midnight py-2 pl-2 pr-2 shadow-2">
        <Orb state="listening" size={52} />
        <p className="min-w-0 flex-1 truncate text-arth text-white">
          {live.heard ? <>…{live.heard}</> : <span className="text-white/60">{t('dock.listening')}</span>}
        </p>
        <Waveform tone="dark" />
        {live.action && (
          <span className="rounded-chip bg-white/10 px-4 py-2 text-body font-semibold text-white">
            ✓ {live.action}
          </span>
        )}
        <button
          type="button"
          onClick={stopMic}
          aria-label={t('dock.stop')}
          className="flex h-[52px] w-[52px] items-center justify-center rounded-chip bg-paytm-blue text-midnight"
        >
          <Square size={20} fill="currentColor" />
        </button>
      </div>
    );
  }

  return (
    <div className="mx-8 mb-5 flex flex-col gap-2">
      {allChips.length > 0 && (
        <div className="no-scrollbar flex gap-2 overflow-x-auto">
          {allChips.map((c) => (
            <button
              key={c.label}
              type="button"
              onClick={() => submit(c.text)}
              className="h-9 shrink-0 rounded-chip border border-line bg-white px-4 text-meta font-bold text-midnight shadow-1"
            >
              {c.label}
            </button>
          ))}
        </div>
      )}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (text.trim()) submit(text.trim());
          setText('');
        }}
        className="flex h-[60px] items-center gap-3 rounded-dock bg-white pl-5 pr-1.5 shadow-1"
      >
        <span className="h-3 w-3 rounded-chip bg-paytm-blue" />
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder={t('dock.placeholder')}
          className="min-w-0 flex-1 bg-transparent text-arth text-ink outline-none placeholder:text-ink-3"
        />
        <button
          type="button"
          onClick={startMic}
          aria-label={t('dock.mic')}
          className="flex h-12 w-12 items-center justify-center rounded-chip bg-paytm-blue text-midnight"
        >
          <Mic size={22} />
        </button>
      </form>
    </div>
  );
}

/** One device screen: header, content area and the ask dock (spec I3 geometry). */
export function Screen({
  title,
  sub,
  right,
  chips,
  dock = true,
  children,
  className,
}: {
  title: string;
  sub?: string;
  right?: ReactNode;
  chips?: { label: string; text: string }[];
  dock?: boolean;
  children: ReactNode;
  className?: string;
}) {
  return (
    <div className="flex h-full min-w-0 flex-1 flex-col">
      <Header title={title} sub={sub} right={right} />
      <main className={cx('no-scrollbar min-h-0 flex-1 overflow-y-auto px-8 pb-4 pt-2', className)}>
        {children}
      </main>
      {dock && <AskDock chips={chips} />}
    </div>
  );
}

/** Centred overlay sheet over the dimmed screen (I3 overlays). */
export function Sheet({
  open,
  onClose,
  children,
  width = 820,
}: {
  open: boolean;
  onClose: () => void;
  children: ReactNode;
  width?: number;
}) {
  const { t } = useI18n();
  if (!open) return null;
  return (
    <div className="absolute inset-0 z-40 flex items-center justify-center bg-ink/40" onClick={onClose}>
      <div
        className="fade-up relative max-h-[640px] overflow-hidden rounded-card bg-white shadow-2"
        style={{ width }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          type="button"
          onClick={onClose}
          aria-label={t('common.close')}
          className="absolute right-4 top-4 z-10 flex h-10 w-10 items-center justify-center rounded-chip bg-ground text-ink-2"
        >
          <X size={20} />
        </button>
        {children}
      </div>
    </div>
  );
}

function useNow(active: boolean) {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    if (!active) return;
    const id = window.setInterval(() => setNow(Date.now()), 500);
    return () => window.clearInterval(id);
  }, [active]);
  return now;
}

/** Undo toast after every self-done action: "… · Wapas lo 0:24" (I3 rule 8). */
export function Toasts() {
  const { t } = useI18n();
  const toasts = useTurn((s) => s.toasts);
  const dismiss = useTurn((s) => s.dismiss);
  const run = useCommand();
  const now = useNow(toasts.length > 0);
  useEffect(() => {
    for (const toast of toasts) {
      const end = toast.until ?? 0;
      const ttl = toast.until ? end : null;
      if (ttl && now > ttl) dismiss(toast.id);
    }
  }, [now, toasts, dismiss]);
  useEffect(() => {
    const timers = toasts.filter((x) => !x.until).map((x) => window.setTimeout(() => dismiss(x.id), 4500));
    return () => timers.forEach((id) => window.clearTimeout(id));
  }, [toasts, dismiss]);
  if (!toasts.length) return null;
  const tone = {
    done: 'bg-midnight text-white',
    info: 'bg-white text-ink',
    error: 'bg-red text-white',
    amber: 'bg-amber-tint text-amber-text border-2 border-amber',
  };
  return (
    <div className="pointer-events-none absolute bottom-24 left-0 right-0 z-50 flex flex-col items-center gap-2">
      {toasts.map((toast) => {
        const left = toast.until ? Math.max(0, Math.ceil((toast.until - now) / 1000)) : null;
        const params = {
          ...toast.params,
          what: toast.params?.what ? t(`cmd.${String(toast.params.what)}`) : '',
        };
        return (
          <div
            key={toast.id}
            className={cx(
              'fade-up pointer-events-auto flex items-center gap-4 rounded-dock px-5 py-3 shadow-2',
              tone[toast.tone],
            )}
          >
            <span className="text-body font-semibold">{t(toast.textKey, params)}</span>
            {toast.undo && left !== null && left > 0 && (
              <button
                type="button"
                className="num rounded-chip bg-white/15 px-3 py-1 text-meta font-bold"
                onClick={() => {
                  dismiss(toast.id);
                  if (toast.undo) void run(toast.undo.type, toast.undo.payload);
                }}
              >
                {t('toast.undo', { s: `0:${String(left).padStart(2, '0')}` })}
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}

/** Shared screen states (J0): loading, error, offline and the layer-pending empty state. */
export function Loading() {
  return (
    <div className="grid grid-cols-5 gap-5">
      <Skeleton className="col-span-3 h-64" />
      <Skeleton className="col-span-2 h-64" />
      <Skeleton className="col-span-5 h-32" />
    </div>
  );
}

export function ErrorState({ error, onRetry }: { error: Error; onRetry?: () => void }) {
  const { t } = useI18n();
  const offline = error.name === 'NetworkError';
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
      <Orb state="alert" size={88} />
      <p className="text-title text-ink">{t(offline ? 'state.offline_title' : 'state.error_title')}</p>
      <p className="max-w-md text-body text-ink-3">
        {t(offline ? 'state.offline_body' : 'state.error_body')}
      </p>
      {onRetry && (
        <Button variant="dark" onClick={onRetry}>
          {t('common.retry')}
        </Button>
      )}
    </div>
  );
}

export function PendingState({ pending, icon }: { pending: LayerPendingView; icon?: ReactNode }) {
  const { t } = useI18n();
  return (
    <div className="flex h-full flex-col items-center justify-center gap-4 px-16 text-center">
      {icon ?? <Orb state="thinking" size={96} />}
      <p className="text-title text-ink">{t(pending.reason_key)}</p>
      <p className="max-w-lg text-body text-ink-3">{t('state.pending_body', { layer: pending.layer })}</p>
    </div>
  );
}

export function Empty({ title, body, action }: { title: string; body?: string; action?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10 text-center">
      <Orb state="done" size={64} />
      <p className="text-arth font-semibold text-ink">{title}</p>
      {body && <p className="max-w-md text-body text-ink-3">{body}</p>}
      {action}
    </div>
  );
}
