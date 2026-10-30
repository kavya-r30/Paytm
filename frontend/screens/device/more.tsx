'use client';

// J6 · More: SCR-MENU, SCR-TEAM, SCR-RUN, SCR-MEMORY, SCR-HISAAB, SCR-REPORTS, SCR-FEEDBACK, SCR-LANG,
// SCR-STAFF, SCR-TRUST, SCR-HEALTH, SCR-CAPITAL.
import {
  BarChart3,
  Bot,
  Brain,
  Calculator,
  CircleCheck,
  Cpu,
  FileText,
  Gift,
  HeartPulse,
  Landmark,
  Languages,
  Link2,
  MessageSquareHeart,
  ShieldCheck,
  Smartphone,
  Sparkles,
  Star,
  Truck,
  Users,
  Volume2,
} from 'lucide-react';
import { useState } from 'react';
import { ArthNote, Orb } from '@/components/arth/orb';
import { Screen, useDeviceNav } from '@/components/shell/device';
import { Button, Card, Chip, Money, Pill, SectionTitle, TierChip, Toggle, cx } from '@/components/ui/kit';
import { apiGet } from '@/lib/api/client';
import { useCommand } from '@/lib/api/commands';
import { useDataMode, useView } from '@/lib/api/hooks';
import { useName } from '@/lib/api/names';
import { views } from '@/lib/api/views';
import type { AuditVerification } from '@/lib/contracts';
import { NATIVE_NAME, UI_LOCALES, isUiLocale, type UiLocale } from '@/lib/i18n/core';
import { useI18n } from '@/lib/i18n/react';
import { ViewGate, field, type ScreenProps } from './common';

const TILES = [
  { id: 'forecast', icon: Sparkles },
  { id: 'offers', icon: Gift },
  { id: 'team', icon: Bot },
  { id: 'ask', icon: MessageSquareHeart },
  { id: 'suppliers', icon: Truck },
  { id: 'hisaab', icon: Calculator },
  { id: 'reports', icon: FileText },
  { id: 'feedback', icon: Star },
  { id: 'storefront', icon: Link2 },
  { id: 'health', icon: Smartphone },
  { id: 'language', icon: Languages },
  { id: 'staff', icon: Users },
  { id: 'trust', icon: ShieldCheck },
  { id: 'memory', icon: Brain },
  { id: 'capital', icon: Landmark },
  { id: 'orders', icon: BarChart3 },
] as const;

export function MenuScreen(_: ScreenProps) {
  const { t, locale } = useI18n();
  const nav = useDeviceNav();
  const notif = useView(views.notifications());
  const health = useView(views.health());
  const sub: Partial<Record<string, string>> = {
    team: t('menu.team_sub', { n: notif.data?.needs_you.length ?? 0 }),
    health: health.data?.device ? t('menu.health_ok') : t('menu.health_unknown'),
    language: NATIVE_NAME[locale],
  };
  return (
    <Screen title={t('menu.title')} sub={t('menu.sub')}>
      <div className="grid grid-cols-4 gap-4">
        {TILES.map(({ id, icon: Icon }) => (
          <Card key={id} onClick={() => nav(id)} className="flex h-[120px] flex-col justify-between p-5">
            <span className="flex h-11 w-11 items-center justify-center rounded-ground bg-sky text-midnight">
              <Icon size={22} />
            </span>
            <span>
              <span className="block truncate text-body font-bold">{t(`menu.tile_${id}`)}</span>
              <span className="block truncate text-meta text-ink-3">
                {sub[id] ?? t(`menu.tile_${id}_sub`)}
              </span>
            </span>
          </Card>
        ))}
      </div>
    </Screen>
  );
}

export function TeamScreen(_: ScreenProps) {
  const { t } = useI18n();
  const nav = useDeviceNav();
  const run = useCommand();
  const state = useView(views.team());
  return (
    <Screen
      title={t('team.title')}
      sub={t('team.sub')}
      right={
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" onClick={() => nav('trust')}>
            {t('team.activity_log')}
          </Button>
          <Button variant="dark" size="sm" onClick={() => void run('agents.pause_all', {})}>
            {t('team.pause_all')}
          </Button>
        </div>
      }
      chips={[{ label: t('team.chip_night'), text: 'Kya kya kiya raat ko?' }]}
    >
      <ViewGate state={state} pendingIcon={<Orb state="thinking" size={96} />}>
        {() => null}
      </ViewGate>
    </Screen>
  );
}

