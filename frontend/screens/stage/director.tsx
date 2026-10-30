'use client';

// Director (I2 STG-DIRECTOR, T7.16): the presenter's phone. Scenario picker, beats with cues, "Next beat",
// "Say it for me", persona replies, clock, fault injection and assertion status per beat. Uses the director
// token; beats reach the stage over a BroadcastChannel (same browser) and the shared API.
import { CircleCheck, CircleDashed, CircleX, Clock, FastForward, Megaphone, Send, Zap } from 'lucide-react';
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
  presenterSessions,
  staticPay,
  type StageFocus,
} from '@/lib/api/sim';
import { useI18n } from '@/lib/i18n/react';
import { SCENARIOS, holds, type Beat } from '@/lib/scenarios';

type Status = 'todo' | 'running' | 'pass' | 'fail';

export function DirectorApp() {
  const { t } = useI18n();
  const mode = useDataMode();
  const [scenarioId, setScenarioId] = useState(SCENARIOS[0]!.id);
  const scenario = SCENARIOS.find((s) => s.id === scenarioId)!;
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

  const say = (s: string) => setLog((l) => [`${new Date().toLocaleTimeString()} ${s}`, ...l].slice(0, 30));
  const send = (focus: StageFocus) => channel.current?.postMessage(focus);

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
    send({ beat: i, scene: scenario.id, paused, ...b.focus });
    try {
      await runAction(b);
      const ok = await check(b);
      setStatus((s) => ({ ...s, [i]: ok ? 'pass' : 'fail' }));
      say(`${t(b.title_key)} → ${ok ? 'pass' : 'fail'}`);
    } catch (e) {
      setStatus((s) => ({ ...s, [i]: 'fail' }));
      say(`${t(b.title_key)} → ${String(e)}`);
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

  const sayForMe = (b: Beat) => {
    const u = new SpeechSynthesisUtterance(t(b.cue_key));
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
            {SCENARIOS.map((s) => (
              <option key={s.id} value={s.id}>
                {t(s.title_key)}
              </option>
            ))}
          </select>
        </SectionTitle>
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
                {i + 1}. {t(b.title_key)}
              </span>
              <span className="block text-meta text-ink-3">{t(b.cue_key)}</span>
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
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setPaused(!paused);
              send({
                beat: Math.max(beat, 0),
                scene: scenario.id,
                paused: !paused,
                ...(scenario.beats[Math.max(beat, 0)]?.focus ?? {}),
              });
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
            <Chip
              key={s}
              onClick={() => send({ beat: Math.max(beat, 0), scene: scenario.id, device_screen: s })}
            >
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
