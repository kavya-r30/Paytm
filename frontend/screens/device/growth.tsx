'use client';

// J5 · Badhao bound to the L6 growth layer: SCR-GROW, SCR-PLAN, SCR-BUNDLE, SCR-CAMPAIGN, SCR-LEDGER.
import { Gift, Link2, Megaphone, Package, Square, TrendingUp, Users, Wallet } from 'lucide-react';
import { ArthNote } from '@/components/arth/orb';
import { Empty, Screen, useDeviceNav } from '@/components/shell/device';
import { Button, Card, Money, Pill, SectionTitle, TierChip, cx } from '@/components/ui/kit';
import { useCommand } from '@/lib/api/commands';
import { useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import { addItemPayload } from '@/lib/catalog';
import type { CampaignView, GrowView } from '@/lib/contracts';
import { IDS } from '@/lib/fixtures/gupta';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, field, type ScreenProps } from './common';

/** Signed change tile for the gross-profit decomposition (GRW-1), in whole rupees. */
function PartTile({ label, paise }: { label: string; paise: number }) {
  const { money } = useI18n();
  const rupees = Math.round(paise / 100) * 100;
  return (
    <Card className="flex flex-col gap-1 p-4">
      <span className="truncate text-meta text-ink-3">{label}</span>
      <span
        className={cx('num whitespace-nowrap text-xl font-extrabold', paise < 0 ? 'text-red' : 'text-green')}
      >
        {rupees > 0 ? '+' : ''}
        {money(rupees)}
      </span>
    </Card>
  );
}

type PeerMetric = { metric: string; p25: number; p50: number; p75: number; p90: number };

