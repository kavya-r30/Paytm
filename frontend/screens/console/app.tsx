'use client';

// Console (I7 CON, T7.13): CON-HOME, ASK, WORK, PLANS, LEDGER, CAPITAL, OTP, R4, TRUST, SETTINGS on a 390-wide
// mobile shell. R4 (refunds, write-offs, bulk price, erasure, capital apply) happens only here, after OTP + KFS.
import {
  Bot,
  BriefcaseBusiness,
  ChevronRight,
  Home,
  Landmark,
  MessageSquare,
  Settings,
  ShieldCheck,
  Sparkles,
  TrendingUp,
} from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useState, type ReactNode } from 'react';
import { ArthNote, Orb } from '@/components/arth/orb';
import { Toasts } from '@/components/shell/device';
import { Button, Card, Money, Pill, SectionTitle, TierChip, Toggle, cx } from '@/components/ui/kit';
import { ApiProblem, apiPost, newIdempotencyKey } from '@/lib/api/client';
import { useDecide } from '@/lib/api/commands';
import { useDataMode, useView } from '@/lib/api/hooks';
import { views } from '@/lib/api/views';
import type { CapitalView } from '@/lib/contracts';
import { PATRONS, ITEMS } from '@/lib/fixtures/gupta';
import { useI18n } from '@/lib/i18n/react';
import { useTurn } from '@/lib/store/turn';
import { useGateText } from '../device/today';

const TABS = [
  { id: 'home', icon: Home },
  { id: 'work', icon: BriefcaseBusiness },
  { id: 'ask', icon: MessageSquare },
  { id: 'capital', icon: Landmark },
  { id: 'settings', icon: Settings },
] as const;

function Shell({ title, children, back }: { title: string; children: ReactNode; back?: boolean }) {
  const { t } = useI18n();
  const router = useRouter();
  return (
    <div className="flex min-h-screen justify-center bg-ink">
      <div className="relative flex min-h-screen w-full max-w-[390px] flex-col bg-ground">
        <header className="sticky top-0 z-10 flex items-center gap-3 bg-midnight px-4 pb-3 pt-6 text-white">
          {back && (
            <button
              type="button"
              onClick={() => router.back()}
              className="text-meta font-bold"
              aria-label={t('common.close')}
            >
              ←
            </button>
          )}
          <Orb size={32} />
          <h1 className="flex-1 truncate text-arth font-bold">{title}</h1>
          <span className="rounded-chip bg-white/10 px-2 py-0.5 text-meta">{t('con.badge')}</span>
        </header>
        <main className="flex flex-1 flex-col gap-3 p-4 pb-24">{children}</main>
        <nav className="fixed bottom-0 flex w-full max-w-[390px] justify-around border-t border-line bg-white py-2">
          {TABS.map(({ id, icon: Icon }) => (
            <Link
              key={id}
              href={`/console/${id}`}
              className="flex flex-col items-center gap-0.5 text-meta text-ink-3"
            >
              <Icon size={20} />
              {t(`con.tab_${id}`)}
            </Link>
          ))}
        </nav>
        <Toasts />
      </div>
    </div>
  );
}

function Row({
  href,
  icon,
  title,
  sub,
  right,
}: {
  href: string;
  icon: ReactNode;
  title: string;
  sub?: string;
  right?: ReactNode;
}) {
  return (
    <Link href={href} className="flex items-center gap-3 rounded-ground bg-white p-3 shadow-1">
      <span className="flex h-10 w-10 items-center justify-center rounded-ground bg-sky text-midnight">
        {icon}
      </span>
      <span className="min-w-0 flex-1">
        <span className="block truncate text-body font-bold">{title}</span>
        {sub && <span className="block truncate text-meta text-ink-3">{sub}</span>}
      </span>
      {right ?? <ChevronRight size={18} className="text-ink-3" />}
    </Link>
  );
}

