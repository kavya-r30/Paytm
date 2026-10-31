'use client';

// J1 · Aaj: SCR-HOME, SCR-ASK, SCR-FORECAST, SCR-NOTIF.
import { BellRing, Check, Clock3, MessageSquare, Truck, Undo2, Users, Volume2 } from 'lucide-react';
import { useCallback, useState } from 'react';
import { ArthNote, Orb, ProvenanceChips, Waveform } from '@/components/arth/orb';
import { Donut, LineBand, MiniBars, SERIES, Sparkline } from '@/components/ui/charts';
import { Button, Card, Chip, Money, Pill, SectionTitle, TierChip, cx } from '@/components/ui/kit';
import { CardStack } from '@/components/cards/registry';
import { Empty, Screen, StatusPill, useAction, useDeviceNav, useTurnSubmit } from '@/components/shell/device';
import { useCommand, useDecide } from '@/lib/api/commands';
import { apiPost } from '@/lib/api/client';
import { useDataMode, useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import type { ForecastView, HomeView, NotificationsView } from '@/lib/contracts';
import { useI18n } from '@/lib/i18n/react';
import { useTurn } from '@/lib/store/turn';
import { ViewGate, field, type ScreenProps } from './common';

const GATE_ICON: Record<string, typeof Truck> = { message: MessageSquare, truck: Truck, users: Users };
const ICON_BY_DOMAIN: Record<string, string> = { ledger: 'message', supply: 'truck', growth: 'users' };

type Gate = HomeView['gates'][number];

/** Gate row text computed from the gate's scope (J1 binding fix): title_key + summary_params from the view. */
export function useGateText() {
  const { t, money } = useI18n();
  return (g: Pick<Gate, 'type' | 'title_key' | 'summary_params'>) => {
    const p = g.summary_params;
    const amount = typeof p.amount_paise === 'number' ? money(p.amount_paise) : null;
    const params = { ...p, amount: amount ?? '' };
    const title = t(g.title_key, params);
    const sub = [p.supplier, p.patron, p.item, amount]
      .filter((x) => x !== null && x !== undefined && x !== '')
      .join(' · ');
    return {
      title: title === g.title_key ? t(`gate_type.${g.type}`) : title,
      sub: sub || t('gate.tap_for_scope'),
      icon: ICON_BY_DOMAIN[g.type.split('.')[0] ?? ''] ?? 'message',
    };
  };
}

type Intraday = {
  hours: number[];
  today: (number | null)[];
  typical: (number | null)[];
  band_low: (number | null)[];
  band_high: (number | null)[];
  pin?: { hour: number; note: string };
};

function BriefCard({ brief }: { brief: HomeView['brief'] }) {
  const { t } = useI18n();
  const submit = useTurnSubmit();
  const [playing, setPlaying] = useState(false);
  const { money } = useI18n();
  // Night Shift writes structured numbers; the sentence comes from the catalogue (no literal copy).
  const sales = field(brief, 'sales_paise', -1);
  const typical = field(brief, 'typical_paise', 0);
  const composed =
    sales >= 0
      ? t(typical ? 'home.brief_compose' : 'home.brief_compose_no_typical', {
          sales: money(sales),
          delta: typical ? Math.round(((sales - typical) / typical) * 100) : 0,
          khata: money(field(brief, 'khata_due_paise', 0)),
        })
      : '';
  const text = field(brief, 'text', '') || composed;
  const duration = field(brief, 'duration_s', Math.min(12, Math.ceil(text.length / 14)));
  if (!text) return null;
  const speak = () => {
    setPlaying(true);
    if ('speechSynthesis' in window) {
      const u = new SpeechSynthesisUtterance(text);
      u.lang = 'hi-IN';
      u.onend = () => setPlaying(false);
      window.speechSynthesis.speak(u);
    } else globalThis.setTimeout(() => setPlaying(false), 2000);
  };
  return (
    <div className="flex gap-5 rounded-card border border-paytm-blue/20 bg-sky/70 px-5 py-4 shadow-1">
      <Orb state={playing ? 'speaking' : 'idle'} size={60} className="mt-1" />
      <div className="min-w-0 flex-1">
        <p className="line-clamp-2 text-lg leading-snug text-ink">{text}</p>
        <div className="mt-2.5 flex items-center gap-3">
          <button
            type="button"
            onClick={speak}
            className="flex h-10 shrink-0 items-center gap-2 whitespace-nowrap rounded-chip bg-midnight pl-1.5 pr-4 text-meta font-bold text-white"
          >
            <span className="flex h-8 w-8 items-center justify-center rounded-chip bg-paytm-blue text-midnight">
              <Volume2 size={16} />
            </span>
            {t(playing ? 'home.brief_playing' : 'home.brief_play')}
          </button>
          <Waveform active={playing} bars={22} />
          <span className="num text-meta text-ink-3">0:{String(duration).padStart(2, '0')}</span>
          <div className="ml-auto flex gap-2">
            {['home.chip_why', 'home.chip_evening'].map((k) => (
              <Chip key={k} tone="sky" onClick={() => submit(t(k))}>
                {t(k)}
              </Chip>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function SalesChart({ home }: { home: HomeView }) {
  const { t, money } = useI18n();
  const intraday = field<Intraday | null>(home.brief, 'intraday', null);
  const delta = field(home.brief, 'delta_bp', 0);
  if (home.data_sufficiency.status === 'cold_start' || !intraday) {
    return (
      <Card className="flex flex-col justify-center gap-3 p-6">
        <SectionTitle>{t('home.sales_title')}</SectionTitle>
        <Money paise={home.today.sales_paise} className="text-4xl font-extrabold leading-none" />
        <ArthNote>{t('home.cold_start', { days: home.data_sufficiency.days_of_history })}</ArthNote>
      </Card>
    );
  }
  const labels = intraday.hours.map((h) =>
    h === 12 ? '12' : h > 12 ? `${h - 12}${h === 14 ? 'pm' : ''}` : `${h}${h === 8 ? 'am' : ''}`,
  );
  const pinIndex = intraday.pin ? intraday.hours.indexOf(intraday.pin.hour) : undefined;
  return (
    <Card className="relative px-5 py-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-body text-ink-3">{t('home.sales_title')}</p>
          <div className="mt-1 flex items-center gap-3">
            <Money paise={home.today.sales_paise} className="text-4xl font-extrabold leading-none" />
            {delta !== 0 && (
              <Pill tone={delta > 0 ? 'green' : 'red'}>
                {delta > 0 ? '▲' : '▼'} {Math.abs(delta / 100)}%
              </Pill>
            )}
          </div>
        </div>
        <ul className="space-y-1 text-meta text-ink-2">
          <li className="flex items-center gap-2">
            <span className="h-1 w-5 rounded-chip bg-midnight" />
            {t('home.legend_today')}
          </li>
          <li className="flex items-center gap-2">
            <span className="h-0.5 w-5 border-t-2 border-dashed border-ink-3" />
            {t('home.legend_typical')}
          </li>
          <li className="flex items-center gap-2">
            <span className="h-2.5 w-5 rounded-chip bg-sky" />
            {t('home.legend_forecast')}
          </li>
        </ul>
      </div>
      {intraday.pin && (
        <div className="absolute left-40 top-[78px] z-10 flex max-w-[300px] items-start gap-2 rounded-ground border-l-4 border-amber bg-white p-3 shadow-2">
          <Orb size={26} />
          <p className="text-meta font-semibold leading-snug text-ink">{intraday.pin.note}</p>
        </div>
      )}
      <div className="mt-2">
        <LineBand
          labels={labels}
          actual={intraday.today}
          typical={intraday.typical}
          low={intraday.band_low}
          high={intraday.band_high}
          pinIndex={pinIndex}
          height={120}
          yFormat={(v) =>
            v === 0 ? '0' : money(Math.round(v), true).replace('.00', '').replace(/,000$/, 'k')
          }
        />
      </div>
    </Card>
  );
}

function Kpis({ home }: { home: HomeView }) {
  const { t } = useI18n();
  const modes = Object.entries(home.today.by_mode);
  const total = modes.reduce((s, [, v]) => s + v, 0) || 1;
  return (
    <div className="grid grid-cols-3 gap-4">
      <Card className="px-5 py-3.5">
        <p className="truncate text-meta text-ink-3">{t('home.kpi_mix')}</p>
        <div className="mt-2 flex items-center gap-3">
          <Donut parts={modes.map(([, v], i) => ({ value: v, color: SERIES[i]! }))} size={52} stroke={9} />
          <ul className="space-y-0.5 text-meta font-semibold">
            {modes.map(([mode, v], i) => (
              <li key={mode} className="flex items-center gap-1.5 whitespace-nowrap">
                <span className="h-2.5 w-2.5 rounded-chip" style={{ background: SERIES[i] }} />
                {t(`pay.${mode}`)} {Math.round((v / total) * 100)}%
              </li>
            ))}
          </ul>
        </div>
      </Card>
      <Card className="px-5 py-3.5">
        <div className="flex justify-between gap-2">
          <p className="truncate text-meta text-ink-3">{t('home.kpi_customers')}</p>
          <span className="shrink-0 text-meta font-bold text-cyan-text">
            {t('home.kpi_new', { n: home.today.new_customers })}
          </span>
        </div>
        <div className="mt-2 flex items-end justify-between">
          <span className="num text-3xl font-extrabold leading-none">{home.today.customers}</span>
          <MiniBars values={[22, 30, 18, 34, 26, home.today.customers]} width={90} height={34} />
        </div>
      </Card>
      <Card className="px-5 py-3.5">
        <div className="flex justify-between gap-2">
          <p className="truncate text-meta text-ink-3">{t('home.kpi_khata')}</p>
          {home.khata.change_today_paise !== 0 && (
            <Money paise={home.khata.change_today_paise} className="shrink-0 text-meta font-bold text-red" />
          )}
        </div>
        <div className="mt-2 flex items-end justify-between">
          <Money paise={home.khata.outstanding_paise} className="text-2xl font-extrabold leading-none" />
          <Sparkline values={[7, 6.5, 6.8, 6, 5.6, 5.4, 5]} />
        </div>
      </Card>
    </div>
  );
}

/** Batch card: today's pending gates with one decision (WFL-4). Each gate keeps its own tier. */
function BatchCard({ gates }: { gates: Gate[] }) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const decide = useDecide();
  const text = useGateText();
  const [done, setDone] = useState(false);
  const mode = useDataMode();
  const approveAll = useCallback(async () => {
    // WFL-4: one thread for the batch (POST /v1/work/batches); each gate still keeps its own tier server-side.
    if (mode === 'live') {
      try {
        const { thread_id } = (await apiPost('/v1/work/batches', {
          gate_ids: gates.map((g) => g.gate_id),
        })) as {
          thread_id: string;
        };
        await decide(thread_id, 'approve');
        setDone(true);
        return;
      } catch {
        // fall through: approve one by one
      }
    }
    for (const g of gates) await decide(g.thread_id, 'approve');
    setDone(true);
  }, [gates, decide, mode]);
  useAction(
    useCallback(
      (a: string) => {
        if (a === 'approve_all') void approveAll();
      },
      [approveAll],
    ),
  );
  if (!gates.length || done) {
    return (
      <Card className="flex h-full flex-col items-center justify-center p-6">
        <Empty title={t('home.batch_empty')} body={t('home.batch_empty_next')} />
      </Card>
    );
  }
  const needsReadback = gates.some((g) => g.tier === 'R2');
  return (
    <Card attention className="flex h-full flex-col p-5">
      <div className="flex items-center gap-3">
        <Orb size={40} state="needs_you" />
        <h2 className="text-arth font-bold leading-tight text-ink">
          {t('home.batch_title', { n: gates.length })}
        </h2>
      </div>
      <p className="mt-1 truncate text-meta text-ink-3">{t('home.batch_sub')}</p>
      <ul className="mt-2 flex-1 divide-y divide-line">
        {gates.slice(0, 4).map((g) => {
          const g2 = text(g);
          const Icon = GATE_ICON[g2.icon] ?? MessageSquare;
          return (
            <li key={g.gate_id}>
              <button
                type="button"
                onClick={() => nav(`gate/${g.gate_id}`)}
                className="flex w-full items-center gap-3 py-2 text-left"
              >
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-ground bg-ground text-midnight">
                  <Icon size={22} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-body font-bold text-ink">{g2.title}</span>
                  <span className="flex items-center gap-2">
                    <TierChip tier={g.tier} compact />
                    <span className="truncate text-meta text-ink-3">{g2.sub}</span>
                  </span>
                </span>
                <Check size={20} className="shrink-0 text-paytm-blue" />
              </button>
            </li>
          );
        })}
      </ul>
      {needsReadback && <p className="mb-2 text-meta text-amber-text">{t('home.batch_readback')}</p>}
      <Button onClick={approveAll} className="w-full">
        {t('home.batch_approve', { n: gates.length })}
      </Button>
      <Button
        variant="ghost"
        size="md"
        className="mt-2 w-full"
        onClick={() => nav(`gate/${gates[0]!.gate_id}`)}
      >
        {t('home.batch_one_by_one')}
      </Button>
    </Card>
  );
}

export function HomeScreen(_: ScreenProps) {
  const { t, day, time } = useI18n();
  const state = useView(views.home());
  const g = state.data?.greeting;
  return (
    <Screen
      title={g ? t(`home.greeting_${g.part_of_day}`, { name: g.owner_name }) : t('nav.home')}
      sub={g ? `${g.shop_name} · ${day(g.now)} · ${time(g.now)}` : undefined}
      right={<StatusPill text={state.mode === 'fixture' ? t('home.status_example') : undefined} />}
    >
      <ViewGate state={state}>
        {(home) => (
          <div className="flex flex-col gap-3">
            <BriefCard brief={home.brief} />
            <div className="grid grid-cols-5 gap-4">
              <div className="col-span-3 flex flex-col gap-4">
                <SalesChart home={home} />
                <Kpis home={home} />
              </div>
              <div className="col-span-2">
                <BatchCard gates={home.gates} />
              </div>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

/** SCR-ASK: the question, the grounded answer with its cards and provenance, earlier turns collapsed above. */
export function AskScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const state = useView(views.ask());
  const envelope = useTurn((s) => s.envelope);
  const presence = useTurn((s) => s.presence);
  return (
    <Screen
      title={t('ask.title')}
      sub={t('ask.sub')}
      chips={[{ label: t('ask.chip_yesterday'), text: 'Aur kal ka?' }]}
    >
      <ViewGate state={state}>
        {(v) => {
          const turns = [...v.turns].sort((a, b) => a.created_at.localeCompare(b.created_at));
          const last = turns[turns.length - 1];
          return (
            <div className="grid grid-cols-[1fr_280px] gap-4">
              <div className="flex flex-col gap-3">
                {turns.slice(0, -1).map((turn) => (
                  <p
                    key={turn.id}
                    className="truncate rounded-ground bg-white/60 px-4 py-2 text-meta text-ink-3"
                  >
                    “{turn.heard}” → {turn.said}
                  </p>
                ))}
                {last && (
                  <>
                    <p className="self-end rounded-card bg-midnight px-5 py-3 text-arth text-white">
                      🎙 {envelope?.caption?.heard ?? last.heard}
                    </p>
                    <Card className="flex flex-col gap-3 p-5">
                      <div className="flex items-start gap-3">
                        <Orb state={presence === 'thinking' ? 'thinking' : 'speaking'} size={44} />
                        <p className="text-arth leading-snug text-ink">
                          {envelope?.speech?.text ?? last.said}
                        </p>
                      </div>
                      {envelope && <CardStack envelope={envelope} audience="owner" />}
                      <ProvenanceChips
                        items={envelope?.provenance ?? [{ kind: 'bills', count: 31 }, { kind: 'upi_ledger' }]}
                      />
                      <span className="text-meta text-ink-3">{time(last.created_at)}</span>
                    </Card>
                  </>
                )}
                {!last && <ArthNote>{t('ask.empty')}</ArthNote>}
              </div>
              <div className="flex flex-col gap-3">
                <SectionTitle>{t('ask.also_noticed')}</SectionTitle>
                <ArthNote label={false}>{t('ask.nudge_example')}</ArthNote>
              </div>
            </div>
          );
        }}
      </ViewGate>
      <p className="mt-2 text-center text-meta text-ink-3">{t('ask.privacy')}</p>
    </Screen>
  );
}

function ForecastBody({ f }: { f: ForecastView }) {
  const { t, money, date } = useI18n();
  const nav = useDeviceNav();
  const today = f.days[0];
  const poor = (f.accuracy.wape_bp ?? 0) > 3500;
  const labels = [
    ...f.actuals.map((a) => date(`${a.date}T06:00:00Z`)),
    ...f.days.map((d) => date(`${d.date}T06:00:00Z`)),
  ];
  const n = f.actuals.length;
  const pad = (k: number) => Array<number | null>(k).fill(null);
  if (f.status === 'needs_more_data' || !today)
    return <ArthNote>{t('sufficiency.forecast_pending')}</ArthNote>;
  return (
    <div className="grid grid-cols-[1fr_300px] gap-4">
      <div className="flex flex-col gap-4">
        <Card className="p-5">
          <p className="text-body text-ink-3">{t('forecast.headline')}</p>
          <Money paise={today.p50_paise} className="text-4xl font-extrabold" />
          <p className="text-body text-ink-2">
            {t('forecast.range', { low: money(today.p10_paise), high: money(today.p90_paise) })}
          </p>
          {poor && <Pill tone="amber">{t('forecast.poor_accuracy')}</Pill>}
          <LineBand
            labels={labels}
            actual={[...f.actuals.map((a) => a.sales_paise), ...pad(f.days.length)]}
            low={[...pad(n - 1), f.actuals[n - 1]?.sales_paise ?? null, ...f.days.map((d) => d.p10_paise)]}
            high={[...pad(n - 1), f.actuals[n - 1]?.sales_paise ?? null, ...f.days.map((d) => d.p90_paise)]}
            typical={[
              ...pad(n - 1),
              f.actuals[n - 1]?.sales_paise ?? null,
              ...f.days.map((d) => d.p50_paise),
            ]}
            height={170}
            yFormat={(v) => money(Math.round(v), true)}
          />
        </Card>
        <p className="text-meta text-ink-3">
          {t('forecast.accuracy', { k: f.accuracy.within_band, n: f.accuracy.window_days })}
        </p>
      </div>
      <div className="flex flex-col gap-3">
        <Card className="p-5">
          <SectionTitle>{t('forecast.why')}</SectionTitle>
          {f.drivers.map((d) => (
            <p key={d.key} className="flex justify-between border-b border-line py-2 text-body">
              <span>{t(d.key)}</span>
              <Money
                paise={d.contribution_paise}
                className={d.contribution_paise < 0 ? 'text-red' : 'text-green'}
              />
            </p>
          ))}
        </Card>
        {f.items.length > 0 && (
          <Card className="p-5">
            <SectionTitle>{t('forecast.items')}</SectionTitle>
            {f.items.map((i) => (
              <p key={i.item_id} className="flex justify-between text-body">
                <span className="truncate">{i.name}</span>
                <span className="num">{i.horizon_qty_milli / 1000}</span>
              </p>
            ))}
          </Card>
        )}
        <Button onClick={() => nav('stock')}>{t('forecast.cta', { festival: t('festival.diwali') })}</Button>
      </div>
    </div>
  );
}

export function ForecastScreen(_: ScreenProps) {
  const { t } = useI18n();
  const [metric, setMetric] = useState<'sales' | 'items'>('sales');
  const state = useView(views.forecast(metric));
  return (
    <Screen
      title={t('forecast.title')}
      sub={t('forecast.sub', { festival: t('festival.diwali'), n: 10 })}
      right={
        <div className="flex gap-2">
          {(['sales', 'items'] as const).map((m) => (
            <Chip key={m} active={metric === m} onClick={() => setMetric(m)}>
              {t(`forecast.metric_${m}`)}
            </Chip>
          ))}
        </div>
      }
      chips={[{ label: t('forecast.chip_tomorrow'), text: 'Kal kitni bikri hogi?' }]}
    >
      <ViewGate state={state}>{(f) => <ForecastBody f={f} />}</ViewGate>
    </Screen>
  );
}

function DoneRow({ d }: { d: NotificationsView['done'][number] }) {
  const { t, time } = useI18n();
  const run = useCommand();
  const open = d.undo_until && Date.parse(d.undo_until) > Date.now();
  return (
    <li className="flex items-center gap-4 py-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-ground bg-green-tint text-green">
        <Check size={18} />
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-body font-semibold">{t(`cmd.${d.type}`)}</span>
        <span className="num text-meta text-ink-3">{time(d.occurred_at)}</span>
      </span>
      <TierChip tier={d.tier} />
      {open && (
        <Button
          variant="tint"
          size="sm"
          icon={<Undo2 size={16} />}
          onClick={() => void run('counter.undo', { command_id: d.command_id })}
        >
          {t('notif.undo')}
        </Button>
      )}
    </li>
  );
}

export function NotificationsScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const nav = useDeviceNav();
  const text = useGateText();
  const state = useView(views.notifications());
  return (
    <Screen
      title={t('notif.title')}
      sub={t('notif.sub')}
      chips={[{ label: t('notif.chip_pending'), text: 'Kya pending hai?' }]}
    >
      <ViewGate state={state}>
        {(n) => (
          <div className="grid grid-cols-2 gap-5">
            <Card className="p-6" attention={n.needs_you.length > 0}>
              <SectionTitle>
                <span className="flex items-center gap-2">
                  <BellRing size={18} /> {t('notif.needs_you', { n: n.needs_you.length })}
                </span>
              </SectionTitle>
              {n.needs_you.length === 0 && <Empty title={t('notif.none')} />}
              <ul className="divide-y divide-line">
                {n.needs_you.map((g) => (
                  <li key={g.gate_id}>
                    <button
                      type="button"
                      onClick={() => nav(`gate/${g.gate_id}`)}
                      className="flex w-full items-center gap-3 py-3 text-left"
                    >
                      <span className="min-w-0 flex-1">
                        <span className="block truncate text-body font-bold">{text(g).title}</span>
                        <span className="block truncate text-meta text-ink-3">{text(g).sub}</span>
                      </span>
                      <TierChip tier={g.tier} />
                    </button>
                  </li>
                ))}
              </ul>
            </Card>
            <div className="flex flex-col gap-5">
              <Card className="p-6">
                <SectionTitle>{t('notif.done_by_arth')}</SectionTitle>
                <ul className="divide-y divide-line">
                  {n.done.map((d) => (
                    <DoneRow key={d.command_id} d={d} />
                  ))}
                </ul>
              </Card>
              {n.snoozed.length > 0 && (
                <Card className="p-6">
                  <SectionTitle>{t('notif.snoozed')}</SectionTitle>
                  {n.snoozed.map((g) => (
                    <div key={g.gate_id} className="flex items-center gap-3 py-2">
                      <Clock3 size={18} className="text-ink-3" />
                      <span className="flex-1 text-body">{t(`gate_type.${g.type}`)}</span>
                      <span className={cx('num text-meta text-ink-3')}>
                        {t('notif.back_at', { time: time(g.expires_at) })}
                      </span>
                    </div>
                  ))}
                </Card>
              )}
              <ProvenanceChips items={[{ kind: 'audit', count: n.done.length }]} />
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}
