'use client';

// The stage (I2, STG-MAIN): 1920×1080 fixed, scaled to fit. Device (960×720 ×1.15), phone column with
// persona tabs, customer display, evidence tabs. Each director beat sets the focus (auto-focus).
import { useQuery } from '@tanstack/react-query';
import { Pause, Play } from 'lucide-react';
import { useEffect, useState } from 'react';
import { MiniOrb } from '@/components/arth/orb';
import { FixedCanvas } from '@/components/shell/frame';
import { Money, Pill, cx } from '@/components/ui/kit';
import { API_BASE, sessionToken } from '@/lib/api/client';
import { useDataMode, useView } from '@/lib/api/hooks';
import { STAGE_CHANNEL, type StageFocus } from '@/lib/api/sim';
import { views } from '@/lib/api/views';
import { NATIVE_NAME } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { SCENARIOS } from '@/lib/scenarios';
import { Evidence, type EvidenceTab } from './evidence';

const PERSONAS = ['owner', 'priya', 'mehta', 'balaji', 'chotu'];

/** Iframe that keeps a fixed logical size and scales into its slot. */
function Frame({
  src,
  w,
  h,
  scale,
  title,
}: {
  src: string;
  w: number;
  h: number;
  scale: number;
  title: string;
}) {
  return (
    <div style={{ width: w * scale, height: h * scale }} className="overflow-hidden rounded-card shadow-2">
      <iframe
        src={src}
        title={title}
        style={{ width: w, height: h, transform: `scale(${scale})`, transformOrigin: 'top left', border: 0 }}
      />
    </div>
  );
}

export function StageApp() {
  const { t, locale, time } = useI18n();
  const mode = useDataMode();
  const scenario = SCENARIOS[0]!;
  const [focus, setFocus] = useState<StageFocus>({
    beat: 0,
    scene: scenario.id,
    ...scenario.beats[0]!.focus,
  });
  const [tab, setTab] = useState<EvidenceTab>('trace');
  const [table, setTable] = useState('bills');
  const [persona, setPersona] = useState('owner');
  const [suffix, setSuffix] = useState('');
  const health = useView(views.health());
  const clock = useQuery({
    queryKey: ['healthz'],
    refetchInterval: 5000,
    queryFn: async () => (await (await fetch(`${API_BASE}/healthz`)).json()) as { clock?: string },
  });

  // Same-origin iframes share localStorage, but a stage opened with ?session= passes it on explicitly.
  useEffect(() => {
    const token = sessionToken();
    const params = new URLSearchParams();
    if (token) params.set('session', token);
    params.set('lang', locale);
    setSuffix(`?${params.toString()}`);
  }, [locale]);

  // Auto-focus: each beat (or a director override) sets device screen, persona, evidence tab and table.
  useEffect(() => {
    const ch = new BroadcastChannel(STAGE_CHANNEL);
    ch.onmessage = (e: MessageEvent<StageFocus>) => setFocus(e.data);
    return () => ch.close();
  }, []);
  useEffect(() => {
    if (focus.evidence_tab) setTab(focus.evidence_tab as EvidenceTab);
    if (focus.table) setTable(focus.table);
    if (focus.phone_persona) setPersona(focus.phone_persona);
  }, [focus]);

  // Library beats (L8) carry their own title and cue; the local fallback looks them up by index.
  const local = focus.title ? undefined : scenario.beats[focus.beat];
  const beatTitle = focus.title ?? (local ? t(local.title_key) : '');
  const beatCue = focus.cue ?? (local ? t(local.cue_key) : '');
  const voice = focus.edition === 'voice';
  const providers = health.data?.providers ?? [];
  const replay = providers.some((p) => p.mode !== 'live');

  return (
    <FixedCanvas width={1920} height={1080} className="bg-ground" letterbox="bg-ink">
      <header className="flex h-14 items-center gap-6 bg-midnight px-6 text-white">
        <MiniOrb />
        <span className="text-body font-bold">{focus.scenario_title ?? t(scenario.title_key)}</span>
        <span className="text-meta text-white/70">
          {t('stage.beat', { n: focus.beat + 1, total: focus.total ?? scenario.beats.length })} · {beatTitle}
        </span>
        <span className="num text-meta">
          {t('stage.clock', { time: clock.data?.clock ? time(clock.data.clock) : '—' })}
        </span>
        <Pill tone="sky">{t(voice ? 'stage.edition_voice' : 'stage.edition_display')}</Pill>
        <Pill>{NATIVE_NAME[locale]}</Pill>
        <Pill tone={replay ? 'amber' : 'green'}>{t(replay ? 'stage.ai_replay' : 'stage.ai_live')}</Pill>
        <span className="text-meta">
          {t('health.spend')} <Money paise={health.data?.ai_spend_today_paise ?? 0} />
        </span>
        {mode === 'fixture' && <Pill tone="amber">{t('status.fixture')}</Pill>}
        <span className="ml-auto flex items-center gap-2 text-meta">
          {focus.paused ? <Pause size={16} /> : <Play size={16} />}
          {t(focus.paused ? 'stage.paused' : 'stage.running')}
        </span>
      </header>
      <div className="flex gap-6 p-6">
        <div style={{ width: 1104 }} className="flex flex-col gap-3">
          {voice ? (
            <Frame src={`/device-voice${suffix}`} w={960} h={720} scale={1.15} title="voice" />
          ) : (
            <Frame
              src={`/device/${focus.device_screen ?? 'home'}${suffix}`}
              w={960}
              h={720}
              scale={1.15}
              title="device"
            />
          )}
          {beatCue && (
            <p className="rounded-ground bg-white px-4 py-2 text-body text-ink-2 shadow-1">
              <span className="font-bold text-midnight">{t('stage.cue')} </span>
              {beatCue}
            </p>
          )}
        </div>
        <div style={{ width: 360 }} className="flex flex-col gap-4">
          <div className="flex gap-1">
            {PERSONAS.map((p) => (
              <button
                key={p}
                type="button"
                onClick={() => setPersona(p)}
                className={cx(
                  'flex-1 rounded-chip py-1 text-meta font-bold',
                  p === persona ? 'bg-midnight text-white' : 'bg-white text-ink-2',
                )}
              >
                {t(`stage.persona_${p}`)}
              </button>
            ))}
          </div>
          <Frame src={`/phone/${persona}${suffix}`} w={390} h={693} scale={360 / 390} title="phone" />
          <Frame src={`/customer-display${suffix}`} w={400} h={200} scale={0.9} title="customer display" />
        </div>
        <div style={{ width: 360, height: 1000 }}>
          <Evidence tab={tab} setTab={setTab} table={table} setTable={setTable} />
        </div>
      </div>
    </FixedCanvas>
  );
}