function HomeScreen() {
  const { t } = useI18n();
  const home = useView(views.home());
  const h = home.data;
  return (
    <Shell title={t('con.home')}>
      {h && (
        <Card className="p-4">
          <p className="text-meta text-ink-3">{t('home.sales_title')}</p>
          <Money paise={h.today.sales_paise} className="text-3xl font-extrabold" />
          <p className="text-meta text-ink-3">
            {t('con.bills_customers', { bills: h.today.bills, customers: h.today.customers })}
          </p>
        </Card>
      )}
      <Row
        href="/console/work"
        icon={<ShieldCheck size={20} />}
        title={t('con.needs_you', { n: h?.gates.length ?? 0 })}
        right={<Pill tone="amber">{h?.gates.length ?? 0}</Pill>}
      />
      <Row
        href="/console/plans"
        icon={<TrendingUp size={20} />}
        title={t('con.plans')}
        sub={t('con.plans_sub')}
      />
      <Row
        href="/console/ledger"
        icon={<Sparkles size={20} />}
        title={t('con.ledger')}
        sub={t('con.ledger_sub')}
      />
      <Row
        href="/console/capital"
        icon={<Landmark size={20} />}
        title={t('con.capital')}
        sub={t('con.capital_sub')}
      />
      <Row href="/console/r4" icon={<ShieldCheck size={20} />} title={t('con.r4')} sub={t('con.r4_sub')} />
      <Row href="/console/trust" icon={<Bot size={20} />} title={t('con.trust')} sub={t('con.trust_sub')} />
    </Shell>
  );
}

function WorkScreen() {
  const { t } = useI18n();
  const decide = useDecide();
  const text = useGateText();
  const n = useView(views.notifications());
  const toast = useTurn((s) => s.toast);
  return (
    <Shell title={t('con.work')}>
      <Button
        variant="danger"
        onClick={() => toast({ textKey: 'toast.decision_snooze', until: null, tone: 'info' })}
      >
        {t('team.pause_all')}
      </Button>
      {(n.data?.needs_you ?? []).map((g) => {
        const s = text(g);
        return (
          <Card key={g.gate_id} attention className="flex flex-col gap-2 p-4">
            <div className="flex items-center justify-between gap-2">
              <p className="min-w-0 truncate text-body font-bold">{s.title}</p>
              <TierChip tier={g.tier} compact />
            </div>
            <p className="text-meta text-ink-3">{s.sub}</p>
            <div className="flex gap-2">
              <Button size="sm" onClick={() => void decide(g.thread_id, 'approve')}>
                {t('gate.approve')}
              </Button>
              <Button size="sm" variant="ghost" onClick={() => void decide(g.thread_id, 'edit', {})}>
                {t('gate.edit')}
              </Button>
              <Button size="sm" variant="text" onClick={() => void decide(g.thread_id, 'snooze')}>
                {t('gate.snooze')}
              </Button>
            </div>
          </Card>
        );
      })}
      {n.data && n.data.needs_you.length === 0 && <ArthNote>{t('notif.none')}</ArthNote>}
    </Shell>
  );
}

function AskScreen() {
  const { t } = useI18n();
  const state = useView(views.ask());
  return (
    <Shell title={t('ask.title')}>
      <ArthNote>{t(state.pending?.reason_key ?? 'sufficiency.ask_pending')}</ArthNote>
      <p className="text-meta text-ink-3">{t('con.ask_same_session')}</p>
    </Shell>
  );
}

function PendingScreen({ title, spec }: { title: string; spec: ReturnType<typeof views.grow> }) {
  const { t } = useI18n();
  const state = useView(spec);
  return (
    <Shell title={title} back>
      <ArthNote>{t(state.pending?.reason_key ?? 'sufficiency.growth_pending')}</ArthNote>
      <p className="text-meta text-ink-3">
        {t('state.pending_body', { layer: state.pending?.layer ?? 'L6' })}
      </p>
    </Shell>
  );
}

/** OTP + KFS step-up (CON-OTP). The simulated OTP is shown on screen; nothing real is sent. */
function OtpEntry({ onVerified, kfs }: { onVerified: (otp: string) => void; kfs?: string }) {
  const { t } = useI18n();
  const [otp, setOtp] = useState('');
  const [agreed, setAgreed] = useState(!kfs);
  const demo = '482617';
  return (
    <Card className="flex flex-col gap-3 p-4">
      <SectionTitle action={<TierChip tier="R4" />}>{t('con.otp_title')}</SectionTitle>
      <p className="text-meta text-ink-3">{t('con.otp_sent', { otp: demo })}</p>
      <input
        inputMode="numeric"
        maxLength={6}
        value={otp}
        onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
        className="num h-14 rounded-ground border-2 border-line text-center text-title tracking-[0.5em]"
        aria-label={t('con.otp_title')}
      />
      {kfs && (
        <label className="flex items-start gap-2 text-meta">
          <Toggle on={agreed} onChange={setAgreed} label={t('con.kfs_agree')} />
          <span>
            {t('con.kfs_agree')}{' '}
            <a href={kfs} className="font-bold text-cyan-text">
              {t('con.kfs_link')}
            </a>
          </span>
        </label>
      )}
      <Button disabled={otp.length !== 6 || !agreed} onClick={() => onVerified(otp)}>
        {t('con.verify')}
      </Button>
    </Card>
  );
}

