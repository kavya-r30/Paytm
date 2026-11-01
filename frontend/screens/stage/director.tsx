'use client';

// Director (I2 STG-DIRECTOR, T7.16 + T8.7): the presenter's phone. Scenario picker over the backend library
// (`GET /v1/director/scenarios`, local fallback without a backend), "Play" builds the scenario's world, each
// beat runs live in the server with its expectations, a failed beat offers "Restore scene" (snapshot < 3 s).
// Also "Say it for me", persona replies, clock and faults. Beats reach the stage over a BroadcastChannel.
import { useQuery } from '@tanstack/react-query';
import {
  CircleCheck,
  CircleDashed,
  CircleX,
  Clock,
  FastForward,
  Megaphone,
  Play,
  RotateCcw,
  Send,
  Zap,
} from 'lucide-react';
import { useEffect, useRef, useState } from 'react';
import { Button, Card, Chip, Pill, SectionTitle, cx } from '@/components/ui/kit';
import { apiGet } from '@/lib/api/client';
import { useDataMode } from '@/lib/api/hooks';
import {
  STAGE_CHANNEL,
  buildWorld,
  inbound,
  injectFault,
  merchantId,
  moveClock,
  setClockRunning,
  currentPlay,
  playBeat,
  playScenario,
  presenterSessions,
  restoreSnapshot,
  scenarioLibrary,
  staticPay,
  type StageFocus,
} from '@/lib/api/sim';
import { useI18n } from '@/lib/i18n/react';
import { SCENARIOS, fromLibrary, fromLocal, holds, type Beat, type PlayScenario } from '@/lib/scenarios';

type Status = 'todo' | 'running' | 'pass' | 'fail';

