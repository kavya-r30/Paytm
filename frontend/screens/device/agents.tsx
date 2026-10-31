'use client';

// J6 bound to the L5 agentic layer: SCR-TEAM (helpers, runs, kill switch), SCR-RUN, SCR-MEMORY.
import { Check, CircleDot, Clock3, Pause, Play } from 'lucide-react';
import { MemoryCard } from '@/components/arth/memory';
import { ArthNote, Orb } from '@/components/arth/orb';
import { Empty, Screen, useDeviceNav } from '@/components/shell/device';
import { Button, Card, Pill, SectionTitle, TierChip, cx } from '@/components/ui/kit';
import { useCommand } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import type { MemoryView } from '@/lib/contracts';
import { IDS } from '@/lib/fixtures/gupta';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, field, type ScreenProps } from './common';

const STATUS_DOT: Record<string, string> = {
  working: 'bg-green-fill',
  waiting: 'bg-amber',
  idle: 'bg-line',
  paused: 'bg-red',
};

export function TeamScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.team());
  const pauseAll = (paused: boolean) => void run('agents.pause', { agent: '*', paused });
  return (
    <Screen
      title={t('team.title')}
      sub={t('team.sub')}
      right={
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => nav('trust')}>
            {t('team.activity_log')}
          </Button>
          <Button
            variant={state.data?.kill_switch ? 'primary' : 'dark'}
            size="sm"
            onClick={() => pauseAll(!state.data?.kill_switch)}
          >
            {t(state.data?.kill_switch ? 'team.resume_all' : 'team.pause_all')}
          </Button>
        </div>
      }
      chips={[{ label: t('team.chip_night'), text: 'Kya kya kiya raat ko?' }]}
    >
      <ViewGate state={state}>
        {(v) => (
          <div className="flex flex-col gap-4">
            <ArthNote>
              {t('team.summary', { n: v.summary.done_since_night, k: v.summary.waiting_for_you })}
            </ArthNote>
            {v.kill_switch && <Pill tone="red">{t('team.all_paused')}</Pill>}
            <div className="grid grid-cols-3 gap-3">
              {v.helpers.map((h) => (
                <Card key={h.id} attention={h.pending_gates > 0} className="flex flex-col gap-2 p-4">
                  <div className="flex items-center gap-2">
                    <span className={cx('h-2.5 w-2.5 rounded-chip', STATUS_DOT[h.status] ?? 'bg-line')} />
                    <span className="flex-1 truncate text-body font-bold">{t(h.name_key)}</span>
                    <TierChip tier={h.tier} compact />
                  </div>
                  <p className="line-clamp-2 min-h-[2.5em] text-meta text-ink-2">
                    {h.line ?? t(`team.status_${h.status}`)}
                  </p>
                  <div className="flex items-center justify-between text-meta text-ink-3">
                    <span>{t('team.counts', { gates: h.pending_gates, work: h.open_work })}</span>
                    <button
                      type="button"
                      aria-label={t(h.status === 'paused' ? 'team.resume' : 'team.pause')}
                      onClick={() =>
                        void run('agents.pause', {
                          agent: h.agents[0] ?? h.id,
                          paused: h.status !== 'paused',
                        })
                      }
                      className="rounded-chip bg-ground p-1.5"
                    >
                      {h.status === 'paused' ? <Play size={14} /> : <Pause size={14} />}
                    </button>
                  </div>
                </Card>
              ))}
            </div>
            <Card className="p-5">
              <SectionTitle>{t('team.running')}</SectionTitle>
              {v.runs.length === 0 && <p className="text-meta text-ink-3">{t('team.no_runs')}</p>}
              {v.runs.map((r) => (
                <button
                  key={r.id}
                  type="button"
                  onClick={() => nav(`run/${r.id}`)}
                  className="flex w-full items-center gap-3 border-b border-line py-2.5 text-left"
                >
                  <Orb size={28} state={r.status === 'waiting' ? 'needs_you' : 'thinking'} />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate text-body font-bold">{t(`playbook.${r.playbook}`)}</span>
                    <span className="text-meta text-ink-3">
                      {t(`step.${r.step}`)} · <Subject id={r.subject} />
                    </span>
                  </span>
                  <span className="num text-meta text-ink-3">{time(r.updated_at)}</span>
                </button>
              ))}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

function Subject({ id }: { id: string }) {
  const name = useName(id.includes('_') ? id : null);
  return <span>{name || id}</span>;
}

const STEP_ICON = { done: Check, active: CircleDot, todo: Clock3 } as const;

export function RunScreen({ param }: ScreenProps) {
  const { t, time } = useI18n();
  const run = useCommand();
  const state = useView(views.run(param ?? IDS.RUN_ID));
  return (
    <Screen title={t('run.title')} sub={t('run.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_300px] gap-4">
            <Card className="p-5">
              <SectionTitle
                action={
                  <Pill tone={v.run.status === 'waiting' ? 'amber' : 'sky'}>
                    {t(`run.status_${v.run.status}`)}
                  </Pill>
                }
              >
                {t(`playbook.${v.run.playbook}`)} · <Subject id={v.run.subject} />
              </SectionTitle>
              <ol className="flex flex-col">
                {v.steps.map((s, i) => {
                  const Icon = STEP_ICON[s.status as keyof typeof STEP_ICON] ?? Check;
                  return (
                    <li key={`${s.step}-${i}`} className="flex items-start gap-3 border-b border-line py-2.5">
                      <Icon
                        size={18}
                        className={cx(
                          s.status === 'done'
                            ? 'text-green'
                            : s.status === 'active'
                              ? 'text-amber'
                              : 'text-ink-3',
                        )}
                      />
                      <span className="flex-1 text-body">{t(`step.${s.step}`)}</span>
                      <span className="num text-meta text-ink-3">{time(s.occurred_at)}</span>
                    </li>
                  );
                })}
              </ol>
            </Card>
            <div className="flex flex-col gap-3">
              {v.run.wait && (
                <ArthNote label={false}>
                  {t('run.waiting_on', { topic: String(field(v.run.wait, 'topic', '')) })}
                  {field(v.run.wait, 'until', '') ? ` · ${time(field(v.run.wait, 'until', ''))}` : ''}
                </ArthNote>
              )}
              <Button
                variant="ghost"
                onClick={() => void run('agents.pause', { agent: v.run.agent, paused: true })}
              >
                {t('team.pause')}
              </Button>
              <Button
                variant="ghost"
                onClick={() => void run('agents.pause', { agent: v.run.agent, paused: false })}
              >
                {t('team.resume')}
              </Button>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

type Fact = MemoryView['facts'][number];

/** Facts grouped by who they are about: patrons, suppliers, items, the owner. */
function group(facts: Fact[]): [string, Fact[]][] {
  const by: Record<string, Fact[]> = {};
  for (const f of facts) {
    const kind = f.subject.split('_')[0] ?? 'owner';
    const key =
      kind === 'pat' ? 'patrons' : kind === 'supplier' ? 'suppliers' : kind === 'item' ? 'items' : 'owner';
    (by[key] ??= []).push(f);
  }
  return Object.entries(by);
}

function FactCard({ f }: { f: Fact }) {
  const { t } = useI18n();
  const who = useName(f.subject.includes('_') ? f.subject : null) || f.subject;
  return (
    <MemoryCard
      factId={f.id}
      fact={t('memory.fact', { who, what: t(`predicate.${f.predicate}`), value: f.value })}
      evidence={[...f.evidence, t(`memory.source_${f.source}`)]}
    />
  );
}

export function MemoryScreen(_: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.memory());
  return (
    <Screen title={t('memory.title')} sub={t('memory.sub')}>
      <ViewGate state={state}>
        {(v) => {
          const live = v.facts.filter((f) => f.status === 'active' || f.status === 'unverified');
          if (!live.length) return <Empty title={t('sufficiency.memory_pending')} />;
          return (
            <div className="flex flex-col gap-4">
              {group(live).map(([k, facts]) => (
                <div key={k}>
                  <SectionTitle>{t(`memory.group_${k}`)}</SectionTitle>
                  <div className="grid grid-cols-2 gap-3">
                    {facts.map((f) => (
                      <FactCard key={f.id} f={f} />
                    ))}
                  </div>
                </div>
              ))}
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}