/** Submits an R4 command from the console session; the server enforces channel + step-up (policy). */
function useR4() {
  const mode = useDataMode();
  const toast = useTurn((s) => s.toast);
  return async (type: string, payload: Record<string, unknown>) => {
    if (mode === 'fixture') {
      toast({ textKey: 'con.r4_done_fixture', params: { what: type }, until: null, tone: 'done' });
      return true;
    }
    try {
      await apiPost('/v1/commands', { type, payload }, newIdempotencyKey());
      toast({ textKey: 'toast.done', params: { what: type }, until: null, tone: 'done' });
      return true;
    } catch (e) {
      toast({
        textKey: e instanceof ApiProblem ? e.messageKey : 'toast.needs_network',
        until: null,
        tone: 'error',
      });
      return false;
    }
  };
}

function OfferCard({ offer, recommended }: { offer: CapitalView['offers'][number]; recommended: boolean }) {
  const { t, money, date } = useI18n();
  const submit = useR4();
  const [step, setStep] = useState<'view' | 'otp' | 'done'>('view');
  const rows: [string, string][] = [
    ['con.cap_amount', money(offer.amount_paise)],
    ['con.cap_tenor', t('con.days', { n: offer.tenor_days })],
    ['con.cap_apr', `${(offer.apr_bp / 100).toFixed(2)}%`],
    ['con.cap_edi', money(offer.edi_paise)],
    ['con.cap_fee', money(offer.processing_fee_paise)],
    ['con.cap_total', money(offer.total_repayment_paise)],
    ['con.cap_cooling', t('con.days', { n: offer.cooling_off_days })],
    ['con.cap_expires', date(offer.expires_at)],
  ];
  return (
    <Card className={cx('flex flex-col gap-2 p-4', recommended && 'border-2 border-paytm-blue')}>
      <div className="flex items-center justify-between">
        <p className="text-body font-bold">{offer.lender}</p>
        {recommended && <Pill tone="sky">{t('gate.recommended')}</Pill>}
      </div>
      {rows.map(([k, v]) => (
        <p key={k} className="flex justify-between text-body">
          <span className="text-ink-3">{t(k)}</span>
          <span className="num font-semibold">{v}</span>
        </p>
      ))}
      <Pill tone={offer.affordable ? 'green' : 'red'}>
        {t(offer.affordable ? 'con.affordable' : 'con.not_affordable')}
      </Pill>
      {step === 'view' && <Button onClick={() => setStep('otp')}>{t('con.apply')}</Button>}
      {step === 'otp' && (
        <OtpEntry
          kfs={offer.kfs_url}
          onVerified={async () => {
            if (await submit('capital.apply', { offer_id: offer.id })) setStep('done');
          }}
        />
      )}
      {step === 'done' && <ArthNote>{t('con.applied', { days: offer.cooling_off_days })}</ArthNote>}
    </Card>
  );
}

function CapitalScreen() {
  const { t } = useI18n();
  const state = useView(views.capital());
  const c = state.data;
  return (
    <Shell title={t('con.capital')}>
      {c?.need && (
        <ArthNote>
          {t('capital.shortfall')}{' '}
          <Money
            paise={Number((c.need as Record<string, unknown>).shortfall_paise ?? 0)}
            className="font-bold"
          />
        </ArthNote>
      )}
      {(c?.offers ?? []).map((o) => (
        <OfferCard key={o.id} offer={o} recommended={o.id === c?.recommended_offer_id} />
      ))}
      {c && c.offers.length === 0 && <p className="text-body text-ink-3">{t('con.no_offers')}</p>}
    </Shell>
  );
}