export function RunScreen({ param }: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.run(param ?? 'current'));
  return (
    <Screen title={t('run.title')} sub={t('run.sub')}>
      <ViewGate state={state}>{() => null}</ViewGate>
    </Screen>
  );
}

export function MemoryScreen(_: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.memory());
  return (
    <Screen title={t('memory.title')} sub={t('memory.sub')}>
      <ViewGate state={state} pendingIcon={<Orb state="thinking" size={96} />}>
        {() => null}
      </ViewGate>
    </Screen>
  );
}

export function HisaabScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const run = useCommand();
  const state = useView(views.hisaab());
  return (
    <Screen title={t('hisaab.title')} sub={t('hisaab.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5">
              <SectionTitle>{t('hisaab.today')}</SectionTitle>
              <Money paise={v.today.sales_paise} className="text-3xl font-extrabold" />
              {Object.entries(v.today.by_mode).map(([m, p]) => (
                <p key={m} className="flex justify-between text-body">
                  <span>{t(`pay.${m}`)}</span>
                  <Money paise={p} />
                </p>
              ))}
              <p className="mt-2 flex justify-between text-meta text-ink-3">
                <span>{t('hisaab.expenses')}</span>
                <Money paise={v.today.expenses_paise} />
              </p>
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('hisaab.close')}</SectionTitle>
              {v.close ? (
                <>
                  <p className="text-body">{t('hisaab.matched', { n: field(v.close, 'matched', 0) })}</p>
                  <p className="text-body text-amber-text">
                    {t('hisaab.unmatched', { n: v.unmatched.length })}
                  </p>
                  <p className="text-body">
                    {t('hisaab.cash_variance')}{' '}
                    <Money paise={field(v.close, 'cash_variance_paise', 0)} className="font-bold text-red" />
                  </p>
                  <ArthNote label={false}>{t(field(v.close, 'cause_key', 'hisaab.cause_unknown'))}</ArthNote>
                </>
              ) : (
                <p className="text-body text-ink-3">{t('hisaab.not_closed')}</p>
              )}
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('hisaab.settlement')}</SectionTitle>
              {v.settlements.map((s) => (
                <div key={s.id} className="text-body">
                  <p className="flex justify-between">
                    <span>{t('hisaab.gross')}</span>
                    <Money paise={s.gross_paise} />
                  </p>
                  {s.deductions.map((d) => (
                    <p key={d.kind} className="flex justify-between text-meta text-ink-3">
                      <span>{t(`hisaab.ded_${d.kind}`)}</span>
                      <Money paise={-d.amount_paise} />
                    </p>
                  ))}
                  <p className="flex justify-between border-t border-line pt-1 font-bold">
                    <span>{t('hisaab.net')}</span>
                    <Money paise={s.net_paise} />
                  </p>
                </div>
              ))}
            </Card>
            <Card className="col-span-2 p-5" attention={v.unmatched.length > 0}>
              <SectionTitle>{t('hisaab.unmatched_queue')}</SectionTitle>
              {v.unmatched.map((u) => (
                <div key={u.payment_id} className="flex items-center gap-3 border-b border-line py-2.5">
                  <Money paise={u.amount_paise} className="text-arth font-bold" />
                  <span className="num text-meta text-ink-3">{time(u.received_at)}</span>
                  <span className="flex-1 text-body">
                    {u.khata_patron_id ? <Who id={u.khata_patron_id} /> : null}
                  </span>
                  {u.suggestions[0] && (
                    <Button
                      variant="tint"
                      size="sm"
                      onClick={() =>
                        void run('treasury.match_bill', {
                          payment_id: u.payment_id,
                          bill_id: u.suggestions[0]!.bill_id,
                        })
                      }
                    >
                      {t('hisaab.match', { pct: Math.round(u.suggestions[0].score_bp / 100) })}
                    </Button>
                  )}
                </div>
              ))}
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('hisaab.shifts')}</SectionTitle>
              {v.shifts.map((s) => (
                <div key={s.id} className="text-body">
                  <Who id={s.staff_id} /> · {time(s.opened_at)}
                  <p className="text-meta text-ink-3">
                    {t('hisaab.expected')} <Money paise={s.expected_paise} />
                  </p>
                </div>
              ))}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

function Who({ id }: { id: string }) {
  return <span className="font-semibold">{useName(id)}</span>;
}