export function DirectorApp() {
  const { t } = useI18n();
  const mode = useDataMode();
  const library = useQuery({ queryKey: ['director', 'scenarios'], queryFn: scenarioLibrary, retry: false });
  const all: PlayScenario[] = library.data?.length
    ? library.data.map(fromLibrary)
    : SCENARIOS.map((s) => fromLocal(s, t));
  const [scenarioId, setScenarioId] = useState('gupta_diwali');
  const scenario = all.find((s) => s.id === scenarioId) ?? all[0]!;
  const [playing, setPlaying] = useState<string | null>(null);
  const [recover, setRecover] = useState<string | null>(null);
  const [beat, setBeat] = useState(-1);
  const [status, setStatus] = useState<Record<number, Status>>({});
  const [log, setLog] = useState<string[]>([]);
  const [merchant, setMerchant] = useState<string | null>(null);
  const [reply, setReply] = useState('');
  const [persona, setPersona] = useState('mehta');
  const [paused, setPaused] = useState(false);
  const channel = useRef<BroadcastChannel | null>(null);

  useEffect(() => {
    channel.current = new BroadcastChannel(STAGE_CHANNEL);
    setMerchant(merchantId());
    return () => channel.current?.close();
  }, [mode]);

  // A shop restored by `python dev.py demo` (or played earlier) is ready: pick it up instead of rebuilding.
  useEffect(() => {
    void currentPlay()
      .then(async (p) => {
        if (!p.scenario || !p.merchant_id) return;
        await presenterSessions(p.merchant_id);
        setScenarioId(p.scenario);
        setMerchant(p.merchant_id);
        setPlaying(p.scenario);
        // beats the saved demo already played (Night Shift): shown as passed, Next beat continues after them
        const beats = all.find((s) => s.id === p.scenario)?.beats ?? [];
        const done = beats.map((b, i) => (p.done?.includes(b.id) ? i : -1)).filter((i) => i >= 0);
        if (done.length) {
          setStatus(Object.fromEntries(done.map((i) => [i, 'pass' as Status])));
          setBeat(Math.max(...done));
        }
        setLog((l) => [`${new Date().toLocaleTimeString()} ${t('dir.ready', { id: p.merchant_id })}`, ...l]);
      })
      .catch(() => {});
  }, [t]);

  const say = (s: string) => setLog((l) => [`${new Date().toLocaleTimeString()} ${s}`, ...l].slice(0, 30));
  const send = (focus: StageFocus) => channel.current?.postMessage(focus);

  const focusOf = (i: number, extra: Partial<StageFocus> = {}): StageFocus => {
    const b = scenario.beats[i];
    return {
      beat: i,
      scene: scenario.id,
      paused,
      scenario_title: scenario.title,
      total: scenario.beats.length,
      ...(b ? { title: b.title, cue: b.cue, ...b.focus } : {}),
      ...extra,
    };
  };

  const runAction = async (b: Beat) => {
    if (!b.action || !merchant) return;
    const a = b.action;
    if (a.kind === 'static_pay') await staticPay(merchant, a.amount_paise);
    if (a.kind === 'inbound') await inbound(merchant, a.persona, a.text);
    if (a.kind === 'clock') await moveClock(a.advance_minutes);
    if (a.kind === 'fault') await injectFault(merchant, a.fault);
  };

  const check = async (b: Beat): Promise<boolean> => {
    if (!b.expect?.length || mode === 'fixture') return true;
    for (const e of b.expect) {
      const body = await apiGet(`/v1/views/${e.view}`);
      if (!holds(body, e)) return false;
    }
    return true;
  };

  const go = async (i: number) => {
    const b = scenario.beats[i];
    if (!b) return;
    setBeat(i);
    setStatus((s) => ({ ...s, [i]: 'running' }));
    send(focusOf(i));
    try {
      if (scenario.library && playing === scenario.id) {
        const r = await playBeat(b.id);
        setStatus((s) => ({ ...s, [i]: r.ok ? 'pass' : 'fail' }));
        setRecover(r.ok ? null : r.snapshot);
        say(`${b.id} ${b.title} → ${r.ok ? t('dir.pass_ms', { ms: r.ms ?? 0 }) : r.error}`);
        return;
      }
      if (b.local) await runAction(b.local);
      const ok = b.local ? await check(b.local) : true;
      setStatus((s) => ({ ...s, [i]: ok ? 'pass' : 'fail' }));
      say(`${b.title} → ${ok ? 'pass' : 'fail'}`);
    } catch (e) {
      setStatus((s) => ({ ...s, [i]: 'fail' }));
      say(`${b.title} → ${String(e)}`);
    }
  };

  const play = async () => {
    try {
      say(t('dir.building', { pack: scenario.pack }));
      const started = await playScenario(scenario.id);
      await presenterSessions(started.merchant_id);
      setMerchant(started.merchant_id);
      setPlaying(scenario.id);
      setStatus({});
      setBeat(-1);
      setRecover(null);
      say(t('dir.ready', { id: started.merchant_id }));
    } catch (e) {
      say(`${t('dir.failed')}: ${String(e)}`);
    }
  };

  const restore = async (name: string) => {
    try {
      const r = await restoreSnapshot(name);
      await presenterSessions(merchant ?? undefined);
      setRecover(null);
      const first = scenario.beats.findIndex((b) => name.endsWith(`-scene-${b.scene}`));
      setStatus((s) => Object.fromEntries(Object.entries(s).filter(([k]) => Number(k) < Math.max(first, 0))));
      setBeat(Math.max(first, 0) - 1);
      say(t('dir.restored', { name, ms: r.ms }));
    } catch (e) {
      say(`${t('dir.failed')}: ${String(e)}`);
    }
  };

  const setup = async (pack: string) => {
    try {
      say(t('dir.building', { pack }));
      const manifest = await buildWorld(pack, 30);
      await presenterSessions(manifest.merchant_id);
      setMerchant(manifest.merchant_id);
      say(t('dir.ready', { id: manifest.merchant_id }));
    } catch (e) {
      say(`${t('dir.failed')}: ${String(e)}`);
    }
  };

  const connect = async () => {
    try {
      await presenterSessions(merchant ?? undefined);
      setMerchant(merchantId());
      say(t('dir.connected'));
    } catch (e) {
      say(`${t('dir.failed')}: ${String(e)}`);
    }
  };

  const sayForMe = (b: { cue: string }) => {
    const u = new SpeechSynthesisUtterance(b.cue);
    u.lang = 'hi-IN';
    window.speechSynthesis?.speak(u);
  };

  const Icon = ({ s }: { s: Status | undefined }) =>
    s === 'pass' ? (
      <CircleCheck size={18} className="text-green" />
    ) : s === 'fail' ? (
      <CircleX size={18} className="text-red" />
    ) : (
      <CircleDashed size={18} className={cx('text-ink-3', s === 'running' && 'orb-spin')} />
    );

  return (
    <main className="mx-auto flex min-h-screen max-w-[430px] flex-col gap-3 bg-ground p-4">
      <header className="flex items-center justify-between">
        <h1 className="text-title">{t('dir.title')}</h1>
        <Pill tone={mode === 'live' ? 'green' : 'amber'}>
          {mode === 'live' ? t('dir.live') : t('status.fixture')}
        </Pill>
      </header>

      <Card className="flex flex-col gap-2 p-4">
        <SectionTitle>{t('dir.setup')}</SectionTitle>
        <p className="text-meta text-ink-3">
          {merchant ? t('dir.shop', { id: merchant }) : t('dir.no_shop')}
        </p>
        <div className="flex flex-wrap gap-2">
          {['kirana', 'cafe', 'pharmacy', 'salon'].map((p) => (
            <Chip key={p} onClick={() => void setup(p)}>
              {t(`pack.${p}`)}
            </Chip>
          ))}
        </div>
        <Button variant="ghost" size="sm" onClick={() => void connect()}>
          {t('dir.connect')}
        </Button>
        <a href="/stage" target="_blank" rel="noreferrer" className="text-meta font-bold text-cyan-text">
          {t('dir.open_stage')}
        </a>
      </Card>

      <Card className="flex flex-col gap-2 p-4">
        <SectionTitle>
          <select
            value={scenarioId}
            onChange={(e) => setScenarioId(e.target.value)}
            className="bg-transparent font-bold"
          >
            {all.map((s) => (
              <option key={s.id} value={s.id}>
                {s.title}
              </option>
            ))}
          </select>
        </SectionTitle>
        {scenario.library && (
          <Button
            variant={playing === scenario.id ? 'ghost' : 'tint'}
            size="sm"
            icon={<Play size={16} />}
            onClick={() => void play()}
          >
            {t(playing === scenario.id ? 'dir.replay' : 'dir.play')}
          </Button>
        )}
        {recover && (
          <Button
            variant="tint"
            size="sm"
            className="text-red"
            icon={<RotateCcw size={16} />}
            onClick={() => void restore(recover)}
          >
            {t('dir.restore')}
          </Button>
        )}
        {scenario.beats.map((b, i) => (
          <button
            key={b.id}
            type="button"
            onClick={() => void go(i)}
            className={cx('flex items-start gap-3 rounded-ground p-2 text-left', i === beat && 'bg-sky')}
          >
            <Icon s={status[i]} />
            <span className="min-w-0 flex-1">
              <span className="block text-body font-bold">
                {b.id} · {b.title}
                {b.who ? ` · ${b.who}` : ''}
              </span>
              <span className="block text-meta text-ink-3">{b.cue}</span>
            </span>
          </button>
        ))}
        <div className="flex gap-2">
          <Button
            size="lg"
            className="flex-1"
            icon={<FastForward size={20} />}
            onClick={() => void go(beat + 1)}
            disabled={beat >= scenario.beats.length - 1}
          >
            {t('dir.next')}
          </Button>
          <Button
            variant="tint"
            size="lg"
            icon={<Megaphone size={20} />}
            onClick={() => scenario.beats[Math.max(beat, 0)] && sayForMe(scenario.beats[Math.max(beat, 0)]!)}
          >
            {t('dir.say')}
          </Button>
        </div>
      </Card>

      <Card className="flex flex-col gap-2 p-4">
        <SectionTitle>{t('dir.reply')}</SectionTitle>
        <div className="flex flex-wrap gap-1.5">
          {['mehta', 'priya', 'balaji', 'owner'].map((p) => (
            <Chip key={p} active={persona === p} onClick={() => setPersona(p)}>
              {t(`stage.persona_${p}`)}
            </Chip>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (merchant && reply.trim())
              void inbound(merchant, persona, reply.trim()).then(() => say(`${persona}: ${reply}`));
            setReply('');
          }}
          className="flex gap-2"
        >
          <input
            value={reply}
            onChange={(e) => setReply(e.target.value)}
            placeholder={t('phone.type')}
            className="h-11 flex-1 rounded-ground border border-line px-3 text-body"
          />
          <Button type="submit" icon={<Send size={16} />} disabled={!merchant}>
            {t('phone.send')}
          </Button>
        </form>
      </Card>

      <Card className="flex flex-col gap-2 p-4">
        <SectionTitle>{t('dir.controls')}</SectionTitle>
        <div className="flex flex-wrap gap-2">
          {[15, 60, 24 * 60].map((m) => (
            <Button
              key={m}
              variant="ghost"
              size="sm"
              icon={<Clock size={14} />}
              onClick={() => void moveClock(m).then((r) => say(t('dir.clock', { time: r.clock })))}
            >
              {t(`dir.clock_${m}`)}
            </Button>
          ))}
          {[false, true].map((running) => (
            <Button
              key={String(running)}
              variant="ghost"
              size="sm"
              icon={<Clock size={14} />}
              onClick={() =>
                void setClockRunning(running).then((r) => say(t('dir.clock', { time: r.clock })))
              }
            >
              {t(running ? 'dir.clock_run' : 'dir.clock_freeze')}
            </Button>
          ))}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setPaused(!paused);
              send(focusOf(Math.max(beat, 0), { paused: !paused }));
            }}
          >
            {t(paused ? 'dir.resume' : 'dir.pause')}
          </Button>
        </div>
        <div className="flex flex-wrap gap-2">
          {(['duplicate', 'drop', 'delay', 'wrong_amount'] as const).map((f) => (
            <Button
              key={f}
              variant="ghost"
              size="sm"
              className="text-red"
              icon={<Zap size={14} />}
              disabled={!merchant}
              onClick={() => void injectFault(merchant!, f).then(() => say(t('dir.fault', { f })))}
            >
              {t(`dir.fault_${f}`)}
            </Button>
          ))}
        </div>
        <div className="flex flex-wrap gap-1.5">
          {['home', 'bill/new', 'khata', 'stock', 'grow', 'hisaab', 'trust'].map((s) => (
            <Chip key={s} onClick={() => send(focusOf(Math.max(beat, 0), { device_screen: s }))}>
              {s}
            </Chip>
          ))}
        </div>
        <p className="text-meta text-ink-3">{t('dir.snapshot_note')}</p>
      </Card>

      <ul className="text-meta text-ink-3">
        {log.map((l, i) => (
          <li key={i}>{l}</li>
        ))}
      </ul>
    </main>
  );
}