const R4_ACTIONS = [
  {
    id: 'refund',
    type: 'treasury.refund',
    payload: {
      payment_id: 'payment_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0',
      amount_paise: 9000,
      reason_key: 'refund.duplicate',
    },
  },
  {
    id: 'write_off',
    type: 'ledger.reverse_entry',
    payload: { entry_id: 'entry_01JBQ0Z7Y8K3M4N5P6Q7R8S9T0', reason_key: 'ledger.owner_correction' },
  },
  {
    id: 'bulk_price',
    type: 'catalog.bulk_price',
    payload: { prices: [{ item_id: ITEMS.sugar.id, price_paise: 4900 }] },
  },
  {
    id: 'erase',
    type: 'privacy.erase_patron',
    payload: { patron_id: PATRONS.rohit.id, reason_key: 'privacy.customer_request' },
  },
] as const;

function R4Screen() {
  const { t } = useI18n();
  const submit = useR4();
  const [open, setOpen] = useState<string | null>(null);
  return (
    <Shell title={t('con.r4')} back>
      <ArthNote>{t('con.r4_note')}</ArthNote>
      {R4_ACTIONS.map((a) => (
        <Card key={a.id} className="flex flex-col gap-2 p-4">
          <div className="flex items-center justify-between">
            <p className="text-body font-bold">{t(`con.r4_${a.id}`)}</p>
            <TierChip tier="R4" compact />
          </div>
          <p className="text-meta text-ink-3">{t(`con.r4_${a.id}_sub`)}</p>
          {open === a.id ? (
            <OtpEntry onVerified={async () => (await submit(a.type, a.payload)) && setOpen(null)} />
          ) : (
            <Button variant="ghost" size="sm" onClick={() => setOpen(a.id)}>
              {t('con.continue')}
            </Button>
          )}
        </Card>
      ))}
    </Shell>
  );
}

function TrustScreen() {
  const { t } = useI18n();
  const state = useView(views.trust());
  return (
    <Shell title={t('con.trust')} back>
      {(state.data?.tiers ?? []).map((tier) => (
        <Card key={tier.tier} className="flex items-center gap-3 p-3">
          <TierChip tier={tier.tier} compact />
          <span className="text-body">{t(tier.confirm_key)}</span>
        </Card>
      ))}
      {state.data && (
        <Pill tone={state.data.audit.ok ? 'green' : 'red'}>
          {t('trust.audit_rows', { n: state.data.audit.rows })}
        </Pill>
      )}
    </Shell>
  );
}

function SettingsScreen() {
  const { t } = useI18n();
  const trust = useView(views.trust());
  const staff = useView(views.staff());
  const health = useView(views.health());
  return (
    <Shell title={t('con.settings')}>
      <Card className="flex items-center justify-between p-4">
        <span className="text-body">{t('trust.peer_benchmarks')}</span>
        <Toggle
          on={trust.data?.data_sharing.peer_benchmarks ?? false}
          onChange={() => undefined}
          label={t('trust.peer_benchmarks')}
        />
      </Card>
      <Card className="p-4">
        <SectionTitle>{t('staff.title')}</SectionTitle>
        {(staff.data?.staff ?? []).map((s) => (
          <p key={s.id} className="text-body">
            {s.name} · <span className="text-ink-3">{t(`role.${s.role}`)}</span>
          </p>
        ))}
      </Card>
      <Card className="p-4">
        <SectionTitle>{t('health.providers')}</SectionTitle>
        {(health.data?.providers ?? []).map((p) => (
          <p key={p.name} className="flex justify-between text-body capitalize">
            {p.name} <Pill>{t(`health.mode_${p.mode}`)}</Pill>
          </p>
        ))}
      </Card>
    </Shell>
  );
}

export function ConsoleApp({ screen }: { screen: string; param?: string }) {
  const { t } = useI18n();
  switch (screen) {
    case 'work':
      return <WorkScreen />;
    case 'ask':
      return <AskScreen />;
    case 'plans':
      return <PendingScreen title={t('con.plans')} spec={views.grow()} />;
    case 'ledger':
      return <PendingScreen title={t('con.ledger')} spec={views.ledger()} />;
    case 'capital':
      return <CapitalScreen />;
    case 'r4':
    case 'otp':
      return <R4Screen />;
    case 'trust':
      return <TrustScreen />;
    case 'settings':
      return <SettingsScreen />;
    default:
      return <HomeScreen />;
  }
}