export function ReportsScreen(_: ScreenProps) {
  const { t } = useI18n();
  const run = useCommand();
  const state = useView(views.reports());
  return (
    <Screen title={t('reports.title')} sub={t('reports.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-2 gap-5">
            <Card className="p-6">
              <SectionTitle>{t('reports.pnl', { month: v.month })}</SectionTitle>
              {(
                [
                  ['sales_paise', 'reports.sales'],
                  ['cogs_paise', 'reports.cogs'],
                  ['gross_profit_paise', 'reports.gross'],
                  ['expenses_paise', 'reports.expenses'],
                  ['reward_cost_paise', 'reports.rewards'],
                ] as const
              ).map(([k, label]) => (
                <p key={k} className="flex justify-between border-b border-line py-2 text-body">
                  <span>{t(label)}</span>
                  <Money paise={v.pnl[k]} />
                </p>
              ))}
              <p className="flex justify-between pt-2 text-arth font-bold">
                <span>{t('reports.net')}</span>
                <Money paise={v.pnl.net_paise} className="text-green" />
              </p>
            </Card>
            <div className="flex flex-col gap-4">
              <Card className="p-6">
                <SectionTitle>{t('reports.gst')}</SectionTitle>
                <Pill tone="sky">{t(`reports.profile_${v.profile}`)}</Pill>
                <p className="mt-2 text-body">{t('reports.invoices', { n: v.gst.invoices })}</p>
              </Card>
              <Card className="p-6">
                <SectionTitle>{t('reports.scheduled')}</SectionTitle>
                {v.scheduled.map((s) => (
                  <p key={s.id} className="text-body">
                    {t(`reports.cadence_${s.cadence}`)}
                  </p>
                ))}
                <div className="mt-3 flex gap-2">
                  <Button
                    variant="tint"
                    size="sm"
                    onClick={() => void run('books.close_month', { month: v.month })}
                  >
                    {t('reports.close_month')}
                  </Button>
                  <Button variant="ghost" size="sm">
                    {t('reports.export')}
                  </Button>
                </div>
              </Card>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function FeedbackScreen(_: ScreenProps) {
  const { t, date } = useI18n();
  const state = useView(views.feedback());
  return (
    <Screen title={t('feedback.title')} sub={t('feedback.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[300px_1fr] gap-5">
            <Card className="flex flex-col items-center justify-center gap-2 p-6">
              <p className="num text-amount font-extrabold">
                {v.average_bp ? (v.average_bp / 10000).toFixed(1) : '—'}
              </p>
              <p className="text-body text-ink-3">{t('feedback.count', { n: v.count })}</p>
              <Pill tone={v.complaints ? 'amber' : 'green'}>
                {t('feedback.complaints', { n: v.complaints })}
              </Pill>
            </Card>
            <Card className="divide-y divide-line">
              {v.ratings.map((r) => (
                <div key={r.id} className="flex items-center gap-3 px-5 py-3">
                  <span className="flex gap-0.5 text-amber">
                    {Array.from({ length: 5 }, (_, i) => (
                      <Star key={i} size={16} fill={i < r.rating ? 'currentColor' : 'none'} />
                    ))}
                  </span>
                  <span className="flex-1 text-body">{r.complaint_key ? t(r.complaint_key) : ''}</span>
                  <span className="text-meta text-ink-3">{date(r.occurred_at)}</span>
                  {r.complaint_key && (
                    <Button variant="tint" size="sm">
                      {t('feedback.recover')} · R3
                    </Button>
                  )}
                </div>
              ))}
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function LanguageScreen(_: ScreenProps) {
  const { t, locale, setLocale, money } = useI18n();
  const run = useCommand();
  const state = useView(views.language());
  const home = useView(views.home());
  const [speech, setSpeech] = useState('hi-IN');
  const choose = (l: UiLocale) => {
    setLocale(l);
    if (l !== 'xx-LONG')
      void run('merchant.update_settings', {
        screen_lang: l,
        speech_lang: speech,
        customer_lang: state.data?.customer_lang ?? 'hi',
      });
  };
  const preview = t('language.preview', {
    amount: money(home.data?.today.sales_paise ?? 0),
    n: home.data?.today.bills ?? 0,
  });
  return (
    <Screen title={t('language.title')} sub={t('language.sub')}>
      <div className="grid grid-cols-[1fr_340px] gap-5">
        <div className="grid grid-cols-3 gap-3">
          {UI_LOCALES.filter((l) => l !== 'xx-LONG' || process.env.NODE_ENV !== 'production').map((l) => (
            <button
              key={l}
              type="button"
              onClick={() => choose(l)}
              className={cx(
                'flex h-[92px] flex-col justify-center rounded-card border-2 bg-white px-5 text-left shadow-1',
                locale === l ? 'border-paytm-blue bg-sky' : 'border-transparent',
              )}
            >
              <span className="text-arth font-bold">{NATIVE_NAME[l]}</span>
              <span className="text-meta text-ink-3">{t(`lang.${l}`)}</span>
            </button>
          ))}
        </div>
        <Card className="flex flex-col gap-4 p-6">
          <SectionTitle>{t('language.voice')}</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {['hi-IN', 'en-IN', 'mr-IN', 'ta-IN'].map((s) => (
              <Chip key={s} active={speech === s} onClick={() => setSpeech(s)}>
                {s}
              </Chip>
            ))}
          </div>
          <SectionTitle>{t('language.customers')}</SectionTitle>
          <p className="text-body">
            {state.data
              ? t(`lang.${isUiLocale(state.data.customer_lang) ? state.data.customer_lang : 'hi'}`)
              : '…'}
          </p>
          <ArthNote label={false}>{preview}</ArthNote>
          <Button
            variant="dark"
            icon={<Volume2 size={18} />}
            onClick={() => {
              const u = new SpeechSynthesisUtterance(preview);
              u.lang = speech;
              window.speechSynthesis?.speak(u);
            }}
          >
            {t('language.listen')}
          </Button>
        </Card>
      </div>
    </Screen>
  );
}

export function StaffScreen(_: ScreenProps) {
  const { t } = useI18n();
  const state = useView(views.staff());
  const trust = useView(views.trust());
  return (
    <Screen title={t('staff.title')} sub={t('staff.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-3 gap-4">
            {v.staff.map((s) => {
              const role = trust.data?.roles.find((r) => r.role === s.role);
              return (
                <Card key={s.id} className="flex flex-col gap-2 p-5">
                  <p className="text-arth font-bold">{s.name}</p>
                  <Pill tone="sky">{t(`role.${s.role}`)}</Pill>
                  {role && (
                    <p className="text-meta text-ink-3">
                      {t('staff.max_tier')} <TierChip tier={role.max_tier} />
                    </p>
                  )}
                  <Button variant="ghost" size="sm">
                    {t('staff.reset_pin')}
                  </Button>
                </Card>
              );
            })}
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function TrustScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const run = useCommand();
  const mode = useDataMode();
  const state = useView(views.trust());
  const [verify, setVerify] = useState<AuditVerification | null>(null);
  const check = async () => {
    if (mode === 'fixture') setVerify({ valid: true, checked: state.data?.audit.rows ?? 0, bad_seq: null });
    else setVerify((await apiGet('/v1/audit/verify')) as AuditVerification);
  };
  return (
    <Screen title={t('trust.title')} sub={t('trust.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-[1fr_360px] gap-5">
            <div className="flex flex-col gap-4">
              <Card className="p-5">
                <SectionTitle>{t('trust.can_do')}</SectionTitle>
                {v.tiers.map((tier) => (
                  <div key={tier.tier} className="flex items-center gap-3 border-b border-line py-2.5">
                    <TierChip tier={tier.tier} />
                    <span className="flex-1 text-body">{t(tier.confirm_key)}</span>
                    <span className="text-meta text-ink-3">
                      {t('trust.commands', { n: tier.commands.length })}
                    </span>
                  </div>
                ))}
              </Card>
              <Card className="p-5">
                <SectionTitle
                  action={
                    <Button
                      variant="tint"
                      size="sm"
                      icon={<CircleCheck size={16} />}
                      onClick={() => void check()}
                    >
                      {t('trust.verify')}
                    </Button>
                  }
                >
                  {t('trust.activity')}
                </SectionTitle>
                {verify && (
                  <Pill tone={verify.valid ? 'green' : 'red'}>
                    {verify.valid
                      ? t('trust.verified', { n: verify.checked })
                      : t('trust.tampered', { seq: verify.bad_seq ?? 0 })}
                  </Pill>
                )}
                {v.activity.map((a) => (
                  <div key={a.command_id} className="flex items-center gap-3 border-b border-line py-2">
                    <CircleCheck size={16} className="text-green" />
                    <span className="flex-1 text-body">{t(`cmd.${a.type}`)}</span>
                    <TierChip tier={a.tier} />
                    <span className="num text-meta text-ink-3">{time(a.occurred_at)}</span>
                  </div>
                ))}
              </Card>
            </div>
            <div className="flex flex-col gap-4">
              <Card className="p-5">
                <SectionTitle>{t('trust.kill_switch')}</SectionTitle>
                <Button variant="danger" className="w-full" onClick={() => void run('agents.pause_all', {})}>
                  {t('team.pause_all')}
                </Button>
              </Card>
              <Card className="p-5">
                <SectionTitle>{t('trust.data_sharing')}</SectionTitle>
                <div className="flex items-center justify-between">
                  <span className="text-body">{t('trust.peer_benchmarks')}</span>
                  <Toggle
                    on={v.data_sharing.peer_benchmarks}
                    onChange={(on) => void run('privacy.set_data_sharing', { peer_benchmarks: on })}
                    label={t('trust.peer_benchmarks')}
                  />
                </div>
              </Card>
              <Card className="p-5">
                <SectionTitle>{t('trust.audit')}</SectionTitle>
                <Pill tone={v.audit.ok ? 'green' : 'red'}>{t('trust.audit_rows', { n: v.audit.rows })}</Pill>
              </Card>
            </div>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

export function HealthScreen(_: ScreenProps) {
  const { t, time } = useI18n();
  const state = useView(views.health());
  return (
    <Screen title={t('health.title')} sub={t('health.sub')}>
      <ViewGate state={state}>
        {(v) => (
          <div className="grid grid-cols-3 gap-4">
            <Card className="p-5">
              <SectionTitle>{t('health.device')}</SectionTitle>
              <Cpu className="text-midnight" />
              <p className="mt-2 text-body">
                {t('health.battery', { pct: field(v.device, 'battery_pct', 0) })}
              </p>
              <p className="text-body">{t('health.network', { net: field(v.device, 'network', '—') })}</p>
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('health.providers')}</SectionTitle>
              {v.providers.map((p) => (
                <p key={p.name} className="flex justify-between py-1 text-body">
                  <span className="capitalize">{p.name}</span>
                  <Pill tone={p.mode === 'live' ? 'green' : p.mode === 'fallback' ? 'amber' : 'grey'}>
                    {t(`health.mode_${p.mode}`)}
                  </Pill>
                </p>
              ))}
            </Card>
            <Card className="p-5">
              <SectionTitle>{t('health.spend')}</SectionTitle>
              <Money paise={v.ai_spend_today_paise} className="text-3xl font-extrabold" />
              <p className="mt-2 text-meta text-ink-3">{t('health.queue', { n: v.offline_queue.size })}</p>
              {v.backup.last_snapshot_at && (
                <p className="text-meta text-ink-3">
                  {t('health.backup', { time: time(v.backup.last_snapshot_at) })}
                </p>
              )}
              <HeartPulse className="mt-2 text-green" />
            </Card>
          </div>
        )}
      </ViewGate>
    </Screen>
  );
}

/** SCR-CAPITAL: the need card and a Console pointer. The device never shows an apply button (CAP-4). */
export function CapitalScreen(_: ScreenProps) {
  const { t, date } = useI18n();
  const state = useView(views.capital());
  return (
    <Screen title={t('capital.title')} sub={t('capital.sub')}>
      <ViewGate state={state}>
        {(v) => {
          const offer = v.offers.find((o) => o.id === v.recommended_offer_id);
          return (
            <div className="grid grid-cols-2 gap-5">
              <Card className="flex flex-col gap-3 p-6">
                <SectionTitle>{t('capital.need')}</SectionTitle>
                {v.need ? (
                  <>
                    <p className="text-arth font-bold">
                      {t(field(v.need, 'purpose_key', 'capital.purpose_generic'))}
                    </p>
                    <p className="text-body">
                      {t('capital.shortfall')}{' '}
                      <Money paise={field(v.need, 'shortfall_paise', 0)} className="font-bold text-red" />
                    </p>
                    <p className="text-meta text-ink-3">
                      {t('capital.by', {
                        date: date(`${field(v.need, 'shortfall_on', '2026-11-01')}T00:00:00Z`),
                      })}
                    </p>
                  </>
                ) : (
                  <p className="text-body text-ink-3">{t('capital.no_need')}</p>
                )}
                {offer && (
                  <ArthNote>
                    {t('capital.smallest_offer', { lender: offer.lender })}{' '}
                    <Money paise={offer.amount_paise} className="font-bold" />
                  </ArthNote>
                )}
              </Card>
              <Card className="flex flex-col items-center justify-center gap-4 bg-midnight p-8 text-center text-white">
                <Landmark size={48} />
                <p className="text-arth font-bold">{t(v.console_pointer.message_key)}</p>
                <TierChip tier="R4" />
                <p className="text-body text-white/70">{v.console_pointer.route}</p>
              </Card>
            </div>
          );
        }}
      </ViewGate>
    </Screen>
  );
}