/** Peer bands (p25–p75, median tick) for money metrics; only when the cohort has 10+ shops (GRW-12, AIQ-19). */
function Peers({ peers }: { peers: GrowView['peers'] }) {
  const { t, money } = useI18n();
  const n = field(peers, 'n', 0);
  if (n < 10) return <p className="text-meta text-ink-3">{t('grow.peers_too_few')}</p>;
  const metrics = field<PeerMetric[]>(peers, 'metrics', [])
    .filter((m) => m.metric.endsWith('_paise'))
    .slice(0, 2);
  return (
    <div className="flex flex-col gap-3">
      <span className="text-meta text-ink-3">{t('grow.peer_title', { n })}</span>
      {metrics.map((m) => {
        const span = m.p90 * 1.1 || 1;
        return (
          <div key={m.metric} className="flex flex-col gap-1">
            <div className="flex justify-between text-meta">
              <span className="font-semibold">{t(`peer.${m.metric}`)}</span>
              <span className="num text-ink-3">
                {t('grow.peer_band', { low: money(m.p25), mid: money(m.p50), high: money(m.p75) })}
              </span>
            </div>
            <div className="relative h-2.5 rounded-chip bg-line">
              <span
                className="absolute h-2.5 rounded-chip bg-sky"
                style={{ left: `${(m.p25 / span) * 100}%`, width: `${((m.p75 - m.p25) / span) * 100}%` }}
              />
              <span
                className="absolute -top-1 h-4.5 w-1 rounded-chip bg-midnight"
                style={{ left: `${(m.p50 / span) * 100}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

export function GrowScreen(_: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.grow());
  return (
    <Screen
      title={t('grow.title')}
      sub={t('grow.sub')}
      chips={[
        { label: t('grow.chip_how'), text: 'Bikri kaise badhayein?' },
        { label: t('grow.chip_goal'), text: 'Diwali tak do lakh' },
      ]}
    >
      <ViewGate state={state}>
        {(g) => {
          const plan = g.plans.find((p) => p.status === 'active');
          return (
            <div className="grid grid-cols-[1fr_300px] gap-4">
              <div className="flex flex-col gap-4">
                <Card className="flex flex-col gap-3 p-5">
                  <div className="flex items-end justify-between">
                    <div>
                      <p className="text-body text-ink-3">{t('grow.change_title')}</p>
                      <Money
                        paise={g.diagnostics.change_paise}
                        className={cx(
                          'text-4xl font-extrabold',
                          g.diagnostics.change_paise < 0 ? 'text-red' : 'text-green',
                        )}
                      />
                    </div>
                    <p className="text-meta text-ink-3">
                      {t('grow.customers_visits', {
                        customers: g.diagnostics.current.customers,
                        visits: g.diagnostics.current.visits,
                      })}
                    </p>
                  </div>
                  <div className="grid grid-cols-3 gap-3">
                    <PartTile label={t('grow.part_customers')} paise={g.diagnostics.parts.customers_paise} />
                    <PartTile label={t('grow.part_frequency')} paise={g.diagnostics.parts.frequency_paise} />
                    <PartTile label={t('grow.part_basket')} paise={g.diagnostics.parts.basket_paise} />
                  </div>
                  <Peers peers={g.peers} />
                </Card>
                <Card className="p-5">
                  <SectionTitle>{t('grow.levers')}</SectionTitle>
                  {g.levers.map((l) => (
                    <div key={l.name} className="flex items-center gap-3 border-b border-line py-2.5">
                      <span className="flex-1 text-body font-semibold">{t(`lever.${l.name}`)}</span>
                      <span className="text-meta text-ink-3">{t('grow.eligible', { n: l.eligible })}</span>
                      <Pill tone="sky">
                        ~<Money paise={l.estimate_paise} /> · {t('grow.estimate')}
                      </Pill>
                    </div>
                  ))}
                </Card>
              </div>
              <div className="flex flex-col gap-3">
                {plan ? (
                  <Card attention onClick={() => nav(`plan/${plan.id}`)} className="flex flex-col gap-2 p-5">
                    <SectionTitle action={<Pill tone="green">{t(`plan.status_${plan.status}`)}</Pill>}>
                      {t('grow.plan_running')}
                    </SectionTitle>
                    <p className="text-body font-bold">{t(plan.goal_key)}</p>
                    <p className="text-meta text-ink-3">
                      {plan.levers.map((l) => t(`lever.${l}`)).join(' · ')} ·{' '}
                      <Money paise={plan.budget_paise} />
                    </p>
                  </Card>
                ) : (
                  <Card attention className="flex flex-col gap-3 p-5">
                    <SectionTitle action={<TierChip tier="R3" compact />}>{t('grow.no_plan')}</SectionTitle>
                    <Button
                      onClick={() =>
                        void run('growth.create_plan', {
                          goal_key: 'goal.more_visits',
                          levers: g.levers
                            .filter((l) => l.enabled)
                            .map((l) => l.name)
                            .slice(0, 3),
                          budget_paise: 50000,
                          holdout_bp: 2000,
                        })
                      }
                    >
                      {t('grow.make_plan')}
                    </Button>
                  </Card>
                )}
                {g.advisor.slice(0, 2).map((a) => (
                  <ArthNote key={a.account_id}>
                    <AdvisorLine
                      patron={a.patron_id}
                      from={a.current_limit_paise}
                      to={a.suggested_limit_paise}
                      reason={a.reason_key}
                    />
                  </ArthNote>
                ))}
                {(
                  [
                    ['demand', TrendingUp],
                    ['bundle', Package],
                    ['offers', Gift],
                    ['ledger', Wallet],
                    ['storefront', Link2],
                  ] as const
                ).map(([id, Icon]) => (
                  <Card key={id} onClick={() => nav(id)} className="flex items-center gap-3 p-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-ground bg-sky text-midnight">
                      <Icon size={18} />
                    </span>
                    <span className="text-body font-bold">{t(`grow.link_${id}`)}</span>
                  </Card>
                ))}
              </div>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

function AdvisorLine({
  patron,
  from,
  to,
  reason,
}: {
  patron: string;
  from: number;
  to: number;
  reason: string;
}) {
  const { t, money } = useI18n();
  return (
    <>{t('grow.advisor', { name: useName(patron), from: money(from), to: money(to), why: t(reason) })}</>
  );
}

function CampaignCard({ c }: { c: CampaignView['campaign'] }) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const r = c.result;
  return (
    <Card onClick={() => nav(`campaign/${c.id}`)} className="flex flex-col gap-2 p-4">
      <div className="flex items-center justify-between">
        <span className="flex items-center gap-2 text-body font-bold">
          <Megaphone size={18} /> {t(`lever.${c.lever}`)}
        </span>
        <Pill tone={c.status === 'running' ? 'green' : 'grey'}>{t(`campaign.status_${c.status}`)}</Pill>
      </div>
      <p className="text-meta text-ink-3">
        {t('campaign.counts', { treated: c.treated, holdout: c.holdout, sent: c.sent })}
      </p>
      {field(r, 'returned', -1) >= 0 && (
        <p className="text-meta text-ink-2">{t('campaign.returned', { n: field(r, 'returned', 0) })}</p>
      )}
    </Card>
  );
}

export function PlanScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.plan(param ?? IDS.PLAN_ID));
  return (
    <Screen
      title={t('plan.title')}
      sub={t('plan.sub')}
      chips={[{ label: t('plan.chip_first_two'), text: 'Sirf pehle do' }]}
    >
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_300px] gap-4">
            <div className="flex flex-col gap-3">
              <Card className="flex flex-col gap-2 p-5">
                <SectionTitle action={<Pill tone="green">{t(`plan.status_${v.plan.status}`)}</Pill>}>
                  {t(v.plan.goal_key)}
                </SectionTitle>
                <p className="text-body">
                  {t('plan.scope', {
                    levers: v.plan.levers.map((l) => t(`lever.${l}`)).join(', '),
                    holdout: v.plan.holdout_bp / 100,
                  })}{' '}
                  <Money paise={v.plan.budget_paise} className="font-bold" />
                </p>
                <p className="text-meta text-ink-3">{t('plan.estimate_note')}</p>
              </Card>
              {v.campaigns.map((c) => (
                <CampaignCard key={c.id} c={c} />
              ))}
              {v.campaigns.length === 0 && <Empty title={t('plan.no_campaigns')} />}
            </div>
            <Card attention className="flex flex-col gap-3 self-start p-5">
              <SectionTitle action={<TierChip tier="R3" compact />}>{t('plan.send_title')}</SectionTitle>
              {v.plan.levers.map((l) => (
                <Button
                  key={l}
                  variant="tint"
                  onClick={() =>
                    void run('outreach.send_campaign', {
                      plan_id: v.plan.id,
                      lever: l,
                      template: `outreach.${l}_gentle`,
                    })
                  }
                >
                  {t('plan.send', { lever: t(`lever.${l}`) })}
                </Button>
              ))}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function CampaignScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.campaign(param ?? IDS.CAMPAIGN_ID));
  return (
    <Screen title={t('campaign.title')} sub={t('campaign.sub')}>
      <ViewGate state={state}>
        {(v) => {
          const c = v.campaign;
          const r = c.result;
          const measurable = field(r, 'measurable', false);
          return (
            <div className="grid grid-cols-3 gap-4">
              <Card className="flex flex-col gap-1 p-5">
                <span className="flex items-center gap-2 text-meta text-ink-3">
                  <Users size={16} /> {t('campaign.audience')}
                </span>
                <span className="num text-3xl font-extrabold">{c.treated + c.holdout}</span>
                <span className="text-meta text-ink-3">
                  {t('campaign.treated_holdout', { treated: c.treated, holdout: c.holdout })}
                </span>
              </Card>
              <Card className="flex flex-col gap-1 p-5">
                <span className="text-meta text-ink-3">{t('campaign.sent')}</span>
                <span className="num text-3xl font-extrabold">{c.sent}</span>
                <span className="text-meta text-ink-3">
                  {t('campaign.replied', { n: field(r, 'replied', 0) })} ·{' '}
                  {t('campaign.opted_out', { n: field(r, 'opted_out', 0) })}
                </span>
              </Card>
              <Card className="flex flex-col gap-1 p-5">
                <span className="text-meta text-ink-3">{t('campaign.outcome')}</span>
                <span className="num text-3xl font-extrabold">{field(r, 'returned', 0)}</span>
                <span className="text-meta text-ink-3">
                  {measurable ? t('campaign.uplift_measured') : t('campaign.counts_only')}
                </span>
              </Card>
              <Card className="col-span-3 flex items-center justify-between p-5">
                <span className="text-body">
                  {c.stop_reason ? t(c.stop_reason) : t(`campaign.status_${c.status}`)}
                </span>
                {c.status === 'running' && (
                  <Button
                    variant="danger"
                    icon={<Square size={16} />}
                    onClick={() =>
                      void run('growth.stop_campaign', {
                        campaign_id: c.id,
                        reason_key: 'guardrail.owner_stop',
                      })
                    }
                  >
                    {t('campaign.stop')}
                  </Button>
                )}
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}

export function LedgerScreen(_: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.ledger());
  return (
    <Screen title={t('ledger.title')} sub={t('ledger.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="flex flex-col gap-4">
            <div className="grid grid-cols-3 gap-4">
              {(['measured', 'direct', 'estimated'] as const).map((k) => (
                <Card key={k} className="flex flex-col gap-1 p-5">
                  <Pill tone={k === 'measured' ? 'green' : k === 'direct' ? 'sky' : 'amber'}>
                    {t(`ledger.label_${k}`)}
                  </Pill>
                  <Money paise={v.impact[`${k}_paise`]} className="text-3xl font-extrabold" />
                </Card>
              ))}
            </div>
            <Card className="divide-y divide-line">
              {v.entries.map((e) => (
                <div
                  key={e.campaign_id}
                  className="grid grid-cols-[1fr_140px_120px_120px] items-center gap-3 px-5 py-3 text-body"
                >
                  <span className="font-semibold">{t(`lever.${e.lever}`)}</span>
                  <span className="text-meta text-ink-3">
                    {t('campaign.treated_holdout', { treated: e.treated_n, holdout: e.holdout_n })}
                  </span>
                  <Pill tone={e.label === 'measured' ? 'green' : e.label === 'direct' ? 'sky' : 'amber'}>
                    {t(`ledger.label_${e.label}`)}
                  </Pill>
                  <span className="num text-right">
                    <Money paise={e.direct_paise} /> · −<Money paise={e.reward_cost_paise} />
                  </span>
                </div>
              ))}
              {v.entries.length === 0 && <Empty title={t('ledger.empty')} />}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function BundleScreen(_: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.bundles());
  return (
    <Screen title={t('bundle.title')} sub={t('bundle.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_300px] gap-4">
            <div className="flex flex-col gap-3">
              {v.bundles.map((b, i) => (
                <Card key={i} className="flex flex-col gap-2 p-5">
                  <div className="flex items-center justify-between">
                    <span className="text-body font-bold">{b.names.join(' + ')}</span>
                    <Money paise={b.price_paise} className="text-arth font-extrabold" />
                  </div>
                  <p className="text-meta text-ink-3">
                    {t('bundle.margin', { pct: (b.margin_bp / 100).toFixed(0), n: b.support })}
                  </p>
                  <div className="flex items-center gap-2">
                    <TierChip tier="R2" compact />
                    <Button
                      variant="tint"
                      size="sm"
                      onClick={() =>
                        void run(
                          'catalog.add_item',
                          addItemPayload({
                            name: b.names.join(' + '),
                            pricePaise: b.price_paise,
                            costPaise: Math.round((b.price_paise * (10000 - b.margin_bp)) / 10000),
                            category: 'bundles',
                            recipe: b.items.map((item_id) => ({ item_id, qty_milli: 1000 })),
                          }),
                          { label: b.names.join(' + ') },
                        )
                      }
                    >
                      {t('bundle.set_price')}
                    </Button>
                  </div>
                </Card>
              ))}
              {v.bundles.length === 0 && <Empty title={t('bundle.empty')} />}
            </div>
            <Card className="flex flex-col gap-2 self-start p-5">
              <SectionTitle>{t('bundle.preorders')}</SectionTitle>
              {v.preorders.map((p) => (
                <PreorderRow
                  key={p.id}
                  patron={p.patron_id}
                  total={p.total_paise}
                  deposit={p.deposit_paise}
                  status={p.status}
                />
              ))}
              {v.preorders.length === 0 && <p className="text-meta text-ink-3">{t('bundle.no_preorders')}</p>}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

function PreorderRow({
  patron,
  total,
  deposit,
  status,
}: {
  patron: string;
  total: number;
  deposit: number;
  status: string;
}) {
  const { t, money } = useI18n();
  return (
    <p className="flex justify-between gap-2 border-b border-line py-1.5 text-body">
      <span className="truncate">{useName(patron)}</span>
      <span className="num text-meta text-ink-3">
        {money(total)} · {t('bundle.deposit', { amount: money(deposit) })} · {status}
      </span>
    </p>
  );
}
